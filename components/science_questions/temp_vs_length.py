import streamlit as st
import pandas as pd
import plotly.express as px
from utils.weather import fetch_weather, load_cached_weather

LENGTH_BINS = [0, 10, 30, float("inf")]
LENGTH_LABELS = ["Short (0–10 mi)", "Medium (10–30 mi)", "Long (30+ mi)"]

def temp_vs_length_initial_text():
    with st.expander("📌 Scientific Question: Temperature vs Tornado Length", expanded=True):
        st.markdown("""
        #### 🔬 Scientific Question: Do Higher Surface Temperatures Correlate with Longer Tornado Paths?

        **Goal:**  
        Investigate whether warmer surface temperatures are associated with longer tornado tracks.

        **Initial Hypothesis:**  
        Tornadoes that form on warmer days may have access to more energy in the atmosphere, which could help sustain them over longer distances.

        **Datasets Used:**
        - **Path Length (`len`)**: Provided in the NOAA SPC tornado dataset.
        - **Max Surface Temperature (`temperature_2m_max`)**: Retrieved from Open-Meteo’s historical weather API at the tornado start location.

        **Weather Variable Explained:**  
        - `temperature_2m_max` refers to the **maximum surface temperature (°C)** recorded at **2 meters above ground level** on the day of the tornado.

        **Visualization Strategy:**
        - Plot tornado length vs. max daily surface temperature using a **scatter plot with trendline**.
        - Use a **box plot** to compare temperatures across short, medium, and long tornado categories.

        **What We Hope to Learn:**
        - Are longer tornadoes more likely to form on hotter days?
        - Does ambient surface temperature provide clues about tornado energy or persistence?

        **Next Steps:**
        We analyze the visual trends to see if higher temperatures consistently appear in longer tornado events.
        """)

def render_temp_vs_length(filtered_df: pd.DataFrame, prefetch_457_df: pd.DataFrame):
    temp_vs_length_initial_text()

    # Radio toggle between datasets
    choice = st.radio(
        "Choose dataset to explore:",
        ["Top N Tornadoes (Filtered)", "457 Pre-Fetched Tornadoes"],
        horizontal=True
    )

    base_df = filtered_df if choice == "Top N Tornadoes (Filtered)" else prefetch_457_df.copy()
    cache = load_cached_weather()

    # Step: Enrich with weather only if needed
    records = []
    for _, row in base_df.iterrows():
        weather = fetch_weather(row["slat"], row["slon"], row["date"], cache)
        temperature = weather.get("temperature")
        if isinstance(temperature, (int, float)) and pd.notnull(temperature):
            records.append({
                "Max Temp (°C)": temperature,
                "Tornado Length (mi)": row["len"]
            })

    df_temp = pd.DataFrame(records)

    if df_temp.empty:
        st.warning("No temperature data available.")
        return

    # 📉 Scatter Plot
    st.subheader("📉 Scatter Plot: Temperature vs Tornado Length")
    fig1 = px.scatter(
        df_temp,
        x="Max Temp (°C)",
        y="Tornado Length (mi)",
        trendline="ols",
        title="Tornado Length by Max Surface Temperature"
    )
    fig1.update_traces(marker=dict(size=7, opacity=0.6))
    fig1.update_layout(height=500)
    st.plotly_chart(fig1, use_container_width=True)

    # 📊 Box Plot
    st.subheader("📊 Box Plot: Temperature Distribution by Tornado Length Category")
    df_temp["Length Category"] = pd.cut(df_temp["Tornado Length (mi)"], bins=LENGTH_BINS, labels=LENGTH_LABELS)
    fig2 = px.box(
        df_temp,
        x="Length Category",
        y="Max Temp (°C)",
        color="Length Category",
        title="Surface Temperature Distribution by Tornado Length"
    )
    fig2.update_layout(height=500, showlegend=False)
    st.plotly_chart(fig2, use_container_width=True)

    st.markdown("""
    ### 🧠 Scientific Interpretation: Temperature vs Tornado Length

    This section analyzes whether higher surface temperatures are linked to longer tornado paths, based on three different subsets of the top 50 tornadoes.

    ---

    #### 📊 **Top 50 by Length**
    - **Trend:** Slight **positive correlation** observed between surface temperature and tornado length.
    - **Insight:** Most long-path tornadoes occurred at **moderate to high temperatures** (22–30°C).
    - **Implication:** Warmer surface air may help sustain stronger updrafts, supporting extended tornado tracks.

    ---

    #### 🌪️ **Top 50 by Width**
    - **Trend:** **Slight negative correlation** between temperature and tornado length.
    - **Insight:** Wide tornadoes were not necessarily associated with higher temperatures.
    - **Implication:** Width may depend more on mesocyclone structure than surface heating alone.

    ---

    #### ☠️ **Top 50 by Fatalities**
    - **Trend:** Also shows **mild negative correlation**.
    - **Insight:** Tornadoes with high fatalities did not consistently occur on the hottest days.
    - **Implication:** Fatality count is more influenced by **timing, population density, and preparedness** than temperature.

    ---

    ### ✅ Final Conclusion
    While **longer tornadoes** appear more likely to form on **warmer days**, this relationship weakens when filtered by **width or fatalities**. This suggests that **temperature alone is insufficient** as a predictor of tornado severity. Future analysis should consider combining temperature with other atmospheric indicators (e.g., CAPE, wind shear) for deeper insights.
    """)