from typing import Optional, Tuple, List, Union

import state.state as store
from routing import optimal_parking, get_trips, Parking, TripInfo
from state.journey import Journey
from state.user_in_trip import UserInTrip
from visual.train_card_gen import generate_train_card


def solve_planning(journey_id: str) ->\
        Optional[Tuple[Journey, Parking, List[Tuple[UserInTrip, Union[Tuple[str, str], TripInfo]]], TripInfo]]:
    journey = store.get_journey(journey_id)
    users = store.get_journey_users(journey_id)
    month = journey.deadline_month
    day = journey.deadline_day
    time = journey.deadline_time
    destination = journey.destination

    # TODO solve "year problem"
    date = f"2024-{month}-{day}"

    solution = optimal_parking(users, date, time)

    if solution is None:
        return None
    else:
        # TODO store and present solution
        parking = solution[0]
        user_plan = zip(users, solution[1])

        final_train_options = get_trips(parking.coords, destination, date, time)

        if len(final_train_options) == 0:
            return None

        final_train = final_train_options[0]

        return journey, parking, user_plan, final_train


def prepare_planning_v1(journey, parking, user_plan, final_train):
    dest_name = parking.name
    instructions = [f"=== {journey.title} ===\n"]

    for (user, trip) in user_plan:
        user_name = user.user_id  # TODO update user registration with name...
        if user.car == 0:
            via_string = ""
            if len(trip.stops) > 2:
                via_string = ', via: ' + ','.join([s[0] for s in trip.stops[1:-1]])
            instructions.append(f"[{user_name}] Public transport - From:{trip.start} @ {trip.start_time} to {trip.end} "
                                f"@ {trip.stop_time}{via_string}")
        else:
            instructions.append(f"[{user_name}] Drive - from {user.location} to {dest_name} P+R")

    instructions.append(f"[Final] Public transport - From:{final_train.start} @ {final_train.start_time} to " +
                        f"{final_train.end} @ {final_train.stop_time}")

    train_card_location = generate_train_card(final_train.start, final_train.end, final_train.start_time,
                                              final_train.stop_time)

    print(train_card_location)
    instructions.append("\n You will all be there on time to take the train together!")
    plan = "\n".join(instructions)
    store.set_journey_plan(journey.journey_id, plan)

    return plan, train_card_location

