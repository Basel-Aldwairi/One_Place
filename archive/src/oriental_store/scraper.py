from bs4 import BeautifulSoup
import pandas as pd
from io import StringIO

# Async scraper for Compujordan
async def scrap_url(session, semaphore, url,  categories=None):

    # Empty categories handling
    if categories is None:
        categories = set()

    async with semaphore:
        # Error handling
        try:
            # GET request of page
            # Parsing
            async with session.get(url) as response:
                html = await response.text()
                soup = BeautifulSoup(html, parser='lxml', features='lxml')

            # Product Name
            product_name_tag = soup.find('div',
                                         class_='tb_wt tb_wt_page_title_system tb_mb_10 display-block tb_system_page_title')
            product_name = product_name_tag.text if product_name_tag else 'Unknown'


            # In Stock, Product Code, Brand
            info_tag = soup.find('div', id='ProductInfoSystem_Ho7r8pnm')
            in_stock, product_code, brand = False, 'Unknown', 'Unknown'

            if info_tag:
                info_list = [info.text for info in info_tag.find_all('dd')]
                len_info_list = len(info_list)
                in_stock = True if info_list[0] == 'In Stock' else False
                product_code = info_list[1] if len_info_list > 1 else 'Unknown'
                brand = info_list[2] if len_info_list > 2 else 'Unknown'


            # Price, Current Price, Original Price, Currency
            original_price = current_price = None
            currency = 'Unknown'
            price_tag = soup.find('div', class_='price')

            # No Discount
            if price_tag:
                price_regular_tag = price_tag.find('span', class_='price-regular')
                original_price_tag = price_tag.find('span', class_='price-old')

                if price_regular_tag:
                    current_price = float(price_regular_tag.text.split()[1].replace(',', ''))

                elif original_price_tag:
                    original_price = float(original_price_tag.text.split()[1].replace(',', ''))

                    current_price_tag = price_tag.find('span', class_='price-new')
                    current_price = float(current_price_tag.text.split()[1].replace(',', ''))

                currency = price_tag.text.split()[0]

            # Descriptions - Most of the products don't have descriptions
            product_description_tag = soup.find('div', id='ProductDescriptionSystem_Bx7ALQdc')
            product_description = 'Unknown'

            if product_description_tag:
                p_tags = product_description_tag.find_all('p')
                product_description_list = [p.text for p in p_tags if p.text.strip()]
                product_description = '\n'.join(product_description_list)

            # Removing contact table, to extarct specs easier
            table_tag = soup.find_all('div', id='qoute-form-popup')
            for tt in table_tag:
                tt.decompose()

            # Specs, Properties
            found_tables = soup.find('table')
            properties = {}

            if found_tables:
                tables = pd.read_html(StringIO(soup.prettify()))
                for i in range(len(tables)):
                    df = tables[i]

                    if df.shape[1] >= 2:
                        df = df.iloc[:, :2]
                        df.columns = ['Specification', 'Value']
                        properties = {str(l[0]): str(l[1]) for l in df.to_numpy()}


            # Image URL
            thumbnail_tag = soup.find('a', class_='thumbnail')
            image_url = thumbnail_tag.get('href') if thumbnail_tag else None


            # Product Dictionary
            product_dict = {
                'product_code': product_code,
                'product_name': product_name,
                'brand': brand,
                'store': 'Oriental Store',
                'url': url,
                'image_url': image_url,

                'price': current_price,
                'original_price': original_price,
                'currency': currency,
                'in_stock': in_stock,

                'product_description': product_description,

                'categories': categories,
                'specs': properties
            }

            return product_dict


        # Error Handling
        except Exception as e:
            print(f'failed to scrap {url} : {e}')
            return None