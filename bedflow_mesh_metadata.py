# -*- coding: utf-8 -*-
"""
leitura de metadados de geometria a partir de sidecars json junto a malhas stl/obj.
usado pelo inventario /viewer/meshes e pelo cli.
"""
from __future__ import annotations

import json
from pathlib import Path
from typing import Any, Dict, List, Optional


def _sidecar_paths_for_mesh(mesh_path: Path) -> List[Path]:
    """candidatos por ordem de prioridade (primeiro encontrado com geometry_mode ganha merge)."""
    stem = mesh_path.stem
    parent = mesh_path.parent
    names = [
        f"{stem}_pure_bed.json",
        f"{stem}_packing_report.json",
        f"{stem}.bed.json",
    ]
    if stem.endswith("_pure"):
        base = stem[: -len("_pure")]
        names.insert(0, f"{base}_pure_bed.json")
    out: List[Path] = []
    for n in names:
        p = parent / n
        if p.is_file():
            out.append(p)
    return out


def _extract_geometry_fields(data: Dict[str, Any]) -> Dict[str, Any]:
    if not isinstance(data, dict):
        return {}
    gm = data.get("geometry_mode")
    sl = data.get("slice") if isinstance(data.get("slice"), dict) else {}
    st = data.get("statistical_2d") if isinstance(data.get("statistical_2d"), dict) else {}
    out: Dict[str, Any] = {}
    if gm:
        out["geometry_mode"] = str(gm)
    pt = data.get("porosity_target")
    if pt is None and st:
        pt = st.get("target_porosity")
    pr = data.get("porosity_result")
    if pr is None:
        pr = data.get("porosity_slice_plane")
    if pr is None:
        pr = data.get("porosity_estimate")
    if pt is not None:
        try:
            out["porosity_target"] = float(pt)
        except (TypeError, ValueError):
            pass
    if pr is not None:
        try:
            out["porosity_result"] = float(pr)
        except (TypeError, ValueError):
            pass
    pm = data.get("porosity_method") or data.get("packing_method")
    if pm:
        out["packing_method"] = str(pm)
    gb = data.get("generation_backend")
    if gb:
        out["generation_backend"] = str(gb)
    pk = data.get("particle_kind") or (data.get("particles") or {}).get("kind")
    if pk:
        out["particle_kind"] = str(pk)
    axis = sl.get("slice_axis")
    if axis:
        out["slice_axis"] = str(axis)
    for key, src in (
        ("slice_thickness", sl.get("slice_thickness", st.get("slice_thickness"))),
        ("slice_position", sl.get("slice_position")),
    ):
        if src is not None:
            try:
                out[key] = float(src)
            except (TypeError, ValueError):
                pass
    prast = data.get("porosity_raster")
    if isinstance(prast, dict) and prast.get("nx"):
        out["porosity_method"] = out.get("porosity_method") or "raster"
    return out


def load_mesh_geometry_metadata(mesh_path: Path) -> Dict[str, Any]:
    """
    le sidecars json no mesmo diretorio da malha.
    devolve dict plano para anexar a linhas de scan (campos opcionais).
    """
    merged: Dict[str, Any] = {}
    sidecar_used: Optional[str] = None
    for sp in _sidecar_paths_for_mesh(mesh_path):
        try:
            raw = json.loads(sp.read_text(encoding="utf-8"))
        except (OSError, json.JSONDecodeError):
            continue
        chunk = _extract_geometry_fields(raw)
        if chunk:
            merged.update(chunk)
            if sidecar_used is None:
                sidecar_used = sp.name
    if sidecar_used:
        merged["sidecar_json"] = sidecar_used
    return merged


def augment_mesh_row_with_sidecar(row: Dict[str, Any], mesh_path: Path) -> Dict[str, Any]:
    out = dict(row)
    meta = load_mesh_geometry_metadata(mesh_path)
    for k, v in meta.items():
        if v is not None and v != "":
            out[k] = v
    return out
