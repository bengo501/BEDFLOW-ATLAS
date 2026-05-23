# testes de seed de empacotamento
from __future__ import annotations

import sys
from pathlib import Path

_SCRIPTS = Path(__file__).resolve().parents[2] / "blender_scripts"
if str(_SCRIPTS) not in sys.path:
    sys.path.insert(0, str(_SCRIPTS))

from packed_bed_science.packing_seed import resolve_packing_random_seed  # noqa: E402
from packed_bed_science.packing_spherical import generate_spherical_packing  # noqa: E402
from packed_bed_science.geometry_math import AnnulusBedDomain  # noqa: E402


def test_resolve_seed_fixed_when_in_json():
    s, auto = resolve_packing_random_seed(
        {"random_seed": 99}, {"seed": 1}
    )
    assert s == 99
    assert auto is False


def test_resolve_seed_auto_when_missing():
    s1, auto1 = resolve_packing_random_seed({}, {})
    s2, auto2 = resolve_packing_random_seed({}, {})
    assert auto1 is True
    assert auto2 is True


def test_spherical_differs_without_fixed_seed():
    domain = AnnulusBedDomain(
        r_int=0.02,
        r_ext=0.025,
        height=0.1,
        bottom_cap_thickness=0.003,
        top_cap_thickness=0.003,
        r_sphere=0.0025,
        gap=0.0001,
    )
    a = generate_spherical_packing(
        domain, 12, 0.0025, 0.0001, random_seed=111
    )["centers"]
    b = generate_spherical_packing(
        domain, 12, 0.0025, 0.0001, random_seed=222
    )["centers"]
    assert a != b
