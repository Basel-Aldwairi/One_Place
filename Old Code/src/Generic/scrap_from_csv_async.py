import pandas as pd
import aiohttp
import asyncio
import time
import tqdm

from src.citycenter.citycenter_scrap_async import scrap_citycenter
from src.gts.gts_scraper import scrap_gts_url



async def scrap_all_urls(site_func, links_path, output_path):
    df = pd.read_csv(links_path, index_col=0)
    links_list = df['URLs'].to_list()

    links_list = links_list[:100]

    len_links = len(links_list)
    scraped = []
    error = []
    error_name = []
    raw_texts = []

    start_time = time.time()

    semaphore = asyncio.Semaphore(20)

    async with aiohttp.ClientSession() as session:

        session.headers.update({
            'User-Agent': 'MyCustomAgent/1.0',
            'Accept': 'application/json'
        })

        async def bound_fetch(link):
            async with semaphore:
                try:
                    results = await site_func(session, link)
                    result = results

                    scraped.append(result)
                    # raw_texts.append((link,page_text))
                    # print(f'[INFO {i + 1} / {len_links}] : Processing link : {link}')
                except Exception as e:
                    # print(f'[ERROR {i + 1} / {len_links}] : link : {link}')
                    error.append(link)
                    error_name.append(str(e))
                    print(e)
                # finally:
                #     raw_texts.append((link,page_text))



        tasks = [asyncio.create_task(bound_fetch(link)) for link in links_list]

        with tqdm.tqdm(total=len_links, desc= 'Scraping progress', ncols=100) as pbar:

            for task in asyncio.as_completed(tasks):
                await task
                pbar.update(1)

        await asyncio.gather(*tasks)

    end_time = time.time() - start_time
    print(f'[INFO] : Time taken : {end_time:.2f} s for {len_links}')


    error_dict = {
        'links' : error,
        'error' : error_name,
    }

    df_error = pd.DataFrame(error_dict)
    # df_error.to_csv('error_links_async.csv')

    df_success = pd.DataFrame(scraped, columns=['URLs', 'product_name', 'product_tag', 'product_brand', 'status_availabity', 'currency', 'price', 'sale', 'product_description'])
    df_success.to_csv(output_path)

    df_raw_page = pd.DataFrame(raw_texts, columns=['link','html'])
    # df_raw_page.to_csv('scrapped_html_async.csv')


async def run_citycenter():
    return await scrap_all_urls(scrap_citycenter, '../citycenter/all_found_links_search.csv',
                           '../citycenter/scrapped_data.csv')

async def run_gts():
    return await scrap_all_urls(scrap_gts_url, '../gts/gts_urls.csv',
                           '../gts/scrapped_data.csv')



if __name__ == '__main__':
    pass
    # asyncio.run()
    asyncio.run(run_citycenter())