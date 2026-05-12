"""enquadramento inicial da orbita em torno do centro da malha."""
from __future__ import annotations

from typing import Any

import numpy as np


def setup_orbit_camera(
    scene_widget: Any,
    model_bounds: Any,
    center: np.ndarray,
    fov_deg: float = 60.0,
) -> None:
    cor = np.asarray(center, dtype=np.float32).reshape(3, 1)
    scene_widget.setup_camera(float(fov_deg), model_bounds, cor)
