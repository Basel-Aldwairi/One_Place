import pandas as pd
import aiohttp
from tqdm.asyncio import tqdm_asyncio
import asyncio
import argparse
from dataclasses import dataclass
from typing import Any

import scraper_compujordan
import scraper_orientalstore
import scraper_citycenter
import crawler_compujordan
import crawler_orientalstore
import crawler_citycenter



class ArgumentsError(Exception):
    pass


def parse_args():
    parser = argparse.ArgumentParser(
        description='Async Scraper and Crawler.\n'"NOTE : store 'all' and operation 'both' are currently not supported.")
    parser.add_argument('-s', '--store', default='all', help='''
    Select Store to scrap or crawl:
    all : all stores (default)
    cj : compujordan
    os : oriental store
    ''')
    parser.add_argument('-o', '--operation', default='both', help='''
    Select Operation:
    b : both (default)
    s : scrap
    c : crawl''')
    parser.add_argument('-m', '--maxurls', default='all', help='''
    Select Max number of urls to scrap:
    all : all urls (default)
    ''')
    return parser.parse_args()


@dataclass
class Store:
    name: str
    scraper_module: Any
    crawler_module: Any
    crawl_csv_path: str
    products_csv_path: str


STORES = {
    'cj': Store(
        name='Compu Jordan',
        crawler_module=crawler_compujordan,
        scraper_module=scraper_compujordan,
        crawl_csv_path='../../data/compujordan/compujordan_crawl.csv',
        products_csv_path='../../data/compujordan/compujordan_products.csv',
    ),
    'os': Store(
        name='Oriental Store',
        crawler_module=crawler_orientalstore,
        scraper_module=scraper_orientalstore,
        crawl_csv_path='../../data/oriental_store/oriental_store_crawl.csv',
        products_csv_path='../../data/oriental_store/oriental_store_products.csv'
    ),

    'cc': Store(
        name='City Center',
        crawler_module=crawler_citycenter,
        scraper_module=scraper_citycenter,
        crawl_csv_path='../../data/citycenter/city_center_crawl.csv',
        products_csv_path='../../data/citycenter/city_center_products.csv'
    ),
}


async def scrap_products(store_module: Store, urls: list[str], categories: list[str], max_concurrent_requests: int = 5):
    semaphore = asyncio.Semaphore(max_concurrent_requests)

    async with aiohttp.ClientSession() as session:
        tasks = []

        for index in range(len(urls)):
            url = urls[index]
            category = categories[index]
            task = store_module.scraper_module.scrap_url(session, semaphore, url, category)
            tasks.append(task)

        results = await tqdm_asyncio.gather(*tasks, desc='Scraping urls')
        return results


def scrap_all(store_module: Store, max_urls: str = 'all'):
    df = pd.read_csv(store_module.crawl_csv_path)
    if max_urls != 'all':
        try:
            df = df.head(int(max_urls))
        except ValueError as e:
            raise ArgumentsError(f"max_urls must either be 'all' or an integer") from e

    urls = df['urls'].to_list()
    categories = df['categories'].to_list()

    products = asyncio.run(scrap_products(store_module, urls, categories))

    valid_products = [p for p in products if p is not None]

    df_products = pd.DataFrame(valid_products)
    df_products.to_csv(store_module.products_csv_path, index=False)


async def crawl_urls(store_module: Store, urls: list[str], max_concurrent_requests: int = 5):
    semaphore = asyncio.Semaphore(max_concurrent_requests)

    async with aiohttp.ClientSession() as session:
        tasks = []

        for url in urls:
            task = store_module.crawler_module.crawl_base_url(session, semaphore, url)
            tasks.append(task)

        results = await tqdm_asyncio.gather(*tasks, desc='Crawling urls')
        return results


def crawl_all(store_module: Store, max_urls:str='all'):
    base_urls = store_module.crawler_module.get_base_urls()
    if max_urls != 'all':
        try:
            base_urls = base_urls[:int(max_urls)]
        except ValueError as e:
            raise ArgumentsError(f"max_urls must either be 'all' or an integer") from e

    crawl_results = asyncio.run(crawl_urls(store_module,base_urls))

    all_urls = {}
    for result in crawl_results:
        for url, categories in result.items():

            if url not in all_urls:
                all_urls[url] = categories
            else:
                all_urls[url].update(categories)

    crawl_dict = {
        'urls': [],
        'categories': [],
    }
    for url, categories in all_urls.items():
        crawl_dict['urls'].append(url)
        crawl_dict['categories'].append(categories)

    df = pd.DataFrame.from_dict(crawl_dict)
    df.to_csv(store_module.crawl_csv_path, index=False)


if __name__ == '__main__':

    args = parse_args()

    try:
        store = STORES[args.store]
    except KeyError as e:
        raise ArgumentsError(f"store argument must be one of {list(STORES.keys())}")

    operation = args.operation

    if operation in {'c', 'both'}:
        crawl_all(store, max_urls=args.maxurls)

    if operation in {'s', 'both'}:
        scrap_all(store, max_urls=args.maxurls)

