# modos de geometria de saida: full_3d, pseudo_2d_thin_slice, pseudo_2d_statistical
# separado de packing_method e de particles.kind
from __future__ import annotations

import math
from typing import Any, Dict, List, Optional, Sequence, Tuple

GEOMETRY_FULL_3D = "full_3d"
GEOMETRY_THIN_SLICE = "pseudo_2d_thin_slice"
GEOMETRY_STATISTICAL = "pseudo_2d_statistical"

VALID_GEOMETRY_MODES = (
    GEOMETRY_FULL_3D,
    GEOMETRY_THIN_SLICE,
    GEOMETRY_STATISTICAL,
)

vec2 = Tuple[float, float]
vec3 = Tuple[float, float, float]


def _to_float(v: Any, default: float = 0.0) -> float:
    if v is None:
        return float(default)
    if isinstance(v, (int, float)):
        return float(v)
    return float(str(v).replace(",", "."))


def _to_bool(v: Any, default: bool = False) -> bool:
    if isinstance(v, bool):
        return v
    if v is None:
        return default
    s = str(v).strip().lower()
    if s in ("true", "1", "yes", "sim"):
        return True
    if s in ("false", "0", "no", "nao"):
        return False
    return default


def normalize_geometry_mode(raw: Optional[Any], default: str = GEOMETRY_FULL_3D) -> str:
    if raw is None:
        return default
    s = str(raw).strip().strip('"').strip("'").lower()
    if not s:
        return default
    s = s.replace("-", "_").replace(" ", "_")
    while "__" in s:
        s = s.replace("__", "_")
    aliases = {
        "full": GEOMETRY_FULL_3D,
        "3d": GEOMETRY_FULL_3D,
        "full3d": GEOMETRY_FULL_3D,
        "thin_slice": GEOMETRY_THIN_SLICE,
        "thin": GEOMETRY_THIN_SLICE,
        "pseudo_2d": GEOMETRY_THIN_SLICE,
        "pseudo2d": GEOMETRY_THIN_SLICE,
        "slice": GEOMETRY_THIN_SLICE,
        "statistical": GEOMETRY_STATISTICAL,
        "pseudo_2d_stat": GEOMETRY_STATISTICAL,
        "rsa": GEOMETRY_STATISTICAL,
    }
    s = aliases.get(s, s)
    if s in VALID_GEOMETRY_MODES:
        return s
    return default


def normalize_slice_axis(axis: Any, default: str = "y") -> str:
    a = str(axis or default).strip().lower()
    if a in ("x", "y", "z"):
        return a
    return default


def geometry_mode_from_data(data: Dict[str, Any]) -> str:
    if not isinstance(data, dict):
        return GEOMETRY_FULL_3D
    gm = normalize_geometry_mode(data.get("geometry_mode"), GEOMETRY_FULL_3D)
    sl = data.get("slice")
    if gm == GEOMETRY_FULL_3D and isinstance(sl, dict) and _to_bool(sl.get("slice_enabled"), False):
        return GEOMETRY_THIN_SLICE
    if data.get("statistical_2d") and gm == GEOMETRY_FULL_3D:
        return GEOMETRY_STATISTICAL
    return gm


def resolve_slice_config(data: Dict[str, Any]) -> Dict[str, Any]:
    """devolve dict slice normalizado; vazio se modo full_3d."""
    gm = geometry_mode_from_data(data)
    if gm != GEOMETRY_THIN_SLICE:
        return {}

    slice_raw = data.get("slice") if isinstance(data, dict) else None
    cfg: Dict[str, Any] = dict(slice_raw) if isinstance(slice_raw, dict) else {}
    for k in (
        "slice_enabled",
        "slice_thickness",
        "slice_axis",
        "slice_position",
        "keep_only_intersecting_particles",
        "preserve_original_packing",
    ):
        if isinstance(data, dict) and k in data and k not in cfg:
            cfg[k] = data[k]

    axis = normalize_slice_axis(cfg.get("slice_axis"), "y")
    thickness = _to_float(cfg.get("slice_thickness"), 0.002)
    if thickness <= 0:
        thickness = 0.002
    pos = _to_float(cfg.get("slice_position"), 0.0)

    return {
        "slice_enabled": True,
        "slice_axis": axis,
        "slice_thickness": thickness,
        "slice_position": pos,
        "keep_only_intersecting_particles": _to_bool(
            cfg.get("keep_only_intersecting_particles"), True
        ),
        "preserve_original_packing": _to_bool(cfg.get("preserve_original_packing"), True),
    }


