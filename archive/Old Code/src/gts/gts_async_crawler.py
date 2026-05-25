import requests
from bs4 import BeautifulSoup
import re
import asyncio
import aiohttp
import time
import pandas as pd
import tqdm

def get_number_of_pages():

    url = f'https://gts.jo/en/product/search?search=%20&page=1'

    response = requests.get(url)
    soup = BeautifulSoup(response.text, parser='lxml', features='lxml')

    a_tags = soup.find_all('a', href=True)

    result_text = soup.find('div', class_='results').text

    reslt_regex = re.search(r'(?<=\()\d+ \w+(?=\))', result_text)
    max_search_pages = int(reslt_regex.group(0).split()[0])
    return max_search_pages

semaphor = asyncio.Semaphore(10)

def get_links_in_page(text):
    unique_links = set()
    soup = BeautifulSoup(text, parser='lxml', features='lxml')
    a_tags = soup.find_all('a', href=True)

    for a in a_tags:
        link = a.get_attribute_list('href')[0]
        if 'https://gts.jo' in link:
            unique_links.add(link)
    return unique_links


async def fetch(session, url):
    async with semaphor:
        try:
            async with session.get(url) as response:
                text = await response.text()
                return text
        except Exception as e:
            print(f'[ERROR] : {url} -> {e}')
            return None



async def crawl_gts():
    number_of_pages = get_number_of_pages()
    # number_of_pages = 10
    urls = []
    base_url = 'https://gts.jo/en/product/search?search=%20&page='

    for i in range(number_of_pages):
        new_url = ''.join([base_url,str(i + 1)])
        urls.append(new_url)

    # print(urls)
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64)",
        "Accept-Language": "en-US,en;q=0.9",
    }

    results_html = []

    async with aiohttp.ClientSession(headers= headers) as session:
        tasks = [fetch(session,url) for url in urls]

        with tqdm.tqdm(total=number_of_pages, desc='GTS Crawler', ncols=100) as pbar:

            for task in asyncio.as_completed(tasks):
                result = await task
                results_html.append(result)
                pbar.update(1)

            pbar.close()

    df = pd.Series(results_html)
    df.to_csv('gts_crawl.csv')



asyncio.run(crawl_gts())

