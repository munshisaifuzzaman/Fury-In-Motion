# === Streamlit main entry point ===
import streamlit as st

# MUST be first
st.set_page_config(
    page_title="Fury In Motion",
    page_icon="assets/tornado_start.png",
    layout="wide"
)

# Load views
from components.dashboard import render_task_grid, render_top_N_page, render_weather_stations_exploration_page

# Handle routing
params = st.query_params
if "_view" in params:
    st.session_state["view"] = params["_view"]
    st.query_params.clear()

# === Render correct view ===
if "view" not in st.session_state:
    render_task_grid()
else:
    if st.session_state["view"] == "map":
        render_top_N_page()
    elif st.session_state["view"] == "explore":  # ⬅️ Add this
        render_weather_stations_exploration_page()
