# construção do leito conforme internal_cylinder_mode (python_engine)
from __future__ import annotations

import logging
from typing import Any, Dict, List, Optional, Tuple

from bed_internal_modes import (
    MODE_HOLLOW_BOOLEAN,
    MODE_SOLID_HOLES,
    MODE_VISIBLE_INNER,
    build_boolean_operation_status,
    normalize_internal_cylinder_mode,
    resolve_bed_internal_config,
)
from pure_bed_mesh import (
    MeshData,
    create_cap_geometry,
    create_hollow_cylinder_geometry,
    meshdata_to_lists,
)
from stl_mesh_utils import cylinder_axis, merge_mesh, vec3

logger = logging.getLogger(__name__)


def _solid_cylinder_mesh(
    r: float, height: float, segmentos: int = 48
) -> Tuple[List[vec3], List[tuple]]:
    cz = height / 2.0
    v, f = cylinder_axis(0.0, 0.0, cz, r, height, axis="z", segments=segmentos)
    return list(v), list(f)


def build_bed_shell(
    mode: str,
    r_ext: float,
    r_int: float,
    height: float,
    visibility: Dict[str, bool],
    *,
    segmentos: int = 48,
    bottom_cap_thickness: float = 0.0,
    top_cap_thickness: float = 0.0,
) -> Tuple[List[vec3], List[tuple], Dict[str, Any]]:
    """
    malha do leito (tubo, caps, núcleo) sem partículas.
    devolve vertices, faces, meta parcial.
    """
    m = normalize_internal_cylinder_mode(mode)
    show_outer = visibility.get("show_outer_cylinder", True)
    show_inner = visibility.get("show_internal_cylinder", False)
    v: List[vec3] = []
    f: List[tuple] = []
    components: List[str] = []

    if show_outer and r_int < r_ext and height > 0:
        body = create_hollow_cylinder_geometry(
            r_ext, r_int, height, segmentos=segmentos
        )
        v, f = meshdata_to_lists(body)
        components.append("annulus_shell")

    if bottom_cap_thickness > 0 and show_outer:
        z_inf = bottom_cap_thickness / 2.0
        cap_i = create_cap_geometry(r_ext, bottom_cap_thickness, z_inf, segmentos)
        v, f = merge_mesh(v, f, cap_i.vertices, cap_i.faces)
        components.append("bottom_cap")
    if top_cap_thickness > 0 and show_outer:
        z_sup = height - top_cap_thickness / 2.0
        cap_s = create_cap_geometry(r_ext, top_cap_thickness, z_sup, segmentos)
        v, f = merge_mesh(v, f, cap_s.vertices, cap_s.faces)
        components.append("top_cap")

    outer_status = "explicit_annulus"
    if m == MODE_VISIBLE_INNER:
        outer_status = "fallback_separate_meshes"
    inner_status = "n/a"
    if m == MODE_VISIBLE_INNER:
        inner_status = "visible_separate"
    elif m == MODE_SOLID_HOLES:
        inner_status = "solid_with_holes"

    meta = {
        "shell_components": components,
        "boolean_operation_status": build_boolean_operation_status(
            m,
            backend="python_engine",
            outer_shell=outer_status,
            inner_core=inner_status,
            particle_tools="n/a",
            r_int=r_int,
            r_ext=r_ext,
        ),
    }
    return v, f, meta


