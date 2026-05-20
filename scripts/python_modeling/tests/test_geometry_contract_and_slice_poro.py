import math
import os
import shutil
import subprocess
import sys
from pathlib import Path

import pytest

_PM = Path(__file__).resolve().parents[1]
_ROOT = _PM.parents[1]
if str(_PM) not in sys.path:
    sys.path.insert(0, str(_PM))

from geometry_modes import (  # noqa: E402
    GEOMETRY_STATISTICAL,
    GEOMETRY_THIN_SLICE,
    compute_thin_slice_porosity,
    geometry_mode_from_data,
    validate_geometry_contract,
)
from pure_generation import generate_packed_bed_stl  # noqa: E402


def test_validate_contract_thin_slice_drops_statistical():
    data = {
        "geometry_mode": GEOMETRY_THIN_SLICE,
        "slice": {"slice_enabled": True, "slice_axis": "y"},
        "statistical_2d": {"target_porosity": 0.4},
    }
    gm, notes = validate_geometry_contract(data, mutate=True)
    assert gm == GEOMETRY_THIN_SLICE
    assert "statistical_2d" not in data
    assert any("ignorado" in n for n in notes)


def test_validate_contract_strict_conflict():
    data = {
        "geometry_mode": GEOMETRY_STATISTICAL,
        "slice": {"slice_enabled": True},
        "statistical_2d": {"target_porosity": 0.4},
    }
    with pytest.raises(ValueError):
        validate_geometry_contract(data, strict=True, mutate=True)


def test_thin_slice_porosity_in_annulus():
    r_int, r_ext = 0.02, 0.025
    centers = [(0.0, 0.0, 0.0), (0.022, 0.0, 0.0)]
    p, meta = compute_thin_slice_porosity(
        centers,
        "sphere",
        0.004,
        slice_axis="y",
        slice_position=0.0,
        slice_thickness=0.002,
        r_int=r_int,
        r_ext=r_ext,
    )
    assert 0.0 <= p <= 1.0
    assert meta["porosity_method"] == "slice_raster"
    assert meta["n_particles_in_slice"] >= 1


def test_slice_fixture_exports_slice_porosity(tmp_path):
    fx = _ROOT / "dsl" / "wizard_templates" / "_test_pseudo2d_slice.json"
    if not fx.is_file():
        pytest.skip("fixture ausente")
    out = tmp_path / "slice.stl"
    generate_packed_bed_stl(fx, out, max_passos=300)
    sidecar = tmp_path / "slice_pure_bed.json"
    assert sidecar.is_file()
    import json

    meta = json.loads(sidecar.read_text(encoding="utf-8"))
    assert meta.get("porosity_slice_plane") is not None
    assert meta.get("geometry_mode") == GEOMETRY_THIN_SLICE


@pytest.mark.parametrize(
    "fixture_name",
    ["_test_pseudo2d_statistical_fast.json"],
)
def test_statistical_fast_fixture(fixture_name, tmp_path):
    fx = _ROOT / "dsl" / "wizard_templates" / fixture_name
    out = tmp_path / "stat.stl"
    generate_packed_bed_stl(fx, out, max_passos=200)
    assert out.stat().st_size > 80


@pytest.mark.skipif(
    os.environ.get("BEDFLOW_BLENDER_SMOKE") != "1",
    reason="defina BEDFLOW_BLENDER_SMOKE=1 para executar smoke blender",
)
def test_blender_smoke_thin_slice_script():
    blender = shutil.which("blender")
    if not blender:
        pytest.skip("blender nao esta no PATH")
    script = _ROOT / "scripts" / "blender_scripts" / "smoke_thin_slice.py"
    proc = subprocess.run(
        [blender, "--background", "--python", str(script)],
        cwd=str(_ROOT),
        capture_output=True,
        text=True,
        timeout=180,
    )
    assert proc.returncode == 0, proc.stderr or proc.stdout
    assert "BEDFLOW_THIN_SLICE_SMOKE_OK" in proc.stdout
