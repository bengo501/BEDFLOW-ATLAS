# rigid_body no python_engine = preset dem com menos passos e mais amortecimento
from __future__ import annotations

from typing import Any, Dict, List, Optional, Tuple

from .dem_solver import merge_dem_params, run_dem_packing
from .domain import PackedBedDomain

vec3 = Tuple[float, float, float]


def rigid_body_preset_params(packing: Dict[str, Any]) -> Dict[str, Any]:
    base = merge_dem_params(packing)
    base["steps"] = min(int(base.get("steps", 30_000)), 15_000)
    base["damping"] = max(float(base.get("damping", 0.2)), 0.35)
    base["stiffness"] = float(base.get("stiffness", 5000.0)) * 0.85
    base["settle_steps_required"] = max(int(base.get("settle_steps_required", 50)), 30)
    return base


def run_rigid_body_packing(
    domain: PackedBedDomain,
    n_particles: int,
    packing: Dict[str, Any],
    *,
    warnings: Optional[List[str]] = None,
) -> Tuple[List[vec3], Dict[str, Any]]:
    w = warnings if warnings is not None else []
    w.append(
        "rigid_body (python_engine): simulacao dem simplificada com contacto partícula-partícula; "
        "diferente do rigid body nativo do blender"
    )
    pack = dict(packing)
    pack["dem"] = rigid_body_preset_params(packing)
    centers, meta = run_dem_packing(domain, n_particles, pack, warnings=w)
    meta["packing_mode_resolved"] = "rigid_body_as_dem_preset"
    return centers, meta
