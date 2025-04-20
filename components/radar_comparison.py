# components/radar_comparison.py

import streamlit as st
import plotly.graph_objects as go
from utils.folium_utils import get_state_from_latlon

def spyder_radar_initial_text():
    with st.expander("🧠 Why Use a Spider Radar Chart? What Insights Does It Reveal?", expanded=False):
        st.markdown("""
        This radar chart provides a **multi-dimensional comparison** of selected tornadoes based on five critical attributes:
        - **EF Rating**
        - **Length (mi)**
        - **Width (yd)**
        - **Fatalities**
        - **Injuries**

        #### ✅ Why We Visualized This:
        - To help users identify **patterns across multiple severity metrics** in a single glance.
        - To compare tornadoes that may have similar EF ratings but vastly different outcomes in terms of **damage or human impact**.
        - To expose **trade-offs or outliers**, such as tornadoes with high fatalities but lower wind ratings.

        #### 🔍 What This Visualization Reveals:
        - Some **longer and wider tornadoes** did not result in high casualties.
        - Certain tornadoes with **lower EF ratings** still caused many injuries — suggesting **contextual factors** like time of day or location matter.
        - Users can **visually correlate** EF rating with actual destruction using spider-shaped area comparisons.

        #### 🔬 How It Leads to Deeper Questions:
        - Why do some EF2 tornadoes cause more harm than EF4 ones?
        - Are tornado width or length **better indicators** of impact than EF rating alone?
        - Can we visually detect **clusters of destructive patterns** by comparing shapes?

        This chart is an entry point to **deeper scientific analysis**, especially when paired with weather data like CAPE or wind gusts.
        """)

def render_radar_chart(filtered_df):
    st.markdown("### 🌪️ Tornado Radar Comparison")
    spyder_radar_initial_text()


    df = filtered_df.copy()
    df["name"] = df.apply(lambda row: get_state_from_latlon(row["slat"], row["slon"]), axis=1)

    # Label for dropdown
    df["label"] = df.apply(
        lambda row: f"{row['state']} | {str(row['date'])[:10]} | EF{int(row['mag'])} | {round(row['len'], 1)} mi",
        axis=1
    )

    # Metric columns to include
    metrics = ["mag", "len", "wid", "fat", "inj"]
    metric_labels = ["EF", "Length (mi)", "Width (yd)", "Fatalities", "Injuries"]

    # Sidebar selection
    selected_labels = st.multiselect(
        "✅ Select tornadoes to compare:",
        options=df["label"],
        default=[],
    )
    legend_style = dict(font=dict(size=16))  # base legend font

    if len(selected_labels) >= 2:
        selected_data = df[df["label"].isin(selected_labels)]

        # Normalize per column using min-max scaling (but only for display)
        scaled_data = selected_data.copy()
        for m in metrics:
            min_val = selected_data[m].min()
            max_val = selected_data[m].max()
            if max_val - min_val == 0:
                scaled_data[m] = 0
            else:
                scaled_data[m] = (selected_data[m] - min_val) / (max_val - min_val)

        # Build radar plot
        fig = go.Figure()

        for i, row in scaled_data.iterrows():
            values = [row[m] for m in metrics]
            fig.add_trace(go.Scatterpolar(
                r=values,
                theta=metric_labels,
                fill='toself',
                name=row["label"],
                hovertemplate="<b>%{theta}</b>: %{r:.2f}<extra>" + row["label"] + "</extra>"
            ))

        fig.update_layout(
            polar=dict(
                radialaxis=dict(
                    visible=True,
                    range=[0, 1],
                    tickvals=[0, 0.25, 0.5, 0.75, 1],
                    ticktext=["Very Low", "Low", "Medium", "High", "Very High"],
                    tickfont=dict(size=14),
                    tickangle=45,
                    showline=True,
                    linewidth=1,
                    gridcolor="gray",
                    gridwidth=0.5
                ),
                angularaxis=dict(
                    tickfont=dict(size=18),
                    rotation=90
                )
            ),
            legend=dict(
                title=dict(text="Tornadoes Compared", font=dict(size=18)),
                **legend_style,
                itemsizing="constant",
            ),
            font=dict(size=14),
            showlegend=True,
            height=650,
            margin=dict(t=50, b=30, l=20, r=20)
        )

        st.plotly_chart(fig, use_container_width=True)
    else:
        st.info("☝️ Select at least two tornadoes to generate a radar comparison.")
