# Chart builders for the dashboard, every chart shares the same clean style
# Titles are written by the app, so the charts here have no title
import numpy as np
import plotly.graph_objects as go

from src.config import COLORS, STATUS_COLORS

FONT = "Inter, Segoe UI, sans-serif"
GRID = "#1D242C"
NEUTRAL = "#5B6674"


def with_alpha(hex_color, alpha):
    # Turn a hex colour into an rgba text so plotly accepts the transparency
    hex_color = hex_color.lstrip("#")
    red, green, blue = (int(hex_color[i:i + 2], 16) for i in (0, 2, 4))
    return f"rgba({red},{green},{blue},{alpha})"


def style(fig, height=300, legend=False):
    # Common look for every chart
    fig.update_layout(
        height=height,
        paper_bgcolor="rgba(0,0,0,0)",
        plot_bgcolor="rgba(0,0,0,0)",
        font=dict(family=FONT, color=COLORS["muted"], size=12),
        margin=dict(l=4, r=8, t=10, b=4),
        showlegend=legend,
        legend=dict(orientation="h", y=1.14, x=0, font=dict(size=11), bgcolor="rgba(0,0,0,0)"),
        hoverlabel=dict(bgcolor=COLORS["card"], font_size=12, bordercolor=COLORS["border"]),
        bargap=0.38,
    )
    fig.update_xaxes(showgrid=False, showline=True, linecolor=COLORS["border"], zeroline=False,
                     tickfont=dict(size=11), automargin=True)
    fig.update_yaxes(gridcolor=GRID, zeroline=False, showline=False, tickfont=dict(size=11), automargin=True)
    return fig


def clean(values):
    # Blank values become zero so empty filters never break a chart
    return [float(v) for v in np.nan_to_num(np.array(list(values), dtype=float))]


def trend_chart(daily):
    # Completed and failed bookings per day with the success rate line
    fig = go.Figure()
    fig.add_trace(go.Bar(x=daily["Booking_Date"], y=daily["Completed"], name="Completed", marker_color=COLORS["lime"]))
    fig.add_trace(go.Bar(x=daily["Booking_Date"], y=daily["Failed"], name="Failed",
                         marker_color=with_alpha(COLORS["coral"], 0.6)))
    fig.add_trace(go.Scatter(x=daily["Booking_Date"], y=daily["Success_Rate"] * 100, name="Success rate",
                             yaxis="y2", mode="lines", line=dict(color="#FFFFFF", width=2)))
    fig.update_layout(barmode="stack", yaxis2=dict(overlaying="y", side="right", range=[0, 100],
                                                   showgrid=False, ticksuffix="%"))
    return style(fig, 320, legend=True)


def waterfall(leak):
    # Booked value minus each kind of loss gives the revenue earned
    to_cr = 1e7
    labels = ["Booked value", "Driver cancelled", "Customer cancelled", "No driver found", "Revenue earned"]
    values = [leak["booked"], -leak["driver"], -leak["customer"], -leak["no_driver"], leak["earned"]]
    text = [f"{abs(v) / to_cr:.2f} Cr" for v in values]
    fig = go.Figure(go.Waterfall(
        x=labels, y=[v / to_cr for v in values],
        measure=["absolute", "relative", "relative", "relative", "total"],
        text=text, textposition="outside", cliponaxis=False,
        connector=dict(line=dict(color=COLORS["border"])),
        increasing=dict(marker=dict(color=COLORS["lime"])),
        decreasing=dict(marker=dict(color=COLORS["coral"])),
        totals=dict(marker=dict(color=COLORS["teal"])),
    ))
    fig.update_yaxes(title="Rs crore")
    return style(fig, 320)


def hbar(labels, values, color, fmt=",.0f", suffix="", height=280):
    # Horizontal bars with the value written at the end of each bar
    values = clean(values)
    fig = go.Figure(go.Bar(
        x=values, y=list(labels), orientation="h", marker_color=color,
        text=[format(v, fmt) + suffix for v in values], textposition="outside", cliponaxis=False,
        textfont=dict(color=COLORS["text"], size=11),
    ))
    fig.update_yaxes(autorange="reversed", showgrid=False)
    fig.update_xaxes(showgrid=False, showticklabels=False, showline=False)
    return style(fig, height)


