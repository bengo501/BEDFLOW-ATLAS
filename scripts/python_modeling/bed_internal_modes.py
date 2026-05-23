# modos de cilindro interno e flags de visibilidade (contrato bed.internal_cylinder_mode)
from __future__ import annotations

from typing import Any, Dict, List, Optional, Tuple

MODE_HOLLOW_BOOLEAN = "hollow_boolean_applied"
MODE_VISIBLE_INNER = "internal_cylinder_visible_no_boolean"
MODE_SOLID_HOLES = "solid_internal_cylinder_with_particle_holes"

INTERNAL_CYLINDER_MODES = (
    MODE_HOLLOW_BOOLEAN,
    MODE_VISIBLE_INNER,
    MODE_SOLID_HOLES,
)

_ALIASES = {
    "m1": MODE_HOLLOW_BOOLEAN,
    "hollow": MODE_HOLLOW_BOOLEAN,
    "hollow_boolean": MODE_HOLLOW_BOOLEAN,
    "default": MODE_HOLLOW_BOOLEAN,
    "m2": MODE_VISIBLE_INNER,
    "visible_inner": MODE_VISIBLE_INNER,
    "no_boolean": MODE_VISIBLE_INNER,
    "m3": MODE_SOLID_HOLES,
    "solid_holes": MODE_SOLID_HOLES,
    "particle_holes": MODE_SOLID_HOLES,
}


def _to_bool(v: Any, default: bool = False) -> bool:
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


def normalize_internal_cylinder_mode(raw: Any, default: str = MODE_HOLLOW_BOOLEAN) -> str:
    if raw is None or raw == "":
        return default
    s = str(raw).strip().strip('"').strip("'").lower()
    s = s.replace("-", "_").replace(" ", "_")
    while "__" in s:
        s = s.replace("__", "_")
    s = _ALIASES.get(s, s)
    if s in INTERNAL_CYLINDER_MODES:
        return s
    return default


def default_visibility_for_mode(mode: str) -> Dict[str, bool]:
    m = normalize_internal_cylinder_mode(mode)
    if m == MODE_VISIBLE_INNER:
        return {
            "show_outer_cylinder": True,
            "show_internal_cylinder": True,
            "show_particles": True,
            "show_boolean_tools": False,
            "export_boolean_tools": False,
        }
    if m == MODE_SOLID_HOLES:
        return {
            "show_outer_cylinder": True,
            "show_internal_cylinder": True,
            "show_particles": False,
            "show_boolean_tools": False,
            "export_boolean_tools": False,
        }
    return {
        "show_outer_cylinder": True,
        "show_internal_cylinder": False,
        "show_particles": True,
        "show_boolean_tools": False,
        "export_boolean_tools": False,
    }


def enforce_visibility_for_mode(mode: str, vis: Dict[str, bool]) -> Dict[str, bool]:
    """impede combinações incoerentes (ex.: m1 com núcleo sólido ou m3 com partículas soltas)."""
    m = normalize_internal_cylinder_mode(mode)
    out = dict(vis)
    if m == MODE_HOLLOW_BOOLEAN:
        out["show_internal_cylinder"] = False
        out["show_boolean_tools"] = False
        out["export_boolean_tools"] = False
    elif m == MODE_SOLID_HOLES:
        out["show_particles"] = False
        out["show_boolean_tools"] = False
        out["export_boolean_tools"] = False
    elif m == MODE_VISIBLE_INNER:
        if not out.get("show_internal_cylinder", True):
            pass
        else:
            out["show_internal_cylinder"] = True
    return out


def resolve_bed_internal_config(data: Dict[str, Any]) -> Tuple[str, Dict[str, bool], List[str]]:
    """extrai modo e visibility a partir de data ou data['bed']; devolve avisos."""
    notes: List[str] = []
    bed = data.get("bed") if isinstance(data.get("bed"), dict) else {}
    if not isinstance(bed, dict):
        bed = {}
    raw_mode = bed.get("internal_cylinder_mode")
    if raw_mode is None and data.get("internal_cylinder_mode") is not None:
        raw_mode = data.get("internal_cylinder_mode")
    mode = normalize_internal_cylinder_mode(raw_mode)
    vis_raw = bed.get("visibility")
    if vis_raw is None and isinstance(data.get("visibility"), dict):
        vis_raw = data.get("visibility")
    vis = default_visibility_for_mode(mode)
    if isinstance(vis_raw, dict):
        for k in vis:
            if k in vis_raw:
                vis[k] = _to_bool(vis_raw[k], vis[k])
    vis = enforce_visibility_for_mode(mode, vis)
    return mode, vis, notes


def build_boolean_operation_status(
    mode: str,
    *,
    backend: str = "python_engine",
    outer_shell: Optional[str] = None,
    inner_core: Optional[str] = None,
    particle_tools: Optional[str] = None,
    warnings: Optional[List[str]] = None,
    r_int: Optional[float] = None,
    r_ext: Optional[float] = None,
) -> Dict[str, Any]:
    m = normalize_internal_cylinder_mode(mode)
    if outer_shell is None:
        if m == MODE_HOLLOW_BOOLEAN:
            outer_shell = "applied" if backend == "blender" else "explicit_annulus"
        elif m == MODE_VISIBLE_INNER:
            outer_shell = "fallback_separate_meshes"
        else:
            outer_shell = "explicit_annulus"
    if inner_core is None:
        if m == MODE_HOLLOW_BOOLEAN:
            inner_core = "n/a"
        elif m == MODE_VISIBLE_INNER:
            inner_core = "visible_separate"
        else:
            inner_core = "solid_with_holes"
    if particle_tools is None:
        particle_tools = "applied" if m == MODE_SOLID_HOLES else "n/a"
    out: Dict[str, Any] = {
        "outer_shell": outer_shell,
        "inner_core": inner_core,
        "particle_tools": particle_tools,
        "backend": backend,
        "warnings": list(warnings or []),
    }
    if r_int is not None:
        out["r_int"] = float(r_int)
    if r_ext is not None:
        out["r_ext"] = float(r_ext)
    return out


def validate_bed_geometry_mode(
    data: Dict[str, Any],
    geometry_mode: str,
) -> List[str]:
    """avisos quando statistical ignora modos de cilindro interno."""
    from geometry_modes import GEOMETRY_STATISTICAL, normalize_geometry_mode

    notes: List[str] = []
    gm = normalize_geometry_mode(geometry_mode, geometry_mode)
    mode, _, _ = resolve_bed_internal_config(data)
    if gm == GEOMETRY_STATISTICAL and mode != MODE_HOLLOW_BOOLEAN:
        notes.append(
            "pseudo_2d_statistical: internal_cylinder_mode ignorado; "
            "domínio 2d independente do cilindro interno 3d"
        )
    return notes


def bed_internal_sidecar(
    data: Dict[str, Any],
    *,
    backend: str = "python_engine",
    status: Optional[Dict[str, Any]] = None,
    r_int: Optional[float] = None,
    r_ext: Optional[float] = None,
) -> Dict[str, Any]:
    mode, vis, _ = resolve_bed_internal_config(data)
    st = status or build_boolean_operation_status(
        mode, backend=backend, r_int=r_int, r_ext=r_ext
    )
    return {
        "internal_cylinder_mode": mode,
        "visibility": vis,
        "boolean_operation_status": st,
    }
