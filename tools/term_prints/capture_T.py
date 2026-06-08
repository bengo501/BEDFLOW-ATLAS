#!/usr/bin/env python3
"""
captura prints do FLUXO VIA TERMINAL (T1-T8) do BEDFLOW-ATLAS.

executa os comandos reais do wizard (python bed_wizard.py ...) de forma headless,
captura a saida e renderiza cada uma como imagem estilo terminal (PNG).

T1  menu principal (rich) numerado
T2  wizard interativo - perguntas e respostas
T3  arquivo .bed completo exibido
T4  compilacao OK - params.json + hash
T5  compilacao com erro - linha e tipo
T6  geracao 3d - progresso por etapa
T7  arvore de artefatos gerados
T8  corte 3d (thin slice) via terminal

uso:  python tools/term_prints/capture_T.py [T1 T4 ...]
saida: generated/prints_terminal/Txx_*.png
"""
from __future__ import annotations

import os
import re
import sys
import shutil
import subprocess
from pathlib import Path

from playwright.sync_api import sync_playwright

ROOT = Path(__file__).resolve().parents[2]
OUT = ROOT / "generated" / "prints_terminal"
OUT.mkdir(parents=True, exist_ok=True)
PY = sys.executable
ANSI = re.compile(r"\x1b\[[0-9;?]*[A-Za-z]")

_BROWSER = {"p": None, "browser": None, "ctx": None}


def _env():
    e = dict(os.environ)
    e["PYTHONIOENCODING"] = "utf-8"
    e["PYTHONUTF8"] = "1"
    return e


def run_cmd(args, cwd=None, stdin_text=None, timeout=180, merge=True):
    """roda um comando e devolve (texto saida, comando_str)."""
    proc = subprocess.run(
        [PY] + args,
        cwd=str(cwd or ROOT),
        input=stdin_text,
        capture_output=True,
        text=True,
        encoding="utf-8",
        errors="replace",
        env=_env(),
        timeout=timeout,
    )
    out = proc.stdout or ""
    if merge and proc.stderr:
        out += proc.stderr
    out = ANSI.sub("", out)
    cmd_str = "python " + " ".join(args)
    return out, cmd_str


def _browser_ctx():
    if _BROWSER["ctx"] is None:
        p = sync_playwright().start()
        b = p.chromium.launch()
        ctx = b.new_context(viewport={"width": 1100, "height": 800}, device_scale_factor=2)
        _BROWSER.update(p=p, browser=b, ctx=ctx)
    return _BROWSER["ctx"]


def _close_browser():
    if _BROWSER["browser"]:
        _BROWSER["browser"].close()
    if _BROWSER["p"]:
        _BROWSER["p"].stop()


def _esc(s):
    return s.replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;")


def render_terminal(name, cmd_str, body, caption="", max_lines=None):
    """renderiza saida de terminal como PNG (fundo escuro, monospace)."""
    lines = body.rstrip("\n").split("\n")
    if max_lines and len(lines) > max_lines:
        lines = lines[:max_lines] + ["…"]
    body_html = "\n".join(_esc(l) if l else "&nbsp;" for l in lines)
    cap = f"<div class='cap'>{_esc(caption)}</div>" if caption else ""
    html = f"""<!doctype html><meta charset=utf-8>
<body style='margin:0;background:#0b0e14;display:inline-block;'>
<div id='card' style='display:inline-block;min-width:900px;max-width:1180px;
 font-family:Consolas,"Cascadia Code","JetBrains Mono",monospace;'>
  <div style='background:#161b22;border-radius:10px 10px 0 0;padding:9px 14px;
   border:1px solid #2a2f3a;border-bottom:none;display:flex;align-items:center;gap:8px;'>
    <span style='height:12px;width:12px;border-radius:50%;background:#ff5f56;display:inline-block;'></span>
    <span style='height:12px;width:12px;border-radius:50%;background:#ffbd2e;display:inline-block;'></span>
    <span style='height:12px;width:12px;border-radius:50%;background:#27c93f;display:inline-block;'></span>
    <span style='color:#8b949e;font-size:12.5px;margin-left:8px;'>bedflow-atlas — terminal</span>
  </div>
  <div style='background:#0d1117;border:1px solid #2a2f3a;border-radius:0 0 10px 10px;
   padding:16px 18px;font-size:14.5px;line-height:1.5;color:#d6deeb;white-space:pre;'>
<span style='color:#7ee787;'>$ {_esc(cmd_str)}</span>
{body_html}
  </div>
  {cap}
</div>
<style>.cap{{color:#8b949e;font-size:12.5px;margin-top:8px;padding:0 4px;
 font-family:Segoe UI,Arial,sans-serif;}}</style>
</body>"""
    ctx = _browser_ctx()
    page = ctx.new_page()
    page.set_content(html)
    page.wait_for_timeout(350)
    page.locator("#card").screenshot(path=str(OUT / f"{name}.png"))
    page.close()
    print(f"  salvo: {name}.png")


# --------------------------------------------------------------------------- #
def t1_menu():
    out, _ = run_cmd(["bed_wizard.py", "interactive"], stdin_text="0\n", merge=False)
    # cortar tudo antes do titulo e remover a linha de prompt final
    idx = out.find("bedflow atlas")
    body = out[idx:] if idx >= 0 else out
    body = re.sub(r"\nopcao .*$", "", body.rstrip())
    render_terminal("T1_menu_principal", "python bed_wizard.py interactive", body,
                    "menu principal Rich com opcoes numeradas (criar, web, ajuda, docs, idioma)")


