# Look and feel of the dashboard: CSS and small HTML helpers
from src.config import COLORS

CSS = f"""
<style>
@import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700;800&family=Space+Grotesk:wght@500;700&display=swap');

html, body, [class*="css"] {{ font-family: 'Inter', sans-serif; }}
.stApp {{
    background:
        radial-gradient(1100px 500px at 85% -10%, rgba(215,227,43,0.10), transparent 60%),
        radial-gradient(800px 400px at -10% 10%, rgba(45,212,191,0.07), transparent 60%),
        {COLORS["bg"]};
}}
#MainMenu, footer, header {{ visibility: hidden; }}
.block-container {{ padding-top: 1.4rem; padding-bottom: 3rem; max-width: 1280px; }}

/* Sidebar */
section[data-testid="stSidebar"] {{
    background: {COLORS["card"]};
    border-right: 1px solid {COLORS["border"]};
}}
section[data-testid="stSidebar"] * {{ color: {COLORS["text"]}; }}

/* Hero banner */
.hero {{
    position: relative; overflow: hidden;
    padding: 28px 32px; border-radius: 22px; margin-bottom: 18px;
    background: linear-gradient(120deg, #14181D 0%, #11151A 55%, #1A2108 100%);
    border: 1px solid {COLORS["border"]};
}}
.hero:after {{
    content: ""; position: absolute; right: -60px; top: -60px;
    width: 260px; height: 260px; border-radius: 50%;
    border: 26px solid rgba(215,227,43,0.16);
    box-shadow: inset 0 0 0 10px rgba(215,227,43,0.06);
}}
.hero .tag {{
    display: inline-block; font-size: 11px; letter-spacing: 2px; font-weight: 700;
    color: {COLORS["lime"]}; background: rgba(215,227,43,0.10);
    padding: 5px 12px; border-radius: 999px; margin-bottom: 12px;
}}
.hero h1 {{
    font-family: 'Space Grotesk', sans-serif; font-size: 38px; line-height: 1.1;
    margin: 0 0 8px 0; color: {COLORS["text"]}; font-weight: 700;
}}
.hero h1 span {{ color: {COLORS["lime"]}; }}
.hero p {{ color: {COLORS["muted"]}; margin: 0; max-width: 720px; font-size: 14.5px; line-height: 1.6; }}

/* KPI cards */
.kpi {{
    background: {COLORS["card"]}; border: 1px solid {COLORS["border"]};
    border-radius: 16px; padding: 16px 18px; height: 100%;
    transition: transform .15s ease, border-color .15s ease;
}}
.kpi:hover {{ transform: translateY(-3px); border-color: rgba(215,227,43,0.5); }}
.kpi .label {{ font-size: 11.5px; letter-spacing: .8px; text-transform: uppercase; color: {COLORS["muted"]}; font-weight: 600; }}
.kpi .value {{ font-family: 'Space Grotesk', sans-serif; font-size: 28px; font-weight: 700; color: {COLORS["text"]}; margin: 6px 0 2px 0; }}
.kpi .sub {{ font-size: 12px; color: {COLORS["muted"]}; }}
.kpi.good .value {{ color: {COLORS["lime"]}; }}
.kpi.bad .value {{ color: {COLORS["coral"]}; }}
.kpi.warn .value {{ color: {COLORS["amber"]}; }}

/* Section headings */
.section {{ margin: 26px 0 8px 0; display: flex; align-items: baseline; gap: 12px; }}
.section .num {{ font-family: 'Space Grotesk', sans-serif; color: {COLORS["lime"]}; font-weight: 700; font-size: 14px; }}
.section .title {{ font-size: 20px; font-weight: 700; color: {COLORS["text"]}; }}
.caption {{ color: {COLORS["muted"]}; font-size: 13px; margin: 0 0 10px 0; }}

/* Insight cards */
.insight {{
    background: {COLORS["card"]}; border: 1px solid {COLORS["border"]};
    border-left: 4px solid {COLORS["lime"]}; border-radius: 14px;
    padding: 16px 18px; margin-bottom: 12px;
}}
.insight.high {{ border-left-color: {COLORS["coral"]}; }}
.insight.medium {{ border-left-color: {COLORS["amber"]}; }}
.insight.low {{ border-left-color: {COLORS["teal"]}; }}
.insight .head {{ display: flex; justify-content: space-between; gap: 10px; align-items: center; }}
.insight .name {{ font-weight: 700; color: {COLORS["text"]}; font-size: 15px; }}
.insight .pill {{
    font-size: 10.5px; font-weight: 700; letter-spacing: 1px; padding: 3px 10px;
    border-radius: 999px; background: rgba(255,255,255,0.06); color: {COLORS["muted"]}; white-space: nowrap;
}}
.insight .body {{ color: #C3CAD4; font-size: 13.5px; line-height: 1.65; margin-top: 8px; }}
.insight .action {{ margin-top: 8px; font-size: 13px; color: {COLORS["lime"]}; }}

/* Callout note */
.note {{
    background: rgba(255,176,32,0.07); border: 1px solid rgba(255,176,32,0.35);
    color: #E9D3A3; padding: 12px 16px; border-radius: 12px; font-size: 13px; line-height: 1.6;
}}

/* Vehicle tiles */
.tile {{
    background: {COLORS["card"]}; border: 1px solid {COLORS["border"]};
    border-radius: 14px; padding: 14px 10px; text-align: center;
}}
.tile img {{ width: 44px; height: 44px; margin-bottom: 6px; filter: drop-shadow(0 0 8px rgba(215,227,43,0.25)); }}
.tile .vname {{ font-weight: 600; font-size: 13px; color: {COLORS["text"]}; }}
.tile .vsub {{ font-size: 11.5px; color: {COLORS["muted"]}; }}

/* Tabs */
.stTabs [data-baseweb="tab-list"] {{ gap: 6px; border-bottom: 1px solid {COLORS["border"]}; flex-wrap: wrap; }}
.stTabs [data-baseweb="tab"] {{
    background: transparent; border-radius: 10px 10px 0 0; padding: 10px 16px;
    color: {COLORS["muted"]}; font-weight: 600;
}}
.stTabs [aria-selected="true"] {{ color: {COLORS["lime"]} !important; background: rgba(215,227,43,0.08); }}
.stTabs [data-baseweb="tab-highlight"] {{ background-color: {COLORS["lime"]}; }}

/* Chart containers */
div[data-testid="stPlotlyChart"] {{
    background: {COLORS["card"]}; border: 1px solid {COLORS["border"]};
    border-radius: 16px; padding: 8px;
}}
</style>
"""


