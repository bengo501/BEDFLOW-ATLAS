# algoritmo unificado de partículas na lâmina pseudo-2d (python + contrato blender)
from __future__ import annotations

import math
from dataclasses import dataclass
from typing import Any, Dict, List, Optional, Tuple

from geometry_modes import (
    axis_index,
    collision_radius_for_particle_kind,
    particle_intersects_slice,
    particle_passes_policy,
    slice_footprint_center,
    slice_footprint_spec,
    snap_center_radial_to_util_wall,
    sphere_section_radius,
)
from stl_mesh_utils import (
    box_mesh_anisotropic,
    cylinder_axis,
    merge_mesh,
    tri,
    vec3,
)

SliceParticleSummary = Dict[str, Any]

# motivos de descarte (contrato partilhado python + blender)
DROP_POLICY = "policy"
DROP_OUTSIDE_SLICE = "outside_slice"
DROP_BELOW_MIN_RADIUS = "below_min_radius"
DROP_LEAK_RADIAL = "leak_radial"


@dataclass
class SliceParticleConfig:
    slice_axis: str = "y"
    slice_position: float = 0.0
    slice_thickness: float = 0.002
    min_slice_particle_radius: float = 1e-5
    r_util: float = 0.02
    snap_radial_to_wall: bool = True
    preserve_original_packing: bool = True
    keep_only_intersecting: bool = True

    @classmethod
    def from_slice_cfg(
        cls,
        slice_cfg: Dict[str, Any],
        *,
        r_int: float,
    ) -> "SliceParticleConfig":
        axis = str(slice_cfg.get("slice_axis") or "y").strip().lower()
        if axis not in ("x", "y", "z"):
            axis = "y"
        thickness = float(slice_cfg.get("slice_thickness") or 0.002)
        if thickness <= 0:
            thickness = 0.002
        min_r = float(slice_cfg.get("min_slice_particle_radius") or 1e-5)
        if min_r < 0:
            min_r = 0.0
        return cls(
            slice_axis=axis,
            slice_position=float(slice_cfg.get("slice_position") or 0.0),
            slice_thickness=thickness,
            min_slice_particle_radius=min_r,
            r_util=float(r_int),
            snap_radial_to_wall=bool(slice_cfg.get("snap_radial_to_wall", True)),
            preserve_original_packing=bool(
                slice_cfg.get("preserve_original_packing", True)
            ),
            keep_only_intersecting=bool(
                slice_cfg.get("keep_only_intersecting_particles", True)
            ),
        )


def sphere_intersects_slice(
    center: vec3,
    *,
    particle_kind: str,
    particle_diameter: float,
    slice_axis: str,
    slice_position: float,
    slice_thickness: float,
) -> bool:
    """partícula intersecta a faixa [slice_position ± slice_thickness/2]."""
    return particle_intersects_slice(
        center,
        particle_kind=particle_kind,
        particle_diameter=particle_diameter,
        axis=slice_axis,
        slice_position=slice_position,
        slice_thickness=slice_thickness,
    )


def distance_to_slice_plane(center: vec3, slice_axis: str, slice_position: float) -> float:
    ai = axis_index(slice_axis)
    return abs(float(center[ai]) - float(slice_position))


def compute_slice_radius(
    particle_kind: str,
    particle_diameter: float,
    distance_to_plane: float,
    *,
    slice_axis: str = "y",
) -> float:
    """raio aparente da secção esfera-plano; 0 se fora da esfera."""
    pk = (particle_kind or "sphere").strip().lower()
    d = float(particle_diameter)
    r = d * 0.5
    d_plane = abs(float(distance_to_plane))
    if pk == "sphere":
        return sphere_section_radius(r, d_plane)
    spec = slice_footprint_spec(
        pk, d, d_plane, slice_axis=slice_axis, slice_thickness=1e-9
    )
    if spec.get("shape") == "disc":
        return float(spec.get("radius") or 0.0)
    if spec.get("shape") == "box":
        sx = float(spec.get("size_x") or 0.0)
        sy = float(spec.get("size_y") or 0.0)
        sz = float(spec.get("size_z") or 0.0)
        return max(sx, sy, sz) * 0.5
    return 0.0


