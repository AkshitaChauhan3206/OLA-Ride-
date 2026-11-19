# Business metrics used by the dashboard, the notebook and the report
import numpy as np
import pandas as pd

from src.config import DAY_ORDER, PAYMENT_ORDER, STATUS_ORDER, VEHICLE_ORDER


def safe_div(a, b):
    # Divide without crashing when the filter leaves no rows
    return float(a) / float(b) if b else 0.0


def only_success(df):
    # Rides that were completed by a driver
    return df[df["Is_Success"]]


def kpis(df):
    # One dictionary with every headline number
    ok = only_success(df)
    total = len(df)
    failed = df[~df["Is_Success"]]
    per_customer = df.groupby("Customer_ID").size()
    return {
        "total_bookings": total,
        "success_rides": len(ok),
        "success_rate": safe_div(len(ok), total),
        "customer_cancel_rate": safe_div((df["Booking_Status"] == "Canceled by Customer").sum(), total),
        "driver_cancel_rate": safe_div((df["Booking_Status"] == "Canceled by Driver").sum(), total),
        "no_driver_rate": safe_div((df["Booking_Status"] == "Driver Not Found").sum(), total),
        "booked_value": float(df["Booking_Value"].sum()),
        "realised_revenue": float(ok["Booking_Value"].sum()),
        "lost_value": float(failed["Booking_Value"].sum()),
        "avg_booking_value": float(ok["Booking_Value"].mean()) if len(ok) else 0.0,
        "avg_distance": float(ok["Ride_Distance"].mean()) if len(ok) else 0.0,
        "total_km": float(ok["Ride_Distance"].sum()),
        "avg_driver_rating": float(ok["Driver_Ratings"].mean()) if len(ok) else 0.0,
        "avg_customer_rating": float(ok["Customer_Rating"].mean()) if len(ok) else 0.0,
        "unique_customers": int(df["Customer_ID"].nunique()),
        "repeat_customer_share": safe_div((per_customer > 1).sum(), len(per_customer)),
        "incomplete_rides": int(ok["Is_Incomplete"].sum()),
        "incomplete_rate": safe_div(ok["Is_Incomplete"].sum(), len(ok)),
        "incomplete_value": float(ok.loc[ok["Is_Incomplete"], "Booking_Value"].sum()),
    }


def status_table(df):
    # Count and share of every booking status
    counts = df["Booking_Status"].value_counts().reindex(STATUS_ORDER).fillna(0).astype(int)
    table = counts.rename("Bookings").to_frame()
    table["Share"] = table["Bookings"] / max(len(df), 1)
    return table.reset_index().rename(columns={"index": "Booking_Status", "Booking_Status": "Booking_Status"})


def daily_status(df):
    # Bookings per day split by status, used for the volume over time chart
    grid = df.groupby(["Booking_Date", "Booking_Status"]).size().unstack(fill_value=0)
    return grid.reindex(columns=STATUS_ORDER, fill_value=0)


def hourly_profile(df):
    # Bookings and success rate for each hour of the day
    grouped = df.groupby("Hour").agg(Bookings=("Is_Success", "size"), Success_Rate=("Is_Success", "mean"))
    return grouped.reindex(range(24)).fillna(0).reset_index()


def weekday_hour_matrix(df):
    # Average bookings for each weekday and hour
    # We divide by how many times that weekday appears so five Mondays do not look busier
    days_seen = df.groupby("Day_Name")["Booking_Date"].nunique()
    counts = df.groupby(["Day_Name", "Hour"]).size().unstack(fill_value=0)
    counts = counts.reindex(index=DAY_ORDER, columns=range(24), fill_value=0)
    divisor = days_seen.reindex(DAY_ORDER).replace(0, np.nan)
    return counts.div(divisor, axis=0).fillna(0)


def weekday_average(df):
    # Average bookings per calendar day for each weekday name
    days_seen = df.groupby("Day_Name")["Booking_Date"].nunique()
    totals = df.groupby("Day_Name").size()
    table = pd.DataFrame({"Total": totals, "Days_In_Month": days_seen})
    table["Average_Per_Day"] = table["Total"] / table["Days_In_Month"]
    return table.reindex(DAY_ORDER).fillna(0).reset_index().rename(columns={"index": "Day_Name"})


