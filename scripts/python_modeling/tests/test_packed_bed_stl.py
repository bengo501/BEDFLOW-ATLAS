# testes automaticos do fluxo packed bed stl sem blender
from __future__ import annotations

import json
from pathlib import Path

import pytest

import packed_bed_stl as pbs

FIXTURES = Path(__file__).resolve().parent.parent


def test_load_bed_json_spherical_fixture():
    p = pbs.load_bed_json(FIXTURES / "_test_spherical.json")
    assert p["packing_method"] == "spherical_packing"
    assert p["particle_count"] == 40
    assert p["gap"] == pytest.approx(0.0001)
    assert p["strict_validation"] is True
    assert p["diameter"] == pytest.approx(0.05)
    assert p["wall_thickness"] == pytest.approx(0.002)


def test_load_bed_json_hex_fixture():
    p = pbs.load_bed_json(FIXTURES / "_test_hex.json")
    assert p["packing_method"] == "hexagonal_3d"


def test_load_bed_json_rigid_fixture():
    p = pbs.load_bed_json(FIXTURES / "_test_rigidbody.json")
    assert p["packing_method"] == "rigid_body"


def test_packing_method_name_aliases():
    assert pbs._packing_method_name({}) == "rigid_body"
    assert pbs._packing_method_name({"method": "hexagonal3d"}) == "hexagonal_3d"
    assert pbs._packing_method_name({"method": "hexagonal-3d"}) == "hexagonal_3d"
    assert pbs._packing_method_name({"method": "spherical_packing"}) == "spherical_packing"


def test_to_float_and_int():
    assert pbs._to_float("1,5", 0.0) == pytest.approx(1.5)
    assert pbs._to_float(None, 3.0) == 3.0
    assert pbs._to_int("10", 0) == 10


@pytest.mark.parametrize(
    "method,expect_sidecar",
    [
        ("spherical", True),
        ("hex", True),
    ],
)
def test_generate_science_writes_stl_and_optional_json(
    tmp_path: Path, method: str, expect_sidecar: bool
):
    name = "_test_spherical.json" if method == "spherical" else "_test_hex.json"
    out = tmp_path / f"out_{method}.stl"
    pbs.generate_packed_bed_stl(FIXTURES / name, out)
    assert out.is_file()
    assert out.stat().st_size > 8_000
    side = tmp_path / f"out_{method}_pure_bed.json"
    if expect_sidecar:
        assert side.is_file()
        data = json.loads(side.read_text(encoding="utf-8"))
        assert "validation" in data
        placed = data.get("n_particles_placed", data.get("n_spheres_placed", 0))
        assert placed >= 1


def test_generate_legacy_rigid_writes_stl(tmp_path: Path):
    out = tmp_path / "out_rigid.stl"
    pbs.generate_packed_bed_stl(
        FIXTURES / "_test_rigidbody.json",
        out,
        max_passos=5_000,
    )
    assert out.is_file()
    assert out.stat().st_size > 5_000
