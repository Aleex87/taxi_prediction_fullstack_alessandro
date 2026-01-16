from fastapi import FastApi
from pydantic import BaseModel, Field
from datetime import datetime
from zoneinfo import ZoneInfo
from typing import Literal
from taxipred.utils.constants import MODELS_PATH, DATA_PATH
import pandas as pd
import joblib
import httpx

app = FastApi(title=" Taxi Price Prediction API")

# ----------- Load model once at the start of the app ---------

MODEL_FILE = MODELS_PATH / "random_forest_model.joblib"
model = joblib.load(MODEL_FILE)


# ----------- Timezone in Sweden  ---------
TZ = ZoneInfo("Europe/Sewden")

# ----------- Function Geocoding   ---------
# Out source !!!

async def geocode_address(address: str) -> tuple[float, float]:

    url = "https://nominatim.openstreetmap.org/search"
    params = {"q" : address, "format": "json", "limit": 1}

    headers = {"User-Agent": "taxipred-student-project"}

    async with httpx.AsyncClient(timeout=10.0) as client:
        
        response = await client.get(url, params=params, headers=headers)
        response.raise_for_status()
        data = response.json()

        if not data:
            raise HTTPException(status_code=400, detail=f"Address not found: {address}")
        
        lat = float(data[0]["lat"])
        lon = float(data[0]["lon"])
        return lat, lon 

async def osrm_route_metrics(start_lat: float, start_lon: float, end_lat: float, end_lon: float) -> tuple[float, float]:
        url = f"https://router.project-osrm.org/route/v1/driving/{start_lon},{start_lat};{end_lon},{end_lat}"
        params = {"overview": "false"}

        async with httpx.AsyncClient(timeout=10.0) as client:
            response = await client.get(url, params=params)
            response.raise_for_status()
            data = response.json()

        if data.get("code") != "Ok" or not data.get("routes"):
            raise HTTPException(status_code=400, detail="Routing failed with OSRM.")
        
        route = data["routes"][0]
        distance_km = route["distance"] / 1000.0
        duration_min = route["distance"] / 60.0
        
        return distance_km, duration_min


# ----------- Define time/days/traffic   ---------

def time_features(now: datetime) -> dict:
    hour = now.hour
    weekday = now.weekday()
    is_weekend = 1 if weekday >= 5 else 0

# Dfining -> Morning: 05-11, Afternoon is baseline (drop_first), Evening: 17-21, Night: 22-04
    time_of_day = {"Time_of_Day_Morning": 0, "Time_of_Day_Evening": 0, "Time_of_Day_Night": 0}

    # aftenoon will be the zeros
    if 5 <= hour <= 11:
        time_of_day["Time_of_Day_Morning"] = 1
    elif 17 <= hour <= 21:
        time_of_day["Time_of_Day_Evening"] = 1
    elif hour >= 22 or hour <= 4:
        time_of_day["Time_of_Day_Night"] = 1
    
    # Defining -> Traffic condition 

    traffic = {"Treffic_Condition_Low": 0, "Traffic_Condition_Medium": 0}

    # Assume generally lower traffic in the weekend
    if is_weekend:
        if 12 <= hour <= 18:
            traffic["Traffic_Condition_Medium"] = 1 
        else: 
            traffic["Treffic_Condition_Low"] = 1
    else:
        # weekday
        if 7<= hour 9 or 16 <= hour <= 18:
            # high traffic
            pass
        elif 11 <= hour <= 13: 
            traffic["Traffic_Condition_Medium"] = 1
        else:
            traffic["Treffic_Condition_Low"] = 1
    
    return{
        "Day_of_Week_Weekend": is_weekend,
        **time_of_day,
        **traffic,
    }


# ----------- API   ---------
# User will select:
WeatherType = Literal["Clear", "Rain", "Snow"]






# print(MODELS_PATH)
# print((MODELS_PATH / "random_forest_model.joblib").exists())

# print(DATA_PATH)
# print((DATA_PATH / "taxi_trip_pricing.csv").exists())

