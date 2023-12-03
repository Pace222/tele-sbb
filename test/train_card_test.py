import unittest
from visual.train_card_gen import generate_train_card


class TrainCardTest(unittest.TestCase):
    # shows return value of store operations...
    def test_train_card_image(self):
        image_name = generate_train_card("Lausanne", "Zurich", "11h49m10s",
                                    "15h54m41s")
        print("Image name: " + image_name)


if __name__ == '__main__':
    unittest.main()
