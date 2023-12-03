from datetime import timedelta, datetime

from api_sbb.sbb_priv import API_URL, PARKINGS, get_token, get_coords_by_name, direct_p2p_meters, minus_times, \
    plus_times
from typing import List, Union, Tuple, Optional, Dict

import requests

from api_maps.api_maps import car_p2p
from state.user_in_trip import UserInTrip

MAX_PARKINGS = 3


class TripInfo:

    def __init__(self, legs):
        stops = [l['serviceJourney']['stopPoints'] for l in legs if l['type'] == 'PTRideLeg']
        self.stops = [[s['place']['name'] for s in (stop[0], stop[-1])] for stop in stops]
        self.start = self.stops[0][0]
        self.end = self.stops[-1][1]
        self.start_time = stops[0][0]['departure']['timeAimed']
        self.stop_time = stops[-1][-1]['arrival']['timeAimed']

        # self.duration = int(parse_duration(duration).total_seconds())


class Parking:
    def __init__(self, parking):
        self.name = parking["Name Haltestelle"]
        self.coords = parking["coords"]
        self.nb_parks = int(parking["parkrail_anzahl"])
        self.price_day = parking["parkrail_preis_tag"]


def get_trips(origin: Union[str, List[float]], destination: Union[str, List[float]], date: str = None, time: str = None,
              for_arrival: bool = False) -> List[TripInfo]:
    auth = get_token()['access_token']
    headers = {
        'Authorization': f"Bearer {auth}",
        'accept': 'application/json',
        'Accept-Language': 'en',
        'Content-Type': 'application/json'
    }
    if type(origin) == str:
        origin = get_coords_by_name(auth, origin)
    if type(destination) == str:
        destination = get_coords_by_name(auth, destination)

    content = {
        "origin": str(origin[::-1]),
        "destination": str(destination[::-1]),
        "forArrival": for_arrival
    }
    if date is not None:
        content["date"] = date
    if time is not None:
        content["time"] = time

    trips = requests.post(f"{API_URL}/v3/trips/by-origin-destination", headers=headers, json=content).json()
    if "trips" not in trips:
        return []
    return [TripInfo(t['legs']) for t in trips["trips"]]


def sbb_p2p(origin: List[float], destination: List[float], date: str, time: str) -> int:
    trips = get_trips(origin, destination, date, time, for_arrival=True)
    if len(trips) == 0:
        return -1

    return min([minus_times(date, time, t.start_time) for t in trips]).seconds


def parking_dists_to_coords(user: UserInTrip, date: str, time: str, destination: Union[str, List[float]],
                            for_arrival: bool = False):
    remaining_parks = PARKINGS['coords'].loc[
        PARKINGS['coords'].apply(lambda park_coords: direct_p2p_meters(user.getLatLon(), park_coords)).nsmallest(
            MAX_PARKINGS).index]

    if user.car:
        dists = remaining_parks.apply(lambda park_coords: car_p2p(user.getLatLon(), park_coords))
        dists = dists[dists > 0]
        if not for_arrival:
            return dists
        else:
            return dists, [], [], []
    else:
        if not for_arrival:
            dists = remaining_parks.apply(lambda park_coords: sbb_p2p(user.getLatLon(), park_coords, date, time))
            dists = dists[dists > 0]
            return dists
        else:
            def dists_from_coords(park_coords):
                trip = get_trips(park_coords, destination, date, time, for_arrival=True)[-1]
                start_time = datetime.fromisoformat(trip.start_time)
                start_date, start_time = start_time.date().strftime("%Y-%m-%d"), start_time.time().strftime("%H:%M")
                # TODO: remove start_date, start_time
                return sbb_p2p(user.getLatLon(), park_coords, start_date, start_time), start_date, start_time, trip

            dists = remaining_parks.apply(dists_from_coords)
            dists = dists[dists.apply(lambda d: d[0] > 0)]
            return dists.apply(lambda d: d[0]), dists.apply(lambda d: d[1]), dists.apply(lambda d: d[2]), dists.apply(lambda d: d[3])


# def closest_k_parks(k: int, user: UserInTrip) -> List[Parking]:
#    return PARKINGS.loc[parking_dists_to_coords(user).nsmallest(k).index].apply(lambda row: Parking(row), axis=1) \
#        .to_list()


# def parks_in_radius(r: float, user: UserInTrip, date: str, time: str) -> List[Parking]:
#    park_to_coords = parking_dists_to_coords(r, user, date, time)
#    return park_to_coords[(0 < park_to_coords) & (park_to_coords < r)].apply(lambda row: Parking(row), axis=1).to_list()


