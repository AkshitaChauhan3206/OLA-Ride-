# Central settings for the Ola Ride Insights project
from pathlib import Path

# Folder locations
ROOT_DIR = Path(__file__).resolve().parent.parent
DATA_DIR = ROOT_DIR / "data"
CLEAN_FILE = DATA_DIR / "ola_cleaned.csv"
SQL_FILE = ROOT_DIR / "sql" / "ola_queries.sql"

# Raw Excel file and sheet name used by the cleaning script
RAW_FILE_NAME = "OLA_DataSet.xlsx"
RAW_SHEET_NAME = "July"

# Project links, fill these after publishing the repository and the app
GITHUB_URL = "https://github.com/YOUR_USERNAME/ola-ride-insights"
STREAMLIT_URL = "https://YOUR_APP_NAME.streamlit.app"
POWERBI_EMBED_URL = ""

# Fixed display order so every chart shows vehicles in the same order
VEHICLE_ORDER = ["Auto", "Bike", "eBike", "Mini", "Prime Sedan", "Prime Plus", "Prime SUV"]
STATUS_ORDER = ["Success", "Canceled by Customer", "Canceled by Driver", "Driver Not Found"]
PAYMENT_ORDER = ["Cash", "UPI", "Credit Card", "Debit Card"]
DAY_ORDER = ["Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday", "Sunday"]
SLOT_ORDER = ["Late Night", "Morning", "Afternoon", "Evening", "Night"]

# Vehicle icons taken from the second sheet of the Excel file
VEHICLE_ICONS = {
    "Prime Sedan": "https://cdn-icons-png.flaticon.com/128/14183/14183770.png",
    "Bike": "https://cdn-icons-png.flaticon.com/128/9983/9983173.png",
    "Prime SUV": "https://cdn-icons-png.flaticon.com/128/9983/9983204.png",
    "eBike": "https://cdn-icons-png.flaticon.com/128/6839/6839867.png",
    "Mini": "https://cdn-icons-png.flaticon.com/128/3202/3202926.png",
    "Prime Plus": "https://cdn-icons-png.flaticon.com/128/11409/11409716.png",
    "Auto": "https://cdn-icons-png.flaticon.com/128/16526/16526595.png",
}

# Colour palette used by the dashboard and the charts
COLORS = {
    "bg": "#0B0D10",
    "card": "#14181D",
    "border": "#232A32",
    "text": "#EDEFF2",
    "muted": "#8D96A3",
    "lime": "#D7E32B",
    "teal": "#2DD4BF",
    "coral": "#FF6B6B",
    "amber": "#FFB020",
    "violet": "#8B7CF6",
    "blue": "#4EA8FF",
}

# Colour for each booking status
STATUS_COLORS = {
    "Success": COLORS["lime"],
    "Canceled by Customer": COLORS["amber"],
    "Canceled by Driver": COLORS["coral"],
    "Driver Not Found": COLORS["violet"],
}

# Colour sequence for categories
SEQUENCE = [
    COLORS["lime"], COLORS["teal"], COLORS["blue"], COLORS["violet"],
    COLORS["amber"], COLORS["coral"], "#B8C0CC",
]
