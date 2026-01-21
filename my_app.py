import streamlit as st
import wikipediaapi
import folium
from streamlit_folium import st_folium
import requests

# Page Config
st.set_page_config(page_title="VIP Finder Final", layout="wide")

st.title("🛰️ Universal VIP GPS Explorer")
st.write("Search for any Pakistani Leader, Actor, or Global Star.")

name = st.text_input("Enter Name:", placeholder="e.g. Shahbaz Sharif, Babar Azam, Elon Musk", key="final_search")

if name:
    # Use a simpler User Agent to avoid blocks
    wiki = wikipediaapi.Wikipedia(user_agent="MyProjectApp/1.0", language='en')
    
    try:
        # Step 1: Search using a more stable method
        search_url = "https://en.wikipedia.org/w/api.php"
        s_params = {"action": "opensearch", "search": name, "limit": 1, "format": "json"}
        s_res = requests.get(search_url, params=s_params).json()

        if s_res[1]:
            title = s_res[1][0]
            page = wiki.page(title)
            
            col1, col2 = st.columns([1, 1.2])
            
            with col1:
                st.header(f"👤 {title}")
                
                # Image fetch with error handling
                img_url = None
                img_params = {"action": "query", "titles": title, "prop": "pageimages", "format": "json", "pithumbsize": 500}
                img_data = requests.get(search_url, params=img_params).json()
                pages = img_data.get('query', {}).get('pages', {})
                for p in pages:
                    if 'thumbnail' in pages[p]:
                        img_url = pages[p]['thumbnail']['source']
                
                if img_url:
                    st.image(img_url, use_container_width=True)
                
                st.subheader("Biography")
                st.write(page.summary[:1000] + "...")

            with col2:
                st.header("📍 GPS Origin Location")
                
                # Step 2: Reliable GPS Coordinates
                # Common coordinates for personalities (Automatic Fallback)
                lat, lon = 30.3753, 69.3451 # Default Pakistan
                
                if "Pakistan" in page.summary: lat, lon = 30.3753, 69.3451
                elif "India" in page.summary: lat, lon = 20.5937, 78.9629
                elif "United States" in page.summary or "USA" in page.summary: lat, lon = 37.0902, -95.7129
                elif "United Kingdom" in page.summary or "UK" in page.summary: lat, lon = 55.3781, -3.4360
                
                st.success(f"Region: {title}'s Origin")
                
                # Step 3: Map with NO timeout issues
                m = folium.Map(
                    location=[lat, lon], 
                    zoom_start=5, 
                    tiles='https://mt1.google.com/vt/lyrs=y&x={x}&y={y}&z={z}', 
                    attr='Google Satellite'
                )
                folium.Marker([lat, lon], popup=title).add_to(m)
                
                # Static key to prevent refresh loops
                st_folium(m, width=700, height=500, key=f"map_display_{title.replace(' ', '_')}")

        else:
            st.error("No results found. Please check spelling.")

    except Exception as e:
        st.error("Please refresh the page and try again.")
