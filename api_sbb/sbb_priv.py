from datetime import datetime, timedelta
from math import radians, sin, cos, atan2, sqrt

import os
from typing import List

import pandas as pd
import pytz

import requests

PARKINGS: pd.DataFrame = pd.read_csv(os.path.join(os.path.dirname(os.path.abspath(__file__)), "mobilitat.csv"),
                                     delimiter=';')
PARKINGS: pd.DataFrame = PARKINGS[PARKINGS['parkrail_anzahl'] > 0]
PARKINGS['coords'] = PARKINGS['Geoposition'].str.split(',').apply(lambda x: [float(coord) for coord in x])
PARKINGS = PARKINGS.drop(columns='Geoposition')

API_URL: str = "https://journey-service-int.api.sbb.ch"
CLIENT_SECRET: str = ""
CLIENT_ID: str = ""
SCOPE: str = ""


def get_token():
    params = {
        'grant_type': 'client_credentials',
        'scope': SCOPE,
        'client_id': CLIENT_ID,
        'client_secret': CLIENT_SECRET
    }
    return requests.post('https://login.microsoftonline.com/2cda5d11-f0ac-46b3-967d-af1b2e1bd01a/oauth2/v2.0/token',
                         data=params).json()


def get_coords_by_name(auth: str, place: str):
    headers = {
        'Authorization': f"Bearer {auth}",
        'accept': 'application/json',
        'Accept-Language': 'en',
        'Content-Type': 'application/json'
    }
    content = {
        'nameMatch': place
    }
    place_ids = requests.get(f"{API_URL}/v3/places", headers=headers, params=content).json()['places']
    if len(place_ids) == 0:
        raise ValueError("Invalid place")
    else:
        return place_ids[0]['centroid']['coordinates'][::-1]

def direct_p2p_meters(coords1: List[float], coords2: List[float]):
    R = 6371  # Earth radius in kilometers
    dlat = radians(coords2[1] - coords1[1])
    dlon = radians(coords2[0] - coords1[0])
    a = sin(dlat / 2) ** 2 + cos(radians(coords1[1])) * cos(radians(coords2[1])) * sin(dlon / 2) ** 2
    c = 2 * atan2(sqrt(a), sqrt(1 - a))
    distance = R * c
    return distance * 1000

def minus_times(final_date: str, final_time: str, start_date_time: str):
    datetime_str = f"{final_date} {final_time}"
    final_combined = datetime.strptime(datetime_str, "%Y-%m-%d %H:%M").astimezone(pytz.timezone('Europe/Zurich'))
    start_combined = datetime.fromisoformat(start_date_time)
    return final_combined - start_combined

def plus_times(start_date: str, start_time: str, seconds_to_add: int):
    datetime_str = f"{start_date} {start_time}"
    start_combined = datetime.strptime(datetime_str, "%Y-%m-%d %H:%M").astimezone(pytz.timezone('Europe/Zurich'))
    return start_combined + timedelta(seconds=seconds_to_add)
