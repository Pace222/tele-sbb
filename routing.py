from api_sbb.sbb_priv import API_URL, PARKINGS, get_token, get_id_by_name, direct_p2p_meters
from typing import List, Union

import requests

from api_maps.api_maps import car_p2p
from state.user_in_trip import UserInTrip

THEORETICAL_DIRECT_SPEED = 150 / 3.6 # km/h in m/s


class TripInfo:

    def __init__(self, legs):
        stops = [l['serviceJourney']['stopPoints'] for l in legs if l['type'] == 'PTRideLeg']
        self.stops = [[s['place']['name'] for s in (stop[0], stop[-1])] for stop in stops]
        self.start = self.stops[0][0]
        self.end = self.stops[-1][1]
        self.start_time = legs[0]['serviceJourney']['stopPoints'][0]['departure']['timeAimed']
        self.stop_time = legs[-1]['serviceJourney']['stopPoints'][-1]['arrival']['timeAimed']


class Parking:
    def __init__(self, parking):
        self.name = parking["Name Haltestelle"]
        self.coords = parking["coords"]
        self.nb_parks = int(parking["parkrail_anzahl"])
        self.price_day = parking["parkrail_preis_tag"]

    def __eq__(self, other):
        return isinstance(other, Parking) and self.__attrs() == other.__attrs()

    def __hash__(self):
        return hash(self.__attrs())


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

    trips = requests.post(f"{API_URL}/v3/trips/by-origin-destination", headers=headers, json=content).json()[
        "trips"]
    if len(trips) == 0:
        raise ValueError("No trip was found")

    return TripInfo(trips[0]['legs'])





def parking_dists_to_coords(r: float, user: UserInTrip):
    remaining_parks = PARKINGS['coords'][PARKINGS['coords'].apply(
        lambda park_coords: direct_p2p_meters(user.location, park_coords)) < r * THEORETICAL_DIRECT_SPEED]

    if user.car:
        return remaining_parks.apply(lambda park_coords: car_p2p(user.location, park_coords)[0])
    else:
        # TODO: call SBB
        return


# def closest_k_parks(k: int, user: UserInTrip) -> List[Parking]:
#    return PARKINGS.loc[parking_dists_to_coords(user).nsmallest(k).index].apply(lambda row: Parking(row), axis=1) \
#        .to_list()


def parks_in_radius(r: float, user: UserInTrip) -> List[Parking]:
    return PARKINGS[parking_dists_to_coords(r, user) < r].apply(lambda row: Parking(row), axis=1).to_list()


def optimal_station(users: List[UserInTrip]) -> Parking:
    r = 5
    while True:
        people_close_to_park = {}
        for u in users:
            for park in parks_in_radius(r, u):
                if park not in people_close_to_park:
                    people_close_to_park[park] = 1
                else:
                    people_close_to_park[park] += 1
        if max(people_close_to_park.values()) > len(users) / 2:
            break
        r += 5
    return max(people_close_to_park, key=people_close_to_park.get)


if __name__ == '__main__':
    print(get_trip("Lausanne", "Zürich HB", time="16:20"))
