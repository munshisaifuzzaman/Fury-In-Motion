# Fury In Motion: Visualizing U.S. Tornadoes

> *“The storm never lasts forever. Bad weeks come and go. You can't control the wind—but you can control your sail.”*

<p align="center">
  <img src="https://img.shields.io/badge/Built%20With-Python-blue.svg" alt="Python Badge">
  <img src="https://img.shields.io/badge/Framework-Streamlit-brightgreen.svg" alt="Streamlit Badge">
  <img src="https://img.shields.io/badge/Visualization-Folium%20%7C%20Plotly-orange.svg" alt="Folium and Plotly Badge">
    <a href="https://furyinmotion.streamlit.app/">
        <img src="https://img.shields.io/badge/Live-Demo-orange?logo=streamlit" alt="Live Demo Badge">
      </a>
</p>

---

## 🚀 Project Overview

**Fury In Motion** is an interactive scientific visualization platform that explores U.S. tornado data through dynamic maps, statistical analysis, and weather integration.  
We aim to help users:

- Analyze historical tornado events (1950–2023).
- Explore how tornado severity correlates with environmental and demographic factors.
- Investigate patterns in tornado behavior over time.

This project was developed as part of a scientific visualization course.

---

## 🎯 Project Goals

- **General Goals:**
  - Display tornado data in an engaging and informative format.
  - Use multiple forms of visualization to communicate complex patterns effectively.
  - Cover a large time span to uncover long-term trends.

- **Scientific Goals:**
  - **Munshi:** Visualize and compare the top 10–50 most impactful tornadoes based on path length, width, fatalities, and injuries, integrating historical weather conditions.
  - **Sam:** Incorporate NOAA weather station data to explore meteorological influences on tornado frequency and distribution.
  - **Matthew:** Investigate the relationship between county population sizes and tornado damage (fatalities and injuries).

---

## 📚 Background

- **Primary Dataset:**  
  NOAA's US Tornado Database (1950–2023).

- **Supplementary Data:**
  - NOAA Weather Stations (precipitation, temperature, etc.).
  - Open-Meteo Weather API (historical hourly/daily weather).
  - U.S. Census Bureau County Population Estimates (2023).
  - TIGER Line Shapefiles for county boundaries.

- **Scientific Context:**  
  We consulted academic and meteorological resources to hypothesize and validate relationships between atmospheric conditions and tornado severity.

---

## 🗺️ Project Components

- **Top-N Tornado Explorer:**  
  Visualizes the most impactful tornadoes colored by EF rating, with weather-enriched start/end popups.

- **Scientific Question Explorer:**  
  Explores relationships between tornado metrics and weather variables (e.g., temperature vs. path length, wind speed vs. fatalities).

- **Meteorological Trends Over Time:**  
  Investigates how tornado frequency and intensity vary across seasons and decades using weather station data.

- **Demographic Impact Map:**  
  Interactive choropleth showing county populations overlaid with tornado damage indicators.

---

## 🛠️ Implementation Details

- **Framework:** Python + Streamlit
- **Main Libraries:**
  - Folium (Geospatial maps)
  - Plotly (Interactive plots and radar charts)
  - GeoPandas (Geographical data processing)
  - PyDeck (Stacked geo bar charts)
  - TQDM, Seaborn, Pandas, NumPy, Shapely

- **Architecture:**

```bash
/data                # Tornado datasets, GeoJSONs
/cache               # Prefetched weather data (weather_cache.json)
/utils               # Data loading and processing utilities
/components          # Visualization modules
/science_questions   # Scientific exploration scripts
app.py               # Main Streamlit app
```
- - **Caching Strategy:**  
  Used local caching of weather API responses to ensure faster rendering and reproducibility.

---

## 📈 Scientific Highlights

- Most severe tornadoes (by fatalities and width) cluster heavily in the Southeast and Midwest.
- Higher surface temperatures did **not** strongly correlate with longer tornado paths.
- Surface wind gusts showed **weak** correlation with fatalities.
- Precipitation levels had **minimal** correlation with tornado width.

