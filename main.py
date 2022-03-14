from argparse import ArgumentParser
from typing import List, Union
from pathlib import Path
import httpx
import re

def get_download_request_headers(url: str) -> dict:
    """
    create headers for download request
    copied from https://tabs.ultimate-guitar.com/tab/metallica/nothing-else-matters-guitar-pro-225441
    """
    headers = {
        'accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.9',
        'accept-encoding': 'gzip, deflate, br',
        'accept-language': 'en-US,en;q=0.9',
        'dnt': '1',
        'referer': f'{url}',
        'sec-ch-ua': '" Not A;Brand";v="99", "Chromium";v="99","Google Chrome";v="99"',
        'sec-ch-ua-mobile': '?0',
        'upgrade-insecure-requests': '1'
    }
    return headers

def get_download_request_url(url: str) -> str:
    """
    Get url of tab file download from tab url
    """
    tab_id = re.search('(\d)*$', url).group() 
    return f"https://tabs.ultimate-guitar.com/tab/download?id={tab_id}&session_id="

def _download_bytes(url: str) -> Union[None, bytes]:
    """
    download tab bytes at url.
    """
    resp = None
    with httpx.Client() as client:
        headers = get_download_request_headers(url)
        request_url = get_download_request_url(url)
        resp = client.get(request_url, headers=headers)
    return resp

def _get_filename_from_headers(s: str) -> str:
    """
    extract filename from content disposition header
    """
    return re.search('filename="(.*)";', s).groups()[0]

def download(url: str) -> None:
    """
    download tab file at url. save with name from site.
    save to directory at save_to
    """
    resp = _download_bytes(url)
    fn = _get_filename_from_headers(resp.headers['content-disposition'])
    with open(fn, 'wb+') as f:
        f.write(resp.content)


def get_urls(inf: str) -> List[str]:
    """
    Get urls from input file (inf). Accepts text files
    """
    files = []
    with open(inf, 'r') as f:
        for line in f: 
            files.append(clean_urls(line))
    return files

def clean_urls(filename: str) -> List[str]:
    """
    Remove any training newlines from filenames
    """
    return filename.replace('\r','').replace('\n','')

def get_parser() -> ArgumentParser:
    """
    Get parser
    Parser provides script argument descriptions and help messaging
    """
    parser = ArgumentParser(description='Download tabs')
    parser.add_argument('input', nargs=1, type=str)
    return parser

if __name__ == '__main__':
    args = get_parser().parse_args()

    file = args.input[0]    # argparse returns single element list for input
    urls = get_urls(file)
    success = []

    for url in urls:
        try:
            download(url)
            success.append(url)
        except KeyError:
            print(f"Missed expected header downloading: {url}")
        finally:
            print(f"Failed to download: {list(set(urls) - set(success))}")
        
