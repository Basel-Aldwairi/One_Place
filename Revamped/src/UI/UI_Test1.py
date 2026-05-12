
import sys
from pathlib import Path

root_path = Path(__file__).resolve().parents[1]
if str(root_path) not in sys.path:
    sys.path.append(str(root_path))

import data_scripts.search_engine as search_engine
import streamlit as st

st.set_page_config(

    page_title="One Place",
    layout='wide',

)

if 'search_engine' not in st.session_state:
    st.session_state['search_engine'] = search_engine.SearchEngine(static=True)
if 'top_k' not in st.session_state:
    st.session_state['top_k'] = 8
if 'query' not in st.session_state:
    st.session_state['query'] = ""

# UI Test Layout
st.title("📍 OnePlace")
st.header("No Where Else!")
st.subheader("Find what you need, right near you.")

st.sidebar.slider('top_k', min_value=1, max_value=50, value=10, step=1)


product_names = [""] + list(inventory.keys())

col1, col2 = st.columns(2)

search_query = st.text_input("Search for a product:")

if search_query:
    st.session_state['query'] = search_query

# Display Results
if st.button("Search"):
    products = st.session_state['search_engine'].search_static(st.session_state['query'],st.session_state['top_k'])

    for product in products:
        print(product)
    #
    # st.divider()
    # st.markdown(f"### {search_query}")
    #
    # col1, col2 = st.columns(2)
    #
    # with col2:
    #     # Check if a discount exists and render the custom HTML
    #     # I used Gemini to get this HTML code :)
    #     if product["discounted_price"]:
    #         savings = product['original_price'] - product['discounted_price']
    #
    #         pricing_html = f"""
    #         <div>
    #             <span style='color: #C00000; font-size: 26px; font-weight: bold;'>JOD {product['discounted_price']:.2f}</span><br>
    #             <span style='color: #888888; text-decoration: line-through; font-size: 18px; font-weight: bold;'>JOD {product['original_price']:.2f}</span><br>
    #             <div style='background-color: #1AA31A; color: white; padding: 4px 8px; display: inline-block; font-weight: bold; margin-top: 5px; font-size: 16px; border-radius: 4px;'>
    #                 You save JOD {savings:.2f}
    #             </div>
    #         </div>
    #         """
    #         st.markdown(pricing_html, unsafe_allow_html=True)
    #
    #     else:
    #         # Standard formatting for items with no discount
    #         st.markdown(f"<span style='font-size: 20px; font-weight: bold;'>JOD {product['original_price']:.2f}</span>",
    #                     unsafe_allow_html=True)
    #
    # st.write("**Description:**")
    # st.info(product["description"])