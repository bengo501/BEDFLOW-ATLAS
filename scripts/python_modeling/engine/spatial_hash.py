# grade espacial 3d para vizinhos de colisao O(n) amortizado
from __future__ import annotations

from typing import Dict, List, Sequence, Tuple

import numpy as np

CellKey = Tuple[int, int, int]


def _cell_index(coord: float, origin: float, cell_size: float) -> int:
    return int((coord - origin) // cell_size)


def build_spatial_grid(
    positions: Sequence[np.ndarray],
    cell_size: float,
    *,
    origin: Tuple[float, float, float] = (0.0, 0.0, 0.0),
) -> Dict[CellKey, List[int]]:
    grid: Dict[CellKey, List[int]] = {}
    cs = max(cell_size, 1e-12)
    ox, oy, oz = origin
    for i, pos in enumerate(positions):
        cx = _cell_index(float(pos[0]), ox, cs)
        cy = _cell_index(float(pos[1]), oy, cs)
        cz = _cell_index(float(pos[2]), oz, cs)
        key = (cx, cy, cz)
        grid.setdefault(key, []).append(i)
    return grid


def get_neighbor_cells(cell: CellKey) -> List[CellKey]:
    cx, cy, cz = cell
    out: List[CellKey] = []
    for dx in (-1, 0, 1):
        for dy in (-1, 0, 1):
            for dz in (-1, 0, 1):
                out.append((cx + dx, cy + dy, cz + dz))
    return out


def find_candidate_pairs(
    grid: Dict[CellKey, List[int]],
    *,
    dedupe: bool = True,
) -> List[Tuple[int, int]]:
    pairs: List[Tuple[int, int]] = []
    seen: set[Tuple[int, int]] = set()
    for key, indices in grid.items():
        for nk in get_neighbor_cells(key):
            other = grid.get(nk)
            if not other:
                continue
            for i in indices:
                for j in other:
                    if i >= j:
                        continue
                    pair = (i, j)
                    if dedupe:
                        if pair in seen:
                            continue
                        seen.add(pair)
                    pairs.append(pair)
    return pairs
