import streamlit as st
import wikipediaapi
import folium
from streamlit_folium import st_folium
import requests

# 1. Page Config
st.set_page_config(page_title="Global Personality Explorer", layout="wide")

st.title("🌟 Global Personality Explorer")
st.write("Search any famous personality to see their latest photo and origin country on the map.")

# 2. Search Function for Latest Images
def get_latest_image(query):
    try:
        url = f"https://duckduckgo.com/pd.js?q={query}&kl=wt-wt"
        res = requests.get(url).json()
        return res['results'][0]['image'] 
    except:
        return None

# 3. Input Box
name = st.text_input("Enter Personality Name:", placeholder="e.g. Cristiano Ronaldo, Imran Khan, Elon Musk")

if name:
    wiki = wikipediaapi.Wikipedia(user_agent="FinalProject/3.0", language='en')
    page = wiki.page(name)

    if page.exists():
        img_url = get_latest_image(name)
        col1, col2 = st.columns([1, 1.2])

        with col1:
            st.header(f"Profile: {page.title}")
            if img_url:
                st.image(img_url, caption=f"Latest Image of {page.title}", use_container_width=True)
            else:
                st.info("Image not found on web. Showing biography...")
            
            st.subheader("Biography")
            st.write(page.summary[:1000] + "...")

        with col2:
            st.header("🌍 Origin Country Map")
            
            # 4. Improved Country Detection Logic
            country_name = "Pakistan" # Default
            countries_coords = {
                "Pakistan": [30.3753, 69.3451],
                "India": [20.5937, 78.9629],
                "USA": [37.0902, -95.7129],
                "UK": [55.3781, -3.4360],
                "Portugal": [39.3999, -8.2245],
                "Argentina": [-38.4161, -63.6167],
                "Canada": [56.1304, -106.3468],
                "Germany": [51.1657, 10.4515],
                "France": [46.2276, 2.2137],
                "Turkey": [38.9637, 35.2433]
            }

            for c in countries_coords.keys():
                if c in page.summary:
                    country_name = c
                    break
            
            st.success(f"Detected Country: {country_name}")
            center = countries_coords.get(country_name, [20, 0])
            
            # 5. Professional Map Rendering (English Labels)
            # 'CartoDB positron' tiles labels ko English mein rakhte hain aur view clean hota hai
            m = folium.Map(
                location=center, 
                zoom_start=5, 
                tiles='CartoDB positron'
            )
            
            # Professional Marker
            folium.Marker(
                location=center, 
                popup=f"Origin: {country_name}",
                tooltip="Click for info",
                icon=folium.Icon(color='red', icon='info-sign')
            ).add_to(m)
            
            # Display Map
            st_folium(m, width=700, height=500, key=f"map_{country_name}")

    else:
        st.error("Personality not found. Please try another name.")
