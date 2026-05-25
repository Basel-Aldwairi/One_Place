import streamlit as st
import pandas as pd
import numpy as np
import os

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

col1, col2 = st.columns(2)
# Dummy Values Just to visualize and test the charts
with col1:
    st.markdown("**Indexed Inventory by Category**")
    chart_data = pd.DataFrame({
        "Items": [120, 85, 40, 25, 10],
        "Category": ["GPUs", "CPUs", "Motherboards", "RAM", "Power Supplies"]
    }).set_index("Category")
    st.bar_chart(chart_data)

with col2:
    st.markdown("**Average Price Distribution (JOD)**")
    hist_data = pd.DataFrame(np.random.normal(250, 50, 100), columns=["Price"])
    st.line_chart(hist_data)

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