def slice_is_active(data: Dict[str, Any]) -> bool:
    return bool(resolve_slice_config(data))


def resolve_statistical_config(data: Dict[str, Any]) -> Dict[str, Any]:
    gm = geometry_mode_from_data(data)
    if gm != GEOMETRY_STATISTICAL:
        return {}

    raw = data.get("statistical_2d")
    cfg: Dict[str, Any] = dict(raw) if isinstance(raw, dict) else {}

    bed = data.get("bed") if isinstance(data.get("bed"), dict) else {}
    particles = data.get("particles") if isinstance(data.get("particles"), dict) else {}

    d_bed = _to_float(bed.get("diameter"), 0.05)
    h_bed = _to_float(bed.get("height"), 0.1)
    d_part = _to_float(particles.get("diameter"), 0.005)
    target_p = cfg.get("target_porosity", particles.get("target_porosity", 0.4))

    return {
        "domain_width": _to_float(cfg.get("domain_width"), d_bed),
        "domain_height": _to_float(cfg.get("domain_height"), h_bed),
        "target_porosity": _to_float(target_p, 0.4),
        "tolerance": _to_float(cfg.get("tolerance"), 0.02),
        "max_attempts": int(_to_float(cfg.get("max_attempts"), 50)),
        "slice_thickness": _to_float(cfg.get("slice_thickness"), 0.002),
        "seed": int(_to_float(cfg.get("seed", particles.get("seed")), 42)),
        "particle_diameter": d_part,
    }


def axis_index(axis: str) -> int:
    a = normalize_slice_axis(axis)
    return 0 if a == "x" else (1 if a == "y" else 2)


def particle_coord_on_axis(center: vec3, axis: str) -> float:
    ai = axis_index(axis)
    return center[ai]


def collision_radius_for_particle_kind(kind: str, characteristic_diameter: float) -> float:
    """alinhado a packed_bed_science.geometry_math (raio de colisao conservador)."""
    k = (kind or "sphere").strip().lower()
    d = float(characteristic_diameter)
    if d <= 0:
        return 1e-9
    if k == "sphere":
        return d * 0.5
    if k == "cube":
        return d * math.sqrt(3.0) * 0.5
    if k == "cylinder":
        return d * 0.5
    return d * 0.5


def particle_intersects_slice(
    center: vec3,
    *,
    particle_kind: str,
    particle_diameter: float,
    axis: str,
    slice_position: float,
    slice_thickness: float,
) -> bool:
    r_eq = collision_radius_for_particle_kind(particle_kind, particle_diameter)
    coord = particle_coord_on_axis(center, axis)
    half = slice_thickness / 2.0
    return abs(coord - slice_position) <= r_eq + half


def sphere_section_radius(sphere_radius: float, distance_to_plane: float) -> float:
    d = abs(distance_to_plane)
    if d >= sphere_radius:
        return 0.0
    return math.sqrt(max(0.0, sphere_radius * sphere_radius - d * d))


def section_radius_for_particle_kind(
    kind: str,
    diameter: float,
    distance_to_plane: float,
    *,
    axis: str = "y",
) -> float:
    """raio efetivo do disco na fatia (esfera/cilindro perp. ao eixo z)."""
    spec = slice_footprint_spec(kind, diameter, distance_to_plane, slice_axis=axis)
    if spec.get("shape") == "disc":
        return float(spec.get("radius") or 0.0)
    return 0.0


