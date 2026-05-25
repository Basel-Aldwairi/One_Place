import pandas as pd
import time
from src.citycenter import city_center_scrap

df = pd.read_csv('../citycenter/all_found_links_search.csv', index_col=0)
links_list = df['Links'].to_list()

# links_list = links_list[:40]

len_links = len(links_list)
scraped = []
error = []
start_time = time.time()
for i, link in enumerate(links_list):
    print(f'[INFO {i+1} / {len_links}] : Processing link : {link}')
    try:
        scraped.append(city_center_scrap.scrap_citycenter(link))

    except Exception as e:
        print(f'[ERROR {i+1} / {len_links}] : link : {link}')
        error.append(link)

end_time = time.time() - start_time

print(f'[INFO] : Time taken : {end_time:.2f} s')

df_error = pd.DataFrame(error, columns=['links'])
df_error.to_csv('error_links.csv')

df_success = pd.DataFrame(scraped, columns=['link', 'product_name', 'product_description', 'currency', 'price', 'sale', 'whatsapp_number'])
df_success.to_csv('scrapped_data.csv')