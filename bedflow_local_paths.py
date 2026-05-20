# caminhos canonicos para artefactos locais (cli, fastapi, wizard)
# raiz = pasta do repositorio (pai deste ficheiro)
from __future__ import annotations

import hashlib
import os
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Dict, List, Optional, Tuple

_REPO_ROOT = Path(__file__).resolve().parent

# extensoes de malha que o visualizador web e desktop tentam carregar
VIEWER_MESH_EXTENSIONS: Tuple[str, ...] = (
    ".stl",
    ".obj",
    ".ply",
    ".gltf",
    ".glb",
)

# ficheiros de cena blender (so desktop / blender, nao three direto)
VIEWER_SCENE_EXTENSIONS: Tuple[str, ...] = (".blend",)

# prefixos relativos à raiz do repo onde procurar malhas
VIEWER_MESH_PATH_PREFIXES: Tuple[str, ...] = (
    "local_data/models_3d/",
    "local_data/aux/",
    "local_data/simulations/",
    "generated/3d/output/",
    "generated/batch/",
    "generated/cfd/",
)


def project_root() -> Path:
    return _REPO_ROOT


def local_data_root() -> Path:
    p = project_root() / "local_data"
    p.mkdir(parents=True, exist_ok=True)
    return p


def beds_dir() -> Path:
    d = local_data_root() / "beds"
    d.mkdir(parents=True, exist_ok=True)
    return d


def models_3d_dir() -> Path:
    d = local_data_root() / "models_3d"
    d.mkdir(parents=True, exist_ok=True)
    return d


def simulations_dir() -> Path:
    d = local_data_root() / "simulations"
    d.mkdir(parents=True, exist_ok=True)
    return d


def reports_dir() -> Path:
    d = local_data_root() / "reports"
    d.mkdir(parents=True, exist_ok=True)
    return d


def aux_dir() -> Path:
    d = local_data_root() / "aux"
    d.mkdir(parents=True, exist_ok=True)
    return d


def legacy_generated_root() -> Path:
    p = project_root() / "generated"
    p.mkdir(parents=True, exist_ok=True)
    return p


def legacy_output_root() -> Path:
    p = project_root() / "output"
    p.mkdir(parents=True, exist_ok=True)
    return p


def ensure_local_data_layout() -> None:
    for fn in (beds_dir, models_3d_dir, simulations_dir, reports_dir, aux_dir):
        fn()
    scratch = local_data_root() / "scratch"
    scratch.mkdir(parents=True, exist_ok=True)
    captures = aux_dir() / "captures"
    captures.mkdir(parents=True, exist_ok=True)
    migrated_beds = beds_dir() / "migrated-from-root"
    migrated_beds.mkdir(parents=True, exist_ok=True)
    migrated_models = models_3d_dir() / "migrated-from-root"
    migrated_models.mkdir(parents=True, exist_ok=True)
    organize_project_root_once()


def organize_project_root_once() -> None:
    """
    move artefactos soltos da raiz do repo para pastas em local_data (uma vez).
    nao altera bed_wizard.py, README.md nem ficheiros de configuracao do projeto.
    """
    marker = local_data_root() / ".root_organized_v1"
    if marker.is_file():
        return
    root = project_root()
    moves: List[tuple[Path, Path]] = []

    def _plan(src_name: str, dest: Path) -> None:
        src = root / src_name
        if src.is_file():
            dest.parent.mkdir(parents=True, exist_ok=True)
            target = dest / src.name
            if not target.exists():
                moves.append((src, target))

    for bed in sorted(root.glob("*.bed")):
        _plan(bed.name, beds_dir() / "migrated-from-root")
        json_side = Path(f"{bed}.json")
        if json_side.is_file():
            _plan(json_side.name, beds_dir() / "migrated-from-root")
        alt_json = bed.with_name(f"{bed.name}.json")
        if alt_json.is_file() and alt_json != json_side:
            _plan(alt_json.name, beds_dir() / "migrated-from-root")

    for pattern in (
        "_quick_work_*",
        "_tmp_*",
        "_test_*",
        "leito*.json",
        "*_pure_bed.json",
        "*_pure_pure_bed.json",
        "leito1Blender.json",
    ):
        for fp in root.glob(pattern):
            if fp.is_file():
                _plan(fp.name, local_data_root() / "scratch")

    for stl in root.glob("*.stl"):
        _plan(stl.name, models_3d_dir() / "migrated-from-root")

    for cap in list(root.glob("Depth*.json")) + list(root.glob("Depth*.png")) + list(
        root.glob("RenderOption*.json")
    ):
        if cap.is_file():
            _plan(cap.name, aux_dir() / "captures")

    db_root = root / "cfd_pipeline.db"
    db_local = local_data_root() / "cfd_pipeline.db"
    if db_root.is_file() and not db_local.is_file():
        db_local.parent.mkdir(parents=True, exist_ok=True)
        moves.append((db_root, db_local))

    for src, dest in moves:
        try:
            src.rename(dest)
        except OSError:
            try:
                import shutil

                shutil.move(str(src), str(dest))
            except OSError:
                continue

    try:
        from bedflow_bed_registry import register_bed_file

        for dest in {d for _s, d in moves}:
            if dest.suffix.lower() == ".bed":
                try:
                    rel = str(dest.relative_to(root.resolve())).replace("\\", "/")
                except ValueError:
                    rel = dest.name
                register_bed_file(
                    rel,
                    source="terminal",
                    creation_mode="migrated",
                    filename=dest.name,
                    extra={"migrated_from_root": True},
                )
    except ImportError:
        pass

    marker.write_text(_now_iso_marker(), encoding="utf-8")


