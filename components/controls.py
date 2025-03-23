import streamlit as st
from utils.constants import MAP_STYLES, COLUMN_MAPPING

def render_sidebar_controls(df):
    # Header row with logo and project title
    with st.sidebar:
        st.markdown(
            """
            <div style="display: flex; align-items: center; gap: 10px;">
                <span style="font-size: 30px;">🌪️</span>
                <span style="font-weight: bold; font-size: 26px;">Fury In Motion</span>
            </div>
            <hr style="margin-top: 10px;">
            """,
            unsafe_allow_html=True
        )
        # st.markdown("---")  # Optional: horizontal separator
        st.sidebar.title("🛠️ Filters")

    # with st.sidebar:
    #     st.image("assets/fury.gif", width=120)
    #     st.markdown(
    #         "<h1 style='font-size:28px; margin-top: 0;'>Fury In Motion</h1>",
    #         unsafe_allow_html=True
    #     )

    metric = st.sidebar.selectbox("Select Metric", ["Select"] + list(COLUMN_MAPPING.keys()))
    top_n = st.sidebar.selectbox("Top N Tornadoes", ["Select", 10, 20, 30, 40, 50])
    map_style = st.sidebar.selectbox("Map Style", list(MAP_STYLES.keys()))

    value_range = (0.0, 100.0)
    if metric != "Select" and top_n != "Select":
        col, _ = COLUMN_MAPPING[metric]
        filtered = df.sort_values(col, ascending=False).head(top_n)
        filtered = filtered.dropna(subset=["slat", "slon", "elat", "elon"])
        filtered = filtered[
            (filtered["slat"].between(-90, 90)) & (filtered["slon"].between(-180, 180)) &
            (filtered["elat"].between(-90, 90)) & (filtered["elon"].between(-180, 180))
        ]
        if not filtered.empty:
            min_val = float(filtered[col].min())
            max_val = float(filtered[col].max())
            value_range = st.sidebar.slider(
                "Filter Range",
                min_value=min_val,
                max_value=max_val,
                value=(min_val, max_val),
                step=(max_val - min_val) / 20
            )

    return metric, top_n, map_style, value_range