import streamlit as st
import pandas as pd
import numpy as np
import os
import json
import plotly.express as px

# Page Config must be the first Streamlit command
st.set_page_config(
    page_title="Welcome to ONEplace",
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



col1, col2 = st.columns(2)
# Dummy Values Just to visualize and test the charts
with col1:
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

with col2:

    brand_count_path = os.path.join(base_dir, 'insight_date/brand_count.json')

    with open(brand_count_path) as f:
        brand_count = json.load(f)


    brand_count_data = {
        'brands' : brand_count['brands'],
        'count' : brand_count['count'],
    }

    st.markdown("**Average Price Distribution (JOD)**")

    pie_data = pd.DataFrame(brand_count_data)
    pie_chart = px.pie(pie_data, values='count', names='brands')
    st.plotly_chart(pie_chart)

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