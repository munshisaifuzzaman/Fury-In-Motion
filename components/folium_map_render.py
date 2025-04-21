import folium
import streamlit as st
from folium.plugins import MarkerCluster

from components.map_utils import create_ef_layers
from utils.constants import MAP_STYLES, COLUMN_MAPPING, EF_COLORS, \
    TORNADO_START_PNG_ICON, TORNADO_START_GIF_ICON, TORNADO_END_PNG_ICON, TORNADO_END_GIF_ICON
from utils.coordinates import validate_coordinates
from utils.folium_utils import build_tornado_dropdown
from utils.geojson import add_state_borders, add_ef_legend
from utils.weather import load_cached_weather, prepare_weather_data


def folium_render_map(data, column, top_n, value_range, map_style):
    TORNADO_START_ICON = TORNADO_START_PNG_ICON if top_n >= 50 else TORNADO_START_GIF_ICON
    TORNADO_END_ICON = TORNADO_END_PNG_ICON if top_n >= 50 else TORNADO_END_GIF_ICON
    icon_size = (40, 40) if top_n >= 50 else (55, 55)


    st.markdown(f"### 🌪️ Top {top_n} Tornado Visualization based on {column}")
    st.markdown("---")  # Horizontal line separator

    col_key, _ = COLUMN_MAPPING[column]
    min_val, max_val = value_range

    filtered = data[(data[col_key] >= min_val) & (data[col_key] <= max_val)]
    filtered = filtered.sort_values(col_key, ascending=False).head(top_n)
    tornado_options, filtered = build_tornado_dropdown(filtered)

    selected_tornado_idx = st.sidebar.selectbox(
        "🔍 Highlight a Tornado",
        options=[None] + list(tornado_options.keys()),
        format_func=lambda k: "State | Year | Mag | Len" if k is None else tornado_options[k],
        index=0
    )

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

    for row_idx, row in filtered.iterrows():
        start = validate_coordinates(row["slat"], row["slon"])
        end = validate_coordinates(row["elat"], row["elon"])
        if not start or not end:
            continue

        color = EF_COLORS.get(int(row["mag"]), "#000000")
        ef_layer = ef_layers.get(f"EF{int(row['mag'])}", folium.FeatureGroup())

        points, weather_data = prepare_weather_data(row, cache, include_path=SHOW_PATHS)

        # Updated to return {} instead of (None,) * 9 when missing
        start_weather = weather_data[0] if weather_data and isinstance(weather_data[0], dict) else {}
        end_weather = weather_data[-1] if weather_data and isinstance(weather_data[-1], dict) else {}

        is_selected = (selected_tornado_idx is not None and row_idx == selected_tornado_idx)

        if is_selected:
            folium.CircleMarker(
                location=start,
                radius=18,
                color="blue",
                fill=False,
                weight=3,
                opacity=0.8
            ).add_to(ef_layer)

        # ✅ Start Marker using dict keys
        folium.Marker(
            location=start,
            icon=folium.CustomIcon(TORNADO_START_ICON, icon_size=icon_size),
            popup=folium.Popup(
                f"""<b>Tornado Start</b><br><b>Date:</b> {row['date']}<br>
                    <b>Temp:</b> {start_weather.get('temperature', 'N/A')}°C<br>
                    <b>Wind:</b> {start_weather.get('wind_speed', 'N/A')} m/s<br>
                    <b>Humidity:</b> {start_weather.get('humidity', 'N/A')}%<br>
                    <b>Pressure:</b> {start_weather.get('pressure', 'N/A')} hPa<br>
                    <b>CAPE:</b> {start_weather.get('cape', 'N/A')}""",
                max_width=300)
        ).add_to(marker_cluster)

        # ✅ End Marker using dict keys
        folium.Marker(
            location=end,
            icon=folium.CustomIcon(TORNADO_END_ICON, icon_size=icon_size),
            popup=folium.Popup(
                f"""<b>Tornado End</b><br><b>Date:</b> {row['date']}<br><b>Length:</b> {row['len']} miles<br>
                    <b>Temp:</b> {end_weather.get('temperature', 'N/A')}°C<br>
                    <b>Wind:</b> {end_weather.get('wind_speed', 'N/A')} m/s<br>
                    <b>Humidity:</b> {end_weather.get('humidity', 'N/A')}%<br>
                    <b>Pressure:</b> {end_weather.get('pressure', 'N/A')} hPa<br>
                    <b>CAPE:</b> {end_weather.get('cape', 'N/A')}""",
                max_width=300)
        ).add_to(marker_cluster)

        # Add tornado cluster to map (NOT to the global one)
        marker_cluster.add_to(folium_map)

        # Add path and weather markers if enabled
        if SHOW_PATHS:
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
                                    max_width=300
                    )
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

    # Add markers and layers to map
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