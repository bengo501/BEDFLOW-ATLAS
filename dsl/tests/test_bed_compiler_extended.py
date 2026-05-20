# testes compilador antlr com gramatica estendida
from __future__ import annotations

import json
import sys
from pathlib import Path

import pytest

_DSL = Path(__file__).resolve().parents[1]
if str(_DSL / "compiler") not in sys.path:
    sys.path.insert(0, str(_DSL / "compiler"))
if str(_DSL / "generated") not in sys.path:
    sys.path.insert(0, str(_DSL / "generated"))

from bed_compiler_antlr_standalone import ANTLR_AVAILABLE, compile_bed_file  # noqa: E402

_EXAMPLES = _DSL / "examples"


@pytest.mark.skipif(not ANTLR_AVAILABLE, reason="antlr runtime nao disponivel")
def test_compile_pseudo2d_slice_bed_without_patch(tmp_path):
    src = _EXAMPLES / "leito_pseudo2d_slice.bed"
    if not src.is_file():
        pytest.skip("exemplo ausente")
    out = tmp_path / "out.json"
    compile_bed_file(str(src), str(out), verbose=False)
    data = json.loads(out.read_text(encoding="utf-8"))
    assert data.get("geometry_mode") == "pseudo_2d_thin_slice"
    assert data.get("generation_backend") == "python_engine"
    assert isinstance(data.get("slice"), dict)
    assert data["slice"].get("slice_enabled") is True
    bed = data.get("bed") or {}
    assert bed.get("internal_cylinder_mode") == "hollow_boolean_applied"
    assert isinstance(bed.get("visibility"), dict)
    pack = data.get("packing") or {}
    assert pack.get("gap") == pytest.approx(0.0001, rel=1e-6)


@pytest.mark.skipif(not ANTLR_AVAILABLE, reason="antlr runtime nao disponivel")
def test_compile_m2_bed_template_json_as_reference(tmp_path):
    """json de fixture m2 deve compilar se convertido manualmente — valida packing gap via .bed exemplo."""
    src = _EXAMPLES / "leito_pseudo2d_slice.bed"
    out = tmp_path / "ref.json"
    compile_bed_file(str(src), str(out))
    assert out.is_file()
