# testes de revisao: combinacoes geometry_mode + packing
from __future__ import annotations

import json
import sys
import tempfile
from pathlib import Path

import pytest

_PM = Path(__file__).resolve().parents[1]
_ROOT = _PM.parents[1]
_TEMPLATES = _ROOT / "dsl" / "wizard_templates"
if str(_PM) not in sys.path:
    sys.path.insert(0, str(_PM))

from geometry_modes import geometry_mode_from_data, resolve_slice_config
from pure_generation import load_bed_json, generate_packed_bed_stl


@pytest.mark.parametrize(
    "fixture",
    [
        "_test_spherical_python.json",
        "_test_hexagonal_python.json",
        "_test_dem_python.json",
        "_test_pseudo2d_slice.json",
        "_test_pseudo2d_statistical.json",
    ],
)
def test_fixture_generates_stl(fixture: str):
    path = _TEMPLATES / fixture
    if not path.is_file():
        pytest.skip(f"fixture ausente: {fixture}")
    with tempfile.TemporaryDirectory() as td:
        out = Path(td) / "out.stl"
        generate_packed_bed_stl(path, out)
        assert out.stat().st_size > 500
        side = Path(td) / "out_pure_bed.json"
        assert side.is_file()


def test_thin_slice_resolve_without_slice_enabled_flag():
    data = {
        "geometry_mode": "pseudo_2d_thin_slice",
        "slice": {"slice_axis": "y", "slice_thickness": 0.002},
    }
    assert geometry_mode_from_data(data) == "pseudo_2d_thin_slice"
    sl = resolve_slice_config(data)
    assert sl.get("slice_enabled") is True


def test_load_bed_json_propagates_geometry():
    path = _TEMPLATES / "_test_pseudo2d_slice.json"
    if not path.is_file():
        pytest.skip("fixture slice ausente")
    p = load_bed_json(path)
    assert p["geometry_mode"] == "pseudo_2d_thin_slice"
    assert p.get("slice", {}).get("slice_enabled") is True
