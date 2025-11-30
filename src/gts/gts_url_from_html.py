from bs4 import BeautifulSoup
import pandas as pd


def parse_gts_for_urls(csv_file):
    df = pd.read_csv(csv_file)
    html_list = df.to_list()

    unique_urls = set()
    all_urls = []

    for html in html_list:

        soup = BeautifulSoup(html, parser='lxml', features='lxml')

        a_href = soup.find_all('a', href=True)

        for url in a_href:
            if 'https://gts.jo' in url:
                unique_urls.add(url)
                all_urls.append(url)




csv_file = 'gts_crawl.csv'
parse_gts_for_urls(csv_file)

