# Cleaning steps for the raw Ola ride data
# Run this file once to create data/ola_cleaned.csv from the Excel file
import sys
from pathlib import Path

import pandas as pd

from src.config import CLEAN_FILE, RAW_FILE_NAME, RAW_SHEET_NAME

# Columns that hold free text and need extra spaces removed
TEXT_COLUMNS = [
    "Booking_ID", "Booking_Status", "Customer_ID", "Vehicle_Type",
    "Pickup_Location", "Drop_Location", "Canceled_Rides_by_Customer",
    "Canceled_Rides_by_Driver", "Incomplete_Rides", "Incomplete_Rides_Reason",
    "Payment_Method",
]

# Final column order of the cleaned file
FINAL_COLUMNS = [
    "Booking_Datetime", "Date", "Time", "Booking_ID", "Booking_Status",
    "Customer_ID", "Vehicle_Type", "Pickup_Location", "Drop_Location",
    "V_TAT", "C_TAT", "Canceled_Rides_by_Customer", "Canceled_Rides_by_Driver",
    "Incomplete_Rides", "Incomplete_Rides_Reason", "Booking_Value",
    "Payment_Method", "Ride_Distance", "Driver_Ratings", "Customer_Rating",
]


def load_raw(path):
    # Read the July sheet which holds all booking rows
    return pd.read_excel(path, sheet_name=RAW_SHEET_NAME)


def standardise_text(df):
    # Remove extra spaces from text columns and keep real blanks as missing
    for col in TEXT_COLUMNS:
        df[col] = df[col].astype("string").str.strip()
    return df


def fix_dates(df):
    # The raw Date column already holds date and time together
    stamp = pd.to_datetime(df["Date"], errors="coerce")
    df["Booking_Datetime"] = stamp
    df["Date"] = stamp.dt.strftime("%Y/%m/%d")
    df["Time"] = stamp.dt.strftime("%H:%M:%S")
    return df


def remove_duplicates(df):
    # Drop rows that repeat the same booking id
    before = len(df)
    df = df.drop_duplicates(subset="Booking_ID", keep="first")
    print("Duplicate bookings removed:", before - len(df))
    return df


def check_rules(df):
    # Business rule checks, the results are printed for the project report
    success = df["Booking_Status"].eq("Success")
    checks = {
        "Rows with no booking date": int(df["Booking_Datetime"].isna().sum()),
        "Booking value not above zero": int((df["Booking_Value"] <= 0).sum()),
        "Success rides with zero distance": int((success & (df["Ride_Distance"] <= 0)).sum()),
        "Failed bookings that still show distance": int((~success & (df["Ride_Distance"] > 0)).sum()),
        "Success rides without a rating": int((success & df["Driver_Ratings"].isna()).sum()),
        "Failed bookings that carry a rating": int((~success & df["Driver_Ratings"].notna()).sum()),
        "Ratings outside the range 1 to 5": int(
            ((df["Driver_Ratings"] < 1) | (df["Driver_Ratings"] > 5)).sum()
        ),
    }
    for name, value in checks.items():
        print(name + ":", value)
    return checks


def build_clean_file(raw_path, out_path=CLEAN_FILE):
    # Run every cleaning step in order and save the result
    df = load_raw(raw_path)
    print("Raw shape:", df.shape)
    df = standardise_text(df)
    df = fix_dates(df)
    df = remove_duplicates(df)
    check_rules(df)

    # Missing values in TAT, payment, ratings and reasons are real blanks
    # because a cancelled ride never reaches those steps, so we keep them blank
    df = df[FINAL_COLUMNS].sort_values("Booking_Datetime").reset_index(drop=True)
    out_path = Path(out_path)
    out_path.parent.mkdir(parents=True, exist_ok=True)
    df.to_csv(out_path, index=False)
    print("Clean file saved:", out_path, df.shape)
    return df


if __name__ == "__main__":
    # Usage: run the module src.cleaning and give the path of the Excel file
    raw = sys.argv[1] if len(sys.argv) > 1 else RAW_FILE_NAME
    build_clean_file(raw)
