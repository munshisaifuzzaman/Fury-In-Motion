import streamlit as st
import plotly.io as pio
import html

def graphical_plot(fig):
    # Apply consistent theme and styling
    fig.update_layout(
        template="plotly_white",
        plot_bgcolor="white",
        paper_bgcolor="white",
        xaxis=dict(showline=True, linewidth=1, linecolor="black", mirror=True),
        yaxis=dict(showline=True, linewidth=1, linecolor="black", mirror=True),
    )

    # Convert to HTML and escape for iframe
    fig_html = pio.to_html(fig, include_plotlyjs="cdn", full_html=False)
    escaped_fig = html.escape(fig_html)

    # Render inside a bordered, shadowed container
    col1, col2, col3 = st.columns([0.05, 0.9, 0.05])
    with col2:
        st.components.v1.html(f"""
        <div style="
            border: 3px solid #444;
            border-radius: 12px;
            box-shadow: 0 4px 12px rgba(0, 0, 0, 0.3);
            padding: 10px;
            background-color: white;
            margin-bottom: 30px;
        ">
            <iframe srcdoc='{escaped_fig}' width="100%" height="600" style="border: none;"></iframe>
        </div>
        """, height=650)
