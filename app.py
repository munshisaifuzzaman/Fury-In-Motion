# Streamlit main entry point
import pandas as pd
import streamlit as st

from components.map_render import render_map
from utils.data_loader import load_tornado_data
from components.controls import render_sidebar_controls


# === Streamlit UI ===
st.set_page_config(
    page_title="Fury In Motion",
    page_icon="assets/tornado_start.png",  # or use path: "assets/fury.gif" but emojis work best in tabs
    layout="wide"
)

st.title("🌪️ Tornado Visualizer")
# project summary
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

# st.markdown("### 🌪️ Tornado Map Visualizer")

df = load_tornado_data()

# UI Controls
metric, top_n, map_style, value_range = render_sidebar_controls(df)

if metric != "Select" and top_n != "Select":
    render_map(df, metric, int(top_n), value_range, map_style)
else:
    st.info("Select both metric and top N to begin.")

st.markdown("---")
st.markdown("""
<div style='font-size:14px; color:gray; text-align:center;'>
    🔗 Data powered by <a href='https://www.spc.noaa.gov' target='_blank'>NOAA SPC</a>. Weather data from <a href='https://open-meteo.com/' target='_blank'>Open-Meteo</a>.
</div>
""", unsafe_allow_html=True)