# Ola Ride Insights: main Streamlit dashboard
import itertools

import pandas as pd
import streamlit as st
import streamlit.components.v1 as components

from src import charts, metrics, styles
from src.config import (
    COLORS, GITHUB_URL, PAYMENT_ORDER, POWERBI_EMBED_URL, STATUS_ORDER,
    STREAMLIT_URL, VEHICLE_ICONS, VEHICLE_ORDER,
)
from src.data_loader import load_data
from src.insights import build_insights, limits_of_data
from src.sql_lab import build_connection, load_queries, run_query
from src.styles import fmt_money, fmt_pct

# Page setup must be the first Streamlit call
st.set_page_config(
    page_title="Ola Ride Insights",
    page_icon="🚖",
    layout="wide",
    initial_sidebar_state="expanded",
)
st.markdown(styles.CSS, unsafe_allow_html=True)

# Counter that gives every chart a unique key on each run
chart_ids = itertools.count()


# Section: data

@st.cache_data(show_spinner="Loading ride data")
def get_data():
    # Load once and keep in memory for every user
    return load_data()


@st.cache_resource(show_spinner="Preparing SQL lab")
def get_connection():
    # In memory database used by the SQL lab tab
    return build_connection(get_data())


# Section: small helpers

def show_chart(fig):
    # Draw a chart, try the newer Streamlit option first and fall back to the older one
    key = f"chart_{next(chart_ids)}"
    try:
        st.plotly_chart(fig, width="stretch", key=key)
    except Exception:
        st.plotly_chart(fig, use_container_width=True, key=key)


def show_table(table, height=None):
    # Draw a table, height is passed only when it is set because newer Streamlit rejects an empty height
    options = {"hide_index": True}
    if height is not None:
        options["height"] = height
    try:
        st.dataframe(table, width="stretch", **options)
    except Exception:
        st.dataframe(table, use_container_width=True, **options)


def html(text):
    # Shortcut for writing custom HTML
    st.markdown(text, unsafe_allow_html=True)


def kpi_row(cards):
    # Show a row of KPI cards, each card is label, value, sub text and tone
    columns = st.columns(len(cards))
    for column, card in zip(columns, cards):
        with column:
            html(styles.kpi_card(*card))


# Section: sidebar filters

def apply_filters(df):
    # Sidebar controls that change every tab
    with st.sidebar:
        html(
            '<div style="font-family:Space Grotesk,sans-serif;font-size:22px;font-weight:700;">'
            f'<span style="color:{COLORS["lime"]};">●</span> OLA Insights</div>'
            f'<div style="color:{COLORS["muted"]};font-size:12px;margin-bottom:14px;">July 2024 ride analytics</div>'
        )
        st.markdown("**Filters**")

        first, last = df["Booking_Date"].min().date(), df["Booking_Date"].max().date()
        picked = st.date_input("Date range", value=(first, last), min_value=first, max_value=last)
        vehicles = st.multiselect("Vehicle type", VEHICLE_ORDER, default=VEHICLE_ORDER)
        statuses = st.multiselect("Booking status", STATUS_ORDER, default=STATUS_ORDER)
        payments = st.multiselect(
            "Payment method", PAYMENT_ORDER, default=PAYMENT_ORDER,
            help="Payment is only recorded for completed rides, so narrowing this keeps completed rides only.",
        )
        places = sorted(df["Pickup_Location"].unique())
        pickups = st.multiselect("Pickup location", places, default=places)

        st.markdown("---")
        html(
            f'<a href="{GITHUB_URL}" target="_blank" style="color:{COLORS["lime"]};text-decoration:none;">GitHub repository</a><br>'
            f'<a href="{STREAMLIT_URL}" target="_blank" style="color:{COLORS["lime"]};text-decoration:none;">Live dashboard</a>'
        )

    # A single picked date comes back as a one item tuple
    if isinstance(picked, (tuple, list)) and len(picked) == 2:
        start, end = picked
    else:
        start = end = picked[0] if isinstance(picked, (tuple, list)) else picked

    mask = df["Booking_Date"].between(pd.Timestamp(start), pd.Timestamp(end))
    mask &= df["Vehicle_Type"].isin(vehicles)
    mask &= df["Booking_Status"].isin(statuses)
    mask &= df["Pickup_Location"].isin(pickups)
    if set(payments) != set(PAYMENT_ORDER):
        mask &= df["Payment_Method"].isin(payments)
    return df[mask]


