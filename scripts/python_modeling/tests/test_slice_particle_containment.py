# testes de contenção radial/slice para pseudo-2d thin slice
from __future__ import annotations

import math
import sys
from pathlib import Path

import pytest

_PM = Path(__file__).resolve().parents[1]
if str(_PM) not in sys.path:
    sys.path.insert(0, str(_PM))

from bed_reference_frame import BedReferenceFrame, frame_from_slice_cfg  # noqa: E402
from geometry_modes import (  # noqa: E402
    SLICE_POLICY_CONTAINED,
    SLICE_POLICY_INTERSECTING,
    footprint_vertices_leak_util,
    particle_passes_policy,
    particle_slice_metrics,
    resolve_slice_config,
)
from thin_slice_build import apply_thin_slice_mesh  # noqa: E402

R_INT = 0.02
R_EXT = 0.025
HEIGHT = 0.1
D_PART = 0.004
R_EQ = D_PART * 0.5


def _fixture_wall_center() -> tuple:
    """centro perto da parede no plano xy; pegada radial vaza; contained remove."""
    rho_target = R_INT - 0.5 * R_EQ
    return (rho_target, 0.0, HEIGHT * 0.5)


def _fixture_slice_edge_center() -> tuple:
    half = 0.001
    s_center = 0.05
    return (0.0, s_center + half - 0.6 * R_EQ, 0.05)


def test_resolve_slice_config_default_contained():
    data = {"geometry_mode": "pseudo_2d_thin_slice", "slice": {"slice_axis": "y"}}
    cfg = resolve_slice_config(data)
    assert cfg.get("slice_particle_policy") == SLICE_POLICY_CONTAINED
    assert cfg.get("slice_enabled") is True


def test_fixture_wall_contained_rejects():
    center = _fixture_wall_center()
    frame = BedReferenceFrame(
        r_util=R_INT,
        r_ext=R_EXT,
        height=HEIGHT,
        slice_axis="y",
        slice_center=0.0,
        slice_thickness=0.002,
        slice_particle_policy=SLICE_POLICY_CONTAINED,
    )
    assert not particle_passes_policy(
        center,
        particle_kind="sphere",
        particle_diameter=D_PART,
        slice_axis=frame.slice_axis,
        slice_center=frame.slice_center,
        slice_thickness=frame.slice_thickness,
        r_util=frame.r_util,
        policy=SLICE_POLICY_CONTAINED,
    )
    m = particle_slice_metrics(
        center,
        particle_kind="sphere",
        particle_diameter=D_PART,
        slice_axis="y",
        slice_center=0.0,
        slice_thickness=0.002,
        r_util=R_INT,
    )
    assert m["passes_legacy_slice_only"] or m["passes_intersecting_slice"]
    assert m["leak_footprint_legacy"]


def test_fixture_slice_edge_contained_rejects():
    center = _fixture_slice_edge_center()
    assert not particle_passes_policy(
        center,
        particle_kind="sphere",
        particle_diameter=D_PART,
        slice_axis="y",
        slice_center=0.05,
        slice_thickness=0.002,
        r_util=R_INT,
        policy=SLICE_POLICY_CONTAINED,
    )


def test_fixture_wall_intersecting_accepts():
    center = _fixture_wall_center()
    assert particle_passes_policy(
        center,
        particle_kind="sphere",
        particle_diameter=D_PART,
        slice_axis="y",
        slice_center=0.0,
        slice_thickness=0.002,
        r_util=R_INT,
        policy=SLICE_POLICY_INTERSECTING,
    )


def test_apply_thin_slice_mesh_leak_count_zero_contained():
    slice_cfg = {
        "slice_enabled": True,
        "slice_axis": "y",
        "slice_position": 0.0,
        "slice_thickness": 0.005,
        "slice_particle_policy": SLICE_POLICY_CONTAINED,
        "keep_only_intersecting_particles": True,
        "preserve_original_packing": True,
    }
    centers = [_fixture_wall_center(), (0.01, 0.0, 0.05)]
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
    assert summary["n_dropped_policy"] >= 1
    assert summary["n_kept"] >= 1


def test_apply_thin_slice_intersecting_clips_or_drops():
    slice_cfg = {
        "slice_enabled": True,
        "slice_axis": "y",
        "slice_position": 0.0,
        "slice_thickness": 0.005,
        "slice_particle_policy": SLICE_POLICY_INTERSECTING,
        "keep_only_intersecting_particles": True,
    }
    centers = [(0.01, 0.0, 0.05)]
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
    if v:
        assert not footprint_vertices_leak_util(
            v,
            r_util=R_INT,
            slice_axis="y",
            slice_center=0.0,
            slice_thickness=0.005,
        )
    assert summary["n_kept"] >= 1


def test_frame_from_slice_cfg_policy():
    cfg = frame_from_slice_cfg(
        {"slice_particle_policy": "intersecting", "slice_axis": "z"},
        r_int=R_INT,
        r_ext=R_EXT,
        height=HEIGHT,
    )
    assert cfg.slice_particle_policy == SLICE_POLICY_INTERSECTING
    assert cfg.slice_axis == "z"
    c = (0.01, 0.02, 0.05)
    assert math.isclose(cfg.rho_from_center(c), math.hypot(0.01, 0.02), rel_tol=1e-6)
