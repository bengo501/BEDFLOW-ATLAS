# pipeline unificado: packing -> malha -> export
from __future__ import annotations

import sys
import time
from pathlib import Path
from typing import Any, Dict, List, Tuple

_PMDIR = Path(__file__).resolve().parent.parent
_SCRIPTS = _PMDIR.parent / "blender_scripts"
if str(_PMDIR) not in sys.path:
    sys.path.insert(0, str(_PMDIR))
if str(_SCRIPTS) not in sys.path:
    sys.path.insert(0, str(_SCRIPTS))

from packed_bed_science.geometry_math import collision_radius_for_particle_kind  # noqa: E402
from packed_bed_science.packing_hexagonal import generate_hexagonal_packing  # noqa: E402
from packed_bed_science.packing_spherical import generate_spherical_packing  # noqa: E402
from packed_bed_science.validation import validate_configuration  # noqa: E402

from bed_internal_modes import bed_internal_sidecar, validate_bed_geometry_mode  # noqa: E402
from geometry_modes import (  # noqa: E402
    GEOMETRY_STATISTICAL,
    compute_thin_slice_porosity,
    geometry_mode_from_data,
    resolve_slice_config,
    validate_geometry_contract,
)
from pseudo_2d_statistical import generate_statistical_thin_3d_stl  # noqa: E402
from pure_bed_mesh import build_packed_bed_model, export_model_data  # noqa: E402
from thin_slice_build import apply_thin_slice_mesh, slice_cfg_active  # noqa: E402

from .dem_solver import run_dem_packing
from .domain import PackedBedDomain
from .reports import PackingResult, write_packing_report
from .rigid_body import run_rigid_body_packing

vec3 = Tuple[float, float, float]


def _to_float(v: Any, default: float = 0.0) -> float:
    if v is None:
        return float(default)
    if isinstance(v, (int, float)):
        return float(v)
    return float(str(v).replace(",", "."))


def _to_int(v: Any, default: int = 0) -> int:
    if v is None:
        return int(default)
    if isinstance(v, int):
        return v
    if isinstance(v, float):
        return int(v)
    return int(float(str(v).replace(",", ".")))


def _porosity_volume_kind(
    domain: PackedBedDomain,
    centers: List[vec3],
) -> float:
    import math

    ann = domain.annulus
    v_void = ann.annulus_volume_void()
    if v_void <= 0:
        return 0.0
    n = len(centers)
    d = domain.particle_diameter
    k = domain.particle_kind
    if k == "cube":
        v_part = n * d * d * d
    elif k == "cylinder":
        v_part = n * math.pi * (d / 2.0) ** 2 * d
    else:
        v_part = n * (4.0 / 3.0) * math.pi * (d / 2.0) ** 3
    return max(0.0, min(1.0, 1.0 - v_part / v_void))


