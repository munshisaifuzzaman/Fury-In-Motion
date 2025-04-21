import streamlit as st
import pandas as pd
import plotly.express as px
from utils.data_loader import load_tornado_data
from utils.graphical_plot import graphical_plot
from utils.weather import fetch_weather, load_cached_weather

FATALITY_BINS = [0, 1, 5, 20, float("inf")]
FATALITY_LABELS = ["0", "1–5", "6–20", "21+"]

def wind_vs_fatalities_initial_text():
    with st.expander("📌 Scientific Question: Wind Gust vs Fatalities", expanded=True):
        st.markdown("""
        #### 🔬 Scientific Question: Do Higher Surface Wind Gusts Correlate with More Fatalities?

        **Goal:**  
        To explore whether tornadoes occurring on days with stronger surface wind gusts tend to result in more fatalities.

        **Initial Hypothesis:**  
        Tornadoes that form under conditions of stronger surface winds (e.g., gust fronts, downdrafts) are more likely to cause structural damage and increase fatality risk.

        **Datasets Used:**
        - **Fatalities**: Provided in the NOAA SPC tornado dataset.
        - **Max Wind Speed at 10m (`wind_speed_10m_max`)**: Daily surface wind gust (km/h) retrieved from Open-Meteo’s historical weather API at the tornado’s start location.

        **Weather Variable Explained:**  
        - `wind_speed_10m_max` refers to the **maximum surface wind speed (gust)** recorded at **10 meters above ground** on the day of the tornado.  
        - This metric reflects the **storm environment** rather than the tornado’s internal wind.

        **Visualization Strategy:**
        - Plot wind gusts against the number of fatalities using a **scatter plot**.
        - Group tornadoes by EF rating or fatality count buckets to compare **wind gust patterns** using a **box plot** or **density chart**.

        **What We Hope to Learn:**
        - Are tornadoes with higher fatality counts associated with stronger wind gusts?
        - Does wind gust appear to be a proxy for severity or casualty potential?

        **Next Steps:**
        After confirming the data availability and quality, we’ll move on to plotting and interpreting the results to confirm or refute the hypothesis.
        """)


# Fetch all needed weather data once and reuse
@st.cache_data  # Only recomputes if input changes
def build_weather_dataframe(filtered_df):
    cache = load_cached_weather()
    records = []
    for _, row in filtered_df.iterrows():
        weather = fetch_weather(row["slat"], row["slon"], row["date"], cache)
        wind = weather.get("wind_speed")
        if isinstance(wind, (int, float)) and pd.notnull(wind):
            records.append({
                "Wind Gust (km/h)": wind,
                "Fatalities": row["fat"]
            })
    return pd.DataFrame(records)

def render_wind_vs_fatalities(filtered_df, prefetch_457_df):
    wind_vs_fatalities_initial_text()

    scope = st.radio(
        "Choose dataset to analyze:",
        ["Top N Tornadoes (Filtered)", "Pre-fetched 457 Tornadoes"],
        horizontal=True
    )
    df = filtered_df if scope == "Top N Tornadoes (Filtered)" else prefetch_457_df

    gust_df = build_weather_dataframe(df)

    if gust_df.empty:
        st.warning("No wind gust data available.")
        return

    # 📉 Enhanced Scatter Plot
    st.subheader("📉 Scatter Plot: Wind Gust vs Fatalities")
    st.caption(
        "This plot shows if higher wind gusts correlate with more fatalities. A trendline is included for insight.")
    fig = px.scatter(
        gust_df,
        x="Wind Gust (km/h)",
        y="Fatalities",
        trendline="ols",
        labels={"Fatalities": "Number of Fatalities"},
        color_discrete_sequence=["#1f77b4"],
        title="💨 Wind Gust vs Fatalities (With Linear Trendline)"
    )
    fig.update_traces(
        marker=dict(size=8, opacity=0.7, color="rgba(0,100,200,0.7)", line=dict(width=1, color="DarkSlateGrey"))
    )
    fig.update_layout(height=500)
    graphical_plot(fig)

    # 📊 Enhanced Box Plot
    st.subheader("📊 Box Plot: Wind Gust by Fatality Range")
    st.caption("Visualize how wind gusts vary across tornadoes grouped by fatality counts.")
    gust_df["Fatality Bin"] = pd.cut(gust_df["Fatalities"], bins=FATALITY_BINS, labels=FATALITY_LABELS)
    fig_box = px.box(
        gust_df,
        x="Fatality Bin",
        y="Wind Gust (km/h)",
        color="Fatality Bin",
        color_discrete_sequence=["#A0C4FF", "#FFADAD", "#BDB2FF", "#CAFFBF"],
        title="📊 Wind Gust Distribution Across Fatality Ranges",
        # color_discrete_sequence = px.colors.qualitative.Set2
    )
    fig_box.update_traces(marker=dict(opacity=0.5), line=dict(width=1.5))
    fig_box.update_layout(height=500, showlegend=False)
    graphical_plot(fig_box)

    # 📌 Interpretation
    st.markdown("""
    ### 🧠 Interpretation

    - The scatter plot reveals whether a positive correlation exists between surface wind and fatalities.
    - The box plot helps determine if tornadoes with higher fatalities tend to occur on higher-wind days.
    - If **higher fatality bins consistently show higher wind speeds**, it may suggest environmental wind shear or gust potential plays a role in impact severity.

    ### ✅ Result

    _[⬜ To be filled based on output — e.g., “Moderate wind values (30–40 km/h) were common across all fatality groups, with no strong upward trend observed.”]_  
    _[⬜ Or “The 21+ fatality bin had a significantly higher wind gust distribution compared to 0-death tornadoes.”]_
    """)