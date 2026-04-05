"""Build interactive folium map with Welsh boundary layers."""

import folium

LAYER_CONFIG: dict[str, dict[str, str]] = {
    "unitary": {
        "colour": "#2196F3",
        "label": "Unitary Authorities",
        "name_field": "CTYUA24NM",
        "type_label": "Unitary Authority",
    },
    "senedd": {
        "colour": "#4CAF50",
        "label": "Senedd Constituencies",
        "name_field": "english_na",
        "type_label": "Senedd Constituency",
    },
    "westminster": {
        "colour": "#FF9800",
        "label": "Westminster Constituencies",
        "name_field": "PCON24NM",
        "type_label": "Westminster Constituency",
    },
}

# Centre of Wales (approximately Llandrindod Wells)
WALES_CENTRE = (52.24, -3.38)
DEFAULT_ZOOM = 8


def get_name_field(dataset: str) -> str:
    """Return the GeoJSON property name for the boundary name."""
    return LAYER_CONFIG[dataset]["name_field"]


def build_map(boundary_data: dict[str, dict[str, object]]) -> folium.Map:
    """Build a folium map with all boundary layers.

    Args:
        boundary_data: Dict mapping dataset name ('unitary', 'senedd',
            'westminster') to parsed GeoJSON dicts.

    Returns:
        Configured folium.Map with all layers and controls.
    """
    m = folium.Map(
        location=WALES_CENTRE,
        zoom_start=DEFAULT_ZOOM,
        tiles="cartodbpositron",
    )

    for dataset, geojson in boundary_data.items():
        cfg = LAYER_CONFIG[dataset]
        name_field = cfg["name_field"]
        type_label = cfg["type_label"]

        layer = folium.FeatureGroup(name=cfg["label"])

        folium.GeoJson(
            geojson,
            style_function=lambda feature, c=cfg["colour"]: {
                "fillColor": c,
                "color": c,
                "weight": 2,
                "fillOpacity": 0.3,
            },
            tooltip=folium.GeoJsonTooltip(
                fields=[name_field],
                aliases=[f"{type_label}: "],
                sticky=True,
            ),
            popup=folium.GeoJsonPopup(
                fields=[name_field],
                aliases=[f"{type_label}: "],
            ),
        ).add_to(layer)

        layer.add_to(m)

    folium.LayerControl(collapsed=False).add_to(m)

    return m
