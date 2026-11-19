# Look and feel of the dashboard: CSS and small HTML helpers
from src.config import COLORS

CSS = f"""
<style>
@import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700&display=swap');

html, body, [class*="css"] {{ font-family: 'Inter', sans-serif; }}
.stApp {{
    background:
        radial-gradient(900px 380px at 100% -8%, rgba(215,227,43,0.07), transparent 60%),
        {COLORS["bg"]};
}}
#MainMenu, footer, header {{ visibility: hidden; }}
.block-container {{ padding-top: 1.2rem; padding-bottom: 3rem; max-width: 1320px; }}

/* Sidebar */
section[data-testid="stSidebar"] {{ background: #0F1318; border-right: 1px solid {COLORS["border"]}; }}
section[data-testid="stSidebar"] label p {{ font-size: 12.5px; font-weight: 600; color: {COLORS["muted"]}; }}

/* Top bar */
.topbar {{
    display: flex; justify-content: space-between; align-items: center;
    padding: 4px 0 16px 0; margin-bottom: 14px; border-bottom: 1px solid {COLORS["border"]};
}}
.brand {{ display: flex; align-items: center; gap: 14px; }}
.ring {{
    width: 30px; height: 30px; border-radius: 50%; border: 6px solid {COLORS["lime"]};
    box-sizing: border-box; position: relative;
}}
.ring:after {{
    content: ""; position: absolute; width: 8px; height: 8px; border-radius: 50%;
    background: {COLORS["lime"]}; top: 5px; left: 5px;
}}
.brand .name {{ font-size: 21px; font-weight: 700; color: {COLORS["text"]}; line-height: 1.1; }}
.brand .sub {{ font-size: 12px; color: {COLORS["muted"]}; margin-top: 2px; }}
.badges {{ display: flex; gap: 8px; flex-wrap: wrap; justify-content: flex-end; }}
.badge {{
    font-size: 12px; font-weight: 600; color: {COLORS["muted"]}; background: {COLORS["card"]};
    border: 1px solid {COLORS["border"]}; padding: 6px 12px; border-radius: 999px;
}}
.badge.hot {{ color: {COLORS["lime"]}; border-color: rgba(215,227,43,0.35); background: rgba(215,227,43,0.07); }}

/* Page menu */
div[role="radiogroup"] {{ gap: 6px; flex-wrap: wrap; margin-bottom: 6px; }}
div[role="radiogroup"] > label {{
    background: {COLORS["card"]}; border: 1px solid {COLORS["border"]}; border-radius: 999px;
    padding: 6px 16px; cursor: pointer; margin: 0;
}}
div[role="radiogroup"] > label > div:first-child {{ display: none; }}
div[role="radiogroup"] > label p {{ font-size: 13px; font-weight: 600; color: {COLORS["muted"]}; }}
div[role="radiogroup"] > label:has(input:checked) {{
    background: rgba(215,227,43,0.12); border-color: rgba(215,227,43,0.6);
}}
div[role="radiogroup"] > label:has(input:checked) p {{ color: {COLORS["lime"]}; }}

/* KPI cards */
.kpi {{
    background: {COLORS["card"]}; border: 1px solid {COLORS["border"]}; border-radius: 14px;
    padding: 15px 18px; height: 100%; position: relative; overflow: hidden;
}}
.kpi:before {{ content: ""; position: absolute; left: 0; top: 0; bottom: 0; width: 3px; background: {COLORS["border"]}; }}
.kpi.good:before {{ background: {COLORS["lime"]}; }}
.kpi.bad:before {{ background: {COLORS["coral"]}; }}
.kpi.warn:before {{ background: {COLORS["amber"]}; }}
.kpi .label {{ font-size: 11.5px; letter-spacing: .7px; text-transform: uppercase; color: {COLORS["muted"]}; font-weight: 600; }}
.kpi .value {{ font-size: 27px; font-weight: 700; color: {COLORS["text"]}; margin: 6px 0 2px 0; }}
.kpi .sub {{ font-size: 12px; color: {COLORS["muted"]}; }}

/* Card headings */
.chead {{ margin-bottom: 4px; }}
.ctitle {{ font-size: 15px; font-weight: 700; color: {COLORS["text"]}; }}
.ctake {{ font-size: 12.5px; color: {COLORS["muted"]}; margin-top: 3px; line-height: 1.5; }}
.ctake b {{ color: {COLORS["lime"]}; font-weight: 600; }}

/* Page headings */
.page-title {{ font-size: 20px; font-weight: 700; color: {COLORS["text"]}; margin: 14px 0 2px 0; }}
.page-sub {{ font-size: 13px; color: {COLORS["muted"]}; margin-bottom: 14px; }}

/* Notes */
.note {{
    background: rgba(255,255,255,0.03); border: 1px solid {COLORS["border"]};
    color: #B9C1CC; padding: 12px 16px; border-radius: 12px; font-size: 13px; line-height: 1.6;
}}

/* Priority cards */
.prio {{
    background: {COLORS["card"]}; border: 1px solid {COLORS["border"]}; border-radius: 14px;
    padding: 14px 16px; height: 100%;
}}
.prio .rank {{ font-size: 11px; font-weight: 700; letter-spacing: 1px; color: {COLORS["lime"]}; }}
.prio .what {{ font-size: 14px; font-weight: 600; color: {COLORS["text"]}; margin: 6px 0; line-height: 1.45; }}
.prio .money {{ font-size: 13px; color: {COLORS["lime"]}; font-weight: 600; }}
.prio .team {{ font-size: 12px; color: {COLORS["muted"]}; margin-top: 4px; }}

/* Tables */
.dtable {{ width: 100%; border-collapse: collapse; font-size: 13px; }}
.dtable th {{
    text-align: left; color: {COLORS["muted"]}; font-weight: 600; font-size: 11.5px; letter-spacing: .6px;
    text-transform: uppercase; padding: 10px 12px; border-bottom: 1px solid {COLORS["border"]};
}}
.dtable td {{ padding: 11px 12px; border-bottom: 1px solid #1A2028; color: {COLORS["text"]}; vertical-align: middle; }}
.dtable tr:hover td {{ background: rgba(255,255,255,0.02); }}
.dtable .num {{ text-align: right; font-variant-numeric: tabular-nums; }}
.bar {{ display: flex; align-items: center; gap: 8px; min-width: 120px; }}
.bar .track {{ flex: 1; height: 6px; background: #222A33; border-radius: 99px; overflow: hidden; }}
.bar .fill {{ height: 100%; background: {COLORS["lime"]}; border-radius: 99px; }}
.tag {{ font-size: 11px; font-weight: 700; padding: 3px 9px; border-radius: 999px; }}
.tag.high {{ color: {COLORS["coral"]}; background: rgba(255,107,107,0.12); }}
.tag.medium {{ color: {COLORS["amber"]}; background: rgba(255,176,32,0.12); }}
.tag.low {{ color: {COLORS["teal"]}; background: rgba(45,212,191,0.12); }}
</style>
"""


