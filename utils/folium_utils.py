import geopandas as gpd
from shapely.geometry import Point

from utils.constants import US_STATES_GEOJSON_FILE_PATH

# Load U.S. state shapes (one-time load)
states_gdf = gpd.read_file(US_STATES_GEOJSON_FILE_PATH)

def get_state_from_latlon(lat, lon):
    point = Point(lon, lat)  # Geo format: (lon, lat)
    for _, row in states_gdf.iterrows():
        if row["geometry"].contains(point):
            return row["name"]
    return "NA"


def build_tornado_dropdown(filtered_df):
    df = filtered_df.copy()
    df["state"] = df.apply(lambda row: get_state_from_latlon(row["slat"], row["slon"]), axis=1)
    df_sorted = df.sort_values("state")
    options = {
        idx: f"{row['state']} | {str(row['date'])[:10]} | EF{int(row['mag'])} | {round(row['len'], 1)} mi"
        for idx, row in df_sorted.iterrows()
    }
    return options, df