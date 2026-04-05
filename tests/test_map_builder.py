from map_builder import LAYER_CONFIG, build_map, get_name_field


def _fake_geojson(name_field: str, names: list[str]) -> dict:
    return {
        "type": "FeatureCollection",
        "features": [
            {
                "type": "Feature",
                "properties": {name_field: n},
                "geometry": {
                    "type": "Polygon",
                    "coordinates": [[[-3.5, 51.5], [-3.4, 51.5], [-3.4, 51.6], [-3.5, 51.6], [-3.5, 51.5]]],
                },
            }
            for n in names
        ],
    }


def test_layer_config_has_three_entries():
    assert len(LAYER_CONFIG) == 3
    for key in ("unitary", "senedd", "westminster"):
        assert key in LAYER_CONFIG
        cfg = LAYER_CONFIG[key]
        assert "colour" in cfg
        assert "label" in cfg
        assert "name_field" in cfg
        assert "type_label" in cfg


def test_get_name_field():
    assert get_name_field("unitary") == LAYER_CONFIG["unitary"]["name_field"]
    assert get_name_field("senedd") == LAYER_CONFIG["senedd"]["name_field"]
    assert get_name_field("westminster") == LAYER_CONFIG["westminster"]["name_field"]


def test_build_map_returns_folium_map():
    import folium

    data = {
        "unitary": _fake_geojson("CTYUA24NM", ["Cardiff"]),
        "senedd": _fake_geojson("english_na", ["Cardiff South"]),
        "westminster": _fake_geojson("PCON24NM", ["Cardiff South and Penarth"]),
    }
    m = build_map(data)
    assert isinstance(m, folium.Map)


def test_build_map_html_contains_layer_names():
    data = {
        "unitary": _fake_geojson("CTYUA24NM", ["Cardiff"]),
        "senedd": _fake_geojson("english_na", ["Cardiff South"]),
        "westminster": _fake_geojson("PCON24NM", ["Cardiff South and Penarth"]),
    }
    m = build_map(data)
    html = m._repr_html_()
    assert "Unitary Authorities" in html
    assert "Senedd Constituencies" in html
    assert "Westminster Constituencies" in html
