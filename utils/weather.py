# Weather API + cache logic

import json
import os
import requests
import pandas as pd

WEATHER_CACHE_FILE = "weather_cache.json"

# Load cache
if os.path.exists(WEATHER_CACHE_FILE):
    with open(WEATHER_CACHE_FILE, "r") as f:
        cached_weather = json.load(f)
else:
    cached_weather = {}

def fetch_weather(latitude, longitude, event_date):
    """
    Retrieve historical weather data for a given location and date from Open-Meteo.
    Uses a local cache to avoid repeated API calls.
    """
    event_date = pd.to_datetime(event_date).strftime("%Y-%m-%d")
    cache_key = f"{latitude},{longitude}"

    if event_date in cached_weather and cache_key in cached_weather[event_date]:
        return cached_weather[event_date][cache_key]

    api_url = (
        f"https://archive-api.open-meteo.com/v1/archive?latitude={latitude}&longitude={longitude}"
        f"&start_date={event_date}&end_date={event_date}"
        "&daily=temperature_2m_max,wind_speed_10m_max,precipitation_sum&timezone=auto"
    )

    response = requests.get(api_url)
    if response.status_code != 200:
        return "N/A", "N/A", "N/A"

    try:
        data = response.json()["daily"]
        temp = data["temperature_2m_max"][0]
        wind = data["wind_speed_10m_max"][0]
        precipitation = data["precipitation_sum"][0]
    except (KeyError, IndexError):
        return "N/A", "N/A", "N/A"

    # Store in cache
    cached_weather.setdefault(event_date, {})[cache_key] = (temp, wind, precipitation)

    with open(WEATHER_CACHE_FILE, "w") as f:
        json.dump(cached_weather, f, indent=4)

    return temp, wind, precipitation
