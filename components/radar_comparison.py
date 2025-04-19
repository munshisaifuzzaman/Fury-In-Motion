# components/radar_comparison.py

import streamlit as st
import plotly.graph_objects as go
from utils.folium_utils import get_state_from_latlon

def render_radar_chart(filtered_df):
    st.markdown("### 🌪️ Tornado Radar Comparison")
    st.markdown("---")  # Horizontal line separator

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
