from typing import Optional, Tuple, List, Union, Dict

import state.state as store
from routing import optimal_parking, get_trips, Parking, TripInfo, share_cars
from state.journey import Journey
from state.user_in_trip import UserInTrip
from visual.train_card_gen import generate_train_card


def solve_planning(journey_id: str) -> \
        Optional[Tuple[Journey, Parking, Dict[UserInTrip, Tuple[str, List[Tuple[UserInTrip, str]]]], List[Tuple[
            UserInTrip, Union[Tuple[str, str], TripInfo, Tuple[UserInTrip, str]]]], TripInfo]]:
    journey = store.get_journey(journey_id)
    users = store.get_journey_users(journey_id)
    month = journey.deadline_month
    day = journey.deadline_day
    time = journey.deadline_time
    destination = journey.destination

    # TODO solve "year problem"
    date = f"2024-{month}-{day}"

    solution_v1 = optimal_parking(users, date, time, destination)

    if solution_v1 is None:
        return None
    else:
        parking = solution_v1[0]

        # dict[driver, tuple[start_time, list[tuple[passenger, pick_up_time]]]]
        drivers_sol: Dict[UserInTrip, Tuple[str, List[Tuple[UserInTrip, str]]]] = share_cars(users, parking, date, time)

        user_plan_v2 = []

        # Collect passengers
        passengers_n_drivers = []
        for car_driver, car_passengers in drivers_sol.items():
            for car_passenger, _ in car_passengers[1]:
                passengers_n_drivers.append(car_passenger)
            passengers_n_drivers.append(car_driver)

        # Use TP for non (car driver or passenger)
        for user, tp_plan in zip(users, solution_v1[1]):
            if user not in passengers_n_drivers:
                user_plan_v2.append((user, tp_plan))

        # Inform passengers of their driver
        for car_driver, car_passengers in drivers_sol.items():
            for car_passenger, pick_up_time in car_passengers[1]:
                user_plan_v2.append((car_passenger, (car_driver, pick_up_time)))

        # Get train trip as a team
        final_train_options = get_trips(parking.coords, destination, date, time)

        if len(final_train_options) == 0:
            return None

        final_train = final_train_options[0]

        return journey, parking, drivers_sol, user_plan_v2, final_train


def prepare_planning_v1(journey, parking, drivers: Dict[UserInTrip, Tuple[str, List[Tuple[UserInTrip, str]]]],
                        user_plan: List[Tuple[UserInTrip, Union[Tuple[str, str], TripInfo, Tuple[UserInTrip, str]]]],
                        final_train):
    dest_name = parking.name
    instructions = [f"=== Trip to: {final_train.end} ===\n\nPassengers will first meet-up at {parking.name}:\n"]

    print("Drivers:")
    print(drivers)
    # Driver
    for driver, (start_time, passengers_n_time) in drivers.items():
        #  (check how many passengers)
        if len(passengers_n_time) == 0:
            instructions.append(f"[{driver.user_id}] Drive - from {driver.location} to {dest_name} P+R\n")
        else:
            passengers_text = ' - ' + ' - \n'.join([f"{p.user_id} @ {cleanerTime(t)}" for p, t in passengers_n_time])
            instructions.append(f"[{driver.user_id}] Car sharing (driver) - From: {driver.location} @ "
                                f"{cleanerTime(start_time)}, "
                                f" To: {dest_name}"  # @ {trip.stop_time}"  # TODO add arrival time also??
                                f"Pick-up passengers:\n{passengers_text}\n")

    # Passengers or TP

    for user, trip in user_plan:
        user_name = user.user_id  # TODO update user registration with name...
        if isinstance(trip, TripInfo):
            # Public transportation user
            via_string = ""
            if len(trip.stops) > 2:
                via_string = ', via: ' + ','.join([s[0] for s in trip.stops[1:-1]])
            instructions.append(f"[{user_name}] Public transport - From:{trip.start} @ {cleanerTime(trip.start_time)} "
                                f"to {trip.end} @ {cleanerTime(trip.stop_time)}{via_string}\n")
        else:
            # Case of passenger
            instructions.append(f"[{user_name}] Car sharing (passenger), driver = [{trip[0]}], pick-up from:"
                                f"{user.location} @ {trip[1]}\n")

    instructions.append(f"[Final] Public transport - From:{final_train.start} @ {cleanerTime(final_train.start_time)} "
                        f"to {final_train.end} @ {cleanerTime(final_train.stop_time)}")

    train_card_location = generate_train_card(final_train.start, final_train.end, cleanerTime(final_train.start_time),
                                              cleanerTime(final_train.stop_time))

    print(train_card_location)
    instructions.append("\n You will all be there on time to take the train together!")
    plan = "\n".join(instructions)
    store.set_journey_plan(journey.journey_id, plan)

    return plan, train_card_location


# No date no UTC...
def cleanerTime(time: str):
    return time[11:-6]
