"""
encerramento gracioso com ctrl+c: mensagem de despedida em vez de traceback.
"""
from __future__ import annotations

import signal
import sys
from typing import Callable, Optional

_ORIGINAL_EXCEPTHOOK = sys.excepthook
_SHUTDOWN_LANG = "pt"
_LANG_GETTER: Optional[Callable[[], str]] = None
_INTERRUPT_HANDLED = False


def _normalize_lang(code: Optional[str]) -> str:
    c = (code or "pt").strip().lower()
    return "en" if c.startswith("en") else "pt"


def farewell_message(lang: Optional[str] = None) -> str:
    lg = _normalize_lang(lang if lang is not None else _current_lang())
    if lg == "en":
        return "shutting down safely. goodbye!"
    return "encerrado com seguranca. ate logo!"


def _current_lang() -> str:
    if _LANG_GETTER is not None:
        try:
            return _normalize_lang(_LANG_GETTER())
        except Exception:
            pass
    return _normalize_lang(_SHUTDOWN_LANG)


def set_shutdown_lang(lang: str) -> None:
    global _SHUTDOWN_LANG
    _SHUTDOWN_LANG = _normalize_lang(lang)


def set_shutdown_lang_getter(getter: Callable[[], str]) -> None:
    global _LANG_GETTER
    _LANG_GETTER = getter


def emit_farewell(lang: Optional[str] = None) -> None:
    msg = farewell_message(lang)
    try:
        sys.stdout.write(f"\n\n{msg}\n")
        sys.stdout.flush()
    except Exception:
        print(f"\n\n{msg}")


def exit_on_user_interrupt(lang: Optional[str] = None, code: int = 0) -> None:
    global _INTERRUPT_HANDLED
    if _INTERRUPT_HANDLED:
        raise SystemExit(1 if code == 0 else code)
    _INTERRUPT_HANDLED = True
    emit_farewell(lang)
    raise SystemExit(code)


def _on_keyboard_interrupt() -> None:
    exit_on_user_interrupt()


def _excepthook(exc_type, exc, tb):
    if exc_type is KeyboardInterrupt:
        sys.tracebacklimit = 0
        _on_keyboard_interrupt()
    _ORIGINAL_EXCEPTHOOK(exc_type, exc, tb)


def ensure_installed() -> None:
    """reaplica hook se outra biblioteca (ex.: prompt_toolkit) o substituiu."""
    if sys.excepthook is not _excepthook:
        sys.excepthook = _excepthook


def _on_sigint(signum, frame) -> None:  # noqa: ARG001
    _on_keyboard_interrupt()


def install_graceful_shutdown(lang: str = "pt") -> None:
    """regista handler de ctrl+c e excepthook para keyboardinterrupt."""
    set_shutdown_lang(lang)
    sys.excepthook = _excepthook
    signal.signal(signal.SIGINT, _on_sigint)