def top_bar(period_text, bookings_text, filter_text):
    # Slim header with the brand name and the current data scope
    return (
        '<div class="topbar">'
        '<div class="brand"><div class="ring"></div>'
        '<div><div class="name">Ola Ride Insights</div>'
        '<div class="sub">Booking performance dashboard</div></div></div>'
        '<div class="badges">'
        f'<span class="badge">{period_text}</span>'
        f'<span class="badge hot">{bookings_text}</span>'
        f'<span class="badge">{filter_text}</span>'
        '</div></div>'
    )


def page_heading(title, subtitle):
    # Title and one line of context for each page
    return f'<div class="page-title">{title}</div><div class="page-sub">{subtitle}</div>'


def kpi_card(label, value, sub="", tone=""):
    # One number card, tone can be good, bad or warn
    return (
        f'<div class="kpi {tone}">'
        f'<div class="label">{label}</div>'
        f'<div class="value">{value}</div>'
        f'<div class="sub">{sub}</div>'
        '</div>'
    )


def card_header(title, takeaway=""):
    # Chart title with a one line takeaway
    take = f'<div class="ctake">{takeaway}</div>' if takeaway else ""
    return f'<div class="chead"><div class="ctitle">{title}</div>{take}</div>'


def note(text):
    # Information box
    return f'<div class="note">{text}</div>'


def priority_card(rank, action, impact, team):
    # Short card for the top priorities on the summary page
    return (
        '<div class="prio">'
        f'<div class="rank">PRIORITY {rank}</div>'
        f'<div class="what">{action}</div>'
        f'<div class="money">{impact}</div>'
        f'<div class="team">Owner: {team}</div>'
        '</div>'
    )


def data_bar(text, percent):
    # Number with a small bar next to it
    width = max(0, min(100, percent))
    return (
        f'<div class="bar"><span>{text}</span>'
        f'<div class="track"><div class="fill" style="width:{width:.0f}%"></div></div></div>'
    )


def html_table(headers, rows, numeric_from=1):
    # Clean table, columns from numeric_from onwards are aligned to the right
    head = "".join(
        f'<th class="{"num" if i >= numeric_from else ""}">{h}</th>' for i, h in enumerate(headers)
    )
    body = ""
    for row in rows:
        cells = "".join(
            f'<td class="{"num" if i >= numeric_from else ""}">{c}</td>' for i, c in enumerate(row)
        )
        body += f"<tr>{cells}</tr>"
    return f'<table class="dtable"><thead><tr>{head}</tr></thead><tbody>{body}</tbody></table>'


def action_table(items):
    # Prioritised action plan with owner, evidence and expected impact
    headers = ["Priority", "Owner", "Action", "Evidence from the data", "Expected impact"]
    rows = []
    for item in items:
        tag = f'<span class="tag {item["priority"].lower()}">{item["priority"].upper()}</span>'
        rows.append([tag, item["team"], item["action"], item["evidence"], item["impact"]])
    return html_table(headers, rows, numeric_from=99)


def fmt_money(value):
    # Short Indian style money text such as Rs 3.51 Cr
    if value >= 1e7:
        return f"Rs {value / 1e7:.2f} Cr"
    if value >= 1e5:
        return f"Rs {value / 1e5:.2f} L"
    return f"Rs {value:,.0f}"


def fmt_pct(value, digits=1):
    # Fraction to percent text
    return f"{value * 100:.{digits}f}%"
