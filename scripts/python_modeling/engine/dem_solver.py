# solver dem simples para esferas (contacto mola-amortecedor)
from __future__ import annotations

import math
import random
import time
from typing import Any, Dict, List, Optional, Tuple

import numpy as np

from .collision import apply_cylinder_wall, apply_pair_contact
from .domain import PackedBedDomain
from .particles import Particle
from .spatial_hash import build_spatial_grid, find_candidate_pairs

vec3 = Tuple[float, float, float]


def default_dem_params() -> Dict[str, Any]:
    return {
        "time_step": 1e-4,
        "steps": 30_000,
        "gravity": 9.81,
        "stiffness": 5000.0,
        "damping": 0.2,
        "friction": 0.2,
        "restitution": 0.3,
        "settle_threshold": 1e-3,
        "max_velocity_threshold": 0.01,
        "settle_steps_required": 50,
        "seed": 42,
        "density": 2500.0,
    }


def merge_dem_params(packing: Dict[str, Any]) -> Dict[str, Any]:
    out = default_dem_params()
    raw = packing.get("dem") if isinstance(packing.get("dem"), dict) else {}
    for k, v in raw.items():
        if v is not None:
            out[k] = v
    for k in ("time_step", "steps", "gravity", "stiffness", "damping", "friction"):
        if packing.get(k) is not None and k not in raw:
            out[k] = packing[k]
    return out


def _spawn_particles(
    domain: PackedBedDomain,
    n: int,
    *,
    seed: int,
    density: float,
) -> List[Particle]:
    rng = random.Random(seed)
    ann = domain.annulus
    rho_min, rho_max = ann.radial_bounds()
    zmin, zmax = ann.z_bounds()
    if rho_max <= rho_min or zmax <= zmin:
        return []

    r_sphere = ann.r_sphere
    particles: List[Particle] = []
    z_spawn_base = zmax + r_sphere * 2.0
    for i in range(n):
        for _ in range(200):
            ang = rng.uniform(0.0, 2.0 * math.pi)
            rho = rng.uniform(0.0, max(0.0, rho_max * 0.85))
            x = rho * math.cos(ang)
            y = rho * math.sin(ang)
            z = z_spawn_base + i * r_sphere * 2.5 + rng.uniform(0.0, r_sphere)
            pos = (x, y, z)
            ok = True
            for p in particles:
                d = math.dist(pos, tuple(p.position))
                if d < 2.0 * r_sphere * 0.95:
                    ok = False
                    break
            if ok:
                particles.append(
                    Particle.create(
                        i,
                        domain.particle_kind,
                        pos,
                        r_sphere,
                        density=density,
                    )
                )
                break
        else:
            ang = rng.uniform(0.0, 2.0 * math.pi)
            rho = rng.uniform(0.0, max(0.0, rho_max * 0.5))
            particles.append(
                Particle.create(
                    i,
                    domain.particle_kind,
                    (
                        rho * math.cos(ang),
                        rho * math.sin(ang),
                        z_spawn_base + i * r_sphere * 2.5,
                    ),
                    r_sphere,
                    density=density,
                )
            )
    return particles


