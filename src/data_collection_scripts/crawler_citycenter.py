import requests
from bs4 import BeautifulSoup
import re

# City Center URL
shop_url = 'https://citycenter.jo/'

# Returns all the menu categories, used for crawling over the menus
def get_base_urls():

    # GET request and parsing
    response = requests.get(shop_url).text
    soup = BeautifulSoup(response, parser='lxml', features='lxml')

    # Citycenter menu items all have different IDs and Classes
    # To get all the base urls, the best solution I found is to itterate over all the list items,
    # And take the valid base urls
    all_list_items = soup.find_all('li')

    # List items that are counted as menu items
    valid_list_items = [li for li in all_list_items if li.get_attribute_list('id') and 'menu_url_' in li.get_attribute_list('id')[0]]

    # Iterate over all list items and save the urls in a list
    base_urls = []

    for li in valid_list_items:
        a = li.find_all('a')[0]
        url = a.get_attribute_list('href')[0]

        # Valid href in a
        if shop_url in url:
            base_urls.append(url)

    # Return all base urls that will be used in crawling
    return base_urls

# Crawl a base url and return a dictionary with the urls and the breadcrumbs as categoreis
async def crawl_base_url(session, semaphore,  base_url):

    async with semaphore:

        # Dictionary of urls as keys and a set breadcrumbs as values
        all_urls = {}
        page_url_addition = '?limit=100&page='

        num_pages_url = base_url + page_url_addition + str(1)
        try:
            # Async GET request
            async with session.get(num_pages_url) as response:
                html = await response.text()

            # Parsing
            soup = BeautifulSoup(html, parser='lxml', features='lxml')

            # Find number of pages in the category to crawl over
            num_pages_tag = soup.find('div', class_='results')
            num_pages = int(re.findall(r'(?<=\()\d+', num_pages_tag.text)[0]) if num_pages_tag else 1

            # The url that will iterate over the page counter
            search_base_url = base_url + page_url_addition
            # print(search_base_url)

            # Iterate over every page in that category
            for i in range(1, num_pages + 1):
                # Debugging, will replace with tqdm later on
                # print(f'{base_url} : {i}/{num_pages}')

                # GET request and Parsing
                search_url = search_base_url + str(i)
                async with session.get(search_url) as response:
                    html = await response.text()

                soup = BeautifulSoup(html, parser='lxml', features='lxml')

                # Get breadcrumbs to be set as categories
                breadcrumb_tag = soup.find('ul', class_='breadcrumb')
                breadcrumbs = set([li.text.strip() for li in breadcrumb_tag.find_all('li')][1:])

                # Get every item on the page
                all_caption_tags = soup.find_all('div', class_='caption')
                # print(len(all_caption_tags))
                # Iterate over every item
                for caption in all_caption_tags:
                    # Get item url
                    a_tag = caption.find('a', href=True)
                    url = a_tag.get_attribute_list('href')[0]

                    # parse item url without the breadcrumbs
                    product_name_url = url.split('/')[-1].split('?')[0]
                    final_url = str(shop_url + product_name_url)

                    # If existing item, update categories
                    if final_url in all_urls:
                        all_urls[final_url].update(breadcrumbs)

                    # If new item, add with the found breadcrumbs
                    else:
                        all_urls[final_url] = breadcrumbs

            # Return all urls and categories
            return all_urls

        # Error handling
        except Exception as e:
            # print(f'failed to crawl {base_url} : {e}')
            return all_urls