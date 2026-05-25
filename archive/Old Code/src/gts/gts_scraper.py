from bs4 import BeautifulSoup
import pandas as pd
import aiohttp


# url = 'https://gts.jo/en/gaming/dell'

# @scrap_all_urlls
async def scrap_gts_url(session: aiohttp.ClientSession, url):
    product_name, product_tag, product_brand, status_availabity, currency, price, sale, product_description = (None for _ in range(8))

    try:
        async with session.get(url) as response:

            page_text = await response.text()
            soup = BeautifulSoup(page_text, parser='lxml', features='lxml')

            # with open('gts_test.html', 'w', encoding='utf-8') as f:
            #     f.write(soup.prettify())

            name_tag = soup.find('div', class_='tb_wt tb_wt_page_title_system tb_mb_20 display-block tb_system_page_title')

            product_name = name_tag.find('h1').text if name_tag else None

            product_code_tag = soup.find('dd', class_='product-info product-info-code product-info-code-value')

            product_tag = product_code_tag.text if product_code_tag else None

            product_brand_tag = soup.find('dd', class_='product-info product-info-brand product-info-brand-value')

            product_brand = product_brand_tag.text if product_brand_tag else None

            status_availabity_tag = soup.find('span', class_='tb_stock_status_in_stock')

            status_availabity = status_availabity_tag.text if status_availabity_tag else None

            price = None
            sale = None
            currency = None

            price_tag = soup.find('div', class_='price')


            price_list = price_tag.text.strip().split()
            currency = price_list[0]
            price = price_list[1]
            sale = price_list[3] if len(price_list) > 2 else None

            dfs = pd.read_html(url)

            product_description_table = None

            if len(dfs) > 1:
                df = dfs[1]
                product_description_cat = df.iloc[:,0].to_list()
                product_description_value = df.iloc[:, 1].to_list()
                product_description_table = list(zip(product_description_cat,product_description_value))

            product_description_list_tag = soup.find('div', class_='panel-body tb_product_description tb_text_wrap')

            product_description_list_items = None
            if product_description_list_tag:
                product_description_list_item_tags = product_description_list_tag.find_all('li')
                product_description_list_items = [li.text.strip() for li in product_description_list_item_tags]

            product_description = []
            if product_description_table:
                product_description.extend(product_description_table)
            if product_description_list_items:
                product_description.extend(product_description_list_items)

    except Exception as e:
        pass
        # print(e)

    return url, product_name, product_tag,product_brand, status_availabity, currency, price, sale, product_description

#
# link = 'https://gts.jo/en/headset-ovling-gaming-p1-aux'
#
#
# # s = aiohttp.ClientSession()
#
# results = scrap_gts_url(s, link)
# for s in results:
#     print(s)