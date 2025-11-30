import requests
from bs4 import BeautifulSoup

# reg_price = 'https://citycenter.jo/computer-hardware/components-cpu-and-processor/amd-ryzen-9-9900x3d-12-core-4-4ghz-5-5-ghz-max-boost-140mb-cache-am5-desktop-processor-tray'
# old_new_price = 'https://citycenter.jo/computer-hardware/components-cpu-and-processor/amd-ryzen-9-9950x3d-16-core-4-3ghz-5-7-ghz-max-boost-132mb-cache-am5-desktop-processor-tray'
#

def scrap_citycenter(link):
    page_text = requests.get(link).text
    soup = BeautifulSoup(page_text,parser='lxml',features='lxml')

    with open('../../testing_files/cpu_html_page.txt', 'w', encoding='utf-8') as f:
        f.write(soup.prettify())

    product_name = soup.find('div', class_='tb_wt tb_wt_page_title_system tb_mb_10 display-block tb_system_page_title')
    if product_name:
        product_name = product_name.text
    else:
        return None, None, None, None, None, None, None

    product_description =  soup.find('ul', class_='a-unordered-list a-vertical a-spacing-mini')

    if product_description:
        product_description_items = product_description.find_all('li', class_='a-spacing-mini')

        product_description_list = []
        for item in product_description_items:
            product_description_list.append(item.text)

        product_description = product_description_list
    else:
        product_description = soup.find('div', class_='tb_wt tb_wt_product_field_system display-block tb_system_product_field_1').text

    product_info = soup.find('div', class_='tb_wt tb_wt_product_info_system display-inline-block tb_system_product_info')

    product_info_dt = product_info.find_all('dt')

    product_info_dt = [item.text[:-1] for item in product_info_dt]

    product_info_dd = product_info.find_all('dd')

    product_info_dd = [item.text for item in product_info_dd]

    product_info = zip(product_info_dt,product_info_dd)

    price_tag = soup.find('div', class_='price')

    reg = price_tag.find('span', class_='price-regular')

    def get_price(price_list):
        price_list = price_list.replace('\n', '').split()
        currency = price_list[0]
        price = price_list[1]
        return currency, price

    if reg:
        currency, price = get_price(reg.text)
        sale = None
    else:
        price = price_tag.find('span', class_='price-old')
        sale = price_tag.find('span', class_='price-new')
        currency, price = get_price(price.text)
        currency, sale = get_price(sale.text)

    whatsapp_button = soup.find('a', id= 'whatsapp-btn-pro')
    whatsapp_number =  whatsapp_button.get_attribute_list('href')[0][-12:]
    whatsapp_number = ''.join(['+',whatsapp_number])


    return link, product_name, product_description, currency, price, sale, whatsapp_number

