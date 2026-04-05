"""Download and cache Welsh boundary GeoJSON data."""

import json
from pathlib import Path

import requests

DATA_DIR = Path(__file__).parent / "data"

# ONS uses generalised (20m) clipped boundaries for reasonable file sizes.
# Senedd 2026 boundaries come from DataMapWales (not ONS).
DATASETS: dict[str, str] = {
    "unitary": (
        "https://services1.arcgis.com/ESMARspQHYMw9BZ9/arcgis/rest/services/"
        "Counties_and_Unitary_Authorities_December_2024_Boundaries_UK_BGC/"
        "FeatureServer/0/query?where=CTYUA24CD%20LIKE%20%27W%25%27"
        "&outFields=*&outSR=4326&f=geojson"
    ),
    "senedd": (
        "https://datamap.gov.wales/geoserver/geonode/ows?"
        "service=WFS&version=1.0.0&request=GetFeature"
        "&typeName=geonode:senedd_final_2026&outputFormat=application/json"
        "&srsName=EPSG:4326"
    ),
    "westminster": (
        "https://services1.arcgis.com/ESMARspQHYMw9BZ9/arcgis/rest/services/"
        "Westminster_Parliamentary_Constituencies_July_2024_Boundaries_UK_BGC/"
        "FeatureServer/0/query?where=PCON24CD%20LIKE%20%27W%25%27"
        "&outFields=*&outSR=4326&f=geojson"
    ),
}


def get_cached_path(dataset: str, data_dir: Path = DATA_DIR) -> Path:
    """Return the local cache path for a dataset."""
    return data_dir / f"{dataset}.geojson"


def download_boundaries(
    dataset: str,
    data_dir: Path = DATA_DIR,
) -> dict[str, object]:
    """Download boundary GeoJSON, using local cache if available.

    Args:
        dataset: One of 'unitary', 'senedd', 'westminster'.
        data_dir: Directory for cached files.

    Returns:
        Parsed GeoJSON dict.

    Raises:
        KeyError: If dataset name is not recognised.
    """
    url = DATASETS[dataset]
    cache_path = get_cached_path(dataset, data_dir)

    if cache_path.exists():
        return json.loads(cache_path.read_text(encoding="utf-8"))

    data_dir.mkdir(parents=True, exist_ok=True)
    response = requests.get(url, timeout=60)
    response.raise_for_status()
    geojson = response.json()

    cache_path.write_text(json.dumps(geojson), encoding="utf-8")
    return geojson