# Section: tabs

def tab_overview(df):
    k = metrics.kpis(df)
    html(styles.section("01", "Headline numbers", "Summary for the selected filters."))
    kpi_row([
        ("Total bookings", f"{k['total_bookings']:,}", f"{k['unique_customers']:,} unique customers", ""),
        ("Success rate", fmt_pct(k["success_rate"]), f"{k['success_rides']:,} completed rides",
         "good" if k["success_rate"] >= 0.7 else "warn"),
        ("Revenue earned", fmt_money(k["realised_revenue"]), "Booking value of completed rides", "good"),
        ("Revenue lost", fmt_money(k["lost_value"]), "Booking value of failed bookings", "bad"),
    ])
    st.write("")
    kpi_row([
        ("Average booking value", f"Rs {k['avg_booking_value']:,.0f}", "Completed rides", ""),
        ("Average distance", f"{k['avg_distance']:.1f} km", "Completed rides only", ""),
        ("Average ratings", f"{k['avg_driver_rating']:.2f} / {k['avg_customer_rating']:.2f}", "Driver and customer", ""),
        ("Repeat customers", fmt_pct(k["repeat_customer_share"]), "Booked more than once", "warn"),
    ])

    html(styles.section("02", "Ride volume and outcome", "How many bookings came in each day and how they ended."))
    left, right = st.columns([2, 1])
    with left:
        show_chart(charts.volume_over_time(metrics.daily_status(df)))
    with right:
        show_chart(charts.status_donut(metrics.status_table(df)))

    html(styles.section("03", "When do people book", "Demand by hour and by weekday."))
    left, right = st.columns(2)
    with left:
        show_chart(charts.hourly_chart(metrics.hourly_profile(df)))
    with right:
        show_chart(charts.heatmap(metrics.weekday_hour_matrix(df)))
    week = metrics.weekday_average(df)
    show_chart(charts.bar(week["Day_Name"], week["Average_Per_Day"], "Average bookings per day for each weekday", height=300))
    html(styles.note(
        "Note: July 2024 had five Mondays, Tuesdays and Wednesdays, so their totals look higher. "
        "The chart above uses the average per day to remove this effect."
    ))


def tab_vehicles(df):
    summary = metrics.vehicle_summary(df)
    html(styles.section("01", "Vehicle fleet", "Completed rides for every vehicle type."))
    columns = st.columns(len(summary)) if len(summary) else []
    for column, (_, row) in zip(columns, summary.iterrows()):
        with column:
            done = 0 if pd.isna(row["Completed"]) else int(row["Completed"])
            html(styles.vehicle_tile(row["Vehicle_Type"], VEHICLE_ICONS[row["Vehicle_Type"]], f"{done:,} rides"))

    html(styles.section("02", "Distance and value", "Top 5 vehicle types by total distance and the price paid per km."))
    top5 = summary.sort_values("Total_Km", ascending=False).head(5)
    left, right = st.columns(2)
    with left:
        show_chart(charts.bar(top5["Vehicle_Type"], top5["Total_Km"], "Top 5 vehicle types by total ride distance in km"))
    with right:
        show_chart(charts.bar(summary["Vehicle_Type"], summary["Avg_Distance"], "Average distance per completed ride in km", fmt=",.1f"))
    left, right = st.columns(2)
    with left:
        show_chart(charts.bar(summary["Vehicle_Type"], summary["Revenue_Per_KM"], "Revenue per km", fmt=",.1f"))
    with right:
        show_chart(charts.bar(summary["Vehicle_Type"], summary["Revenue"], "Revenue by vehicle type"))
    html(styles.note(
        "Autos travel about 10 km per ride while every other vehicle travels about 25 km, but the average booking "
        "value is almost the same. So Auto shows a much higher revenue per km. This happens because price does not depend on distance."
    ))

    html(styles.section("03", "Reliability and satisfaction", "How each vehicle type performs for riders."))
    left, right = st.columns(2)
    with left:
        show_chart(charts.stacked_status_by_vehicle(summary))
    with right:
        show_chart(charts.bar(summary["Vehicle_Type"], summary["Avg_Customer_Rating"], "Average customer rating", fmt=",.3f"))
    show_table(summary.round(3))


