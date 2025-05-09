# API_KEY, EF_COLORS, MAP_STYLES, icon paths

# === Constants ===
API_KEY = "90927d45c68b47cc8592033a1c84ec33"

US_STATES_GEOJSON_FILE_PATH = "./data/us-states.json"
WEATHER_CACHE_FILE = "./cache/weather_cache.json"
TORNADO_CSV_URL = "./data/1950-2023_actual_tornadoes.csv"
WEATHER_STATION_DATA_URL = "./data/weather_stations/"

MAP_STYLES = {
    "OpenStreetMap": {"tiles": "OpenStreetMap", "attr": ""},
    "CartoDB Positron": {"tiles": "cartodbpositron", "attr": ""},
    "Esri WorldImagery": {
        "tiles": "https://server.arcgisonline.com/ArcGIS/rest/services/World_Imagery/MapServer/tile/{z}/{y}/{x}",
        "attr": "Tiles © Esri"
    },
    "Thunderforest Transport": {
        "tiles": f"https://tile.thunderforest.com/transport/{{z}}/{{x}}/{{y}}.png?apikey={API_KEY}",
        "attr": "Tiles © Thunderforest"
    },
}

EF_COLORS = {
    0: "#808080", 1: "#2ca02c", 2: "#ff7f0e",
    3: "#d62728", 4: "#8c0000", 5: "#000000"
}

TORNADO_START_GIF_ICON = "./assets/gif_icon_4.gif"
TORNADO_END_GIF_ICON = "./assets/gif_icon_5.gif"
TORNADO_START_PNG_ICON = "./assets/tornado_start.png"
TORNADO_END_PNG_ICON = "./assets/tornado_end.png"

THERMOMETER_ICON = "./assets/thermometer.png"

COLUMN_MAPPING = {
    "Length": ("len", "Tornado Length"),
    "Fatalities": ("fat", "Fatalities"),
    "Injuries": ("inj", "Injuries"),
    "Width": ("wid", "Tornado Width")
}