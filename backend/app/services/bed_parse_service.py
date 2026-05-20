# parse e compile de ficheiros .bed com overrides (modal carregar .bed)
from __future__ import annotations

import json
import subprocess
import sys
import tempfile
from pathlib import Path
from typing import Any, Dict, List, Optional, Tuple

from bedflow_local_paths import beds_dir, project_root


def _dsl_dir() -> Path:
    return project_root() / "dsl"


def _compiler_script() -> Path:
    return _dsl_dir() / "compiler" / "bed_compiler_antlr_standalone.py"


def _import_wizard_loader():
    dsl = _dsl_dir()
    if str(dsl) not in sys.path:
        sys.path.insert(0, str(dsl))
    from wizard_json_loader import (  # noqa: WPS433
        json_to_wizard_params,
        load_wizard_json,
        normalize_loaded_dict,
        patch_compiled_json_bed,
        patch_compiled_json_export,
        patch_compiled_json_metadata,
        patch_compiled_json_packing,
        patch_compiled_json_slice,
        patch_compiled_json_statistical,
    )

    return {
        "json_to_wizard_params": json_to_wizard_params,
        "load_wizard_json": load_wizard_json,
        "normalize_loaded_dict": normalize_loaded_dict,
        "patch_compiled_json_bed": patch_compiled_json_bed,
        "patch_compiled_json_export": patch_compiled_json_export,
        "patch_compiled_json_metadata": patch_compiled_json_metadata,
        "patch_compiled_json_packing": patch_compiled_json_packing,
        "patch_compiled_json_slice": patch_compiled_json_slice,
        "patch_compiled_json_statistical": patch_compiled_json_statistical,
    }


def _run_antlr_compile(bed_path: Path, json_path: Path) -> Tuple[bool, str, str]:
    dsl_dir = _dsl_dir()
    script = _compiler_script()
    if not script.exists():
        return False, "", "compilador não encontrado"
    result = subprocess.run(
        [
            sys.executable,
            str(script),
            str(bed_path),
            "-o",
            str(json_path),
            "-v",
        ],
        capture_output=True,
        text=True,
        timeout=30,
        cwd=str(dsl_dir),
    )
    if result.returncode != 0:
        return False, result.stdout, result.stderr
    return True, result.stdout, result.stderr


def _extract_parsed_summary(data: Dict[str, Any]) -> Dict[str, Any]:
    w = _import_wizard_loader()["json_to_wizard_params"](data)
    bed = w.get("bed") or {}
    particles = w.get("particles") or {}
    packing = w.get("packing") or {}
    export = w.get("export") or {}
    vis = bed.get("visibility") if isinstance(bed.get("visibility"), dict) else {}
    summary = {
        "bed": {
            "diameter": bed.get("diameter"),
            "height": bed.get("height"),
            "wall_thickness": bed.get("wall_thickness"),
            "internal_cylinder_mode": bed.get("internal_cylinder_mode"),
            "visibility": vis,
        },
        "particles": {
            "kind": particles.get("kind"),
            "count": particles.get("count"),
            "diameter": particles.get("diameter"),
            "target_porosity": particles.get("target_porosity"),
        },
        "packing": {
            "method": packing.get("method") or data.get("packing_mode"),
            "gap": packing.get("gap"),
        },
        "geometry_mode": w.get("geometry_mode") or data.get("geometry_mode") or "full_3d",
        "generation_backend": w.get("generation_backend")
        or data.get("generation_backend")
        or "blender",
        "export": {
            "formats": export.get("formats") or [],
        },
    }
    if w.get("slice"):
        summary["slice"] = dict(w["slice"])
    if w.get("statistical_2d"):
        summary["statistical_2d"] = dict(w["statistical_2d"])
    return summary


def _deep_merge(base: Dict[str, Any], override: Dict[str, Any]) -> Dict[str, Any]:
    out = dict(base)
    for k, v in override.items():
        if v is None:
            continue
        if isinstance(v, dict) and isinstance(out.get(k), dict):
            out[k] = _deep_merge(out[k], v)
        else:
            out[k] = v
    return out


def _wizard_dict_from_parsed_and_overrides(
    compiled: Dict[str, Any], overrides: Optional[Dict[str, Any]]
) -> Dict[str, Any]:
    w = _import_wizard_loader()["json_to_wizard_params"](compiled)
    if not overrides:
        return w
    merged = _deep_merge(w, overrides)
    gb = overrides.get("generation_backend")
    if gb:
        if str(gb).lower() in ("pure_python", "python"):
            merged["generation_backend"] = "python_engine"
        else:
            merged["generation_backend"] = str(gb)
    gm = overrides.get("geometry_mode")
    if gm:
        merged["geometry_mode"] = gm
        if gm == "pseudo_2d_statistical":
            merged.pop("slice", None)
        elif gm == "pseudo_2d_thin_slice":
            merged.pop("statistical_2d", None)
        elif gm == "full_3d":
            merged.pop("slice", None)
            merged.pop("statistical_2d", None)
    pack_ov = overrides.get("packing")
    if isinstance(pack_ov, dict) and pack_ov.get("method"):
        merged.setdefault("packing", {})
        merged["packing"]["method"] = pack_ov["method"]
        merged["packing_mode"] = pack_ov["method"]
    return merged


