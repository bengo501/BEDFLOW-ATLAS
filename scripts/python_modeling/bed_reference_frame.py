# referencial unico do leito (eixo z) e da fatia pseudo-2d
from __future__ import annotations

import math
from dataclasses import dataclass
from typing import Any, Dict, List, Tuple

from geometry_modes import (
    _to_float,
    axis_index,
    normalize_slice_axis,
    normalize_slice_particle_policy,
    resolve_slice_config,
)
from stl_mesh_utils import (
    annulus_cap_pair,
    cylinder_axis,
    filter_faces_by_slab,
    merge_mesh,
    tri,
    vec3,
)

BED_AXIS = "z"


@dataclass
class BedReferenceFrame:
    bed_axis: str = BED_AXIS
    origin: vec3 = (0.0, 0.0, 0.0)
    r_util: float = 0.02
    r_ext: float = 0.025
    height: float = 0.1
    slice_axis: str = "y"
    slice_center: float = 0.0
    slice_thickness: float = 0.002
    slice_particle_policy: str = "contained"

    def rho_from_center(self, center: vec3) -> float:
        x, y, _z = center
        return math.hypot(float(x), float(y))

    def slice_coord(self, center: vec3) -> float:
        ai = axis_index(self.slice_axis)
        return float(center[ai])

    def slab_bounds(self) -> Tuple[float, float]:
        half = self.slice_thickness / 2.0
        return self.slice_center - half, self.slice_center + half

    def point_in_util_volume(self, p: vec3) -> bool:
        rho = math.hypot(p[0], p[2])
        if rho > self.r_util + 1e-12:
            return False
        s = self.slice_coord(p)
        lo, hi = self.slab_bounds()
        return lo - 1e-12 <= s <= hi + 1e-12


def get_reference_frame(
    data: Dict[str, Any],
    *,
    r_int: float,
    r_ext: float,
    height: float,
) -> BedReferenceFrame:
    slice_cfg = resolve_slice_config(data) if isinstance(data, dict) else {}
    bed = data.get("bed") if isinstance(data, dict) and isinstance(data.get("bed"), dict) else {}
    return BedReferenceFrame(
        bed_axis=BED_AXIS,
        origin=(0.0, 0.0, 0.0),
        r_util=float(r_int),
        r_ext=float(r_ext),
        height=float(height),
        slice_axis=normalize_slice_axis(slice_cfg.get("slice_axis"), "y"),
        slice_center=_to_float(slice_cfg.get("slice_position"), 0.0),
        slice_thickness=max(_to_float(slice_cfg.get("slice_thickness"), 0.002), 1e-9),
        slice_particle_policy=normalize_slice_particle_policy(
            slice_cfg.get("slice_particle_policy"), "contained"
        ),
    )


def frame_from_slice_cfg(
    slice_cfg: Dict[str, Any],
    *,
    r_int: float,
    r_ext: float,
    height: float,
) -> BedReferenceFrame:
    return BedReferenceFrame(
        bed_axis=BED_AXIS,
        r_util=float(r_int),
        r_ext=float(r_ext),
        height=float(height),
        slice_axis=normalize_slice_axis(slice_cfg.get("slice_axis"), "y"),
        slice_center=_to_float(slice_cfg.get("slice_position"), 0.0),
        slice_thickness=max(_to_float(slice_cfg.get("slice_thickness"), 0.002), 1e-9),
        slice_particle_policy=normalize_slice_particle_policy(
            slice_cfg.get("slice_particle_policy"), "contained"
        ),
    )


def blender_cutter_spec(frame: BedReferenceFrame) -> Tuple[List[float], List[float]]:
    """localizacao e escala (metade das dimensoes) do cubo cortador no blender."""
    big = max(frame.height * 2.0, frame.r_ext * 4.0, 1.0)
    ai = axis_index(frame.slice_axis)
    dims = [big, big, big]
    dims[ai] = frame.slice_thickness
    loc = [0.0, 0.0, frame.height / 2.0]
    loc[ai] = frame.slice_center
    scale = [dims[0] / 2.0, dims[1] / 2.0, dims[2] / 2.0]
    return loc, scale


def build_slice_volume_mesh(
    frame: BedReferenceFrame,
    *,
    segments: int = 32,
) -> Tuple[List[vec3], List[tri]]:
    """
    aproximacao do volume util: cilindro r_util ao longo de z,
    depois faces dentro da faixa do slice (conservador para clip).
    """
    cx, cy, cz = 0.0, 0.0, frame.height / 2.0
    v_cyl, f_cyl = cylinder_axis(
        cx, cy, cz, frame.r_util, frame.height, axis=frame.bed_axis, segments=segments
    )
    lo, hi = frame.slab_bounds()
    v_out, f_out = filter_faces_by_slab(
        v_cyl, f_cyl, axis=frame.slice_axis, min_v=lo, max_v=hi
    )
    cap_v, cap_f = annulus_cap_pair(
        r_ext=frame.r_util,
        r_int=0.0,
        axis=frame.slice_axis,
        position=frame.slice_center,
        thickness=frame.slice_thickness,
        segments=max(12, segments),
    )
    if cap_v:
        v_out, f_out = merge_mesh(v_out, f_out, cap_v, cap_f)
    return v_out, f_out


__all__ = [
    "BED_AXIS",
    "BedReferenceFrame",
    "blender_cutter_spec",
    "build_slice_volume_mesh",
    "frame_from_slice_cfg",
    "get_reference_frame",
]
