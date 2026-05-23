# regressão: close() não deve bloquear ao chamar update() com o mesmo lock
from __future__ import annotations

import sys
from pathlib import Path

import pytest

_PM = Path(__file__).resolve().parents[1]
if str(_PM) not in sys.path:
    sys.path.insert(0, str(_PM))

from mesh_progress_ui import MeshProgressReporter  # noqa: E402


def test_close_does_not_deadlock_without_gui():
    rep = MeshProgressReporter(use_gui=False)
    rep.update("mesh", pct=55.0)
    rep.close(ok=True)


def test_begin_long_task_suppresses_gui_calls():
    rep = MeshProgressReporter(use_gui=False)
    rep.begin_long_task()
    rep.update("export", pct=88.0)
    rep.end_long_task()
    rep.close(ok=True)