def vehicle_summary(df):
    # One row per vehicle type with volume, distance, money and ratings
    ok = only_success(df)
    all_rides = df.groupby("Vehicle_Type").agg(
        Bookings=("Is_Success", "size"),
        Success_Rate=("Is_Success", "mean"),
        Driver_Cancel_Rate=("Booking_Status", lambda s: (s == "Canceled by Driver").mean()),
        Customer_Cancel_Rate=("Booking_Status", lambda s: (s == "Canceled by Customer").mean()),
        No_Driver_Rate=("Booking_Status", lambda s: (s == "Driver Not Found").mean()),
    )
    done = ok.groupby("Vehicle_Type").agg(
        Completed=("Is_Success", "size"),
        Revenue=("Booking_Value", "sum"),
        Avg_Value=("Booking_Value", "mean"),
        Total_Km=("Ride_Distance", "sum"),
        Avg_Distance=("Ride_Distance", "mean"),
        Avg_Driver_Rating=("Driver_Ratings", "mean"),
        Avg_Customer_Rating=("Customer_Rating", "mean"),
        Avg_Vehicle_TAT=("V_TAT", "mean"),
        Incomplete_Rate=("Is_Incomplete", "mean"),
    )
    table = all_rides.join(done, how="left")
    table["Revenue_Per_KM"] = table["Revenue"] / table["Total_Km"].replace(0, np.nan)
    table = table.reindex([v for v in VEHICLE_ORDER if v in table.index])
    return table.reset_index()


def payment_summary(df):
    # Money and rides for each payment method, only for completed rides
    ok = only_success(df)
    table = ok.groupby("Payment_Method").agg(
        Rides=("Booking_Value", "size"),
        Revenue=("Booking_Value", "sum"),
        Avg_Value=("Booking_Value", "mean"),
    )
    table["Revenue_Share"] = table["Revenue"] / max(table["Revenue"].sum(), 1)
    table = table.reindex([p for p in PAYMENT_ORDER if p in table.index])
    return table.reset_index()


def top_customers(df, n=5, by="value"):
    # Best customers by total booking value or by number of bookings
    if by == "value":
        ok = only_success(df)
        table = ok.groupby("Customer_ID").agg(
            Total_Value=("Booking_Value", "sum"), Rides=("Booking_Value", "size")
        )
        return table.sort_values("Total_Value", ascending=False).head(n).reset_index()
    table = df.groupby("Customer_ID").agg(
        Bookings=("Booking_ID", "size"), Booked_Value=("Booking_Value", "sum")
    )
    return table.sort_values(["Bookings", "Booked_Value"], ascending=False).head(n).reset_index()


def customer_frequency(df):
    # How many customers booked once, twice, three times and so on
    per_customer = df.groupby("Customer_ID").size()
    table = per_customer.value_counts().sort_index().rename("Customers").reset_index()
    table.columns = ["Bookings_Per_Customer", "Customers"]
    return table


def cancel_reasons(df, who):
    # Count and share of each reason for the chosen side
    if who == "customer":
        column, status = "Canceled_Rides_by_Customer", "Canceled by Customer"
    else:
        column, status = "Canceled_Rides_by_Driver", "Canceled by Driver"
    part = df[df["Booking_Status"] == status]
    table = part[column].value_counts().rename("Rides").reset_index()
    table.columns = ["Reason", "Rides"]
    table["Share"] = table["Rides"] / max(table["Rides"].sum(), 1)
    return table


def incomplete_reasons(df):
    # Reasons given for rides that were marked as incomplete
    part = only_success(df)
    part = part[part["Is_Incomplete"]]
    table = part["Incomplete_Rides_Reason"].value_counts().rename("Rides").reset_index()
    table.columns = ["Reason", "Rides"]
    table["Share"] = table["Rides"] / max(table["Rides"].sum(), 1)
    return table


def location_summary(df, column="Pickup_Location"):
    # Volume and success rate for each place
    table = df.groupby(column).agg(
        Bookings=("Is_Success", "size"),
        Success_Rate=("Is_Success", "mean"),
        No_Driver=("Booking_Status", lambda s: (s == "Driver Not Found").sum()),
    )
    return table.sort_values("Bookings", ascending=False).reset_index()


def daily_distance(df):
    # Average and total distance of completed rides for each day
    ok = only_success(df)
    return ok.groupby("Booking_Date").agg(
        Avg_Distance=("Ride_Distance", "mean"), Total_Km=("Ride_Distance", "sum")
    ).reset_index()


