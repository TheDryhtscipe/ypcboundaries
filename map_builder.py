"""Build interactive folium map with Welsh boundary layers."""

import json

import folium
from folium import Element

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

    layer_info: list[dict[str, str]] = []

    for dataset, geojson in boundary_data.items():
        cfg = LAYER_CONFIG[dataset]
        name_field = cfg["name_field"]
        type_label = cfg["type_label"]

        layer = folium.FeatureGroup(name=cfg["label"])

        geojson_layer = folium.GeoJson(
            geojson,
            style_function=lambda feature, c=cfg["colour"]: {
                "fillColor": c,
                "color": c,
                "weight": 2,
                "fillOpacity": 0.3,
            },
        )
        geojson_layer.add_to(layer)
        layer.add_to(m)

        layer_info.append({
            "var_name": geojson_layer.get_name(),
            "name_field": name_field,
            "type_label": type_label,
            "group_name": layer.get_name(),
        })

    folium.LayerControl(collapsed=False).add_to(m)

    _add_combined_click_handler(m, layer_info)

    return m


def _add_combined_click_handler(
    m: folium.Map,
    layer_info: list[dict[str, str]],
) -> None:
    """Add JS click handler that shows all boundaries at click point.

    Attaches a click listener to each GeoJson layer. On click, iterates
    all layers doing point-in-polygon ray casting, then opens a single
    combined popup showing every visible boundary at that location.
    """
    map_var = m.get_name()

    js_layers = []
    for info in layer_info:
        js_layers.append(
            f'{{geojson: {info["var_name"]}, '
            f'nameField: {json.dumps(info["name_field"])}, '
            f'typeLabel: {json.dumps(info["type_label"])}, '
            f'group: {info["group_name"]}}}'
        )
    js_layers_str = ",\n            ".join(js_layers)

    # Build list of geojson var names to attach click handlers to
    geojson_vars = [info["var_name"] for info in layer_info]

    script = f"""
    <script>
    window.addEventListener('load', function() {{
        var map = {map_var};
        var layers = [
            {js_layers_str}
        ];

        function pointInRing(lng, lat, ring) {{
            var inside = false;
            for (var i = 0, j = ring.length - 1; i < ring.length; j = i++) {{
                var xi = ring[i].lng, yi = ring[i].lat;
                var xj = ring[j].lng, yj = ring[j].lat;
                if (((yi > lat) !== (yj > lat)) &&
                    (lng < (xj - xi) * (lat - yi) / (yj - yi) + xi)) {{
                    inside = !inside;
                }}
            }}
            return inside;
        }}

        function pointInPolygonLayer(latlng, layer) {{
            if (!layer.getLatLngs) return false;
            var polys = layer.getLatLngs();
            // MultiPolygon: array of polygons, each polygon is array of rings
            // Polygon: array of rings (outer + holes)
            // Simple polygon: single ring (array of LatLng)
            if (polys.length === 0) return false;
            // Detect nesting level by checking if first element is a LatLng
            if (polys[0].lat !== undefined) {{
                // Simple ring
                return pointInRing(latlng.lng, latlng.lat, polys);
            }}
            if (polys[0][0] && polys[0][0].lat !== undefined) {{
                // Single polygon with rings — check outer ring
                return pointInRing(latlng.lng, latlng.lat, polys[0]);
            }}
            // MultiPolygon — check outer ring of each polygon
            for (var p = 0; p < polys.length; p++) {{
                if (polys[p][0] && pointInRing(latlng.lng, latlng.lat, polys[p][0])) {{
                    return true;
                }}
            }}
            return false;
        }}

        function findHits(latlng) {{
            var lines = [];
            for (var i = 0; i < layers.length; i++) {{
                var info = layers[i];
                if (!map.hasLayer(info.group)) continue;
                info.geojson.eachLayer(function(layer) {{
                    if (layer.feature && pointInPolygonLayer(latlng, layer)) {{
                        var name = layer.feature.properties[info.nameField] || '(unknown)';
                        lines.push('<b>' + info.typeLabel + ':</b> ' + name);
                    }}
                }});
            }}
            return lines;
        }}

        function onLayerClick(e) {{
            L.DomEvent.stopPropagation(e);
            var lines = findHits(e.latlng);
            if (lines.length > 0) {{
                L.popup()
                    .setLatLng(e.latlng)
                    .setContent(lines.join('<br>'))
                    .openOn(map);
            }}
        }}

        // Attach click handler to each GeoJson layer
        var geojsonLayers = [{", ".join(geojson_vars)}];
        for (var g = 0; g < geojsonLayers.length; g++) {{
            geojsonLayers[g].on('click', onLayerClick);
        }}
    }});
    </script>
    """
    m.get_root().html.add_child(Element(script))
