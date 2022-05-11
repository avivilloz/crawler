# Crawler

## Description

Simple web crawler. Crawls through given url and keeps information about other urls found.

## Dependency on Python Libraries

- argparse
- asyncio
- bs4
- aiohttp
- urllib

## Installation

``` git clone https://github.com/avivilloz/crawler ```

## Run

``` cd crawler ```

``` python test.py -u <url> [optional flags] ```

## Flags

``` -s --get-statistics ``` - if chosen, statistics are displayed with output info

``` -l --log ``` - if chosen, run-time logs will be added to output/log_crawling.txt

``` -otf --output-to-file ``` - if chosen, output is displayed in file

``` -ofn --output-file-name <file-name> ``` - default file name is "crawled_info.txt"

``` -m --max-crawls <num-of-crawls> ``` - default is 30
