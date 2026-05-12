"""flags de visibilidade da malha solida, wire e bbox (sem open3d)."""
from __future__ import annotations

from dataclasses import dataclass


@dataclass
class MeshVisibilityController:
    show_mesh: bool = True
    wireframe: bool = False
    show_bbox: bool = False
