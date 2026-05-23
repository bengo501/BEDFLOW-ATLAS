# fila global e subprocess assíncrono para geração de malha (evita bloquear o event loop)
from __future__ import annotations

import asyncio
import os
import re
from typing import Any, Dict, List, Optional, Tuple

_MESH_LOCK = asyncio.Lock()
_ACTIVE_JOB_ID: Optional[str] = None

_PROGRESS_RE = re.compile(
    r"\[bedflow\s+(\d+(?:\.\d+)?)%\]",
    re.IGNORECASE,
)


def active_mesh_job_id() -> Optional[str]:
    return _ACTIVE_JOB_ID


def mesh_slot_busy() -> bool:
    return _ACTIVE_JOB_ID is not None


async def acquire_mesh_slot(job_id: str) -> bool:
    global _ACTIVE_JOB_ID
    async with _MESH_LOCK:
        if _ACTIVE_JOB_ID is not None and _ACTIVE_JOB_ID != job_id:
            return False
        _ACTIVE_JOB_ID = job_id
        return True


async def release_mesh_slot(job_id: str) -> None:
    global _ACTIVE_JOB_ID
    async with _MESH_LOCK:
        if _ACTIVE_JOB_ID == job_id:
            _ACTIVE_JOB_ID = None


def _parse_progress_line(line: str) -> Optional[float]:
    m = _PROGRESS_RE.search(line)
    if not m:
        return None
    try:
        return float(m.group(1))
    except ValueError:
        return None


def should_open_blender_gui(requested: bool) -> bool:
    """evita abrir gui no servidor salvo permissão explícita."""
    if not requested:
        return False
    return os.environ.get("BEDFLOW_ALLOW_BLENDER_GUI", "").strip().lower() in (
        "1",
        "true",
        "yes",
        "sim",
    )


async def run_command_async(
    cmd: List[str],
    *,
    cwd: str,
    env: Optional[Dict[str, str]] = None,
    timeout_sec: float = 600.0,
    on_progress: Optional[Any] = None,
) -> Tuple[int, str]:
    """
    executa comando sem bloquear o event loop.
    devolve (returncode, stdout+stderr combinado).
    on_progress(pct, line) opcional.
    """
    proc = await asyncio.create_subprocess_exec(
        *cmd,
        cwd=cwd,
        env=env,
        stdout=asyncio.subprocess.PIPE,
        stderr=asyncio.subprocess.STDOUT,
    )
    lines: List[str] = []

    async def _read_stream() -> None:
        assert proc.stdout is not None
        while True:
            raw = await proc.stdout.readline()
            if not raw:
                break
            line = raw.decode("utf-8", errors="replace").rstrip()
            if line:
                lines.append(line)
                if on_progress is not None:
                    pct = _parse_progress_line(line)
                    if pct is not None:
                        on_progress(pct, line)

    try:
        await asyncio.wait_for(
            asyncio.gather(_read_stream(), proc.wait()),
            timeout=timeout_sec,
        )
    except asyncio.TimeoutError:
        try:
            proc.kill()
            await proc.wait()
        except ProcessLookupError:
            pass
        raise

    text = "\n".join(lines)
    return int(proc.returncode or 0), text
