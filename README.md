# taxi_prediction_fullstack_alessandro
Fullstack ML application for predicting taxi prices

# Data Directory

This project uses a public dataset downloded from kaggle.

The dataset is ingored from gitignore.
To run the project:

1. Download the dataset from the original source
2. Place the file in the data directory.


# ------- Design Choice ---------

## Design Choices and Assumptions

To provide a user-friendly experience, the application requires only:
- pickup address (Point A)
- drop-off address (Point B)
- weather conditions (selected by the user)
- passenger count (selected by the user)

### Automatic features
Some features are automatically derived at request time:
- `Time_of_Day` is computed from the current system time.
- `Day_of_Week` (weekday/weekend) is computed from the current date.
- `Traffic_Conditions` is estimated using simple time-based rules (e.g., morning and evening rush hours).

### Route distance and duration
`Trip_Distance_km` and `Trip_Duration_Minutes` are computed from Point A and Point B using a routing service (OSRM with Encoding).
This avoids asking the user to manually enter distance and duration and enables a more realistic end-to-end prediction flow.

### Notes
Traffic and weather can affect pricing, but real-time traffic and weather APIs were not required for this project.
Instead, traffic is approximated with time-based rules, and weather is provided by the user to keep the solution simple, transparent, and consistent with the course scope.


