import unittest
import state.state as store


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


if __name__ == '__main__':
    unittest.main()
