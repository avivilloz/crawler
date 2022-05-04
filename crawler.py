import asyncio
import aiohttp
from bs4 import BeautifulSoup
from urllib.parse import urlparse, urljoin
from utils import clean_screen, show_on_screen

class Crawler:

    class CrawledUrlData:
        url = ""
        urls_accessed = 0
        depth_reached = 0
        internal_urls = set()
        external_urls = set()
        broken_urls = set()
        internal_urls_by_depth = {}
        external_urls_by_depth = {}

    _crawled_urls_data = {}

    async def crawl(self, url, max_crawls = 30):
        data = self.CrawledUrlData()
        self._crawled_urls_data[url] = data
        data.url = url
        data.depth_reached += 1
        await self._crawl_single_page(data, url)
        for depth in list(data.internal_urls_by_depth):
            if data.urls_accessed >= max_crawls:
                break
            data.depth_reached += 1
            tasks = []
            for internal_url in data.internal_urls_by_depth[depth]:
                if data.urls_accessed >= max_crawls:
                    break
                data.urls_accessed += 1
                task = asyncio.Task(self._crawl_single_page(data, internal_url))
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
        info += "\nBroken Urls:\n\n"
        for url in data.broken_urls:
            info += (url + "\n")
        return info

    def get_statistics(self, url):
        return "Url: " + self._crawled_urls_data[url].url \
        + "\nUrls Accessed: " + str(self._crawled_urls_data[url].urls_accessed) \
        + "\nDepth Reached: " + str(self._crawled_urls_data[url].depth_reached)\
        + "\nInternal Urls: " + str(len(self._crawled_urls_data[url].internal_urls)) \
        + "\nExternal Urls: " + str(len(self._crawled_urls_data[url].external_urls)) \
        + "\nBroken Urls: " + str(len(self._crawled_urls_data[url].broken_urls))

    async def _crawl_single_page(self, data, url):
        clean_screen()
        show_on_screen("Crawling: " + url)
        html = await self._fetch_html(url)
        html_parser = self._get_html_parser(html)
        self._parse_html(data, html_parser, url)

    async def _fetch_html(self, url):
        async with aiohttp.ClientSession() as session:
            async with session.get(url) as response:
                return await response.text()

    def _get_html_parser(self, html):
        return BeautifulSoup(html, "html.parser")

    def _parse_html(self, data, html_parser, url):
        url_domain_name = urlparse(url).netloc
        for a in html_parser.findAll("a"):
            href = a.attrs.get("href")
            if href == "" or href is None:
                continue
            href = urljoin(url, href)
            href_parsed = urlparse(href)
            href = href_parsed.scheme + "://" + href_parsed.netloc + href_parsed.path
            if not self._is_valid_url(href):
                data.broken_urls.add(href)
            elif url_domain_name not in href:
                if href not in data.external_urls:
                    data.external_urls.add(href)
                    if data.depth_reached not in data.external_urls_by_depth:
                        data.external_urls_by_depth[data.depth_reached] = set()
                    data.external_urls_by_depth[data.depth_reached].add(href)
            elif href not in data.internal_urls:
                data.internal_urls.add(href)
                if data.depth_reached not in data.internal_urls_by_depth:
                    data.internal_urls_by_depth[data.depth_reached] = set()
                data.internal_urls_by_depth[data.depth_reached].add(href)

    def _is_valid_url(self, url):
        url_parsed = urlparse(url)
        return bool(url_parsed.netloc) and bool(url_parsed.scheme)