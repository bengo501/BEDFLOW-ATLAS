# integracao: gera stl pequeno com dem e spherical
from __future__ import annotations

import json
import sys
import tempfile
from pathlib import Path

_PM = Path(__file__).resolve().parents[1]
_ROOT = _PM.parents[1]
if str(_PM) not in sys.path:
    sys.path.insert(0, str(_PM))

from pure_generation import load_bed_json, generate_packed_bed_stl


def _minimal_bed(method: str, n: int = 6) -> dict:
    return {
        "geometry_mode": "full_3d",
        "generation_backend": "python_engine",
        "bed": {"diameter": 0.04, "height": 0.06, "wall_thickness": 0.002},
        "lids": {"bottom_thickness": 0.002, "top_thickness": 0.002},
        "particles": {"count": n, "diameter": 0.005, "kind": "sphere"},
        "packing": {
            "method": method,
            "gap": 0.0,
            "strict_validation": False,
            "dem": {
                "steps": 1500,
                "time_step": 3e-4,
                "settle_steps_required": 15,
                "seed": 7,
            },
        },
    }


def test_generate_dem_stl():
    with tempfile.TemporaryDirectory() as td:
        td_path = Path(td)
        jpath = td_path / "bed.json"
        jpath.write_text(json.dumps(_minimal_bed("dem")), encoding="utf-8")
        out = td_path / "out.stl"
        generate_packed_bed_stl(jpath, out, max_passos=100)
        assert out.exists() and out.stat().st_size > 100
        side = td_path / "out_pure_bed.json"
        assert side.exists()
        meta = json.loads(side.read_text(encoding="utf-8"))
        assert meta.get("packing_method") == "dem"
        assert meta.get("particle_type") == "sphere" or meta.get("particle_kind") == "sphere"


def test_generate_spherical_stl():
    with tempfile.TemporaryDirectory() as td:
        td_path = Path(td)
        jpath = td_path / "bed.json"
        data = _minimal_bed("spherical_packing", n=5)
        data["packing"]["max_placement_attempts"] = 5000
        data["packing"]["random_seed"] = 3
        jpath.write_text(json.dumps(data), encoding="utf-8")
        out = td_path / "out.stl"
        generate_packed_bed_stl(jpath, out)
        assert out.exists()
        meta = json.loads((td_path / "out_pure_bed.json").read_text(encoding="utf-8"))
        assert meta.get("packing_method") == "spherical_packing"
        assert "n_particles_placed" in meta
