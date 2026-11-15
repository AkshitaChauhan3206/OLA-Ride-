# Runs the project SQL queries on a temporary SQLite database
import re
import sqlite3

import pandas as pd

from src.config import SQL_FILE

TABLE_NAME = "ola_bookings"

# Columns that go into the SQL table, derived helper columns are left out
SQL_COLUMNS = [
    "Date", "Time", "Booking_ID", "Booking_Status", "Customer_ID", "Vehicle_Type",
    "Pickup_Location", "Drop_Location", "V_TAT", "C_TAT",
    "Canceled_Rides_by_Customer", "Canceled_Rides_by_Driver", "Incomplete_Rides",
    "Incomplete_Rides_Reason", "Booking_Value", "Payment_Method", "Ride_Distance",
    "Driver_Ratings", "Customer_Rating",
]


def build_connection(df):
    # Copy the cleaned table into an in memory database
    conn = sqlite3.connect(":memory:", check_same_thread=False)
    df[SQL_COLUMNS].to_sql(TABLE_NAME, conn, index=False, if_exists="replace")
    return conn


def load_queries(path=SQL_FILE):
    # Split the SQL file into numbered questions using the Q marker comments
    text = path.read_text(encoding="utf-8")
    pattern = re.compile(r"/\*\s*Q(\d+)\s*\|\s*(.*?)\s*\*/\s*(.*?;)", re.S)
    queries = []
    for number, title, sql in pattern.findall(text):
        queries.append({"number": int(number), "title": title, "sql": sql.strip()})
    return queries


def is_safe_select(sql):
    # Only plain read queries are allowed in the lab
    cleaned = sql.strip().rstrip(";").strip().lower()
    blocked = ["insert", "update", "delete", "drop", "alter", "create", "attach", "pragma"]
    starts_ok = cleaned.startswith("select") or cleaned.startswith("with")
    return starts_ok and ";" not in cleaned and not any(re.search(r"\b" + w + r"\b", cleaned) for w in blocked)


def run_query(conn, sql, limit=500):
    # Run one query and return a table, long results are cut for speed
    if not is_safe_select(sql):
        raise ValueError("Only a single SELECT query is allowed here.")
    result = pd.read_sql_query(sql, conn)
    return result.head(limit)