def run_packing(p: Dict[str, Any]) -> PackingResult:
    """executa apenas o empacotamento (centros + metadados)."""
    domain = PackedBedDomain.from_bed_params(p)
    ann = domain.annulus
    method = str(p.get("packing_method") or "rigid_body")
    pk = domain.particle_kind
    n_req = int(p["particle_count"])
    warnings: List[str] = []
    t0 = time.perf_counter()
    packing = dict(p.get("packing") or {})

    use_legacy = _to_bool(packing.get("use_legacy_drop"), False)

    if method == "dem":
        centers, gen_meta = run_dem_packing(domain, n_req, packing, warnings=warnings)
        collisions = int(gen_meta.get("collisions_checked", 0))
    elif method == "rigid_body" and not use_legacy:
        centers, gen_meta = run_rigid_body_packing(domain, n_req, packing, warnings=warnings)
        collisions = int(gen_meta.get("collisions_checked", 0))
    elif method == "spherical_packing":
        seed = p.get("random_seed")
        if seed is None:
            seed = p.get("particles_seed")
        seed_i = _to_int(seed, 42) if seed is not None else None
        r_pack = collision_radius_for_particle_kind(pk, domain.particle_diameter)
        gen = generate_spherical_packing(
            ann,
            n_req,
            r_pack,
            domain.gap,
            random_seed=seed_i,
            max_placement_attempts=_to_int(p.get("max_placement_attempts"), 500_000),
        )
        centers = gen["centers"]
        gen_meta = {k: v for k, v in gen.items() if k != "centers"}
        collisions = int(gen.get("attempts", 0))
    elif method == "hexagonal_3d":
        r_pack = collision_radius_for_particle_kind(pk, domain.particle_diameter)
        step_x_opt = p.get("step_x")
        step_x_f = _to_float(step_x_opt, 0.0) if step_x_opt is not None else None
        if step_x_f is not None and step_x_f <= 0:
            step_x_f = None
        gen = generate_hexagonal_packing(
            ann, n_req, r_pack, domain.gap, step_x=step_x_f
        )
        centers = gen["centers"]
        gen_meta = {k: v for k, v in gen.items() if k != "centers"}
        collisions = 0
    else:
        raise ValueError(f"packing_method nao suportado no motor python: {method}")

    elapsed = time.perf_counter() - t0
    r_pack = collision_radius_for_particle_kind(pk, domain.particle_diameter)
    radii = [r_pack] * len(centers)
    report_val = validate_configuration(centers, radii, ann, domain.gap)
    poros = _porosity_volume_kind(domain, centers)

    strict = bool(p.get("strict_validation", True))
    validation_ok = bool(report_val.get("ok", False))
    if not validation_ok and strict:
        raise RuntimeError(
            "validacao geometrica falhou: " + str(report_val.get("messages", []))[:500]
        )
    if method == "spherical_packing" and len(centers) < n_req and strict:
        raise RuntimeError(
            f"spherical packing so colocou {len(centers)} de {n_req}"
        )

    return PackingResult(
        centers=centers,
        method=method,
        particle_type=pk,
        n_requested=n_req,
        n_placed=len(centers),
        porosity=poros,
        validation_ok=validation_ok,
        collisions_checked=collisions,
        wall_violations=int(report_val.get("domain_violations", 0) or 0),
        elapsed_sec=elapsed,
        metadata={
            "generation": gen_meta,
            "validation": report_val,
            "collision_radius_equiv": r_pack,
            "collision_model": "circumscribed_sphere",
        },
        warnings=warnings,
    )


def _to_bool(v: Any, default: bool = True) -> bool:
    if v is None:
        return default
    if isinstance(v, bool):
        return v
    s = str(v).strip().lower()
    if s in ("true", "1", "yes", "sim"):
        return True
    if s in ("false", "0", "no", "nao"):
        return False
    return default


