import os
import json
import pandas as pd
import numpy as np
import requests
from tqdm import tqdm
import time

# === Constants ===
DATA_PATH = "../data/1950-2023_actual_tornadoes.csv"
CACHE_PATH = "../cache/weather_cache.json"

# === Load tornado dataset ===
df = pd.read_csv(DATA_PATH)
df["date"] = pd.to_datetime(df["date"], errors="coerce")
df = df[(df["slat"] != 0.0) & (df["slon"] != 0.0)]

# === Top 150 per metric ===
top_len = df.sort_values("len", ascending=False).head(150)
top_wid = df.sort_values("wid", ascending=False).head(150)
top_fat = df.sort_values("fat", ascending=False).head(150)
top_inj = df.sort_values("inj", ascending=False).head(150)

combined = pd.concat([top_len, top_wid, top_fat, top_inj]).drop_duplicates()

# === Load existing cache ===
if os.path.exists(CACHE_PATH):
    with open(CACHE_PATH, "r") as f:
        weather_cache = json.load(f)
else:
    weather_cache = {}

# === Intermediate point generator ===
def get_intermediate_points(start_lat, start_lon, end_lat, end_lon, steps=4):
    lats = np.linspace(start_lat, end_lat, steps)
    lons = np.linspace(start_lon, end_lon, steps)
    return list(zip(np.round(lats, 2), np.round(lons, 2)))

# === Weather fetch ===
def fetch_weather(lat, lon, date_str):
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
        return result
    except:
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

# === Prefetch loop ===
print(f"Processing {len(combined)} tornadoes with intermediate points...")
for _, row in tqdm(combined.iterrows(), total=len(combined)):
    date_str = pd.to_datetime(row["date"]).strftime("%Y-%m-%d")

    points = [(row["slat"], row["slon"])] + \
             get_intermediate_points(row["slat"], row["slon"], row["elat"], row["elon"], steps=4) + \
             [(row["elat"], row["elon"])]

    for lat, lon in points:
        key = f"{lat:.2f},{lon:.2f}"
        if date_str in weather_cache and key in weather_cache[date_str]:
            continue  # already fetched
        result = fetch_weather(lat, lon, date_str)
        weather_cache.setdefault(date_str, {})[key] = result

        time.sleep(0.2)  # add short delay to reduce API pressure

# === Save cache ===
os.makedirs(os.path.dirname(CACHE_PATH), exist_ok=True)
with open(CACHE_PATH, "w") as f:
    json.dump(weather_cache, f, indent=4)

print("✅ Weather cache updated with path points.")