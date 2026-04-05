#!/usr/bin/env python3
"""Generate interactive Wales boundary map.

Downloads boundary GeoJSON (caching locally in data/) and produces
a self-contained HTML map in output/.
"""

from pathlib import Path

from download import DATASETS, download_boundaries
from map_builder import build_map

OUTPUT_DIR = Path(__file__).parent / "output"


def main() -> None:
    print("Downloading boundary data...")
    boundary_data: dict[str, dict[str, object]] = {}
    for dataset in DATASETS:
        print(f"  {dataset}...", end=" ", flush=True)
        boundary_data[dataset] = download_boundaries(dataset)
        n = len(boundary_data[dataset].get("features", []))
        print(f"{n} boundaries")

    print("Building map...")
    m = build_map(boundary_data)

    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
    output_path = OUTPUT_DIR / "wales_boundaries.html"
    m.save(str(output_path))
    print(f"Map saved to {output_path}")


if __name__ == "__main__":
    main()
