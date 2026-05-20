# smoke: blender consegue importar geometry_modes (paridade com leito_extracao)
# executar: blender --background --python scripts/blender_scripts/smoke_thin_slice.py
from __future__ import annotations

import sys
from pathlib import Path

_pm = Path(__file__).resolve().parents[1] / "python_modeling"
if str(_pm) not in sys.path:
    sys.path.insert(0, str(_pm))

from geometry_modes import (  # noqa: E402
    particle_intersects_slice,
    slice_footprint_spec,
    validate_geometry_contract,
)

data = {
    "geometry_mode": "pseudo_2d_thin_slice",
    "slice": {"slice_enabled": True, "slice_axis": "y", "slice_thickness": 0.002},
    "statistical_2d": {"target_porosity": 0.4},
}
gm, notes = validate_geometry_contract(data, mutate=True)
assert gm == "pseudo_2d_thin_slice"
assert "statistical_2d" not in data
assert particle_intersects_slice(
    (0.0, 0.0, 0.0),
    particle_kind="sphere",
    particle_diameter=0.01,
    axis="y",
    slice_position=0.0,
    slice_thickness=0.002,
)
spec = slice_footprint_spec("cube", 0.01, 0.0, slice_axis="y", slice_thickness=0.002)
assert spec.get("shape") == "box"
print("BEDFLOW_THIN_SLICE_SMOKE_OK", notes)
