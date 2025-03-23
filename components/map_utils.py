import folium
from utils.constants import EF_COLORS


def create_ef_layers():
    """
    Create a dictionary of folium FeatureGroups for EF ratings.
    """
    return {
        f"EF{ef}": folium.FeatureGroup(
            name=f"<span style='color:{EF_COLORS[ef]}'>⬤ EF{ef}</span>"
        )
        for ef in range(6)
    }

def add_ef_legend(folium_map):
    """
    Append a fixed-position EF rating legend to the map.
    """
    legend_html = '''
    <div style="
        position: fixed;
        bottom: 50px;
        left: 50px;
        width: 170px;
        height: 180px;
        background-color: white;
        z-index:9999;
        border:2px solid grey;
        padding: 10px;
    ">
    <b style="font-size:16px;">EF Rating Legend</b><br>
    '''

    for ef, color in EF_COLORS.items():
        legend_html += (
            f'<span style="background-color:{color}; '
            f'width:15px; height:15px; display:inline-block; '
            f'margin-right:5px; margin-top:2px; font-size:14px;"></span>'
            f' EF{ef} ({color})<br>'
        )

    legend_html += '</div>'
    folium_map.get_root().html.add_child(folium.Element(legend_html))