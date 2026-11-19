# Ola Ride Insights: main Streamlit dashboard
import itertools

import pandas as pd
import streamlit as st

from src import charts, metrics, styles
from src.config import (
    COLORS, GITHUB_URL, SLOT_ORDER, STREAMLIT_URL, VEHICLE_ORDER,
)
from src.data_loader import load_data
from src.insights import action_plan, limits_of_data
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

PAGES = [
    "Executive Summary", "Cancellations", "Demand", "Revenue and Customers",
    "Vehicles", "Action Plan", "SQL Lab",
]


# Section: data

@st.cache_data(show_spinner="Loading ride data")
def get_data():
    # Load once and keep in memory for every user
    return load_data()


@st.cache_resource(show_spinner="Preparing SQL lab")
def get_connection():
    # In memory database used by the SQL lab page
    return build_connection(get_data())


# Section: small helpers

def html(text):
    # Shortcut for writing custom HTML
    st.markdown(text, unsafe_allow_html=True)


def card():
    # Bordered box that holds one chart or table, older Streamlit versions get a plain box
    try:
        return st.container(border=True)
    except TypeError:
        return st.container()


def show_chart(fig):
    # Draw a chart, try the newer Streamlit option first and fall back to the older one
    key = f"chart_{next(chart_ids)}"
    try:
        st.plotly_chart(fig, width="stretch", key=key)
    except Exception:
        st.plotly_chart(fig, use_container_width=True, key=key)


def chart_card(title, takeaway, fig):
    # Chart with a title and a one line takeaway inside a box
    with card():
        html(styles.card_header(title, takeaway))
        show_chart(fig)


def table_card(title, takeaway, table_html):
    # Table with a title and a takeaway inside a box
    with card():
        html(styles.card_header(title, takeaway))
        html(table_html)


def kpi_row(cards):
    # Show a row of KPI cards, each card is label, value, sub text and tone
    columns = st.columns(len(cards))
    for column, item in zip(columns, cards):
        with column:
            html(styles.kpi_card(*item))


# Section: sidebar filters

def filter_defaults(df):
    # Starting value of every filter
    return {
        "f_dates": (df["Booking_Date"].min().date(), df["Booking_Date"].max().date()),
        "f_vehicle": VEHICLE_ORDER,
        "f_slot": SLOT_ORDER,
        "f_pickup": sorted(df["Pickup_Location"].unique()),
    }


def reset_filters(defaults):
    # Put every filter back to its starting value
    for key, value in defaults.items():
        st.session_state[key] = value


def apply_filters(df):
    # Sidebar controls that change every page
    defaults = filter_defaults(df)
    for key, value in defaults.items():
        st.session_state.setdefault(key, value)

    first, last = defaults["f_dates"]
    with st.sidebar:
        html(
            '<div style="font-size:18px;font-weight:700;margin-bottom:2px;">Filters</div>'
            f'<div style="color:{COLORS["muted"]};font-size:12px;margin-bottom:12px;">Apply to every page except SQL Lab</div>'
        )
        picked = st.date_input("Date range", min_value=first, max_value=last, key="f_dates")
        vehicles = st.multiselect("Vehicle type", VEHICLE_ORDER, key="f_vehicle")
        slots = st.multiselect("Time of day", SLOT_ORDER, key="f_slot")
        pickups = st.multiselect("Pickup area", defaults["f_pickup"], key="f_pickup")
        st.button("Reset filters", on_click=reset_filters, args=(defaults,))
        html(
            f'<div style="margin-top:18px;font-size:12.5px;">'
            f'<a href="{GITHUB_URL}" target="_blank" style="color:{COLORS["lime"]};text-decoration:none;">GitHub repository</a><br>'
            f'<a href="{STREAMLIT_URL}" target="_blank" style="color:{COLORS["lime"]};text-decoration:none;">Live dashboard</a></div>'
        )

    # A single picked date comes back as a one item tuple
    if isinstance(picked, (tuple, list)):
        start = picked[0]
        end = picked[1] if len(picked) == 2 else picked[0]
    else:
        start = end = picked

    mask = df["Booking_Date"].between(pd.Timestamp(start), pd.Timestamp(end))
    mask &= df["Vehicle_Type"].isin(vehicles)
    mask &= df["Time_Slot"].isin(slots)
    mask &= df["Pickup_Location"].isin(pickups)
    changed = sum(1 for key in defaults if st.session_state[key] != defaults[key])
    return df[mask], changed


