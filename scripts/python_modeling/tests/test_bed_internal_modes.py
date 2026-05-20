# testes modos cilindro interno
from __future__ import annotations

import json
import sys
from pathlib import Path

import pytest

_PM = Path(__file__).resolve().parents[1]
if str(_PM) not in sys.path:
    sys.path.insert(0, str(_PM))

from bed_internal_modes import (  # noqa: E402
    MODE_HOLLOW_BOOLEAN,
    MODE_SOLID_HOLES,
    MODE_VISIBLE_INNER,
    build_boolean_operation_status,
    normalize_internal_cylinder_mode,
    resolve_bed_internal_config,
    validate_bed_geometry_mode,
)
from bed_shell_build import build_bed_shell  # noqa: E402
from geometry_modes import GEOMETRY_STATISTICAL  # noqa: E402
from pure_generation import generate_packed_bed_stl, load_bed_json  # noqa: E402

_SCRIPTS = Path(__file__).resolve().parents[2] / "blender_scripts"
if str(_SCRIPTS) not in sys.path:
    sys.path.insert(0, str(_SCRIPTS))
from packed_bed_science.geometry_math import AnnulusBedDomain  # noqa: E402
from packed_bed_science.packing_hexagonal import generate_hexagonal_packing  # noqa: E402

_TEMPLATES = Path(__file__).resolve().parents[3] / "dsl" / "wizard_templates"


def _load(name: str) -> dict:
    return json.loads((_TEMPLATES / name).read_text(encoding="utf-8"))


def test_normalize_modes():
    assert normalize_internal_cylinder_mode("m2") == MODE_VISIBLE_INNER
    assert normalize_internal_cylinder_mode(None) == MODE_HOLLOW_BOOLEAN
    assert normalize_internal_cylinder_mode("solid_holes") == MODE_SOLID_HOLES


def test_m2_visibility_defaults():
    mode, vis, _ = resolve_bed_internal_config(
        {"bed": {"internal_cylinder_mode": MODE_VISIBLE_INNER}}
    )
    assert mode == MODE_VISIBLE_INNER
    assert vis["show_internal_cylinder"] is True


def test_m2_shell_has_components():
    v, f, meta = build_bed_shell(
        MODE_VISIBLE_INNER,
        0.025,
        0.023,
        0.1,
        {
            "show_outer_cylinder": True,
            "show_internal_cylinder": True,
            "show_particles": True,
            "show_boolean_tools": False,
            "export_boolean_tools": False,
        },
        segmentos=16,
        bottom_cap_thickness=0.003,
        top_cap_thickness=0.003,
    )
    assert len(v) > 0
    assert "inner_cylinder_visible" in meta.get("shell_components", [])
    st = meta["boolean_operation_status"]
    assert st["outer_shell"] == "fallback_separate_meshes"
    assert st["inner_core"] == "visible_separate"


def test_statistical_ignores_mode_warning():
    notes = validate_bed_geometry_mode(
        {"bed": {"internal_cylinder_mode": MODE_VISIBLE_INNER}},
        GEOMETRY_STATISTICAL,
    )
    assert any("ignorado" in n for n in notes)


def _annulus_from_fixture(data: dict) -> AnnulusBedDomain:
    bed = data["bed"]
    r_ext = float(bed["diameter"]) / 2.0
    r_int = r_ext - float(bed["wall_thickness"])
    lids = data.get("lids") or {}
    pd = float((data.get("particles") or {}).get("diameter", 0.002))
    gap = float((data.get("packing") or {}).get("gap", 0.0001))
    return AnnulusBedDomain(
        r_int=r_int,
        r_ext=r_ext,
        height=float(bed["height"]),
        bottom_cap_thickness=float(lids.get("bottom_thickness", 0.003)),
        top_cap_thickness=float(lids.get("top_thickness", 0.003)),
        r_sphere=pd / 2.0,
        gap=gap,
    )


def test_packing_invariant_all_modes():
    base = _load("_test_bed_m1_hollow_boolean.json")
    ann = _annulus_from_fixture(base)
    r_pack = 0.001
    centers_ref = generate_hexagonal_packing(ann, 15, r_pack, 0.0001)["centers"]
    for fixture, mode in (
        ("_test_bed_m1_hollow_boolean.json", MODE_HOLLOW_BOOLEAN),
        ("_test_bed_m2_visible_inner.json", MODE_VISIBLE_INNER),
        ("_test_bed_m3_solid_holes.json", MODE_SOLID_HOLES),
    ):
        data = _load(fixture)
        centers = generate_hexagonal_packing(
            _annulus_from_fixture(data), 15, r_pack, 0.0001
        )["centers"]
        assert len(centers) == len(centers_ref)
        assert data["bed"]["internal_cylinder_mode"] == mode


@pytest.mark.parametrize("fixture", ["_test_bed_m1_hollow_boolean.json", "_test_bed_m2_visible_inner.json"])
def test_python_export_sidecar(tmp_path, fixture):
    fx = _TEMPLATES / fixture
    out = tmp_path / "bed.stl"
    generate_packed_bed_stl(fx, out)
    sidecar = tmp_path / "bed_pure_bed.json"
    assert sidecar.is_file()
    meta = json.loads(sidecar.read_text(encoding="utf-8"))
    assert "internal_cylinder_mode" in meta
    assert "boolean_operation_status" in meta
    assert meta["boolean_operation_status"]["backend"] == "python_engine"
    if fixture.endswith("m2_visible_inner.json"):
        assert meta["boolean_operation_status"]["outer_shell"] == "fallback_separate_meshes"


def test_m1_stl_vertex_count():
    v, f, meta = build_bed_shell(
        MODE_HOLLOW_BOOLEAN,
        0.025,
        0.023,
        0.1,
        {
            "show_outer_cylinder": True,
            "show_internal_cylinder": False,
            "show_particles": True,
            "show_boolean_tools": False,
            "export_boolean_tools": False,
        },
        segmentos=24,
    )
    assert len(v) >= 24 * 4
    assert meta["boolean_operation_status"]["outer_shell"] == "explicit_annulus"


def test_boolean_status_builder():
    st = build_boolean_operation_status(MODE_HOLLOW_BOOLEAN, backend="blender")
    assert st["outer_shell"] == "applied"
    assert st["inner_core"] == "n/a"