def prepare_slice_particle_for_mesh(
    center: vec3,
    particle_kind: str,
    particle_diameter: float,
    *,
    cfg: SliceParticleConfig,
    policy: str = "contained",
) -> Tuple[Optional[vec3], float, Dict[str, Any]]:
    """
    pipeline unificado de decisão + centro na lâmina (mesma ordem que aplicar_thin_slice no blender).
    devolve (centro_final, raio_aparente, meta) ou (None, 0, meta) se descartada.
    """
    meta: Dict[str, Any] = {"included": False}
    pk = (particle_kind or "sphere").strip().lower()
    d = float(particle_diameter)
    c = (float(center[0]), float(center[1]), float(center[2]))

    if not particle_passes_policy(
        c,
        particle_kind=pk,
        particle_diameter=d,
        slice_axis=cfg.slice_axis,
        slice_center=cfg.slice_position,
        slice_thickness=cfg.slice_thickness,
        r_util=cfg.r_util,
        policy=policy,
    ):
        meta["reason"] = DROP_POLICY
        return None, 0.0, meta

    if not sphere_intersects_slice(
        c,
        particle_kind=pk,
        particle_diameter=d,
        slice_axis=cfg.slice_axis,
        slice_position=cfg.slice_position,
        slice_thickness=cfg.slice_thickness,
    ):
        meta["reason"] = DROP_OUTSIDE_SLICE
        return None, 0.0, meta

    d_plane = distance_to_slice_plane(c, cfg.slice_axis, cfg.slice_position)
    rs = compute_slice_radius(pk, d, d_plane, slice_axis=cfg.slice_axis)
    if rs < cfg.min_slice_particle_radius:
        meta["reason"] = DROP_BELOW_MIN_RADIUS
        meta["apparent_radius"] = rs
        return None, 0.0, meta

    cx, cy, cz = align_center_to_slice_plane(
        c,
        slice_axis=cfg.slice_axis,
        slice_position=cfg.slice_position,
        preserve_original_packing=cfg.preserve_original_packing,
    )
    snapped = False
    if cfg.snap_radial_to_wall:
        rho = math.hypot(cx, cy)
        if rho + rs > cfg.r_util + 1e-9:
            cx, cy, cz = snap_center_radial_to_util_wall(
                (cx, cy, cz), cfg.r_util, rs
            )
            snapped = True

    rho_final = math.hypot(cx, cy)
    if rho_final + rs > cfg.r_util + 1e-6:
        meta["reason"] = DROP_LEAK_RADIAL
        meta["center_final"] = [cx, cy, cz]
        meta["apparent_radius"] = rs
        return None, 0.0, meta

    r_mesh = max(rs, collision_radius_for_particle_kind(pk, d) * 0.25)
    meta.update(
        {
            "included": True,
            "reason": "keep",
            "apparent_radius": rs,
            "distance_to_plane": d_plane,
            "snapped_to_wall": snapped,
            "center_final": [cx, cy, cz],
            "mesh_radius": r_mesh,
        }
    )
    return (cx, cy, cz), r_mesh, meta


def align_center_to_slice_plane(
    center: vec3,
    *,
    slice_axis: str,
    slice_position: float,
    preserve_original_packing: bool = True,
) -> vec3:
    """
    coloca o centro na lâmina (coordenada no eixo da fatia = slice_position).

    preserve_original_packing=true no json: mantém o layout no plano da fatia
    (x,z para slice_axis=y) e projeta na lâmina — mesma semântica do commit 7868234
    (preserve_other_coords).
    false: mantém também a coordenada fora do plano (empacotamento 3d bruto).
    """
    return slice_footprint_center(
        center,
        slice_axis=slice_axis,
        slice_position=slice_position,
        preserve_original_packing=not preserve_original_packing,
    )


def create_slice_cylinder_mesh(
    particle_kind: str,
    center: vec3,
    particle_diameter: float,
    *,
    cfg: SliceParticleConfig,
    segmentos: int = 24,
    policy: str = "contained",
) -> Tuple[List[vec3], List[tri], Dict[str, Any]]:
    """
    gera malha do disco/cilindro fino no eixo da fatia.
    devolve (vertices, faces, meta) ou ([], [], meta) se descartada.
    """
    pk = (particle_kind or "sphere").strip().lower()
    d = float(particle_diameter)
    loc, r_mesh, meta = prepare_slice_particle_for_mesh(
        center, pk, d, cfg=cfg, policy=policy
    )
    if loc is None:
        return [], [], meta

    cx, cy, cz = loc
    d_plane = float(meta.get("distance_to_plane") or 0.0)
    r_app = float(meta.get("apparent_radius") or r_mesh)
    seg = max(12, min(32, segmentos))
    t = cfg.slice_thickness
    spec = slice_footprint_spec(
        pk, d, d_plane, slice_axis=cfg.slice_axis, slice_thickness=t
    )

    if spec.get("shape") == "none":
        meta["reason"] = "no_footprint"
        meta["included"] = False
        return [], [], meta

    if spec.get("shape") == "disc":
        rs = float(spec.get("radius") or r_mesh)
        sv, sf = cylinder_axis(
            cx, cy, cz, rs, t, axis=cfg.slice_axis, segments=seg
        )
    elif spec.get("shape") == "box":
        sv, sf = box_mesh_anisotropic(
            cx,
            cy,
            cz,
            float(spec["size_x"]),
            float(spec["size_y"]),
            float(spec["size_z"]),
        )
    else:
        meta["reason"] = "unknown_shape"
        return [], [], meta

    meta.update(
        {
            "included": True,
            "apparent_radius": r_app,
            "distance_to_plane": d_plane,
            "snapped_to_wall": bool(meta.get("snapped_to_wall")),
            "center_final": [cx, cy, cz],
        }
    )
    return sv, sf, meta


