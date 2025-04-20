# Weather API + cache logic
import os
import json
import pandas as pd
import requests
from utils.constants import WEATHER_CACHE_FILE
from utils.coordinates import get_intermediate_points
from typing import Dict, Tuple

# Optional flag to disable live API fetches (safe for presentations)
DISABLE_API_FETCH = True

def load_cached_weather() -> Dict[str, Dict[str, Tuple]]:
    if os.path.exists(WEATHER_CACHE_FILE):
        with open(WEATHER_CACHE_FILE, "r") as f:
            return json.load(f)
    return {}

def save_cached_weather(cache: Dict[str, Dict[str, Tuple]]) -> None:
    os.makedirs(os.path.dirname(WEATHER_CACHE_FILE), exist_ok=True)
    with open(WEATHER_CACHE_FILE, "w") as f:
        json.dump(cache, f, indent=4)

def fetch_weather(lat: float, lon: float, date, cache: Dict[str, Dict[str, Dict]]) -> Dict:
    key = f"{lat:.2f},{lon:.2f}"
    date_str = pd.to_datetime(date).strftime("%Y-%m-%d")

    if date_str in cache and key in cache[date_str]:
        print(f"✅ Cache hit for {key} on {date_str}")
        cached = cache[date_str][key]
        if isinstance(cached, dict):
            return cached
    else:
        print(f"❌ Cache miss for {key} on {date_str}")

    if DISABLE_API_FETCH:
        print(f"⚠️ API fetch blocked in safe mode: {date_str} @ {key}")
        return {
            "temperature": None,
            "wind_speed": None,
            "precipitation": None,
            "dew_point": None,
            "humidity": None,
            "cloud_cover": None,
            "pressure": None,
            "cape": None,
            "soil_moisture": None
        }

    # Open-Meteo request
    url = (
        f"https://archive-api.open-meteo.com/v1/archive?"
        f"latitude={lat}&longitude={lon}&start_date={date_str}&end_date={date_str}"
        f"&daily=temperature_2m_max,wind_speed_10m_max,precipitation_sum,"
        f"dew_point_2m_mean,relative_humidity_2m_mean,cloud_cover_mean,"
        f"pressure_msl_mean,cape_max,soil_moisture_0_to_100cm_mean&timezone=auto"
    )

    try:
        r = requests.get(url)
        r.raise_for_status()
        daily = r.json().get("daily", {})

        result = {
            "temperature": daily.get("temperature_2m_max", [None])[0],
            "wind_speed": daily.get("wind_speed_10m_max", [None])[0],
            "precipitation": daily.get("precipitation_sum", [None])[0],
            "dew_point": daily.get("dew_point_2m_mean", [None])[0],
            "humidity": daily.get("relative_humidity_2m_mean", [None])[0],
            "cloud_cover": daily.get("cloud_cover_mean", [None])[0],
            "pressure": daily.get("pressure_msl_mean", [None])[0],
            "cape": daily.get("cape_max", [None])[0],
            "soil_moisture": daily.get("soil_moisture_0_to_100cm_mean", [None])[0]
        }

    except Exception as e:
        print(f"⚠️ Weather API error: {e}")
        result = {
            "temperature": None,
            "wind_speed": None,
            "precipitation": None,
            "dew_point": None,
            "humidity": None,
            "cloud_cover": None,
            "pressure": None,
            "cape": None,
            "soil_moisture": None
        }

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

    # ✅ Round lat/lon to 2 decimal places before fetching
    weather_data = [
        fetch_weather(round(lat, 2), round(lon, 2), row["date"], cache)
        for lat, lon in points
    ]

    return points, weather_data
