from zoneinfo import ZoneInfo
from typing import Literal
from datetime import datetime



# ----------- Timezone in Sweden  ---------
TZ = ZoneInfo("Europe/Stockholm")

def now_time_features(now: datetime) -> dict:
    hour = now.hour
    weekday = now.weekday()
    is_weekend = 1 if weekday >= 5 else 0

# ----------- Define time/days/traffic   ---------


# Dfining -> Morning: 05-11, Afternoon is baseline (drop_first), Evening: 17-21, Night: 22-04
    time_of_day = {"Time_of_Day_Morning": 0, "Time_of_Day_Evening": 0, "Time_of_Day_Night": 0}

    # aftenoon will be the zeros
    if 5 <= hour <= 11:
        time_of_day["Time_of_Day_Morning"] = 1
    elif 17 <= hour <= 21:
        time_of_day["Time_of_Day_Evening"] = 1
    elif hour >= 22 or hour <= 4:
        time_of_day["Time_of_Day_Night"] = 1
    
    # Defining -> Traffic condition baseline will be high

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
        # build a singol dict with all the feature
    }

