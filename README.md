# taxi_prediction_fullstack_alessandro
Full-stack ML application for predicting taxi trip prices.

## Dataset and Data Directory

This project uses a public dataset downloaded from Kaggle.

The dataset file is ignored via `.gitignore`.
To run the project locally:

1. Download the dataset from the original source (Kaggle)
2. Place the CSV file in the project `data/` directory (or the expected data folder used in the code)

## Design Choices and Assumptions

To provide a user-friendly experience, the application requires only:
- Pickup address (Point A)
- Drop-off address (Point B)
- Weather conditions (selected by the user)
- Passenger count (selected by the user)

### Automatically derived features
Some features are automatically derived at request time:
- `Time_of_Day` is computed from the current system time.
- `Day_of_Week` (weekday/weekend) is computed from the current date.
- `Traffic_Conditions` is approximated using simple time-based rules (e.g., morning and evening rush hours).

### Route distance and duration
`Trip_Distance_km` and `Trip_Duration_Minutes` are computed from Point A and Point B using:
- Nominatim (OpenStreetMap) for geocoding (address → coordinates)
- OSRM public routing service for route metrics (distance and duration)

This avoids asking the user to manually enter distance and duration and enables a more realistic end-to-end prediction flow.

### Notes on traffic and weather
Real-time traffic and weather APIs were not required for this project.
To keep the solution simple, transparent, and consistent with the course scope:
- Traffic is approximated with time-based rules.
- Weather is provided by the user.

### Weather feature note (data-driven limitation)
The effect of `Weather` on the predicted price is learned from the training dataset.
In the cleaned dataset, the number of observations for each category is not balanced (e.g., `Snow` has fewer samples than `Clear` and `Rain`).
Additionally, in this dataset the mean/median `Trip_Price` for `Snow` is slightly lower than for `Clear` and `Rain`.
For this reason, the model may predict similar or slightly lower prices under `Snow`, which reflects the patterns in the dataset rather than a real-world pricing rule.

## Author

Performed by
Alessandro Abbate
Nackademin MLOps student.  
