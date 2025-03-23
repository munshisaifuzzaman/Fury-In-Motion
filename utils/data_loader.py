# NOAA CSV loading + validation
import pandas as pd
import streamlit as st

TORNADO_CSV_URL = "./data/1950-2023_actual_tornadoes.csv"

@st.cache_data
def load_tornado_data():
    df = pd.read_csv(TORNADO_CSV_URL)
    df["date"] = pd.to_datetime(df["date"], errors="coerce")
    df = df[
        (df["slat"] != 0.0) & (df["slon"] != 0.0) &
        (df["elat"].between(-90, 90)) & (df["elon"].between(-180, 180))
    ]
    return df[['date', 'yr', 'slat', 'slon', 'elat', 'elon', 'len', 'mag', 'wid', 'fat', 'inj']]