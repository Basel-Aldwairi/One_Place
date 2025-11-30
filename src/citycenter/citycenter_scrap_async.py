import requests
import aiohttp
import asyncio
from bs4 import BeautifulSoup
# from src.Generic.scrap_from_csv_async import scrap_all_urls

# reg_price = 'https://citycenter.jo/computer-hardware/components-cpu-and-processor/amd-ryzen-9-9900x3d-12-core-4-4ghz-5-5-ghz-max-boost-140mb-cache-am5-desktop-processor-tray'
# old_new_price = 'https://citycenter.jo/computer-hardware/components-cpu-and-processor/amd-ryzen-9-9950x3d-16-core-4-3ghz-5-7-ghz-max-boost-132mb-cache-am5-desktop-processor-tray'
#

# @scrap_all_urls
async def scrap_citycenter(session : requests.Session ,link):
    try:
        async with session.get(link) as response:
            page_text = await response.text()
            soup = BeautifulSoup(page_text,parser='lxml',features='lxml')

            with open('../../testing_files/cpu_html_page.txt', 'w', encoding='utf-8') as f:
                f.write(soup.prettify())

            product_name = soup.find('div', class_='tb_wt tb_wt_page_title_system tb_mb_10 display-block tb_system_page_title')
            product_name = product_name.text if product_name else None


            product_description_ul =  soup.find('ul', class_='a-unordered-list a-vertical a-spacing-mini')
            product_description_div = soup.find('div', class_='tb_wt tb_wt_product_field_system display-block tb_system_product_field_1')
            product_description = None

            if product_description_ul:
                product_description_items = product_description_ul.find_all('li', class_='a-spacing-mini')

                product_description_list = []
                for item in product_description_items:
                    product_description_list.append(item.text)

                product_description = product_description_list
            elif product_description_div:
                product_description = product_description_div.text


            product_info = soup.find('div', class_='tb_wt tb_wt_product_info_system display-inline-block tb_system_product_info')

            if product_info:
                product_info_dt = product_info.find_all('dt')

                product_info_dt = [item.text[:-1] for item in product_info_dt]

                product_info_dd = product_info.find_all('dd')

                product_info_dd = [item.text for item in product_info_dd]


                # product_info = zip(product_info_dt,product_info_dd)

            price_tag = soup.find('div', class_='price')

            price = None
            sale = None
            currency = None
            if price_tag:
                price_regular = price_tag.find('span', class_='price-regular')

                price_old = price_tag.find('span', class_='price-old')
                price_new = price_tag.find('span', class_='price-new')



                def get_price(price_list):
                    price_list = price_list.replace('\n', '').split()
                    currency = price_list[0]
                    price = price_list[1]
                    return currency, price

                if price_regular:
                    currency, price = get_price(price_regular.text)
                    sale = None
                elif price_old:
                    price = price_old.text
                    sale = price_new.text
                    currency, price = get_price(price)
                    currency, sale = get_price(sale)


            whatsapp_button = soup.find('a', id= 'whatsapp-btn-pro')
            whatsapp_number = None
            if whatsapp_button:
                whatsapp_number =  whatsapp_button.get_attribute_list('href')[0][-12:]
                whatsapp_number = ''.join(['+',whatsapp_number])


            return page_text,link, product_name, product_description, currency, price, sale, whatsapp_number

    except Exception as e:
        print(e)
        return page_text,link, 'er', None, None, None, None, None


# @scrap_all_urls
# async def run_citycenter(session, link):
#     return await scrap_citycenter(session, link)

# asyncio.run(scrap_citycenter())