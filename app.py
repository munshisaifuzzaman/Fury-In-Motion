# === Streamlit main entry point ===
import streamlit as st

# MUST be first
st.set_page_config(
    page_title="Fury In Motion",
    page_icon="assets/tornado_start.png",
    layout="wide"
)

# Load views
from components.dashboard import render_task_grid, render_top_N_page

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
    elif st.session_state["view"] == "ef":
        render_top_N_page()

# === Footer ===
st.markdown("---")
st.markdown("""
<div style='font-size:14px; color:gray; text-align:center;'>
    🔗 Data powered by <a href='https://www.spc.noaa.gov' target='_blank'>NOAA SPC</a>. Weather data from <a href='https://open-meteo.com/' target='_blank'>Open-Meteo</a>.
</div>
""", unsafe_allow_html=True)