# Section: pages

def page_summary(df):
    k = metrics.kpis(df)
    leak = metrics.value_leakage(df)
    cust = metrics.customer_summary(df)
    html(styles.page_heading("Executive Summary", "How many bookings become rides, and where the money is lost."))

    kpi_row([
        ("Total bookings", f"{k['total_bookings']:,}", f"{k['unique_customers']:,} customers", ""),
        ("Success rate", fmt_pct(k["success_rate"]), f"{k['success_rides']:,} completed rides", "good" if k["success_rate"] >= 0.7 else "warn"),
        ("Revenue earned", fmt_money(k["realised_revenue"]), "Completed rides only", "good"),
        ("Revenue lost", fmt_money(k["lost_value"]), f"{fmt_pct(metrics.safe_div(k['lost_value'], k['booked_value']))} of booked value", "bad"),
    ])
    st.write("")
    kpi_row([
        ("Average booking value", f"Rs {k['avg_booking_value']:,.0f}", "Completed rides", ""),
        ("Average distance", f"{k['avg_distance']:.1f} km", "Completed rides", ""),
        ("Repeat customers", fmt_pct(k["repeat_customer_share"]), f"{fmt_pct(cust['one_time_share'])} booked only once", "warn"),
        ("Incomplete rides", fmt_pct(k["incomplete_rate"]), f"{fmt_money(k['incomplete_value'])} at risk", "warn"),
    ])
    st.write("")

    left, right = st.columns(2)
    with left:
        trend = metrics.daily_trend(df)
        chart_card(
            "Daily bookings and success rate",
            f"The success rate stays close to <b>{fmt_pct(k['success_rate'])}</b> on every day, so the loss is steady and not a one day event.",
            charts.trend_chart(trend),
        )
    with right:
        driver_share = metrics.safe_div(leak["driver"], leak["booked"] - leak["earned"])
        chart_card(
            "Where the booked value goes",
            f"Driver cancellations are <b>{fmt_pct(driver_share, 0)}</b> of the lost value, the largest single reason.",
            charts.waterfall(leak),
        )

    html(styles.page_heading("Top priorities", "The three actions with the biggest effect. The full list is on the Action Plan page."))
    plan = action_plan(df)[:3]
    columns = st.columns(3)
    for rank, (column, item) in enumerate(zip(columns, plan), 1):
        with column:
            html(styles.priority_card(rank, item["action"], item["impact"], item["team"]))


def page_cancellations(df):
    k = metrics.kpis(df)
    service = metrics.service_cancel_summary(df)
    html(styles.page_heading("Cancellations", "Why bookings fail and how many of the reasons Ola can fix."))
    kpi_row([
        ("Cancelled by drivers", fmt_pct(k["driver_cancel_rate"]), "Share of all bookings", "bad"),
        ("Cancelled by customers", fmt_pct(k["customer_cancel_rate"]), "Share of all bookings", "warn"),
        ("Driver not found", fmt_pct(k["no_driver_rate"]), "Share of all bookings", "warn"),
        ("Service related cancels", fmt_pct(service["share"]), "Of customer cancels, Ola can fix", "bad"),
    ])
    st.write("")

    customer = metrics.cancel_reasons(df, "customer")
    driver = metrics.cancel_reasons(df, "driver")
    left, right = st.columns(2)
    with left:
        chart_card(
            "Why customers cancel",
            f"<b>{fmt_pct(service['share'], 0)}</b> of these cancels are caused by the driver not moving, the driver asking to cancel, or a faulty AC.",
            charts.hbar(customer["Reason"], customer["Rides"], COLORS["amber"], height=270),
        )
    with right:
        top_driver = driver.iloc[0] if len(driver) else None
        take = f"<b>{top_driver['Reason']}</b> is the top reason at {fmt_pct(top_driver['Share'])}." if top_driver is not None else ""
        chart_card("Why drivers cancel", take, charts.hbar(driver["Reason"], driver["Rides"], COLORS["coral"], height=270))

    incomplete = metrics.incomplete_reasons(df)
    left, right = st.columns([2, 1])
    with left:
        take = (
            f"{k['incomplete_rides']:,} completed rides were marked incomplete. "
            "Revenue should be reported with and without them."
        )
        chart_card("Why completed rides end incomplete", take, charts.hbar(incomplete["Reason"], incomplete["Rides"], COLORS["violet"], height=230))
    with right:
        kpi_row([("Incomplete rides", f"{k['incomplete_rides']:,}", f"{fmt_pct(k['incomplete_rate'])} of completed rides", "warn")])
        st.write("")
        kpi_row([("Value at risk", fmt_money(k["incomplete_value"]), "Counted inside revenue earned", "bad")])


