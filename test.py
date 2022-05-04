import asyncio
from utils import clean_screen, output_to_file, output_to_screen
from crawler import Crawler
from args import args

if __name__ == "__main__":
    url = args.url
    crawler = Crawler()
    asyncio.run(crawler.crawl(url, args.max_crawls))
    output = crawler.get_info(url)
    if args.should_get_statistics:
        output = crawler.get_statistics(url) + output
    if args.is_output_to_file:
        output_to_file(output, args.output_file)
        clean_screen()
    else:
        output_to_screen(output)