def _now_iso_marker() -> str:
    return datetime.now(timezone.utc).isoformat()


def resolve_repo_relative(rel: str) -> Path:
    r = (rel or "").replace("\\", "/").lstrip("/")
    return project_root() / r


def resolve_existing_artifact(rel: str) -> Optional[Path]:
    """
    devolve path absoluto se existir no disco; tenta localizacoes legadas
    (generated/configs, generated/3d/output, generated/cfd, output/).
    """
    r = (rel or "").replace("\\", "/").lstrip("/")
    if not r:
        return None
    direct = project_root() / r
    if direct.is_file() or direct.is_dir():
        return direct.resolve()

    name = Path(r).name

    if r.startswith("generated/configs/"):
        cand = beds_dir() / name
        if cand.exists():
            return cand.resolve()

    if r.startswith("generated/3d/output/"):
        cand = models_3d_dir() / name
        if cand.exists():
            return cand.resolve()

    if r.startswith("generated/cfd/"):
        tail = r[len("generated/cfd/") :].strip("/")
        if tail:
            cand = simulations_dir() / Path(tail)
            if cand.exists():
                return cand.resolve()
            leg = legacy_generated_root() / "cfd" / tail
            if leg.exists():
                return leg.resolve()

    if r.startswith("output/"):
        cand = beds_dir() / name
        if cand.exists():
            return cand.resolve()

    return None


def iter_search_roots_for_beds() -> List[Path]:
    roots: List[Path] = [beds_dir(), legacy_generated_root() / "configs", legacy_output_root()]
    return [p for p in roots if p.exists()]


def _bed_search_bases() -> List[Tuple[str, Path]]:
    """pastas onde terminal e web costumam gravar ficheiros .bed (sem cwd do servidor)."""
    bases: List[Tuple[str, Path]] = []
    for base in iter_search_roots_for_beds():
        try:
            rel = str(base.resolve().relative_to(project_root().resolve())).replace("\\", "/")
        except ValueError:
            rel = base.name
        bases.append((rel, base))
    dsl = project_root() / "dsl"
    if dsl.is_dir():
        bases.append(("dsl", dsl))
    bases.append(("repo_root", project_root()))
    return bases


def resolve_validated_bed_path(rel: str) -> Optional[Path]:
    """resolve caminho relativo ao repo se for um .bed conhecido nas pastas de pesquisa."""
    r = (rel or "").replace("\\", "/").lstrip("/")
    if not r or ".." in r or not r.lower().endswith(".bed"):
        return None
    direct = (project_root() / r).resolve()
    root_res = project_root().resolve()
    try:
        direct.relative_to(root_res)
    except ValueError:
        return None
    if direct.is_file():
        return direct
    return None


def _detect_bed_origin(preview: str) -> str:
    low = (preview or "")[:800].lower()
    if "wizard web" in low:
        return "web"
    if "wizard" in low or "gerado pelo" in low or "gerado automaticamente" in low:
        return "wizard"
    return "terminal"


