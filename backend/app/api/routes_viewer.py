# endpoints para listar e servir malhas 3d ao visualizador web e ferramentas cli
from __future__ import annotations

import shutil
import subprocess
import sys
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Dict, List, Optional, Tuple

from fastapi import APIRouter, HTTPException, Query
from fastapi.responses import FileResponse
from pydantic import BaseModel, Field

from bedflow_local_paths import (
    mesh_id_for_relative_path,
    project_root,
    resolve_validated_mesh_path,
    scan_project_mesh_files,
)
from backend.app.services.blender_launch import (
    BLENDER_IMPORT_LOG_HINT,
    build_blender_launch_command,
    default_subprocess_log,
    popen_blender_mesh,
)

router = APIRouter()


class MeshInfo(BaseModel):
    mesh_id: str
    relative_path: str
    filename: str
    size_bytes: int
    mtime_iso: str
    format: str
    source_hint: str = Field(
        default="",
        description="origem inferida por caminho/nome (heuristica)",
    )
    recommended_modes: str = Field(
        default="",
        description="modos de visualizacao sugeridos (web | desktop | blender)",
    )
    geometry_mode: Optional[str] = Field(
        None, description="full_3d, pseudo_2d_thin_slice, pseudo_2d_statistical (sidecar)"
    )
    generation_backend: Optional[str] = Field(None, description="python_engine ou blender")
    packing_method: Optional[str] = Field(None, description="metodo de empacotamento ou statistical_reconstruction")
    particle_kind: Optional[str] = Field(None, description="sphere, cube, cylinder")
    porosity_target: Optional[float] = Field(None, description="porosidade alvo (2d/3d)")
    porosity_result: Optional[float] = Field(None, description="porosidade estimada no sidecar")
    porosity_method: Optional[str] = Field(None, description="raster ou formula (modo estatistico)")
    slice_axis: Optional[str] = Field(None, description="eixo da lamina fina x|y|z")
    slice_thickness: Optional[float] = Field(None, description="espessura da lamina (m)")
    slice_position: Optional[float] = Field(None, description="posicao do plano de corte (m)")
    sidecar_json: Optional[str] = Field(None, description="nome do ficheiro json lido")
    internal_cylinder_mode: Optional[str] = Field(
        None,
        description="hollow_boolean_applied | internal_cylinder_visible_no_boolean | solid_internal_cylinder_with_particle_holes",
    )
    boolean_operation_status: Optional[Dict[str, Any]] = Field(
        None, description="estado de booleanas no sidecar (outer_shell, inner_core, ...)"
    )
    boolean_outer_shell: Optional[str] = None
    boolean_inner_core: Optional[str] = None
    boolean_particle_tools: Optional[str] = None
    boolean_backend: Optional[str] = None
    boolean_warnings: Optional[str] = None
    job_id: Optional[str] = Field(None, description="id do job que gerou a malha")
    content_hash: Optional[str] = Field(None, description="sha256 do ficheiro de malha")
    packing_random_seed: Optional[Any] = Field(None, description="seed do empacotamento")
    particles_seed: Optional[Any] = Field(None, description="seed das partículas")
    modeling_profile: Optional[str] = Field(None, description="perfil python/blender")
    representation_dimension: Optional[str] = Field(
        None, description="2d ou 3d (heurística por geometry_mode)"
    )
    bed_particle_layout: Optional[str] = Field(
        None,
        description="solid_fill ou boolean_holes",
    )


class MeshListResponse(BaseModel):
    meshes: List[MeshInfo]
    total: int
    project_root_hint: str = Field(description="apenas informativo para o cli")


class LaunchViewerRequest(BaseModel):
    mesh_id: str = Field(..., min_length=8, max_length=32)


def _resolve_mesh_file(mesh_id: str) -> Tuple[Path, Dict[str, Any]]:
    for row in scan_project_mesh_files(max_files=2500):
        if row["mesh_id"] == mesh_id:
            p = resolve_validated_mesh_path(row["relative_path"])
            if p is None:
                raise HTTPException(status_code=404, detail="ficheiro invalido ou inexistente")
            return p, row
    raise HTTPException(status_code=404, detail="mesh nao encontrado")


