# forcas de contacto mola-amortecedor para dem
from __future__ import annotations

import numpy as np

from .particles import Particle


def normal_contact_force(
    overlap: float,
    normal_velocity: float,
    *,
    stiffness: float,
    damping: float,
) -> float:
    if overlap <= 0.0:
        return 0.0
    return stiffness * overlap - damping * normal_velocity


def apply_pair_contact(
    p1: Particle,
    p2: Particle,
    *,
    stiffness: float,
    damping: float,
    friction: float = 0.0,
) -> None:
    delta = p2.position - p1.position
    dist = float(np.linalg.norm(delta))
    min_dist = p1.radius + p2.radius
    if dist < min_dist and dist > 1e-14:
        normal = delta / dist
        overlap = min_dist - dist
        rel_v = p2.velocity - p1.velocity
        vn = float(np.dot(rel_v, normal))
        fn = normal_contact_force(overlap, vn, stiffness=stiffness, damping=damping)
        force = fn * normal
        p1.force -= force
        p2.force += force
        if friction > 0.0:
            vt = rel_v - vn * normal
            vt_norm = float(np.linalg.norm(vt))
            if vt_norm > 1e-14:
                ft = min(friction * abs(fn), friction * vt_norm)
                tangent = vt / vt_norm
                p1.force += ft * tangent
                p2.force -= ft * tangent


def apply_cylinder_wall(
    p: Particle,
    r_wall: float,
    z_bottom: float,
    z_top: float,
    *,
    stiffness: float,
    damping: float,
) -> None:
    x, y, z = p.position
    radial = float(np.sqrt(x * x + y * y))
    max_radial = r_wall - p.radius
    if radial > max_radial and radial > 1e-14:
        normal_xy = np.array([x / radial, y / radial, 0.0])
        overlap = radial - max_radial
        vn = float(np.dot(p.velocity, normal_xy))
        fn = normal_contact_force(overlap, vn, stiffness=stiffness, damping=damping)
        p.force -= fn * normal_xy

    if z - p.radius < z_bottom:
        overlap = z_bottom - (z - p.radius)
        normal = np.array([0.0, 0.0, 1.0])
        vn = float(np.dot(p.velocity, normal))
        fn = normal_contact_force(overlap, vn, stiffness=stiffness, damping=damping)
        p.force += fn * normal

    if z + p.radius > z_top:
        overlap = (z + p.radius) - z_top
        normal = np.array([0.0, 0.0, -1.0])
        vn = float(np.dot(p.velocity, normal))
        fn = normal_contact_force(overlap, vn, stiffness=stiffness, damping=damping)
        p.force += fn * normal