def column(labels, values, color, fmt=",.0f", suffix="", height=280, highlight=None):
    # Vertical bars, one bar can be highlighted in lime
    values = clean(values)
    labels = list(labels)
    colors = [color] * len(values)
    if highlight in labels:
        colors = [NEUTRAL if lab != highlight else COLORS["lime"] for lab in labels]
    fig = go.Figure(go.Bar(
        x=labels, y=values, marker_color=colors,
        text=[format(v, fmt) + suffix for v in values], textposition="outside", cliponaxis=False,
        textfont=dict(color=COLORS["text"], size=11),
    ))
    fig.update_yaxes(showticklabels=False)
    return style(fig, height)


def hourly_chart(hourly):
    # Bars for bookings and a line for the success rate in every hour
    fig = go.Figure()
    fig.add_trace(go.Bar(x=hourly["Hour"], y=hourly["Bookings"], name="Bookings",
                         marker_color=with_alpha(COLORS["lime"], 0.85)))
    fig.add_trace(go.Scatter(x=hourly["Hour"], y=hourly["Success_Rate"] * 100, name="Success rate",
                             yaxis="y2", mode="lines+markers", line=dict(color="#FFFFFF", width=2),
                             marker=dict(size=5)))
    fig.update_layout(yaxis2=dict(overlaying="y", side="right", range=[0, 100], showgrid=False, ticksuffix="%"))
    fig.update_xaxes(dtick=2)
    return style(fig, 300, legend=True)


def donut(labels, values, colors, center_text="", height=290):
    # Donut chart with a short text in the middle
    fig = go.Figure(go.Pie(
        labels=list(labels), values=clean(values), hole=0.7, sort=False,
        marker=dict(colors=colors, line=dict(color=COLORS["bg"], width=3)), textinfo="percent",
        textfont=dict(size=12),
    ))
    if center_text:
        fig.add_annotation(text=center_text, showarrow=False, font=dict(size=18, color=COLORS["text"]))
    fig = style(fig, height, legend=True)
    fig.update_layout(legend=dict(orientation="v", x=1.0, y=0.5))
    return fig


def outcome_stack(summary):
    # How every vehicle type ends its bookings, shown as 100 percent bars
    parts = [
        ("Success", "Success_Rate"), ("Canceled by Driver", "Driver_Cancel_Rate"),
        ("Canceled by Customer", "Customer_Cancel_Rate"), ("Driver Not Found", "No_Driver_Rate"),
    ]
    fig = go.Figure()
    for status, col in parts:
        fig.add_trace(go.Bar(y=summary["Vehicle_Type"], x=summary[col] * 100, name=status, orientation="h",
                             marker_color=STATUS_COLORS[status],
                             text=[f"{v * 100:.0f}%" for v in summary[col]], textposition="inside",
                             textfont=dict(color="#0B0D10", size=11)))
    fig.update_layout(barmode="stack")
    fig.update_yaxes(autorange="reversed", showgrid=False)
    fig.update_xaxes(range=[0, 100], showticklabels=False, showline=False)
    return style(fig, 330, legend=True)


def price_scatter(ok, sample=3000):
    # Random sample of completed rides to show how price relates to distance
    part = ok.sample(min(sample, len(ok)), random_state=7) if len(ok) else ok
    fig = go.Figure(go.Scattergl(
        x=part["Ride_Distance"], y=part["Booking_Value"], mode="markers",
        marker=dict(size=4, color=COLORS["lime"], opacity=0.3),
    ))
    fig.update_xaxes(title="Ride distance in km")
    fig.update_yaxes(title="Booking value in Rs")
    return style(fig, 300)


def lever_chart(levers):
    # Extra revenue from every improvement lever in the simulator
    labels = list(levers.keys())
    values = [levers[name]["revenue"] / 1e5 for name in labels]
    return hbar(labels, values, COLORS["teal"], fmt=",.1f", suffix=" L", height=230)
