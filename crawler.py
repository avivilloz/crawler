import os
import asyncio
import aiohttp
from bs4 import BeautifulSoup
from urllib.parse import urlparse, urljoin
from utils import clean_screen, show_on_screen

class Crawler:

    _blacklist_extensions = [".pdf", ".jpg", ".jpeg", ".png", ".zip"]
    _blacklist_schemes = ["javascript"]
    _log_file_path = "output/log_crawling.txt"

    def __init__(self, max_crawls, should_log_to_file):
        self._crawled_urls_data = {}
        self._max_crawls = max_crawls
        self._log_file = None
        if os.path.exists(Crawler._log_file_path):
            os.remove(Crawler._log_file_path)
        if should_log_to_file:
            self._log_file = open(Crawler._log_file_path, "a+")

    def __del__(self):
        if self._log_file:
            self._log_file.close()

    class CrawledUrlData:
        def __init__(self):
            self.url = ""
            self.crawls_attempts = 1
            self.crawled_urls = set()
            self.failed_to_fetch_urls = set()
            self.internal_urls = set()
            self.external_urls = set()
            self.internal_urls_by_depth = {}
            self.external_urls_by_depth = {}
            self.broken_urls = set()
            self.unsupported_urls = set()

    def crawl(self, url):
        data = self.CrawledUrlData()
        self._crawled_urls_data[url] = data
        data.url = url
        data.internal_urls.add(url)
        asyncio.run(self._crawl_rec(data, url, 1))

    async def _crawl_rec(self, data, url, depth):
        links = await self._crawl_page(data, url, depth)
        if not links:
            return
        tasks = []
        for link in links:
            if data.crawls_attempts > self._max_crawls:
                break
            data.crawls_attempts += 1
            task = asyncio.Task(self._crawl_rec(data, link, depth + 1))
            tasks.append(task)
        await asyncio.gather(*tasks)

    def _log(self, str):
        clean_screen()
        show_on_screen(str)
        if self._log_file:
            self._log_file.write(str + "\n")

    async def _crawl_page(self, data, url, depth):
        html = await self._fetch_html(data, url)
        if not html:
            return
        self._log("Crawling: " + url)
        html_parser = self._get_html_parser(html)
        links = self._parse_html(data, html_parser, url, depth)
        data.crawled_urls.add(url)
        return links

    async def _fetch_html(self, data, url):
        try:
            async with aiohttp.ClientSession() as session:
                async with session.get(url) as response:
                    return await response.text()
        except Exception as e:
            data.failed_to_fetch_urls.add(url)
            self._log("Failed To Fetch: " + url + " Exception: " + str(e))
        return False

    def _get_html_parser(self, html):
        return BeautifulSoup(html, "html.parser")

    def _parse_html(self, data, html_parser, url, depth):
        links = set()
        url_domain_name = urlparse(url).netloc
        for a in html_parser.findAll("a"):
            href = a.attrs.get("href")
            if href == "" or href is None:
                continue
            href = urljoin(url, href)
            parsed_href = urlparse(href)
            href = parsed_href.scheme + "://" + parsed_href.netloc + parsed_href.path
            if not self._is_valid_url(href):
                if not self._contains_url(data.broken_urls, href):
                    data.broken_urls.add(href)
            elif not self._is_supported_url(href):
                if not self._contains_url(data.unsupported_urls, href):
                    data.unsupported_urls.add(href)
            elif url_domain_name not in href: # is external url
                if not self._contains_url(data.external_urls, href):
                    data.external_urls.add(href)
                    if depth not in data.external_urls_by_depth:
                        data.external_urls_by_depth[depth] = set()
                    data.external_urls_by_depth[depth].add(href)
            elif not self._contains_url(data.internal_urls, href):
                data.internal_urls.add(href)
                if depth not in data.internal_urls_by_depth:
                    data.internal_urls_by_depth[depth] = set()
                data.internal_urls_by_depth[depth].add(href)
                links.add(href)
        return links

    def _is_supported_url(self, url):
        parsed_url = urlparse(url)
        for scheme in Crawler._blacklist_schemes:
            if parsed_url.scheme == scheme:
                return False
        for extension in Crawler._blacklist_extensions:
            if url.endswith(extension):
                return False
        return True

    @staticmethod
    def _contains_url(container, url):
        if url[-1] == '/':
            return (url in container) or (url[:-1] in container)
        else:
            return (url in container) or ((url + "/") in container)

    @staticmethod
    def _is_valid_url(url):
        parsed_url = urlparse(url)
        return bool(parsed_url.netloc) and bool(parsed_url.scheme)

    def get_info(self, url):
        info = ""
        data = self._crawled_urls_data[url]
        for depth in data.internal_urls_by_depth:
            info += ("\nInternal Urls - Depth " + str(depth) + ":\n\n")
            for url in data.internal_urls_by_depth[depth]:
                info += (url + "\n")
        for depth in data.external_urls_by_depth:
            info += ("\nExternal Urls - Depth " + str(depth) + ":\n\n")
            for url in data.external_urls_by_depth[depth]:
                info += (url + "\n")
        info += "\nUnsupported Urls:\n\n"
        for url in data.unsupported_urls:
            info += (url + "\n")
        info += "\nBroken Urls:\n\n"
        for url in data.broken_urls:
            info += (url + "\n")
        info += "\nCrawled Urls:\n\n"
        for url in data.crawled_urls:
            info += (url + "\n")
        info += "\nFailed To Fetch Urls:\n\n"
        for url in data.failed_to_fetch_urls:
            info += (url + "\n")
        return info

    def get_statistics(self, url):
        data = self._crawled_urls_data[url]
        internal_urls_depth = len(data.internal_urls_by_depth)
        external_urls_depth = len(data.external_urls_by_depth)
        return "Url: " + data.url \
        + "\nCrawled Urls: " + str(len(data.crawled_urls)) \
        + "\nFailed To Fetch Urls: " + str(len(data.failed_to_fetch_urls)) \
        + "\nDepth Reached: " + str(max(internal_urls_depth, external_urls_depth)) \
        + "\nInternal Urls: " + str(len(data.internal_urls)) \
        + "\nExternal Urls: " + str(len(data.external_urls)) \
        + "\nUnsupported Urls: " + str(len(data.unsupported_urls)) \
        + "\nBroken Urls: " + str(len(data.broken_urls)) \
        + "\n"