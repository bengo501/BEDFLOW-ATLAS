# reconstrucao 2d estatistica (rsa) + extrusao para lamina 3d fina
from __future__ import annotations

import math
import random
import time
from pathlib import Path
from typing import Any, Dict, List, Tuple

from geometry_modes import (
    GEOMETRY_STATISTICAL,
    compute_axial_porosity_profile_2d,
    compute_global_porosity_2d_raster,
    compute_radial_porosity_profile_2d,
    compute_two_point_correlation_2d,
    resolve_statistical_config,
)
from pure_bed_mesh import MeshData, PackedBedModel, export_model_data
from stl_mesh_utils import cylinder_axis, merge_mesh, tri, vec3, write_stl_binary

vec2 = Tuple[float, float]


def _discs_overlap(c1: vec2, c2: vec2, r: float) -> bool:
    return math.hypot(c1[0] - c2[0], c1[1] - c2[1]) < 2.0 * r - 1e-12


def _random_disc_centers_rsa(
    *,
    width: float,
    height: float,
    radius: float,
    target_count: int,
    rng: random.Random,
    max_place_attempts: int,
) -> List[vec2]:
    centers: List[vec2] = []
    attempts = 0
    margin = radius
    while len(centers) < target_count and attempts < max_place_attempts:
        attempts += 1
        x = rng.uniform(margin, width - margin)
        y = rng.uniform(margin, height - margin)
        c = (x, y)
        if any(_discs_overlap(c, o, radius) for o in centers):
            continue
        centers.append(c)
    return centers


def _estimate_disc_count(target_porosity: float, width: float, height: float, radius: float) -> int:
    area = width * height
    disc_area = math.pi * radius * radius
    solid_frac = max(0.05, min(0.95, 1.0 - target_porosity))
    return max(1, int(area * solid_frac / disc_area))


