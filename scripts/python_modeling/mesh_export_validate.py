# validação pós-export de malhas pseudo-2d thin slice e full 3d
from __future__ import annotations

import struct
from pathlib import Path
from typing import Any, Dict, List, Optional, Tuple

from geometry_modes import axis_index, geometry_mode_from_data, normalize_slice_axis
from stl_mesh_utils import tri, vec3

__all__ = [
    "validate_thin_slice_mesh",
    "validate_stl_file",
    "check_geometry_mode_slice_consistency",
]


def _read_stl_vertices(path: Path) -> List[vec3]:
    data = path.read_bytes()
    if len(data) < 84:
        return []
    if data[:5].lower() == b"solid":
        return _read_ascii_stl_vertices(data.decode("utf-8", errors="ignore"))
    n_tri = int.from_bytes(data[80:84], "little")
    verts: List[vec3] = []
    off = 84
    tri_record = 52  # 12 floats + uint16 + 2 bytes pad (formato write_stl_binary)
    for _ in range(n_tri):
        if off + tri_record > len(data):
            break
        off += 12  # normal (3 floats)
        for _ in range(3):
            x = _unpack_f(data, off)
            y = _unpack_f(data, off + 4)
            z = _unpack_f(data, off + 8)
            off += 12
            if abs(x) < 1e6 and abs(y) < 1e6 and abs(z) < 1e6:
                verts.append((x, y, z))
        off += 4  # atributo uint16 + padding
    return verts


def _unpack_f(data: bytes, off: int) -> float:
    return struct.unpack("<f", data[off : off + 4])[0]


def _read_ascii_stl_vertices(text: str) -> List[vec3]:
    verts: List[vec3] = []
    for line in text.splitlines():
        line = line.strip()
        if line.lower().startswith("vertex"):
            parts = line.split()
            if len(parts) >= 4:
                try:
                    verts.append(
                        (float(parts[1]), float(parts[2]), float(parts[3]))
                    )
                except ValueError:
                    pass
    return verts


def _bbox(vertices: List[vec3]) -> Tuple[vec3, vec3]:
    if not vertices:
        return (0.0, 0.0, 0.0), (0.0, 0.0, 0.0)
    xs = [p[0] for p in vertices]
    ys = [p[1] for p in vertices]
    zs = [p[2] for p in vertices]
    return (min(xs), min(ys), min(zs)), (max(xs), max(ys), max(zs))


def _extent_on_axis(vertices: List[vec3], axis: str) -> float:
    ai = axis_index(axis)
    vals = [p[ai] for p in vertices]
    return max(vals) - min(vals) if vals else 0.0


def validate_thin_slice_mesh(
    vertices: List[vec3],
    *,
    slice_axis: str = "y",
    slice_thickness: float = 0.002,
    bed_height: Optional[float] = None,
    particle_region_only: bool = False,
) -> Dict[str, Any]:
    """
    detecta regressão «colunas z».
    com particle_region_only=True exige extensão no eixo da fatia ~ slice_thickness.
    com casco incluído (False) só detecta colunas altas em z com lâmina fina no eixo da fatia.
    """
    axis = normalize_slice_axis(slice_axis)
    thick = max(float(slice_thickness), 1e-9)
    bed_h = float(bed_height) if bed_height is not None and float(bed_height) > 0 else None

    if not vertices:
        return {"ok": False, "errors": ["malha sem vértices"]}

    ext_slice = _extent_on_axis(vertices, axis)
    ext_z = _extent_on_axis(vertices, "z")
    errors: List[str] = []
    warnings: List[str] = []

    if ext_slice > 1.0:
        errors.append(f"extensão no eixo {axis} inválida ({ext_slice}) — stl corrupto?")
    elif particle_region_only and ext_slice > thick * 2.5:
        errors.append(
            f"extensão no eixo {axis} ({ext_slice:.6f} m) > espessura da fatia "
            f"({thick:.6f} m) — discos mal orientados"
        )

    if not particle_region_only and bed_h and ext_z > bed_h * 0.85 and ext_slice <= thick * 2.5:
        errors.append(
            f"extensão em z ({ext_z:.6f} m) ~ altura do leito ({bed_h:.6f} m) com fatia fina "
            "no eixo da fatia — possíveis colunas verticais (regressão)"
        )

    lo, hi = _bbox(vertices)
    return {
        "ok": len(errors) == 0,
        "errors": errors,
        "warnings": warnings,
        "extent_slice_axis": ext_slice,
        "extent_z": ext_z,
        "bbox_min": lo,
        "bbox_max": hi,
        "slice_axis": axis,
        "slice_thickness": thick,
        "particle_region_only": particle_region_only,
    }


def validate_stl_file(
    stl_path: Path,
    *,
    geometry_mode: str = "pseudo_2d_thin_slice",
    slice_axis: str = "y",
    slice_thickness: float = 0.002,
    bed_height: Optional[float] = None,
) -> Dict[str, Any]:
    verts = _read_stl_vertices(stl_path)
    if geometry_mode == "pseudo_2d_thin_slice":
        return validate_thin_slice_mesh(
            verts,
            slice_axis=slice_axis,
            slice_thickness=slice_thickness,
            bed_height=bed_height,
        )
    if not verts:
        return {"ok": False, "errors": ["stl sem vértices ou ilegível"]}
    lo, hi = _bbox(verts)
    return {
        "ok": True,
        "errors": [],
        "warnings": [],
        "vertex_count": len(verts),
        "bbox_min": lo,
        "bbox_max": hi,
        "geometry_mode": geometry_mode,
    }


def check_geometry_mode_slice_consistency(
    bed_data: Dict[str, Any],
    slice_cfg: Dict[str, Any],
) -> List[str]:
    """avisos quando geometry_mode pede thin slice mas slice_cfg está vazio."""
    warnings: List[str] = []
    gm = geometry_mode_from_data(bed_data)
    if gm == "pseudo_2d_thin_slice" and not slice_cfg.get("slice_enabled"):
        warnings.append(
            "geometry_mode=pseudo_2d_thin_slice mas slice não activo — export pode ser full_3d"
        )
    return warnings
