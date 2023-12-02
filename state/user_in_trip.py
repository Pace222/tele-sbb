from typing import List


class UserInTrip:
    def __init__(self, user_id: str, location: str, car=0, car_capacity=1):
        self.user_id = user_id
        self.location = location
        self.car = car
        self.car_capacity = car_capacity

    def getLonLat(self) -> List[float]:
        return [float(loc) for loc in self.location.split(",")]

    def setLonLat(self, location: List[float]):
        self.location = ",".join([str(loc) for loc in location])
