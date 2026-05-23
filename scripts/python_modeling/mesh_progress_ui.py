# janela de progresso opcional para geração de malha (motor python)
from __future__ import annotations

import os
import sys
import threading
import time
from typing import Optional


def _env_truthy(name: str, default: str = "auto") -> bool:
    raw = os.environ.get(name, default).strip().lower()
    if raw in ("0", "false", "no", "nao", "off"):
        return False
    if raw in ("1", "true", "yes", "sim", "on"):
        return True
    if raw == "auto":
        return bool(sys.stdout.isatty())
    return False


def should_use_progress_window(explicit: Optional[bool] = None) -> bool:
    if explicit is not None:
        return bool(explicit)
    return _env_truthy("BEDFLOW_PROGRESS_UI", "auto")


class MeshProgressReporter:
    """barra de progresso em consola e, se possível, janela tkinter."""

    STAGES = (
        ("load", "carregar parâmetros"),
        ("packing", "empacotamento de partículas"),
        ("mesh", "construir geometria do leito"),
        ("slice", "aplicar fatia pseudo-2d"),
        ("export", "exportar stl e metadados"),
        ("done", "concluído"),
    )

    def __init__(self, *, use_gui: bool = True, title: str = "bedflow — motor python"):
        self._use_gui = use_gui and self._tk_available()
        self._title = title
        self._lock = threading.RLock()
        self._root = None
        self._suppress_gui = False
        self._label = None
        self._detail = None
        self._bar = None
        self._pct_var = None
        self._closed = False
        self._stage_index = 0
        if self._use_gui:
            self._init_gui()

    @staticmethod
    def _tk_available() -> bool:
        try:
            import tkinter  # noqa: F401

            return True
        except Exception:
            return False

    def _init_gui(self) -> None:
        import tkinter as tk
        from tkinter import ttk

        self._root = tk.Tk()
        self._root.title(self._title)
        self._root.geometry("420x140")
        self._root.resizable(False, False)
        frm = ttk.Frame(self._root, padding=12)
        frm.pack(fill=tk.BOTH, expand=True)
        self._label = ttk.Label(frm, text="iniciando…", font=("Segoe UI", 10, "bold"))
        self._label.pack(anchor=tk.W)
        self._detail = ttk.Label(frm, text="", wraplength=380)
        self._detail.pack(anchor=tk.W, pady=(4, 8))
        self._pct_var = tk.DoubleVar(value=0.0)
        self._bar = ttk.Progressbar(frm, maximum=100.0, variable=self._pct_var)
        self._bar.pack(fill=tk.X, pady=(0, 4))
        self._root.update_idletasks()

    def begin_long_task(self) -> None:
        """durante export pesado: não chamar tk update (evita deadlock no windows)."""
        self._suppress_gui = True

    def end_long_task(self) -> None:
        self._suppress_gui = False

    def _emit_console(self, pct: float, stage: str, detail: str) -> None:
        msg = f"[bedflow {pct:5.1f}%] {stage}"
        if detail:
            msg += f" — {detail}"
        print(msg, flush=True)

    def update(
        self,
        stage_key: str,
        *,
        pct: Optional[float] = None,
        detail: str = "",
    ) -> None:
        with self._lock:
            labels = {k: v for k, v in self.STAGES}
            stage_label = labels.get(stage_key, stage_key)
            if pct is None:
                for i, (k, _) in enumerate(self.STAGES):
                    if k == stage_key:
                        pct = 100.0 * i / max(1, len(self.STAGES) - 1)
                        break
                else:
                    pct = float(self._stage_index)
            pct = max(0.0, min(100.0, float(pct)))
            self._stage_index = int(pct)
            self._emit_console(pct, stage_label, detail)
            if (
                self._use_gui
                and not self._suppress_gui
                and self._root is not None
            ):
                import tkinter as tk

                if self._label is not None:
                    self._label.config(text=stage_label)
                if self._detail is not None:
                    self._detail.config(text=detail or "")
                if self._pct_var is not None:
                    self._pct_var.set(pct)
                try:
                    self._root.update_idletasks()
                except tk.TclError:
                    pass
            time.sleep(0.02)

    def pulse(self, detail: str = "") -> None:
        """atualização rápida dentro de uma etapa longa (ex.: empacotamento)."""
        self.update("packing", pct=None, detail=detail)

    def close(self, *, ok: bool = True) -> None:
        root = None
        destroy_ok = False
        with self._lock:
            if self._closed:
                return
            self._closed = True
            self._suppress_gui = False
            root = self._root
            destroy_ok = ok and self._use_gui and root is not None
        if ok:
            self.update("done", pct=100.0, detail="malha gerada com sucesso")
        if destroy_ok and root is not None:
            try:
                root.after(200, root.destroy)
                root.update_idletasks()
            except Exception:
                pass
            self._root = None
        elif root is not None and not destroy_ok:
            try:
                root.destroy()
            except Exception:
                pass
            self._root = None

    def __enter__(self) -> "MeshProgressReporter":
        self.update("load", pct=2.0, detail="a preparar geração")
        return self

    def __exit__(self, exc_type, exc, tb) -> None:
        self.close(ok=exc is None)


def null_progress() -> MeshProgressReporter:
    """reporter que só escreve no console, sem janela."""
    rep = MeshProgressReporter(use_gui=False)
    rep._use_gui = False
    return rep
