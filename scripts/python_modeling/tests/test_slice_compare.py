"""
prova de que a saída de validação do corte 2d (2d + 3d) funciona.

ao gerar uma fatia 2d (pseudo_2d_thin_slice), o pipeline pode gerar também o
modelo 3d (antes do corte) e arquivos de comparação, conforme slice.compare_mode:

  off       -> só o 2d
  separate  -> 2d + 3d em arquivos separados (_full3d)
  combined  -> além disso, 2d e 3d lado a lado num arquivo (_compare)
  overlay   -> além disso, 2d dentro do 3d, na posição do corte (_overlay)
  all       -> separate + combined + overlay
"""
from __future__ import annotations

import struct
import sys
from pathlib import Path

import pytest

_PM = Path(__file__).resolve().parents[1]
if str(_PM) not in sys.path:
    sys.path.insert(0, str(_PM))

from engine.pipeline import generate_packed_bed  # noqa: E402
from geometry_modes import resolve_slice_config  # noqa: E402
from slice_compare import normalize_compare_mode  # noqa: E402


def _base_params(compare_mode: str) -> dict:
    return dict(
        diameter=0.05, wall_thickness=0.003, height=0.06, bottom_thickness=0.004,
        top_thickness=0.004, gap=0.0005, particle_diameter=0.008, particle_kind="sphere",
        particle_count=16, packing_method="hexagonal_3d", mesh_segmentos=18,
        sphere_lat=4, sphere_lon=6, strict_validation=False,
        geometry_mode="pseudo_2d_thin_slice", particles_seed=7, packing={"seed": 7},
        slice={"slice_enabled": True, "slice_axis": "y", "slice_thickness": 0.004,
               "compare_mode": compare_mode},
    )


def _stl_x_span(path: Path):
    with open(path, "rb") as f:
        f.read(80)
        (n,) = struct.unpack("<I", f.read(4))
        lo, hi = 1e9, -1e9
        for _ in range(n):
            f.read(12)
            for _v in range(3):
                x, _y, _z = struct.unpack("<3f", f.read(12))
                lo = min(lo, x)
                hi = max(hi, x)
            f.read(2)
    return lo, hi


def test_compare_mode_normalization():
    assert normalize_compare_mode(None) == "separate"
    assert normalize_compare_mode("lado_a_lado") == "combined"
    assert normalize_compare_mode("dentro") == "overlay"
    assert normalize_compare_mode("nao") == "off"


def test_resolve_legacy_preserve_full_3d_maps_to_off():
    cfg = resolve_slice_config(
        {"geometry_mode": "pseudo_2d_thin_slice",
         "slice": {"slice_enabled": True, "preserve_full_3d": False}}
    )
    assert cfg["compare_mode"] == "off"
    assert cfg["preserve_full_3d"] is False


def test_off_only_2d(tmp_path):
    generate_packed_bed(_base_params("off"), tmp_path / "leito.stl")
    names = {p.name for p in tmp_path.iterdir()}
    assert "leito.stl" in names
    assert "leito_full3d.stl" not in names
    assert not any("_compare" in n or "_overlay" in n for n in names)


def test_separate_two_files(tmp_path):
    generate_packed_bed(_base_params("separate"), tmp_path / "leito.stl")
    names = {p.name for p in tmp_path.iterdir()}
    assert "leito.stl" in names
    assert "leito_full3d.stl" in names           # 3d separado
    assert not any("_compare" in n or "_overlay" in n for n in names)


def test_combined_side_by_side(tmp_path):
    generate_packed_bed(_base_params("combined"), tmp_path / "leito.stl")
    names = {p.name for p in tmp_path.iterdir()}
    for f in ("leito_full3d.stl", "leito_compare.stl", "leito_compare.obj", "leito_compare.mtl"):
        assert f in names, f
    # lado a lado: o combinado é mais largo em x que o 2d sozinho
    lo2d, hi2d = _stl_x_span(tmp_path / "leito.stl")
    loc, hic = _stl_x_span(tmp_path / "leito_compare.stl")
    assert (hic - loc) > (hi2d - lo2d) * 1.5


def test_overlay_2d_inside_3d(tmp_path):
    generate_packed_bed(_base_params("overlay"), tmp_path / "leito.stl")
    names = {p.name for p in tmp_path.iterdir()}
    for f in ("leito_full3d.stl", "leito_overlay.stl", "leito_overlay.obj", "leito_overlay.mtl"):
        assert f in names, f
    # sobreposto: a largura em x ~ a do 3d (2d dentro do 3d, mesma posição)
    lo3d, hi3d = _stl_x_span(tmp_path / "leito_full3d.stl")
    loo, hio = _stl_x_span(tmp_path / "leito_overlay.stl")
    assert abs((hio - loo) - (hi3d - lo3d)) < 1e-3
    # o .obj tem dois objetos nomeados e materiais (leito translúcido + fatia sólida)
    obj = (tmp_path / "leito_overlay.obj").read_text(encoding="utf-8")
    mtl = (tmp_path / "leito_overlay.mtl").read_text(encoding="utf-8")
    assert obj.count("\no ") + (1 if obj.startswith("o ") else 0) == 2
    assert mtl.count("newmtl") == 2
    assert "d 0.220" in mtl  # leito 3d translúcido


def test_all_generates_everything(tmp_path):
    generate_packed_bed(_base_params("all"), tmp_path / "leito.stl")
    names = {p.name for p in tmp_path.iterdir()}
    for f in (
        "leito.stl", "leito_full3d.stl",
        "leito_compare.stl", "leito_compare.obj", "leito_compare.mtl",
        "leito_overlay.stl", "leito_overlay.obj", "leito_overlay.mtl",
    ):
        assert f in names, f
    # sidecar registra o modo e os arquivos de comparação
    import json
    sc = json.loads((tmp_path / "leito_pure_bed.json").read_text(encoding="utf-8"))
    assert sc.get("compare_mode") == "all"
    assert len(sc.get("comparison_files") or []) >= 6
