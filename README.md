# Crawler

## Description

Simple web crawler. Crawls through given url and keeps information about other urls found.

## Dependency on Python Libraries:

- argparse
- asyncio
- bs4
- aiohttp
- urllib

## Instalation

git clone https://github.com/avivilloz/crawler

## Run

``` cd crawler ```
``` python test.py -u <url> [optional flags] ```

## Flags:

``` -gs --get-statistics ``` : if chosen, statistics are displayed with output info

``` -otf --output-to-file : if chosen, output is displayed in file ```

``` -ofn --output-file-name <file-name> : default file name is "crawled_info.txt" ```

``` -mc --max-crawls <num-of-crawls> : default is 30 ```
