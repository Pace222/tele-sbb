import sqlite3
from typing import List

from state.journey import Journey
from state.user_in_trip import UserInTrip


def init_db():
    with sqlite3.connect('state.sqlite') as con:
        # Journey reference
        con.execute("CREATE TABLE IF NOT EXISTS journeys (journey_id TINYTEXT PRIMARY KEY, title TINYTEXT,"
                    "destination TINYTEXT, deadline_month TINYTEXT, deadline_day TINYTEXT, deadline_time TINYTEXT,"
                    "plan MEDIUMTEXT)")

        # Telegram user ID (if known)
        con.execute("CREATE TABLE IF NOT EXISTS users (user_id TINYTEXT PRIMARY KEY, user_name TINYTEXT)")

        # For a journey, a user takes part from a start location, with a car (optional) of a certain capacity
        con.execute("CREATE TABLE IF NOT EXISTS user_journeys (user_id TINYTEXT, journey_id TINYTEXT,"
                    "location TINYTEXT, car BOOLEAN NOT NULL CHECK (car IN (0, 1)),"
                    "car_capacity INTEGER CHECK (car_capacity > 0),"
                    "PRIMARY KEY (user_id, journey_id),"
                    "FOREIGN KEY(user_id) REFERENCES users(user_id),"
                    "FOREIGN KEY(journey_id) REFERENCES journeys(journey_id))")


# IDEA: Generate journey_id from the telegram group ID
def add_journey(journey_id: str, journey_text: str, destination: str, deadline_month: str, deadline_day: str,
                deadline_time: str, plan: str):
    with sqlite3.connect('state.sqlite') as con:
        con.execute("INSERT OR IGNORE INTO journeys VALUES (?, ?, ?, ?, ?, ?, ?)",
                    (journey_id, journey_text, destination, deadline_month, deadline_day, deadline_time, plan))


def add_journey_id(journey_id: str):
    add_journey(journey_id, "", "", "", "", "", "")


def set_journey_title(journey_id: str, title: str):
    with sqlite3.connect('state.sqlite') as con:
        con.execute("UPDATE journeys SET title = ? WHERE journey_id = ?", (title, journey_id))


def set_journey_destination(journey_id: str, destination: str):
    with sqlite3.connect('state.sqlite') as con:
        con.execute("UPDATE journeys SET destination = ? WHERE journey_id = ?", (destination, journey_id))


def set_journey_deadline_month(journey_id: str, deadline_month: str):
    with sqlite3.connect('state.sqlite') as con:
        con.execute("UPDATE journeys SET deadline_month = ? WHERE journey_id = ?", (deadline_month, journey_id))


def set_journey_deadline_day(journey_id: str, deadline_day: str):
    with sqlite3.connect('state.sqlite') as con:
        con.execute("UPDATE journeys SET deadline_day = ? WHERE journey_id = ?", (deadline_day, journey_id))


def set_journey_deadline_time(journey_id: str, deadline_time: str):
    with sqlite3.connect('state.sqlite') as con:
        con.execute("UPDATE journeys SET deadline_time = ? WHERE journey_id = ?", (deadline_time, journey_id))


def set_journey_plan(journey_id: str, plan: str):
    with sqlite3.connect('state.sqlite') as con:
        con.execute("UPDATE journeys SET plan = ? WHERE journey_id = ?", (plan, journey_id))


# IDEA: Generate user_id from the telegram user ID
def add_user(user_id: str, user_name: str = ""):
    with sqlite3.connect('state.sqlite') as con:
        # Ignore if user already exists
        con.execute("INSERT OR IGNORE INTO users VALUES(?, ?)", (user_id, user_name))


def set_user_name(user_id: str, user_name: str):
    with sqlite3.connect('state.sqlite') as con:
        con.execute("UPDATE users SET user_name = ? WHERE user_id = ?", (user_name, user_id))


def get_user_name(user_id: str) -> str:
    with sqlite3.connect('state.sqlite') as con:
        return con.execute("SELECT user_name FROM users WHERE user_id = ?", (user_id,)).fetchone()[0]


def join_journey(user_id: str, journey_id: str, start_location, car=False, car_capacity=1):
    with sqlite3.connect('state.sqlite') as con:
        con.execute("INSERT OR IGNORE INTO users VALUES(?, ?)", (user_id, ""))
        con.execute("INSERT OR REPLACE INTO user_journeys VALUES (?, ?, ?, ?, ?)",
                    (user_id, journey_id, start_location, car, car_capacity))


def update_user_car(user_id: str, journey_id: str, car: bool):
    with sqlite3.connect('state.sqlite') as con:
        con.execute("UPDATE user_journeys SET car = ? WHERE journey_id = ? AND user_id = ?", (car, journey_id, user_id))


def update_user_car_capacity(user_id: str, journey_id: str, car_capacity: int):
    with sqlite3.connect('state.sqlite') as con:
        con.execute("UPDATE user_journeys SET car_capacity = ? WHERE journey_id = ? AND user_id = ?",
                    (car_capacity, journey_id, user_id))


def store_journey_plan(journey_id: str, plan: str):
    with sqlite3.connect('state.sqlite') as con:
        con.execute("UPDATE journeys SET plan = ? WHERE journey_id = ?", (plan, journey_id))


def get_journey(journey_id: str) -> Journey:
    with sqlite3.connect('state.sqlite') as con:
        res = con.execute("SELECT * FROM journeys WHERE journey_id = ?", (journey_id,)).fetchone()
        return Journey(*res)


def get_journey_plan(journey_id: str) -> str:
    with sqlite3.connect('state.sqlite') as con:
        return con.execute("SELECT plan FROM journeys WHERE journey_id = ?", (journey_id,)).fetchone()


def get_journey_users(journey_id: str) -> List[UserInTrip]:
    with sqlite3.connect('state.sqlite') as con:
        res = con.execute("SELECT user_id, location, car, car_capacity FROM user_journeys WHERE journey_id = ?",
                          (journey_id,)).fetchall()
        return [UserInTrip(*r) for r in res]


def count_journey_users(journey_id: str) -> int:
    with sqlite3.connect('state.sqlite') as con:
        return con.execute("SELECT COUNT(*) FROM user_journeys WHERE journey_id = ?", (journey_id,)).fetchone()[0]


def remove_journey(journey_id: str):
    with sqlite3.connect('state.sqlite') as con:
        con.execute("DELETE FROM journeys WHERE journey_id = ?", (journey_id,))
        con.execute("DELETE FROM user_journeys WHERE journey_id = ?", (journey_id,))


def remove_user_from_journey(user_id: str, journey_id: str):
    with sqlite3.connect('state.sqlite') as con:
        con.execute("DELETE FROM user_journeys WHERE journey_id = ? AND user_id = ?", (journey_id, user_id))


def remove_user(user_id: str):
    with sqlite3.connect('state.sqlite') as con:
        con.execute("DELETE FROM users WHERE user_id = ?", (user_id,))
        con.execute("DELETE FROM user_journeys WHERE user_id = ?", (user_id,))


def print_all_db():
    with sqlite3.connect('state.sqlite') as con:
        res = con.execute("Select * from users").fetchall()
        print("--- Users:")
        print(res)

        print("--- Journeys:")
        res = con.execute("Select * from journeys").fetchall()
        print(res)

        print("--- User Journeys:")
        res = con.execute("Select * from user_journeys").fetchall()
        print(res)


def flush_db():
    with sqlite3.connect('state.sqlite') as con:
        con.execute("DELETE FROM users")
        con.execute("DELETE FROM journeys")
        con.execute("DELETE FROM user_journeys")