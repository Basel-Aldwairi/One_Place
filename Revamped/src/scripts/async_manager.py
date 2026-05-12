import pandas as pd
import scraper_compujordan
import scraper_orientalstore
import aiohttp
import asyncio
import crawler_compujordan
import crawler_orientalstore
from tqdm.asyncio import tqdm_asyncio
import argparse

scraper = None
crawler = None

class ArgumentsError(Exception):
    """Raised when there is a problem with arguments"""
    pass


def parse_args():
    parser = argparse.ArgumentParser(description='Async Scraper and Crawler.\n'"NOTE : store 'all' and operation 'both' are currently not supported.")
    parser.add_argument('-s','--store',default='all',help='''
    Select Store to scrap or crawl:
    all : all stores (default)
    cj : compujordan
    os : oriental store
    ''')
    parser.add_argument('-o','--operation',default='both',help='''
    Select Operation:
    b : both (default)
    s : scrap
    c : crawl''')
    parser.add_argument('-m','--maxurls',default='all',help='''
    Select Max number of urls to scrap:
    all : all urls (default)
    ''')
    return parser.parse_args()

async def scrap_products(urls, categories, max_concurrent_requests = 5):
    semaphore = asyncio.Semaphore(max_concurrent_requests)

    async with aiohttp.ClientSession() as session:
        tasks = []

        for index in range(len(urls)):
            url = urls[index]
            category = categories[index]
            task = scraper.scrap_url(session, semaphore, url, category)
            tasks.append(task)

        results = await tqdm_asyncio.gather(*tasks, desc='Scraping urls')
        return results

def scrap_all(max_urls:str = 'all'):
    df = None
    if max_urls == 'all':
        df = pd.read_csv('../../data/compujordan/compujordan_crawl.csv')
    else:
        df = pd.read_csv('../../data/compujordan/compujordan.csv').loc[:int(max_urls)]

    urls = df['urls'].to_list()
    categories = df['categories'].to_list()

    products = asyncio.run(scrap_products(urls, categories))

    valid_products = [p for p in products if p is not None]

    df_products = pd.DataFrame(valid_products)
    df_products.to_csv('../../data/compujordan/compujordan_products.csv')


async def crawl_urls(urls, max_concurrent_requests = 5):
    semaphore = asyncio.Semaphore(max_concurrent_requests)

    async with aiohttp.ClientSession() as session:
        tasks = []

        for url in urls:
            task = crawler.crawl_base_url(session, semaphore, url)
            tasks.append(task)

        results = await tqdm_asyncio.gather(*tasks, desc='Crawling urls')
        return results


def crawl_all(max_urls = 'all'):
    base_urls = crawler.get_base_urls()
    if max_urls != 'all':
        base_urls = base_urls[:max_urls]

    crawl_results = asyncio.run(crawl_urls(base_urls))

    all_urls = {}
    for result in crawl_results:
        for url, categories in result.items():

            if url not in all_urls:
                all_urls[url] = categories
            else:
                all_urls[url].update(categories)


    crawl_dict = {
        'urls' : [],
        'categories' : [],
    }
    for url, categories in all_urls.items():
        crawl_dict['urls'].append(url)
        crawl_dict['categories'].append(categories)

    df = pd.DataFrame.from_dict(crawl_dict)
    df.to_csv('../../data/compujordan/compujordan_crawl_testing.csv')


if __name__ == '__main__':

    args = parse_args()

    store = args.store
    operation = args.operation
    max_urls = args.maxurls

    if store not in {'all', 'cj', 'os'}:
        raise ArgumentsError(f"store argument must be one of 'all', 'cj', or 'os'")

    if operation not in {'both', 'c', 's'}:
        raise ArgumentsError(f"operation argument must be one of 'both', 'c', or 's'")

    try:
        if max_urls != 'all':
            max_urls = int(max_urls)

    except ValueError as e:
        raise ArgumentsError(f"max_urls must either be 'all' or an integer") from e

    # print(f'''
    #     {store = }
    #     {operation = }
    #     {max_urls = }
    #     ''')

    if store == 'cj':
        scraper = scraper_compujordan
        crawler = crawler_compujordan
    if store == 'os':
        scraper = scraper_orientalstore
        crawler = crawler_orientalstore


    if operation == 'c':
        crawl_all()
    if operation == 's':
        scrap_all()

    # crawl_all()
    # scrap_all()