def page_demand(df):
    hourly = metrics.hourly_profile(df)
    week = metrics.weekday_average(df)
    html(styles.page_heading("Demand", "When and where bookings come from."))
    busiest = hourly.loc[hourly["Bookings"].idxmax()]
    quietest = hourly.loc[hourly["Bookings"].idxmin()]
    gap = metrics.safe_div(busiest["Bookings"], quietest["Bookings"]) - 1
    per_day = metrics.safe_div(len(df), df["Booking_Date"].nunique())
    kpi_row([
        ("Bookings per day", f"{per_day:,.0f}", "Average", ""),
        ("Busiest hour", f"{int(busiest['Hour']):02d}:00", f"{int(busiest['Bookings']):,} bookings", ""),
        ("Quietest hour", f"{int(quietest['Hour']):02d}:00", f"{int(quietest['Bookings']):,} bookings", ""),
        ("Busiest vs quietest", fmt_pct(gap), "Small gap means no clear peak", "warn"),
    ])
    st.write("")

    left, right = st.columns([3, 2])
    with left:
        chart_card(
            "Bookings and success rate by hour",
            f"Demand is almost flat across the day, with only <b>{fmt_pct(gap)}</b> between the busiest and quietest hour.",
            charts.hourly_chart(hourly),
        )
    with right:
        chart_card(
            "Average bookings per day of the week",
            "Averages remove the calendar effect. July 2024 had five Mondays, Tuesdays and Wednesdays.",
            charts.column(week["Day_Name"].str[:3], week["Average_Per_Day"], COLORS["teal"], height=300),
        )

    pickups = metrics.top_pickups(df, 10)
    slots = metrics.time_slot_summary(df)
    left, right = st.columns(2)
    with left:
        chart_card(
            "Top 10 pickup areas by bookings",
            "Use this list to place drivers in the areas with the most bookings.",
            charts.hbar(pickups["Pickup_Location"], pickups["Bookings"], COLORS["lime"], height=330),
        )
    with right:
        chart_card(
            "Success rate by time of day",
            "Success is similar in every part of the day, so the shortage of drivers is not only at rush time.",
            charts.column(slots["Time_Slot"].astype(str), slots["Success_Rate"] * 100, COLORS["teal"], fmt=",.1f", suffix="%", height=330),
        )