def slice_footprint_spec(
    kind: str,
    diameter: float,
    distance_to_plane: float,
    *,
    slice_axis: str = "y",
    slice_thickness: float = 0.002,
) -> Dict[str, Any]:
    """
    especificacao da secao na lamina fina.
    disc: cilindro fino (esfera ou cilindro com corte perp. ao eixo z da particula).
    box: paralelepipedo achatado (cubo ou cilindro com corte // eixo z).
    """
    pk = (kind or "sphere").strip().lower()
    d = float(diameter)
    r = d * 0.5
    d_plane = abs(distance_to_plane)
    ax = normalize_slice_axis(slice_axis)
    t = max(float(slice_thickness), 1e-9)

    if pk == "sphere":
        rs = sphere_section_radius(r, d_plane)
        if rs <= 1e-9:
            return {"shape": "none"}
        return {"shape": "disc", "radius": rs, "thickness": t, "slice_axis": ax}

    if pk == "cube":
        half = d * 0.5
        if d_plane > half + 1e-12:
            return {"shape": "none"}
        sx, sy, sz = d, d, d
        if ax == "x":
            sx = t
        elif ax == "y":
            sy = t
        else:
            sz = t
        return {
            "shape": "box",
            "size_x": sx,
            "size_y": sy,
            "size_z": sz,
            "slice_axis": ax,
        }

    if pk == "cylinder":
        # particula com eixo z (legacy): corte perp. a z -> disco; corte perp. a x/y -> retangulo d x d
        if ax == "z":
            rs = sphere_section_radius(r, d_plane)
            if rs <= 1e-9:
                return {"shape": "none"}
            return {"shape": "disc", "radius": rs, "thickness": t, "slice_axis": ax}
        if d_plane > r + 1e-12:
            return {"shape": "none"}
        if ax == "x":
            return {
                "shape": "box",
                "size_x": t,
                "size_y": d,
                "size_z": d,
                "slice_axis": ax,
            }
        return {
            "shape": "box",
            "size_x": d,
            "size_y": t,
            "size_z": d,
            "slice_axis": ax,
        }

    rs = sphere_section_radius(r, d_plane)
    if rs <= 1e-9:
        return {"shape": "none"}
    return {"shape": "disc", "radius": rs, "thickness": t, "slice_axis": ax}


def slice_footprint_center(
    center: vec3,
    *,
    slice_axis: str,
    slice_position: float,
    preserve_original_packing: bool,
) -> vec3:
    x, y, z = center
    if preserve_original_packing:
        return (float(x), float(y), float(z))
    ax = normalize_slice_axis(slice_axis)
    if ax == "x":
        return (float(slice_position), float(y), float(z))
    if ax == "y":
        return (float(x), float(slice_position), float(z))
    return (float(x), float(y), float(slice_position))


def compute_global_porosity_2d_formula(
    disc_centers: Sequence[vec2],
    disc_radius: float,
    domain_width: float,
    domain_height: float,
) -> float:
    """formula analitica sem sobreposicao: solido = N * pi * r^2 (superestima se discos se tocam)."""
    area_total = max(domain_width * domain_height, 1e-12)
    area_solid = len(disc_centers) * math.pi * disc_radius * disc_radius
    return max(0.0, min(1.0, 1.0 - area_solid / area_total))


def compute_global_porosity_2d_raster(
    disc_centers: Sequence[vec2],
    disc_radius: float,
    domain_width: float,
    domain_height: float,
    *,
    cells_per_radius: int = 10,
    max_cells_per_axis: int = 512,
) -> Tuple[float, Dict[str, Any]]:
    """
    porosidade 2d por raster: grelha no dominio; celula solida se o centro cai dentro de algum disco.
    desconta sobreposicao (uniao das areas), ao contrario da formula analitica.
    """
    w = max(float(domain_width), 1e-12)
    h = max(float(domain_height), 1e-12)
    r = max(float(disc_radius), 0.0)
    if r <= 0 or not disc_centers:
        return 1.0, {
            "porosity_method": "raster",
            "raster_nx": 0,
            "raster_ny": 0,
            "solid_fraction": 0.0,
        }
    cpr = max(4, int(cells_per_radius))
    cell = r / float(cpr)
    nx = max(8, min(max_cells_per_axis, int(math.ceil(w / cell))))
    ny = max(8, min(max_cells_per_axis, int(math.ceil(h / cell))))
    r2 = r * r
    solid_cells = 0
    for j in range(ny):
        cy = (j + 0.5) * h / ny
        for i in range(nx):
            cx = (i + 0.5) * w / nx
            for (dx, dy) in disc_centers:
                ddx = cx - dx
                ddy = cy - dy
                if ddx * ddx + ddy * ddy <= r2:
                    solid_cells += 1
                    break
    total = nx * ny
    solid_frac = solid_cells / max(total, 1)
    porosity = max(0.0, min(1.0, 1.0 - solid_frac))
    return porosity, {
        "porosity_method": "raster",
        "raster_nx": nx,
        "raster_ny": ny,
        "raster_cell_m": cell,
        "solid_fraction": solid_frac,
        "n_discs": len(disc_centers),
    }


