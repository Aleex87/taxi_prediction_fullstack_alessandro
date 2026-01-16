import requests
import streamlit as st
import folium
from streamlit_folium import st_folium

API_URL = "http://127.0.0.1:8000/predict"

st.set_page_config(page_title= "Taxi Price Prediction", layout="centered")

st.title("Taxi Price Prediction")
st.write("Enter pickup and drop-off addresses, select weather conditions and passenger count.")

with st.form("predict_form"):
    pickup_address = st.text_input("Pickup address (Point A)", value="Stockholm Centralstation")
    dropoff_address = st.text_input("Drop-off address (Point B)", value= "Gamla stan, Stockholm")

    weather = st.selectbox("Wheather", ["Clear","Rain","Snow"], index=0)
    passenger_count =st.slider("Passenger count", min_value=1, max_value=8, value=2)

    submitted = st.form_submit_button("Predict Price")

    if submitted:
        playload = {
            "pickup_address": pickup_address,
            "dropoff_address": dropoff_address,
            "weather": weather,
            "passenger_count": passenger_count,
        }

        try:
            response = requests.post(API_URL, json=playload, timeout=15)
            response.raise_for_status()
            result = response.json()

            predicted_price = result["predicted_price"]
            distance_km = result["distance_km"]
            duration_min = result["duration_min"]

            pickup_lat = result["pickup_lat"]
            pickup_lon = result["pickup_lon"]
            dropoff_lat = result["dropoff_lat"]
            dropoff_lon = result["dropoff_lon"]

            st.subheader("Prediction resutl")
            st.metric("Predicted price", f"{predicted_price:.2f}")
            st.write("Distance", f"{distance_km:.2f}")
            st.write("Duration", f"{duration_min:.1f} minutes")

# zoomable map (out source)

            center_lat = (pickup_lat + dropoff_lat) / 2
            center_lon = (pickup_lon + dropoff_lon) / 2

            taxi_map = folium.Map(location=[center_lat, center_lon], zoom_start=13)

            folium.Marker(
                location=[pickup_lat, pickup_lon],
                popup="Pickup (A)",
                tooltip="Pickup (A)",
            ).add_to(taxi_map)

            folium.Marker(
                location=[dropoff_lat, dropoff_lon],
                popup="Drop-off (B)",
                tooltip="Drop-off (B)",
            ).add_to(taxi_map)

            st.subheader("Map")
            st_folium(taxi_map, width=700, height=450)
        
        except requests.exceptions.RequestException as e:
            st.error(f"API request failed: {e}")
        except KeyError:
            st.error("Unexpected API response format. Check the backend output.")          

