import pandas as pd

from components.folium_radar_map import render_geographic_radar_map, geo_radar_initial_text
from components.radar_comparison import render_radar_chart
from components.science_questions.correlation_matrix import render_correlation_matrix
from components.science_questions.ef_vs_cape import render_ef_vs_cape
from components.science_questions.precipitation_vs_width import render_precipitation_vs_width
from components.science_questions.temp_vs_length import render_temp_vs_length
from components.science_questions.wind_vs_fatalities import render_wind_vs_fatalities


def initial_text(st):
    with st.expander("🧽 Overview: Top N Tornadoes Explorer", expanded=True):
        st.markdown("""
        **Purpose:**  
        This module enables users to explore the most significant tornadoes in the U.S. based on various metrics like path length, width, EF rating, fatalities, and injuries. The visual interface provides dynamic insights into storm characteristics and serves as a launching pad for scientific exploration.

        **Datasets Used:**
        - **NOAA SPC Tornado Database (1950–2023)**  
          Contains geospatial and severity-related information of tornadoes such as:
          - EF rating
          - Path length (mi) and width (yd)
          - Fatalities and injuries
          - Start and end coordinates
          - Date and location metadata

        - **Open-Meteo Daily Historical Weather API**  
          Provides atmospheric conditions (for tornado origin and path) such as:
          - Max Temperature (`temperature_2m_max`)
          - Max Wind Speed (`wind_speed_10m_max`)
          - Daily Precipitation (`precipitation_sum`)
          - Max CAPE (`cape_max`, used for scientific questions)

        **What You Can Do on This Page:**
        - 📍 Visualize the **Top N tornadoes** interactively on a Folium map  
        - 📊 Compare tornadoes using a **spider-style radar chart**  
        - 🗜️ Analyze tornado **paths and geography** using a side-by-side radar map  
        - 🔬 Use this as a **gateway to scientific exploration**, such as:
          - Investigating the correlation between EF rating and CAPE
          - Studying how weather patterns vary across tornado severities
          - Exploring if path length relates to higher CAPE or max wind speed
        """)

def why_top_n_visualtion(st):
    with st.expander("❓ Why Visualize Top N Tornadoes? What Have We Learned?", expanded=False):
        st.markdown("""
        The Top N tornado visualization was created to help users explore the most impactful tornado events in U.S. history, ranked by measurable metrics like path length, EF rating, width, fatalities, and injuries.

        #### ✅ Why We Visualized This:
        - To focus on **outliers** — the most extreme and destructive tornadoes.
        - To enable **quick visual comparisons** using radar charts and side-by-side maps.
        - To understand how severity metrics **relate to one another** (e.g., does a longer path always mean higher EF rating?).

        #### 🌪 What This Visualization Reveals:
        - **Longer tornadoes** don’t always cause the most fatalities — some short ones were more deadly due to location or time.
        - **EF4 and EF5 tornadoes** often show significant variation in injuries and path width.
        - In several cases, tornadoes with **moderate EF ratings** caused severe damage due to **high wind and terrain factors**, which we now connect to atmospheric data.

        #### 🧪 How This Leads to Scientific Questions:
        These findings led us to ask:
        - What **weather conditions** caused these severe events?
        - Do **CAPE** or **wind speeds** correlate with path size or fatalities?
        - Can we visually spot **atmospheric precursors** for the most intense tornadoes?

        This Top N module serves as a launching pad for deeper scientific exploration, backed by real data and real storms.
        """)

def render_scientific_explorer(st, filtered):
    st.title("🔬 Scientific Questions Explorer")

    st.markdown("""
    Dive deeper into how weather conditions relate to tornado severity. 
    Select a hypothesis to explore its visual analysis and interpretations.
    """, unsafe_allow_html=True)

    question = st.selectbox("Choose a scientific question to explore:", [
        "— Select a question —",
        "Spider Radar Chart (EF, Injuries, Width, etc.)",
        "Geographic Radar View (Compare Tornado Paths)",
        "EF Rating vs CAPE",
        "Wind Gust vs Fatalities",
        "Temperature vs Tornado Length",
        "Precipitation vs Tornado Width",
        "Correlation Matrix"
    ])

    if question == "Spider Radar Chart (EF, Injuries, Width, etc.)":
        render_radar_chart(filtered)

    elif question == "Geographic Radar View (Compare Tornado Paths)":
        st.markdown("### 📽️ Geographic Tornado Radar Map")
        geo_radar_initial_text(st)
        st.markdown("#### 🌐 Select tornadoes for geographic comparison:")
        selected_geo = st.multiselect(
            "Choose tornadoes to show on the map",
            options=list(filtered.index),
            format_func=lambda
                i: f"{filtered.loc[i]['state']} | {filtered.loc[i]['date']} | EF{int(filtered.loc[i]['mag'])}"
        )

        selected_geo_df = filtered.loc[selected_geo] if selected_geo else pd.DataFrame()

        if len(selected_geo_df) >= 2:
            render_geographic_radar_map(selected_geo_df)
        else:
            st.info("📌 Select two or more tornadoes to view them on the comparison map.")

    elif question == "EF Rating vs CAPE":
        render_ef_vs_cape()

    elif question == "Wind Gust vs Fatalities":
        render_wind_vs_fatalities(filtered)

    elif question == "Temperature vs Tornado Length":
        render_temp_vs_length(filtered)

    elif question == "Precipitation vs Tornado Width":
        render_precipitation_vs_width(filtered)

    elif question == "Correlation Matrix":
        render_correlation_matrix(filtered)

    else:
        st.warning("🚧 This scientific question is under construction. Please select another.")
