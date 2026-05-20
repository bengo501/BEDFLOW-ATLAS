# registo de metadados dos ficheiros .bed (web, terminal, migrados)
from __future__ import annotations

import json
import re
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Dict, List, Optional

from bedflow_local_paths import beds_dir, project_root

REGISTRY_FILENAME = "_bed_registry.json"
REGISTRY_VERSION = 1


def registry_path() -> Path:
    return beds_dir() / REGISTRY_FILENAME


def _now_iso() -> str:
    return datetime.now(timezone.utc).isoformat()


def load_registry() -> Dict[str, Any]:
    path = registry_path()
    if not path.is_file():
        return {"version": REGISTRY_VERSION, "files": {}}
    try:
        data = json.loads(path.read_text(encoding="utf-8"))
    except (json.JSONDecodeError, OSError):
        return {"version": REGISTRY_VERSION, "files": {}}
    if not isinstance(data, dict):
        return {"version": REGISTRY_VERSION, "files": {}}
    data.setdefault("version", REGISTRY_VERSION)
    files = data.get("files")
    if not isinstance(files, dict):
        data["files"] = {}
    return data


def save_registry(data: Dict[str, Any]) -> None:
    path = registry_path()
    path.parent.mkdir(parents=True, exist_ok=True)
    payload = {
        "version": REGISTRY_VERSION,
        "updated_at": _now_iso(),
        "files": data.get("files") if isinstance(data.get("files"), dict) else {},
    }
    path.write_text(json.dumps(payload, indent=2, ensure_ascii=False), encoding="utf-8")


def normalize_bed_relative_path(rel_or_abs: str) -> str:
    p = Path(rel_or_abs)
    root = project_root().resolve()
    if p.is_absolute():
        try:
            return str(p.resolve().relative_to(root)).replace("\\", "/")
        except ValueError:
            return p.name
    return str(p).replace("\\", "/").lstrip("/")


def parse_creation_mode_from_bed(preview: str) -> Optional[str]:
    m = re.search(r"//\s*modo:\s*(\S+)", preview or "", re.IGNORECASE)
    return m.group(1).strip() if m else None


def register_bed_file(
    relative_path: str,
    *,
    source: str,
    creation_mode: str,
    filename: Optional[str] = None,
    created_at: Optional[str] = None,
    extra: Optional[Dict[str, Any]] = None,
) -> Dict[str, Any]:
    """grava ou atualiza metadados de um .bed no registo central."""
    rel = normalize_bed_relative_path(relative_path)
    data = load_registry()
    files: Dict[str, Any] = data["files"]
    prev = files.get(rel) if isinstance(files.get(rel), dict) else {}
    entry = {
        "relative_path": rel,
        "filename": filename or Path(rel).name,
        "source": source,
        "creation_mode": creation_mode,
        "created_at": created_at or prev.get("created_at") or _now_iso(),
        "updated_at": _now_iso(),
    }
    if isinstance(extra, dict):
        entry.update(extra)
    files[rel] = entry
    save_registry(data)
    return entry


def rename_registry_entry(old_rel: str, new_rel: str) -> None:
    old_key = normalize_bed_relative_path(old_rel)
    new_key = normalize_bed_relative_path(new_rel)
    if old_key == new_key:
        return
    data = load_registry()
    files: Dict[str, Any] = data["files"]
    if old_key in files:
        entry = dict(files.pop(old_key))
        entry["relative_path"] = new_key
        entry["filename"] = Path(new_key).name
        entry["updated_at"] = _now_iso()
        files[new_key] = entry
        save_registry(data)


def enrich_scan_item(item: Dict[str, Any], *, preview: str = "") -> Dict[str, Any]:
    """junta registo persistido ao item devolvido por scan_bed_files."""
    rel = normalize_bed_relative_path(item.get("relative_path") or "")
    reg = load_registry().get("files", {}).get(rel)
    if isinstance(reg, dict):
        item["source"] = reg.get("source") or item.get("origin", "terminal")
        item["creation_mode"] = reg.get("creation_mode") or parse_creation_mode_from_bed(preview)
        item["created_at"] = reg.get("created_at") or item.get("mtime_iso")
        item["storage_folder"] = str(Path(rel).parent).replace("\\", "/") or "."
    else:
        parsed_mode = parse_creation_mode_from_bed(preview)
        origin = item.get("origin") or "terminal"
        source = "web" if origin == "web" else "terminal"
        item["source"] = source
        item["creation_mode"] = parsed_mode or ("web" if origin == "web" else "terminal")
        item["created_at"] = item.get("mtime_iso")
        item["storage_folder"] = str(Path(rel).parent).replace("\\", "/") or "."
        if rel.lower().endswith(".bed"):
            register_bed_file(
                rel,
                source=source,
                creation_mode=item["creation_mode"],
                filename=item.get("filename"),
                created_at=item.get("mtime_iso"),
                extra={"backfilled": True},
            )
    return item
