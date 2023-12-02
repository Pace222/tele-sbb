import sqlite3


def init_db():
    with sqlite3.connect('state.db') as con:
        # Journey reference
        con.execute("CREATE TABLE IF NOT EXISTS journeys (journey_id INTEGER PRIMARY KEY, title TEXT, destination TEXT,"
                    "deadline TEXT)")

        # Telegram user ID (if known)
        con.execute("CREATE TABLE IF NOT EXISTS users (user_id TEXT PRIMARY KEY)")

        # For a journey, a user takes part from a start location, with a car (optional) of a certain capacity
        con.execute("CREATE TABLE IF NOT EXISTS user_journeys (user_id TEXT, journey_id INTEGER,"
                    "FOREIGN KEY(user_id) REFERENCES users(user_id),"
                    "FOREIGN KEY(journey_id) REFERENCES journeys(journey_id),"
                    "location TEXT,"
                    "car BOOLEAN NOT NULL CHECK (car IN (0, 1)), car_capacity INTEGER CHECK (car_capacity > 0))")


# IDEA: Generate journey_id from the telegram group ID
def add_journey(journey_id: str):
    with sqlite3.connect('state.db') as con:
        con.execute("INSERT INTO ")


def add_user(user_id: str):
    with sqlite3.connect('state.db') as con:
        con.execute("INSERT INTO ")


def join_journey(user_id: str, journey_id: str, car=False,  car_capacity=1):
    with sqlite3.connect('state.db') as con:
        con.execute("INSERT INTO ")
