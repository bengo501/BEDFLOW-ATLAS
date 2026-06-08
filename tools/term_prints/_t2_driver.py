#!/usr/bin/env python3
"""driver do T2: roda o questionario interativo do wizard ecoando as respostas
(simula o eco do terminal) e imprime a transcricao pergunta->resposta.
para apos a seccao inicial (representativo para a figura)."""
from __future__ import annotations
import os, sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / "dsl"))
os.environ["PYTHONIOENCODING"] = "utf-8"

import bed_wizard  # noqa: E402


class _Stop(Exception):
    pass


# respostas do utilizador (na ordem das perguntas)
ANSWERS = [
    "n",       # carregar um .bed existente? -> nao
    "0.05",    # bed.diameter (m)
    "0.1",     # bed.height (m)
    "0.002",   # bed.wall_thickness (m)
    "0.01",    # bed.clearance (m)
    "steel",   # bed.material
    "0.0",     # bed.roughness (m)
]
MAX_ECHO = len(ANSWERS)


def main():
    w = bed_wizard.BedWizard()
    it = iter(ANSWERS)
    count = {"n": 0}

    def echo(prompt, default=""):
        sys.stdout.write(prompt)
        try:
            a = next(it)
        except StopIteration:
            sys.stdout.write("\n")
            raise _Stop()
        if a == "":
            a = default
        sys.stdout.write(a + "\n")
        sys.stdout.flush()
        count["n"] += 1
        if count["n"] >= MAX_ECHO:
            # deixa terminar esta resposta e para logo a seguir
            pass
        return a

    def ask_line(prompt, default=""):
        return echo(prompt, default)

    def ask_number(prompt, default="", **kw):
        return echo(prompt, default)

    # neutralizar limpeza de ecra para nao apagar a transcricao
    w.ui.ask_line = ask_line
    w.ui.ask_number = ask_number
    try:
        w.clear_screen = lambda *a, **k: None
    except Exception:
        pass
    try:
        w.run_questionnaire_interactive()
    except _Stop:
        pass
    except Exception as e:
        sys.stdout.write(f"\n[fim da amostra: {type(e).__name__}]\n")


if __name__ == "__main__":
    main()
