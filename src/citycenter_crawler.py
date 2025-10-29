#%%
import requests
from bs4 import BeautifulSoup
import time
import pandas as pd
from collections import deque

start = 'https://citycenter.jo/'

def pattern_exists(link,pattern):
    return pattern in link

patterns = [
    'citycenter.jo/pc-and-laptops',
    'citycenter.jo/computer-hardware-monitor-and-display',
    'citycenter.jo/computer-hardware-peripherals',
    'citycenter.jo/computer-hardware-audio',
    'citycenter.jo/computer-hardware-storage',
    'citycenter.jo/computer-hardware',
    'citycenter.jo/gaming',
    'citycenter.jo/peripherals-printer-and-scanner',
    'citycenter.jo/electronics',
    'citycenter.jo/Networking'
]


visited = set()
queue = deque()
visited.add(start)
queue.append(start)
max_depth = 1000
start_time = time.time()
num_links_found = 1

current_depth = 0
print(f'[INFO] : start with link#{num_links_found} : {start}')

while queue:
    current_link = queue.popleft()
    current_depth += 1
    response = requests.get(current_link)
    new_link_found = False
    print(f'[INFO] : depth = {current_depth} / {max_depth}')
    soup = BeautifulSoup(response.text, parser='lxml',features='lxml')

    all_links = soup.find_all('a', href=True)

    for link_text in all_links:
        link = link_text.get_attribute_list('href')[0]
        valid_link = any([pattern_exists(link,pattern) for pattern in patterns])
        if valid_link and link not in visited:
            num_links_found += 1
            print(f'[INFO depth = {current_depth} / {max_depth}] : link #{num_links_found} : {link}')
            visited.add(link)
            if len(link) <= 90:
                queue.append(link)
            new_link_found = True

    if not new_link_found:
        current_depth -= 1

finish_time = time.time() - start_time
print(f'[INFO] : finished in {finish_time:.2f}')


all_found_links = list(visited)

df_dict = {
    'Links' : all_found_links
}

df = pd.DataFrame(df_dict)
df.to_csv('all_found_links.csv')
