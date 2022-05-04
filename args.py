import argparse

args_parser = argparse.ArgumentParser()

args_parser.add_argument("-u", "--url", dest="url", help="Input url", required=True)
args_parser.add_argument("-gs", "--get-statistics", dest="should_get_statistics", action="store_true", help="Get statistics")
args_parser.add_argument("-otf", "--output-to-file", dest="is_output_to_file", action="store_true", help="Should output to file")
args_parser.add_argument("-ofn", "--output-file", dest="output_file", default="crawled_info.txt", help="Output file name")
args_parser.add_argument("-mc", "--max-crawls", dest="max_crawls", default=30, help="Max urls to crawl", type=int)

args = args_parser.parse_args()