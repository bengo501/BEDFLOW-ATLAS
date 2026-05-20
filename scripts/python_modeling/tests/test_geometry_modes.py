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
    validate_geometry_contract,
    collision_radius_for_particle_kind,
    compute_global_porosity_2d,
    compute_global_porosity_2d_formula,
    compute_global_porosity_2d_raster,
    geometry_mode_from_data,
    particle_intersects_slice,
    resolve_slice_config,
    resolve_statistical_config,
    slice_footprint_spec,
    sphere_section_radius,
)


def test_geometry_mode_from_slice_fallback():
    data = {"slice": {"slice_enabled": True, "slice_axis": "y"}}
    assert geometry_mode_from_data(data) == GEOMETRY_THIN_SLICE


def test_validate_contract_infers_statistical():
    data = {"geometry_mode": "full_3d", "statistical_2d": {"target_porosity": 0.4}}
    gm, _ = validate_geometry_contract(data, mutate=True)
    assert gm == GEOMETRY_STATISTICAL
    assert data["geometry_mode"] == GEOMETRY_STATISTICAL


def test_resolve_slice_forces_enabled():
    data = {"geometry_mode": GEOMETRY_THIN_SLICE, "slice": {"slice_axis": "z"}}
    sl = resolve_slice_config(data)
    assert sl["slice_enabled"] is True
    assert sl["slice_axis"] == "z"


def test_particle_intersects_slice_sphere():
    d = 0.01
    assert particle_intersects_slice(
        (0.0, 0.0, 0.0),
        particle_kind="sphere",
        particle_diameter=d,
        axis="y",
        slice_position=0.0,
        slice_thickness=0.002,
    )
    assert not particle_intersects_slice(
        (0.0, 0.1, 0.0),
        particle_kind="sphere",
        particle_diameter=d,
        axis="y",
        slice_position=0.0,
        slice_thickness=0.002,
    )


def test_particle_intersects_slice_cube_uses_circumscribed_radius():
    d = 0.01
    r_eq = collision_radius_for_particle_kind("cube", d)
    # centro perto do plano: esfera nao intersecta; cubo (raio maior) intersecta
    assert not particle_intersects_slice(
        (0.0, 0.007, 0.0),
        particle_kind="sphere",
        particle_diameter=d,
        axis="y",
        slice_position=0.0,
        slice_thickness=0.002,
    )
    assert particle_intersects_slice(
        (0.0, 0.007, 0.0),
        particle_kind="cube",
        particle_diameter=d,
        axis="y",
        slice_position=0.0,
        slice_thickness=0.002,
    )
    assert r_eq > d * 0.5


def test_slice_footprint_cube_is_box_not_disc():
    spec = slice_footprint_spec("cube", 0.01, 0.0, slice_axis="y", slice_thickness=0.002)
    assert spec["shape"] == "box"
    assert spec["size_x"] == 0.01
    assert spec["size_y"] == 0.002


def test_slice_footprint_cylinder_disc_on_z_axis():
    spec = slice_footprint_spec(
        "cylinder", 0.01, 0.0, slice_axis="z", slice_thickness=0.002
    )
    assert spec["shape"] == "disc"
    assert abs(spec["radius"] - 0.005) < 1e-9


def test_slice_footprint_cylinder_box_on_y_axis():
    spec = slice_footprint_spec(
        "cylinder", 0.01, 0.0, slice_axis="y", slice_thickness=0.002
    )
    assert spec["shape"] == "box"
    assert spec["size_y"] == 0.002


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


def test_porosity_raster_handles_overlap():
    r = 0.005
    w, h = 0.05, 0.05
    # discos sobrepostos (distancia < 2r): formula conta area em dobro
    c1 = (0.02, 0.025)
    c2 = (0.02 + 1.5 * r, 0.025)
    p_formula = compute_global_porosity_2d_formula([c1, c2], r, w, h)
    p_raster, meta = compute_global_porosity_2d_raster([c1, c2], r, w, h)
    assert meta["porosity_method"] == "raster"
    assert p_raster > p_formula
