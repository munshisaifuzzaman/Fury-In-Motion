import streamlit as st

from components.controls import render_sidebar_controls
from components.folium_map_render import folium_render_map
from utils.constants import COLUMN_MAPPING
from utils.data_loader import load_tornado_data, load_station_data
from utils.folium_utils import get_state_from_latlon
from utils.top_n_utils import render_scientific_explorer, why_top_n_visualtion, initial_text

# Load data globally
TDS = load_tornado_data()
STATIONS = load_station_data()

def render_task_grid():
    st.title("🌪️ Tornado Visualizer")

    st.markdown("""
    <div style='font-size:21px; line-height:1.5; padding-bottom:10px;'>
        <b>Fury In Motion</b> is an interactive visualization platform for tornado patterns across the US. 
        Select filters to explore tornado intensity, path, weather data, and more.
    </div>
    """, unsafe_allow_html=True)

    with st.expander("📄 About the Dataset"):
        st.markdown("""
        - Source: [NOAA SPC Tornado Database](https://www.spc.noaa.gov/wcm/#data)
        - Range: 1950 - 2023  
        - Fields: Location, Date, EF Rating, Path Length, Width, Fatalities, Injuries, etc.
        """)

    st.markdown("### 🔍 Select a View to Explore")

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
        {"title": "Visualize Top N Tornadoes", "image": "./assets/tornado_end.png", "key": "map"},
        {"title": "Explore Scientific Questions", "image": "./assets/science_icon.png", "key": "science"},
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

    initial_text(st)
    st.markdown("<br>", unsafe_allow_html=True)

    metric, top_n, map_style, value_range = render_sidebar_controls(TDS)

    if metric != "Select" and top_n != "Select":
        folium_render_map(TDS, metric, int(top_n), value_range, map_style)
        why_top_n_visualtion(st)

        col_key, _ = COLUMN_MAPPING[metric]
        min_val, max_val = value_range
        filtered = TDS[(TDS[col_key] >= min_val) & (TDS[col_key] <= max_val)]
        filtered = filtered.sort_values(col_key, ascending=False).head(int(top_n))

        filtered = filtered.copy()
        filtered["state"] = filtered.apply(lambda row: get_state_from_latlon(row["slat"], row["slon"]), axis=1)

        render_scientific_explorer(st, filtered)

    else:
        st.info("Select both metric and top N to begin.")

