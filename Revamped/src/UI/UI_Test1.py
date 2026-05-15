import sys
from pathlib import Path

root_path = Path(__file__).resolve().parents[1]
if str(root_path) not in sys.path:
    sys.path.append(str(root_path))

import data_scripts.search_engine as search_engine
import streamlit as st
import asyncio
import aiohttp
from io import BytesIO
from PIL import Image

st.set_page_config(

    page_title="One Place",
    layout='wide',

)

if 'search_engine' not in st.session_state:
    st.session_state['search_engine'] = search_engine.SearchEngine()
if 'top_k' not in st.session_state:
    st.session_state['top_k'] = 8
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
    st.session_state['max_price'] = 500

# UI Test Layout
st.header("ONEplace")
st.header("NO WHERE ELSE!")
top_k = st.sidebar.slider('top_k', min_value=1, max_value=50, value=10, step=1)
max_concurrent_calls = st.sidebar.slider('max_concurrent_calls', min_value=1, max_value=10, value=5, step=1)
in_stock = st.sidebar.checkbox('In Stock Only')
price_range = st.sidebar.slider('Price Range', min_value=0, max_value=40000, value=(100, 500), step=100)
min_price, max_price = price_range

if top_k != st.session_state['top_k']:
    st.session_state['top_k'] = top_k

if max_concurrent_calls != st.session_state['max_concurrent_calls']:
    st.session_state['max_concurrent_calls'] = max_concurrent_calls

if in_stock != st.session_state['in_stock']:
    st.session_state['in_stock'] = in_stock

if min_price != st.session_state['min_price']:
    st.session_state['min_price'] = min_price
if max_price != st.session_state['max_price']:
    st.session_state['max_price'] = max_price

search_query = st.text_input("Search for a product:")


# --- ASYNC IMAGE FETCHING LOGIC ---

async def fetch_image(session, url, semaphore):
    """Fetches a single image asynchronously and converts it for Streamlit."""
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
    """Gathers all image fetch tasks and runs them concurrently."""
    semaphore = asyncio.Semaphore(semaphore_count)

    async with aiohttp.ClientSession() as session:
        # Create a list of tasks for all URLs
        tasks = [fetch_image(session, url, semaphore) for url in urls]
        # asyncio.gather runs them all at the exact same time
        return await asyncio.gather(*tasks)


if search_query:
    st.session_state['query'] = search_query

# Display Results
if st.button("Search"):
    products = st.session_state['search_engine'].search_query(st.session_state['query'], st.session_state['top_k'],
                                                              st.session_state['in_stock'],
                                                              min_price=st.session_state['min_price'],
                                                              max_price=st.session_state['max_price'])
    # for product in products:
    #     print(product)

    # 1. Extract all URLs from our results
    image_urls = [item["image_url"] for item in products]

    # 2. Show a loading spinner while we fetch them asynchronously
    with st.spinner("Searching..."):
        # asyncio.run() blocks the script until all async tasks finish
        downloaded_images = asyncio.run(fetch_all_images(image_urls, st.session_state['max_concurrent_calls']))

    st.session_state['products'] = products
    st.session_state['downloaded_images'] = downloaded_images
    st.session_state['has_results'] = True

if st.session_state['has_results']:
    cols = st.columns(3)

    for index, item in enumerate(st.session_state['products']):
        col_index = index % 3

        with cols[col_index]:
            with st.container(border=True):

                st.image(st.session_state['downloaded_images'][index])
                st.markdown(f"#### {item["product_name"]}")

                missing_flags = ['<null>', 'No Description', '_']

                current_desc = item.get('product_description')
                current_specs = item.get('specs')
                # Description filtering
                if current_desc in missing_flags:

                    if current_specs in missing_flags:
                        st.markdown("*Go to website to see more info.*")
                    else:
                        if len(str(current_specs)) > 100:
                            st.markdown(f"{current_specs[:100]}...")
                        else:
                            st.markdown(f"{current_specs}")
                else:
                    if len(str(current_desc)) > 100:
                        st.markdown(f"{current_desc[:100]}...")
                    else:
                        st.markdown(current_desc)

                if item.get("original_price") >= item.get("price"):
                    st.markdown(
                        f"##### {item['price']:.0f} JOD  |                      [{item['store']}]({item['url']})")
                else:
                    st.markdown(
                        f"##### {item['original_price']:.0f} JOD  |             [{item['store']}]({item['url']})")
