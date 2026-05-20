import json
import sys
import tempfile
from pathlib import Path

import pytest

_PM = Path(__file__).resolve().parents[1]
_ROOT = _PM.parents[1]
if str(_PM) not in sys.path:
    sys.path.insert(0, str(_PM))

from pure_generation import generate_packed_bed_stl  # noqa: E402


@pytest.mark.parametrize(
    "fixture_name",
    ["_test_pseudo2d_slice.json", "_test_pseudo2d_statistical.json"],
)
def test_generate_stl_from_fixture(fixture_name):
    fx = _ROOT / "dsl" / "wizard_templates" / fixture_name
    if not fx.is_file():
        pytest.skip(f"fixture ausente: {fx}")
    with tempfile.TemporaryDirectory() as td:
        out = Path(td) / "out.stl"
        generate_packed_bed_stl(fx, out, max_passos=500)
        assert out.is_file()
        assert out.stat().st_size > 80
        sidecar = out.parent / f"{out.stem}_pure_bed.json"
        if sidecar.is_file():
            meta = json.loads(sidecar.read_text(encoding="utf-8"))
            assert meta.get("geometry_mode") in (
                "pseudo_2d_thin_slice",
                "pseudo_2d_statistical",
            )
