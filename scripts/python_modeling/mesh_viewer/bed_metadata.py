"""carregar parametros do leito a partir de .bed.json ao lado da malha."""
from __future__ import annotations

import json
from pathlib import Path
from typing import Any, Dict, List, Optional


def load_bed_json_for_mesh(mesh_path: Path, explicit: Optional[Path] = None) -> Optional[Dict[str, Any]]:
    """tenta explicit; senao mesh.stem + .bed.json no mesmo directorio."""
    candidates: List[Path] = []
    if explicit is not None:
        candidates.append(explicit.expanduser().resolve())
    mp = mesh_path.expanduser().resolve()
    candidates.append(mp.with_suffix(".bed.json"))
    seen: set[str] = set()
    for c in candidates:
        key = str(c)
        if key in seen:
            continue
        seen.add(key)
        if not c.is_file():
            continue
        try:
            with open(c, encoding="utf-8") as f:
                data = json.load(f)
            if isinstance(data, dict):
                return data
        except Exception:
            continue
    return None


def bed_summary_lines(meta: Optional[Dict[str, Any]], ext: Any) -> List[str]:
    """linhas curtas para o painel (portugues)."""
    if meta is None:
        ez = float(ext[2]) if hasattr(ext, "__len__") and len(ext) > 2 else 0.0
        return [
            "leito (.bed.json): nao encontrado",
            f"alt.aprox z={ez:.4f} m — params em .bed.json",
        ]
    out: List[str] = []
    b = meta.get("bed") if isinstance(meta.get("bed"), dict) else {}
    if b:
        out.append(f"altura (bed): {b.get('height', '?')}")
        out.append(f"diametro (bed): {b.get('diameter', '?')}")
        out.append(f"espessura parede: {b.get('wall_thickness', '?')}")
        if "clearance" in b:
            out.append(f"folga interna: {b['clearance']}")
    pt = meta.get("particles") if isinstance(meta.get("particles"), dict) else {}
    if pt:
        out.append(f"particulas (contagem): {pt.get('count', '?')}")
        out.append(f"diam. particula: {pt.get('diameter', '?')}")
        if "target_porosity" in pt:
            out.append(f"porosidade alvo: {pt['target_porosity']}")
    lids = meta.get("lids") if isinstance(meta.get("lids"), dict) else {}
    if lids:
        out.append(
            f"tampas: sup {lids.get('top_thickness', '?')} / "
            f"inf {lids.get('bottom_thickness', '?')}"
        )
    if not out:
        out.append("leito (.bed.json): sem blocos bed/particles reconhecidos")
    return out[:4]
