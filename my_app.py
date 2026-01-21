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
name = st.text_input("Enter Personality Name:", placeholder="e.g. Elon Musk, Cristiano Ronaldo, Amitabh Bachchan")

if name:
    wiki = wikipediaapi.Wikipedia(user_agent="FinalProject/5.0", language='en')
    page = wiki.page(name)

    if page.exists():
        img_url = get_latest_image(page.title)
        
        # Profile Header
        st.header(f"👤 {page.title}")
        
        col1, col2 = st.columns([1, 1.2])

        with col1:
            if img_url:
                st.image(img_url, use_container_width=True)
            else:
                st.info("Image not available.")

        with col2:
            summary = page.summary[:1500]
            # DOB Extraction
            dob_match = re.search(r"born\s+([0-9]+\s+[A-Za-z]+\s+[0-9]{4}|[A-Za-z]+\s+[0-9]+,\s+[0-9]{4})", summary)
            dob = dob_match.group(1) if dob_match else "Not found in summary"
            
            st.subheader("📌 Basic Information")
            st.write(f"**Date of Birth:** {dob}")
            
            st.subheader("📖 Biography")
            st.write(summary + "...")

        st.markdown("---")
        
        # --- IMPROVED LOCATION LOGIC ---
        st.subheader(f"🌍 Origin: {page.title}'s Country")

        # Bari list taake sahi mulk pakra jaye
        countries_data = {
            "United States": [37.0902, -95.7129], "USA": [37.0902, -95.7129], "America": [37.0902, -95.7129],
            "India": [20.5937, 78.9629], "Pakistan": [30.3753, 69.3451],
            "Portugal": [39.3999, -8.2245], "Argentina": [-38.4161, -63.6167],
            "United Kingdom": [55.3781, -3.4360], "UK": [55.3781, -3.4360], "England": [55.3781, -3.4360],
            "Canada": [56.1304, -106.3468], "Germany": [51.1657, 10.4515],
            "France": [46.2276, 2.2137], "Turkey": [38.9637, 35.2433],
            "South Africa": [-30.5595, 22.9375], "Australia": [-25.2744, 133.7751],
            "Brazil": [-14.2350, -51.9253], "Spain": [40.4637, -3.7492]
        }

        # Default: Agar kuch na mile to World View (0,0)
        center = [20, 0]
        detected_country = "Global"

        # Wikipedia ki pehli 200 words mein mulk dhoondna
        short_bio = page.summary[:500]
        for country, coords in countries_data.items():
            if country in short_bio:
                center = coords
                detected_country = country
                break
        
        st.info(f"Map showing: {detected_country}")

        # Colorful Google Maps Style
        m = folium.Map(
            location=center, 
            zoom_start=4 if detected_country != "Global" else 2, 
            tiles='https://mt1.google.com/vt/lyrs=m&x={x}&y={y}&z={z}', 
            attr='Google'
        )
        folium.Marker(location=center, popup=f"Location: {detected_country}").add_to(m)
        
        st_folium(m, width=1200, height=500, key=f"map_{name}")

    else:
        st.error("Personality not found. Please try another name.")
