import sqlite3


def init_db():
    with sqlite3.connect('state.db') as con:
        # Journey reference
        con.execute("CREATE TABLE IF NOT EXISTS journeys (journey_id INTEGER PRIMARY KEY, title TEXT, destination TEXT,"
                    "deadline TEXT, plan TEXT)")

        # Telegram user ID (if known)
        con.execute("CREATE TABLE IF NOT EXISTS users (user_id TEXT PRIMARY KEY)")

        # For a journey, a user takes part from a start location, with a car (optional) of a certain capacity
        con.execute("CREATE TABLE IF NOT EXISTS user_journeys (user_id TEXT, journey_id INTEGER,"
                    "FOREIGN KEY(user_id) REFERENCES users(user_id),"
                    "FOREIGN KEY(journey_id) REFERENCES journeys(journey_id),"
                    "location TEXT,"
                    "car BOOLEAN NOT NULL CHECK (car IN (0, 1)), car_capacity INTEGER CHECK (car_capacity > 0))")


# IDEA: Generate journey_id from the telegram group ID
def add_journey(journey_id: str, journey_text: str, destination: str, deadline: str):
    with sqlite3.connect('state.db') as con:
        con.execute("INSERT INTO journeys VALUES (?, ?, ?, ?)", (journey_id, journey_text, destination, deadline))


# IDEA: Generate user_id from the telegram user ID
def add_user(user_id: str):
    with sqlite3.connect('state.db') as con:
        con.execute("INSERT INTO users VALUES (?) ", user_id)


def join_journey(user_id: str, journey_id: str, start_location, car=False,  car_capacity=1):
    with sqlite3.connect('state.db') as con:
        con.execute("INSERT INTO user_journeys VALUES (?, ?, ?, ?, ?)", (user_id, journey_id, start_location, car,
                                                                         car_capacity))


def store_journey_plan(journey_id: str, plan: str):
    with sqlite3.connect('state.db') as con:
        con.execute("UPDATE journeys SET plan = ? WHERE journey_id = ?", (plan, journey_id))


def get_journey(journey_id: str):
    with sqlite3.connect('state.db') as con:
        return con.execute("SELECT * FROM journeys WHERE journey_id = ?", journey_id).fetchone()


def get_journey_plan(journey_id: str):
    with sqlite3.connect('state.db') as con:
        return con.execute("SELECT plan FROM journeys WHERE journey_id = ?", journey_id).fetchone()


def get_journey_users(journey_id: str):
    with sqlite3.connect('state.db') as con:
        return con.execute("SELECT (user_id, location, car, car_capacity) FROM user_journeys WHERE journey_id = ?", (journey_id,)).fetchall()


def remove_journey(journey_id: str):
    with sqlite3.connect('state.db') as con:
        con.execute("DELETE FROM journeys WHERE journey_id = ?", journey_id)
        con.execute("DELETE FROM user_journeys WHERE journey_id = ?", journey_id)


def remove_user_from_journey(user_id: str, journey_id: str):
    with sqlite3.connect('state.db') as con:
        con.execute("DELETE FROM user_journeys WHERE journey_id = ? AND user_id = ?", (journey_id, user_id))


def remove_user(user_id: str):
    with sqlite3.connect('state.db') as con:
        con.execute("DELETE FROM users WHERE user_id = ?", user_id)
        con.execute("DELETE FROM user_journeys WHERE user_id = ?", user_id)