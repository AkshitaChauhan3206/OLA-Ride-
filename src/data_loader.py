# Loads the cleaned data and prepares it for analysis
import pandas as pd

from src.config import CLEAN_FILE
from src.features import add_features


def load_clean(path=CLEAN_FILE):
    # Read the cleaned file and turn the timestamp text into real dates
    df = pd.read_csv(path, parse_dates=["Booking_Datetime"])
    return df


def load_data(path=CLEAN_FILE):
    # Full pipeline used by the app, the notebook and the report
    return add_features(load_clean(path))
