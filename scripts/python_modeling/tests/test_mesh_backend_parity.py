# paridade empacotamento + thin slice entre contratos python/blender
from __future__ import annotations

import json
import sys
from pathlib import Path

import pytest

_PM = Path(__file__).resolve().parents[1]
_SCRIPTS = _PM.parent / "blender_scripts"
if str(_PM) not in sys.path:
    sys.path.insert(0, str(_PM))
if str(_SCRIPTS) not in sys.path:
    sys.path.insert(0, str(_SCRIPTS))

from bed_internal_modes import MODE_SOLID_HOLES  # noqa: E402
from packed_bed_science.geometry_math import AnnulusBedDomain  # noqa: E402
from packed_bed_science.packing_spherical import generate_spherical_packing  # noqa: E402
from thin_slice_build import apply_thin_slice_mesh  # noqa: E402
from thin_slice_particles import prepare_slice_particle_for_mesh, SliceParticleConfig  # noqa: E402
from pure_bed_mesh import build_packed_bed_model  # noqa: E402
from pure_generation import generate_packed_bed_stl  # noqa: E402

_TEMPLATES = Path(__file__).resolve().parents[3] / "dsl" / "wizard_templates"


def _annulus():
    return AnnulusBedDomain(
        r_int=0.023,
        r_ext=0.025,
        height=0.1,
        bottom_cap_thickness=0.003,
        top_cap_thickness=0.003,
        r_sphere=0.0025,
        gap=0.0001,
    )


def test_packing_same_seed_same_centers():
    ann = _annulus()
    a = generate_spherical_packing(ann, 20, 0.0025, 0.0001, random_seed=777)["centers"]
    b = generate_spherical_packing(ann, 20, 0.0025, 0.0001, random_seed=777)["centers"]
    assert a == b


def test_prepare_slice_matches_filter_count():
    ann = _annulus()
    centers = generate_spherical_packing(ann, 50, 0.0025, 0.0001, random_seed=42)["centers"]
    slice_cfg = {
        "slice_enabled": True,
        "slice_axis": "y",
        "slice_position": 0.0,
        "slice_thickness": 0.002,
        "preserve_original_packing": True,
    }
    shell = build_packed_bed_model(
        0.025, 0.023, 0.1, 0.003, 0.003, [], 0.005, "sphere", bed_config={"bed": {}}
    )
    _, _, summary = apply_thin_slice_mesh(
        shell.mesh.vertices,
        shell.mesh.faces,
        centers,
        particle_diameter=0.005,
        particle_kind="sphere",
        r_ext=0.025,
        r_int=0.023,
        slice_cfg=slice_cfg,
        segmentos=16,
    )
    pcfg = SliceParticleConfig.from_slice_cfg(slice_cfg, r_int=0.023)
    manual_kept = 0
    for c in centers:
        loc, _, meta = prepare_slice_particle_for_mesh(
            c, "sphere", 0.005, cfg=pcfg, policy="contained"
        )
        if loc is not None:
            manual_kept += 1
    assert summary["n_kept"] == manual_kept


def test_solid_holes_python_metadata_contract(tmp_path):
    from bed_shell_build import build_bed_with_internal_mode

    data = {
        "bed": {
            "internal_cylinder_mode": MODE_SOLID_HOLES,
            "visibility": {"show_internal_cylinder": True, "show_particles": False},
        }
    }
    centers = [(0.01, 0.0, 0.05), (0.0, 0.0, 0.04), (-0.008, 0.0, 0.06)]
    v, f, meta = build_bed_with_internal_mode(
        data,
        0.025,
        0.023,
        0.1,
        0.003,
        0.003,
        centers,
        0.004,
        "sphere",
        segmentos=12,
    )
    assert len(v) > 0
    assert meta.get("internal_cylinder_mode") == MODE_SOLID_HOLES
    st = meta.get("boolean_operation_status") or {}
    assert st.get("particle_tools") in ("applied", "failed", "n/a")
