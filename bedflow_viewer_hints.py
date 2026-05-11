# -*- coding: utf-8 -*-
"""
metadados heuristica para o inventario de malhas (cli, api, wizard).
nao le ficheiros — apenas caminho/nome/extensao.
"""
from __future__ import annotations

from typing import Any, Dict


def mesh_source_hint(relative_path: str, filename: str) -> str:
    """inferencia grossa da origem provavel (gerador real pode variar)."""
    r = (relative_path or "").replace("\\", "/").lower()
    fn = (filename or "").lower()
    if "_pure" in fn or fn.endswith("_pure.stl"):
        return "python puro (stl)"
    if "local_data/models_3d/" in r:
        return "wizard / pipeline (models_3d)"
    if "generated/batch" in r or "generated/3d" in r:
        return "geracao batch / saida 3d"
    if "local_data/simulations" in r or "generated/cfd" in r:
        return "cfd / simulacao"
    if "local_data/aux" in r:
        return "auxiliar (local_data/aux)"
    if "/" not in r.strip("/"):
        return "raiz do repositorio"
    return "outros caminhos do projeto"


def mesh_recommended_modes(relative_path: str, format_ext: str) -> str:
    """lista curta de modos de visualizacao alinhados ao codigo actual."""
    ext = (format_ext or "").strip().lower().lstrip(".")
    _ = relative_path  # reservado para futuras regras por pasta
    if ext == "blend":
        return "blender (cena)"
    order: list[str] = []
    if ext in ("stl", "obj", "ply", "gltf", "glb"):
        order.append("web (three.js)")
    if ext in ("stl", "obj", "ply"):
        order.append("desktop (open3d)")
    if ext in ("stl", "obj", "ply", "gltf", "glb"):
        order.append("blender (import)")
    return " | ".join(order) if order else "—"


def augment_mesh_scan_row(row: Dict[str, Any]) -> Dict[str, Any]:
    out = dict(row)
    rel = str(out.get("relative_path") or "")
    fn = str(out.get("filename") or "")
    fmt = str(out.get("format") or "")
    out["source_hint"] = mesh_source_hint(rel, fn)
    out["recommended_modes"] = mesh_recommended_modes(rel, fmt)
    return out
