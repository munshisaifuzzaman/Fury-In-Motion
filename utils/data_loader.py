# NOAA CSV loading + validation
import pandas as pd
import streamlit as st
import os

TORNADO_CSV_URL = "./data/1950-2023_actual_tornadoes.csv"
WEATHER_STATION_DATA_URL = "./data/weather_stations/"

@st.cache_data
def load_tornado_data():
    df = pd.read_csv(TORNADO_CSV_URL)
    df["date"] = pd.to_datetime(df["date"], errors="coerce")
    df = df[
        (df["slat"] != 0.0) & (df["slon"] != 0.0) &
        (df["elat"].between(-90, 90)) & (df["elon"].between(-180, 180))
    ]
    return df[['date', 'yr', 'slat', 'slon', 'elat', 'elon', 'len', 'mag', 'wid', 'fat', 'inj']]


# some of this data is getting processed as NaN, this could be an issue. investigate later
@st.cache_data
def load_station_data():
    stations = list()
    for filename in os.listdir(WEATHER_STATION_DATA_URL):
        stations.append(pd.read_csv(WEATHER_STATION_DATA_URL + filename))

    return stations




def load_prefetch_457_df():
    df = pd.read_csv(TORNADO_CSV_URL)
    df["date"] = pd.to_datetime(df["date"], errors="coerce")
    df = df[(df["slat"] != 0.0) & (df["slon"] != 0.0)]

    top_len = df.sort_values("len", ascending=False).head(150)
    top_wid = df.sort_values("wid", ascending=False).head(150)
    top_fat = df.sort_values("fat", ascending=False).head(150)
    top_inj = df.sort_values("inj", ascending=False).head(150)

    combined = pd.concat([top_len, top_wid, top_fat, top_inj]).drop_duplicates()
    return combined.reset_index(drop=True)