def generate_statistical_2d_centers(
    stat_cfg: Dict[str, Any],
) -> Tuple[List[vec2], Dict[str, Any]]:
    w = float(stat_cfg["domain_width"])
    h = float(stat_cfg["domain_height"])
    target = float(stat_cfg["target_porosity"])
    tol = float(stat_cfg["tolerance"])
    max_attempts = int(stat_cfg["max_attempts"])
    d_part = float(stat_cfg["particle_diameter"])
    r = d_part / 2.0
    seed = int(stat_cfg.get("seed", 42))

    rng = random.Random(seed)
    n_target = _estimate_disc_count(target, w, h, r)
    best_centers: List[vec2] = []
    best_porosity = 0.0
    best_err = 1.0
    best_raster_meta: Dict[str, Any] = {}

    for attempt in range(max(1, max_attempts)):
        n_try = max(1, n_target + attempt - max_attempts // 2)
        centers = _random_disc_centers_rsa(
            width=w,
            height=h,
            radius=r,
            target_count=n_try,
            rng=rng,
            max_place_attempts=min(5000, max(500, n_try * 200)),
        )
        porosity, raster_meta = compute_global_porosity_2d_raster(centers, r, w, h)
        err = abs(porosity - target)
        if err < best_err:
            best_err = err
            best_porosity = porosity
            best_centers = centers
            best_raster_meta = raster_meta
        if err <= tol:
            break
        if porosity > target:
            n_target = max(1, n_target - 1)
        else:
            n_target = n_target + 1

    meta = {
        "porosity_target": target,
        "porosity_result": best_porosity,
        "porosity_error": best_err,
        "porosity_method": best_raster_meta.get("porosity_method", "raster"),
        "raster_nx": best_raster_meta.get("raster_nx"),
        "raster_ny": best_raster_meta.get("raster_ny"),
        "raster_cell_m": best_raster_meta.get("raster_cell_m"),
        "solid_fraction": best_raster_meta.get("solid_fraction"),
        "n_discs": len(best_centers),
        "domain_width": w,
        "domain_height": h,
    }
    return best_centers, meta


def extrude_statistical_to_thin_3d(
    centers: List[vec2],
    *,
    domain_width: float,
    domain_height: float,
    particle_diameter: float,
    slice_thickness: float,
    wall_thickness: float = 0.002,
) -> Tuple[List[vec3], List[tri]]:
    """canal fino retangular + discos como cilindros ao longo de z (espessura = slice_thickness)."""
    tw = slice_thickness
    r_disc = particle_diameter / 2.0
    wt = max(wall_thickness, tw * 0.5)
    # caixa oca simplificada: quatro paredes finas
    x0, x1 = 0.0, domain_width
    y0, y1 = 0.0, domain_height
    z0, z1 = 0.0, tw
    verts: List[vec3] = []
    faces: List[tri] = []

    def add_box(xa, xb, ya, yb, za, zb):
        nonlocal verts, faces
        box_v = [
            (xa, ya, za),
            (xb, ya, za),
            (xb, yb, za),
            (xa, yb, za),
            (xa, ya, zb),
            (xb, ya, zb),
            (xb, yb, zb),
            (xa, yb, zb),
        ]
        box_f = [
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
        off = len(verts)
        verts.extend(box_v)
        faces.extend([(a + off, b + off, c + off) for a, b, c in box_f])

    add_box(x0, x1, y0, y1, z0, z1)
    # parede fina perimetral (anel)
    add_box(x0, x0 + wt, y0, y1, z0, z1)
    add_box(x1 - wt, x1, y0, y1, z0, z1)
    add_box(x0, x1, y0, y0 + wt, z0, z1)
    add_box(x0, x1, y1 - wt, y1, z0, z1)

    seg = 16
    for (cx, cy) in centers:
        cv, cf = cylinder_axis(cx, cy, tw / 2.0, r_disc, tw, axis="z", segments=seg)
        verts, faces = merge_mesh(verts, faces, cv, cf)

    return verts, faces


def generate_statistical_thin_3d_stl(p: Dict[str, Any], out_stl: Path) -> None:
    data = {
        "geometry_mode": GEOMETRY_STATISTICAL,
        "statistical_2d": p.get("statistical_2d") or {},
        "bed": p.get("bed") or {
            "diameter": p.get("diameter"),
            "height": p.get("height"),
        },
        "particles": {
            "diameter": p.get("particle_diameter"),
            "target_porosity": (p.get("statistical_2d") or {}).get("target_porosity"),
            "seed": (p.get("statistical_2d") or {}).get("seed"),
        },
    }
    stat_cfg = resolve_statistical_config(data)
    if not stat_cfg:
        stat_cfg = resolve_statistical_config(
            {
                "geometry_mode": GEOMETRY_STATISTICAL,
                "statistical_2d": p.get("statistical_2d", {}),
                "bed": {"diameter": p["diameter"], "height": p["height"]},
                "particles": {"diameter": p["particle_diameter"], "target_porosity": 0.4},
            }
        )

    t0 = time.perf_counter()
    centers, pack_meta = generate_statistical_2d_centers(stat_cfg)
    w = stat_cfg["domain_width"]
    h = stat_cfg["domain_height"]
    d_part = stat_cfg["particle_diameter"]
    tw = stat_cfg["slice_thickness"]
    r_disc = d_part / 2.0

    verts, faces = extrude_statistical_to_thin_3d(
        centers,
        domain_width=w,
        domain_height=h,
        particle_diameter=d_part,
        slice_thickness=tw,
        wall_thickness=p.get("wall_thickness", 0.002),
    )

    packed = PackedBedModel(
        mesh=MeshData(vertices=verts, faces=faces),
        meta={"geometry_mode": GEOMETRY_STATISTICAL},
    )

    axial = compute_axial_porosity_profile_2d(centers, r_disc, w, h)
    radial = compute_radial_porosity_profile_2d(centers, r_disc, w, h)
    tpc = compute_two_point_correlation_2d(centers, w, h)

    extra: Dict[str, Any] = {
        "geometry_mode": GEOMETRY_STATISTICAL,
        "packing_method": "statistical_reconstruction",
        "particle_kind": p.get("particle_kind", "sphere"),
        "statistical_2d": stat_cfg,
        "porosity_target": pack_meta["porosity_target"],
        "porosity_result": pack_meta["porosity_result"],
        "porosity_method": pack_meta.get("porosity_method", "raster"),
        "porosity_raster": {
            "nx": pack_meta.get("raster_nx"),
            "ny": pack_meta.get("raster_ny"),
            "cell_m": pack_meta.get("raster_cell_m"),
            "solid_fraction": pack_meta.get("solid_fraction"),
        },
        "porosity_axial_profile": axial,
        "porosity_radial_profile": radial,
        "two_point_correlation": tpc,
        "n_discs_placed": len(centers),
        "generation_wall_time_sec": time.perf_counter() - t0,
        "disc_centers_preview": [[c[0], c[1]] for c in centers[:50]],
    }
    out_json = out_stl.parent / f"{out_stl.stem}_pure_bed.json"
    export_model_data(packed, out_stl, out_json=out_json, extra=extra)
