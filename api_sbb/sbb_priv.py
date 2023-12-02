from typing import List, Union

import requests

API_URL = "https://journey-service-int.api.sbb.ch"
CLIENT_SECRET = ""
CLIENT_ID = ""
SCOPE = ""


def get_token():
    params = {
        'grant_type': 'client_credentials',
        'scope': SCOPE,
        'client_id': CLIENT_ID,
        'client_secret': CLIENT_SECRET
    }
    return requests.post('https://login.microsoftonline.com/2cda5d11-f0ac-46b3-967d-af1b2e1bd01a/oauth2/v2.0/token',
                         data=params).json()


def get_id_by_name(auth: str, place: str):
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
        raise ValueError("Invalid origin")
    else:
        return place_ids[0]['id']

