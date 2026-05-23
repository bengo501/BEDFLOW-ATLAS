# construcao de malha thin slice (lamina fina) a partir de packing 3d
from __future__ import annotations

from pathlib import Path
from typing import Any, Dict, List, Optional, Tuple

from bed_reference_frame import frame_from_slice_cfg
from slice_debug_export import (
    empty_slice_summary,
    export_debug_gizmo_stl,
    write_slice_debug_json,
)
from stl_mesh_utils import (
    annulus_cap_pair,
    filter_faces_by_slab,
    merge_mesh,
    tri,
    vec3,
)
from thin_slice_particles import (
    DROP_POLICY,
    SliceParticleConfig,
    prepare_slice_particle_for_mesh,
    process_slice_particles,
)

SliceSummary = Dict[str, Any]


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
    bed_h = _infer_height_from_shell(shell_vertices)
    frame = frame_from_slice_cfg(
        slice_cfg, r_int=r_int, r_ext=r_ext, height=bed_h
    )
    axis = frame.slice_axis
    thickness = frame.slice_thickness
    pos = frame.slice_center
    policy = frame.slice_particle_policy
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
    if cap_v and cap_f:
        v_all, f_all = merge_mesh(v_all, f_all, cap_v, cap_f)

    pk = (particle_kind or "sphere").strip().lower()
    pcfg = SliceParticleConfig.from_slice_cfg(slice_cfg, r_int=r_int)
    pcfg.preserve_original_packing = preserve

    filtered: List[vec3] = []
    particle_logs: List[Dict[str, Any]] = []
    n_dropped_policy = 0
    leak_centers: List[vec3] = []

    for center in centers:
        c = (float(center[0]), float(center[1]), float(center[2]))
        loc, _rs, prep_meta = prepare_slice_particle_for_mesh(
            c,
            pk,
            particle_diameter,
            cfg=pcfg,
            policy=policy,
        )
        if loc is None:
            if prep_meta.get("reason") == DROP_POLICY:
                n_dropped_policy += 1
            if bool(slice_cfg.get("debug_export_gizmos")):
                leak_centers.append(c)
            continue
        filtered.append(c)

    pv, pf, part_summary = process_slice_particles(
        filtered,
        particle_kind=pk,
        particle_diameter=particle_diameter,
        cfg=pcfg,
        segmentos=segmentos,
        policy=policy,
    )
    if pv:
        from mesh_export_validate import validate_thin_slice_mesh

        bed_h = _infer_height_from_shell(shell_vertices)
        vpre = validate_thin_slice_mesh(
            pv,
            slice_axis=axis,
            slice_thickness=thickness,
            bed_height=bed_h,
            particle_region_only=True,
        )
        if not vpre.get("ok"):
            raise RuntimeError(
                "validação thin slice (partículas): "
                + "; ".join(vpre.get("errors") or [])
            )
        v_all, f_all = merge_mesh(v_all, f_all, pv, pf)

    summary = empty_slice_summary()
    summary.update(part_summary)
    summary["slice_particle_policy"] = policy
    summary["geometry_mode"] = "pseudo_2d_thin_slice"
    summary["slice_axis"] = axis
    summary["slice_position"] = pos
    summary["slice_thickness"] = thickness
    summary["n_dropped_policy"] = n_dropped_policy
    summary["slice_particle_summary"] = dict(part_summary)

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
