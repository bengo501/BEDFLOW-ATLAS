# testes do algoritmo unificado thin slice (discos no eixo do corte)
from __future__ import annotations

import math
import sys
from pathlib import Path

import pytest

_PM = Path(__file__).resolve().parents[1]
if str(_PM) not in sys.path:
    sys.path.insert(0, str(_PM))

from geometry_modes import axis_index, resolve_slice_config  # noqa: E402
from stl_mesh_utils import cylinder_axis  # noqa: E402
from thin_slice_particles import (  # noqa: E402
    SliceParticleConfig,
    align_center_to_slice_plane,
    compute_slice_radius,
    create_slice_cylinder_mesh,
    process_slice_particles,
    sphere_intersects_slice,
    validate_slice_particle_vertices,
)

R_INT = 0.02
THICK = 0.002
D_PART = 0.004
R_EQ = D_PART * 0.5


def _cfg(axis: str = "y", pos: float = 0.0, thick: float = THICK) -> SliceParticleConfig:
    return SliceParticleConfig(
        slice_axis=axis,
        slice_position=pos,
        slice_thickness=thick,
        min_slice_particle_radius=1e-5,
        r_util=R_INT,
    )


def _max_extent_on_axis(vertices, axis: str) -> float:
    ai = axis_index(axis)
    vals = [p[ai] for p in vertices]
    return max(vals) - min(vals)


def test_center_on_plane_full_radius():
    center = (0.0, 0.0, 0.0)
    r_app = compute_slice_radius("sphere", D_PART, 0.0, slice_axis="y")
    assert r_app == pytest.approx(R_EQ, rel=1e-6)
    cfg = _cfg("y", 0.0)
    sv, sf, meta = create_slice_cylinder_mesh("sphere", center, D_PART, cfg=cfg)
    assert meta["included"]
    assert _max_extent_on_axis(sv, "y") <= THICK + 1e-6


def test_offset_smaller_radius():
    d_plane = 0.001
    r_app = compute_slice_radius("sphere", D_PART, d_plane, slice_axis="y")
    expected = math.sqrt(R_EQ * R_EQ - d_plane * d_plane)
    assert r_app == pytest.approx(expected, rel=1e-5)
    assert r_app < R_EQ


def test_outside_slab_excluded():
    center = (0.0, 0.05, 0.0)
    assert not sphere_intersects_slice(
        center,
        particle_kind="sphere",
        particle_diameter=D_PART,
        slice_axis="y",
        slice_position=0.0,
        slice_thickness=THICK,
    )


@pytest.mark.parametrize("axis", ["x", "y", "z"])
def test_disc_extent_along_slice_axis(axis: str):
    ai = axis_index(axis)
    c = [0.0, 0.0, 0.0]
    c[ai] = 0.001
    cfg = _cfg(axis, 0.0)
    sv, _, meta = create_slice_cylinder_mesh("sphere", tuple(c), D_PART, cfg=cfg)
    assert meta["included"]
    assert _max_extent_on_axis(sv, axis) <= THICK + 1e-6


def test_below_min_radius_discarded():
    cfg = SliceParticleConfig(
        slice_axis="y",
        slice_position=0.0,
        slice_thickness=THICK,
        min_slice_particle_radius=R_EQ + 0.001,
        r_util=R_INT,
    )
    sv, _, meta = create_slice_cylinder_mesh("sphere", (0.0, 0.0, 0.0), D_PART, cfg=cfg)
    assert not sv
    assert meta.get("reason") == "below_min_radius"


def test_resolve_slice_config_respects_user_thickness():
    data = {
        "geometry_mode": "pseudo_2d_thin_slice",
        "slice": {"slice_axis": "y", "slice_thickness": 0.005},
    }
    cfg = resolve_slice_config(data)
    assert cfg["slice_thickness"] == pytest.approx(0.005)
    assert "particle_bed_height" not in cfg


def test_shell_and_particle_same_thickness_in_config():
    data = {
        "geometry_mode": "pseudo_2d_thin_slice",
        "slice": {"slice_thickness": 0.003, "min_slice_particle_radius": 1e-6},
    }
    cfg = resolve_slice_config(data)
    assert cfg["slice_thickness"] == pytest.approx(0.003)
    assert cfg["min_slice_particle_radius"] == pytest.approx(1e-6)


def test_align_center_to_slice_plane_preserves_when_true():
    c = align_center_to_slice_plane(
        (0.1, 0.2, 0.3),
        slice_axis="y",
        slice_position=0.0,
        preserve_original_packing=True,
    )
    assert c[1] == pytest.approx(0.0)
    assert c[0] == pytest.approx(0.1)
    assert c[2] == pytest.approx(0.3)


def test_align_center_to_slice_plane_snaps_when_false():
    c = align_center_to_slice_plane(
        (0.1, 0.2, 0.3),
        slice_axis="y",
        slice_position=0.0,
        preserve_original_packing=False,
    )
    assert c[1] == pytest.approx(0.2)
    assert c[0] == pytest.approx(0.1)
    assert c[2] == pytest.approx(0.3)


def test_process_slice_particles_summary():
    centers = [(0.0, 0.0, 0.0), (0.0, 0.02, 0.0)]
    _, _, summary = process_slice_particles(
        centers,
        particle_kind="sphere",
        particle_diameter=D_PART,
        cfg=_cfg(),
    )
    assert summary["n_kept"] >= 1
    assert summary["slice_thickness"] == pytest.approx(THICK)
    assert validate_slice_particle_vertices(
        [(0.0, 0.0, 0.0)],
        slice_axis="y",
        slice_position=0.0,
        slice_thickness=THICK,
    )
