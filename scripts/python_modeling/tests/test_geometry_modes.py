import math
import sys
from pathlib import Path

import pytest

_PM = Path(__file__).resolve().parents[1]
if str(_PM) not in sys.path:
    sys.path.insert(0, str(_PM))

from geometry_modes import (  # noqa: E402
    GEOMETRY_STATISTICAL,
    GEOMETRY_THIN_SLICE,
    compute_global_porosity_2d,
    geometry_mode_from_data,
    particle_intersects_slice,
    resolve_slice_config,
    resolve_statistical_config,
    sphere_section_radius,
)


def test_geometry_mode_from_slice_fallback():
    data = {"slice": {"slice_enabled": True, "slice_axis": "y"}}
    assert geometry_mode_from_data(data) == GEOMETRY_THIN_SLICE


def test_resolve_slice_forces_enabled():
    data = {"geometry_mode": GEOMETRY_THIN_SLICE, "slice": {"slice_axis": "z"}}
    sl = resolve_slice_config(data)
    assert sl["slice_enabled"] is True
    assert sl["slice_axis"] == "z"


def test_particle_intersects_slice():
    assert particle_intersects_slice(
        (0.0, 0.0, 0.0),
        0.005,
        axis="y",
        slice_position=0.0,
        slice_thickness=0.002,
    )
    assert not particle_intersects_slice(
        (0.0, 0.1, 0.0),
        0.005,
        axis="y",
        slice_position=0.0,
        slice_thickness=0.002,
    )


def test_sphere_section_radius():
    r = 0.01
    d = 0.005
    rs = sphere_section_radius(r, d)
    assert abs(rs - math.sqrt(r * r - d * d)) < 1e-9


def test_statistical_config_resolve():
    data = {
        "geometry_mode": GEOMETRY_STATISTICAL,
        "statistical_2d": {"target_porosity": 0.4, "max_attempts": 10},
        "bed": {"diameter": 0.05, "height": 0.1},
        "particles": {"diameter": 0.004, "target_porosity": 0.42},
    }
    st = resolve_statistical_config(data)
    assert st["domain_width"] == 0.05
    assert st["target_porosity"] == 0.4  # statistical_2d block overrides particles


def test_global_porosity_2d():
    centers = [(0.01, 0.01), (0.03, 0.03)]
    p = compute_global_porosity_2d(centers, 0.005, 0.05, 0.05)
    assert 0.0 < p < 1.0