def scan_bed_files(*, max_files: int = 2000) -> List[Dict[str, Any]]:
    """
    lista ficheiros .bed em local_data/beds, generated/configs, output, dsl e raiz do repo.
    alinhado a _discover_bed_files do bed_wizard (terminal).
    """
    root_res = project_root().resolve()
    seen: Dict[str, Path] = {}
    for _label, base in _bed_search_bases():
        if not base.is_dir():
            continue
        try:
            if base.resolve() == root_res:
                candidates = list(base.glob("*.bed"))
            else:
                candidates = list(base.glob("*.bed"))
        except OSError:
            continue
        for fp in candidates:
            if not fp.is_file():
                continue
            try:
                seen[str(fp.resolve())] = fp.resolve()
            except OSError:
                continue

    items: List[Dict[str, Any]] = []
    for fp in seen.values():
        try:
            rel = str(fp.relative_to(root_res)).replace("\\", "/")
        except ValueError:
            continue
        st = fp.stat()
        json_path = Path(f"{fp}.json")
        if not json_path.is_file():
            alt_json = fp.with_suffix(".bed.json")
            json_path = alt_json if alt_json.is_file() else json_path
        preview = ""
        try:
            preview = fp.read_text(encoding="utf-8", errors="replace")[:1200]
        except OSError:
            pass
        json_rel = None
        if json_path.is_file():
            try:
                json_rel = str(json_path.relative_to(root_res)).replace("\\", "/")
            except ValueError:
                json_rel = json_path.name
        row = {
            "relative_path": rel,
            "filename": fp.name,
            "size_bytes": st.st_size,
            "mtime": st.st_mtime,
            "mtime_iso": datetime.fromtimestamp(
                st.st_mtime, tz=timezone.utc
            ).isoformat(),
            "has_json": json_path.is_file(),
            "json_relative_path": json_rel,
            "origin": _detect_bed_origin(preview),
        }
        try:
            from bedflow_bed_registry import enrich_scan_item

            enrich_scan_item(row, preview=preview)
        except ImportError:
            row["source"] = row["origin"]
            row["creation_mode"] = None
            row["created_at"] = row["mtime_iso"]
            row["storage_folder"] = str(Path(rel).parent).replace("\\", "/") or "."
        items.append(row)
    items.sort(key=lambda x: (-float(x["mtime"]), x["filename"].lower()))
    return items[:max_files]


def iter_search_roots_for_models_3d() -> List[Path]:
    roots: List[Path] = [models_3d_dir(), legacy_generated_root() / "3d" / "output"]
    return [p for p in roots if p.exists()]


def iter_search_roots_for_simulations() -> List[Path]:
    roots: List[Path] = [simulations_dir(), legacy_generated_root() / "cfd"]
    return [p for p in roots if p.exists()]


def resolve_simulation_case_dir(case_name: str) -> Optional[Path]:
    for base in iter_search_roots_for_simulations():
        d = (base / case_name).resolve()
        if d.is_dir():
            return d
    return None


def find_wizard_json_and_blend(file_base: str) -> Tuple[Optional[Path], Optional[Path]]:
    """
    localiza json compilado e .blend pelo nome base do wizard (sem .bed).
    procura local_data primeiro depois pastas legadas generated/*.
    """
    stem = (file_base or "").replace(".bed", "").strip()
    json_name = f"{stem}.bed.json"
    blend_name = f"{stem}.blend"
    bed_json: Optional[Path] = None
    for base in (beds_dir(), legacy_generated_root() / "configs"):
        p = base / json_name
        if p.is_file():
            bed_json = p
            break
    blend_file: Optional[Path] = None
    for base in (models_3d_dir(), legacy_generated_root() / "3d" / "output"):
        p = base / blend_name
        if p.is_file():
            blend_file = p
            break
    return bed_json, blend_file


def mesh_id_for_relative_path(rel: str) -> str:
    r = (rel or "").replace("\\", "/").lstrip("/")
    return hashlib.sha256(r.encode("utf-8")).hexdigest()[:16]


def iter_mesh_scan_roots() -> List[Path]:
    roots: List[Path] = []
    for base in iter_search_roots_for_models_3d():
        roots.append(base)
    ax = aux_dir()
    if ax.exists():
        roots.append(ax)
    leg = legacy_generated_root()
    for sub in ("batch",):
        p = leg / sub
        if p.exists():
            roots.append(p)
    for base in iter_search_roots_for_simulations():
        if base.exists():
            roots.append(base)
    # dedupe preservando ordem
    seen: set[str] = set()
    out: List[Path] = []
    for r in roots:
        k = str(r.resolve())
        if k not in seen:
            seen.add(k)
            out.append(r)
    return out


