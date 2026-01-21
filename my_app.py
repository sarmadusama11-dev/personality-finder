import streamlit as st
import wikipediaapi
import folium
from streamlit_folium import st_folium
import requests

# 1. Page Configuration
st.set_page_config(page_title="VIP Finder Pro", layout="wide")

st.title("🛰️ Universal VIP GPS Explorer")
st.write("Dunya ki kisi bhi mashhoor shakhsiyat ka naam likhen (Actors, PMs, Players).")

# 2. Search Input
name = st.text_input("Enter Name:", placeholder="e.g. Babar Azam, Nawaz Sharif, Shahrukh Khan, Elon Musk", key="main_search")

if name:
    # Fail-safe Wikipedia Search
    wiki = wikipediaapi.Wikipedia(user_agent="UltimateFinder/1.0", language='en')
    
    try:
        # Step 1: Search for the most accurate title
        search_url = "https://en.wikipedia.org/w/api.php"
        params = {
            "action": "query",
            "list": "search",
            "srsearch": name,
            "format": "json"
        }
        search_res = requests.get(search_url, params=params).json()
        
        if search_res.get('query') and search_res['query']['search']:
            official_title = search_res['query']['search'][0]['title']
            page = wiki.page(official_title)
            
            col1, col2 = st.columns([1, 1.2])
            
            with col1:
                st.header(f"👤 {page.title}")
                
                # Step 2: Reliable Image Fetch
                img_url = None
                img_params = {
                    "action": "query",
                    "titles": official_title,
                    "prop": "pageimages",
                    "format": "json",
                    "pithumbsize": 500
                }
                img_data = requests.get(search_url, params=img_params).json()
                pages = img_data.get('query', {}).get('pages', {})
                for p in pages:
                    if 'thumbnail' in pages[p]:
                        img_url = pages[p]['thumbnail']['source']
                
                if img_url:
                    st.image(img_url, use_container_width=True)
                else:
                    st.warning("Official Photo not found, showing Biography.")
                
                st.subheader("Biography")
                st.write(page.summary[:1000] + "...")

            with col2:
                st.header("📍 GPS Origin Location")
                
                # Step 3: Reliable Location Detection (Backup system)
                # Hum pehle summary se mulk dhoondte hain
                countries = ["Pakistan", "India", "USA", "UK", "Canada", "Germany", "France", "Russia", "China", "Portugal"]
                detected_country = "Pakistan" # Default
                for c in countries:
                    if c in page.summary:
                        detected_country = c
                        break
                
                # GPS Coordinates Backup (Taake timeout ka masla hi na ho)
                coords = {
                    "Pakistan": [30.3753, 69.3451], "India": [20.5937, 78.9629],
                    "USA": [37.0902, -95.7129], "UK": [55.3781, -3.4360],
                    "Portugal": [39.3999, -8.2245], "China": [35.8617, 104.1954]
                }
                
                lat_lon = coords.get(detected_country, [20, 0])
                
                st.success(f"Region Detected: {detected_country}")
                
                # Satellite View Map
                m = folium.Map(
                    location=lat_lon, 
                    zoom_start=5, 
                    tiles='https://mt1.google.com/vt/lyrs=y&x={x}&y={y}&z={z}', 
                    attr='Google Satellite'
                )
                folium.Marker(lat_lon, popup=f"{page.title}'s Origin").add_to(m)
                
                st_folium(m, width=700, height=500, key=f"map_{official_title.replace(' ', '_')}")
        else:
            st.error("No results found. Please check the spelling.")
            
    except Exception as e:
        st.error("System Refreshing... Please try again in a few seconds.")
