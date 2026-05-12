"""textos dos paineis 2d fixos (hud) — sem widgets, so strings."""
from __future__ import annotations

from pathlib import Path
from typing import Any, Dict, List, Optional

import numpy as np

from mesh_viewer.bed_metadata import bed_summary_lines
from mesh_viewer.cut_controller import CutController


def inspection_tips_lines() -> List[str]:
    return [
        "dica: corte no eixo z (lado max/min) ajuda a ver particulas mais claras.",
        "dica: marque 'arestas' e opacidade 1 (opaco) para contornos nitidos no interior.",
        "dica: se a parede tapar o interior, baixe a opacidade e combine com corte.",
    ]


def model_overlay_lines(
    path: Path,
    n_vert: int,
    n_tri: int,
    n_comp: int,
    ext: np.ndarray,
    cut: CutController,
    bed_meta: Optional[Dict[str, Any]] = None,
    max_lines: int = 14,
) -> List[str]:
    ax = ("x", "y", "z")[cut.axis % 3]
    side = "max" if cut.from_max else "min"
    ex, ey, ez = float(ext[0]), float(ext[1]), float(ext[2])
    dia = float(max(ex, ez))
    lines: List[str] = [f"ficheiro: {path.name}"]
    lines.extend(bed_summary_lines(bed_meta, ext))
    lines.extend(
        [
            f"v={n_vert}  t={n_tri}  comp~{n_comp}",
            f"extents m x={ex:.3f} y={ey:.3f} z={ez:.3f}  diam~{dia:.3f}",
            f"corte: {cut.clip_frac:.3f}  eixo={ax}  lado={side}",
        ]
    )
    lines.extend(inspection_tips_lines())
    return lines[: int(max_lines)]


def camera_overlay_lines(scene_widget: Any) -> Optional[List[str]]:
    try:
        cam = scene_widget.scene.camera
        fov = float(cam.get_field_of_view())
        vm = np.asarray(cam.get_view_matrix())
        inv = np.linalg.inv(vm)
        pos = inv[:3, 3]
        px, py, pz = float(pos[0]), float(pos[1]), float(pos[2])
        return [
            "modo: trackball (parecido ao blender)",
            "orbita: btn esquerdo  [no blender: btn do meio]",
            "pan: btn direito  [no blender: shift + meio]",
            "zoom: roda  [alt: shift + esq arrasta = dolly]",
            "duplo clique esq: pivot na superficie",
            f"pos: x={px:.2f} y={py:.2f} z={pz:.2f}",
            f"fov: {fov:.1f} deg",
            "reset: barra lateral",
        ]
    except Exception:
        return None