def _to_mesh_info(row: Dict[str, Any]) -> MeshInfo:
    ts = datetime.fromtimestamp(row["mtime"], tz=timezone.utc).isoformat()

    def _opt_float(key: str) -> Optional[float]:
        v = row.get(key)
        if v is None:
            return None
        try:
            return float(v)
        except (TypeError, ValueError):
            return None

    return MeshInfo(
        mesh_id=row["mesh_id"],
        relative_path=row["relative_path"],
        filename=row["filename"],
        size_bytes=int(row["size_bytes"]),
        mtime_iso=ts,
        format=str(row["format"]),
        source_hint=str(row.get("source_hint") or ""),
        recommended_modes=str(row.get("recommended_modes") or ""),
        geometry_mode=row.get("geometry_mode"),
        generation_backend=row.get("generation_backend"),
        packing_method=row.get("packing_method"),
        particle_kind=row.get("particle_kind"),
        porosity_target=_opt_float("porosity_target"),
        porosity_result=_opt_float("porosity_result"),
        porosity_method=row.get("porosity_method"),
        slice_axis=row.get("slice_axis"),
        slice_thickness=_opt_float("slice_thickness"),
        slice_position=_opt_float("slice_position"),
        sidecar_json=row.get("sidecar_json"),
        internal_cylinder_mode=row.get("internal_cylinder_mode"),
        boolean_operation_status=row.get("boolean_operation_status")
        if isinstance(row.get("boolean_operation_status"), dict)
        else None,
        boolean_outer_shell=row.get("boolean_outer_shell"),
        boolean_inner_core=row.get("boolean_inner_core"),
        boolean_particle_tools=row.get("boolean_particle_tools"),
        boolean_backend=row.get("boolean_backend"),
        boolean_warnings=row.get("boolean_warnings"),
        job_id=row.get("job_id"),
        content_hash=row.get("content_hash"),
        packing_random_seed=row.get("packing_random_seed"),
        particles_seed=row.get("particles_seed"),
        modeling_profile=row.get("modeling_profile"),
        representation_dimension=row.get("representation_dimension"),
        bed_particle_layout=row.get("bed_particle_layout"),
    )


@router.get("/viewer/meshes", response_model=MeshListResponse, tags=["viewer"])
async def list_viewer_meshes(
    q: Optional[str] = Query(None, description="filtro por nome ou caminho"),
    limit: int = Query(200, ge=1, le=2000),
):
    """
    inventario de malhas e cenas 3d geradas (stl, obj, ply, gltf, glb, blend)
    a partir de local_data e pastas legadas generated/.
    """
    rows = scan_project_mesh_files(max_files=limit * 4)
    if q:
        ql = q.strip().lower()
        rows = [
            r
            for r in rows
            if ql in r["relative_path"].lower() or ql in r["filename"].lower()
        ]
    rows = rows[:limit]
    root = project_root()
    return MeshListResponse(
        meshes=[_to_mesh_info(r) for r in rows],
        total=len(rows),
        project_root_hint=str(root),
    )


@router.get("/viewer/meshes/recent", response_model=MeshListResponse, tags=["viewer"])
async def list_recent_meshes(limit: int = Query(12, ge=1, le=100)):
    rows = scan_project_mesh_files(max_files=limit)
    root = project_root()
    return MeshListResponse(
        meshes=[_to_mesh_info(r) for r in rows],
        total=len(rows),
        project_root_hint=str(root),
    )


@router.get("/viewer/meshes/lookup", response_model=MeshInfo, tags=["viewer"])
async def lookup_mesh_by_id(mesh_id: str = Query(..., min_length=8, max_length=32)):
    for row in scan_project_mesh_files(max_files=2500):
        if row["mesh_id"] == mesh_id:
            return _to_mesh_info(row)
    raise HTTPException(status_code=404, detail="mesh nao encontrado")


