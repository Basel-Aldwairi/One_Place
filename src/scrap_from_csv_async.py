import pandas as pd
import aiohttp
import asyncio
import time
import tqdm
from citycenter_scrap_async import scrap_citycenter


async def main():
    df = pd.read_csv('all_found_links_search.csv',index_col=0)
    links_list = df['Links'].to_list()

    links_list = links_list[:1]

    len_links = len(links_list)
    scraped = []
    error = []
    error_name = []
    raw_texts = []

    start_time = time.time()

    semaphore = asyncio.Semaphore(100)

    async with aiohttp.ClientSession() as session:

        session.headers.update({
            'User-Agent': 'MyCustomAgent/1.0',
            'Accept': 'application/json'
        })
        async def bound_fetch(link):
            async with semaphore:
                try:
                    results = await scrap_citycenter(session, link)
                    page_text, *result = results

                    scraped.append(result)
                    raw_texts.append((link,page_text))
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
    df_error.to_csv('error_links_async.csv')

    df_success = pd.DataFrame(scraped, columns=['link', 'product_name', 'product_description', 'currency', 'price', 'sale', 'whatsapp_number'])
    df_success.to_csv('scrapped_data_async.csv')

    df_raw_page = pd.DataFrame(raw_texts, columns=['link','html'])
    df_raw_page.to_csv('scrapped_html_async.csv')

if __name__ == '__main__':
    asyncio.run(main())