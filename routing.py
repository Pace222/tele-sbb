from datetime import datetime, timedelta

from api_sbb.sbb_priv import API_URL, PARKINGS, get_token, get_id_by_name, direct_p2p_meters
from typing import List, Union, Tuple, Optional
from isodate import parse_duration

import requests

from api_maps.api_maps import car_p2p
from state.user_in_trip import UserInTrip

MAX_DISTANCE = 10_000  # in m


class TripInfo:

    def __init__(self, legs):
        stops = [l['serviceJourney']['stopPoints'] for l in legs if l['type'] == 'PTRideLeg']
        self.stops = [[s['place']['name'] for s in (stop[0], stop[-1])] for stop in stops]
        self.start = self.stops[0][0]
        self.end = self.stops[-1][1]
        self.start_time = stops[0][0]['departure']['timeAimed']
        self.stop_time = stops[-1][-1]['arrival']['timeAimed']

        self.duration = int(parse_duration(duration).total_seconds())


class Parking:
    def __init__(self, parking):
        self.name = parking["Name Haltestelle"]
        self.coords = parking["coords"]
        self.nb_parks = int(parking["parkrail_anzahl"])
        self.price_day = parking["parkrail_preis_tag"]


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
        "origin": str(origin[::-1]),
        "destination": str(destination[::-1]),
        "forArrival": for_arrival
    }
    if date is not None:
        content["date"] = date
    if time is not None:
        content["time"] = time

    trips = requests.post(f"{API_URL}/v3/trips/by-origin-destination", headers=headers, json=content).json()["trips"]

    return [TripInfo(t['legs'], t['duration']) for t in trips if 'duration' in t]


def sbb_p2p(origin: List[float], destination: List[float], date: str = None, time: str = None, ) -> int:
    trips = get_trips(origin, destination, date, time, for_arrival=True)
    if len(trips) == 0:
        return -1

    return min([t.duration for t in trips])


def parking_dists_to_coords(user: UserInTrip, date: str, time: str):
    remaining_parks = PARKINGS['coords'][PARKINGS['coords'].apply(
        lambda park_coords: direct_p2p_meters(user.getLatLon(), park_coords)) < MAX_DISTANCE]

    if user.car:
        dists = remaining_parks.apply(lambda park_coords: car_p2p(user.getLatLon(), park_coords))
        dists = dists[dists > 0]
        return dists
    else:
        dists = remaining_parks.apply(lambda park_coords: sbb_p2p(user.getLatLon(), park_coords, date, time))
        dists = dists[dists > 0]
        return dists


# def closest_k_parks(k: int, user: UserInTrip) -> List[Parking]:
#    return PARKINGS.loc[parking_dists_to_coords(user).nsmallest(k).index].apply(lambda row: Parking(row), axis=1) \
#        .to_list()


# def parks_in_radius(r: float, user: UserInTrip, date: str, time: str) -> List[Parking]:
#    park_to_coords = parking_dists_to_coords(r, user, date, time)
#    return park_to_coords[(0 < park_to_coords) & (park_to_coords < r)].apply(lambda row: Parking(row), axis=1).to_list()


# Union[Tuple[str,str], TripInfo]]
def optimal_parking(users: List[UserInTrip], date: str = None, time: str = None) -> Optional[Tuple[Parking, List[Union[Tuple[str, str], TripInfo]]]]:
    dists_users_parks = {u: parking_dists_to_coords(u, date, time) for u in users}
    if any([len(v) == 0 for v in dists_users_parks.values()]):
        return None

    r = 60 * (min([min(v) for v in dists_users_parks.values()]) // 60)
    while True:
        distances_to_park = {}

        for park_dists in dists_users_parks.values():
            for park, dist in park_dists[(0 < park_dists) & (park_dists < r)].items():
                if park not in distances_to_park:
                    distances_to_park[park] = [dist]
                else:
                    distances_to_park[park].append(dist)
        if r > max([max(v) for v in dists_users_parks.values()]):
            return None
        if len(distances_to_park.values()) > 0 and max([len(dists) for dists in distances_to_park.values()]) > len(
                users) / 2:
            break
        r += 60

    def custom_max(key):
        distances = distances_to_park[key]
        return len(distances), -sum(distances)

    best_parking = Parking(PARKINGS.loc[max(distances_to_park, key=custom_max)])

    datetime_str = f"{date if date else datetime.now().date()} {time}"
    combined_dt = datetime.strptime(datetime_str, "%Y-%m-%d %H:%M")
    leave = []
    for u in users:
        if u.car:
            t = combined_dt - timedelta(seconds=car_p2p(u.getLatLon(), best_parking.coords))
            leave_date = t.strftime("%Y-%m-%d")
            leave_time = t.strftime("%H:%M")
            leave.append((leave_date, leave_time))
        else:
            t = get_trips(u.getLatLon(), best_parking.coords, date, time, for_arrival=True)[0]
            leave.append(t)
    return best_parking, leave


if __name__ == '__main__':
    users = [UserInTrip("1", "47.531271, 7.636413", car=1), UserInTrip("2", "47.552954, 7.584171", car=1),
             UserInTrip("3", "47.562917, 7.601509", car=0)]
    station = optimal_parking(users, time="21:00")
    print(station[0].name)
    print(station[1])