def tab_revenue(df):
    ok = metrics.only_success(df)
    pay = metrics.payment_summary(df)
    html(styles.section("01", "Revenue by payment method", "Completed rides only."))
    left, right = st.columns(2)
    with left:
        show_chart(charts.donut(pay["Payment_Method"], pay["Revenue"], "Revenue share by payment method"))
    with right:
        show_chart(charts.bar(pay["Payment_Method"], pay["Revenue"], "Revenue by payment method"))

    html(styles.section("02", "Top 5 customers by total booking value", "Value of completed rides for each customer."))
    top = metrics.top_customers(df, 5, "value")
    left, right = st.columns([3, 2])
    with left:
        show_chart(charts.bar(top["Customer_ID"], top["Total_Value"], "Top 5 customers by booking value", horizontal=True, height=300))
    with right:
        show_table(top)

    html(styles.section("03", "Ride distance per day", "Average and total kilometres of completed rides."))
    left, right = st.columns([3, 2])
    with left:
        show_chart(charts.distance_trend(metrics.daily_distance(df)))
    with right:
        show_chart(charts.distance_histogram(ok))

    html(styles.section("04", "Price against distance", "Price should normally rise with distance."))
    left, right = st.columns(2)
    with left:
        show_chart(charts.distance_value_scatter(ok))
    with right:
        show_chart(charts.fare_per_km_histogram(ok))
    html(styles.note(
        "The points show no upward slope, so booking value does not depend on distance. "
        "In normal pricing the value rises as distance increases."
    ))


def tab_cancellations(df):
    k = metrics.kpis(df)
    html(styles.section("01", "Failed bookings", "Where bookings are lost and how much money that costs."))
    kpi_row([
        ("Cancelled by drivers", fmt_pct(k["driver_cancel_rate"]), "Share of all bookings", "bad"),
        ("Cancelled by customers", fmt_pct(k["customer_cancel_rate"]), "Share of all bookings", "warn"),
        ("Driver not found", fmt_pct(k["no_driver_rate"]), "Share of all bookings", "warn"),
        ("Booking value lost", fmt_money(k["lost_value"]), "All failed bookings", "bad"),
    ])

    html(styles.section("02", "Why rides are cancelled", "Reasons given by customers and by drivers."))
    left, right = st.columns(2)
    with left:
        show_chart(charts.reason_bars(metrics.cancel_reasons(df, "customer"), "Customer cancel reasons", COLORS["amber"]))
    with right:
        show_chart(charts.reason_bars(metrics.cancel_reasons(df, "driver"), "Driver cancel reasons", COLORS["coral"]))

    html(styles.section("03", "Incomplete rides", "Rides marked successful but flagged as not fully completed."))
    left, right = st.columns([2, 1])
    with left:
        show_chart(charts.reason_bars(metrics.incomplete_reasons(df), "Reasons for incomplete rides", COLORS["violet"]))
    with right:
        kpi_row([("Incomplete rides", f"{k['incomplete_rides']:,}", f"{fmt_pct(k['incomplete_rate'])} of completed rides", "warn")])
        st.write("")
        kpi_row([("Value at risk", fmt_money(k["incomplete_value"]), "Counted inside revenue earned", "bad")])

    html(styles.section("04", "Pickup areas", "Busiest pickup areas and the areas with the lowest success rate."))
    places = metrics.location_summary(df, "Pickup_Location")
    low = places[places["Bookings"] >= 50].sort_values("Success_Rate").head(8)
    left, right = st.columns(2)
    with left:
        busy = places.head(8)
        show_chart(charts.bar(busy["Pickup_Location"], busy["Bookings"], "Busiest pickup areas", horizontal=True, height=320))
    with right:
        show_chart(charts.bar(low["Pickup_Location"], low["Success_Rate"] * 100, "Lowest success rate by pickup area in percent",
                              color=COLORS["coral"], horizontal=True, fmt=",.1f", height=320))


