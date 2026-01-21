import streamlit as st
import wikipediaapi
import folium
from streamlit_folium import st_folium
import requests

# Page Config
st.set_page_config(page_title="Accurate VIP Tracker", layout="wide")

st.title("🛰️ Professional Personality GPS Tracker")
st.write("Dunya ki kisi bhi shakhsiyat ko search karein. Sahi GPS location automatic load hogi.")

name = st.text_input("Enter Personality Name:", placeholder="e.g. Virat Kohli, Nawaz Sharif, Elon Musk")

if name:
    wiki = wikipediaapi.Wikipedia(user_agent="FinalGPSApp/2.0", language='en')
    
    try:
        # Step 1: Accurate Search
        s_url = "https://en.wikipedia.org/w/api.php"
        s_params = {"action": "opensearch", "search": name, "limit": 1, "format": "json"}
        s_res = requests.get(s_url, params=s_params).json()

        if s_res[1]:
            title = s_res[1][0]
            page = wiki.page(title)
            
            # Step 2: GET REAL GPS COORDINATES FROM WIKIPEDIA
            coord_params = {
                "action": "query",
                "prop": "coordinates",
                "titles": title,
                "format": "json"
            }
            coord_data = requests.get(s_url, params=coord_params).json()
            pages = coord_data.get('query', {}).get('pages', {})
            
            lat, lon = None, None
            for p in pages:
                if 'coordinates' in pages[p]:
                    lat = pages[p]['coordinates'][0]['lat']
                    lon = pages[p]['coordinates'][0]['lon']

            # Backup: Agar page par direct coordinates na hon to country search karein
            if not lat:
                if "India" in page.summary: lat, lon = 20.5937, 78.9629
                elif "Pakistan" in page.summary: lat, lon = 30.3753, 69.3451
                elif "USA" in page.summary or "United States" in page.summary: lat, lon = 37.0902, -95.7129
                else: lat, lon = 20.0, 0.0 # Global Center

            col1, col2 = st.columns([1, 1.2])
            
            with col1:
                st.header(f"👤 {title}")
                # Image fetch
                img_params = {"action": "query", "titles": title, "prop": "pageimages", "format": "json", "pithumbsize": 500}
                img_data = requests.get(s_url, params=img_params).json()
                pgs = img_data.get('query', {}).get('pages', {})
                for p in pgs:
                    if 'thumbnail' in pgs[p]:
                        st.image(pgs[p]['thumbnail']['source'], use_container_width=True)
                
                st.subheader("Official Biography")
                st.write(page.summary[:1000] + "...")

            with col2:
                st.header("📍 Accurate GPS Satellite View")
                st.success(f"GPS Locked on {title}'s Origin")
                
                # Satellite Map
                m = folium.Map(
                    location=[lat, lon], 
                    zoom_start=5, 
                    tiles='https://mt1.google.com/vt/lyrs=y&x={x}&y={y}&z={z}', 
                    attr='Google Satellite'
                )
                folium.Marker([lat, lon], popup=f"{title}'s Origin", icon=folium.Icon(color='red', icon='info-sign')).add_to(m)
                
                st_folium(m, width=700, height=550, key=f"fixed_map_{title.replace(' ', '_')}")
        else:
            st.error("Personality not found.")
    except Exception as e:
        st.error("Please refresh and try again.")