# Union[Tuple[str,str], TripInfo]]
def optimal_parking(users: List[UserInTrip], date: str, time: str, destination: Union[str, List[float]],
                    for_arrival: bool = False) -> Optional[
    Tuple[Parking, List[Union[Tuple[str, str], TripInfo]], str, str]]:
    for u in users:
        try:
            u.getLatLon()
        except ValueError:
            try:
                u.location = str(get_coords_by_name(get_token()['access_token'], u.location))[1:-1]
            except ValueError:
                return None

    dists_users_parks = {u: parking_dists_to_coords(u, date, time, destination, for_arrival) for u in users}
    try:
        if any([len(v if not for_arrival else v[0]) == 0 for v in dists_users_parks.values()]):
            return None
    except KeyError:
        return None

    r = 60 * (min([min(v if not for_arrival else v[0]) for v in dists_users_parks.values()]) // 60)
    while True:
        distances_to_park = {}

        for park_dists in dists_users_parks.values():
            if for_arrival:
                park_dists = park_dists[0]
            for park, dist in park_dists[(0 < park_dists) & (park_dists < r)].items():
                if park not in distances_to_park:
                    distances_to_park[park] = [dist]
                else:
                    distances_to_park[park].append(dist)
        if r > max([max(v if not for_arrival else v[0]) for v in dists_users_parks.values()]):
            return None
        if len(distances_to_park.values()) > 0 and max([len(dists) for dists in distances_to_park.values()]) > len(
                users) / 2:
            break
        r += 60

    def custom_max(key):
        distances = distances_to_park[key]
        return len(distances), -sum(distances)

    best_parking_id = max(distances_to_park, key=custom_max)
    best_parking = Parking(PARKINGS.loc[best_parking_id])
    best_park_date = [d_u_p[1] for u, d_u_p in dists_users_parks.items() if not u.car][0].loc[best_parking_id]
    best_park_time = [d_u_p[2] for u, d_u_p in dists_users_parks.items() if not u.car][0].loc[best_parking_id]
    best_trip = [d_u_p[3] for u, d_u_p in dists_users_parks.items() if not u.car][0].loc[best_parking_id]

    leave = []
    if not for_arrival:
        for u in users:
            if u.car:
                t = plus_times(date, time, -car_p2p(u.getLatLon(), best_parking.coords))
                leave_date = t.strftime("%Y-%m-%d")
                leave_time = t.strftime("%H:%M")
                leave.append((leave_date, leave_time))
            else:
                t = get_trips(u.getLatLon(), best_parking.coords, best_park_date, best_park_time, for_arrival=True)[-1]
                leave.append(t)
    return best_parking, leave, best_park_date, best_park_time, best_trip


def share_cars(users: List[UserInTrip], parking: Parking, date: str, time: str) -> Dict[
    UserInTrip, Tuple[str, List[Tuple[UserInTrip, str]], str]]:
    pt_time = {}
    neighs_dists_per_car = {}
    cargo_per_car = {}
    car_past = {}
    already_in_car = []
    finished = {}
    for u in users:
        if u.car:
            cargo_per_car[u] = []
            car_past[u] = {}
            already_in_car.append(u)
            finished[u] = False

            candidates = [(neigh, car_p2p(u.getLatLon(), neigh.getLatLon())) for neigh in users if not neigh.car]
            if len(candidates) == 0:
                finished[u] = True
                continue
            neighs_dists_per_car[u] = min(candidates, key=lambda tup: tup[1])
        else:
            pt_time[u] = sbb_p2p(u.getLatLon(), parking.coords, date, time)

    while not all([finished[u] for u in users if u.car]):
        for u in users:
            if u.car and len(cargo_per_car[u]) >= u.car_capacity - 1:
                finished[u] = True
            if u.car and not finished[u] and len(cargo_per_car[u]) < u.car_capacity - 1:
                closest_neigh, closest_dist = neighs_dists_per_car[u]
                alternative = car_p2p(closest_neigh.getLatLon(), parking.coords)
                if alternative < pt_time[closest_neigh] and all(
                        closest_dist - car_past[u][passenger] + alternative < pt_time[passenger] for passenger, _ in
                        cargo_per_car[u]):
                    cargo_per_car[u].append((closest_neigh, alternative))
                    car_past[u][closest_neigh] = closest_dist
                    already_in_car.append(closest_neigh)
                else:
                    finished[u] = True
                    continue
                candidates = [(neigh, closest_dist + car_p2p(closest_neigh.getLatLon(), neigh.getLatLon()))
                              for neigh in users if neigh not in already_in_car]
                if len(candidates) == 0:
                    finished[u] = True
                    continue
                neighs_dists_per_car[u] = min(candidates, key=lambda tup: tup[1])

    timings_per_driver = {}
    for driver, passengers in cargo_per_car.items():
        if len(passengers) == 0:
            start = plus_times(date, time, -car_p2p(driver.getLatLon(), parking.coords))
        else:
            last_pass, last_track = passengers[-1]
            start = plus_times(date, time, -car_past[driver][last_pass] - last_track)
        passenger_timings = []
        for p, _ in passengers:
            time = start + timedelta(seconds=car_past[driver][p])
            passenger_timings.append((p, time.strftime("%Y-%m-%d %H:%M")))
        timings_per_driver[driver] = (start.strftime("%Y-%m-%d %H:%M"), passenger_timings)  # , f"{date} {time}")

    return timings_per_driver


if __name__ == '__main__':
    users = [UserInTrip("1", "47.531271, 7.636413", car=1), UserInTrip("2", "47.552954, 7.584171", car=1),
             UserInTrip("3", "47.562917, 7.601509", car=0)]
    station = optimal_parking(users, time="21:00")
    print(station[0].name)
    print(station[1])
