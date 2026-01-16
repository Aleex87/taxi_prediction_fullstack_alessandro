from fastapi import FastAPI , HTTPException
from pydantic import BaseModel, Field
from datetime import datetime
from zoneinfo import ZoneInfo
from typing import Literal
from taxipred.utils.constants import MODELS_PATH, DATA_PATH
import pandas as pd
import joblib
import httpx

app = FastAPI(title=" Taxi Price Prediction API")

# ----------- Load model once at the start of the app ---------

MODEL_FILE = MODELS_PATH / "random_forest_model.joblib"
model = joblib.load(MODEL_FILE)

# all the columns

FEATURE_COLUMNS = [
    "Trip_Distance_km",
    "Passenger_Count",
    "Base_Fare",
    "Per_Km_Rate",
    "Per_Minute_Rate",
    "Trip_Duration_Minutes",
    "Time_of_Day_Evening",
    "Time_of_Day_Morning",
    "Time_of_Day_Night",
    "Day_of_Week_Weekend",
    "Traffic_Conditions_Low",
    "Traffic_Conditions_Medium",
    "Weather_Rain",
    "Weather_Snow",
]


# ----------- Timezone in Sweden  ---------
TZ = ZoneInfo("Europe/Stockholm")

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

async def osrm_route_metrics(
    start_lat: float, start_lon: float, end_lat: float, end_lon: float
    ) -> tuple[float, float, list[list[float]]]:
        url = f"https://router.project-osrm.org/route/v1/driving/{start_lon},{start_lat};{end_lon},{end_lat}"
        params = {"overview": "full", "geometries": "geojson"}

        async with httpx.AsyncClient(timeout=10.0) as client:
            response = await client.get(url, params=params)
            response.raise_for_status()
            data = response.json()

        if data.get("code") != "Ok" or not data.get("routes"):
            raise HTTPException(status_code=400, detail="Routing failed with OSRM.")
        
        route = data["routes"][0]
        distance_km = route["distance"] / 1000.0
        duration_min = route["duration"] / 60.0

        coords_lonlat = route["geometry"]["coordinates"]
        route_latlon = [[lat,lon] for lon , lat in coords_lonlat]
        
        return distance_km, duration_min, route_latlon


# ----------- Define time/days/traffic   ---------

def now_time_features(now: datetime) -> dict:
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

    traffic = {"Traffic_Conditions_Low": 0, "Traffic_Conditions_Medium": 0}

    # Assume generally lower traffic in the weekend
    if is_weekend:
        if 12 <= hour <= 18:
            traffic["Traffic_Conditions_Medium"] = 1 
        else: 
            traffic["Traffic_Conditions_Low"] = 1
    else:
        # weekday
        if 7<= hour <= 9 or 16 <= hour <= 18:
            # high traffic
            pass
        elif 11 <= hour <= 13: 
            traffic["Traffic_Conditions_Medium"] = 1
        else:
            traffic["Traffic_Conditions_Low"] = 1
    
    return{
        "Day_of_Week_Weekend": is_weekend,
        **time_of_day,
        **traffic,
    }


# ----------- API   ---------
# User will select:
WeatherType = Literal["Clear", "Rain", "Snow"]

# validation with pydantic:

class PredictRequest(BaseModel):
    pickup_address: str = Field(..., min_length=3)
    dropoff_address: str = Field(..., min_length=3)
    weather : WeatherType = "Clear"
    passenger_count : int = Field(1, ge= 1, le=8)

class PredictResponse(BaseModel):
    predicted_price: float
    distance_km : float
    duration_min : float
    pickup_lat : float
    pickup_lon : float
    dropoff_lat : float
    dropoff_lon : float
    route : list[list[float]]

# endpoint:

@app.get("/check")
def works_check():
    return {"satus": "ok"}


@app.post("/predict", response_model=PredictResponse)
async def predict_price(request: PredictRequest) -> PredictResponse:
    
    # Geocode
    
    pickup_lat, pickup_lon = await geocode_address(request.pickup_address) 
    dropoff_lat, dropoff_lon = await geocode_address(request.dropoff_address)
    
    # Rout from OSRM

    distance_km, duration_min, route_latlon = await osrm_route_metrics(
    pickup_lat, pickup_lon, dropoff_lat, dropoff_lon
)


    # Time 

    now = datetime.now(TZ)
    time_features = now_time_features(now)

    # Weather (Clear is the base)
    weather_features = {"Weather_Rain": 0 , "Weather_Snow": 0}
    if request.weather == "Rain":
        weather_features["Weather_Rain"] = 1 
    elif request.weather == "Snow":
        weather_features["Weather_Snow"] = 1
    
    # Rates

    base_fare = 3.0
    per_km_rate = 1.2
    per_minute_rate = 0.3

    # Imput 

    model_input = {
        "Trip_Distance_km" : distance_km,
        "Passenger_Count" : float(request.passenger_count),
        "Base_Fare" : base_fare,
        "Per_Km_Rate" : per_km_rate,
        "Per_Minute_Rate" : per_minute_rate,
        "Trip_Duration_Minutes" : duration_min,
        **time_features,
        **weather_features,

    }

    input_df = pd.DataFrame([model_input])
    input_df = input_df.reindex(columns=FEATURE_COLUMNS, fill_value=0.0)

    # predict
    pred = model.predict(input_df)[0]

    return PredictResponse(
        predicted_price=round(float(pred),2),
        distance_km=round(float(distance_km), 2),
        duration_min=round(float(duration_min), 1),
        pickup_lat=float(pickup_lat),
        pickup_lon=float(pickup_lon),
        dropoff_lat=float(dropoff_lat),
        dropoff_lon=float(dropoff_lon),
        route=route_latlon
        
    )


