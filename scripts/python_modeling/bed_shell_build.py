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
    r: float,
    height: float,
    segmentos: int = 48,
    *,
    z_bottom: Optional[float] = None,
    z_top: Optional[float] = None,
) -> Tuple[List[vec3], List[tuple]]:
    """núcleo sólido (cilindro maciço) ao longo de z.

    z_bottom/z_top delimitam o vão interno (entre as faces internas das tampas);
    quando None, ocupa toda a altura (compatibilidade). usado para evitar que o
    núcleo invada o volume das tampas.
    """
    z0 = 0.0 if z_bottom is None else float(z_bottom)
    z1 = float(height) if z_top is None else float(z_top)
    core_h = max(z1 - z0, 1e-6)
    cz = (z0 + z1) / 2.0
    v, f = cylinder_axis(0.0, 0.0, cz, r, core_h, axis="z", segments=segmentos)
    return list(v), list(f)


def _interior_span(
    height: float, bottom_cap_thickness: float, top_cap_thickness: float
) -> Tuple[float, float]:
    """vão interno do leito entre as faces internas das tampas (convenção python)."""
    z0 = max(0.0, float(bottom_cap_thickness))
    z1 = float(height) - max(0.0, float(top_cap_thickness))
    if z1 <= z0:
        # tampas maiores que o leito: degenera para o meio
        mid = float(height) / 2.0
        return mid - 1e-4, mid + 1e-4
    return z0, z1


def _as_trimesh_volume(vertices: List[vec3], faces: List[tuple]):
    """constrói um Trimesh reparado (volume estanque) para operações booleanas.

    devolve (trimesh ou None, ok). process=True + merge_vertices + fix_normals
    transformam a malha gerada (process=False) num volume válido (is_volume).
    """
    try:
        import trimesh  # type: ignore
    except ImportError:
        return None, False
    try:
        m = trimesh.Trimesh(vertices=vertices, faces=faces, process=True)
        m.merge_vertices()
        m.fix_normals()
        if not m.is_volume:
            m.fill_holes()
            m.fix_normals()
        return m, bool(m.is_volume)
    except Exception:
        return None, False


def _trimesh_particle_tool(cx: float, cy: float, cz: float, kind: str, diameter: float):
    """ferramenta booleana (volume estanque) de uma partícula via trimesh.creation."""
    import trimesh  # type: ignore

    pk = (kind or "sphere").strip().lower()
    r = float(diameter) / 2.0
    if pk == "cube":
        tool = trimesh.creation.box(extents=(float(diameter),) * 3)
    elif pk == "cylinder":
        tool = trimesh.creation.cylinder(radius=r, height=float(diameter), sections=16)
    else:
        tool = trimesh.creation.icosphere(radius=r, subdivisions=1)
    tool.apply_translation([float(cx), float(cy), float(cz)])
    return tool


