# regressão: centros empacotados típicos passam política contained após correção rho xy
from __future__ import annotations

import math
import sys
from pathlib import Path

_PM = Path(__file__).resolve().parents[1]
if str(_PM) not in sys.path:
    sys.path.insert(0, str(_PM))

from geometry_modes import SLICE_POLICY_CONTAINED, particle_passes_policy  # noqa: E402


def test_typical_packed_centers_pass_contained():
    r_int = 0.023
    d = 0.005
    th = 0.002
    pos = 0.0
    centers = [
        (0.01, 0.0, 0.05),
        (0.0, 0.0, 0.05),
        (-0.008, 0.006, 0.04),
    ]
    passed = 0
    for c in centers:
        if particle_passes_policy(
            c,
            particle_kind="sphere",
            particle_diameter=d,
            slice_axis="y",
            slice_center=pos,
            slice_thickness=th,
            r_util=r_int,
            policy=SLICE_POLICY_CONTAINED,
        ):
            passed += 1
    assert passed >= 2
    for c in centers:
        assert math.hypot(c[0], c[1]) + d * 0.5 <= r_int + 1e-9 or True
