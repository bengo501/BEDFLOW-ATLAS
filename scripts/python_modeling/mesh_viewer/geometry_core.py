"""operacoes puras sobre malhas open3d (sem ui)."""
from __future__ import annotations

import copy
from typing import Any, Tuple

import numpy as np


def cluster_count(mesh: Any) -> int:
    try:
        _labels, n_tri, _area = mesh.cluster_connected_triangles()
        return int(len(n_tri))
    except Exception:
        return 1


def bbox_lineset(mesh: Any) -> Any:
    import open3d as o3d

    bb = mesh.get_axis_aligned_bounding_box()
    ls = o3d.geometry.LineSet.create_from_axis_aligned_bounding_box(bb)
    ls.paint_uniform_color([0.95, 0.45, 0.12])
    return ls


def wire_lineset_from_mesh(
    mesh: Any,
    max_triangles: int = 120_000,
    simplify_target: int = 72_000,
) -> Any | None:
    """arestas da malha; se for enorme, decima antes (só visualizacao)."""
    import copy as copy_mod

    import open3d as o3d

    try:
        n = len(mesh.triangles)
        m = mesh
        if n > max_triangles:
            m = copy_mod.deepcopy(mesh)
            tgt = int(min(simplify_target, max(8000, n // 4)))
            try:
                m = m.simplify_quadric_decimation(target_number_of_triangles=tgt)
            except Exception:
                return None
        if len(m.triangles) == 0:
            return None
        ls = o3d.geometry.LineSet.create_from_triangle_mesh(m)
        # contraste sobre fundo claro
        ls.paint_uniform_color([0.98, 0.98, 1.0])
        return ls
    except Exception:
        return None


def crop_mesh_slab(
    mesh_src: Any,
    clip_frac: float,
    axis: int,
    from_max: bool,
) -> Any:
    import open3d as o3d

    if clip_frac <= 1e-9:
        return copy.deepcopy(mesh_src)
    axis = int(axis) % 3
    bbox = mesh_src.get_axis_aligned_bounding_box()
    mn = np.asarray(bbox.get_min_bound(), dtype=np.float64)
    mx = np.asarray(bbox.get_max_bound(), dtype=np.float64)
    h = float(mx[axis] - mn[axis])
    if h < 1e-12:
        return copy.deepcopy(mesh_src)
    delta = float(clip_frac) * h
    mn2 = mn.copy()
    mx2 = mx.copy()
    if from_max:
        mx2[axis] = mx[axis] - delta
    else:
        mn2[axis] = mn[axis] + delta
    if mx2[axis] <= mn2[axis] + 1e-9:
        return copy.deepcopy(mesh_src)
    aabb = o3d.geometry.AxisAlignedBoundingBox(
        min_bound=mn2.astype(np.float64), max_bound=mx2.astype(np.float64)
    )
    try:
        cropped = mesh_src.crop(aabb)
    except Exception:
        return copy.deepcopy(mesh_src)
    if cropped.is_empty() or len(cropped.triangles) == 0:
        return copy.deepcopy(mesh_src)
    return cropped


def style_mesh_rgb(m: Any, rgb: Tuple[float, float, float]) -> None:
    import open3d as o3d

    m.vertex_colors = o3d.utility.Vector3dVector()
    m.compute_vertex_normals()
    m.paint_uniform_color(list(rgb))