def page_revenue(df):
    k = metrics.kpis(df)
    ok = metrics.only_success(df)
    pay = metrics.payment_summary(df)
    veh = metrics.vehicle_summary(df)
    health = metrics.data_health(df)
    freq = metrics.customer_frequency(df)
    html(styles.page_heading("Revenue and Customers", "How customers pay, what a kilometre earns, and how often customers return."))

    share = pay.set_index("Payment_Method")["Revenue_Share"] if len(pay) else pd.Series(dtype=float)
    kpi_row([
        ("Revenue earned", fmt_money(k["realised_revenue"]), "Completed rides", "good"),
        ("Average booking value", f"Rs {k['avg_booking_value']:,.0f}", "Per completed ride", ""),
        ("Cash share", fmt_pct(share.get("Cash", 0)), "Of revenue", "warn"),
        ("UPI share", fmt_pct(share.get("UPI", 0)), "Of revenue", ""),
    ])
    st.write("")

    left, right = st.columns(2)
    with left:
        colors = [COLORS["lime"], COLORS["teal"], COLORS["blue"], COLORS["violet"]]
        chart_card(
            "Revenue by payment method",
            f"Cash brings <b>{fmt_pct(share.get('Cash', 0))}</b> of revenue. Cards together are under 5 percent.",
            charts.donut(pay["Payment_Method"], pay["Revenue"], colors[: len(pay)], center_text=fmt_money(k["realised_revenue"])),
        )
    with right:
        best = veh.loc[veh["Revenue_Per_KM"].idxmax(), "Vehicle_Type"] if len(veh) and veh["Revenue_Per_KM"].notna().any() else None
        chart_card(
            "Revenue per kilometre by vehicle",
            "Auto earns far more per km only because short rides cost the same as long ones.",
            charts.column(veh["Vehicle_Type"], veh["Revenue_Per_KM"], charts.NEUTRAL, fmt=",.1f", height=290, highlight=best),
        )

    left, right = st.columns(2)
    with left:
        chart_card(
            "Booking value against distance",
            f"No upward slope. The link between price and distance is only <b>{health['value_distance_corr']:.3f}</b>.",
            charts.price_scatter(ok),
        )
    with right:
        once = metrics.safe_div(freq.loc[freq["Bookings_Per_Customer"] == 1, "Customers"].sum(), freq["Customers"].sum())
        labels = [f"{int(n)} booking" + ("s" if n > 1 else "") for n in freq["Bookings_Per_Customer"]]
        chart_card(
            "Customers by number of bookings",
            f"<b>{fmt_pct(once)}</b> of customers booked only once in the month.",
            charts.hbar(labels, freq["Customers"], COLORS["blue"], height=290),
        )

    top = metrics.top_customers(df, 5, "value")
    rows = [[r["Customer_ID"], f"{int(r['Rides'])}", f"Rs {r['Total_Value']:,.0f}"] for _, r in top.iterrows()]
    left, right = st.columns([3, 2])
    with left:
        table_card(
            "Top 5 customers by total booking value",
            "The best customers made only a few rides, so there is no group of heavy repeat users yet.",
            styles.html_table(["Customer", "Completed rides", "Total value"], rows),
        )
    with right:
        with card():
            html(styles.card_header("Pricing checks", "Rides whose price per km looks wrong."))
            kpi_row([("Very high price per km", f"{health['very_high_fare_per_km']:,}", "Above 10 times the median", "bad")])
            st.write("")
            kpi_row([("Very low price per km", f"{health['very_low_fare_per_km']:,}", "Below a quarter of the median", "bad")])


def page_vehicles(df):
    summary = metrics.vehicle_summary(df)
    html(styles.page_heading("Vehicles", "How every vehicle type performs on volume, reliability, price and ratings."))

    rows = []
    for _, r in summary.iterrows():
        rows.append([
            f"<b>{r['Vehicle_Type']}</b>",
            f"{int(r['Bookings']):,}",
            styles.data_bar(fmt_pct(r["Success_Rate"]), r["Success_Rate"] * 100),
            fmt_pct(r["Driver_Cancel_Rate"]),
            f"{r['Avg_Distance']:.1f}" if pd.notna(r["Avg_Distance"]) else "0.0",
            f"Rs {r['Avg_Value']:,.0f}" if pd.notna(r["Avg_Value"]) else "Rs 0",
            f"{r['Revenue_Per_KM']:.1f}" if pd.notna(r["Revenue_Per_KM"]) else "0.0",
            f"{r['Avg_Driver_Rating']:.2f}" if pd.notna(r["Avg_Driver_Rating"]) else "0.00",
            f"{r['Avg_Customer_Rating']:.2f}" if pd.notna(r["Avg_Customer_Rating"]) else "0.00",
        ])
    headers = ["Vehicle", "Bookings", "Success rate", "Driver cancels", "Avg km", "Avg value", "Rs per km", "Driver rating", "Customer rating"]
    table_card(
        "Vehicle scorecard",
        "Every vehicle type succeeds about 62 percent of the time and is rated about 4.0, so no vehicle type is the problem.",
        styles.html_table(headers, rows),
    )
    st.write("")

    top5 = summary.sort_values("Total_Km", ascending=False).head(5)
    left, right = st.columns(2)
    with left:
        chart_card("How bookings end for each vehicle", "Outcome shares are almost identical for every vehicle type.", charts.outcome_stack(summary))
    with right:
        chart_card(
            "Top 5 vehicle types by total distance",
            "Total kilometres of completed rides.",
            charts.hbar(top5["Vehicle_Type"], top5["Total_Km"], COLORS["teal"], height=330),
        )


