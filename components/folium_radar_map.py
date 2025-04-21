import folium
import streamlit as st
from folium.plugins import MarkerCluster

from components.map_utils import create_ef_layers
from utils.constants import MAP_STYLES, EF_COLORS, TORNADO_START_GIF_ICON, \
    TORNADO_END_GIF_ICON
from utils.coordinates import validate_coordinates
from utils.geojson import add_state_borders, add_ef_legend
from utils.weather import load_cached_weather, prepare_weather_data


def geo_radar_initial_text(st):
    with st.expander("🌍 Why Use a Geographic Radar Map? What Insights Does It Reveal?", expanded=False):
        st.markdown("""
        The **Geographic Radar Map** visually compares the paths and intensities of selected tornadoes side-by-side on a U.S. map. It overlays **start/end markers**, **path lines**, and **weather information** along the route for deeper spatial understanding.

        #### ✅ Why We Included This Map:
        - To explore how **tornado geography** influences severity and destruction.
        - To visualize **path orientation, distance, and location density**.
        - To correlate storm tracks with **terrain or atmospheric conditions** (like temperature and wind speed).

        #### 🌪 What This Visualization Reveals:
        - Tornadoes with **similar EF ratings** may occur in very different regions or follow unique directions.
        - **Longer tracks** can intersect populated areas, increasing risk — even with moderate EF levels.
        - Observing **start and end markers** with weather data reveals localized atmospheric shifts.

        #### 🧪 How This Leads to Scientific Questions:
        - Do tornadoes in certain **geographic regions** tend to be longer or deadlier?
        - Can we identify **atmospheric precursors** along the tornado path?
        - How does **location or directionality** affect EF severity?

        This map enables spatial analysis of tornado patterns, setting the stage for region-specific and meteorological investigations.
        """)

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
        start_weather = weather_data[0] if weather_data and isinstance(weather_data[0], dict) else {}
        end_weather = weather_data[-1] if weather_data and isinstance(weather_data[-1], dict) else {}

        # Start marker
        folium.Marker(
            location=start,
            icon=folium.CustomIcon(TORNADO_START_GIF_ICON, icon_size=(55, 55)),
            popup=folium.Popup(
                f"""<b>Tornado Start</b><br><b>Date:</b> {row['date']}<br>
                    <b>Temp:</b> {start_weather.get('temperature', 'N/A')}°C<br>
                    <b>Wind:</b> {start_weather.get('wind_speed', 'N/A')} m/s<br>
                    <b>Humidity:</b> {start_weather.get('humidity', 'N/A')}%<br>
                    <b>Pressure:</b> {start_weather.get('pressure', 'N/A')} hPa<br>
                    <b>CAPE:</b> {start_weather.get('cape', 'N/A')}""",
                max_width=300)
        ).add_to(marker_cluster)

        # End marker
        folium.Marker(
            location=end,
            icon=folium.CustomIcon(TORNADO_END_GIF_ICON, icon_size=(55, 55)),
            popup=folium.Popup(
                f"""<b>Tornado End</b><br><b>Date:</b> {row['date']}<br><b>Length:</b> {row['len']} miles<br>
                    <b>Temp:</b> {end_weather.get('temperature', 'N/A')}°C<br>
                    <b>Wind:</b> {end_weather.get('wind_speed', 'N/A')} m/s<br>
                    <b>Humidity:</b> {end_weather.get('humidity', 'N/A')}%<br>
                    <b>Pressure:</b> {end_weather.get('pressure', 'N/A')} hPa<br>
                    <b>CAPE:</b> {end_weather.get('cape', 'N/A')}""",
                max_width=300)
        ).add_to(marker_cluster)

        # Intermediate weather
        for idx, (lat, lon) in enumerate(points[1:-1]):
            weather = weather_data[idx + 1] if weather_data and len(weather_data) > idx + 1 else {}
            folium.CircleMarker(
                location=(lat, lon),
                radius=5,
                color=color,
                fill=True,
                fill_color=color,
                popup=folium.Popup(
                    f"""<b>Path Weather</b><br>
                                    <b>Temp:</b> {weather.get("temperature", 'N/A')}°C<br>
                                    <b>Wind:</b> {weather.get("wind_speed", 'N/A')} m/s""",
                                    max_width=300)
            ).add_to(ef_layer)

        # Tornado path line
        folium.PolyLine(
            locations=[start, end],
            color=color,
            weight=2 + row["mag"] * 2,
            tooltip=folium.Tooltip(
                    f"<b>Date:</b> {row['date']}<br><b>Length:</b> {row['len']} miles<br>"
                    f"<b>EF Rating:</b> EF{int(row['mag'])}<br><b>Fatalities:</b> {row['fat']}<br><b>Injuries:</b> {row['inj']}",
                    sticky=True)
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