def compute_global_porosity_2d(
    disc_centers: Sequence[vec2],
    disc_radius: float,
    domain_width: float,
    domain_height: float,
    *,
    use_raster: bool = True,
    cells_per_radius: int = 10,
) -> float:
    if use_raster:
        p, _meta = compute_global_porosity_2d_raster(
            disc_centers,
            disc_radius,
            domain_width,
            domain_height,
            cells_per_radius=cells_per_radius,
        )
        return p
    return compute_global_porosity_2d_formula(
        disc_centers, disc_radius, domain_width, domain_height
    )


def compute_axial_porosity_profile_2d(
    disc_centers: Sequence[vec2],
    disc_radius: float,
    domain_width: float,
    domain_height: float,
    *,
    n_bins: int = 10,
) -> List[Dict[str, float]]:
    """porosidade por faixas ao longo de y (altura do dominio 2d)."""
    n_bins = max(1, n_bins)
    bin_h = domain_height / n_bins
    profile: List[Dict[str, float]] = []
    r2 = disc_radius * disc_radius
    for i in range(n_bins):
        y0 = i * bin_h
        y1 = (i + 1) * bin_h
        y_mid = (y0 + y1) / 2.0
        area_bin = domain_width * bin_h
        solid = 0.0
        for (cx, cy) in disc_centers:
            if y0 <= cy < y1 or (i == n_bins - 1 and cy == y1):
                solid += math.pi * r2
        porosity = 1.0 - min(1.0, solid / max(area_bin, 1e-12))
        profile.append({"y_min": y0, "y_max": y1, "y_mid": y_mid, "porosity": porosity})
    return profile


def compute_radial_porosity_profile_2d(
    disc_centers: Sequence[vec2],
    disc_radius: float,
    domain_width: float,
    domain_height: float,
    *,
    n_bins: int = 10,
) -> List[Dict[str, float]]:
    """implementacao inicial: faixas radiais desde o centro do dominio."""
    cx0 = domain_width / 2.0
    cy0 = domain_height / 2.0
    r_max = math.hypot(domain_width, domain_height) / 2.0
    n_bins = max(1, n_bins)
    dr = r_max / n_bins
    r2 = disc_radius * disc_radius
    profile: List[Dict[str, float]] = []
    for i in range(n_bins):
        r0 = i * dr
        r1 = (i + 1) * dr
        area_shell = math.pi * (r1 * r1 - r0 * r0)
        solid = 0.0
        for (cx, cy) in disc_centers:
            cr = math.hypot(cx - cx0, cy - cy0)
            if r0 <= cr < r1:
                solid += math.pi * r2
        porosity = 1.0 - min(1.0, solid / max(area_shell, 1e-12))
        profile.append({"r_min": r0, "r_max": r1, "porosity": porosity})
    return profile


def compute_two_point_correlation_2d(
    disc_centers: Sequence[vec2],
    domain_width: float,
    domain_height: float,
    *,
    n_r_bins: int = 20,
) -> List[Dict[str, float]]:
    """correlacao radial g(r) simplificada (par de centros por distancia)."""
    if len(disc_centers) < 2:
        return []
    r_max = min(domain_width, domain_height) / 2.0
    n_r_bins = max(2, n_r_bins)
    dr = r_max / n_r_bins
    counts = [0] * n_r_bins
    pairs = 0
    n = len(disc_centers)
    for i in range(n):
        for j in range(i + 1, n):
            d = math.hypot(
                disc_centers[i][0] - disc_centers[j][0],
                disc_centers[i][1] - disc_centers[j][1],
            )
            pairs += 1
            bi = min(n_r_bins - 1, int(d / dr) if dr > 0 else 0)
            counts[bi] += 1
    out: List[Dict[str, float]] = []
    for i, c in enumerate(counts):
        out.append(
            {
                "r_min": i * dr,
                "r_max": (i + 1) * dr,
                "count": float(c),
                "normalized": float(c) / max(pairs, 1),
            }
        )
    return out
