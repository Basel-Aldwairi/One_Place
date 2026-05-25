import pandas as pd
import scraper
import aiohttp
import asyncio
import crawler
from tqdm.asyncio import tqdm_asyncio

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

def scrap_all():
    df = pd.read_csv('../../../data/compujordan/compujordan_crawl.csv')

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


def crawl_all():
    base_urls = crawler.get_base_urls()
    # base_test = [base_urls[20]]

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

    # crawl_all()
    scrap_all()