def tab_ratings(df):
    ok = metrics.only_success(df)
    k = metrics.kpis(df)
    html(styles.section("01", "Rating overview", "Ratings are given only for completed rides."))
    kpi_row([
        ("Average driver rating", f"{k['avg_driver_rating']:.2f}", "Out of 5", "good"),
        ("Average customer rating", f"{k['avg_customer_rating']:.2f}", "Out of 5", "good"),
        ("Driver rating 4.5 and above", fmt_pct(metrics.rating_summary(df).loc["4.5 to 5.0", "Driver"]), "Completed rides", ""),
        ("Driver rating below 3.5", fmt_pct(metrics.rating_summary(df).loc["3.0 to 3.4", "Driver"]), "Completed rides", "warn"),
    ])

    html(styles.section("02", "Rating distribution", "How scores are spread."))
    left, right = st.columns(2)
    with left:
        show_chart(charts.rating_histogram(ok))
    with right:
        show_chart(charts.rating_density(ok))

    html(styles.section("03", "Ratings by vehicle type", "Average scores for each vehicle."))
    summary = metrics.vehicle_summary(df)
    left, right = st.columns(2)
    with left:
        show_chart(charts.bar(summary["Vehicle_Type"], summary["Avg_Driver_Rating"], "Average driver rating", fmt=",.3f"))
    with right:
        show_chart(charts.bar(summary["Vehicle_Type"], summary["Avg_Customer_Rating"], "Average customer rating", fmt=",.3f"))
    html(styles.note(
        "Scores are spread almost evenly between 3.0 and 5.0, nobody scored below 3.0, and ratings do not change with "
        "price, distance or waiting time. So ratings alone cannot separate good rides from bad rides."
    ))


def tab_health(df):
    health = metrics.data_health(df)
    html(styles.section("01", "Data health checks", "Checks I did on the data before using it."))
    kpi_row([
        ("Same pickup and drop", f"{health['same_pickup_drop']:,}", f"{health['same_pickup_drop_completed']:,} completed", "warn"),
        ("Very high price per km", f"{health['very_high_fare_per_km']:,}", "Above 10 times the median", "bad"),
        ("Very low price per km", f"{health['very_low_fare_per_km']:,}", "Below a quarter of the median", "bad"),
        ("Value and distance link", f"{health['value_distance_corr']:.3f}", "Close to zero means no link", "warn"),
    ])

    html(styles.section("02", "Blank cells are not errors", "A cancelled ride never reaches payment, rating or reason steps."))
    missing = df.isna().sum()
    table = pd.DataFrame({"Column": missing.index, "Blank cells": missing.values})
    table = table[table["Blank cells"] > 0].copy()
    table["Share of rows"] = (table["Blank cells"] / max(len(df), 1)).map(lambda v: f"{v * 100:.1f}%")
    table = table[~table["Column"].isin(["Fare_Per_KM", "Distance_Band", "Failure_Owner"])]
    show_table(table)

    html(styles.section("03", "What this data cannot tell us", "Limits of this dataset."))
    for line in limits_of_data():
        st.markdown(f"- {line}")


