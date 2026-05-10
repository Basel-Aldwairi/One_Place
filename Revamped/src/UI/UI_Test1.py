import streamlit as st

# Dummy inventory values
inventory = {
    "MSI GeForce RTX 5090  Graphics Card": {
        "original_price": 4999.00,
        "discounted_price": 4499.00,
        "description":
            "Powered by the NVIDIA Blackwell architecture and DLSS 4."
            "Core Clocks: Extreme Performance: 2775 MHz (MSI Center) Boost: 2730 MHz",
        "in_stock": True
    },
    "AMD Ryzen 9 7900X Processor": {
        "original_price": 299.00,
        "discounted_price": None,
        "description":
            "The world's best gaming desktop processor that can deliver ultra-fast 100+ FPS performance in the world's most popular games."
            "12 Cores and 24 processing threads, based on AMD ""Zen 4"" architecture, with a max boost clock of up to 5.6 GHz and 64 MB of L3 cache.",
        "in_stock": True
    },
    "Kingston FURY Renegade G5 2TB NVMe M.2 SSD": {
        "original_price": 369.00,
        "discounted_price": 269.00,
        "description":
            "Kingston FURY Renegade G5 PCIe 5.0 NVMe M.2 SSD is for high-power users, hardware enthusiasts and gamers ready for the latest Gen 5x4 performance. With ranging speeds of up to 14,800MB/s read and 14,000MB/s write¹, its extreme performance boosts game and app load times and improves reaction time, while its exceptional design keeps it cool."
            "Unleash the full potential of your system with Kingston FURY Renegade G5 PCIe 5.0 NVMe M.2 SSD. By leveraging the latest PCIe Gen5 x4 controller and 3D TLC NAND, Kingston FURY Renegade G5 SSD offers extreme speeds of up to 14,800/14,000MB/s read/write¹.",
        "in_stock": True
    },
    "Corsair Vengeance RGB 32GB (2x16GB) DDR5 RAM": {
        "original_price": 125.00,
        "discounted_price": None,
        "description":
            "Dynamic Ten-Zone RGB Lighting: Illuminate your system with ten individually addressable, ultra-bright RGB LEDs per module, encased in a panoramic light bar for vivid RGB lighting from any viewing angle."
            "Onboard Voltage Regulation: Enables easier, more finely-tuned, and more stable overclocking through CORSAIR iCUE software than previous generation motherboard control.",
        "in_stock": False
    },
    "ASUS ROG Strix X870E-H Gaming WIFI7 ATX Motherboard": {
        "original_price": 349.00,
        "discounted_price": 249.00,
        "description":
            "AMD Socket AM5 Supports for AMD Ryzen™ 9000 & 8000 & 7000 Series Desktop Processors."
            "Memory: 4 x DIMM slots, max. 256GB, DDR5 Supports up to 8000+MT/s(OC) with Ryzen™ 9000 & 8000 & 7000 Series Processors Dual channel memory architecture Supports AMD Extended Profiles for Overclocking (EXPO™).",
        "in_stock": True
    }
}

# UI Test Layout
st.title("📍 OnePlace")
st.header("No Where Else!")
st.subheader("Find what you need, right near you.")

product_names = [""] + list(inventory.keys())

search_query = st.selectbox("Search for a product:", product_names)

# Display Results
if search_query:
    product = inventory[search_query]

    st.divider()
    st.markdown(f"### {search_query}")

    col1, col2 = st.columns(2)

    with col2:
        # Check if a discount exists and render the custom HTML
        # I used Gemini to get this HTML code :)
        if product["discounted_price"]:
            savings = product['original_price'] - product['discounted_price']

            pricing_html = f"""
            <div>
                <span style='color: #C00000; font-size: 26px; font-weight: bold;'>JOD {product['discounted_price']:.2f}</span><br>
                <span style='color: #888888; text-decoration: line-through; font-size: 18px; font-weight: bold;'>JOD {product['original_price']:.2f}</span><br>
                <div style='background-color: #1AA31A; color: white; padding: 4px 8px; display: inline-block; font-weight: bold; margin-top: 5px; font-size: 16px; border-radius: 4px;'>
                    You save JOD {savings:.2f}
                </div>
            </div> 
            """
            st.markdown(pricing_html, unsafe_allow_html=True)

        else:
            # Standard formatting for items with no discount
            st.markdown(f"<span style='font-size: 20px; font-weight: bold;'>JOD {product['original_price']:.2f}</span>",
                        unsafe_allow_html=True)

    st.write("**Description:**")
    st.info(product["description"])