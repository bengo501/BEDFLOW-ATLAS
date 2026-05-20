# listagem e leitura de ficheiros .bed gerados (web, terminal, legado)
from __future__ import annotations

from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Dict, List, Optional

from fastapi import APIRouter, HTTPException, Query
from fastapi.responses import FileResponse
from pydantic import BaseModel

from bedflow_local_paths import project_root, resolve_validated_bed_path, scan_bed_files

router = APIRouter(tags=["bed-files"])


class BedFileItem(BaseModel):
    relative_path: str
    filename: str
    size_bytes: int
    mtime_iso: str
    has_json: bool
    json_relative_path: Optional[str] = None
    origin: str
    source: str = "terminal"
    creation_mode: Optional[str] = None
    created_at: Optional[str] = None
    storage_folder: Optional[str] = None


class BedFileListResponse(BaseModel):
    items: List[BedFileItem]
    total: int
    page: int
    limit: int
    total_pages: int


class BedFileContentResponse(BaseModel):
    relative_path: str
    filename: str
    content: str
    size_bytes: int
    mtime_iso: str
    has_json: bool
    json_relative_path: Optional[str] = None
    origin: str
    source: str = "terminal"
    creation_mode: Optional[str] = None
    created_at: Optional[str] = None
    storage_folder: Optional[str] = None


def _filter_items(
    items: List[Dict[str, Any]],
    *,
    search: Optional[str],
    has_json: Optional[bool],
    origin: Optional[str],
    creation_mode: Optional[str] = None,
) -> List[Dict[str, Any]]:
    out = items
    if search:
        q = search.strip().lower()
        out = [
            x
            for x in out
            if q in x["filename"].lower()
            or q in x["relative_path"].lower()
            or q in str(x.get("creation_mode") or "").lower()
            or q in str(x.get("storage_folder") or "").lower()
        ]
    if has_json is not None:
        out = [x for x in out if bool(x.get("has_json")) is has_json]
    if origin:
        o = origin.strip().lower()
        out = [
            x
            for x in out
            if str(x.get("origin", "")).lower() == o
            or str(x.get("source", "")).lower() == o
        ]
    if creation_mode:
        cm = creation_mode.strip().lower()
        out = [x for x in out if str(x.get("creation_mode") or "").lower() == cm]
    return out


@router.get("/bed-files", response_model=BedFileListResponse)
async def list_bed_files(
    page: int = Query(1, ge=1),
    limit: int = Query(12, ge=1, le=100),
    search: Optional[str] = Query(None),
    has_json: Optional[bool] = Query(None),
    origin: Optional[str] = Query(None),
    creation_mode: Optional[str] = Query(None),
):
    """lista ficheiros .bed no disco (local_data/beds, legado, dsl, raiz)."""
    all_items = scan_bed_files()
    filtered = _filter_items(
        all_items,
        search=search,
        has_json=has_json,
        origin=origin,
        creation_mode=creation_mode,
    )
    total = len(filtered)
    total_pages = max(1, (total + limit - 1) // limit)
    page = min(page, total_pages)
    start = (page - 1) * limit
    page_items = filtered[start : start + limit]
    return BedFileListResponse(
        items=[BedFileItem(**row) for row in page_items],
        total=total,
        page=page,
        limit=limit,
        total_pages=total_pages,
    )


@router.get("/bed-files/content", response_model=BedFileContentResponse)
async def get_bed_file_content(rel: str = Query(..., description="caminho relativo ao repo")):
    fp = resolve_validated_bed_path(rel)
    if fp is None or not fp.is_file():
        raise HTTPException(status_code=404, detail="ficheiro .bed nao encontrado")
    try:
        content = fp.read_text(encoding="utf-8", errors="replace")
    except OSError as e:
        raise HTTPException(status_code=500, detail=str(e)) from e
    st = fp.stat()
    json_path = Path(f"{fp}.json")
    if not json_path.is_file():
        alt = fp.with_suffix(".bed.json")
        json_path = alt if alt.is_file() else json_path
    root = project_root().resolve()
    json_rel = None
    if json_path.is_file():
        try:
            json_rel = str(json_path.relative_to(root)).replace("\\", "/")
        except ValueError:
            json_rel = json_path.name
    rel_norm = str(fp.relative_to(root)).replace("\\", "/")
    from bedflow_local_paths import _detect_bed_origin
    from bedflow_bed_registry import enrich_scan_item

    row = enrich_scan_item(
        {
            "relative_path": rel_norm,
            "filename": fp.name,
            "mtime_iso": datetime.fromtimestamp(st.st_mtime, tz=timezone.utc).isoformat(),
            "origin": _detect_bed_origin(content[:1200]),
        },
        preview=content[:1200],
    )

    return BedFileContentResponse(
        relative_path=rel_norm,
        filename=fp.name,
        content=content,
        size_bytes=st.st_size,
        mtime_iso=row.get("mtime_iso") or datetime.fromtimestamp(st.st_mtime, tz=timezone.utc).isoformat(),
        has_json=json_path.is_file(),
        json_relative_path=json_rel,
        origin=row.get("origin") or _detect_bed_origin(content[:1200]),
        source=row.get("source") or "terminal",
        creation_mode=row.get("creation_mode"),
        created_at=row.get("created_at"),
        storage_folder=row.get("storage_folder"),
    )


@router.get("/bed-files/download")
async def download_bed_file(rel: str = Query(...)):
    fp = resolve_validated_bed_path(rel)
    if fp is None or not fp.is_file():
        raise HTTPException(status_code=404, detail="ficheiro .bed nao encontrado")
    return FileResponse(
        path=str(fp),
        media_type="text/plain",
        filename=fp.name,
    )
