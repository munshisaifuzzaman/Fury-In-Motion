import folium
import streamlit as st

from components.map_utils import create_ef_layers
from utils.constants import MAP_STYLES, COLUMN_MAPPING, EF_COLORS, TORNADO_START_ICON, TORNADO_END_ICON
from utils.coordinates import validate_coordinates, get_intermediate_points
from utils.geojson import add_state_borders, add_ef_legend
from utils.weather import load_cached_weather, fetch_weather, prepare_weather_data
from folium.plugins import MarkerCluster


def folium_render_map(data, column, top_n, value_range, map_style):
    # global points
    col_key, _ = COLUMN_MAPPING[column]
    min_val, max_val = value_range

    filtered = data[(data[col_key] >= min_val) & (data[col_key] <= max_val)]
    filtered = filtered.sort_values(col_key, ascending=False).head(top_n)

    # Only show paths and weather markers for small numbers of tornadoes
    SHOW_PATHS = st.sidebar.checkbox("Show Tornado Paths", value=(top_n <= 10))

    if filtered.empty:
        st.error("No data matches your filters.")
        return

    map_cfg = MAP_STYLES[map_style]
    folium_map = folium.Map(location=[38, -97], tiles=map_cfg["tiles"], attr=map_cfg["attr"], zoom_start=5)
    add_state_borders(folium_map)

    ef_layers = create_ef_layers()
    cache = load_cached_weather()
    marker_cluster = MarkerCluster(name="Tornado Markers")


    for _, row in filtered.iterrows():
        start = validate_coordinates(row["slat"], row["slon"])
        end = validate_coordinates(row["elat"], row["elon"])
        if not start or not end:
            continue

        color = EF_COLORS.get(int(row["mag"]), "#000000")
        ef_layer = ef_layers.get(f"EF{int(row['mag'])}", folium.FeatureGroup())

        points, weather_data = prepare_weather_data(row, cache, include_path=SHOW_PATHS)

        # Start Marker (with full weather popup)
        folium.Marker(
            location=start,
            icon=folium.CustomIcon(TORNADO_START_ICON, icon_size=(40, 40)),
            popup=folium.Popup(
                f"<b>Tornado Start</b><br><b>Date:</b> {row['date']}<br>"
                f"<b>Temp:</b> {weather_data[0][0]}°C<br><b>Wind:</b> {weather_data[0][1]} m/s",
                max_width=300)
        ).add_to(marker_cluster)

        # End Marker (with full weather + length popup)
        folium.Marker(
            location=end,
            icon=folium.CustomIcon(TORNADO_END_ICON, icon_size=(40, 40)),
            popup=folium.Popup(
                f"<b>Tornado End</b><br><b>Date:</b> {row['date']}<br><b>Length:</b> {row['len']} miles<br>"
                f"<b>Temp:</b> {weather_data[-1][0]}°C<br><b>Wind:</b> {weather_data[-1][1]} m/s",
                max_width=300)
        ).add_to(marker_cluster)

        # Mid Weather Points
        # If allowed, add path and weather markers
        # If paths are enabled, show intermediate weather & path
        if SHOW_PATHS:
            for idx, (lat, lon) in enumerate(points[1:-1]):
                folium.CircleMarker(
                    location=(lat, lon),
                    radius=5,
                    color=color,
                    fill=True,
                    fill_color=color,
                    popup=folium.Popup(
                        f"<b>Path Weather</b><br><b>Temp:</b> {weather_data[idx + 1][0]}°C<br><b>Wind:</b> {weather_data[idx + 1][1]} m/s",
                        max_width=300)
                ).add_to(ef_layer)

            folium.PolyLine(
                locations=[start, end],
                color=color,
                weight=2 + row["mag"] * 2,
                tooltip=folium.Tooltip(
                    f"<b>Date:</b> {row['date']}<br><b>Length:</b> {row['len']} miles<br>"
                    f"<b>EF Rating:</b> EF{int(row['mag'])}<br><b>Fatalities:</b> {row['fat']}<br><b>Injuries:</b> {row['inj']}",
                    sticky=True)
            ).add_to(ef_layer)
        # for idx, (lat, lon) in enumerate(points[1:-1]):
        #     folium.CircleMarker(
        #         location=(lat, lon),
        #         radius=4,
        #         color=color,
        #         fill=True,
        #         fill_color=color,
        #         popup=f"Weather: {weather_data[idx+1]}"
        #     ).add_to(ef_layer)
        #
        # folium.PolyLine(
        #     locations=[start, end],
        #     color=color,
        #     weight=2 + row["mag"] * 2,
        #     tooltip=f"EF{int(row['mag'])}, Length: {row['len']} miles"
        # ).add_to(ef_layer)

    # Add markers and layers to map
    marker_cluster.add_to(folium_map)
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