def scan_project_mesh_files(*, max_files: int = 2000) -> List[Dict[str, Any]]:
    """
    lista ficheiros de malha conhecidos sob raizes de modelo/simulacao.
    ordenado por mtime decrescente; limita quantidade para evitar travar em arvores enormes.
    """
    root = project_root()
    root_res = root.resolve()
    items: List[Dict[str, Any]] = []
    exts = {e.lower() for e in VIEWER_MESH_EXTENSIONS} | {e.lower() for e in VIEWER_SCENE_EXTENSIONS}

    def _append_if_mesh(fp: Path) -> None:
        if not fp.is_file():
            return
        if fp.suffix.lower() not in exts:
            return
        try:
            rel = str(fp.resolve().relative_to(root_res)).replace("\\", "/")
        except ValueError:
            return
        if not is_viewer_mesh_relative_path(rel):
            return
        st = fp.stat()
        row = {
            "relative_path": rel,
            "filename": fp.name,
            "mesh_id": mesh_id_for_relative_path(rel),
            "size_bytes": st.st_size,
            "mtime": st.st_mtime,
            "format": fp.suffix.lower().lstrip("."),
        }
        try:
            from bedflow_viewer_hints import augment_mesh_scan_row

            row = augment_mesh_scan_row(row)
        except ImportError:
            row["source_hint"] = ""
            row["recommended_modes"] = ""
        items.append(row)

    for base in iter_mesh_scan_roots():
        try:
            for fp in base.rglob("*"):
                _append_if_mesh(fp)
        except OSError:
            continue
    # raiz do repo: apenas ficheiros directos (evita varrer node_modules, .git, etc.)
    try:
        for ext in sorted(exts):
            for fp in root.glob(f"*{ext}"):
                _append_if_mesh(fp)
    except OSError:
        pass
    models_prefix = "local_data/models_3d/"

    def _scan_sort_key(item: Dict[str, Any]) -> Tuple[int, float]:
        rel = str(item.get("relative_path") or "").replace("\\", "/")
        # saida do blender / wizard: esta pasta primeiro, depois por data
        pri = 0 if rel.startswith(models_prefix) else 1
        return (pri, -float(item["mtime"]))

    items.sort(key=_scan_sort_key)
    return items[:max_files]


def is_viewer_mesh_relative_path(rel: str) -> bool:
    r = (rel or "").replace("\\", "/").lstrip("/")
    if ".." in r or r.startswith("/"):
        return False
    if any(r.startswith(pref) for pref in VIEWER_MESH_PATH_PREFIXES):
        return True
    # malha ou cena blender directamente na raiz do repo (ex.: leito_hex_pure.stl)
    mesh_exts = tuple(
        e.lower() for e in VIEWER_MESH_EXTENSIONS + VIEWER_SCENE_EXTENSIONS
    )
    if "/" not in r and r.lower().endswith(mesh_exts):
        return True
    return False


def resolve_validated_mesh_path(rel: str) -> Optional[Path]:
    if not is_viewer_mesh_relative_path(rel):
        return None
    p = (project_root() / rel.replace("\\", "/").lstrip("/")).resolve()
    try:
        p.relative_to(project_root().resolve())
    except ValueError:
        return None
    if not p.is_file():
        return None
    return p


# limite de referencia para o dashboard (uso em disco dos artefactos)
ARTIFACTS_STORAGE_CAP_BYTES: int = 60 * 1024 * 1024 * 1024


def directory_size_bytes(path: Path) -> int:
    """soma tamanhos de ficheiros sob path (nao segue symlinks como dirs)."""
    total = 0
    if not path.exists():
        return 0
    try:
        base = path.resolve()
        for root, _dirs, files in os.walk(base, topdown=True, followlinks=False):
            for name in files:
                fp = Path(root) / name
                try:
                    if fp.is_symlink():
                        continue
                    if fp.is_file():
                        total += fp.stat().st_size
                except OSError:
                    continue
    except OSError:
        return 0
    return total


def get_artifacts_storage_report() -> Dict[str, Any]:
    """
    uso em disco das pastas de artefactos do projeto vs teto de 60 gib (dashboard).
    inclui local_data, generated e output na raiz.
    """
    parts: List[Tuple[str, Path]] = [
        ("local_data", local_data_root()),
        ("generated", legacy_generated_root()),
        ("output", legacy_output_root()),
    ]
    breakdown: List[Dict[str, Any]] = []
    used = 0
    for label, p in parts:
        try:
            resolved = p.resolve()
        except OSError:
            resolved = p
        b = directory_size_bytes(resolved)
        used += b
        breakdown.append({"label": label, "path": str(resolved), "size_bytes": b})
    cap = ARTIFACTS_STORAGE_CAP_BYTES
    pct = round((100.0 * used / cap), 2) if cap else 0.0
    pct = min(max(pct, 0.0), 100.0)
    return {
        "bytes_used": used,
        "bytes_cap": cap,
        "cap_gb": round(cap / (1024**3), 2),
        "percent_of_cap": pct,
        "breakdown": breakdown,
    }
