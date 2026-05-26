import streamlit as st
import pandas as pd
import numpy as np
import os
import json
import plotly.express as px
from PIL import Image

# Page Config must be the first Streamlit command


current_dir = os.path.dirname(os.path.realpath(__file__))

logo_tab_img_path = os.path.join(current_dir, "processor_logo.png")
logo_tab_img = Image.open(logo_tab_img_path)

st.set_page_config(
    page_title="Welcome to ONEplace",
    page_icon=logo_tab_img_path,
    layout='wide',
)

current_dir = os.path.dirname(os.path.realpath(__file__))
logo_path = os.path.join(current_dir, "oneplace_logo10.gif")

st.image(logo_path)
st.markdown("<h2 style='text-align: center;'>Find what you need, exactly where you are!</h2>", unsafe_allow_html=True)
st.divider()

st.header("What is ONEplace?")
st.write("""
ONEplace is a smart inventory search engine designed to save you time, gas, and frustration. 
Instead of driving from store to store, ONEplace aggregates real-time inventory data for high-demand 
electronic and PC parts, showing you exactly who has your item in stock, locally.
""")

st.header("Platform Insights")

base_dir = os.path.dirname(os.path.abspath(__file__))

cols = st.columns(2)
# Dummy Values Just to visualize and test the charts
with cols[0]:
    st.markdown("**Indexed Inventory by Category**")
    categories = [
        {'cpu', 'processor'},
        {'gpu', 'graphics'},
        {'ram', 'memory'},
        {'ssd', 'hdd', 'storage'},
        {'power supply', 'psu'},
        {'motherboard'},
    ]
    count_categories_path = os.path.join(base_dir, 'insight_date/categories_count.json')

    with open(count_categories_path) as f:
        count_categories = json.load(f)

    category_counts = count_categories['count']
    category_names = count_categories['categories']

    chart_data = pd.DataFrame({
        "Items": category_counts,
        "Category": category_names
    }).set_index("Category")
    st.bar_chart(chart_data)

with cols[1]:
    brand_count_path = os.path.join(base_dir, 'insight_date/brand_count.json')

    with open(brand_count_path) as f:
        brand_count = json.load(f)

    brand_count_data = {
        'brands': brand_count['brands'],
        'count': brand_count['count'],
    }

    st.markdown("**Brands Pie Chart**")

    pie_data = pd.DataFrame(brand_count_data)
    pie_chart = px.pie(pie_data, values='count', names='brands')
    st.plotly_chart(pie_chart)

st.divider()

cols = st.columns(2)

with cols[0]:
    in_stock_count_path = os.path.join(base_dir, 'insight_date/in_stock_count.json')

    with open(in_stock_count_path) as f:
        in_stock_count = json.load(f)

    # in_stock_count_data = {
    #     'brands': brand_count['brands'],
    #     'count': brand_count['count'],
    # }

    st.markdown("**In Stock Pie Chart**")

    pie_data = pd.DataFrame(in_stock_count)
    pie_chart = px.pie(pie_data, values='values', names='names')
    st.plotly_chart(pie_chart)

with cols[1]:
    vendor_count_path = os.path.join(base_dir, 'insight_date/vendors_count.json')

    with open(vendor_count_path) as f:
        vendor_count = json.load(f)

    # in_stock_count_data = {
    #     'brands': brand_count['brands'],
    #     'count': brand_count['count'],
    # }

    st.markdown("**Vendor Pie Chart**")

    pie_data = pd.DataFrame(vendor_count)
    pie_chart = px.pie(pie_data, values='counts', names='vendors')
    st.plotly_chart(pie_chart)

st.divider()

cols = st.columns(2)

with cols[0]:
    discount_count_path = os.path.join(base_dir, 'insight_date/discounts_count.json')

    with open(discount_count_path) as f:
        discount_count = json.load(f)

    st.markdown("**Discount Pie Chart**")

    pie_data = pd.DataFrame(discount_count)
    pie_chart = px.pie(pie_data, values='values', names='names')
    st.plotly_chart(pie_chart)

with cols[1]:
    discounts_percentage_path = os.path.join(base_dir, 'insight_date/discounts_histogram.json')

    with open(discounts_percentage_path) as f:
        discounts_percentage = json.load(f)

    discounts_percentage_df = pd.DataFrame(discounts_percentage)

    hist = px.histogram(
        discounts_percentage_df,
        x="percentages",
        nbins=20,
        color_discrete_sequence=["#636EFA"]
    )

    st.markdown("**Distribution of Discount Percentages**")

    st.plotly_chart(hist)

st.divider()

st.header("Our Team")
st.markdown("""
* **Basel Al-Dwairi** - Lead Developer
* **Laith Al-Naimat** - UI/UX & Integrations
* **Supervised By:** Nadia Al-Rousan
""")

st.write("")

col_a, col_b, col_c = st.columns([1, 1, 1])
with col_b:
    if st.button("Begin Search", use_container_width=True, type="primary"):
        st.switch_page("pages/SecondPageTST.py")
