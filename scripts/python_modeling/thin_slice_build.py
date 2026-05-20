# construcao de malha thin slice (lamina fina) a partir de packing 3d
from __future__ import annotations

from typing import Any, Dict, List, Tuple

from geometry_modes import (
    normalize_slice_axis,
    particle_intersects_slice,
    slice_footprint_center,
    slice_footprint_spec,
)
from stl_mesh_utils import (
    annulus_cap_pair,
    box_mesh,
    box_mesh_anisotropic,
    cylinder_axis,
    filter_faces_by_slab,
    merge_mesh,
    tri,
    uv_sphere,
    vec3,
)


def _append_particle_full(
    particle_kind: str,
    center: vec3,
    particle_diameter: float,
    segmentos: int,
) -> Tuple[List[vec3], List[tri]]:
    pk = (particle_kind or "sphere").strip().lower()
    d = float(particle_diameter)
    cx, cy, cz = center
    if pk == "cube":
        return box_mesh(cx, cy, cz, d)
    if pk == "cylinder":
        return cylinder_axis(cx, cy, cz, d * 0.5, d, axis="z", segments=segmentos)
    return uv_sphere(cx, cy, cz, d * 0.5, lat=4, lon=6)


def _append_slice_footprint(
    particle_kind: str,
    center: vec3,
    particle_diameter: float,
    *,
    slice_axis: str,
    slice_position: float,
    slice_thickness: float,
    preserve: bool,
    segmentos: int,
) -> Tuple[List[vec3], List[tri]]:
    ai = 0 if slice_axis == "x" else (1 if slice_axis == "y" else 2)
    d_plane = abs(center[ai] - slice_position)
    spec = slice_footprint_spec(
        particle_kind,
        particle_diameter,
        d_plane,
        slice_axis=slice_axis,
        slice_thickness=slice_thickness,
    )
    if spec.get("shape") == "none":
        return [], []

    cx, cy, cz = slice_footprint_center(
        center,
        slice_axis=slice_axis,
        slice_position=slice_position,
        preserve_original_packing=preserve,
    )
    seg = max(12, min(32, segmentos))

    if spec.get("shape") == "disc":
        rs = float(spec["radius"])
        t = float(spec.get("thickness") or slice_thickness)
        return cylinder_axis(cx, cy, cz, rs, t, axis=slice_axis, segments=seg)

    if spec.get("shape") == "box":
        return box_mesh_anisotropic(
            cx,
            cy,
            cz,
            float(spec["size_x"]),
            float(spec["size_y"]),
            float(spec["size_z"]),
        )
    return [], []


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

    pk = (particle_kind or "sphere").strip().lower()
    seg_p = max(12, min(32, segmentos))

    for (x, y, z) in centers:
        center = (float(x), float(y), float(z))
        if not particle_intersects_slice(
            center,
            particle_kind=pk,
            particle_diameter=particle_diameter,
            axis=axis,
            slice_position=pos,
            slice_thickness=thickness,
        ):
            if keep_only:
                continue
            sv, sf = _append_particle_full(pk, center, particle_diameter, seg_p)
            v_all, f_all = merge_mesh(v_all, f_all, sv, sf)
            continue

        sv, sf = _append_slice_footprint(
            pk,
            center,
            particle_diameter,
            slice_axis=axis,
            slice_position=pos,
            slice_thickness=thickness,
            preserve=preserve,
            segmentos=seg_p,
        )
        if sv:
            v_all, f_all = merge_mesh(v_all, f_all, sv, sf)

    return v_all, f_all
