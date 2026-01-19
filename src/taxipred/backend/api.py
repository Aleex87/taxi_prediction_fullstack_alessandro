from fastapi import FastAPI
from pydantic import BaseModel, Field
from datetime import datetime
from zoneinfo import ZoneInfo
from typing import Literal
from taxipred.utils.constants import MODELS_PATH, FEATURE_COLUMNS, USD_TO_SEK, CURRENCY
from taxipred.backend.services.routing import geocode_address, osrm_route_metrics
from taxipred.backend.services.features import now_time_features


import pandas as pd
import joblib
import httpx

app = FastAPI(title=" Taxi Price Prediction API")

# ----------- Timezone in Sweden  ---------
TZ = ZoneInfo("Europe/Stockholm")

# ----------- Load model once at the start of the app ---------

MODEL_FILE = MODELS_PATH / "random_forest_model.joblib"
model = joblib.load(MODEL_FILE)

  
# Lock with Literal so the User can select:
WeatherType = Literal["Clear", "Rain", "Snow"]

# Validation with pydantic:

class PredictRequest(BaseModel):
    pickup_address: str = Field(..., min_length=3)
    dropoff_address: str = Field(..., min_length=3)
    weather : WeatherType = "Clear"
    passenger_count : int = Field(1, ge= 1, le=8)

class PredictResponse(BaseModel):
    predicted_price_sek: float
    predicted_price_usd: float
    currency: str
    distance_km: float
    duration_min: float
    pickup_lat: float
    pickup_lon: float
    dropoff_lat: float
    dropoff_lon: float
    route: list[list[float]]

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
    
    # --- Pricing rate assumptions (design choice) ---
    # The ML model was trained using these pricing-related features:
    # Base_Fare, Per_Km_Rate, and Per_Minute_Rate.
    # In a real taxi system, these rates may vary by provider, city, time, or policy.
    # Since the user cannot know the exact tariff rates at request time, we set fixed
    # These values come from the median values computed in model_dev.ipynb.

    base_fare = 3.5
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

    # ---------------- Predict ----------------

    pred_usd = float(model.predict(input_df)[0])
    pred_sek = pred_usd * USD_TO_SEK

    return PredictResponse(
        predicted_price_sek=round(pred_sek, 2),
        predicted_price_usd=round(pred_usd, 2),
        currency=CURRENCY,
        distance_km=round(float(distance_km), 2),
        duration_min=round(float(duration_min), 1),
        pickup_lat=float(pickup_lat),
        pickup_lon=float(pickup_lon),
        dropoff_lat=float(dropoff_lat),
        dropoff_lon=float(dropoff_lon),
        route=route_latlon,
    )



