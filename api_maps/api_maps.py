from typing import List
from keys import GOOGLE_MAPS_KEY

import requests


url = 'https://routes.googleapis.com/directions/v2:computeRoutes'


# List[float] = [longitude, latitude]
# TODO can also add travelMode: DRIVE, BICYCLE, WALK
def dist_time_point_to_point(origin: List[float], destination: List[float]):
    headers = {
        'Content-Type': 'application/json',
        'X-Goog-Api-Key': GOOGLE_MAPS_KEY,
        'X-Goog-FieldMask': 'routes.duration,routes.distanceMeters'
    }

    data = {
        "origin": {
            "location": {
                "latLng": {
                    "latitude": origin[1],
                    "longitude": origin[0]
                }
            }
        },
        "destination": {
            "location": {
                "latLng": {
                    "latitude": destination[1],
                    "longitude": destination[0]
                }
            }
        },
        "travelMode": "DRIVE",
        "languageCode": "en-US",
        "units": "METRIC"
    }

    response = requests.post(url, json=data, headers=headers)

    if response.status_code == 200:
        result = response.json()
        return result
    else:
        print(f"Error: {response.status_code}\n{response.text}")
        return {}