These results challenge common assumptions and highlight the complex, multifactorial nature of tornado impacts.

---

## 🧠 Key Learnings

- Data-driven validation is essential—hypotheses often fail under empirical scrutiny.
- API-based data enrichment introduces reproducibility and scaling challenges.
- Balancing interactivity and clarity in visualizations is critical to avoid overwhelming users.
- Visual analytics such as correlation matrices and radar charts can reveal or debunk assumed patterns.

---

## 🛠️ How to Run

1. Clone the repository:

```bash
git clone https://github.com/munshisaifuzzaman/Fury-In-Motion.git
```
2. Navigate to the project directory:
```bash
cd Fury-In-Motion
```
3. Launch the Streamlit app:
```bash
streamlit run app.py
```

---


## 🔗 Code Repository

- **GitHub Repository:** [Fury-In-Motion](https://github.com/munshisaifuzzaman/Fury-In-Motion)
- **Live Demo:** *Coming Soon!* 🚀

---

## ✨ Future Work

- Add financial damage data from insurance datasets.
- Expand to visualize other natural disasters (e.g., hurricanes, wildfires).
- Enhance user interactivity with dynamic filters and expanded weather layers.

---

## 👥 Authors

- **Munshi Saifuzzaman** – Weather-driven scientific exploration
- **Sam** – Temporal analysis and meteorological trends
- **Matthew** – Demographic and spatial analysis

---

## 📸 Sample Visuals

### From Munshi Saifuzzaman's exploration of the top N most impactful tornadoes: 
<p align="center">
<img src="assets/app_snapshots/img_19.png" alt="Sample 1" width="30%">
  <img src="assets/app_snapshots/img.png" alt="Sample 1" width="30%">
  <img src="assets/app_snapshots/img_1.png" alt="Sample 2" width="30%">
  <img src="assets/app_snapshots/img_2.png" alt="Sample 2" width="30%">
  <img src="assets/app_snapshots/img_3.png" alt="Sample 2" width="30%">
  <img src="assets/app_snapshots/img_4.png" alt="Sample 2" width="30%">
  <img src="assets/app_snapshots/img_5.png" alt="Sample 2" width="30%">
  <img src="assets/app_snapshots/img_6.png" alt="Sample 2" width="30%">
  <img src="assets/app_snapshots/img_7.png" alt="Sample 2" width="30%">
  <img src="assets/app_snapshots/img_8.png" alt="Sample 2" width="30%">
  <img src="assets/app_snapshots/img_9.png" alt="Sample 2" width="30%">
  <img src="assets/app_snapshots/img_10.png" alt="Sample 2" width="30%">
  <img src="assets/app_snapshots/img_11.png" alt="Sample 2" width="30%">
  <img src="assets/app_snapshots/img_12.png" alt="Sample 2" width="30%">
  <img src="assets/app_snapshots/img_13.png" alt="Sample 2" width="30%">
  <img src="assets/app_snapshots/img_14.png" alt="Sample 2" width="30%">
  <img src="assets/app_snapshots/img_15.png" alt="Sample 2" width="30%">
  <img src="assets/app_snapshots/img_16.png" alt="Sample 2" width="30%">
  <img src="assets/app_snapshots/img_17.png" alt="Sample 2" width="30%">
  <img src="assets/app_snapshots/img_18.png" alt="Sample 2" width="30%">
  <img src="assets/app_snapshots/img_19.png" alt="Sample 2" width="30%">
</p>

### From Sam's exploration of tornado frequency and intensity over time: 
<p align="center">
  <img src="assets/app_snapshots/img_20.png" alt="Sample 4" width="40%">
  <img src="assets/app_snapshots/img_21.png" alt="Sample 4" width="40%">
</p>

### From Matthew's exploration of tornado damage and population density:
<p align="center">
  <img src="assets/app_snapshots/img_22.png" alt="Sample 4" width="100%">
</p>
---