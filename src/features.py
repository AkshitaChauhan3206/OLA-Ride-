# Derived columns that make the analysis easier
import numpy as np
import pandas as pd

from src.config import SLOT_ORDER


def time_slot(hour):
    # Group each hour of the day into a simple day part
    if hour < 6:
        return "Late Night"
    if hour < 12:
        return "Morning"
    if hour < 17:
        return "Afternoon"
    if hour < 21:
        return "Evening"
    return "Night"


def add_features(df):
    # Work on a copy so the original table stays untouched
    df = df.copy()
    stamp = df["Booking_Datetime"]

    # Calendar columns
    df["Booking_Date"] = stamp.dt.normalize()
    df["Hour"] = stamp.dt.hour
    df["Day_Name"] = stamp.dt.day_name()
    df["Day_Of_Month"] = stamp.dt.day
    df["Is_Weekend"] = stamp.dt.dayofweek >= 5
    df["Time_Slot"] = pd.Categorical(
        df["Hour"].map(time_slot), categories=SLOT_ORDER, ordered=True
    )

    # Status flags
    df["Is_Success"] = df["Booking_Status"].eq("Success")
    df["Is_Cancelled"] = df["Booking_Status"].isin(["Canceled by Customer", "Canceled by Driver"])
    df["Is_Incomplete"] = df["Incomplete_Rides"].eq("Yes")

    # Who caused the failed booking
    owner = {
        "Canceled by Customer": "Customer",
        "Canceled by Driver": "Driver",
        "Driver Not Found": "No Supply",
    }
    df["Failure_Owner"] = df["Booking_Status"].map(owner)

    # Price per kilometre, only meaningful when the ride really happened
    distance = df["Ride_Distance"].where(df["Ride_Distance"] > 0)
    df["Fare_Per_KM"] = df["Booking_Value"] / distance

    # Data quality flag for rides that start and end at the same place
    df["Same_Pickup_Drop"] = df["Pickup_Location"].eq(df["Drop_Location"])

    # Bands used for grouping in charts
    df["Distance_Band"] = pd.cut(
        df["Ride_Distance"].where(df["Ride_Distance"] > 0),
        bins=[0, 5, 10, 20, 30, 40, 50],
        labels=["0 to 5 km", "5 to 10 km", "10 to 20 km", "20 to 30 km", "30 to 40 km", "40 to 50 km"],
    )
    df["Value_Band"] = pd.cut(
        df["Booking_Value"],
        bins=[0, 200, 400, 800, 1500, 3000],
        labels=["Up to 200", "200 to 400", "400 to 800", "800 to 1500", "Above 1500"],
    )
    return df
