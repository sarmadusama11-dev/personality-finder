import streamlit as st
import wikipediaapi
import folium
from streamlit_folium import st_folium
import requests

# 1. Page Config
st.set_page_config(page_title="Global Personality Explorer", layout="wide")

st.title("🌟 Global Personality Explorer")
st.write("Search any famous personality to see their latest photo and GPS Satellite location.")

# 2. Search Function for Latest Images (DuckDuckGo Logic)
def get_latest_image(query):
    try:
        url = f"https://duckduckgo.com/pd.js?q={query}&kl=wt-wt"
        res = requests.get(url).json()
        return res['results'][0]['image'] 
    except:
        return None

# 3. Input Box
name = st.text_input("Enter Personality Name:", placeholder="e.g. Virat Kohli, Nawaz Sharif, Cristiano Ronaldo")

if name:
    # Wikipedia setup
    wiki = wikipediaapi.Wikipedia(user_agent="FinalProject/3.0", language='en')
    
    # Sahi page dhoondne ke liye search logic
    search_url = f"https://en.wikipedia.org/w/api.php?action=opensearch&search={name}&limit=1&namespace=0&format=json"
    resp = requests.get(search_url).json()
    
    if resp[1]:
        page = wiki.page(resp[1][0])
        
        if page.exists():
            # Image fetch karna
            img_url = get_latest_image(page.title)

            col1, col2 = st.columns([1, 1.2])

            with col1:
                st.header(f"Profile: {page.title}")
                if img_url:
                    st.image(img_url, caption=f"Latest Image of {page.title}", use_container_width=True)
                else:
                    st.info("No official image found. Showing biography.")
                
                st.subheader("Biography")
                st.write(page.summary[:1000] + "...")

            with col2:
                st.header("📍 GPS Satellite View")
                
                # --- DYNAMIC GPS LOGIC (From Code 2) ---
                city_coords = {
                    "Lahore": [31.5204, 74.3587], "Karachi": [24.8607, 67.0011],
                    "Islamabad": [33.6844, 73.0479], "Rawalpindi": [33.5651, 73.0169],
                    "London": [51.5074, -0.1278], "Mumbai": [19.0760, 72.8777],
                    "New Delhi": [28.6139, 77.2090], "Lisbon": [38.7223, -9.1393],
                    "Madrid": [40.4168, -3.7038], "New York": [40.7128, -74.0060]
                }
                
                # Default coordinates (Pakistan Center) agar kuch na miley
                lat, lon = 30.3753, 69.3451 
                found_location = "Origin Region"

                # Bio mein se shehr ya mulk pehchanna
                for city, coord in city_coords.items():
                    if city in page.summary:
                        lat, lon = coord
                        found_location = city
                        break
                
                # Agar shehr nahi mila to mulk dhoondo
                countries = {"Pakistan": [30.3753, 69.3451], "India": [20.5937, 78.9629], "Portugal": [39.3999, -8.2245], "USA": [37.0902, -95.7129]}
                if found_location == "Origin Region":
                    for c, co in countries.items():
                        if c in page.summary:
                            lat, lon = co
                            found_location = c
                            break

                st.success(f"GPS Locked on: {found_location}")

                # Hybrid Satellite Map (GPS Style)
                m = folium.Map(
                    location=[lat, lon], 
                    zoom_start=8, 
                    tiles='https://mt1.google.com/vt/lyrs=y&x={x}&y={y}&z={z}', 
                    attr='Google Maps Satellite'
                )
                folium.Marker(
                    [lat, lon], 
                    popup=f"{page.title}'s Location", 
                    icon=folium.Icon(color='red', icon='record', prefix='fa')
                ).add_to(m)
                
                st_folium(m, width=700, height=500, key=f"map_{page.title.replace(' ', '_')}")

    else:
        st.error("Personality not found. Please try a more specific name.")
