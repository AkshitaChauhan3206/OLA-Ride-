# Builds the written findings and recommendations from the data itself
# Numbers inside the text are calculated, so they always match the data
from src import metrics
from src.styles import fmt_money, fmt_pct


def build_insights(df):
    # Collect every number first so the text below stays easy to read
    k = metrics.kpis(df)
    health = metrics.data_health(df)
    pay = metrics.payment_summary(df).set_index("Payment_Method")
    veh = metrics.vehicle_summary(df).set_index("Vehicle_Type")
    cust = metrics.cancel_reasons(df, "customer").set_index("Reason")
    drv = metrics.cancel_reasons(df, "driver").set_index("Reason")
    inc = metrics.incomplete_reasons(df).set_index("Reason")
    hourly = metrics.hourly_profile(df)
    freq = metrics.customer_frequency(df)

    total = k["total_bookings"]
    one_point_value = total * 0.01 * k["avg_booking_value"]
    driver_fault = cust.loc["Driver is not moving towards pickup location", "Share"] + cust.loc["Driver asked to cancel", "Share"]
    fixable = driver_fault + cust.loc["AC is Not working", "Share"]
    hour_gap = (hourly["Success_Rate"].max() - hourly["Success_Rate"].min()) * 100
    hour_spread = hourly["Bookings"].max() / hourly["Bookings"].min() - 1
    auto_km = veh.loc["Auto", "Avg_Distance"]
    other_km = veh.drop("Auto")["Avg_Distance"].mean()
    auto_value = veh.loc["Auto", "Avg_Value"]
    other_value = veh.drop("Auto")["Avg_Value"].mean()

    return [
        {
            "name": f"Only {fmt_pct(k['success_rate'])} of bookings are completed",
            "priority": "high",
            "body": (
                f"Out of {total:,} bookings, {k['success_rides']:,} were completed. The other "
                f"{fmt_pct(1 - k['success_rate'])} failed, so booking value of {fmt_money(k['lost_value'])} was not earned, "
                f"against {fmt_money(k['realised_revenue'])} earned. Each extra 1 percent of success rate is worth about "
                f"{fmt_money(one_point_value)} a month."
            ),
            "action": "Set a target such as 70 percent success rate and track it every week by vehicle type.",
        },
        {
            "name": "Driver cancellations are the biggest reason for lost bookings",
            "priority": "high",
            "body": (
                f"Drivers cancelled {fmt_pct(k['driver_cancel_rate'])} of all bookings, which is "
                f"{k['driver_cancel_rate'] / k['customer_cancel_rate']:.1f} times the customer cancel rate of "
                f"{fmt_pct(k['customer_cancel_rate'])}. The most common driver reasons are personal or car related issues "
                f"({fmt_pct(drv.loc['Personal & Car related issue', 'Share'])}) and customer related issues "
                f"({fmt_pct(drv.loc['Customer related issue', 'Share'])})."
            ),
            "action": "Add a cancel score for drivers, give penalties for repeated cancels and reassign the booking quickly.",
        },
        {
            "name": "Most customer cancellations are caused by the service",
            "priority": "high",
            "body": (
                f"{fmt_pct(driver_fault)} of customer cancellations say the driver was not moving towards the pickup point "
                f"or asked the customer to cancel. Together with AC not working ({fmt_pct(cust.loc['AC is Not working', 'Share'])}), "
                f"{fmt_pct(fixable)} of customer cancellations are problems the company can fix. "
                f"Only change of plans and wrong address are the customer's own reasons."
            ),
            "action": "Send an alert when a driver does not move after accepting, stop drivers from asking customers to cancel, and check the AC in vehicles.",
        },
        {
            "name": "Price does not depend on distance",
            "priority": "high",
            "body": (
                f"The correlation between booking value and ride distance is {health['value_distance_corr']:.3f}, "
                f"which is almost zero. Autos travel {auto_km:.1f} km on average against {other_km:.1f} km for other vehicles, "
                f"but an Auto booking costs Rs {auto_value:.0f} against Rs {other_value:.0f}. About "
                f"{health['very_high_fare_per_km']:,} completed rides cost more than ten times the median price per km, "
                f"and {health['very_low_fare_per_km']:,} cost less than a quarter of it."
            ),
            "action": "Check the pricing logic. If the data export is wrong it should be corrected, otherwise the fare calculation needs review.",
        },
        {
            "name": "Driver not found happens everywhere",
            "priority": "medium",
            "body": (
                f"{fmt_pct(k['no_driver_rate'])} of bookings ended with no driver found. The rate is almost the same across "
                f"hours, days, areas and vehicle types, so there is a general shortage of drivers and it is not only a peak time problem."
            ),
            "action": "Increase the driver search area in steps, give driver incentives and recruit more drivers.",
        },
        {
            "name": "More than half of the revenue is paid in cash",
            "priority": "medium",
            "body": (
                f"Cash is {fmt_pct(pay.loc['Cash', 'Revenue_Share'])} of revenue and UPI is "
                f"{fmt_pct(pay.loc['UPI', 'Revenue_Share'])}. Credit and debit cards together are only "
                f"{fmt_pct(pay.loc['Credit Card', 'Revenue_Share'] + pay.loc['Debit Card', 'Revenue_Share'])}."
            ),
            "action": "Give a small UPI cashback so that more riders pay digitally.",
        },
        {
            "name": "Some completed rides are marked incomplete",
            "priority": "medium",
            "body": (
                f"{k['incomplete_rides']:,} rides ({fmt_pct(k['incomplete_rate'])} of completed rides, "
                f"worth {fmt_money(k['incomplete_value'])}) have status Success but are also marked incomplete. "
                f"Vehicle breakdown is the reason for {fmt_pct(inc.loc['Vehicle Breakdown', 'Share'])} of them and "
                f"customer demand for {fmt_pct(inc.loc['Customer Demand', 'Share'])}."
            ),
            "action": "Show revenue with and without incomplete rides, and add vehicle checks to reduce breakdowns.",
        },
        {
            "name": "There is no peak hour in this data",
            "priority": "low",
            "body": (
                f"Bookings are close to {hourly['Bookings'].mean():,.0f} in every hour. The busiest hour is only "
                f"{hour_spread * 100:.1f} percent above the quietest hour, and the success rate changes by just {hour_gap:.1f} points "
                f"during the day. Monday, Tuesday and Wednesday show higher totals only because July 2024 had five of each."
            ),
            "action": "Keep driver supply steady through the day and test surge pricing in small trials first.",
        },
        {
            "name": "Ratings do not separate good rides from bad rides",
            "priority": "medium",
            "body": (
                f"Average driver and customer ratings are {k['avg_driver_rating']:.2f} and "
                f"{k['avg_customer_rating']:.2f}. Ratings are spread evenly between 3.0 and 5.0, nobody gave less than 3.0, "
                f"and ratings do not change with price, distance or waiting time."
            ),
            "action": "Collect a reason with every rating and check that low ratings are not removed before storage.",
        },
        {
            "name": "Most customers booked only once",
            "priority": "medium",
            "body": (
                f"Out of {k['unique_customers']:,} customers, only {fmt_pct(k['repeat_customer_share'])} booked more than "
                f"once in the month and nobody booked more than {int(freq['Bookings_Per_Customer'].max())} times. "
                f"There is no group of loyal repeat customers yet."
            ),
            "action": "Give an offer for the second ride and track the repeat rate every month.",
        },
        {
            "name": "Some bookings have the same pickup and drop area",
            "priority": "low",
            "body": (
                f"{health['same_pickup_drop']:,} bookings start and end in the same area, and "
                f"{health['same_pickup_drop_completed']:,} of them were completed with an average distance of about 23 km, "
                f"which is not possible for the same place."
            ),
            "action": "Add a check in the booking app and review these records for location errors.",
        },
    ]


def limits_of_data():
    # Things this dataset cannot tell us
    return [
        "Only one month of data, so trends, seasons and growth cannot be measured.",
        "No driver id, so driver level performance and fraud cannot be checked.",
        "No surge multiplier or base fare, so the pricing logic cannot be rebuilt.",
        "No exact map points, so pickup and drop distance cannot be verified.",
        "Units of V_TAT and C_TAT are not given, they look like seconds and should be confirmed.",
    ]
