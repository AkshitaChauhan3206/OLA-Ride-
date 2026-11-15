# Chart builders for the dashboard, all charts share the same dark look
import numpy as np
import plotly.graph_objects as go

from src.config import COLORS, SEQUENCE, STATUS_COLORS, STATUS_ORDER

FONT = "Inter, Segoe UI, sans-serif"


def with_alpha(hex_color, alpha):
    # Turn a hex colour into an rgba text so plotly accepts the transparency
    hex_color = hex_color.lstrip("#")
    red, green, blue = (int(hex_color[i:i + 2], 16) for i in (0, 2, 4))
    return f"rgba({red},{green},{blue},{alpha})"


def style(fig, title=None, height=340, legend=True):
    # Apply the common dark theme to a figure
    fig.update_layout(
        title=dict(text=title, x=0.01, font=dict(size=15, color=COLORS["text"])) if title else None,
        height=height,
        paper_bgcolor="rgba(0,0,0,0)",
        plot_bgcolor="rgba(0,0,0,0)",
        font=dict(family=FONT, color=COLORS["muted"], size=12),
        margin=dict(l=10, r=10, t=50 if title else 15, b=10),
        showlegend=legend,
        legend=dict(orientation="h", y=-0.18, x=0, font=dict(size=11)),
        hoverlabel=dict(bgcolor=COLORS["card"], font_size=12, bordercolor=COLORS["border"]),
    )
    fig.update_xaxes(showgrid=False, linecolor=COLORS["border"], zeroline=False)
    fig.update_yaxes(gridcolor=COLORS["border"], zeroline=False)
    return fig


def volume_over_time(daily):
    # Stacked area of bookings per day split by status
    fig = go.Figure()
    for status in STATUS_ORDER:
        if status in daily.columns:
            fig.add_trace(go.Scatter(
                x=daily.index, y=daily[status], name=status, mode="lines",
                stackgroup="one", line=dict(width=0.8, color=STATUS_COLORS[status]),
                fillcolor=with_alpha(STATUS_COLORS[status], 0.75),
            ))
    return style(fig, "Ride volume over time", 360)


def status_donut(table):
    # Donut chart of the booking status share
    fig = go.Figure(go.Pie(
        labels=table["Booking_Status"], values=table["Bookings"], hole=0.62,
        marker=dict(colors=[STATUS_COLORS[s] for s in table["Booking_Status"]],
                    line=dict(color=COLORS["bg"], width=3)),
        textinfo="percent", sort=False,
    ))
    return style(fig, "Booking status breakdown", 360)


def hourly_chart(hourly):
    # Bars for bookings and a line for success rate by hour
    fig = go.Figure()
    fig.add_trace(go.Bar(x=hourly["Hour"], y=hourly["Bookings"], name="Bookings",
                         marker_color=COLORS["lime"], opacity=0.85))
    fig.add_trace(go.Scatter(x=hourly["Hour"], y=hourly["Success_Rate"] * 100, name="Success rate %",
                             yaxis="y2", mode="lines+markers",
                             line=dict(color=COLORS["teal"], width=2), marker=dict(size=5)))
    fig.update_layout(yaxis2=dict(overlaying="y", side="right", showgrid=False,
                                  range=[0, 100], ticksuffix="%"))
    fig.update_xaxes(dtick=2, title="Hour of day")
    return style(fig, "Bookings and success rate by hour", 340)


def heatmap(matrix):
    # Weekday by hour heatmap of the average bookings
    fig = go.Figure(go.Heatmap(
        z=matrix.values, x=[str(h) for h in matrix.columns], y=list(matrix.index),
        colorscale=[[0, COLORS["card"]], [1, COLORS["lime"]]],
        colorbar=dict(thickness=10, outlinewidth=0),
        hovertemplate="%{y} at hour %{x}: %{z:.1f} bookings<extra></extra>",
    ))
    fig.update_yaxes(autorange="reversed")
    return style(fig, "Average bookings by weekday and hour", 340, legend=False)


def bar(labels, values, title, color=None, horizontal=False, fmt=",.0f", highlight_max=True, height=330):
    # Simple bar chart where the biggest bar is highlighted in lime
    # Blank values become zero so empty filters never break the chart
    values = [float(v) for v in np.nan_to_num(np.array(list(values), dtype=float))]
    labels = list(labels)
    colors = [COLORS["border"]] * len(values)
    if color:
        colors = [color] * len(values)
    elif highlight_max and values:
        colors = [COLORS["muted"]] * len(values)
        colors[int(np.nanargmax(values))] = COLORS["lime"]
    if horizontal:
        fig = go.Figure(go.Bar(x=values, y=labels, orientation="h", marker_color=colors,
                               text=[format(v, fmt) for v in values], textposition="outside",
                               cliponaxis=False))
        fig.update_yaxes(autorange="reversed", showgrid=False)
        fig.update_xaxes(showgrid=False, showticklabels=False)
    else:
        fig = go.Figure(go.Bar(x=labels, y=values, marker_color=colors,
                               text=[format(v, fmt) for v in values], textposition="outside",
                               cliponaxis=False))
    return style(fig, title, height, legend=False)


