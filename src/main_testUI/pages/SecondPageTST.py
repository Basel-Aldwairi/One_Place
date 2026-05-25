import sys
from pathlib import Path
import asyncio
import aiohttp
from io import BytesIO
from PIL import Image
import streamlit as st
import os

root_path = Path(__file__).resolve().parents[2]
if str(root_path) not in sys.path:
    sys.path.append(str(root_path))

import models.search_engine as search_engine

st.set_page_config(page_title="Search - ONEplace", layout='wide')

# --- INITIALIZE SESSION STATE ---
if 'search_engine' not in st.session_state:
    st.session_state['search_engine'] = search_engine.SearchEngine()
if 'top_k' not in st.session_state:
    st.session_state['top_k'] = 100
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
    st.session_state['top_k'] = st.slider('Max Results (top_k)', 1, 100, st.session_state['top_k'])
    st.session_state['max_concurrent_calls'] = st.slider('Concurrent Calls', 1, 10,
                                                         st.session_state['max_concurrent_calls'])

current_dir = os.path.dirname(os.path.realpath(__file__))
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
    search_query = st.text_input("What are you looking for?",placeholder="e.g., RTX 4090, Ryzen 7...")
with cols[1]:
    search_button = st.button("Search")

# EXECUTE SEARCH
if search_button:

    if search_query:
        st.session_state['query'] = search_query
    products = st.session_state['search_engine'].search_query(
        st.session_state['query'],
        st.session_state['top_k'],
        st.session_state['in_stock'],
        min_price=st.session_state['min_price'],
        max_price=st.session_state['max_price']
    )

    with st.spinner("Scanning local stores..."):

        image_urls = [item.get("image_url", "") for item in products]
        downloaded_images = asyncio.run(fetch_all_images(image_urls, st.session_state['max_concurrent_calls']))


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
                missing_flags = ['<null>', 'No Description', '_', '', None]
                current_desc = item.get('product_description')
                current_specs = item.get('specs')

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
                            <span style='color: #ff4b4b; font-weight: bold; font-size: 1.2em;'>{price:.0f} JOD</span>
                        </div>
                        <a href='{store_url}' target='_blank' style='text-decoration: none; color: white; background-color: #ff4b4b; padding: 4px 8px; border-radius: 4px; font-size: 0.9em;'>{store_name} ➔</a>
                    </div>
                    """
                else:
                    pricing_html = f"""
                    <div style='display: flex; justify-content: space-between; align-items: flex-end;'>
                        <span style='font-weight: bold; font-size: 1.2em;'>{price:.0f} JOD</span>
                        <a href='{store_url}' target='_blank' style='text-decoration: none; color: white; background-color: #2e2e38; padding: 4px 8px; border-radius: 4px; font-size: 0.9em;'>{store_name} ➔</a>
                    </div>
                    """
                st.markdown(pricing_html, unsafe_allow_html=True)