@router.get("/viewer/mesh-stream", tags=["viewer"])
async def stream_mesh_file(
    path: Optional[str] = Query(
        None, description="caminho relativo ao repo (ex.: local_data/models_3d/x.stl)"
    ),
    mesh_id: Optional[str] = Query(None, description="alternativa ao path"),
):
    """
    serve bytes da malha depois de validar prefixo permitido (sem path traversal).
    """
    rel: Optional[str] = path
    if mesh_id and not rel:
        for row in scan_project_mesh_files(max_files=2500):
            if row["mesh_id"] == mesh_id:
                rel = row["relative_path"]
                break
    if not rel:
        raise HTTPException(status_code=400, detail="path ou mesh_id obrigatorio")
    p = resolve_validated_mesh_path(rel)
    if p is None:
        raise HTTPException(status_code=404, detail="ficheiro invalido ou inexistente")
    if path and mesh_id and mesh_id_for_relative_path(rel) != mesh_id:
        raise HTTPException(status_code=400, detail="mesh_id nao corresponde ao path")
    return FileResponse(
        path=str(p),
        filename=p.name,
        media_type="application/octet-stream",
    )


@router.post("/viewer/launch-desktop", tags=["viewer"])
async def launch_desktop_viewer(body: LaunchViewerRequest):
    """abre mesh_viewer_desktop.py (open3d) para stl/obj/ply."""
    mesh_path, row = _resolve_mesh_file(body.mesh_id)
    ext = str(row.get("format") or mesh_path.suffix).lower().lstrip(".")
    if ext not in ("stl", "obj", "ply"):
        raise HTTPException(
            status_code=400,
            detail="formato nao suportado no visualizador desktop (use stl, obj ou ply)",
        )
    root = project_root()
    script = root / "scripts" / "python_modeling" / "mesh_viewer_desktop.py"
    if not script.is_file():
        raise HTTPException(status_code=404, detail=f"script nao encontrado: {script}")
    py = shutil.which("python") or shutil.which("python3") or sys.executable
    log_path = default_subprocess_log(root).with_name("bedflow_desktop_viewer.log")
    log_path.parent.mkdir(parents=True, exist_ok=True)
    try:
        with open(log_path, "ab", encoding="utf-8", errors="replace") as lf:
            lf.write(f"\n--- launch {mesh_path.name} ---\n")
            proc = subprocess.Popen(
                [py, str(script), str(mesh_path)],
                cwd=str(root),
                stdin=subprocess.DEVNULL,
                stdout=lf,
                stderr=subprocess.STDOUT,
            )
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e)) from e
    return {
        "ok": True,
        "message": "visualizador desktop solicitado",
        "filename": row.get("filename") or mesh_path.name,
        "path": str(mesh_path),
        "pid": proc.pid,
        "log_hint": str(log_path),
    }


@router.post("/viewer/launch-blender", tags=["viewer"])
async def launch_blender_viewer(body: LaunchViewerRequest):
    """abre o ficheiro no blender (executavel detetado no servidor)."""
    mesh_path, row = _resolve_mesh_file(body.mesh_id)
    from backend.app.services.blender_service import BlenderService

    svc = BlenderService()
    if not svc.check_availability():
        raise HTTPException(
            status_code=503,
            detail="blender nao encontrado no servidor (instale ou ajuste o PATH)",
        )
    root = project_root()
    try:
        _cmd, mode = build_blender_launch_command(
            svc.blender_exe, mesh_path, project_root=root
        )
        popen_blender_mesh(
            svc.blender_exe,
            mesh_path,
            project_root=root,
            log_file=default_subprocess_log(root),
        )
    except FileNotFoundError as e:
        raise HTTPException(status_code=404, detail=str(e)) from e
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e)) from e
    return {
        "ok": True,
        "message": "blender solicitado",
        "filename": row.get("filename") or mesh_path.name,
        "path": str(mesh_path),
        "launch_mode": mode,
        "import_log_hint": BLENDER_IMPORT_LOG_HINT
        if mode == "import_script"
        else None,
    }
