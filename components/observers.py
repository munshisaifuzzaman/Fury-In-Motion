import streamlit as st
from components.folium_map_render import update_map
from utils.constants import COLUMN_MAPPING
import components.controls as controls


def update_filter_slider():
    selected_column = controls.dropdown_1
    selected_top_n = controls.dropdown_2
    tornado_data = controls.tornado_data

    if selected_column == "Select" or selected_top_n == "Select":
        return

    col_key, _ = COLUMN_MAPPING[selected_column]

    # Filter data for slider range
    filtered_data = (
        tornado_data
        .sort_values(col_key, ascending=False)
        .head(selected_top_n)
        .dropna(subset=["slat", "slon", "elat", "elon"])
    )
    filtered_data = filtered_data[
        (filtered_data["slat"].between(-90, 90)) & (filtered_data["slon"].between(-180, 180)) &
        (filtered_data["elat"].between(-90, 90)) & (filtered_data["elon"].between(-180, 180))
    ]

    if filtered_data.empty:
        st.error("Filtered dataset is empty.")
        return

    # Compute new slider range
    min_val = float(filtered_data[col_key].min())
    max_val = float(filtered_data[col_key].max())

    # Update slider range in session state
    if "filter_slider_range" not in st.session_state:
        st.session_state["filter_slider_range"] = (min_val, max_val)
    else:
        curr_range = st.session_state["filter_slider_range"]
        if curr_range != (min_val, max_val):
            st.session_state["filter_slider_range"] = (min_val, max_val)

    # Read latest slider values from session (fallback to full range)
    selected_range = st.session_state.get("filter_slider_range", (min_val, max_val))

    # 🔥 Now update the map using current range
    update_map(
        tornado_data,
        selected_column,
        selected_top_n,
        selected_range,
        controls.map_style_dropdown
    )


def on_change(_=None):
    update_filter_slider()


def setup_observers():
    on_change()