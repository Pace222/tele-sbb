from sbb_priv import API_URL, get_token, get_id_by_name
from typing import List, Union

import requests


class TripInfo:

    def __init__(self, legs):
        stops = [l['serviceJourney']['stopPoints'] for l in legs if l['type'] == 'PTRideLeg']
        self.stops = [[s['place']['name'] for s in (stop[0], stop[-1])] for stop in stops]
        self.start = self.stops[0][0]
        self.end = self.stops[-1][1]
        self.start_time = legs[0]['serviceJourney']['stopPoints'][0]['departure']['timeAimed']
        self.stop_time = legs[-1]['serviceJourney']['stopPoints'][-1]['arrival']['timeAimed']


def get_trip(origin: Union[str, List[float]], destination: Union[str, List[float]], date: str = None, time: str = None,
             for_arrival: bool = False) -> TripInfo:
    auth = get_token()['access_token']
    headers = {
        'Authorization': f"Bearer {auth}",
        'accept': 'application/json',
        'Accept-Language': 'en',
        'Content-Type': 'application/json'
    }
    if type(origin) == str:
        origin = get_id_by_name(auth, origin)
    if type(destination) == str:
        destination = get_id_by_name(auth, destination)

    content = {
        "origin": str(origin),
        "destination": str(destination),
        "forArrival": for_arrival
    }
    if date is not None:
        content["date"] = date
    if time is not None:
        content["time"] = time

    trips = requests.post(f"{API_URL}/v3/trips/by-origin-destination", headers=headers, json=content).json()["trips"]
    if len(trips) == 0:
        raise ValueError("No trip was found")

    return TripInfo(trips[0]['legs'])


if __name__ == '__main__':
    print(get_trip("Lausanne", "Zürich HB", time="16:20"))
