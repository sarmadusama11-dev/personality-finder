import streamlit as st
import wikipediaapi
from geopy.geocoders import Nominatim
import folium
from streamlit_folium import st_folium
import requests

# Page Configuration
st.set_page_config(page_title="Personality Finder", layout="wide")

# Main Title and Description in English
st.title("🌟 Global Personality Explorer")
st.write("Enter the name of a famous personality to discover their biography and home country.")

# English Input Box
name = st.text_input("Enter Personality Name:", placeholder="e.g. Cristiano Ronaldo, Elon Musk, Arshad Nadeem")

if name:
    # Wikipedia API setup
    wiki = wikipediaapi.Wikipedia(user_agent="PersonalityLocator/1.0", language='en')
    page = wiki.page(name)

    if page.exists():
        # Wikipedia image fetch
        def get_wiki_image(title):
            try:
                url = f"https://en.wikipedia.org/w/api.php?action=query&titles={title}&prop=pageimages&format=json&pithumbsize=500"
                response = requests.get(url).json()
                pages = response['query']['pages']
                for p in pages:
                    return pages[p]['thumbnail']['source']
            except:
                return None

        image_url = get_wiki_image(page.title)

        # UI Layout: Two columns
        col1, col2 = st.columns([1, 1])

        with col1:
            st.header(f"Profile: {page.title}")
            if image_url:
                st.image(image_url, width=350)
            else:
                st.info("No official image found on Wikipedia.")
            
            st.subheader("Biography")
            st.write(page.summary[:900] + "...")

        # Map Logic
        try:
            # Fixing the timeout and agent for better connection
            geolocator = Nominatim(user_agent="global_explorer_v3", timeout=10)
            
            # Simple country detection from summary
            target_country = "Pakistan" # Default fallback
            common_countries = ["Pakistan", "India", "USA", "UK", "Canada", "Portugal", "Argentina", "Turkey", "Germany", "France", "Brazil"]
            for c in common_countries:
                if c in page.summary:
                    target_country = c
                    break

            with col2:
                st.header(f"Origin: {target_country}")
                country_loc = geolocator.geocode(target_country)
                
                if country_loc:
                    # Professional Folium Map
                    m = folium.Map(location=[country_loc.latitude, country_loc.longitude], zoom_start=4)
                    folium.Marker(
                        [country_loc.latitude, country_loc.longitude],
                        popup=f"{page.title}'s Country",
                        tooltip="Click for info"
                    ).add_to(m)
                    
                    st_folium(m, width=600, height=450)
                else:
                    st.warning("Map connection timed out. Please try again.")
        except:
            st.error("Geography service is temporarily busy. Please refresh.")
    else:
        st.error("❌ Personality not found. Please check the spelling.")
