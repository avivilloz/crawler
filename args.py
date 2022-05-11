import argparse

args_parser = argparse.ArgumentParser()

args_parser.add_argument("-u", "--url", dest="url", help="Input url", required=True)
args_parser.add_argument("-s", "--statistics", dest="should_get_statistics", action="store_true", help="Get statistics with output")
args_parser.add_argument("-l", "--log", dest="should_log_to_file", action="store_true", help="Log to output/log_crawling.txt")
args_parser.add_argument("-otf", "--output-to-file", dest="is_output_to_file", action="store_true", help="Output to file instead of stdout")
args_parser.add_argument("-ofn", "--output-file", dest="output_file", default="output/crawled_info.txt", help="Output file name")
args_parser.add_argument("-m", "--max", dest="max_crawls", default=30, help="Max urls to crawl", type=int)

args = args_parser.parse_args()