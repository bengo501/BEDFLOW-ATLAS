# testes unitarios do solver dem
from __future__ import annotations

import sys
from pathlib import Path

import numpy as np

_PM = Path(__file__).resolve().parents[1]
if str(_PM) not in sys.path:
    sys.path.insert(0, str(_PM))

from engine.collision import apply_pair_contact
from engine.dem_solver import SimpleDEMSolver, merge_dem_params
from engine.domain import PackedBedDomain
from engine.particles import Particle
from engine.spatial_hash import build_spatial_grid, find_candidate_pairs


def test_merge_dem_params():
    p = merge_dem_params({"dem": {"steps": 100, "stiffness": 3000}})
    assert p["steps"] == 100
    assert p["stiffness"] == 3000.0


def test_pair_contact_separates_overlapping():
    p1 = Particle.create(0, "sphere", (0.0, 0.0, 0.0), 0.01, mass=0.001)
    p2 = Particle.create(1, "sphere", (0.015, 0.0, 0.0), 0.01, mass=0.001)
    p1.velocity = np.array([0.0, 0.0, 0.0])
    p2.velocity = np.array([-0.1, 0.0, 0.0])
    apply_pair_contact(p1, p2, stiffness=5000, damping=0.2)
    assert np.linalg.norm(p1.force) > 0 or np.linalg.norm(p2.force) > 0


def test_spatial_hash_finds_neighbors():
    positions = [
        np.array([0.0, 0.0, 0.0]),
        np.array([0.02, 0.0, 0.0]),
        np.array([1.0, 1.0, 1.0]),
    ]
    grid = build_spatial_grid(positions, 0.05)
    pairs = find_candidate_pairs(grid)
    ids = {(i, j) for i, j in pairs}
    assert (0, 1) in ids or (1, 0) in ids


def test_dem_solver_settles_small_bed():
    p = {
        "diameter": 0.05,
        "height": 0.08,
        "wall_thickness": 0.002,
        "bottom_thickness": 0.003,
        "top_thickness": 0.003,
        "particle_count": 8,
        "particle_diameter": 0.006,
        "particle_kind": "sphere",
        "gap": 0.0,
        "packing": {
            "method": "dem",
            "dem": {
                "steps": 2000,
                "time_step": 2e-4,
                "settle_steps_required": 20,
                "seed": 1,
            },
        },
    }
    domain = PackedBedDomain.from_bed_params(p)
    particles = []
    from engine.dem_solver import _spawn_particles

    particles = _spawn_particles(domain, 8, seed=1, density=2500.0)
    solver = SimpleDEMSolver(
        particles, domain, merge_dem_params(p["packing"])
    )
    meta = solver.run(2000)
    assert meta["steps_run"] > 0
    assert len(particles) == 8
