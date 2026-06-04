#!/usr/bin/env python3
"""
export de formatos extra do motor python (além do STL): OBJ, glTF e GLB.

o motor python sempre grava STL; este módulo adiciona os formatos pedidos em
`export.formats` do `.bed`/JSON. OBJ é gravado nativamente; glTF/GLB usam
`trimesh` (já requerido pelos modos m2/m3). blend/fbx só existem no backend
blender.
"""
from __future__ import annotations

from pathlib import Path
from typing import Any, List, Optional

from slice_compare import write_obj_multi
from stl_mesh_utils import tri, vec3, write_stl_binary

# formatos que o motor python sabe gravar
SUPPORTED_FORMATS = ("stl", "obj", "gltf", "glb")
# formatos que dependem do blender
BLENDER_ONLY_FORMATS = ("blend", "fbx")


def normalize_export_formats(formats: Any) -> List[str]:
    """aceita lista ou string csv; mapeia stl_binary/ascii -> stl; remove duplicados."""
    if formats is None:
        return []
    if isinstance(formats, str):
        raw = [x.strip() for x in formats.split(",")]
    else:
        raw = list(formats)
    out: List[str] = []
    for f in raw:
        s = str(f).strip().lower().strip('"')
        if s in ("stl_binary", "stl_ascii"):
            s = "stl"
        if s and s not in out:
            out.append(s)
    return out


def export_mesh_formats(
    stl_path: Path,
    vertices: List[vec3],
    faces: List[tri],
    formats: Any,
    *,
    skip_stl: bool = True,
    warnings: Optional[List[str]] = None,
) -> List[str]:
    """grava os formatos pedidos ao lado de stl_path; devolve os nomes gerados.

    skip_stl=True assume que o STL já foi gravado pelo pipeline.
    """
    w = warnings if warnings is not None else []
    fmts = normalize_export_formats(formats)
    stl_path = Path(stl_path)
    stem = stl_path.stem
    parent = stl_path.parent
    parent.mkdir(parents=True, exist_ok=True)
    generated: List[str] = []

    _tm = {"mesh": None}

    def _trimesh_mesh():
        if _tm["mesh"] is None:
            import trimesh  # type: ignore

            _tm["mesh"] = trimesh.Trimesh(vertices=vertices, faces=faces, process=False)
        return _tm["mesh"]

    for fmt in fmts:
        if fmt == "stl":
            if not skip_stl:
                write_stl_binary(stl_path, vertices, faces)
                generated.append(stl_path.name)
            continue
        if fmt == "obj":
            p = parent / f"{stem}.obj"
            write_obj_multi(p, [(stem, vertices, faces, "")])
            generated.append(p.name)
            continue
        if fmt in ("gltf", "glb"):
            p = parent / f"{stem}.{fmt}"
            try:
                _trimesh_mesh().export(str(p))
                generated.append(p.name)
            except ImportError:
                w.append(f"export {fmt}: requer trimesh (pip install trimesh)")
            except Exception as exc:  # noqa: BLE001
                w.append(f"export {fmt} falhou: {exc}")
            continue
        if fmt in BLENDER_ONLY_FORMATS:
            w.append(f"export {fmt}: disponível apenas no backend blender")
        else:
            w.append(f"export {fmt}: formato não suportado pelo motor python")
    return generated


__all__ = [
    "SUPPORTED_FORMATS",
    "BLENDER_ONLY_FORMATS",
    "normalize_export_formats",
    "export_mesh_formats",
]
