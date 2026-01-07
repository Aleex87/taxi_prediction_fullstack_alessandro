import pandas as pd 
from taxipred.utils.constants import DATA_PATH
import json
from pprint import pprint
from pydantic import BaseModel, Field

def load_cvs(filename: str) -> pd.DataFrame:


    return pd.read_cvs(DATA_PATH /filename)

def clean_data(df: pd.DataFrame) -> pd.DataFrame:


    df = df.drop_duplicates()
    df = df.dropna()
    return df


if __name__ == "__main__":
    df = load_cvs("taxi_trip_pricing.csv")
    df = clean_data(df)
    print(df.head())

