from bs4 import BeautifulSoup
import time
import pandas as pd
from multiprocessing import Pool, cpu_count


def read_scraped_html(csv_path):
    read_time = time.time()

    df = pd.read_csv(csv_path, index_col=0)
    df.rename(columns={'0': 'html'}, inplace=True)
    html_list = df['html'].to_list()

    read_time = time.time() - read_time
    print(f'[INFO] : CSV File Read Time = {read_time}')

    return html_list


def parse_html(html):
    soup = BeautifulSoup(html, parser='lxml', features='lxml')

    unique_urls = set()
    a_href= soup.find_all('a', href=True)

    for a in a_href:
        url = a.get_attribute_list('href')[0].strip()
        if 'https://gts.jo' in url:
            unique_urls.add(url)

    return unique_urls


def get_urls(csv_path):

    processing_time = time.time()
    with Pool(cpu_count()) as pool:
        html_list = read_scraped_html(csv_path)

        results = pool.map(parse_html, html_list)

        processed_result = set()
        for set_result in results:
            processed_result = processed_result | set_result

    processing_time = time.time() - processing_time
    print(f'[INFO] : Processing Time with Muliprocessing on {cpu_count()} Cores = {processing_time}')

    return processed_result


csv_file = 'gts_crawl.csv'
found_urls = get_urls(csv_file)

print(f'[INFO] : Found {len(found_urls)}')

found_urls_dict = {
    'URLs' : list(found_urls)
}

df = pd.DataFrame(found_urls_dict)
df.to_csv('gts_urls.csv')
