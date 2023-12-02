import unittest
import api_maps.api_maps as maps


class DistMapsTest(unittest.TestCase):
    # shows return value of store operations...
    def test_sample_distance_time(self):

        response = maps.time_p2p([6.611124, 46.538480], [6.657723, 46.510232])

        self.assertEqual('960', response)


if __name__ == '__main__':
    unittest.main()
