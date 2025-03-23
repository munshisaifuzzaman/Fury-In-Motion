# the state border overlay logic using your local us-states.json file
import json
import folium
import streamlit as st
from utils.constants import US_STATES_GEOJSON_FILE_PATH, EF_COLORS

def add_state_borders(map_obj):
    try:
        with open(US_STATES_GEOJSON_FILE_PATH, "r") as f:
            geojson_data = json.load(f)

        folium.GeoJson(
            geojson_data,
            name="State Borders",
            style_function=lambda x: {
                "fillOpacity": 0,
                "color": "gray",
                "weight": 1.5
            },
            tooltip=folium.GeoJsonTooltip(fields=["name"], aliases=["State:"])
        ).add_to(map_obj)

    except Exception as e:
        st.error(f"Failed to load state borders: {e}")

def add_ef_legend(map_obj):
    legend_html = '''
        <div style="position: fixed; bottom: 50px; left: 50px; width: 170px; height: 180px;
                    background-color: white; z-index:9999; border:2px solid grey; padding: 10px;">
            <b style="font-size:16px;">EF Rating Legend</b><br>
    '''
    for ef, color in EF_COLORS.items():
        legend_html += (
            f'<span style="background-color:{color}; width:15px; height:15px; '
            f'display:inline-block; margin-right:5px;"></span> EF{ef}<br>'
        )
    legend_html += '</div>'
    map_obj.get_root().html.add_child(folium.Element(legend_html))