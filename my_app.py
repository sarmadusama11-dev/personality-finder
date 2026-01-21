import streamlit as st
import wikipediaapi
import folium
from streamlit_folium import st_folium
import requests
import re

# 1. Page Config
st.set_page_config(page_title="Global Personality Explorer", layout="wide")

st.title("🌟 Global Personality Explorer")

# 2. Latest Image Function
def get_latest_image(query):
    try:
        url = f"https://duckduckgo.com/pd.js?q={query}&kl=wt-wt"
        res = requests.get(url).json()
        return res['results'][0]['image']
    except:
        return None

# 3. Input Box
name = st.text_input("Enter Personality Name:", placeholder="e.g. Cristiano Ronaldo, Nawaz Sharif, Virat Kohli")

if name:
    wiki = wikipediaapi.Wikipedia(user_agent="FinalProject/4.0", language='en')
    page = wiki.page(name)

    if page.exists():
        img_url = get_latest_image(page.title)
        
        # Profile Section
        st.header(f"👤 {page.title}")
        
        col1, col2 = st.columns([1, 1])

        with col1:
            if img_url:
                st.image(img_url, use_container_width=True)
            else:
                st.info("Image not available.")

        with col2:
            # Date of Birth nikalne ki koshish (Bio se)
            summary = page.summary[:1500]
            dob_match = re.search(r"born\s+([0-9]+\s+[A-Za-z]+\s+[0-9]{4}|[A-Za-z]+\s+[0-9]+,\s+[0-9]{4})", summary)
            dob = dob_match.group(1) if dob_match else "Not found in summary"
            
            st.subheader("📌 Basic Information")
            st.write(f"**Date of Birth:** {dob}")
            
            st.subheader("📖 Biography")
            st.write(summary + "...")

        st.markdown("---")
        
        # Map Section
        st.subheader("🌍 Origin Country Map (Colorful GPS View)")
        
        # Country Detection
        country_name = "Pakistan"
        countries_coords = {
            "Pakistan": [30.3753, 69.3451], "India": [20.5937, 78.9629],
            "USA": [37.0902, -95.7129], "UK": [55.3781, -3.4360],
            "Portugal": [39.3999, -8.2245], "Argentina": [-38.4161, -63.6167],
            "Turkey": [38.9637, 35.2433], "France": [46.2276, 2.2137]
        }
        for c in countries_coords.keys():
            if c in page.summary:
                country_name = c
                break
        
        center = countries_coords.get(country_name, [20, 0])
        
        # COLORFUL GOOGLE MAPS STYLE
        m = folium.Map(
            location=center, 
            zoom_start=5, 
            tiles='https://mt1.google.com/vt/lyrs=m&x={x}&y={y}&z={z}', 
            attr='Google'
        )
        folium.Marker(location=center, popup=f"{page.title}'s Origin: {country_name}").add_to(m)
        
        st_folium(m, width=1200, height=500, key=f"map_{page.title}")

    else:
        st.error("Personality not found. Please try another name.")
