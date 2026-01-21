import streamlit as st
import wikipediaapi
from geopy.geocoders import Nominatim
import folium
from streamlit_folium import st_folium
import requests
import time

# Page Configuration
st.set_page_config(page_title="Personality Explorer", layout="wide")

st.title("🌟 Global Personality Explorer")
st.write("Search any famous personality to see their official photo and origin country on the map.")

name = st.text_input("Enter Personality Name:", placeholder="e.g. Cristiano Ronaldo, Imran Khan, Elon Musk")

if name:
    # Wikipedia API setup
    wiki = wikipediaapi.Wikipedia(user_agent="PersonalityApp/1.2", language='en')
    page = wiki.page(name)

    if page.exists():
        # 1. Official Image Fetching Logic
        def get_wiki_image(title):
            try:
                formatted_title = title.replace(" ", "_")
                api_url = f"https://en.wikipedia.org/w/api.php?action=query&titles={formatted_title}&prop=pageimages&format=json&pithumbsize=600"
                data = requests.get(api_url).json()
                pages = data['query']['pages']
                for pid in pages:
                    return pages[pid]['thumbnail']['source']
            except:
                return None

        image_url = get_wiki_image(page.title)

        # UI Columns
        col1, col2 = st.columns([1, 1.2])

        with col1:
            st.header(f"Profile: {page.title}")
            if image_url:
                st.image(image_url, caption=f"Photo of {page.title}", use_container_width=True)
            else:
                st.warning("Official photo not found on Wikipedia. Displaying Bio only.")
            
            st.subheader("Biography")
            st.write(page.summary[:1000] + "...")

        with col2:
            st.header("🌍 Origin Country Map")
            try:
                # 2. Fixed Map Logic with Timeout
                geolocator = Nominatim(user_agent="explorer_map_fix_v5", timeout=15)
                
                # Detecting Country from Bio
                target_country = "Pakistan" # Default
                countries = ["Pakistan", "India", "USA", "United Kingdom", "Portugal", "Argentina", "Canada", "Germany", "France", "Turkey", "Saudi Arabia"]
                for c in countries:
                    if c in page.summary:
                        target_country = c
                        break
                
                # Finding Coordinates
                location = geolocator.geocode(target_country)
                
                if location:
                    st.success(f"Detected Origin: {target_country}")
                    # Creating the Map
                    m = folium.Map(location=[location.latitude, location.longitude], zoom_start=4)
                    folium.Marker(
                        [location.latitude, location.longitude], 
                        popup=f"{target_country}",
                        tooltip=f"Origin of {page.title}"
                    ).add_to(m)
                    
                    # Displaying the Map
                    st_folium(m, width=600, height=450, key="personality_map")
                else:
                    st.error("Could not locate the country on map. Please refresh.")
            except Exception as e:
                st.error("Map service is taking too long. Please click the 'Search' button again.")
    else:
        st.error("❌ Personality not found. Check your spelling.")