def _apply_patches(json_path: Path, wizard_dict: Dict[str, Any]) -> None:
    loader = _import_wizard_loader()
    loader["patch_compiled_json_packing"](json_path, wizard_dict)
    loader["patch_compiled_json_export"](json_path, wizard_dict)
    loader["patch_compiled_json_metadata"](json_path, wizard_dict)
    loader["patch_compiled_json_slice"](json_path, wizard_dict)
    loader["patch_compiled_json_statistical"](json_path, wizard_dict)
    loader["patch_compiled_json_bed"](json_path, wizard_dict)
    _force_overrides_into_json(json_path, wizard_dict)


def _force_overrides_into_json(json_path: Path, wizard_dict: Dict[str, Any]) -> None:
    with json_path.open("r", encoding="utf-8") as f:
        data = json.load(f)
    gb = wizard_dict.get("generation_backend")
    if gb is not None:
        data["generation_backend"] = gb
    gm = wizard_dict.get("geometry_mode")
    if gm is not None:
        data["geometry_mode"] = gm
    pm = wizard_dict.get("packing_mode") or (wizard_dict.get("packing") or {}).get("method")
    if pm:
        data["packing_mode"] = str(pm)
        pack = dict(data.get("packing") or {})
        pack["method"] = str(pm)
        data["packing"] = pack
    if isinstance(wizard_dict.get("packing"), dict):
        pack = dict(data.get("packing") or {})
        for k, v in wizard_dict["packing"].items():
            if v is not None:
                pack[k] = v
        data["packing"] = pack
    if isinstance(wizard_dict.get("slice"), dict) and wizard_dict["slice"]:
        data["slice"] = dict(wizard_dict["slice"])
    if isinstance(wizard_dict.get("statistical_2d"), dict) and wizard_dict["statistical_2d"]:
        data["statistical_2d"] = dict(wizard_dict["statistical_2d"])
    if gm == "pseudo_2d_statistical":
        data.pop("slice", None)
    if isinstance(wizard_dict.get("bed"), dict):
        bed = dict(data.get("bed") or {})
        wbed = wizard_dict["bed"]
        if wbed.get("internal_cylinder_mode"):
            bed["internal_cylinder_mode"] = wbed["internal_cylinder_mode"]
        if isinstance(wbed.get("visibility"), dict):
            bed["visibility"] = {**dict(bed.get("visibility") or {}), **wbed["visibility"]}
        data["bed"] = bed
    if isinstance(wizard_dict.get("export"), dict):
        exp = dict(data.get("export") or {})
        wexp = wizard_dict["export"]
        if wexp.get("formats"):
            exp["formats"] = wexp["formats"]
        data["export"] = exp
    _import_wizard_loader()["normalize_loaded_dict"](data)
    with json_path.open("w", encoding="utf-8") as f:
        json.dump(data, f, indent=2, ensure_ascii=False)


def _diff_parsed_vs_working(
    parsed_summary: Dict[str, Any], working: Dict[str, Any]
) -> List[Dict[str, Any]]:
    diffs: List[Dict[str, Any]] = []

    def _walk(path: str, a: Any, b: Any) -> None:
        if isinstance(a, dict) and isinstance(b, dict):
            keys = set(a.keys()) | set(b.keys())
            for k in keys:
                _walk(f"{path}.{k}" if path else k, a.get(k), b.get(k))
            return
        if a != b:
            diffs.append({"path": path, "from": a, "to": b})

    working_summary = _extract_parsed_summary(working)
    _walk("", parsed_summary, working_summary)
    return diffs


def parse_bed_content(content: str, filename: str = "parse.bed") -> Dict[str, Any]:
    content = (content or "").strip()
    if not content:
        return {
            "valid": False,
            "filename": filename,
            "parsed": None,
            "warnings": [],
            "errors": [{"message": "conteúdo vazio"}],
            "stderr": "",
        }
    safe = Path(filename).name if filename else "parse.bed"
    if not safe.lower().endswith(".bed"):
        safe = f"{safe}.bed"

    with tempfile.TemporaryDirectory(prefix="bedflow_parse_") as tmp:
        bed_path = Path(tmp) / safe
        json_path = Path(f"{bed_path}.json")
        bed_path.write_text(content, encoding="utf-8")
        ok, stdout, stderr = _run_antlr_compile(bed_path, json_path)
        if not ok:
            return {
                "valid": False,
                "filename": safe,
                "parsed": None,
                "warnings": [],
                "errors": [{"message": stderr or stdout or "erro na compilação"}],
                "stderr": stderr,
            }
        loader = _import_wizard_loader()
        data = loader["load_wizard_json"](json_path)
        parsed = _extract_parsed_summary(data)
        warnings: List[str] = []
        if not data.get("generation_backend"):
            warnings.append("generation_backend ausente no json; default blender assumido após patch")
        return {
            "valid": True,
            "filename": safe,
            "parsed": parsed,
            "warnings": warnings,
            "errors": [],
            "stderr": stderr,
        }