def validate_slice_particle_vertices(
    vertices: List[vec3],
    *,
    slice_axis: str,
    slice_position: float,
    slice_thickness: float,
    r_util: Optional[float] = None,
) -> bool:
    """true se todos os vértices estão dentro da faixa do corte (e opcionalmente r_util)."""
    if not vertices:
        return True
    lo = slice_position - slice_thickness / 2.0
    hi = slice_position + slice_thickness / 2.0
    ai = axis_index(slice_axis)
    for p in vertices:
        s = p[ai]
        if s < lo - 1e-8 or s > hi + 1e-8:
            return False
        if r_util is not None and math.hypot(p[0], p[1]) > float(r_util) + 1e-8:
            return False
    return True


def process_slice_particles(
    centers: List[vec3],
    *,
    particle_kind: str,
    particle_diameter: float,
    cfg: SliceParticleConfig,
    segmentos: int = 24,
    policy: str = "contained",
) -> Tuple[List[vec3], List[tri], SliceParticleSummary]:
    """processa todos os centros e devolve malha agregada + resumo."""
    pk = (particle_kind or "sphere").strip().lower()
    d = float(particle_diameter)
    v_all: List[vec3] = []
    f_all: List[tri] = []
    radii_kept: List[float] = []

    summary: SliceParticleSummary = {
        "slice_axis": cfg.slice_axis,
        "slice_position": cfg.slice_position,
        "slice_thickness": cfg.slice_thickness,
        "min_slice_particle_radius": cfg.min_slice_particle_radius,
        "original_particle_count": len(centers),
        "intersecting_particle_count": 0,
        "n_kept": 0,
        "n_dropped_outside_slice": 0,
        "n_discarded_by_radius_threshold": 0,
        "n_snapped_to_wall": 0,
        "n_full_3d_outside": 0,
        "leak_count": 0,
    }

    for center in centers:
        c = (float(center[0]), float(center[1]), float(center[2]))
        sv, sf, meta = create_slice_cylinder_mesh(
            pk, c, d, cfg=cfg, segmentos=segmentos, policy=policy
        )
        if not sv:
            reason = meta.get("reason")
            if reason == DROP_OUTSIDE_SLICE:
                summary["n_dropped_outside_slice"] = (
                    int(summary["n_dropped_outside_slice"]) + 1
                )
            elif reason == DROP_POLICY:
                summary["n_dropped_policy"] = int(summary.get("n_dropped_policy") or 0) + 1
            elif reason == DROP_BELOW_MIN_RADIUS:
                summary["n_discarded_by_radius_threshold"] = (
                    int(summary["n_discarded_by_radius_threshold"]) + 1
                )
            elif reason == DROP_LEAK_RADIAL:
                summary["leak_count"] = int(summary["leak_count"]) + 1
                summary["n_dropped_policy"] = int(summary.get("n_dropped_policy") or 0) + 1
            continue

        summary["intersecting_particle_count"] = (
            int(summary["intersecting_particle_count"]) + 1
        )

        if meta.get("snapped_to_wall"):
            summary["n_snapped_to_wall"] = int(summary["n_snapped_to_wall"]) + 1

        if not validate_slice_particle_vertices(
            sv,
            slice_axis=cfg.slice_axis,
            slice_position=cfg.slice_position,
            slice_thickness=cfg.slice_thickness,
            r_util=cfg.r_util,
        ):
            summary["leak_count"] = int(summary["leak_count"]) + 1
            continue

        v_all, f_all = merge_mesh(v_all, f_all, sv, sf)
        summary["n_kept"] = int(summary["n_kept"]) + 1
        radii_kept.append(float(meta.get("apparent_radius") or 0.0))

    if radii_kept:
        summary["min_slice_radius"] = min(radii_kept)
        summary["max_slice_radius"] = max(radii_kept)
        summary["average_slice_radius"] = sum(radii_kept) / len(radii_kept)
    else:
        summary["min_slice_radius"] = None
        summary["max_slice_radius"] = None
        summary["average_slice_radius"] = None

    return v_all, f_all, summary


def blender_cylinder_rotation(slice_axis: str) -> Tuple[float, float, float]:
    """ângulos euler xyz (rad) para cilindro bpy alinhado ao slice_axis."""
    ax = slice_axis.strip().lower()
    if ax == "z":
        return (0.0, 0.0, 0.0)
    if ax == "y":
        return (math.pi / 2.0, 0.0, 0.0)
    return (0.0, math.pi / 2.0, 0.0)


__all__ = [
    "SliceParticleConfig",
    "DROP_BELOW_MIN_RADIUS",
    "DROP_LEAK_RADIAL",
    "DROP_OUTSIDE_SLICE",
    "DROP_POLICY",
    "align_center_to_slice_plane",
    "blender_cylinder_rotation",
    "compute_slice_radius",
    "create_slice_cylinder_mesh",
    "distance_to_slice_plane",
    "prepare_slice_particle_for_mesh",
    "process_slice_particles",
    "sphere_intersects_slice",
    "validate_slice_particle_vertices",
]
