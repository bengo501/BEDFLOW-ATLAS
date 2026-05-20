# testes parse/compile-from-bed (modal carregar .bed)
from __future__ import annotations

import json
import sys
from pathlib import Path

import pytest

_REPO = Path(__file__).resolve().parents[2]
if str(_REPO) not in sys.path:
    sys.path.insert(0, str(_REPO))
if str(_REPO / "backend") not in sys.path:
    sys.path.insert(0, str(_REPO / "backend"))

from backend.app.services.bed_parse_service import (  # noqa: E402
    compile_from_bed,
    parse_bed_content,
)


FIXTURE_BED = _REPO / "dsl" / "examples" / "leito_pseudo2d_slice.bed"


def test_parse_valid_bed():
    content = FIXTURE_BED.read_text(encoding="utf-8")
    out = parse_bed_content(content, "leito_pseudo2d_slice.bed")
    assert out["valid"] is True
    assert out["parsed"] is not None
    assert out["parsed"]["geometry_mode"] in (
        "pseudo_2d_thin_slice",
        "full_3d",
    )
    assert out["parsed"]["packing"]["method"]


def test_parse_empty_fails():
    out = parse_bed_content("", "x.bed")
    assert out["valid"] is False


def test_compile_from_bed_with_override_slice_thickness(tmp_path, monkeypatch):
    from bedflow_local_paths import beds_dir

    monkeypatch.setattr(
        "backend.app.services.bed_parse_service.beds_dir",
        lambda: tmp_path / "beds",
    )
    content = FIXTURE_BED.read_text(encoding="utf-8")
    result = compile_from_bed(
        content=content,
        filename="test_slice.bed",
        overrides={
            "geometry_mode": "pseudo_2d_thin_slice",
            "slice": {
                "slice_enabled": True,
                "slice_thickness": 0.005,
                "slice_axis": "y",
                "slice_position": 0.0,
                "keep_only_intersecting_particles": True,
            },
        },
        hub_mode="interactive",
        save_to_db=False,
    )
    assert result["success"] is True
    json_path = _REPO / result["json_file"]
    assert json_path.exists()
    data = json.loads(json_path.read_text(encoding="utf-8"))
    sl = data.get("slice") or {}
    assert float(sl.get("slice_thickness", 0)) == pytest.approx(0.005, rel=1e-6)
    diffs = result.get("diff_from_parsed") or []
    paths = [d["path"] for d in diffs]
    assert any("slice" in p for p in paths) or sl.get("slice_thickness") == 0.005


def test_compile_invalid_syntax():
    with pytest.raises(RuntimeError):
        compile_from_bed(
            content="bed { diameter = ; }",
            filename="bad.bed",
            overrides=None,
        )