def t2_interactive():
    drv = str((ROOT / "tools" / "term_prints" / "_t2_driver.py").resolve())
    out, _ = run_cmd([drv], timeout=90)
    # recortar: do primeiro "carregar um .bed" ate antes do menu "interior do leito"
    start = out.find("opcional: pre-preencher")
    if start < 0:
        start = out.find("carregar um .bed")
    end = out.find("interior do leito:")
    body = out[start:end] if (start >= 0 and end > start) else out
    body = body.strip("\n")
    render_terminal("T2_wizard_interativo", "python bed_wizard.py interactive  →  comecar › criar › criar basico",
                    body,
                    "modo interativo: cada pergunta da DSL com a resposta do utilizador e progressao de campo")


def t3_bed_file():
    bed = (ROOT / "cases" / "meu_leito.bed").read_text(encoding="utf-8")
    render_terminal("T3_arquivo_bed", "cat cases/meu_leito.bed", bed,
                    "arquivo .bed completo com todos os blocos da DSL (bed, lids, particles, packing, export)")


def t4_compile_ok():
    out, cmd = run_cmd(["bed_wizard.py", "compile", "cases/meu_leito.bed"])
    render_terminal("T4_compile_ok", cmd, out.strip(),
                    "compilacao bem-sucedida: params.json gerado e hash exibido")


def t5_compile_err():
    out, cmd = run_cmd(["bed_wizard.py", "compile", "cases/leito_erro.bed"])
    render_terminal("T5_compile_erro", cmd, out.strip(), max_lines=22,
                    caption="erro de sintaxe do compilador ANTLR com indicacao de linha")


def t6_generate():
    out, _ = run_cmd(
        ["bed_wizard.py", "--load-json", "cases/meu_leito.bed.json",
         "--pure-python", "--no-prompt", "--output-bed", "cases/_t6.bed"],
        timeout=240,
    )
    cmd = "python bed_wizard.py generate -j cases/meu_leito.bed.json --pure-python"
    # focar no progresso da geracao
    idx = out.find("geracao python puro")
    body = out[idx:] if idx >= 0 else out
    render_terminal("T6_geracao_3d", cmd, body.strip(),
                    "motor python puro: parametros, empacotamento, geometria, exportacao STL")


def _fmt_size(n):
    for u in ("B", "KB", "MB"):
        if n < 1024 or u == "MB":
            return f"{n:.0f} {u}" if u == "B" else f"{n/1024:.1f} {u}" if u == "KB" else f"{n/1048576:.1f} {u}"
        n_kb = n
    return f"{n} B"


def t7_tree():
    run_dir = OUT / "run_demo"
    if run_dir.exists():
        shutil.rmtree(run_dir)
    run_dir.mkdir(parents=True)
    json_abs = str((ROOT / "cases" / "meu_leito.bed.json").resolve())
    bw_abs = str((ROOT / "bed_wizard.py").resolve())
    run_cmd([bw_abs, "--load-json", json_abs, "--pure-python",
             "--no-prompt", "--output-bed", "leito.bed"],
            cwd=run_dir, timeout=240)
    files = sorted([p for p in run_dir.iterdir() if p.is_file()], key=lambda p: p.name)
    desc = {
        ".bed": "DSL do leito",
        ".bed.json": "params compilados (antlr)",
        "_pure.stl": "malha 3d (STL binario)",
        "_pure.obj": "malha 3d (OBJ)",
        "_pure_pure_bed.json": "sidecar de metadados (hash, seed, porosidade)",
        "_pure_packing_report.json": "relatorio de empacotamento",
    }
    def _d(name):
        for suf, txt in desc.items():
            if name.endswith(suf):
                return txt
        return ""
    lines = ["local_data/models_3d/   (artefatos de uma execucao)"]
    for i, p in enumerate(files):
        branch = "└──" if i == len(files) - 1 else "├──"
        pad = max(0, 34 - len(p.name))
        lines.append(f"{branch} {p.name}{' ' * pad}  {_fmt_size(p.stat().st_size):>8}  {_d(p.name)}")
    render_terminal("T7_arvore_artefatos", "tree  local_data/models_3d/", "\n".join(lines),
                    "artefatos de uma execucao: .bed, params.json, STL, OBJ, sidecar e report")


def t8_slice():
    out, _ = run_cmd(
        ["bed_wizard.py", "--load-json", "cases/meu_leito.bed.json",
         "--pure-python", "--no-prompt", "--output-bed", "cases/_t8.bed",
         "--slice", "--slice-axis", "y", "--slice-thickness", "0.002",
         "--slice-position", "0.0", "--slice-keep-only"],
        timeout=240,
    )
    cmd = ("python bed_wizard.py generate -j cases/meu_leito.bed.json --pure-python "
           "--slice --slice-axis y --slice-thickness 0.002")
    idx = out.find("geracao python puro")
    body = out[idx:] if idx >= 0 else out
    render_terminal("T8_corte_3d", cmd, body.strip(),
                    "corte 3d pseudo-2d: eixo y, espessura 0.002 m, STL da fatia gerado")


TASKS = {
    "T1": t1_menu, "T2": t2_interactive, "T3": t3_bed_file, "T4": t4_compile_ok,
    "T5": t5_compile_err, "T6": t6_generate, "T7": t7_tree, "T8": t8_slice,
}


def main():
    want = [a.upper() for a in sys.argv[1:]] or list(TASKS)
    for k in want:
        fn = TASKS.get(k)
        if not fn:
            print(f"  [skip] {k} desconhecido")
            continue
        print(f"capturando {k}...")
        try:
            fn()
        except Exception as exc:
            print(f"  [erro] {k}: {str(exc)[:200]}")
    _close_browser()
    print(f"\nprints em: {OUT}")


if __name__ == "__main__":
    main()
