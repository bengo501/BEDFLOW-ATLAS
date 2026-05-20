# resultado unificado e relatorio json de empacotamento
from __future__ import annotations

import json
import time
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any, Dict, List, Optional, Tuple

vec3 = Tuple[float, float, float]


@dataclass
class PackingResult:
    centers: List[vec3]
    method: str
    particle_type: str
    n_requested: int
    n_placed: int
    porosity: float
    validation_ok: bool
    collisions_checked: int = 0
    wall_violations: int = 0
    elapsed_sec: float = 0.0
    metadata: Dict[str, Any] = field(default_factory=dict)
    report_path: Optional[Path] = None
    warnings: List[str] = field(default_factory=list)

    def to_dict(self) -> Dict[str, Any]:
        return {
            "packing_method": self.method,
            "particle_type": self.particle_type,
            "particle_kind": self.particle_type,
            "n_particles_requested": self.n_requested,
            "n_particles_placed": self.n_placed,
            "n_spheres_requested": self.n_requested,
            "n_spheres_placed": self.n_placed,
            "porosity_estimate": self.porosity,
            "validation_ok": self.validation_ok,
            "collisions_checked": self.collisions_checked,
            "wall_violations": self.wall_violations,
            "elapsed_sec": self.elapsed_sec,
            "warnings": list(self.warnings),
            "metadata": dict(self.metadata),
        }


def write_packing_report(result: PackingResult, path: Path) -> Path:
    path.parent.mkdir(parents=True, exist_ok=True)
    payload = {
        **result.to_dict(),
        "generated_at": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()),
    }
    with path.open("w", encoding="utf-8") as f:
        json.dump(payload, f, indent=2, ensure_ascii=False)
    result.report_path = path
    return path
