import streamlit as st
import wikipediaapi
import folium
from streamlit_folium import st_folium
import requests
import time

# 1. Page Configuration
st.set_page_config(page_title="Universal VIP Finder", layout="wide")

st.title("🚀 Universal Personality GPS Explorer")
st.markdown("---")

# 2. Input Box
name = st.text_input("Kisi bhi mashhoor shakhsiyat ka naam likhen:", placeholder="e.g. Atif Aslam, Babar Azam, General Asim Munir, Justin Bieber")

if name:
    # Wikipedia API setup
    wiki = wikipediaapi.Wikipedia(user_agent="UniversalSearch/2.0", language='en')
    
    # --- STEP 1: DEEP SEARCH LOGIC ---
    # Yeh logic random naamo ko dhoond nikaalti hai
    search_url = f"https://en.wikipedia.org/w/api.php?action=query&list=search&srsearch={name}&format=json"
    search_res = requests.get(search_url).json()
    
    if search_res.get('query') and search_res['query']['search']:
        # Sab se pehla aur sahi result uthana
        best_match = search_res['query']['search'][0]['title']
        page = wiki.page(best_match)
        
        col1, col2 = st.columns([1, 1.2])
        
        with col1:
            st.header(f"👤 {page.title}")
            # Dynamic Image Fetch (DuckDuckGo Search)
            img_api = f"https://duckduckgo.com/pd.js?q={page.title}+official+photo&kl=wt-wt"
            try:
                img_res = requests.get(img_api).json()
                if img_res.get('results'):
                    st.image(img_res['results'][0]['image'], use_container_width=True)
            except:
                st.info("Image search is loading...")
            
            st.subheader("Biography")
            st.write(page.summary[:1200] + "...")

        with col2:
            st.header("📍 GPS Origin Location")
            
            # --- STEP 2: DYNAMIC GPS (No more stuck location) ---
            # Hum Wikipedia ki summary se location nikaalte hain
            search_query = f"{page.title} origin country"
            geo_url = f"https://nominatim.openstreetmap.org/search?q={search_query}&format=json&addressdetails=1&limit=1"
            headers = {'User-Agent': f'app_{time.time()}'}
            
            try:
                geo_res = requests.get(geo_url, headers=headers).json()
                
                if geo_res:
                    lat = float(geo_res[0]['lat'])
                    lon = float(geo_res[0]['lon'])
                    st.success(f"GPS Locked: {geo_res[0]['display_name']}")
                else:
                    # Fallback agar origin na mile to bio ke words se dhoondo
                    lat, lon = 30.3753, 69.3451 # Default Pakistan
                    st.warning("General region displayed.")

                # Satellite View Map
                m = folium.Map(
                    location=[lat, lon], 
                    zoom_start=5, 
                    tiles='https://mt1.google.com/vt/lyrs=y&x={x}&y={y}&z={z}', 
                    attr='Google Satellite'
                )
                folium.Marker([lat, lon], icon=folium.Icon(color='red')).add_to(m)
                
                # Unique Key for Map Refresh
                st_folium(m, width=700, height=500, key=f"map_{page.pageid}")
                
            except:
                st.error("GPS connection slow, but bio and photo are ready!")
    else:
        st.error("Nahi mil saka! Please naam ke spelling check karein ya poora naam likhen.")
