# construcao de malha thin slice (lamina fina) a partir de packing 3d
from __future__ import annotations

from pathlib import Path
from typing import Any, Dict, List, Optional, Tuple

from bed_reference_frame import BedReferenceFrame, frame_from_slice_cfg
from geometry_modes import (
    SLICE_POLICY_INTERSECTING,
    footprint_vertices_leak_util,
    normalize_slice_axis,
    particle_intersects_slice,
    particle_passes_policy,
    particle_slice_metrics,
    slice_footprint_center,
    slice_footprint_spec,
)
from slice_debug_export import (
    empty_slice_summary,
    export_debug_gizmo_stl,
    write_slice_debug_json,
)
from stl_mesh_utils import (
    annulus_cap_pair,
    box_mesh,
    box_mesh_anisotropic,
    clip_mesh_to_util_volume,
    cylinder_axis,
    filter_faces_by_slab,
    merge_mesh,
    tri,
    uv_sphere,
    vec3,
)

SliceSummary = Dict[str, Any]


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
    debug_stl_path: Optional[Path] = None,
    debug_json_path: Optional[Path] = None,
) -> Tuple[List[vec3], List[tri], SliceSummary]:
    frame = frame_from_slice_cfg(
        slice_cfg, r_int=r_int, r_ext=r_ext, height=_infer_height_from_shell(shell_vertices)
    )
    axis = frame.slice_axis
    thickness = frame.slice_thickness
    pos = frame.slice_center
    keep_only = bool(slice_cfg.get("keep_only_intersecting_particles", True))
    preserve = bool(slice_cfg.get("preserve_original_packing", True))
    policy = frame.slice_particle_policy

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
    if cap_v and f_shell:
        v_all, f_all = merge_mesh(v_all, f_all, cap_v, cap_f)

    pk = (particle_kind or "sphere").strip().lower()
    seg_p = max(12, min(32, segmentos))
    summary = empty_slice_summary()
    summary["slice_particle_policy"] = policy
    summary["n_centers"] = len(centers)
    leak_centers: List[vec3] = []
    particle_logs: List[Dict[str, Any]] = []

    for (x, y, z) in centers:
        center = (float(x), float(y), float(z))
        metrics = particle_slice_metrics(
            center,
            particle_kind=pk,
            particle_diameter=particle_diameter,
            slice_axis=axis,
            slice_center=pos,
            slice_thickness=thickness,
            r_util=frame.r_util,
        )
        legacy_ok = bool(metrics["passes_legacy_slice_only"])
        if not legacy_ok:
            summary["n_dropped_legacy_slice"] += 1
            if not keep_only:
                sv, sf = _append_particle_full(pk, center, particle_diameter, seg_p)
                v_all, f_all = merge_mesh(v_all, f_all, sv, sf)
                summary["n_full_3d_outside"] += 1
            continue

        if not particle_passes_policy(
            center,
            particle_kind=pk,
            particle_diameter=particle_diameter,
            slice_axis=axis,
            slice_center=pos,
            slice_thickness=thickness,
            r_util=frame.r_util,
            policy=policy,
        ):
            summary["n_dropped_policy"] += 1
            if metrics.get("leak_footprint_legacy"):
                leak_centers.append(center)
            if bool(slice_cfg.get("debug_export_gizmos")):
                metrics["action"] = "dropped_policy"
                particle_logs.append(metrics)
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
        if not sv:
            continue

        if footprint_vertices_leak_util(
            sv,
            r_util=frame.r_util,
            slice_axis=axis,
            slice_center=pos,
            slice_thickness=thickness,
        ):
            summary["n_leak_footprint_before_clip"] += 1
            leak_centers.append(center)

        if policy == SLICE_POLICY_INTERSECTING:
            sv2, sf2 = clip_mesh_to_util_volume(
                sv,
                sf,
                r_util=frame.r_util,
                slice_axis=axis,
                slice_center=pos,
                slice_thickness=thickness,
            )
            if not sv2:
                summary["n_clipped"] += 1
                if bool(slice_cfg.get("debug_export_gizmos")):
                    metrics["action"] = "clipped_empty"
                    particle_logs.append(metrics)
                continue
            if len(sv2) < len(sv) or len(sf2) < len(sf):
                summary["n_clipped"] += 1
            sv, sf = sv2, sf2

        if footprint_vertices_leak_util(
            sv,
            r_util=frame.r_util,
            slice_axis=axis,
            slice_center=pos,
            slice_thickness=thickness,
        ):
            summary["leak_count"] += 1
            if bool(slice_cfg.get("debug_export_gizmos")):
                metrics["action"] = "leak_after_processing"
                particle_logs.append(metrics)
            continue

        v_all, f_all = merge_mesh(v_all, f_all, sv, sf)
        summary["n_kept"] += 1
        if bool(slice_cfg.get("debug_export_gizmos")):
            metrics["action"] = "kept"
            particle_logs.append(metrics)

    if bool(slice_cfg.get("debug_export_gizmos")):
        summary["particles"] = particle_logs
        if debug_json_path is not None:
            write_slice_debug_json(debug_json_path, summary, frame)
        if debug_stl_path is not None and leak_centers:
            export_debug_gizmo_stl(
                debug_stl_path,
                frame,
                leak_centers=leak_centers,
                particle_diameter=particle_diameter,
            )

    return v_all, f_all, summary


def _infer_height_from_shell(vertices: List[vec3]) -> float:
    if not vertices:
        return 0.1
    zs = [p[2] for p in vertices]
    return max(max(zs) - min(zs), 0.01)
