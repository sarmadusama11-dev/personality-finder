import streamlit as st
import wikipediaapi
import folium
from streamlit_folium import st_folium
import requests
from geopy.geocoders import Nominatim

# 1. Professional Page Setup
st.set_page_config(page_title="VIP Personality Locator", layout="wide")

st.title("🛰️ Global VIP Explorer & GPS Tracker")
st.write("Search for World Leaders, Actors, or Athletes to see their Bio and GPS Origin.")

# 2. Input Search
name = st.text_input("Enter Personality Full Name:", placeholder="e.g. Narendra Modi, Donald Trump, Shah Rukh Khan, Lionel Messi")

if name:
    # Wikipedia setup with higher level access
    wiki = wikipediaapi.Wikipedia(user_agent="VIPExplorer/5.0", language='en')
    page = wiki.page(name)

    if page.exists():
        # Enhanced Web Image Search (DuckDuckGo API)
        def get_vip_image(query):
            try:
                url = f"https://duckduckgo.com/pd.js?q={query}&kl=wt-wt"
                res = requests.get(url).json()
                return res['results'][0]['image']
            except:
                return None

        img_url = get_vip_image(name)

        # UI Layout
        col1, col2 = st.columns([1, 1.3])

        with col1:
            st.header(f"👤 {page.title}")
            if img_url:
                st.image(img_url, use_container_width=True, caption=f"Latest Image: {page.title}")
            
            st.subheader("Official Biography")
            # Showing more detail for VIPs
            st.write(page.summary[:1200] + "...")

        with col2:
            st.header("📍 Satellite GPS Location")
            
            # 3. High-Accuracy GPS Logic
            geolocator = Nominatim(user_agent="vip_gps_tracker_v9", timeout=25)
            
            try:
                # Priority 1: Search for origin country based on personality
                location = geolocator.geocode(f"{page.title} country")
                
                # Priority 2: Use first paragraph to detect origin
                if not location:
                    bio_snippet = page.summary.split('.')[0] + " " + page.summary.split('.')[1]
                    location = geolocator.geocode(bio_snippet)

                if location:
                    st.success(f"GPS Lock: {location.address}")
                    
                    # Professional Satellite GPS Map (Hybrid View)
                    m = folium.Map(
                        location=[location.latitude, location.longitude], 
                        zoom_start=5, 
                        tiles='https://mt1.google.com/vt/lyrs=s&x={x}&y={y}&z={z}', # Google Satellite Tiles
                        attr='Google'
                    )
                    
                    # Red GPS Marker
                    folium.Marker(
                        [location.latitude, location.longitude],
                        popup=f"Origin: {page.title}",
                        tooltip="Click for Details",
                        icon=folium.Icon(color='red', icon='record', prefix='fa')
                    ).add_to(m)

                    # Display Map
                    st_folium(m, width=750, height=550, key="vip_gps_map")
                else:
                    st.warning("GPS coordinates could not be pinpointed. Bio is loaded.")
            
            except:
                st.error("GPS server is under heavy load. Please refresh in a moment.")

    else:
        st.error("Personality not found. Please provide the full official name (e.g., 'Vladimir Putin').")
