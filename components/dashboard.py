import streamlit as st

from components.controls import render_sidebar_controls_for_top_N_task, render_sidebar_controls_for_weather_station_task
from components.folium_map_render import folium_render_map
from components.weather_station_explore import render_explore_page
from utils.constants import COLUMN_MAPPING
from utils.data_loader import load_tornado_data, load_station_data
from utils.folium_utils import get_state_from_latlon
from utils.top_n_utils import render_scientific_explorer, why_top_n_visualtion, initial_text
import base64

# Load data globally
TDS = load_tornado_data()
STATIONS = load_station_data()

def get_base64_encoded_image(image_path):
    with open(image_path, "rb") as img_file:
        encoded = base64.b64encode(img_file.read()).decode()
        return f"data:image/png;base64,{encoded}"

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
        background-image: url('your-image.jpg');  
        background-size: cover;                  
        background-position: center;
        background-repeat: no-repeat;

        box-shadow: 2px 2px 10px rgba(0,0,0,0.08);
        transition: transform 0.2s ease-out, box-shadow 0.2s ease-out;
        text-align: center;
        cursor: pointer;
        height: 270px;
        position: relative;
        overflow: hidden;
    }

    .card::before {
        content: "";
        position: absolute;
        top: 0; left: 0; right: 0; bottom: 0;
        background: rgba(255, 255, 255, 0.6); 
        z-index: 0;
    }

    .card:hover {
        transform: scale(1.03);
        box-shadow: 4px 4px 14px rgba(0,0,0,0.15);
    }

    .card img {
        width: 120px;
        margin-bottom: 12px;
        z-index: 1;
        position: relative;
    }

    .card-title {
        font-weight: 600;
        font-size: 14px;
        color: #333;
        z-index: 1;
        position: relative;
    }
</style>
    """, unsafe_allow_html=True)

    tasks = [
        {"title": "Visualize Top N Tornadoes", "bg": "assets/bg_munshi_task.png", "key": "map"},
        {"title": "Tornado & Weather Station Map", "bg": "assets/bg_sam_task.png", "key": "explore"},
    ]

    cols = st.columns(3)
    for idx, task in enumerate(tasks):
        with cols[idx % 3]:
            # Encode image as base64 string
            bg_base64 = get_base64_encoded_image(task["bg"])

            st.markdown(f"""
            <a href="/?&_view={task['key']}" style="text-decoration: none;">
                <div class="card" style="
                    background-image: url('{bg_base64}');
                    background-size: cover;
                    background-position: center;
                    position: relative;
                    border: 1px solid #ddd;
                    border-radius: 15px;
                    height: 270px;
                    overflow: hidden;
                    box-shadow: 2px 2px 10px rgba(0,0,0,0.08);
                    transition: transform 0.2s ease-out, box-shadow 0.2s ease-out;
                ">
                    <div style="
                        position: absolute;
                        top: 0;
                        left: 0;
                        width: 100%;
                        height: 100%;
                        background: rgba(255, 255, 255, 0.55);
                        backdrop-filter: blur(2px);
                        display: flex;
                        align-items: center;
                        justify-content: center;
                        border-radius: 15px;
                    ">
                        <div style="
                            font-weight: 1000;
                            font-size: 20px;
                            color: #333;
                            z-index: 1;
                        ">
                            {task['title']}
                        </div>
                    </div>
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

    metric, top_n, map_style, value_range = render_sidebar_controls_for_top_N_task(TDS)

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

    # === Footer ===
    st.markdown("---")
    st.markdown("""
    <div style='font-size:14px; color:gray; text-align:center;'>
        🔗 Data powered by <a href='https://www.spc.noaa.gov' target='_blank'>NOAA SPC</a>. Weather data from <a href='https://open-meteo.com/' target='_blank'>Open-Meteo</a>.
    </div>
    """, unsafe_allow_html=True)

def render_weather_stations_exploration_page():
    cols = st.columns([0.05, 0.95])
    with cols[0]:
        if st.button("⬅️", key="back_btn", help="Go back to dashboard"):
            if "view" in st.session_state:
                del st.session_state["view"]
            st.query_params.clear()
            st.rerun()
    st.title("🌪️ Tornado + Weather Station Explorer")
    st.markdown("<br>", unsafe_allow_html=True)


    year, month, magnitude = render_sidebar_controls_for_weather_station_task()
    return render_explore_page(year, month, magnitude)