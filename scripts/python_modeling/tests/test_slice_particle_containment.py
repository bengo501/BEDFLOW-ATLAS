# testes de contenção radial/slice para pseudo-2d thin slice
from __future__ import annotations

import math
import sys
from pathlib import Path

import pytest

_PM = Path(__file__).resolve().parents[1]
if str(_PM) not in sys.path:
    sys.path.insert(0, str(_PM))

from bed_reference_frame import frame_from_slice_cfg  # noqa: E402
from geometry_modes import (  # noqa: E402
    DEFAULT_SLICE_THICKNESS,
    SLICE_POLICY_CONTAINED,
    axis_index,
    particle_passes_policy,
    resolve_slice_config,
    rho_from_center_xy,
    snap_center_radial_to_util_wall,
)
from thin_slice_build import apply_thin_slice_mesh  # noqa: E402
from thin_slice_particles import align_center_to_slice_plane  # noqa: E402

R_INT = 0.02
R_EXT = 0.025
HEIGHT = 0.1
D_PART = 0.004
R_EQ = D_PART * 0.5
THICK = 0.002


def _fixture_wall_center() -> tuple:
    rho_target = R_INT + 0.5 * R_EQ
    return (rho_target, 0.0, HEIGHT * 0.5)


def _fixture_slice_edge_center() -> tuple:
    """centro fora da faixa no eixo y (não intersecta a lâmina)."""
    half = THICK / 2.0
    return (0.0, half + R_EQ + 0.001, 0.05)


def _max_extent_on_axis(vertices, axis: str) -> float:
    ai = axis_index(axis)
    vals = [p[ai] for p in vertices]
    return max(vals) - min(vals)


def test_resolve_slice_config_uses_user_thickness():
    data = {
        "geometry_mode": "pseudo_2d_thin_slice",
        "bed": {"height": 0.12, "diameter": 0.05},
        "slice": {"slice_axis": "y", "slice_thickness": 0.001},
    }
    cfg = resolve_slice_config(data)
    assert cfg.get("slice_thickness") == pytest.approx(0.001)
    assert cfg.get("min_slice_particle_radius") == pytest.approx(1e-5)
    assert "particle_bed_height" not in cfg


def test_resolve_slice_default_thickness():
    cfg = resolve_slice_config({"geometry_mode": "pseudo_2d_thin_slice"})
    assert cfg["slice_thickness"] == pytest.approx(DEFAULT_SLICE_THICKNESS)


def test_snap_center_to_util_wall():
    c = (0.03, 0.0, 0.05)
    s = snap_center_radial_to_util_wall(c, R_INT, R_EQ)
    assert rho_from_center_xy(s) <= R_INT - R_EQ + 1e-9


def test_align_on_slice_plane():
    c = align_center_to_slice_plane(
        (0.03, 0.15, 0.05),
        slice_axis="y",
        slice_position=0.0,
        preserve_original_packing=True,
    )
    assert c[1] == pytest.approx(0.0)
    assert c[0] == pytest.approx(0.03)


def test_fixture_slice_edge_outside_plane_drops():
    center = _fixture_slice_edge_center()
    assert not particle_passes_policy(
        center,
        particle_kind="sphere",
        particle_diameter=D_PART,
        slice_axis="y",
        slice_center=0.0,
        slice_thickness=THICK,
        r_util=R_INT,
        policy=SLICE_POLICY_CONTAINED,
    )


def test_apply_thin_slice_mesh_discs_not_columns():
    slice_cfg = resolve_slice_config(
        {
            "geometry_mode": "pseudo_2d_thin_slice",
            "bed": {"height": HEIGHT, "diameter": 0.05},
            "slice": {"slice_axis": "y", "slice_position": 0.0, "slice_thickness": THICK},
        }
    )
    centers = [(0.01, 0.0, 0.05), (0.0, 0.0, 0.04)]
    v, f, summary = apply_thin_slice_mesh(
        [],
        [],
        centers,
        particle_diameter=D_PART,
        particle_kind="sphere",
        r_ext=R_EXT,
        r_int=R_INT,
        slice_cfg=slice_cfg,
        segmentos=16,
    )
    assert summary["leak_count"] == 0
    assert summary["n_kept"] >= 1
    assert summary["slice_thickness"] == pytest.approx(THICK)
    if v:
        assert _max_extent_on_axis(v, "y") <= THICK + 1e-5


def test_frame_from_slice_cfg_policy():
    cfg = frame_from_slice_cfg(
        {"slice_particle_policy": "intersecting", "slice_axis": "z", "slice_thickness": THICK},
        r_int=R_INT,
        r_ext=R_EXT,
        height=HEIGHT,
    )
    assert cfg.slice_particle_policy == "intersecting"
    c = (0.01, 0.02, 0.05)
    assert math.isclose(cfg.rho_from_center(c), math.hypot(0.01, 0.02), rel_tol=1e-6)
