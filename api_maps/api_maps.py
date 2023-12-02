from typing import List
from keys import GOOGLE_MAPS_KEY

import requests


url = 'https://routes.googleapis.com/directions/v2:computeRoutes'


# List[float] = [longitude, latitude]
# Returns duration in Seconds (-1 if error)
# TODO can also add travelMode: DRIVE, BICYCLE, WALK
def time_p2p(origin: List[float], destination: List[float]):
    headers = {
        'Content-Type': 'application/json',
        'X-Goog-Api-Key': GOOGLE_MAPS_KEY,
        'X-Goog-FieldMask': 'routes.duration'
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
        if result != {}:
            return result['routes'][0]['duration'][:-1]
        return -1
    else:
        print(f"Error: {response.status_code}\n{response.text}")
        return -1