def punch_holes_in_solid(
    core_v: List[vec3],
    core_f: List[tuple],
    particle_centers: List[vec3],
    particle_kind: str,
    particle_diameter: float,
    *,
    max_holes: Optional[int] = None,
) -> Tuple[List[vec3], List[tuple], str, List[str]]:
    """
    tenta boolean difference com trimesh; devolve mesh, status, warnings.
    """
    warnings: List[str] = []
    if not core_v or not core_f or not particle_centers:
        return core_v, core_f, "n/a", warnings

    try:
        import trimesh  # type: ignore
    except ImportError:
        warnings.append("trimesh nao instalado: nucleo solido sem furos booleanos")
        return core_v, core_f, "failed", warnings

    try:
        core = trimesh.Trimesh(vertices=core_v, faces=core_f, process=False)
        if not core.is_watertight:
            core.fix_normals()
        result = core
        if max_holes is None:
            n = len(particle_centers)
        else:
            n = min(len(particle_centers), max(0, int(max_holes)))
            if len(particle_centers) > n:
                warnings.append(
                    f"furos limitados a {n} de {len(particle_centers)} particulas (desempenho)"
                )
        pk = (particle_kind or "sphere").strip().lower()
        r = particle_diameter / 2.0
        engines = ("manifold", "blender")
        holes_ok = 0
        for c in particle_centers[:n]:
            cx, cy, cz = c
            if pk == "cube":
                tool = trimesh.creation.box(extents=(particle_diameter,) * 3)
                tool.apply_translation([cx, cy, cz])
            elif pk == "cylinder":
                tool = trimesh.creation.cylinder(
                    radius=r, height=particle_diameter, sections=16
                )
                tool.apply_translation([cx, cy, cz])
            else:
                tool = trimesh.creation.icosphere(radius=r, subdivisions=1)
                tool.apply_translation([cx, cy, cz])
            hole_applied = False
            for eng in engines:
                try:
                    result = result.difference(tool, engine=eng)
                    hole_applied = True
                    holes_ok += 1
                    break
                except Exception as exc:
                    if eng == engines[-1]:
                        warnings.append(
                            f"difference falhou em ({cx:.4f},{cy:.4f},{cz:.4f}): {exc}"
                        )
        if holes_ok == 0:
            warnings.append("nenhuma booleana de furo aplicada no nucleo")
        if result is None or len(getattr(result, "vertices", [])) == 0:
            warnings.append("difference resultou malha vazia")
            return core_v, core_f, "failed", warnings
        return (
            result.vertices.tolist(),
            result.faces.tolist(),
            "applied",
            warnings,
        )
    except Exception as exc:
        warnings.append(f"trimesh boolean: {exc}")
        return core_v, core_f, "failed", warnings


def _particle_tool_mesh(
    cx: float,
    cy: float,
    cz: float,
    particle_kind: str,
    particle_diameter: float,
) -> Tuple[List[vec3], List[tuple]]:
    """malha de uma ferramenta/partícula para union ou difference."""
    pk = (particle_kind or "sphere").strip().lower()
    r = particle_diameter / 2.0
    if pk == "cube":
        from stl_mesh_utils import box_mesh

        return box_mesh(cx, cy, cz, particle_diameter)
    if pk == "cylinder":
        return cylinder_axis(cx, cy, cz, r, particle_diameter, axis="z", segments=16)
    from stl_mesh_utils import uv_sphere

    return uv_sphere(cx, cy, cz, r, lat=4, lon=6)


def fuse_core_with_particles(
    core_v: List[vec3],
    core_f: List[tuple],
    particle_centers: List[vec3],
    particle_kind: str,
    particle_diameter: float,
) -> Tuple[List[vec3], List[tuple], str, List[str]]:
    """
    m2: núcleo sólido fundido com partículas (pudim) via trimesh union.
    """
    warnings: List[str] = []
    if not core_v or not core_f:
        return core_v, core_f, "n/a", warnings
    if not particle_centers:
        return core_v, core_f, "n/a", warnings

    try:
        import trimesh  # type: ignore
    except ImportError:
        warnings.append("trimesh nao instalado: exportando nucleo e particulas separados")
        v, f = list(core_v), list(core_f)
        for c in particle_centers:
            pv, pf = _particle_tool_mesh(
                c[0], c[1], c[2], particle_kind, particle_diameter
            )
            v, f = merge_mesh(v, f, pv, pf)
        return v, f, "fallback_separate", warnings

    try:
        result = trimesh.Trimesh(vertices=core_v, faces=core_f, process=False)
        if not result.is_watertight:
            result.fix_normals()
        engines = ("manifold", "blender")
        fused = 0
        for c in particle_centers:
            pv, pf = _particle_tool_mesh(
                c[0], c[1], c[2], particle_kind, particle_diameter
            )
            tool = trimesh.Trimesh(vertices=pv, faces=pf, process=False)
            ok = False
            for eng in engines:
                try:
                    result = result.union(tool, engine=eng)
                    ok = True
                    fused += 1
                    break
                except Exception:
                    continue
            if not ok:
                warnings.append(
                    f"union falhou em ({c[0]:.4f},{c[1]:.4f},{c[2]:.4f})"
                )
        if fused == 0:
            warnings.append("nenhuma union aplicada no nucleo")
            return core_v, core_f, "failed", warnings
        return (
            result.vertices.tolist(),
            result.faces.tolist(),
            "applied",
            warnings,
        )
    except Exception as exc:
        warnings.append(f"trimesh union: {exc}")
        return core_v, core_f, "failed", warnings


