import pandas as pd
import scraper
import aiohttp
import asyncio
import crawler
from tqdm.asyncio import tqdm_asyncio

async def scrap_custom_list(urls, max_concurrent_requests = 5):
    semaphore = asyncio.Semaphore(max_concurrent_requests)

    async with aiohttp.ClientSession() as session:
        tasks = []

        for url in urls:
            task = scraper.scrap_url(session, semaphore, url)
            tasks.append(task)

        results = await tqdm_asyncio.gather(*tasks, desc='Scraping urls')
        return results


async def crawl_urls(urls, max_concurrent_requests = 5):
    semaphore = asyncio.Semaphore(max_concurrent_requests)

    async with aiohttp.ClientSession() as session:
        tasks = []

        for url in urls:
            task = crawler.crawl_base_url(session, semaphore, url)
            tasks.append(task)

        results = await tqdm_asyncio.gather(*tasks, desc='Crawling urls')
        return results


if __name__ == '__main__':
    custom_urls = ['https://compujordan.com/pc-and-laptops/laptops/asus-tuf-gaming-f16-laptop-intel-core-i7-14650hx-nvidia-rtx-5060-8gb-gddr7-16gb-ram-512gb-ssd-16-wuxga-165hz-gaming-laptop',
                   'https://compujordan.com/pc-and-laptops/laptops/acer-nitro-v-15-intel-core-i9-13900h-rtx-5050-8gb-ddr7-15-6-165hz-gaming-laptop',
                   'https://compujordan.com/pc-and-laptops/laptops/lenovo-ideapad-slim-3-intel-core-i5-13420h-8gb-ddr5-512gb-ssd-15-3-fhd-ips-laptop']


    base_urls = crawler.get_base_urls()
    # base_test = base_urls[:3]

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
    df.to_csv('../../data/compujordan/compujordan_crawl.csv')

