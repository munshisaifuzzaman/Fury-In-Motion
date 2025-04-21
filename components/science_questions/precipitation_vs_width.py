import pandas as pd
import plotly.express as px
import streamlit as st

from utils.graphical_plot import graphical_plot
from utils.weather import fetch_weather, load_cached_weather

WIDTH_BINS = [0, 100, 300, 800, float("inf")]
WIDTH_LABELS = ["0–100 yd", "101–300 yd", "301–800 yd", "800+ yd"]

def precipitation_vs_width_description():
    with st.expander("📌 Scientific Question: Precipitation vs Tornado Width", expanded=True):
        st.markdown("""
        #### 🔬 Scientific Question: Does Precipitation Correlate with Tornado Width?

        **Goal:**  
        To explore whether tornadoes that occur on days with higher precipitation totals tend to have wider paths, suggesting a possible link between moisture content and tornado scale.

        **Initial Hypothesis:**  
        Increased precipitation reflects deeper convective processes, which may contribute to broader tornado formation and path spread.

        **Datasets Used:**
        - **Tornado Width (`wid`)**: Measured in yards, from NOAA SPC dataset.
        - **Precipitation Sum (`precipitation_sum`)**: Daily total precipitation from Open-Meteo historical API.

        **Weather Variable Explained:**  
        - `precipitation_sum` measures the total rainfall (in mm) recorded on the day and at the location of the tornado's origin.

        **Visualization Strategy:**
        - Use a **scatter plot** with regression to analyze correlation.
        - Group tornadoes by width buckets and compare average precipitation using a **box plot**.

        **What We Hope to Learn:**
        - Do wider tornadoes occur on rainier days?
        - Can precipitation act as a predictor of large tornado path widths?

        """)

def render_precipitation_vs_width(filtered_df, prefetch_457_df):
    precipitation_vs_width_description()
    cache = load_cached_weather()

    # Dataset toggle
    scope = st.radio(
        "Choose tornado dataset to analyze:",
        ["Top N Tornadoes (Filtered)", "Top 457 Prefetched Tornadoes"],
        horizontal=True
    )

    df = filtered_df if scope == "Top N Tornadoes (Filtered)" else prefetch_457_df

    records = []
    for _, row in df.iterrows():
        weather = fetch_weather(row["slat"], row["slon"], row["date"], cache)
        precip = weather.get("precipitation")
        if isinstance(precip, (int, float)) and pd.notnull(precip):
            records.append({
                "Width": row["wid"],
                "Precipitation (mm)": precip
            })

    df_precip = pd.DataFrame(records)
    if df_precip.empty:
        st.warning("No precipitation data available.")
        return

    # 📉 Scatter Plot
    st.subheader("📉 Scatter Plot: Precipitation vs Tornado Width")
    fig = px.scatter(
        df_precip,
        x="Precipitation (mm)",
        y="Width",
        trendline="ols",
        title="Tornado Width by Daily Precipitation"
    )
    fig.update_traces(
        marker=dict(size=8, opacity=0.7, color="rgba(0,100,200,0.7)", line=dict(width=1, color="DarkSlateGrey"))
    )
    fig.update_layout(height=500)
    graphical_plot(fig)

    # 📊 Box Plot (grouped)
    st.subheader("📊 Box Plot: Precipitation by Width Category")
    df_precip["Width Bin"] = pd.cut(df_precip["Width"], bins=WIDTH_BINS, labels=WIDTH_LABELS)
    fig_box = px.box(
        df_precip,
        x="Width Bin",
        y="Precipitation (mm)",
        color="Width Bin",
        title="Precipitation Distribution by Tornado Width Group",
        color_discrete_sequence = px.colors.qualitative.Set2
    )
    fig_box.update_layout(height=500, showlegend=False)
    graphical_plot(fig_box)

    with st.expander("📌 Scientific Question: Precipitation vs Tornado Width", expanded=True):
        st.markdown("""
        #### 🔬 Scientific Question: Do Heavier Rainfall Events Lead to Wider Tornadoes?

        **Goal:**  
        To investigate whether tornadoes associated with higher daily precipitation levels tend to be wider in size.

        **Initial Hypothesis:**  
        Tornadoes forming during heavy precipitation events (e.g., supercells or mesoscale systems) might exhibit wider structures due to enhanced moisture, storm dynamics, or embedded storm mergers.

        **Datasets Used:**
        - **Tornado Width**: Provided in the NOAA SPC tornado dataset (in yards).
        - **Precipitation (`precipitation_sum`)**: Daily precipitation (in mm) retrieved via Open-Meteo’s API based on the tornado’s start coordinates.

        **Weather Variable Explained:**  
        - `precipitation_sum` reflects the **total daily rainfall** at the tornado's location.  
        - It helps indicate whether the tornado was part of a **wet thunderstorm system** or occurred during drier atmospheric conditions.

        **Visualization Strategy:**
        - We use a **scatter plot** to examine trends between tornado width and precipitation.
        - We also use a **box plot** grouped by width categories to study variability across different tornado size ranges.

        ---

        ### 📊 What We Observed from Top 50 Tornadoes

        **1. Top 50 by Width**
        - Scatter plot shows wide tornadoes occurring across both light and moderate rainfall.
        - Box plot reveals **no significant increase in precipitation for wider tornadoes**.
        - ➤ **Conclusion:** Width alone is not a predictor of rainfall intensity.

        **2. Top 50 by Length**
        - Slight upward trend in precipitation vs. width, though not very strong.
        - Box plot shows a **consistent rainfall pattern across different width groups**.
        - ➤ **Conclusion:** Long-path tornadoes may intersect more precipitation, but no solid trend found.

        **3. Top 50 by Fatalities**
        - Scatter plot includes a few **extreme precipitation outliers (>120mm)**.
        - A **downward trend** observed: more fatal tornadoes often occur with **lower or moderate rainfall**.
        - ➤ **Conclusion:** Human impact is not tied to rainfall levels. Precipitation does **not predict fatalities**.

        ---

        ### 🧠 Interpretation
        - Precipitation **does not strongly correlate** with tornado width across any filtered group.
        - **Rainfall may be a byproduct** of the storm type, but not a controlling factor for tornado size.
        - Larger or fatal tornadoes are often driven by **other dynamics** such as CAPE, shear, or terrain—not rainfall.

        ### ✅ Summary
        The evidence suggests **no strong correlation** between daily precipitation and tornado width.  
        Future analysis could explore **multi-variable relationships** (e.g., CAPE + precipitation + EF) to uncover deeper insights.
        """)