def rating_summary(df):
    # Share of completed rides in each rating bucket
    ok = only_success(df)
    bins = [0, 3.5, 4.0, 4.5, 5.01]
    labels = ["3.0 to 3.4", "3.5 to 3.9", "4.0 to 4.4", "4.5 to 5.0"]
    out = {}
    for name, column in [("Driver", "Driver_Ratings"), ("Customer", "Customer_Rating")]:
        bucket = pd.cut(ok[column], bins=bins, labels=labels, right=False)
        out[name] = bucket.value_counts(normalize=True).reindex(labels).fillna(0)
    return pd.DataFrame(out)


def data_health(df):
    # Checks to see whether the numbers can be trusted
    ok = only_success(df)
    fare = ok["Fare_Per_KM"].dropna()
    median_fare = fare.median() if len(fare) else 0.0
    distance_corr = ok[["Booking_Value", "Ride_Distance"]].corr().iloc[0, 1] if len(ok) > 2 else np.nan
    return {
        "same_pickup_drop": int(df["Same_Pickup_Drop"].sum()),
        "same_pickup_drop_completed": int((df["Same_Pickup_Drop"] & df["Is_Success"]).sum()),
        "very_high_fare_per_km": int((fare > 10 * median_fare).sum()) if median_fare else 0,
        "very_low_fare_per_km": int((fare < 0.25 * median_fare).sum()) if median_fare else 0,
        "median_fare_per_km": float(median_fare),
        "value_distance_corr": float(distance_corr) if pd.notna(distance_corr) else 0.0,
        "incomplete_inside_success": int(ok["Is_Incomplete"].sum()),
        "missing_cells": int(df.isna().sum().sum()),
    }


# Customer reasons that Ola can fix with better service
SERVICE_REASONS = [
    "Driver is not moving towards pickup location",
    "Driver asked to cancel",
    "AC is Not working",
]


def value_leakage(df):
    # Booked value split into what was earned and what was lost for each failure type
    by_status = df.groupby("Booking_Status")["Booking_Value"].sum()
    return {
        "booked": float(df["Booking_Value"].sum()),
        "driver": float(by_status.get("Canceled by Driver", 0)),
        "customer": float(by_status.get("Canceled by Customer", 0)),
        "no_driver": float(by_status.get("Driver Not Found", 0)),
        "earned": float(by_status.get("Success", 0)),
    }


def daily_trend(df):
    # Completed and failed bookings for each day with the daily success rate
    table = df.groupby("Booking_Date").agg(Completed=("Is_Success", "sum"), Total=("Is_Success", "size"))
    table["Failed"] = table["Total"] - table["Completed"]
    table["Success_Rate"] = table["Completed"] / table["Total"]
    return table.reset_index()


def top_pickups(df, n=10):
    # Busiest pickup areas with their success rate
    return location_summary(df, "Pickup_Location").head(n)


def time_slot_summary(df):
    # Bookings and success rate for each part of the day
    table = df.groupby("Time_Slot", observed=False).agg(
        Bookings=("Is_Success", "size"), Success_Rate=("Is_Success", "mean")
    )
    return table.fillna(0).reset_index()


def service_cancel_summary(df):
    # Share of customer cancels caused by the service and not by the customer
    part = df[df["Booking_Status"] == "Canceled by Customer"]
    service = int(part["Canceled_Rides_by_Customer"].isin(SERVICE_REASONS).sum())
    return {"total": len(part), "service": service, "share": safe_div(service, len(part))}


def customer_summary(df):
    # How often customers come back
    per_customer = df.groupby("Customer_ID").size()
    one_time = int((per_customer == 1).sum())
    return {
        "customers": len(per_customer),
        "one_time": one_time,
        "one_time_share": safe_div(one_time, len(per_customer)),
        "avg_bookings": float(per_customer.mean()) if len(per_customer) else 0.0,
    }


def opportunity(df, driver_pct, service_pct, no_driver_pct):
    # Extra rides and revenue if the chosen share of each failure type is recovered
    k = kpis(df)
    driver = int((df["Booking_Status"] == "Canceled by Driver").sum())
    service = service_cancel_summary(df)["service"]
    no_driver = int((df["Booking_Status"] == "Driver Not Found").sum())
    avg = k["avg_booking_value"]
    rides = {
        "Fewer driver cancellations": driver * driver_pct,
        "Fewer service related customer cancels": service * service_pct,
        "Fewer no driver found": no_driver * no_driver_pct,
    }
    total_rides = sum(rides.values())
    return {
        "levers": {name: {"rides": r, "revenue": r * avg} for name, r in rides.items()},
        "extra_rides": total_rides,
        "extra_revenue": total_rides * avg,
        "new_success_rate": safe_div(k["success_rides"] + total_rides, k["total_bookings"]),
    }
