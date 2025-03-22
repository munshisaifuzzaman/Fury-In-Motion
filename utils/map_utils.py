# Folium map construction, paths, markers

import folium
import json

# US States GeoJSON path
US_STATES_GEOJSON_FILE_PATH = "data/us-states.json"

# EF Rating Colors
EF_COLORS = {
    0: "#808080",  # EF0 - Gray
    1: "#2ca02c",  # EF1 - Green
    2: "#ff7f0e",  # EF2 - Orange
    3: "#d62728",  # EF3 - Red
    4: "#8c0000",  # EF4 - Dark Red
    5: "#000000",  # EF5 - Black
}

def get_intermediate_points(start_lat, start_lon, end_lat, end_lon, steps=4):
    """
    Generate evenly spaced intermediate points between start and end locations.
    """
    import numpy as np
    latitudes = np.linspace(start_lat, end_lat, steps)
    longitudes = np.linspace(start_lon, end_lon, steps)
    return [(round(lat, 2), round(lon, 2)) for lat, lon in zip(latitudes, longitudes)]

def add_state_borders(folium_map):
    """
    Overlay state boundaries and display state names on hover.
    """
    try:
        with open(US_STATES_GEOJSON_FILE_PATH, "r") as f:
            geojson_data = json.load(f)

        geojson_layer = folium.GeoJson(
            geojson_data,
            name="State Borders",
            style_function=lambda feature: {
                "fillOpacity": 0,
                "color": "gray",
                "weight": 1.5,
            },
            tooltip=folium.GeoJsonTooltip(
                fields=["name"],
                aliases=["State:"],
                sticky=False,
                opacity=0.9,
                direction="top"
            )
        )

        geojson_layer.add_to(folium_map)

    except Exception as e:
        print(f"[ERROR] Failed to load state borders: {e}")

def validate_coordinates(lat, lon):
    """
    Ensure coordinates are within valid bounds and not zero.
    """
    if (lat == 0.0 and lon == 0.0):
        print(f"[ERROR] Invalid coordinates detected: ({lat}, {lon})")
        return None
    if not (-90 <= lat <= 90 and -180 <= lon <= 180):
        print(f"[ERROR] Out-of-bounds coordinates detected: ({lat}, {lon})")
        return None
    return (lat, lon)