class SimpleDEMSolver:
    def __init__(
        self,
        particles: List[Particle],
        domain: PackedBedDomain,
        params: Dict[str, Any],
    ):
        self.particles = particles
        self.domain = domain
        self.params = params
        self.dt = float(params["time_step"])
        self.gravity = float(params["gravity"])
        self.stiffness = float(params["stiffness"])
        self.damping = float(params["damping"])
        self.friction = float(params.get("friction", 0.0))
        self.settle_threshold = float(params["settle_threshold"])
        self.max_velocity_threshold = float(params.get("max_velocity_threshold", 0.01))
        self.settle_steps_required = int(params.get("settle_steps_required", 50))
        ann = domain.annulus
        self._r_wall = ann.r_int - ann.gap
        zmin, zmax = ann.z_bounds()
        self._z_bottom = zmin
        self._z_top = zmax
        max_r = max((p.radius for p in particles), default=0.005)
        self._cell_size = max(2.0 * max_r, 1e-6)

    def reset_forces(self) -> None:
        g = self.gravity
        for p in self.particles:
            p.force[:] = 0.0
            p.force[2] -= p.mass * g

    def solve_particle_collisions(self) -> int:
        positions = [p.position for p in self.particles]
        grid = build_spatial_grid(positions, self._cell_size)
        pairs = find_candidate_pairs(grid)
        for i, j in pairs:
            apply_pair_contact(
                self.particles[i],
                self.particles[j],
                stiffness=self.stiffness,
                damping=self.damping,
                friction=self.friction,
            )
        return len(pairs)

    def solve_wall_collisions(self) -> None:
        for p in self.particles:
            apply_cylinder_wall(
                p,
                self._r_wall,
                self._z_bottom,
                self._z_top,
                stiffness=self.stiffness,
                damping=self.damping,
            )

    def _clamp_particle(self, p: Particle) -> None:
        x, y, z = p.position
        r = p.radius
        radial = float(np.sqrt(x * x + y * y))
        max_rad = self._r_wall - r
        if radial > max_rad and radial > 1e-14:
            scale = max_rad / radial
            x *= scale
            y *= scale
            vx, vy, vz = p.velocity
            vr = (vx * x + vy * y) / (radial * radial + 1e-14)
            p.velocity[0] = vx - vr * x
            p.velocity[1] = vy - vr * y
        z = float(np.clip(z, self._z_bottom + r, self._z_top - r))
        p.position[:] = (x, y, z)
        speed = float(np.linalg.norm(p.velocity))
        if speed > 5.0:
            p.velocity *= 5.0 / speed

    def integrate(self) -> None:
        dt = self.dt
        for p in self.particles:
            acc = p.force / p.mass
            p.velocity += acc * dt
            p.position += p.velocity * dt
            self._clamp_particle(p)

    def max_speed(self) -> float:
        if not self.particles:
            return 0.0
        return max(float(np.linalg.norm(p.velocity)) for p in self.particles)

    def step(self) -> int:
        self.reset_forces()
        n_pairs = self.solve_particle_collisions()
        self.solve_wall_collisions()
        self.integrate()
        return n_pairs

    def run(self, max_steps: int) -> Dict[str, Any]:
        settled_run = 0
        collisions_total = 0
        for step_i in range(max_steps):
            collisions_total += self.step()
            vmax = self.max_speed()
            if vmax < self.settle_threshold or vmax < self.max_velocity_threshold:
                settled_run += 1
            else:
                settled_run = 0
            if settled_run >= self.settle_steps_required:
                return {
                    "steps_run": step_i + 1,
                    "settled": True,
                    "collisions_checked": collisions_total,
                    "final_max_velocity": vmax,
                }
        return {
            "steps_run": max_steps,
            "settled": False,
            "collisions_checked": collisions_total,
            "final_max_velocity": self.max_speed(),
        }


