import streamlit as st
from geopy.geocoders import Nominatim
import folium
from streamlit_folium import st_folium

st.set_page_config(page_title="City Finder", layout="wide")
st.title("🌍 World City Explorer")

city_name = st.text_input("Kisi bhi sheher ka naam likhen:", placeholder="e.g. Karachi, London")

if city_name:
    geolocator = Nominatim(user_agent="my_explorer_app")
    location = geolocator.geocode(city_name, addressdetails=True, language='en')

    if location:
        details = location.raw['address']
        country = details.get('country', 'N/A')
        lat, lon = location.latitude, location.longitude

        st.success(f"📍 City: {city_name.title()} | Country: {country}")

        # Map display
        m = folium.Map(location=[lat, lon], zoom_start=12)
        folium.Marker([lat, lon], popup=city_name).add_to(m)
        st_folium(m, width=900, height=500)
    else:
        st.error("Sheher nahi mil saka!")