import unittest
import api_maps.api_maps as maps


class DistMapsTest(unittest.TestCase):
    # shows return value of store operations...
    def test_sample_distance_time(self):

        response = maps.dist_time_point_to_point([6.611124, 46.538480], [6.657723, 46.510232])

        self.assertEqual({'routes': [{'distanceMeters': 5652, 'duration': '960s'}]}, response)


if __name__ == '__main__':
    unittest.main()