def _build_and_export_mesh(
    p: Dict[str, Any],
    result: PackingResult,
    out_stl: Path,
) -> None:
    domain = PackedBedDomain.from_bed_params(p)
    r_ext = domain.r_ext
    r_int = domain.r_int
    centers = result.centers
    pk = result.particle_type
    d_char = domain.particle_diameter
    tb = domain.bottom_cap_thickness
    tt = domain.top_cap_thickness
    seg = min(64, max(12, _to_int(p.get("mesh_segmentos"), 48)))
    validate_geometry_contract(p, mutate=True)
    gm = geometry_mode_from_data(p)
    slice_cfg = resolve_slice_config(p)
    bed_mode_notes = validate_bed_geometry_mode(p, gm)

    if not slice_cfg_active(slice_cfg):
        packed = build_packed_bed_model(
            r_ext=r_ext,
            r_int=r_int,
            height=domain.height,
            bottom_cap_thickness=tb,
            top_cap_thickness=tt,
            particle_centers=centers,
            particle_diameter=d_char,
            particle_kind=pk,
            segmentos_cil=seg,
            lat_sphere=_to_int(p.get("sphere_lat"), 4),
            lon_sphere=_to_int(p.get("sphere_lon"), 6),
            bed_config=p,
        )
    else:
        shell = build_packed_bed_model(
            r_ext=r_ext,
            r_int=r_int,
            height=domain.height,
            bottom_cap_thickness=tb,
            top_cap_thickness=tt,
            particle_centers=[],
            particle_diameter=d_char,
            particle_kind=pk,
            segmentos_cil=seg,
            lat_sphere=_to_int(p.get("sphere_lat"), 4),
            lon_sphere=_to_int(p.get("sphere_lon"), 6),
            bed_config=p,
        )
        v_all, f_all = apply_thin_slice_mesh(
            shell.mesh.vertices,
            shell.mesh.faces,
            centers,
            particle_diameter=d_char,
            particle_kind=pk,
            r_ext=r_ext,
            r_int=r_int,
            slice_cfg=slice_cfg,
            segmentos=seg,
        )
        packed = type(shell)(
            mesh=type(shell.mesh)(vertices=v_all, faces=f_all), meta=shell.meta
        )

    preview_n = 12
    extra: Dict[str, Any] = {
        **result.to_dict(),
        "porosity_estimate": result.porosity,
        "validation": result.metadata.get("validation"),
        "generation": result.metadata.get("generation"),
        "generation_wall_time_sec": result.elapsed_sec,
        "gap_convention": "center_distance >= r1+r2+gap",
        "particle_centers_preview": [
            [float(c[0]), float(c[1]), float(c[2])] for c in centers[:preview_n]
        ],
        "geometry_mode": gm,
        "generation_backend": p.get("generation_backend"),
    }
    if slice_cfg_active(slice_cfg):
        extra["slice"] = slice_cfg
        p_slice, slice_poro_meta = compute_thin_slice_porosity(
            centers,
            pk,
            d_char,
            slice_axis=str(slice_cfg.get("slice_axis", "y")),
            slice_position=float(slice_cfg.get("slice_position", 0.0)),
            slice_thickness=float(slice_cfg.get("slice_thickness", 0.002)),
            r_int=r_int,
            r_ext=r_ext,
        )
        extra["porosity_slice_plane"] = p_slice
        extra["porosity_result"] = p_slice
        extra["porosity_estimate"] = p_slice
        extra["porosity_slice_meta"] = slice_poro_meta
        if result.porosity is not None:
            extra["porosity_packing_3d"] = result.porosity

    sidecar = bed_internal_sidecar(
        p, backend="python_engine", r_int=r_int, r_ext=r_ext
    )
    st = sidecar.get("boolean_operation_status") or {}
    if bed_mode_notes:
        st = dict(st)
        st["warnings"] = list(st.get("warnings") or []) + bed_mode_notes
        sidecar["boolean_operation_status"] = st
    extra.update(sidecar)
    if isinstance(packed.meta, dict):
        for k in ("internal_cylinder_mode", "visibility", "boolean_operation_status"):
            if k in packed.meta and k not in extra:
                extra[k] = packed.meta[k]

    out_json = out_stl.parent / f"{out_stl.stem}_pure_bed.json"
    report_path = out_stl.parent / f"{out_stl.stem}_packing_report.json"
    write_packing_report(result, report_path)
    extra["packing_report_path"] = str(report_path)
    export_model_data(packed, out_stl, out_json=out_json, extra=extra)


def generate_packed_bed(p: Dict[str, Any], out_stl: Path) -> PackingResult:
    validate_geometry_contract(p, mutate=True)
    gm = geometry_mode_from_data(p)
    if gm == GEOMETRY_STATISTICAL:
        generate_statistical_thin_3d_stl(p, out_stl)
        return PackingResult(
            centers=[],
            method="statistical_reconstruction",
            particle_type=str(p.get("particle_kind") or "sphere"),
            n_requested=int(p.get("particle_count", 0)),
            n_placed=0,
            porosity=float((p.get("statistical_2d") or {}).get("target_porosity", 0.4)),
            validation_ok=True,
            metadata={"geometry_mode": gm},
        )

    result = run_packing(p)
    _build_and_export_mesh(p, result, out_stl)
    return result
