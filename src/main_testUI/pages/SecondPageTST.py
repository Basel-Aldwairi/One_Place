import sys
import os
import warnings
from pathlib import Path
import time

# Catch the specific __path__ warnings
warnings.filterwarnings("ignore", message=".*Accessing.*__path__.*")
warnings.filterwarnings("ignore", category=UserWarning, module="transformers")

import transformers

transformers.logging.set_verbosity_error()

import asyncio
import aiohttp
from io import BytesIO
from PIL import Image
import streamlit as st

root_path = Path(__file__).resolve().parents[2]
if str(root_path) not in sys.path:
    sys.path.append(str(root_path))

import models.search_engine as search_engine

current_dir = os.path.dirname(os.path.realpath(__file__))

logo_tab_img_path = os.path.join(current_dir, "../processor_logo.png")
logo_tab_img = Image.open(logo_tab_img_path)

st.set_page_config(page_title="Search - ONEplace",
                   page_icon=logo_tab_img,
                   layout='wide')


@st.cache_resource
def load_engine():
    return search_engine.SearchEngine()


engine = load_engine()

if 'top_k' not in st.session_state:
    st.session_state['top_k'] = 1000
if 'query' not in st.session_state:
    st.session_state['query'] = ""
if 'max_concurrent_calls' not in st.session_state:
    st.session_state['max_concurrent_calls'] = 5
if 'has_results' not in st.session_state:
    st.session_state['has_results'] = False
if 'products' not in st.session_state:
    st.session_state['products'] = []
if 'downloaded_images' not in st.session_state:
    st.session_state['downloaded_images'] = []
if 'in_stock' not in st.session_state:
    st.session_state['in_stock'] = False
if 'min_price' not in st.session_state:
    st.session_state['min_price'] = 0
if 'max_price' not in st.session_state:
    st.session_state['max_price'] = 40000

# Filters
st.sidebar.header("Filters")
st.session_state['in_stock'] = st.sidebar.checkbox('In Stock Only', value=st.session_state['in_stock'])

prices_ranges = [0, 25, 50, 100, 150, 200, 300, 500, 750, 1000, 1250, 1500, 2000, 4000, 10000, 20000, 45000]
price_range = st.sidebar.select_slider('Price (JOD)', options=prices_ranges, value=(0, 4000))
st.session_state['min_price'], st.session_state['max_price'] = price_range

# Admin Controls
with st.sidebar.expander("Admin Controls"):
    st.session_state['top_k'] = st.slider('Max Results (top_k)', 1, 1000, st.session_state['top_k'])
    st.session_state['max_concurrent_calls'] = st.slider('Concurrent Calls', 1, 10,
                                                         st.session_state['max_concurrent_calls'])

logo_path = os.path.join(current_dir, "../oneplace_logo10.gif")

st.image(logo_path)
st.title("Search Inventory")


# IMAGE ASYNC
async def fetch_image(session, url, semaphore):
    async with semaphore:
        try:
            async with session.get(url) as response:
                if response.status == 200:
                    data = await response.read()
                    return Image.open(BytesIO(data))
                return None
        except Exception:
            return None


async def fetch_all_images(urls, semaphore_count):
    semaphore = asyncio.Semaphore(semaphore_count)
    async with aiohttp.ClientSession() as session:
        tasks = [fetch_image(session, url, semaphore) for url in urls]
        return await asyncio.gather(*tasks)


def search():
    pass


cols = st.columns(2)
with cols[0]:
    search_query = st.text_input("What are you looking for?", placeholder="e.g., RTX 4090, Ryzen 7...")
with cols[1]:
    search_button = st.button("Search")

# EXECUTE SEARCH
if search_button:

    if search_query:
        with st.spinner("Scanning local stores..."):
            search_time = time.time()
            st.session_state['query'] = search_query
            products = engine.search_query(
                st.session_state['query'],
                st.session_state['top_k'],
                st.session_state['in_stock'],
                min_price=st.session_state['min_price'],
                max_price=st.session_state['max_price']
            )

            search_time = time.time() - search_time

            print()
            print()
            print(f'Query : {st.session_state['query']}')
            print(f'Number of products : {len(products)}')
            print(f'Number of concurent GET requests : {st.session_state['max_concurrent_calls']}')
            print(f'Search Time : {search_time:.5f}')

            image_download_time = time.time()
            image_urls = [item.get("image_url", "") for item in products]
            downloaded_images = asyncio.run(fetch_all_images(image_urls, st.session_state['max_concurrent_calls']))

            image_download_time = time.time() - image_download_time

            print(f'Image Download Time : {image_download_time:.5f}')

    st.session_state['products'] = products
    st.session_state['downloaded_images'] = downloaded_images
    st.session_state['has_results'] = True

# DISPLAY RESULTS
if st.session_state['has_results']:
    st.divider()
    st.subheader(f"Results for '{st.session_state['query']}'")

    cols = st.columns(3)

    for index, item in enumerate(st.session_state['products']):
        col_index = index % 3

        with cols[col_index]:
            with st.container(border=True):

                img = st.session_state['downloaded_images'][index]
                if img:
                    st.image(img, width="content")
                else:
                    st.markdown("*Image unavailable*")

                st.markdown(f"#### {item.get('product_name', 'Unknown Product')}")

                # Description Filtering
                missing_flags = ['<null>', 'No Description', '_', '', None, 'nan']
                current_desc = str(item.get('product_description'))
                current_specs = str(item.get('specs'))

                if current_desc in missing_flags:
                    if current_specs in missing_flags:
                        st.markdown("*Go to website to see more info.*")
                    else:
                        full_specs = str(current_specs)
                        if len(full_specs) > 100:
                            st.markdown(f"{full_specs[:100]}...")
                        else:
                            st.markdown(f"{full_specs}")
                else:
                    full_desc = str(current_desc)
                    if len(full_desc) > 100:
                        st.markdown(f"{full_desc[:100]}...")
                    else:
                        st.markdown(full_desc)

                in_stock = item.get('in_stock', False)
                st.text(f'In Stock : {in_stock}')
                st.divider()

                # HTML/CSS for Price
                price = item.get('price', 0)
                original = item.get('original_price', price)
                store_url = item.get('url', '#')
                store_name = item.get('store', 'View Store')

                if original > price:
                    pricing_html = f"""
                    <div style='display: flex; justify-content: space-between; align-items: flex-end;'>
                        <div>
                            <span style='color: gray; text-decoration: line-through; font-size: 0.9em;'>{original:.0f} JOD</span><br>
                            <span style='color: #03C0CE; font-weight: bold; font-size: 1.2em;'>{price:.0f} JOD</span>
                        </div>
                        <a href='{store_url}' target='_blank' style='text-decoration: none; color: white; background-color: #03C0CE; padding: 4px 8px; border-radius: 4px; font-size: 0.9em;'>{store_name} ➔</a>
                    </div>
                    """
                else:
                    pricing_html = f"""
                    <div style='display: flex; justify-content: space-between; align-items: flex-end;'>
                        <span style='font-weight: bold; font-size: 1.2em;'>{price:.0f} JOD</span>
                        <a href='{store_url}' target='_blank' style='text-decoration: none; color: white; background-color: #03C0CE; padding: 4px 8px; border-radius: 4px; font-size: 0.9em;'>{store_name} ➔</a>
                    </div>
                    """
                st.markdown(pricing_html, unsafe_allow_html=True)
