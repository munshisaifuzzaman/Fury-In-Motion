# handles tornado path geometry and coordinate validation
import numpy as np

# checks whether the coordinates are valid
def validate_coordinates(lat, lon):
    if (lat == 0.0 and lon == 0.0) or not (-90 <= lat <= 90 and -180 <= lon <= 180):
        return None
    return (lat, lon)

# creates a line for the tornado based on start and end coordinates
def get_intermediate_points(start_lat, start_lon, end_lat, end_lon, steps=4):
    lats = np.linspace(start_lat, end_lat, steps)
    lons = np.linspace(start_lon, end_lon, steps)
    return list(zip(np.round(lats, 2), np.round(lons, 2)))