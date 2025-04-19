import streamlit as st
from components.controls import render_sidebar_controls
from components.folium_map_render import folium_render_map
from components.folium_radar_map import render_geographic_radar_map
from utils.constants import COLUMN_MAPPING
from utils.data_loader import load_tornado_data, load_station_data
from components.radar_comparison import render_radar_chart
import pandas as pd

df = load_tornado_data()
wsd = load_station_data()

# Handle query param (replaces experimental_get_query_params)
params = st.query_params
if "_view" in params:
    st.session_state["view"] = params["_view"]
    st.rerun()

def render_task_grid():
    # Dashboard Title + Description
    st.title("🌪️ Tornado Visualizer")

    st.markdown("""
    <div style='font-size:21px; line-height:1.5;'>
        <b>Fury In Motion</b> is an interactive visualization platform for tornado patterns across the US. 
        Select filters to explore tornado intensity, path, weather data, and more.
    </div>
    """, unsafe_allow_html=True)

    with st.expander("📄 About the Dataset"):
        st.markdown("""
        - Source: [NOAA SPC Tornado Database](https://www.spc.noaa.gov/wcm/#data)
        - Range: 1950 - 2023  
        - Fields: Location, Date, EF Rating, Path Length, Width, Fatalities, Injuries, Weather Conditions, etc.
        """)

    st.markdown("### 🔍 Select a View to Explore")

    # Inject CSS
    st.markdown("""
    <style>
    .card {
        border: 1px solid #ddd;
        border-radius: 15px;
        padding: 20px;
        margin-bottom: 10px;
        background-color: #fff;
        box-shadow: 2px 2px 10px rgba(0,0,0,0.08);
        transition: transform 0.2s ease-out, box-shadow 0.2s ease-out;
        text-align: center;
        cursor: pointer;
        height: 270px;
    }
    .card:hover {
        transform: scale(1.03);
        box-shadow: 4px 4px 14px rgba(0,0,0,0.15);
    }
    .card img {
        width: 120px;
        margin-bottom: 12px;
    }
    .card-title {
        font-weight: 600;
        font-size: 14px;
        color: #333;
    }
    </style>
    """, unsafe_allow_html=True)

    tasks = [
        {
            "title": "Visualize Top N Tornadoes in terms of different metrics",
            "image": "./assets/tornado_end.png",
            "key": "map"
        },
        {
            "title": "Visualize Top N Tornadoes in terms of different metrics",
            "image": "./assets/tornado_end.png",
            "key": "ef"
        },
    ]

    cols = st.columns(3)

    for idx, task in enumerate(tasks):
        with cols[idx % 3]:
            st.markdown(f"""
            <a href="/?&_view={task['key']}" style="text-decoration: none;">
                <div class="card">
                    <img src="{task['image']}" />
                    <div class="card-title">{task['title']}</div>
                </div>
            </a>
            """, unsafe_allow_html=True)


def render_top_N_page():
    cols = st.columns([0.05, 0.95])
    with cols[0]:
        if st.button("⬅️", key="back_btn", help="Go back to dashboard"):
            if "view" in st.session_state:
                del st.session_state["view"]
            st.query_params.clear()
            st.rerun()

    st.markdown("<br>", unsafe_allow_html=True)

    # Sidebar UI for filtering
    metric, top_n, map_style, value_range = render_sidebar_controls(df)

    if metric != "Select" and top_n != "Select":

        folium_render_map(df, metric, int(top_n), value_range, map_style)

        # ✅ Filtered data for current selection
        col_key, _ = COLUMN_MAPPING[metric]
        min_val, max_val = value_range
        filtered = df[(df[col_key] >= min_val) & (df[col_key] <= max_val)]
        filtered = filtered.sort_values(col_key, ascending=False).head(int(top_n))

        # ✅ Add state column before dropdown
        from utils.folium_utils import get_state_from_latlon
        filtered = filtered.copy()
        filtered["state"] = filtered.apply(lambda row: get_state_from_latlon(row["slat"], row["slon"]), axis=1)

        # 🔁 Run radar comparison UI + chart logic here
        render_radar_chart(filtered)

        # 🗺️ Geographic Radar Comparison Section
        st.markdown("### 🗺️ Geographic Tornado Radar Map")
        st.markdown("---")

        st.markdown("#### 🌐 Select tornadoes for geographic comparison:")

        selected_geo = st.multiselect(
            "Choose tornadoes to show on the map",
            options=list(filtered.index),
            format_func=lambda
                i: f"{filtered.loc[i]['state']} | {filtered.loc[i]['date']} | EF{int(filtered.loc[i]['mag'])}"
        )

        selected_geo_df = filtered.loc[selected_geo] if selected_geo else pd.DataFrame()

        if len(selected_geo_df) >= 2:
            render_geographic_radar_map(selected_geo_df)
        else:
            st.info("📌 Select two or more tornadoes to view them on the comparison map.")

    else:
        st.info("Select both metric and top N to begin.")