# components/explore.py
import streamlit as st
import matplotlib.pyplot as plt
from matplotlib.colors import Normalize
import matplotlib.cm as cm
import geopandas as gpd
import pandas as pd
from shapely.geometry import Point, box
import os
import io
import base64

from utils.constants import US_STATES_GEOJSON_FILE_PATH, TORNADO_CSV_URL


# --- Utility functions (copied & simplified from temp.py) ---

def prepare_tornado_dataset():
    df_raw = pd.read_csv(TORNADO_CSV_URL)
    df = df_raw[~df_raw['st'].isin(['AK', 'HI', 'PR', 'VI'])]
    geometry = gpd.points_from_xy(df['slon'], df['slat'])
    gdf = gpd.GeoDataFrame(df, geometry=geometry, crs="EPSG:4326")
    gdf = gdf[gdf['mag'] != -9]
    return gdf

def get_clipped_states():
    states = gpd.read_file(US_STATES_GEOJSON_FILE_PATH)
    bounds_box = box(-127, 23, -67, 50)
    return gpd.clip(states, bounds_box)

def get_weather_station_df():
    stations = []
    for filename in os.listdir("data/weather_stations/"):
        stations.append(pd.read_csv(os.path.join("data/weather_stations/", filename)))

    geometry = gpd.points_from_xy(
        [station["LONGITUDE"][0] for station in stations],
        [station["LATITUDE"][0] for station in stations]
    )

    stationdata = [
        [
            station["STATION"][0],
            station["ELEVATION"][1],
            station["DATE"],
            station["PRCP"],
            station["TAVG"],
            station["TMAX"],
            station["TMIN"]
        ]
        for station in stations
    ]

    return gpd.GeoDataFrame(stationdata, geometry=geometry, crs="EPSG:4326")

# --- Main Render Function ---

def render_tornadoes_per_year_trendline():
    import io
    import base64

    # --- Section: Tornadoes Per Year Trendline ---
    st.markdown("## 📈 Tornado Activity Trend by Year")

    row = st.columns([0.25, 0.75])
    with row[0]:
        mag_range = st.slider(
            "Select Magnitude Range for Yearly Trend", 1, 5, (1, 5),
            key="yearly_mag_slider"
        )

    # Prepare data
    gdf_all = prepare_tornado_dataset()
    gdf_filtered = gdf_all[
        (gdf_all["mag"] >= mag_range[0]) & (gdf_all["mag"] <= mag_range[1])
        ]
    yearly_counts = gdf_filtered["yr"].value_counts().sort_index()

    # Create plot
    fig2, ax2 = plt.subplots(figsize=(10, 5))
    ax2.plot(yearly_counts.index, yearly_counts.values, marker="o", linestyle="-", color="#1f77b4")
    ax2.set_title(
        f"Number of Tornadoes Reported by Year (1950–2023)\nwith Magnitudes {mag_range[0]}–{mag_range[1]}",
        fontsize=14
    )
    ax2.set_xlabel("Year", fontsize=12)
    ax2.set_ylabel("Number of Tornadoes", fontsize=12)
    ax2.grid(True)

    # Encode as base64
    buf2 = io.BytesIO()
    fig2.savefig(buf2, format="png", bbox_inches="tight", pad_inches=0.1)
    buf2.seek(0)
    img_base64_2 = base64.b64encode(buf2.read()).decode()

    # Display with same style
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
                text-align: center;
                max-width: 1100px;
                margin-left: auto;
                margin-right: auto;
            ">
                <img src="data:image/png;base64,{img_base64_2}" style="width: 100%; height: auto;" />
            </div>
        """, height=700)


def render_explore_page(year, month, magnitude):


    # year = st.slider("Select Year", 1950, 2023, 1990)
    # month = st.slider("Select Month", 1, 12, 5)
    # magnitude = st.slider("Select Magnitude Range", 1, 5, (1, 5))

    # Load data (can be cached if needed)
    gdf = prepare_tornado_dataset()
    clipped_states = get_clipped_states()
    wgdf = get_weather_station_df()

    gdf_period = gdf[(gdf['yr'] == year) & (gdf['mo'] == month)]
    gdf_period = gdf_period[(gdf_period['mag'] >= magnitude[0]) & (gdf_period['mag'] <= magnitude[1])]

    # Plotting
    norm = Normalize(vmin=1, vmax=5)
    cmap = cm.viridis

    plt.rcParams['figure.dpi'] = 100
    fig, ax = plt.subplots(figsize=(10, 6))
    clipped_states.plot(ax=ax, edgecolor='blue', linewidth=1, facecolor='none')

    if not gdf_period.empty:
        gdf_period.plot(
            ax=ax,
            color=[cmap(norm(m)) for m in gdf_period['mag']],
            marker='.',
            markersize=10,
            alpha=0.7,
            label='Tornado Start Location'
        )

    ax.scatter(
        wgdf.geometry.x, wgdf.geometry.y,
        color='green',
        marker='s',
        s=40,
        alpha=0.5,
        label='Weather Station'
    )

    sm = plt.cm.ScalarMappable(cmap=cmap, norm=norm)
    sm.set_array([])
    cbar = plt.colorbar(sm, ax=ax)
    cbar.set_label("Tornado Magnitude")

    ax.set_title(f"NOAA Tornadoes and Weather Stations ({month}/{year})")
    ax.set_xlabel("Longitude")
    ax.set_ylabel("Latitude")
    ax.legend()

    # Save the Matplotlib figure to a buffer
    buf = io.BytesIO()
    fig.savefig(buf, format="png", bbox_inches='tight', pad_inches=0.1)
    buf.seek(0)

    # Encode the image as base64
    img_base64 = base64.b64encode(buf.read()).decode()

    # Embed in styled HTML container
    col1, col2, col3 = st.columns([0.05, 0.9, 0.05])
    st.components.v1.html(f"""
        <div style="
            border: 3px solid #444;
            border-radius: 12px;
            box-shadow: 0 4px 12px rgba(0, 0, 0, 0.3);
            padding: 10px;
            background-color: white;
            margin-bottom: 30px;
            text-align: center;
            max-width: 1300px;
            margin-left: auto;
            margin-right: auto;
        ">
            <img src="data:image/png;base64,{img_base64}" style="width: 100%; height: auto;" />
        </div>
    """, height=900)

    # Expandable section for inspecting weather station records
    with st.expander("📊 View Weather Station Records"):
        st.markdown("Each row shows a weather station's data for the selected year and month.")

        # You could filter it further if needed — for now, show all
        st.dataframe(
            wgdf.drop(columns=["geometry"]).rename(columns={
                0: "Station ID",
                1: "Elevation (m)",
                2: "Date Series",
                3: "Precipitation",
                4: "Avg Temp (°C)",
                5: "Max Temp (°C)",
                6: "Min Temp (°C)"
            }),
            use_container_width=True
        )

    render_tornadoes_per_year_trendline()

    # === Footer ===
    st.markdown("---")
    st.markdown("""
    <div style='font-size:14px; color:gray; text-align:center;'>
        🔗 Data powered by <a href='https://www.spc.noaa.gov' target='_blank'>NOAA SPC</a>. Weather data from <a href='https://www.ncei.noaa.gov/access/search/data-search/global-summary-of-the-month' target='_blank'>NCEI</a>.
    </div>
    """, unsafe_allow_html=True)
