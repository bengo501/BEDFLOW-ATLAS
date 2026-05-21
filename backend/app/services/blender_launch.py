# abrir malhas no blender (gui) — alinhado ao bed_wizard
from __future__ import annotations

import os
import subprocess
import tempfile
from pathlib import Path
from typing import List, Optional, Tuple

BLENDER_IMPORT_LOG_HINT = str(
    Path(os.environ.get("TEMP", os.environ.get("TMP", "."))) / "bedflow_blender_import.log"
)

_MESH_EXTS_IMPORT_SCRIPT = frozenset({".stl", ".obj", ".ply", ".gltf", ".glb"})


def import_script_path(project_root: Path) -> Path:
    return project_root / "scripts" / "blender_scripts" / "open_imported_mesh_gui.py"


def build_blender_launch_command(
    blender_exe: str,
    mesh_path: Path,
    *,
    project_root: Path,
) -> Tuple[List[str], str]:
    """
    devolve (cmd, mode) onde mode é 'blend' ou 'import_script'.
    levanta FileNotFoundError se malha inexistente ou script em falta.
    """
    p = mesh_path.expanduser().resolve()
    if not p.is_file():
        raise FileNotFoundError(f"ficheiro nao encontrado: {p}")

    ext = p.suffix.lower()
    if ext == ".blend":
        return [str(blender_exe), str(p)], "blend"

    if ext in _MESH_EXTS_IMPORT_SCRIPT:
        script = import_script_path(project_root)
        if not script.is_file():
            raise FileNotFoundError(f"script de importacao em falta: {script}")
        return (
            [
                str(blender_exe),
                "--python",
                str(script),
                "--",
                str(p),
            ],
            "import_script",
        )

    return [str(blender_exe), str(p)], "legacy"


def popen_blender_mesh(
    blender_exe: str,
    mesh_path: Path,
    *,
    project_root: Path,
    log_file: Optional[Path] = None,
) -> subprocess.Popen:
    """lança blender em segundo plano; opcionalmente regista stdout/stderr."""
    cmd, _mode = build_blender_launch_command(
        blender_exe, mesh_path, project_root=project_root
    )
    kwargs = {
        "cwd": str(project_root),
        "stdin": subprocess.DEVNULL,
    }
    if log_file is not None:
        log_file.parent.mkdir(parents=True, exist_ok=True)
        log_handle = open(log_file, "ab")
        kwargs["stdout"] = log_handle
        kwargs["stderr"] = subprocess.STDOUT
    else:
        kwargs["stdout"] = subprocess.DEVNULL
        kwargs["stderr"] = subprocess.DEVNULL
    return subprocess.Popen(cmd, **kwargs)


def default_subprocess_log(project_root: Path) -> Path:
    scratch = project_root / "local_data" / "scratch"
    scratch.mkdir(parents=True, exist_ok=True)
    return scratch / "bedflow_blender_subprocess.log"


def pick_mesh_to_open_in_gui(
    *,
    blend_path: Optional[Path] = None,
    stl_path: Optional[Path] = None,
) -> Optional[Path]:
    """preferir stl/obj para visualização rápida; senão blend."""
    for candidate in (stl_path, blend_path):
        if candidate is not None and candidate.is_file():
            return candidate.resolve()
    return None
