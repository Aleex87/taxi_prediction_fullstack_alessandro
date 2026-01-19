from pathlib import Path

DATA_PATH = (Path(__file__).parent.parent/"data").resolve() 

MODELS_PATH = (Path(__file__).parent.parent/"models").resolve()

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

USD_TO_SEK = 10.5  # fixed exchange rate used for this student project demo

CURRENCY = "SEK"
