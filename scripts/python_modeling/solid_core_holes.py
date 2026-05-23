# furos no núcleo sólido (modo solid_internal_cylinder_with_particle_holes) — contrato partilhado
from __future__ import annotations

from typing import Any, Dict, List, Tuple

vec3 = Tuple[float, float, float]


def solid_holes_particle_mesh_kind(particle_kind: str) -> str:
    """forma da ferramenta de furo alinhada ao blender_build.punch_core_with_particle_tools."""
    return (particle_kind or "sphere").strip().lower()


def solid_holes_status(
    *,
    n_centers: int,
    n_applied: int,
    backend: str,
    warnings: List[str],
) -> Dict[str, Any]:
    st = "applied" if n_applied > 0 else "failed"
    if n_centers == 0:
        st = "n/a"
    return {
        "particle_tools": st,
        "n_holes_requested": n_centers,
        "n_holes_applied": n_applied,
        "backend": backend,
        "warnings": list(warnings),
    }