def _pick_boolean_engine() -> Optional[str]:
    """devolve o engine booleano disponível ('manifold' | 'blender') ou None."""
    try:
        import manifold3d  # noqa: F401  # type: ignore
        return "manifold"
    except Exception:
        pass
    try:
        from trimesh.interfaces import blender as _bl  # type: ignore
        if getattr(_bl, "exists", False):
            return "blender"
    except Exception:
        pass
    return None


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
) -> Tuple[List[vec3], List[tuple], str, List[str], int]:
    """boolean difference (queijo) do núcleo com as partículas.

    devolve (vertices, faces, status, warnings, n_furos_aplicados). status:
    'applied' (todos), 'partial' (alguns), 'failed' (nenhum), 'n/a' (sem entrada).
    """
    warnings: List[str] = []
    if not core_v or not core_f or not particle_centers:
        return core_v, core_f, "n/a", warnings, 0

    try:
        import trimesh  # type: ignore  # noqa: F401
    except ImportError:
        warnings.append("trimesh nao instalado: nucleo solido sem furos booleanos")
        return core_v, core_f, "failed", warnings, 0

    core, core_ok = _as_trimesh_volume(core_v, core_f)
    if core is None or not core_ok:
        warnings.append(
            "nucleo nao e volume estanque: furos booleanos nao aplicados (nucleo solido)"
        )
        return core_v, core_f, "failed", warnings, 0

    engine = _pick_boolean_engine()
    if engine is None:
        warnings.append(
            "sem backend booleano (instale manifold3d): nucleo solido sem furos"
        )
        return core_v, core_f, "failed", warnings, 0

    try:
        result = core
        if max_holes is None:
            n = len(particle_centers)
        else:
            n = min(len(particle_centers), max(0, int(max_holes)))
            if len(particle_centers) > n:
                warnings.append(
                    f"furos limitados a {n} de {len(particle_centers)} particulas (desempenho)"
                )
        holes_ok = 0
        for c in particle_centers[:n]:
            cx, cy, cz = c
            tool = _trimesh_particle_tool(cx, cy, cz, particle_kind, particle_diameter)
            try:
                result = result.difference(tool, engine=engine)
                holes_ok += 1
            except Exception as exc:
                warnings.append(
                    f"difference falhou em ({cx:.4f},{cy:.4f},{cz:.4f}): {exc}"
                )
        if holes_ok == 0:
            warnings.append("nenhuma booleana de furo aplicada no nucleo")
            return core_v, core_f, "failed", warnings, 0
        if result is None or len(getattr(result, "vertices", [])) == 0:
            warnings.append("difference resultou malha vazia")
            return core_v, core_f, "failed", warnings, 0
        if holes_ok < n:
            warnings.append(f"apenas {holes_ok}/{n} furos aplicados no nucleo")
        return (
            result.vertices.tolist(),
            result.faces.tolist(),
            "applied" if holes_ok == n else "partial",
            warnings,
            holes_ok,
        )
    except Exception as exc:
        warnings.append(f"trimesh boolean: {exc}")
        return core_v, core_f, "failed", warnings, 0


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

    def _fallback_separate() -> Tuple[List[vec3], List[tuple], str, List[str]]:
        # núcleo + partículas como malhas separadas (visualmente "grudadas")
        v, f = list(core_v), list(core_f)
        for c in particle_centers:
            pv, pf = _particle_tool_mesh(
                c[0], c[1], c[2], particle_kind, particle_diameter
            )
            v, f = merge_mesh(v, f, pv, pf)
        return v, f, "fallback_separate", warnings

    try:
        import trimesh  # type: ignore  # noqa: F401
    except ImportError:
        warnings.append("trimesh nao instalado: exportando nucleo e particulas separados")
        return _fallback_separate()

    core, core_ok = _as_trimesh_volume(core_v, core_f)
    engine = _pick_boolean_engine()
    if core is None or not core_ok or engine is None:
        if engine is None:
            warnings.append(
                "sem backend booleano (instale manifold3d): nucleo e particulas separados"
            )
        else:
            warnings.append("nucleo nao e volume estanque: nucleo e particulas separados")
        return _fallback_separate()

    try:
        result = core
        fused = 0
        for c in particle_centers:
            tool = _trimesh_particle_tool(
                c[0], c[1], c[2], particle_kind, particle_diameter
            )
            try:
                result = result.union(tool, engine=engine)
                fused += 1
            except Exception:
                warnings.append(
                    f"union falhou em ({c[0]:.4f},{c[1]:.4f},{c[2]:.4f})"
                )
        if fused == 0:
            warnings.append("nenhuma union aplicada: nucleo e particulas separados")
            return _fallback_separate()
        return (
            result.vertices.tolist(),
            result.faces.tolist(),
            "applied" if fused == len(particle_centers) else "partial",
            warnings,
        )
    except Exception as exc:
        warnings.append(f"trimesh union: {exc}")
        return _fallback_separate()


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
    # vão interno entre as tampas: o núcleo sólido fica aqui, sem invadir as tampas
    core_z0, core_z1 = _interior_span(height, bottom_cap_thickness, top_cap_thickness)

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
            cv, cf = _solid_cylinder_mesh(
                r_int, height, segmentos, z_bottom=core_z0, z_top=core_z1
            )
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
        cv, cf = _solid_cylinder_mesh(
            r_int, height, segmentos, z_bottom=core_z0, z_top=core_z1
        )
        n_req = len(particle_centers)
        status["inner_core"] = "solid_with_holes"
        if n_req > 0:
            pv, pf, pstat, pw, n_holes = punch_holes_in_solid(
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
            status["n_holes_applied"] = int(n_holes)
            if pstat in ("applied", "partial") and vis.get("show_internal_cylinder", True):
                v, f = merge_mesh(v, f, pv, pf)
                shell_components.append("inner_core_perforated")
            elif vis.get("show_internal_cylinder", True):
                # furos não aplicados: exporta o núcleo sólido (sem buracos) com aviso
                v, f = merge_mesh(v, f, cv, cf)
                shell_components.append("inner_core_solid_no_holes")
            else:
                status["inner_core"] = "solid_with_holes_omitted_from_export"
        else:
            status["particle_tools"] = "n/a"
            if vis.get("show_internal_cylinder", True):
                v, f = merge_mesh(v, f, cv, cf)
                shell_components.append("inner_core_solid")
        status["warnings"] = warnings

    if warnings:
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