def _resolve_overlaps(
    particles: List[Particle],
    domain: PackedBedDomain,
    *,
    gap: float,
    max_iters: int = 1500,
    tol: float = 1e-9,
    safety: float = 1e-8,
) -> Dict[str, Any]:
    """relaxação pós-DEM: separa sobreposições residuais (contatos soft) projetando
    cada par para distância >= r_i+r_j+gap e reaplicando as paredes.

    isto torna o resultado do DEM compatível com a validação geométrica estrita
    (distância >= soma dos raios + gap), sem precisar de mais passos de dinâmica.
    devolve métricas de convergência.
    """
    n = len(particles)
    if n < 1:
        return {"contact_iters": 0, "max_overlap_before": 0.0, "max_overlap_after": 0.0, "converged": True}

    ann = domain.annulus
    # mesmos limites da validação (já incluem r_sphere + gap)
    _rho_min, rho_max = ann.radial_bounds()
    z_min, z_max = ann.z_bounds()
    # célula >= need (2*raio + gap) garante que todo par sobreposto cai em células
    # vizinhas (3x3x3); com 2*raio só, pares a >1 célula seriam perdidos
    cell = max((2.0 * p.radius for p in particles), default=0.01) + float(gap) + 1e-9

    max_overlap_before = 0.0
    max_overlap_after = 0.0
    for it in range(max_iters):
        positions = [p.position for p in particles]
        grid = build_spatial_grid(positions, cell)
        pairs = find_candidate_pairs(grid)
        max_ov = 0.0
        for i, j in pairs:
            pi = particles[i]
            pj = particles[j]
            dx = pj.position - pi.position
            dist = float(np.linalg.norm(dx))
            min_d = pi.radius + pj.radius + float(gap)
            if dist <= 1e-12:
                # centros coincidentes: separa numa direção arbitrária
                pj.position[0] += min_d * 0.5
                max_ov = max(max_ov, min_d)
                continue
            if dist < min_d:
                ov = min_d - dist
                if ov > max_ov:
                    max_ov = ov
                nrm = dx / dist
                shift = 0.5 * (ov + min_d * safety)
                pi.position -= nrm * shift
                pj.position += nrm * shift
        # paredes (radial + tampas), com os MESMOS limites da validação
        for p in particles:
            x = float(p.position[0])
            y = float(p.position[1])
            radial = math.hypot(x, y)
            if rho_max > 0 and radial > rho_max and radial > 1e-12:
                s = (rho_max * (1.0 - 1e-9)) / radial
                p.position[0] = x * s
                p.position[1] = y * s
            p.position[2] = min(max(float(p.position[2]), z_min), z_max)
            p.velocity[:] = 0.0
        if it == 0:
            max_overlap_before = max_ov
        max_overlap_after = max_ov
        if max_ov <= tol:
            return {
                "contact_iters": it + 1,
                "max_overlap_before": max_overlap_before,
                "max_overlap_after": max_ov,
                "converged": True,
            }
    return {
        "contact_iters": max_iters,
        "max_overlap_before": max_overlap_before,
        "max_overlap_after": max_overlap_after,
        "converged": max_overlap_after <= tol * 10.0,
    }


def _to_bool(v: Any, default: bool = True) -> bool:
    if isinstance(v, bool):
        return v
    if v is None:
        return default
    return str(v).strip().lower() in ("1", "true", "yes", "sim", "on")


def run_dem_packing(
    domain: PackedBedDomain,
    n_particles: int,
    packing: Dict[str, Any],
    *,
    warnings: Optional[List[str]] = None,
) -> Tuple[List[vec3], Dict[str, Any]]:
    w = warnings if warnings is not None else []
    params = merge_dem_params(packing)
    pk = domain.particle_kind
    if pk != "sphere":
        w.append(
            f"dem v1: colisao usa raio circunscrito para particle_type={pk}; "
            "malha exportada mantem forma real"
        )

    seed = int(params.get("seed", 42))
    particles = _spawn_particles(
        domain,
        n_particles,
        seed=seed,
        density=float(params.get("density", 2500.0)),
    )
    t0 = time.perf_counter()
    solver = SimpleDEMSolver(particles, domain, params)
    sim_meta = solver.run(int(params["steps"]))

    # assentamento final: resolve contatos soft residuais p/ passar na validação estrita
    resolve = _to_bool(params.get("resolve_contacts"), True)
    contact_meta: Dict[str, Any] = {}
    if resolve:
        contact_meta = _resolve_overlaps(
            particles,
            domain,
            gap=domain.gap,
            max_iters=int(params.get("contact_max_iters", 1500)),
            tol=float(params.get("contact_tolerance", 1e-9)),
        )
        if not contact_meta.get("converged"):
            w.append(
                "dem: resolução de contatos não convergiu totalmente "
                f"(sobreposição residual {contact_meta.get('max_overlap_after'):.2e} m)"
            )

    elapsed = time.perf_counter() - t0
    centers = [tuple(float(x) for x in p.position) for p in particles]
    meta = {
        **sim_meta,
        "elapsed_sec": elapsed,
        "dem_params": params,
        "n_placed": len(centers),
        "contact_resolution": contact_meta,
    }
    return centers, meta