def build_bed_with_internal_mode(
    data: Dict[str, Any],
    r_ext: float,
    r_int: float,
    height: float,
    bottom_cap_thickness: float,
    top_cap_thickness: float,
    particle_centers: List[vec3],
    particle_diameter: float,
    particle_kind: str,
    *,
    segmentos: int = 48,
    lat_sphere: int = 4,
    lon_sphere: int = 6,
) -> Tuple[List[vec3], List[tuple], Dict[str, Any]]:
    """leito completo (shell + partículas opcionais) para export."""
    from pure_bed_mesh import _append_particle_mesh

    mode, vis, _ = resolve_bed_internal_config(data)
    v, f, meta = build_bed_shell(
        mode,
        r_ext,
        r_int,
        height,
        vis,
        segmentos=segmentos,
        bottom_cap_thickness=bottom_cap_thickness,
        top_cap_thickness=top_cap_thickness,
    )
    status = dict(meta.get("boolean_operation_status") or {})
    warnings = list(status.get("warnings") or [])
    shell_components = list(meta.get("shell_components") or [])

    if mode == MODE_HOLLOW_BOOLEAN:
        status["inner_core"] = "n/a"
        status["particle_tools"] = "n/a"
        if vis.get("show_particles", True):
            pk = (particle_kind or "sphere").strip().lower()
            for c in particle_centers:
                v, f = _append_particle_mesh(
                    v,
                    f,
                    c[0],
                    c[1],
                    c[2],
                    particle_diameter,
                    pk,
                    lat_sphere,
                    lon_sphere,
                )
            shell_components.append("particles_in_annulus")

    elif mode == MODE_VISIBLE_INNER:
        status["outer_shell"] = status.get("outer_shell") or "fallback_separate_meshes"
        show_inner = vis.get("show_internal_cylinder", True)
        show_parts = vis.get("show_particles", True)
        if show_inner and r_int > 0:
            cv, cf = _solid_cylinder_mesh(r_int, height, segmentos)
            pv, pf, pstat, pw = fuse_core_with_particles(
                cv,
                cf,
                particle_centers,
                particle_kind,
                particle_diameter,
            )
            warnings.extend(pw)
            status["particle_tools"] = pstat
            status["inner_core"] = "fused_with_particles"
            v, f = merge_mesh(v, f, pv, pf)
            shell_components.append("inner_pudding_fused")
        elif show_parts:
            pk = (particle_kind or "sphere").strip().lower()
            for c in particle_centers:
                v, f = _append_particle_mesh(
                    v,
                    f,
                    c[0],
                    c[1],
                    c[2],
                    particle_diameter,
                    pk,
                    lat_sphere,
                    lon_sphere,
                )
            status["inner_core"] = "n/a"
            status["particle_tools"] = "n/a"
            shell_components.append("particles_in_annulus")
        else:
            status["inner_core"] = "n/a"
            status["particle_tools"] = "n/a"

    elif mode == MODE_SOLID_HOLES:
        cv, cf = _solid_cylinder_mesh(r_int, height, segmentos)
        n_req = len(particle_centers)
        status["inner_core"] = "solid_with_holes"
        if n_req > 0:
            pv, pf, pstat, pw = punch_holes_in_solid(
                cv,
                cf,
                particle_centers,
                particle_kind,
                particle_diameter,
                max_holes=None,
            )
            warnings.extend(pw)
            status["particle_tools"] = pstat
            status["n_holes_requested"] = n_req
            status["n_holes_applied"] = (
                n_req if pstat == "applied" else 0
            )
            if vis.get("show_internal_cylinder", True):
                v, f = merge_mesh(v, f, pv, pf)
                shell_components.append("inner_core_perforated")
            else:
                status["inner_core"] = "solid_with_holes_omitted_from_export"
        else:
            status["particle_tools"] = "n/a"
            if vis.get("show_internal_cylinder", True):
                v, f = merge_mesh(v, f, cv, cf)
                shell_components.append("inner_core_solid")
        status["warnings"] = warnings

    meta["internal_cylinder_mode"] = mode
    meta["visibility"] = vis
    meta["shell_components"] = shell_components
    meta["boolean_operation_status"] = status
    meta["n_particles"] = len(particle_centers)
    meta["particle_kind"] = (particle_kind or "sphere").strip().lower()
    meta["r_ext"] = r_ext
    meta["r_int"] = r_int
    meta["height"] = height
    logger.info("bed shell mode=%s status=%s", mode, status)
    return v, f, meta
