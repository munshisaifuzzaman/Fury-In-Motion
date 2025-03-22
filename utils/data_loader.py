# NOAA CSV loading + validation

import pandas as pd

def load_tornado_data():
    """
    Load and preprocess tornado events from the NOAA dataset.
    Removes entries with invalid start or end coordinates.
    """
    url = 'https://www.spc.noaa.gov/wcm/data/1950-2023_actual_tornadoes.csv'
    df = pd.read_csv(url)

    df['date'] = pd.to_datetime(df['date'], errors='coerce')
    df = df[
        (df["slat"] != 0.0) & (df["slon"] != 0.0) &
        (df["elat"].between(-90, 90)) & (df["elon"].between(-180, 180))
    ]

    return df[['date', 'yr', 'slat', 'slon', 'elat', 'elon', 'len', 'mag', 'wid', 'fat', 'inj']]

def validate_original_data(df):
    """
    Print warnings for invalid tornado coordinates in the dataset.
    """
    invalid = df[
        ((df["slat"] == 0.0) & (df["slon"] == 0.0)) |
        ((df["elat"] == 0.0) & (df["elon"] == 0.0))
    ]
    if invalid.empty:
        print("[INFO] No invalid entries found in the original dataset.")
    else:
        print("[WARNING] Found invalid tornado entries in original dataset:")
        print(invalid)
