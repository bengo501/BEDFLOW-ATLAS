# construcao de malha thin slice (lamina fina) a partir de packing 3d
from __future__ import annotations

import math
from typing import Any, Dict, List, Tuple

from geometry_modes import (
    normalize_slice_axis,
    particle_intersects_slice,
    section_radius_for_particle_kind,
)
from stl_mesh_utils import (
    annulus_cap_pair,
    cylinder_axis,
    filter_faces_by_slab,
    merge_mesh,
    tri,
    vec3,
)

__all__ = ["apply_thin_slice_mesh", "slice_cfg_active"]


def slice_cfg_active(slice_cfg: Dict[str, Any]) -> bool:
    if not slice_cfg:
        return False
    return bool(slice_cfg.get("slice_enabled"))


def apply_thin_slice_mesh(
    shell_vertices: List[vec3],
    shell_faces: List[tri],
    centers: List[vec3],
    *,
    particle_diameter: float,
    particle_kind: str,
    r_ext: float,
    r_int: float,
    slice_cfg: Dict[str, Any],
    segmentos: int = 48,
) -> Tuple[List[vec3], List[tri]]:
    axis = normalize_slice_axis(slice_cfg.get("slice_axis"), "y")
    thickness = float(slice_cfg.get("slice_thickness") or 0.002)
    if thickness <= 0:
        thickness = 0.002
    pos = float(slice_cfg.get("slice_position") or 0.0)
    keep_only = bool(slice_cfg.get("keep_only_intersecting_particles", True))
    preserve = bool(slice_cfg.get("preserve_original_packing", True))

    min_v = pos - thickness / 2.0
    max_v = pos + thickness / 2.0
    v_shell, f_shell = filter_faces_by_slab(
        shell_vertices,
        shell_faces,
        axis=axis,
        min_v=min_v,
        max_v=max_v,
    )
    cap_v, cap_f = annulus_cap_pair(
        r_ext=r_ext,
        r_int=r_int,
        axis=axis,
        position=pos,
        thickness=thickness,
        segments=max(12, segmentos),
    )
    v_all: List[vec3] = list(v_shell)
    f_all: List[tri] = list(f_shell)
    if cap_v:
        v_all, f_all = merge_mesh(v_all, f_all, cap_v, cap_f)

    r_part = particle_diameter * 0.5
    pk = (particle_kind or "sphere").strip().lower()
    seg_p = max(12, min(32, segmentos))

    for (x, y, z) in centers:
        center = (float(x), float(y), float(z))
        if not particle_intersects_slice(
            center,
            r_part,
            axis=axis,
            slice_position=pos,
            slice_thickness=thickness,
        ):
            if keep_only:
                continue
            continue
        d_plane = abs(
            (center[0] if axis == "x" else center[1] if axis == "y" else center[2])
            - pos
        )
        rs = section_radius_for_particle_kind(
            pk, particle_diameter, d_plane, axis=axis
        )
        if rs <= 1e-9:
            continue
        if preserve:
            cx, cy, cz = center
        else:
            if axis == "x":
                cx, cy, cz = pos, center[1], center[2]
            elif axis == "y":
                cx, cy, cz = center[0], pos, center[2]
            else:
                cx, cy, cz = center[0], center[1], pos
        cv, cf = cylinder_axis(
            cx, cy, cz, rs, thickness, axis=axis, segments=seg_p
        )
        v_all, f_all = merge_mesh(v_all, f_all, cv, cf)

    return v_all, f_all
