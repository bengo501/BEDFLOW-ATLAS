# dominio do leito empacotado (wrap packed_bed_science)
from __future__ import annotations

import sys
from dataclasses import dataclass
from pathlib import Path
from typing import Any, Dict, Tuple

_SCRIPTS = Path(__file__).resolve().parents[2] / "blender_scripts"
if str(_SCRIPTS) not in sys.path:
    sys.path.insert(0, str(_SCRIPTS))

from packed_bed_science.geometry_math import AnnulusBedDomain, collision_radius_for_particle_kind  # noqa: E402

vec3 = Tuple[float, float, float]


@dataclass
class PackedBedDomain:
    """parametros do cilindro oco para packing e dem."""

    r_int: float
    r_ext: float
    height: float
    bottom_cap_thickness: float
    top_cap_thickness: float
    gap: float
    particle_diameter: float
    particle_kind: str

    @property
    def annulus(self) -> AnnulusBedDomain:
        r_pack = collision_radius_for_particle_kind(
            self.particle_kind, self.particle_diameter
        )
        return AnnulusBedDomain(
            r_int=self.r_int,
            r_ext=self.r_ext,
            height=self.height,
            bottom_cap_thickness=self.bottom_cap_thickness,
            top_cap_thickness=self.top_cap_thickness,
            r_sphere=r_pack,
            gap=self.gap,
        )

    @classmethod
    def from_bed_params(cls, p: Dict[str, Any]) -> "PackedBedDomain":
        r_ext = float(p["diameter"]) / 2.0
        r_int = r_ext - float(p["wall_thickness"])
        pk = str(p.get("particle_kind") or "sphere").strip().lower()
        return cls(
            r_int=r_int,
            r_ext=r_ext,
            height=float(p["height"]),
            bottom_cap_thickness=float(p["bottom_thickness"]),
            top_cap_thickness=float(p["top_thickness"]),
            gap=float(p.get("gap") or 0.0),
            particle_diameter=float(p["particle_diameter"]),
            particle_kind=pk,
        )
