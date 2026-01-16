from fastapi import FastApi
from taxipred.utils.constants import MODELS_PATH, DATA_PATH
from pydantic import BaseModel, Field
import pandas as pd
import joblib

app = FastApi(title=" Taxi Price Prediction API")

# ----------- Load model once at the start of the app ---------

MODEL_FILE = MODELS_PATH / "random_forest_model.joblib"
model = joblib.load(MODEL_FILE)




# print(MODELS_PATH)
# print((MODELS_PATH / "random_forest_model.joblib").exists())

# print(DATA_PATH)
# print((DATA_PATH / "taxi_trip_pricing.csv").exists())

