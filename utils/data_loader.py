# NOAA CSV loading + validation
import pandas as pd
import streamlit as st
import os

TORNADO_CSV_URL = "./data/1950-2023_actual_tornadoes.csv"
WEATHER_STATION_TEST_URL = "./data/weather_stations/USC00137844-iowa-spencer.csv"
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


@st.cache_data
def load_station_data():
    stations = list()
    for filename in os.listdir(WEATHER_STATION_DATA_URL):
        stations.append(pd.read_csv(WEATHER_STATION_DATA_URL + filename))
    print(stations)
    print("loaded")
    # dates are stored per month. ie one row per month.
    # ignoring the positional verifications for now. what could go wrong!
    print(stations[0]) # remove later
    print("  ")
    print(stations[0]["LATITUDE"][1]) # this is how you access a single entry 
    print(stations[0].iloc[0]) # this is how you'd access a single row
    print(type(stations[0]["LATITUDE"]))
    return stations # pretty sure i can ignore whatever the other return statement is doing ?