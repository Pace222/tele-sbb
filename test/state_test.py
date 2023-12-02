import unittest
import state.state as store
from state.user_in_trip import UserInTrip


class StateTest(unittest.TestCase):
    # shows return value of store operations...
    def test_sample_journey(self):
        store.init_db()
        store.add_user("test_user_1")
        store.add_user("test_user_2")

        store.add_journey("test_journey_1", "test journey 1", "test destination 1", "test deadline 1", "")
        store.join_journey("test_user_1", "test_journey_1", "test location 1", True, 4)
        store.join_journey("test_user_2", "test_journey_1", "test location 2", False, 1)
        store.store_journey_plan("test_journey_1", "test plan 1")

        journey = store.get_journey("test_journey_1")

        self.assertEqual('test journey 1', journey.title)

        users = store.get_journey_users("test_journey_1")
        self.assertEqual("test location 2", users[1].location)

    def test_set_parse_lat_lon_from_userintrip(self):
        user = UserInTrip("test_user_1", "20,5")
        user.setLatLon([46.538480, 6.611124])
        self.assertEqual([46.538480, 6.611124], user.getLatLon())


if __name__ == '__main__':
    unittest.main()
