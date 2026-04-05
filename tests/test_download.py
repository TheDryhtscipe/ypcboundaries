import json
import os
from pathlib import Path
from unittest.mock import patch, MagicMock

from download import DATASETS, download_boundaries, get_cached_path


def test_datasets_has_three_entries():
    assert len(DATASETS) == 3
    assert "unitary" in DATASETS
    assert "senedd" in DATASETS
    assert "westminster" in DATASETS


def test_get_cached_path():
    path = get_cached_path("unitary", data_dir=Path("/tmp/test_data"))
    assert path == Path("/tmp/test_data/unitary.geojson")


def test_download_uses_cache_when_file_exists(tmp_path):
    cache_file = tmp_path / "unitary.geojson"
    fake_geojson = {"type": "FeatureCollection", "features": []}
    cache_file.write_text(json.dumps(fake_geojson))

    with patch("download.requests") as mock_requests:
        result = download_boundaries("unitary", data_dir=tmp_path)
        mock_requests.get.assert_not_called()

    assert result == fake_geojson


def test_download_fetches_when_no_cache(tmp_path):
    fake_geojson = {"type": "FeatureCollection", "features": [{"type": "Feature"}]}

    with patch("download.requests") as mock_requests:
        mock_response = MagicMock()
        mock_response.json.return_value = fake_geojson
        mock_response.raise_for_status = MagicMock()
        mock_requests.get.return_value = mock_response

        result = download_boundaries("unitary", data_dir=tmp_path)

    assert result == fake_geojson
    assert (tmp_path / "unitary.geojson").exists()


def test_download_raises_for_unknown_dataset(tmp_path):
    import pytest
    with pytest.raises(KeyError):
        download_boundaries("nonexistent", data_dir=tmp_path)
