# Weather API + cache logic
import os
import json
import pandas as pd
import requests
from utils.constants import WEATHER_CACHE_FILE
from utils.coordinates import get_intermediate_points


def load_cached_weather():
    if os.path.exists(WEATHER_CACHE_FILE):
        with open(WEATHER_CACHE_FILE, "r") as f:
            return json.load(f)
    return {}

def save_cached_weather(cache):
    os.makedirs(os.path.dirname(WEATHER_CACHE_FILE), exist_ok=True)
    with open(WEATHER_CACHE_FILE, "w") as f:
        json.dump(cache, f, indent=4)

def fetch_weather(lat, lon, date, cache):
    key = f"{lat:.2f},{lon:.2f}"
    date_str = pd.to_datetime(date).strftime("%Y-%m-%d")

    if date_str in cache and key in cache[date_str]:
        return cache[date_str][key]

    url = (
        f"https://archive-api.open-meteo.com/v1/archive?"
        f"latitude={lat}&longitude={lon}&start_date={date_str}&end_date={date_str}"
        f"&daily=temperature_2m_max,wind_speed_10m_max,precipitation_sum&timezone=auto"
    )
    r = requests.get(url)
    if r.status_code != 200:
        return "N/A", "N/A", "N/A"

    try:
        data = r.json()["daily"]
        result = (
            data["temperature_2m_max"][0],
            data["wind_speed_10m_max"][0],
            data["precipitation_sum"][0]
        )
    except:
        result = ("N/A", "N/A", "N/A")

    cache.setdefault(date_str, {})[key] = result
    save_cached_weather(cache)
    return result

def prepare_weather_data(row, cache, include_path=True):
    if include_path:
        points = [(row["slat"], row["slon"])] + get_intermediate_points(
            row["slat"], row["slon"], row["elat"], row["elon"], steps=4
        ) + [(row["elat"], row["elon"])]
    else:
        points = [(row["slat"], row["slon"]), (row["elat"], row["elon"])]

    weather_data = [fetch_weather(lat, lon, row["date"], cache) for lat, lon in points]
    return points, weather_data