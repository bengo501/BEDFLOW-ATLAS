# gizmos e log de diagnostico para pseudo-2d thin slice
from __future__ import annotations

import json
from pathlib import Path
from typing import Any, Dict, List, Optional, Tuple

from bed_reference_frame import BedReferenceFrame, build_slice_volume_mesh
from geometry_modes import particle_slice_metrics
from stl_mesh_utils import (
    annulus_cap_pair,
    cylinder_axis,
    merge_mesh,
    tri,
    vec3,
    write_stl_binary,
)

SliceSummary = Dict[str, Any]


def empty_slice_summary() -> SliceSummary:
    return {
        "n_centers": 0,
        "n_kept": 0,
        "n_dropped_policy": 0,
        "n_dropped_legacy_slice": 0,
        "n_leak_footprint_before_clip": 0,
        "n_clipped": 0,
        "n_full_3d_outside": 0,
        "leak_count": 0,
        "slice_particle_policy": "contained",
        "particles": [],
    }


def build_debug_gizmo_meshes(
    frame: BedReferenceFrame,
    *,
    leak_centers: List[vec3],
    particle_diameter: float = 0.005,
    segments: int = 24,
) -> Tuple[List[vec3], List[tri]]:
    """malha combinada: cilindro util, planos da fatia, caixas em centros com leak."""
    v_all: List[vec3] = []
    f_all: List[tri] = []

    cx, cy, cz = 0.0, 0.0, frame.height / 2.0
    v_cyl, f_cyl = cylinder_axis(
        cx, cy, cz, frame.r_util, frame.height, axis=frame.bed_axis, segments=segments
    )
    v_all, f_all = merge_mesh(v_all, f_all, v_cyl, f_cyl)

    cap_v, cap_f = annulus_cap_pair(
        r_ext=frame.r_util * 1.02,
        r_int=0.0,
        axis=frame.slice_axis,
        position=frame.slice_center,
        thickness=frame.slice_thickness,
        segments=segments,
    )
    if cap_v:
        v_all, f_all = merge_mesh(v_all, f_all, cap_v, cap_f)

    half = frame.slice_thickness / 2.0
    for plane_pos in (frame.slice_center - half, frame.slice_center + half):
        cv, cf = annulus_cap_pair(
            r_ext=frame.r_util * 1.05,
            r_int=0.0,
            axis=frame.slice_axis,
            position=plane_pos,
            thickness=frame.slice_thickness * 0.05,
            segments=segments,
        )
        if cv:
            v_all, f_all = merge_mesh(v_all, f_all, cv, cf)

    d = float(particle_diameter)
    for c in leak_centers:
        x, y, z = c
        hx = hy = hz = d * 0.55
        verts: List[vec3] = [
            (x - hx, y - hy, z - hz),
            (x + hx, y - hy, z - hz),
            (x + hx, y + hy, z - hz),
            (x - hx, y + hy, z - hz),
            (x - hx, y - hy, z + hz),
            (x + hx, y - hy, z + hz),
            (x + hx, y + hy, z + hz),
            (x - hx, y + hy, z + hz),
        ]
        faces: List[tri] = [
            (0, 1, 2),
            (0, 2, 3),
            (4, 6, 5),
            (4, 7, 6),
            (0, 4, 5),
            (0, 5, 1),
            (1, 5, 6),
            (1, 6, 2),
            (2, 6, 7),
            (2, 7, 3),
            (3, 7, 4),
            (3, 4, 0),
        ]
        base = len(v_all)
        v_all.extend(verts)
        f_all.extend((base + a, base + b, base + c) for (a, b, c) in faces)

    return v_all, f_all


def write_slice_debug_json(
    path: Path,
    summary: SliceSummary,
    frame: Optional[BedReferenceFrame] = None,
) -> None:
    payload = dict(summary)
    if frame is not None:
        payload["frame"] = {
            "r_util": frame.r_util,
            "r_ext": frame.r_ext,
            "height": frame.height,
            "slice_axis": frame.slice_axis,
            "slice_center": frame.slice_center,
            "slice_thickness": frame.slice_thickness,
            "slice_particle_policy": frame.slice_particle_policy,
        }
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", encoding="utf-8") as fp:
        json.dump(payload, fp, indent=2, ensure_ascii=False)


def export_debug_gizmo_stl(
    out_path: Path,
    frame: BedReferenceFrame,
    *,
    leak_centers: List[vec3],
    particle_diameter: float = 0.005,
) -> None:
    v, f = build_debug_gizmo_meshes(
        frame, leak_centers=leak_centers, particle_diameter=particle_diameter
    )
    if v and f:
        write_stl_binary(out_path, v, f)


def collect_particle_metrics(
    centers: List[vec3],
    *,
    frame: BedReferenceFrame,
    particle_kind: str,
    particle_diameter: float,
) -> List[Dict[str, Any]]:
    rows = []
    for c in centers:
        m = particle_slice_metrics(
            c,
            particle_kind=particle_kind,
            particle_diameter=particle_diameter,
            slice_axis=frame.slice_axis,
            slice_center=frame.slice_center,
            slice_thickness=frame.slice_thickness,
            r_util=frame.r_util,
        )
        rows.append(m)
    return rows


__all__ = [
    "build_debug_gizmo_meshes",
    "collect_particle_metrics",
    "empty_slice_summary",
    "export_debug_gizmo_stl",
    "write_slice_debug_json",
]
