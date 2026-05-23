# resolução de seed para empacotamentos (repetível se definido, aleatório se ausente)
from __future__ import annotations

import random
from typing import Any, Dict, Optional, Tuple


def resolve_packing_random_seed(
    packing: Optional[Dict[str, Any]] = None,
    particles: Optional[Dict[str, Any]] = None,
) -> Tuple[int, bool]:
    """
    devolve (seed, auto_generated).
    se random_seed ou particles.seed estiverem no json, a disposição é repetível.
    caso contrário gera seed novo em cada execução.
    """
    packing = packing if isinstance(packing, dict) else {}
    particles = particles if isinstance(particles, dict) else {}
    raw = packing.get("random_seed")
    if raw is None:
        raw = particles.get("seed")
    if raw is None or raw == "":
        return random.randint(1, 2_147_483_647), True
    try:
        return int(raw), False
    except (TypeError, ValueError):
        return random.randint(1, 2_147_483_647), True
