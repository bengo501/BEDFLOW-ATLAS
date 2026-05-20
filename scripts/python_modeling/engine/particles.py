# entidade particula para simulacao dem
from __future__ import annotations

from dataclasses import dataclass, field
from typing import Optional

import numpy as np


@dataclass
class Particle:
    id: int
    particle_type: str
    position: np.ndarray
    velocity: np.ndarray
    force: np.ndarray
    radius: float
    mass: float
    orientation: Optional[np.ndarray] = None
    angular_velocity: Optional[np.ndarray] = field(default=None)

    @classmethod
    def create(
        cls,
        pid: int,
        particle_type: str,
        position: tuple[float, float, float],
        radius: float,
        *,
        mass: float | None = None,
        density: float = 2500.0,
    ) -> "Particle":
        r = float(radius)
        m = float(mass if mass is not None else density * (4.0 / 3.0) * np.pi * r**3)
        pos = np.array(position, dtype=np.float64)
        return cls(
            id=pid,
            particle_type=(particle_type or "sphere").strip().lower(),
            position=pos,
            velocity=np.zeros(3, dtype=np.float64),
            force=np.zeros(3, dtype=np.float64),
            radius=r,
            mass=m,
        )
