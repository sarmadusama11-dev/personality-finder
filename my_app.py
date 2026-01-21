import streamlit as st
import wikipediaapi
import folium
from streamlit_folium import st_folium
import requests
from geopy.geocoders import Nominatim

# 1. Page Setup
st.set_page_config(page_title="Pakistan VIP Locator", layout="wide")

st.title("🛰️ Pakistan VIP GPS Explorer")
st.write("Enter the name of any Pakistani Prime Minister, President, or Leader.")

# 2. Input with Better Search
name = st.text_input("Enter Leader Name:", placeholder="e.g. Nawaz Sharif, Benazir Bhutto, Shahbaz Sharif, Quaid-e-Azam")

if name:
    # Wikipedia setup
    wiki = wikipediaapi.Wikipedia(user_agent="PakLeaderFinder/7.0", language='en')
    
    # --- AUTO-CORRECTION LOGIC ---
    # Agar Wikipedia par direct page nahi milta, to hum search karke pehla result uthatay hain
    def get_correct_page(search_query):
        try:
            # Wikipedia Search API use karke sahi title nikalna
            search_url = f"https://en.wikipedia.org/w/api.php?action=opensearch&search={search_query}&limit=1&namespace=0&format=json"
            response = requests.get(search_url).json()
            if response[1]:
                return wiki.page(response[1][0]) # Pehla sahi result
            return wiki.page(search_query)
        except:
            return wiki.page(search_query)

    page = get_correct_page(name)

    if page.exists():
        # Latest Image Search
        def get_web_image(query):
            try:
                url = f"https://duckduckgo.com/pd.js?q={query}&kl=wt-wt"
                res = requests.get(url).json()
                return res['results'][0]['image']
            except:
                return None

        img_url = get_web_image(page.title)
        col1, col2 = st.columns([1, 1.3])

        with col1:
            st.header(f"👤 {page.title}")
            if img_url:
                st.image(img_url, use_container_width=True)
            st.subheader("Official Biography")
            # Pakistan ke leaders ki details show karna
            st.write(page.summary[:1500] + "...")

        with col2:
            st.header("📍 GPS Origin View")
            
            # GPS Logic
            try:
                geolocator = Nominatim(user_agent="pak_gps_v10", timeout=15)
                # Specifically searching for their link to Pakistan
                location = geolocator.geocode("Islamabad, Pakistan") # Default for PMs
                
                # Check if birthplace is in bio
                if "Lahore" in page.summary: location = geolocator.geocode("Lahore, Pakistan")
                elif "Karachi" in page.summary: location = geolocator.geocode("Karachi, Pakistan")
                elif "Rawalpindi" in page.summary: location = geolocator.geocode("Rawalpindi, Pakistan")

                if location:
                    st.success(f"GPS Lock: {location.address}")
                    lat, lon = location.latitude, location.longitude
                else:
                    lat, lon = 30.3753, 69.3451 # Pakistan Center

                # Satellite Hybrid Map
                m = folium.Map(
                    location=[lat, lon], 
                    zoom_start=6, 
                    tiles='https://mt1.google.com/vt/lyrs=y&x={x}&y={y}&z={z}', 
                    attr='Google'
                )
                folium.Marker([lat, lon], popup=page.title, icon=folium.Icon(color='green', icon='star')).add_to(m)
                st_folium(m, width=700, height=500, key="pak_vip_map")
            except:
                st.error("GPS server timeout. Please refresh.")
    else:
        st.error("Leader not found. Try typing the full name (e.g., 'Zulfikar Ali Bhutto').")
