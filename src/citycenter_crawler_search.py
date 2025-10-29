import requests
from bs4 import BeautifulSoup
import time
import pandas as pd
import re

start = 'https://citycenter.jo/product/search?search=%20&page=1'
response = requests.get(start).text
soup = BeautifulSoup(response, parser='lxml', features='lxml')
max_pages = soup.find('div', class_='results').text
max_pages = int(re.findall(r'\(.*\)', max_pages)[0][1:-1].split()[0])


patterns = ['https://citycenter.jo/',
            'https://citycenter.jo/product/search?search']

visited = set()
visited.add(start)
max_depth = 100
start_time = time.time()
num_links_found = 1

page_iter = 1
print(f'[INFO] : start with link#{start}')

while page_iter <= max_pages:
    current_link = f'https://citycenter.jo/product/search?search=%20&page={page_iter}'
    response = requests.get(current_link)
    new_link_found = False
    print(f'[INFO] : Page = {page_iter} / {max_pages} : {current_link}')
    soup = BeautifulSoup(response.text, parser='lxml', features='lxml')

    all_links = soup.find_all('a', href=True)

    for link_text in all_links:
        link = link_text.get_attribute_list('href')[0]
        valid_link = patterns[0] in link

        if valid_link and link not in visited:
            num_links_found += 1
            visited.add(link)
            print(f'[INFO Page = {page_iter} / {max_pages}] : link #{num_links_found} : {link}')

    page_iter += 1

finish_time = time.time() - start_time
print(f'[INFO] : finished in {finish_time:.2f}')


def pattern_exists(link, pattern):
    return pattern in link

len(visited)

all_found_links = list(visited)

df_dict = {
    'Links': all_found_links
}

df = pd.DataFrame(df_dict)

df.head()

df.to_csv('all_found_links_search.csv')