def tab_insights(full):
    html(styles.section("01", "Key findings and recommendations",
                        "Written from the full month of data, not from the sidebar filters."))
    for item in build_insights(full):
        html(styles.insight_card(item["name"], item["body"], item["action"], item["priority"]))


def tab_sql(df):
    html(styles.section("01", "SQL lab", "The project SQL questions run on a live copy of the data."))
    queries = load_queries()
    if not queries:
        st.warning("The file ola_queries.sql was not found. Upload it to the sql folder of the repository.")
        return
    labels = [f"Q{q['number']}  {q['title']}" for q in queries]
    choice = st.selectbox("Pick a question", labels)
    query = queries[labels.index(choice)]
    st.code(query["sql"], language="sql")
    result = run_query(get_connection(), query["sql"])
    st.caption(f"Showing up to {len(result)} rows")
    show_table(result, height=320)
    st.download_button("Download result as CSV", result.to_csv(index=False), file_name=f"ola_q{query['number']}.csv")

    html(styles.section("02", "Write your own query", "Table name is ola_bookings and only SELECT queries are allowed."))
    text = st.text_area("Your query", "SELECT Vehicle_Type, COUNT(*) AS Rides FROM ola_bookings GROUP BY Vehicle_Type;", height=120)
    if st.button("Run query"):
        try:
            show_table(run_query(get_connection(), text), height=320)
        except Exception as error:
            st.error(f"Could not run the query: {error}")


def tab_powerbi():
    html(styles.section("01", "Power BI dashboard", "Interactive report built on the same cleaned data."))
    if POWERBI_EMBED_URL:
        components.iframe(POWERBI_EMBED_URL, height=640, scrolling=True)
        return
    html(styles.note(
        "No Power BI link is set yet. Publish the report from Power BI, copy the embed link, "
        "and paste it into POWERBI_EMBED_URL in src/config.py. The report will then appear here."
    ))
    st.markdown(
        "**Suggested report pages**\n\n"
        "- Overall: ride volume over time and booking status breakdown\n"
        "- Vehicle type: top 5 vehicle types by ride distance\n"
        "- Revenue: revenue by payment method, top 5 customers and daily distance\n"
        "- Cancellation: customer and driver cancel reasons\n"
        "- Ratings: driver and customer rating distribution"
    )


# Section: page

def main():
    # Show a clear message if the data file is missing from the repository
    try:
        full = get_data()
    except FileNotFoundError as error:
        st.error("The data file could not be found.")
        st.code(str(error))
        st.stop()
    html(styles.hero(
        "Ola Ride", "Insights",
        "Analysis of one month of Ola ride bookings: completed rides, cancellations, revenue, payments and ratings.",
        "RIDE SHARING AND MOBILITY ANALYTICS",
    ))
    filtered = apply_filters(full)
    if filtered.empty:
        st.warning("No rides match these filters. Please widen your selection in the sidebar.")
        st.stop()

    names = ["Overview", "Vehicles", "Revenue", "Cancellations", "Ratings",
             "Data Health", "Insights", "SQL Lab", "Power BI"]
    tabs = st.tabs(names)
    with tabs[0]:
        tab_overview(filtered)
    with tabs[1]:
        tab_vehicles(filtered)
    with tabs[2]:
        tab_revenue(filtered)
    with tabs[3]:
        tab_cancellations(filtered)
    with tabs[4]:
        tab_ratings(filtered)
    with tabs[5]:
        tab_health(filtered)
    with tabs[6]:
        tab_insights(full)
    with tabs[7]:
        tab_sql(full)
    with tabs[8]:
        tab_powerbi()

    html(f'<div style="text-align:center;color:{COLORS["muted"]};font-size:12px;margin-top:40px;">'
         'Ola Ride Insights · Built with Python, SQL, Plotly and Streamlit</div>')


main()
