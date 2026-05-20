# valida pseudo-2d apos compilar .bed (sem patch)
from __future__ import annotations

import json
import sys
import tempfile
from pathlib import Path

import pytest

_ROOT = Path(__file__).resolve().parents[3]
_DSL = _ROOT / "dsl"
_PM = Path(__file__).resolve().parents[1]
_EXAMPLE = _DSL / "examples" / "leito_pseudo2d_slice.bed"

if str(_PM) not in sys.path:
    sys.path.insert(0, str(_PM))
if str(_DSL / "compiler") not in sys.path:
    sys.path.insert(0, str(_DSL / "compiler"))
if str(_DSL / "generated") not in sys.path:
    sys.path.insert(0, str(_DSL / "generated"))

from pure_generation import generate_packed_bed_stl  # noqa: E402


@pytest.mark.skipif(not _EXAMPLE.is_file(), reason="exemplo .bed ausente")
def test_pseudo2d_from_compiled_bed_dsl():
    try:
        from bed_compiler_antlr_standalone import ANTLR_AVAILABLE, compile_bed_file  # noqa: E402
    except ImportError:
        pytest.skip("compilador antlr indisponivel")
    if not ANTLR_AVAILABLE:
        pytest.skip("antlr nao disponivel")
    with tempfile.TemporaryDirectory() as td:
        td_path = Path(td)
        bed_json = td_path / "case.json"
        compile_bed_file(str(_EXAMPLE), str(bed_json))
        out_stl = td_path / "out.stl"
        generate_packed_bed_stl(bed_json, out_stl, max_passos=400)
        side = td_path / "out_pure_bed.json"
        assert side.is_file()
        meta = json.loads(side.read_text(encoding="utf-8"))
        assert meta.get("geometry_mode") == "pseudo_2d_thin_slice"
