import streamlit as st
import pandas as pd
import seaborn as sns
import matplotlib.pyplot as plt
from utils.weather import fetch_weather, load_cached_weather
from utils.data_loader import load_tornado_data


def render_correlation_matrix(filtered_df: pd.DataFrame):
    st.markdown("## 🔬 Enriched Correlation Matrix: Tornado & Weather Variables")
    st.markdown("Analyze deeper relationships between tornado severity and atmospheric conditions.")

    # ✅ Toggle between Top N and Top 457
    scope = st.radio("Choose dataset to analyze:", ["Top N Tornadoes (Filtered)", "Top 457 Tornadoes"], horizontal=True)

    if scope == "Top 457 Tornadoes":
        df = load_tornado_data()
        top_len = df.sort_values("len", ascending=False).head(150)
        top_wid = df.sort_values("wid", ascending=False).head(150)
        top_fat = df.sort_values("fat", ascending=False).head(150)
        top_inj = df.sort_values("inj", ascending=False).head(150)
        df = pd.concat([top_len, top_wid, top_fat, top_inj]).drop_duplicates()
    else:
        df = filtered_df

    cache = load_cached_weather()

    records = []

    for _, row in df.iterrows():
        lat, lon, date = row["slat"], row["slon"], row["date"]
        ef, width, length, fat, inj = row["mag"], row["wid"], row["len"], row["fat"], row["inj"]

        try:
            weather = fetch_weather(lat, lon, date, cache)
        except:
            continue

        if not weather or not isinstance(weather, dict):
            continue

        records.append({
            "EF": ef,
            "Width": width,
            "Length": length,
            "Fatalities": fat,
            "Injuries": inj,
            "Temperature (°C)": weather.get("temperature"),
            "Wind (km/h)": weather.get("wind_speed"),
            "Precipitation (mm)": weather.get("precipitation"),
            "Dew Point (°C)": weather.get("dew_point"),
            "Humidity (%)": weather.get("humidity"),
            "Cloud Cover (%)": weather.get("cloud_cover"),
            "Pressure (hPa)": weather.get("pressure"),
            "CAPE (J/kg)": weather.get("cape"),
            "Soil Moisture (m³/m³)": weather.get("soil_moisture")
        })

    df_corr = pd.DataFrame(records)

    if df_corr.empty:
        st.warning("❌ No valid data to display correlation matrix.")
        return

    # ✅ Drop columns with all null values
    df_corr = df_corr.dropna(axis=1, how="all")
    df_corr = df_corr.dropna(how="all")

    if df_corr.shape[1] < 2:
        st.warning("⚠️ Not enough valid data to compute correlations.")
        return

    corr = df_corr.corr(numeric_only=True)

    if corr.empty:
        st.warning("⚠️ Correlation matrix could not be computed.")
        return

    st.subheader("📊 Correlation Heatmap")
    fig, ax = plt.subplots(figsize=(12, 7))
    sns.heatmap(corr, annot=True, fmt=".2f", cmap="coolwarm", cbar=True, ax=ax)
    st.pyplot(fig)

    if "EF" in corr.columns:
        st.subheader("📋 Correlation with EF Rating")
        ef_corr = corr["EF"].drop("EF").sort_values(ascending=False)
        st.dataframe(ef_corr.to_frame(name="Correlation with EF"), height=300)
    else:
        st.info("EF rating was excluded due to missing data.")