def hero(title_plain, title_accent, text, tag):
    # Top banner of the page
    return (
        '<div class="hero">'
        f'<div class="tag">{tag}</div>'
        f'<h1>{title_plain} <span>{title_accent}</span></h1>'
        f'<p>{text}</p>'
        '</div>'
    )


def kpi_card(label, value, sub="", tone=""):
    # One number card, tone can be good, bad or warn
    return (
        f'<div class="kpi {tone}">'
        f'<div class="label">{label}</div>'
        f'<div class="value">{value}</div>'
        f'<div class="sub">{sub}</div>'
        '</div>'
    )


def section(number, title, caption=""):
    # Numbered section heading with a short caption
    html = f'<div class="section"><span class="num">{number}</span><span class="title">{title}</span></div>'
    if caption:
        html += f'<div class="caption">{caption}</div>'
    return html


def insight_card(name, body, action="", priority="medium"):
    # Finding with a plain explanation and a recommended action
    action_html = f'<div class="action">Recommended action: {action}</div>' if action else ""
    return (
        f'<div class="insight {priority}">'
        f'<div class="head"><span class="name">{name}</span>'
        f'<span class="pill">{priority.upper()} PRIORITY</span></div>'
        f'<div class="body">{body}</div>{action_html}'
        '</div>'
    )


def note(text):
    # Warning or information box
    return f'<div class="note">{text}</div>'


def vehicle_tile(name, icon_url, sub):
    # Small card with the vehicle icon
    return (
        '<div class="tile">'
        f'<img src="{icon_url}"/>'
        f'<div class="vname">{name}</div>'
        f'<div class="vsub">{sub}</div>'
        '</div>'
    )


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
