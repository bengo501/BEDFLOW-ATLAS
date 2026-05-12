"""estado e operacoes de corte por crop (caixa alinhada aos eixos)."""
from __future__ import annotations

from dataclasses import dataclass
from typing import Any

from mesh_viewer.geometry_core import crop_mesh_slab


@dataclass
class CutController:
    clip_frac: float = 0.0
    axis: int = 1
    from_max: bool = True

    def cropped_mesh(self, mesh_orig: Any) -> Any:
        return crop_mesh_slab(
            mesh_orig, float(self.clip_frac), int(self.axis), bool(self.from_max)
        )

    def set_clip(self, v: float) -> None:
        self.clip_frac = float(v)

    def nudge(self, dv: float, lo: float = 0.0, hi: float = 0.95) -> None:
        self.clip_frac = max(lo, min(hi, float(self.clip_frac) + float(dv)))

    def reset(self) -> None:
        self.clip_frac = 0.0

    def set_axis(self, i: int) -> None:
        self.axis = int(i) % 3
