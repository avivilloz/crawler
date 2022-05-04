import asyncio
import aiohttp
from bs4 import BeautifulSoup
from urllib.parse import urlparse, urljoin
from utils import clean_screen, show_on_screen

class Crawler:

    class CrawledUrlData:
        url = ""
        urls_crawled = 0
        internal_urls = set()
        external_urls = set()
        broken_urls = set()
        unsupported_urls = set()
        internal_urls_by_depth = {}
        external_urls_by_depth = {}

    _crawled_urls_data = {}
    _blacklist_extensions = [".pdf", ".jpg"]
    _blacklist_schemes = ["javascript"]

    def crawl(self, url, max_crawls):
        data = self.CrawledUrlData()
        self._crawled_urls_data[url] = data
        data.url = url
        asyncio.run(self.crawl_rec(data, url, max_crawls, 1))

    async def crawl_rec(self, data, url, max_crawls, depth):
        links = await self._crawl_single_page(data, url, depth)
        tasks = []
        for link in links:
            if data.urls_crawled >= max_crawls:
                break
            data.urls_crawled += 1
            # I chose to collect tasks and perform them asynchronously
            # because if I would call directly for 
            # "async self.crawl_rec(...)" it would "break" async and
            # become synchronous, since we need to wait for output of 
            # line 30 anyway to continue the "links loop" at line 32
            task = asyncio.Task(self.crawl_rec(data, link, max_crawls, depth + 1))
            asyncio.ensure_future(task)
            tasks.append(task)
        await asyncio.gather(*tasks)

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
        return info

    def get_statistics(self, url):
        return "Url: " + self._crawled_urls_data[url].url \
        + "\nUrls Crawled: " + str(self._crawled_urls_data[url].urls_crawled) \
        + "\nInternal Urls: " + str(len(self._crawled_urls_data[url].internal_urls)) \
        + "\nExternal Urls: " + str(len(self._crawled_urls_data[url].external_urls)) \
        + "\nUnsupported Urls: " + str(len(self._crawled_urls_data[url].unsupported_urls)) \
        + "\nBroken Urls: " + str(len(self._crawled_urls_data[url].broken_urls)) \
        + "\n"

    async def _crawl_single_page(self, data, url, depth):
        clean_screen()
        show_on_screen("Crawling: " + url)
        html = await self._fetch_html(url)
        html_parser = self._get_html_parser(html)
        return self._parse_html(data, html_parser, url, depth)

    async def _fetch_html(self, url):
        async with aiohttp.ClientSession() as session:
            async with session.get(url) as response:
                return await response.text()

    def _get_html_parser(self, html):
        return BeautifulSoup(html, "html.parser")

    def _parse_html(self, data, html_parser, url, depth):
        urls = set()
        url_domain_name = urlparse(url).netloc
        for a in html_parser.findAll("a"):
            href = a.attrs.get("href")
            if href == "" or href is None:
                continue
            href = urljoin(url, href)
            parsed_href = urlparse(href)
            href = parsed_href.scheme + "://" + parsed_href.netloc + parsed_href.path
            if not self._is_valid_url(href):
                if href not in data.broken_urls:
                    data.broken_urls.add(href)
            # added check for supported urls
            elif not self._is_supported_url(href):
                if href not in data.unsupported_urls:
                    data.unsupported_urls.add(href)
            elif url_domain_name not in href:
                if href not in data.external_urls:
                    data.external_urls.add(href)
                    if depth not in data.external_urls_by_depth:
                        data.external_urls_by_depth[depth] = set()
                    data.external_urls_by_depth[depth].add(href)
            elif href not in data.internal_urls:
                data.internal_urls.add(href)
                if depth not in data.internal_urls_by_depth:
                    data.internal_urls_by_depth[depth] = set()
                data.internal_urls_by_depth[depth].add(href)
                urls.add(href)
        return urls

    def _is_supported_url(self, url):
        parsed_url = urlparse(url)
        for scheme in self._blacklist_schemes:
            if parsed_url.scheme == scheme:
                return False
        for extension in self._blacklist_extensions:
            if url.endswith(extension):
                return False
        return True

    def _is_valid_url(self, url):
        parsed_url = urlparse(url)
        return bool(parsed_url.netloc) and bool(parsed_url.scheme)