def stacked_status_by_vehicle(summary):
    # Share of each outcome inside every vehicle type
    fig = go.Figure()
    parts = [
        ("Success", "Success_Rate"), ("Canceled by Driver", "Driver_Cancel_Rate"),
        ("Canceled by Customer", "Customer_Cancel_Rate"), ("Driver Not Found", "No_Driver_Rate"),
    ]
    for status, column in parts:
        fig.add_trace(go.Bar(x=summary["Vehicle_Type"], y=summary[column] * 100, name=status,
                             marker_color=STATUS_COLORS[status]))
    fig.update_layout(barmode="stack", yaxis=dict(ticksuffix="%"))
    return style(fig, "Outcome share by vehicle type", 340)


def donut(labels, values, title, height=330):
    # Generic donut chart
    fig = go.Figure(go.Pie(
        labels=list(labels), values=list(values), hole=0.62, sort=False,
        marker=dict(colors=SEQUENCE[: len(list(labels))], line=dict(color=COLORS["bg"], width=3)),
        textinfo="percent",
    ))
    return style(fig, title, height)


def distance_trend(daily):
    # Bars for total kilometres and a line for average distance per ride
    fig = go.Figure()
    fig.add_trace(go.Bar(x=daily["Booking_Date"], y=daily["Total_Km"], name="Total km",
                         marker_color=COLORS["border"]))
    fig.add_trace(go.Scatter(x=daily["Booking_Date"], y=daily["Avg_Distance"], name="Average km per ride",
                             yaxis="y2", mode="lines+markers",
                             line=dict(color=COLORS["lime"], width=2), marker=dict(size=5)))
    fig.update_layout(yaxis2=dict(overlaying="y", side="right", showgrid=False))
    return style(fig, "Ride distance per day", 340)


def distance_histogram(ok):
    # Distribution of the distance of completed rides
    fig = go.Figure(go.Histogram(x=ok["Ride_Distance"], nbinsx=25, marker_color=COLORS["teal"], opacity=0.9))
    fig.update_xaxes(title="Ride distance in km")
    return style(fig, "Ride distance distribution", 330, legend=False)


def reason_bars(table, title, color):
    # Horizontal bars for cancel reasons
    return bar(table["Reason"], table["Rides"], title, color=color, horizontal=True, height=300)


def rating_histogram(ok):
    # Overlay of driver and customer rating distributions
    fig = go.Figure()
    fig.add_trace(go.Histogram(x=ok["Driver_Ratings"], name="Driver rating", xbins=dict(size=0.2),
                               marker_color=COLORS["lime"], opacity=0.75))
    fig.add_trace(go.Histogram(x=ok["Customer_Rating"], name="Customer rating", xbins=dict(size=0.2),
                               marker_color=COLORS["blue"], opacity=0.6))
    fig.update_layout(barmode="overlay")
    fig.update_xaxes(title="Rating")
    return style(fig, "Rating distribution", 330)


def rating_density(ok):
    # Heat map to compare driver rating with customer rating
    fig = go.Figure(go.Histogram2d(
        x=ok["Driver_Ratings"], y=ok["Customer_Rating"], nbinsx=10, nbinsy=10,
        colorscale=[[0, COLORS["card"]], [1, COLORS["lime"]]], colorbar=dict(thickness=10),
    ))
    fig.update_xaxes(title="Driver rating")
    fig.update_yaxes(title="Customer rating")
    return style(fig, "Customer rating against driver rating", 330, legend=False)


def distance_value_scatter(ok, sample=4000):
    # Random sample of rides to show how fare relates to distance
    part = ok.sample(min(sample, len(ok)), random_state=7)
    fig = go.Figure(go.Scattergl(
        x=part["Ride_Distance"], y=part["Booking_Value"], mode="markers",
        marker=dict(size=4, color=COLORS["lime"], opacity=0.35),
    ))
    fig.update_xaxes(title="Ride distance in km")
    fig.update_yaxes(title="Booking value")
    return style(fig, "Booking value against distance", 340, legend=False)


def fare_per_km_histogram(ok):
    # Histogram of price per kilometre, cut at 200 so the main shape is visible
    values = ok["Fare_Per_KM"].dropna()
    fig = go.Figure(go.Histogram(x=values[values <= 200], nbinsx=40, marker_color=COLORS["violet"]))
    fig.update_xaxes(title="Booking value per km, values above 200 not shown")
    return style(fig, "Price per kilometre", 340, legend=False)