def _unique_bed_path(base_name: str) -> Path:
    out_dir = beds_dir()
    out_dir.mkdir(parents=True, exist_ok=True)
    candidate = out_dir / base_name
    if not candidate.exists():
        return candidate
    stem = candidate.stem
    suffix = candidate.suffix
    n = 1
    while True:
        alt = out_dir / f"{stem}_{n}{suffix}"
        if not alt.exists():
            return alt
        n += 1


def compile_from_bed(
    *,
    content: Optional[str] = None,
    bed_path: Optional[str] = None,
    filename: str = "leito_custom.bed",
    overrides: Optional[Dict[str, Any]] = None,
    hub_mode: str = "bed_editor",
    save_to_db: bool = False,
    user_id: int = 1,
    db_session=None,
) -> Dict[str, Any]:
    root = project_root()
    if content is None and bed_path:
        p = Path(bed_path)
        if not p.is_absolute():
            p = root / p
        if not p.exists():
            raise FileNotFoundError(f"bed não encontrado: {bed_path}")
        content = p.read_text(encoding="utf-8")
        filename = p.name
    if not content or not str(content).strip():
        raise ValueError("conteúdo do arquivo .bed está vazio")

    safe = Path(filename).name if filename else "leito_custom.bed"
    if not safe.lower().endswith(".bed"):
        safe = f"{safe}.bed"

    bed_file_path = _unique_bed_path(safe)
    bed_file_path.write_text(content, encoding="utf-8")
    json_file_path = Path(f"{bed_file_path}.json")

    ok, stdout, stderr = _run_antlr_compile(bed_file_path, json_file_path)
    if not ok:
        raise RuntimeError(stderr or stdout or "erro na compilação")

    loader = _import_wizard_loader()
    compiled = loader["load_wizard_json"](json_file_path)
    parsed_summary = _extract_parsed_summary(compiled)
    wizard_dict = _wizard_dict_from_parsed_and_overrides(compiled, overrides)
    _apply_patches(json_file_path, wizard_dict)
    working = loader["load_wizard_json"](json_file_path)
    diff = _diff_parsed_vs_working(parsed_summary, working)

    def _rel(p: Path) -> str:
        try:
            return str(p.resolve().relative_to(root.resolve())).replace("\\", "/")
        except ValueError:
            return str(p.resolve()).replace("\\", "/")

    rel_bed = _rel(bed_file_path)
    rel_json = _rel(json_file_path)

    try:
        from bedflow_bed_registry import register_bed_file

        register_bed_file(
            rel_bed,
            source="web_bed_modal",
            creation_mode=hub_mode,
            filename=safe,
        )
    except ImportError:
        pass

    result: Dict[str, Any] = {
        "success": True,
        "bed_file": rel_bed,
        "json_file": rel_json,
        "filename": bed_file_path.name,
        "working_json": working,
        "parsed": parsed_summary,
        "diff_from_parsed": diff,
        "message": "arquivo .bed compilado com sucesso",
    }

    if save_to_db:
        bed_id = save_compiled_bed_to_db(
            working=working,
            rel_bed=rel_bed,
            rel_json=rel_json,
            stem=bed_file_path.stem,
            hub_mode=hub_mode,
            user_id=user_id,
            db_session=db_session,
        )
        if bed_id is not None:
            result["bed_id"] = bed_id

    return result


def save_compiled_bed_to_db(
    *,
    working: Dict[str, Any],
    rel_bed: str,
    rel_json: str,
    stem: str,
    hub_mode: str,
    user_id: int = 1,
    db_session=None,
) -> Optional[int]:
    try:
        from backend.app.database import crud, schemas
        from backend.app.database.connection import DatabaseConnection

        params = _import_wizard_loader()["json_to_wizard_params"](working)
        p_bed = params.get("bed") or {}
        p_part = params.get("particles") or {}
        p_pack = params.get("packing") or {}
        bed_data = schemas.BedCreate(
            name=stem,
            description=f"leito modal .bed ({hub_mode})",
            diameter=float(p_bed.get("diameter", 0.05)),
            height=float(p_bed.get("height", 0.1)),
            wall_thickness=float(p_bed.get("wall_thickness", 0.002)),
            particle_count=int(p_part.get("count", 100)),
            particle_diameter=float(p_part.get("diameter", 0.005)),
            particle_kind=str(p_part.get("kind", "sphere")),
            packing_method=str(p_pack.get("method", "rigid_body")),
            porosity=p_part.get("target_porosity"),
            bed_file_path=rel_bed,
            json_file_path=rel_json,
            parameters_json=params,
            created_by="web_bed_modal",
        )
        session = db_session
        own = None
        if session is None:
            own = DatabaseConnection.get_session()
            session = own
        db_bed = crud.BedCRUD.create(session, bed_data, user_id=user_id)
        if own is not None:
            own.close()
        return int(db_bed.id)
    except Exception:
        return None
