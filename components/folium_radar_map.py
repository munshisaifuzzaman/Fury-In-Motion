import folium
import streamlit as st

from components.map_utils import create_ef_layers
from utils.constants import MAP_STYLES, EF_COLORS, TORNADO_START_ICON, TORNADO_END_ICON
from utils.coordinates import validate_coordinates, get_intermediate_points
from utils.geojson import add_state_borders, add_ef_legend
from utils.weather import load_cached_weather, fetch_weather, prepare_weather_data
from folium.plugins import MarkerCluster

def render_geographic_radar_map(selected_df):
    if selected_df.empty or len(selected_df) < 2:
        st.info("Please select at least two tornadoes to render the radar comparison map.")
        return

    st.markdown("### 🌍 Geographic Tornado Radar Map")

    radar_map = folium.Map(location=[38, -97], zoom_start=5, tiles=MAP_STYLES["OpenStreetMap"]["tiles"],
                           attr=MAP_STYLES["OpenStreetMap"]["attr"])

    add_state_borders(radar_map)
    ef_layers = create_ef_layers()
    cache = load_cached_weather()
    marker_cluster = MarkerCluster(name="Radar Tornado Markers")

    for _, row in selected_df.iterrows():
        start = validate_coordinates(row["slat"], row["slon"])
        end = validate_coordinates(row["elat"], row["elon"])
        if not start or not end:
            continue

        color = EF_COLORS.get(int(row["mag"]), "#000000")
        ef_layer = ef_layers.get(f"EF{int(row['mag'])}", folium.FeatureGroup())

        # Fetch weather data
        points, weather_data = prepare_weather_data(row, cache, include_path=True)

        # Start marker
        folium.Marker(
            location=start,
            icon=folium.CustomIcon(TORNADO_START_ICON, icon_size=(40, 40)),
            popup=folium.Popup(
                f"<b>Start:</b> {row['date']}<br>Temp: {weather_data[0][0]}°C<br>Wind: {weather_data[0][1]} m/s",
                max_width=300)
        ).add_to(marker_cluster)

        # End marker
        folium.Marker(
            location=end,
            icon=folium.CustomIcon(TORNADO_END_ICON, icon_size=(40, 40)),
            popup=folium.Popup(
                f"<b>End:</b> {row['date']}<br>Length: {row['len']} mi<br>Temp: {weather_data[-1][0]}°C<br>Wind: {weather_data[-1][1]} m/s",
                max_width=300)
        ).add_to(marker_cluster)

        # Intermediate weather
        for idx, (lat, lon) in enumerate(points[1:-1]):
            folium.CircleMarker(
                location=(lat, lon),
                radius=5,
                color=color,
                fill=True,
                fill_color=color,
                popup=folium.Popup(
                    f"<b>Path Weather</b><br>Temp: {weather_data[idx + 1][0]}°C<br>Wind: {weather_data[idx + 1][1]} m/s",
                    max_width=300)
            ).add_to(ef_layer)

        # Tornado path line
        folium.PolyLine(
            locations=[start, end],
            color=color,
            weight=2 + row["mag"] * 2,
            tooltip=f"EF{int(row['mag'])}, Length: {row['len']} mi"
        ).add_to(ef_layer)

    marker_cluster.add_to(radar_map)
    for layer in ef_layers.values():
        layer.add_to(radar_map)

    folium.LayerControl(collapsed=True).add_to(radar_map)
    add_ef_legend(radar_map)

    col1, col2, col3 = st.columns([0.05, 0.9, 0.05])
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
                <iframe srcdoc='{radar_map.get_root().render().replace("'", "&apos;")}'
                        width="100%" height="600" style="border: none;"></iframe>
            </div>
        """, height=650)
