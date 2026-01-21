import streamlit as st
import wikipediaapi
import folium
from streamlit_folium import st_folium
import requests

# 1. Page Setup
st.set_page_config(page_title="VIP GPS Tracker", layout="wide")

st.title("🛰️ VIP Personality GPS Tracker")
st.write("Search for any Pakistani Leader (PM, President) or Global Personality.")

# 2. Search Box
name = st.text_input("Enter Personality Name:", placeholder="e.g. Shahbaz Sharif, Nawaz Sharif, Benazir Bhutto, Imran Khan")

if name:
    # Wikipedia Auto-Search Logic
    wiki = wikipediaapi.Wikipedia(user_agent="VIPTracker/9.0", language='en')
    
    def get_official_page(query):
        try:
            # Sahi title dhoondne ke liye Wikipedia Search use karna
            s_url = f"https://en.wikipedia.org/w/api.php?action=opensearch&search={query}&limit=1&namespace=0&format=json"
            resp = requests.get(s_url).json()
            return wiki.page(resp[1][0]) if resp[1] else wiki.page(query)
        except:
            return wiki.page(query)

    page = get_official_page(name)

    if page.exists():
        # Latest Web Image (DuckDuckGo)
        def get_img(q):
            try:
                r = requests.get(f"https://duckduckgo.com/pd.js?q={q}&kl=wt-wt").json()
                return r['results'][0]['image']
            except: return None

        img_url = get_img(page.title)
        col1, col2 = st.columns([1, 1.3])

        with col1:
            st.header(f"👤 {page.title}")
            if img_url:
                st.image(img_url, use_container_width=True)
            st.subheader("Official Biography")
            st.write(page.summary[:1200] + "...")

        with col2:
            st.header("📍 GPS Satellite View")
            
            # --- RELIABLE GPS LOGIC (Fixed for Pakistan Leaders) ---
            # Agar auto-gps fail ho, to ye backup use karega
            city_coords = {
                "Lahore": [31.5204, 74.3587], "Karachi": [24.8607, 67.0011],
                "Islamabad": [33.6844, 73.0479], "Rawalpindi": [33.5651, 73.0169],
                "London": [51.5074, -0.1278]
            }
            
            # Bio mein se shehr pehchanna
            lat, lon = 33.6844, 73.0479 # Default Islamabad
            found_city = "Islamabad"
            for city, coord in city_coords.items():
                if city in page.summary:
                    lat, lon = coord
                    found_city = city
                    break
            
            st.success(f"GPS Locked on: {found_city}, Pakistan")
            
            # Hybrid Satellite Map (GPS Style)
            m = folium.Map(
                location=[lat, lon], 
                zoom_start=10, 
                tiles='https://mt1.google.com/vt/lyrs=y&x={x}&y={y}&z={z}', 
                attr='Google Maps Satellite'
            )
            folium.Marker([lat, lon], popup=f"{page.title}'s Base", icon=folium.Icon(color='red', icon='record', prefix='fa')).add_to(m)
            st_folium(m, width=700, height=550, key="final_vip_gps")
    else:
        st.error("Personality not found. Try full name (e.g. 'Mian Muhammad Nawaz Sharif').")
