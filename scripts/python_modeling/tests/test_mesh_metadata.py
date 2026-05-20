import json
import sys
from pathlib import Path

import pytest

_ROOT = Path(__file__).resolve().parents[3]
if str(_ROOT) not in sys.path:
    sys.path.insert(0, str(_ROOT))

from bedflow_mesh_metadata import load_mesh_geometry_metadata  # noqa: E402


def test_load_sidecar_pure_bed(tmp_path):
    stl = tmp_path / "leito_pure.stl"
    stl.write_bytes(b"x" * 80)
    sidecar = tmp_path / "leito_pure_bed.json"
    sidecar.write_text(
        json.dumps(
            {
                "geometry_mode": "pseudo_2d_thin_slice",
                "generation_backend": "python_engine",
                "porosity_target": 0.4,
                "porosity_result": 0.38,
                "slice": {
                    "slice_axis": "y",
                    "slice_thickness": 0.002,
                    "slice_position": 0.0,
                },
            }
        ),
        encoding="utf-8",
    )
    meta = load_mesh_geometry_metadata(stl)
    assert meta["geometry_mode"] == "pseudo_2d_thin_slice"
    assert meta["slice_axis"] == "y"
    assert abs(meta["slice_thickness"] - 0.002) < 1e-9
    assert meta["sidecar_json"] == "leito_pure_bed.json"