def page_actions(df):
    html(styles.page_heading("Action Plan", "What to fix first, who owns it, and what it could be worth."))
    k = metrics.kpis(df)

    with card():
        html(styles.card_header(
            "Revenue opportunity simulator",
            "Choose how much of each failure type can be recovered. Recovered bookings are assumed to be completed at the current average booking value.",
        ))
        a, b, c = st.columns(3)
        with a:
            driver_pct = st.slider("Fewer driver cancellations", 0, 50, 20, format="%d%%")
        with b:
            service_pct = st.slider("Fewer service related customer cancels", 0, 50, 30, format="%d%%")
        with c:
            no_driver_pct = st.slider("Fewer no driver found", 0, 50, 20, format="%d%%")
        result = metrics.opportunity(df, driver_pct / 100, service_pct / 100, no_driver_pct / 100)
        kpi_row([
            ("Extra completed rides", f"{result['extra_rides']:,.0f}", "Every month", "good"),
            ("Extra revenue", fmt_money(result["extra_revenue"]), "Every month", "good"),
            ("New success rate", fmt_pct(result["new_success_rate"]), f"Now {fmt_pct(k['success_rate'])}", "good"),
        ])
        st.write("")
        show_chart(charts.lever_chart(result["levers"]))

    st.write("")
    html(styles.page_heading("Priority actions", "Ordered by effect on revenue. Money estimates use the same simple assumptions as the simulator."))
    with card():
        html(styles.action_table(action_plan(df)))

    with st.expander("What this data cannot tell us"):
        for line in limits_of_data():
            st.markdown(f"- {line}")


def page_sql(df):
    html(styles.page_heading("SQL Lab", "The project SQL questions run on a live copy of the full data."))
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
    st.dataframe(result, hide_index=True)
    st.download_button("Download result as CSV", result.to_csv(index=False), file_name=f"ola_q{query['number']}.csv")

    html(styles.card_header("Write your own query", "The table name is ola_bookings and only SELECT queries are allowed."))
    text = st.text_area("Your query", "SELECT Vehicle_Type, COUNT(*) AS Rides FROM ola_bookings GROUP BY Vehicle_Type;", height=120)
    if st.button("Run query"):
        try:
            st.dataframe(run_query(get_connection(), text), hide_index=True)
        except Exception as error:
            st.error(f"Could not run the query: {error}")


# Section: page

def main():
    # Show a clear message if the data file is missing from the repository
    try:
        full = get_data()
    except FileNotFoundError as error:
        st.error("The data file could not be found.")
        st.code(str(error))
        st.stop()

    filtered, changed = apply_filters(full)
    first, last = full["Booking_Date"].min(), full["Booking_Date"].max()
    html(styles.top_bar(
        f"{first.strftime('%d %b')} to {last.strftime('%d %b %Y')}",
        f"{len(filtered):,} bookings shown",
        f"{changed} filter{'s' if changed != 1 else ''} active" if changed else "All data",
    ))

    page = st.radio("Page", PAGES, horizontal=True, label_visibility="collapsed", key="page")
    if page == "SQL Lab":
        page_sql(full)
        return
    if filtered.empty:
        st.warning("No rides match these filters. Please widen your selection in the sidebar.")
        st.stop()

    pages = {
        "Executive Summary": page_summary,
        "Cancellations": page_cancellations,
        "Demand": page_demand,
        "Revenue and Customers": page_revenue,
        "Vehicles": page_vehicles,
        "Action Plan": page_actions,
    }
    pages[page](filtered)

    html(f'<div style="text-align:center;color:{COLORS["muted"]};font-size:12px;margin-top:36px;">'
         'Ola Ride Insights · Built with Python, SQL, Plotly and Streamlit</div>')


main()
