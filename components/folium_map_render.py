import folium
import streamlit as st

from components.map_utils import create_ef_layers
from utils.constants import MAP_STYLES, COLUMN_MAPPING, EF_COLORS, TORNADO_START_ICON, TORNADO_END_ICON
from utils.coordinates import validate_coordinates, get_intermediate_points
from utils.geojson import add_state_borders, add_ef_legend
from utils.weather import load_cached_weather, fetch_weather


def folium_render_map(data, column, top_n, value_range, map_style):
    col_key, _ = COLUMN_MAPPING[column]
    min_val, max_val = value_range

    filtered = data[(data[col_key] >= min_val) & (data[col_key] <= max_val)]
    filtered = filtered.sort_values(col_key, ascending=False).head(top_n)

    if filtered.empty:
        st.error("No data matches your filters.")
        return

    map_cfg = MAP_STYLES[map_style]
    folium_map = folium.Map(location=[38, -97], tiles=map_cfg["tiles"], attr=map_cfg["attr"], zoom_start=5)
    add_state_borders(folium_map)

    ef_layers = create_ef_layers()
    cache = load_cached_weather()


    for _, row in filtered.iterrows():
        start = validate_coordinates(row["slat"], row["slon"])
        end = validate_coordinates(row["elat"], row["elon"])
        if not start or not end:
            continue

        color = EF_COLORS.get(int(row["mag"]), "#000000")
        ef_layer = ef_layers.get(f"EF{int(row['mag'])}", folium.FeatureGroup())

        points = [start] + get_intermediate_points(*start, *end) + [end]
        weather_data = [fetch_weather(lat, lon, row["date"], cache) for lat, lon in points]

        # Start/End Markers
        folium.Marker(
            location=start,
            icon=folium.CustomIcon(TORNADO_START_ICON, icon_size=(40, 40)),
            popup=f"Start: {weather_data[0]}"
        ).add_to(ef_layer)

        folium.Marker(
            location=end,
            icon=folium.CustomIcon(TORNADO_END_ICON, icon_size=(40, 40)),
            popup=f"End: {weather_data[-1]}"
        ).add_to(ef_layer)

        # Mid Weather Points
        for idx, (lat, lon) in enumerate(points[1:-1]):
            folium.CircleMarker(
                location=(lat, lon),
                radius=4,
                color=color,
                fill=True,
                fill_color=color,
                popup=f"Weather: {weather_data[idx+1]}"
            ).add_to(ef_layer)

        folium.PolyLine(
            locations=[start, end],
            color=color,
            weight=2 + row["mag"] * 2,
            tooltip=f"EF{int(row['mag'])}, Length: {row['len']} miles"
        ).add_to(ef_layer)

    for layer in ef_layers.values():
        layer.add_to(folium_map)

    folium.LayerControl(collapsed=True).add_to(folium_map)
    add_ef_legend(folium_map)
    # Responsive layout
    col1, col2, col3 = st.columns([0.05, 0.9, 0.05])  # side padding
    with col2:
        st.components.v1.html(f"""
            <div style="
                border: 3px solid #444;
                border-radius: 12px;
                box-shadow: 0 4px 12px rgba(0, 0, 0, 0.3);
                padding: 10px;
                background-color: white;
                margin-bottom: 30px;
            ">
                <iframe srcdoc='{folium_map.get_root().render().replace("'", "&apos;")}'
                        width="100%" height="600" style="border: none;"></iframe>
            </div>
        """, height=650)