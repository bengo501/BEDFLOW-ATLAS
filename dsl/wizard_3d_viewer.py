# modo terminal: listar malhas geradas e abrir no browser, open3d ou blender
from __future__ import annotations

import os
import subprocess
import sys
import webbrowser
from pathlib import Path
from typing import TYPE_CHECKING, Any, Dict, List

if TYPE_CHECKING:
    from bed_wizard import BedWizard

_REPO = Path(__file__).resolve().parent.parent
_DSL_DIR = Path(__file__).resolve().parent
# dsl/ antes da raiz: em sys.path[0] existe bed_wizard.py atalho sem _WizardCancelled
for _p in (_REPO, _DSL_DIR):
    if str(_p) not in sys.path:
        sys.path.insert(0, str(_p))

from bedflow_local_paths import resolve_validated_mesh_path, scan_project_mesh_files  # noqa: E402
from bed_wizard import _WizardCancelled  # noqa: E402
from wizard_terminal_ui import global_keys_hint, view3d_mesh_pick_aux_lines  # noqa: E402


def render_view3d_education_panels(ui: Any, wizard: Any) -> None:
    """painel de modos + tabela formato x modo (rich se disponivel)."""
    console = getattr(ui, "console", None)
    try:
        from rich import box as rich_box
        from rich.panel import Panel
        from rich.table import Table
    except ImportError:
        Table = None  # type: ignore

    if Table is None or console is None:
        ui.println(
            "[modos] web (three.js): stl obj ply gltf glb | "
            "desktop (open3d): stl obj ply | "
            "blender: todos; cad importa via open_imported_mesh_gui.py"
        )
        ui.println(
            "[formato x modo] stl/obj/ply: web+desktop+blender | "
            "gltf/glb: web+blender | blend: so blender"
        )
        return

    modes_body = (
        "[bold]web — three.js no frontend[/bold]\n"
        "  objetivo: inspeccao rapida no browser sem instalar blender.\n"
        "  vantagens: orbit controls, lista via api, sem disco extra.\n"
        "  limitacoes: nao abre .blend; depende de api + npm run dev.\n"
        "  formatos: stl, obj, ply, gltf, glb.\n\n"
        "[bold]desktop — open3d (mesh_viewer_desktop.py)[/bold]\n"
        "  objetivo: janela local leve.\n"
        "  vantagens: bom para stl/obj/ply grandes.\n"
        "  limitacoes: requer pip install open3d; sem gltf/glb.\n"
        "  formatos: stl, obj, ply.\n\n"
        "[bold]blender — gui[/bold]\n"
        "  objetivo: edicao, materiais, exportacao avancada.\n"
        "  vantagens: .blend nativo; malhas cad importadas automaticamente.\n"
        "  limitacoes: binario blender; gltf depende do addon gltf no blender.\n"
        "  formatos: todos os listados + cena .blend.\n"
    )
    console.print(
        Panel(
            modes_body,
            title=wizard._t("view3d.education.modes_title", "modos de visualizacao"),
            border_style="rgb(95,25,35)",
        )
    )

    ft = Table(
        title=wizard._t("view3d.education.matrix_title", "formato x modo"),
        box=rich_box.ROUNDED,
        show_header=True,
        header_style="bold rgb(240,212,168)",
        border_style="dim",
    )
    ft.add_column(
        wizard._t("view3d.education.col_format", "formato"),
        style="bold",
        justify="left",
    )
    ft.add_column("web", justify="center")
    ft.add_column("desktop", justify="center")
    ft.add_column("blender", justify="center")
    matrix = [
        ("stl", "sim", "sim", "sim"),
        ("obj", "sim", "sim", "sim"),
        ("ply", "sim", "sim", "sim"),
        ("gltf", "sim", "nao", "sim"),
        ("glb", "sim", "nao", "sim"),
        ("blend", "nao", "nao", "sim"),
    ]
    for row in matrix:
        ft.add_row(*row)
    console.print(ft)


def print_visualization_modes_help(wizard: Any) -> None:
    """menu ajuda opcao 7 — resumo dos modos 3d."""
    render_view3d_education_panels(wizard.ui, wizard)


def _env_frontend_url() -> str:
    return os.environ.get("BEDFLOW_VIEWER_FRONTEND_URL", "http://localhost:5173").rstrip("/")


def _env_api_url() -> str:
    return os.environ.get("BEDFLOW_API_URL", "http://localhost:8000").rstrip("/")


def _try_http_ok(url: str, timeout: float = 1.5) -> bool:
    try:
        from urllib.request import urlopen

        with urlopen(url, timeout=timeout) as r:
            return 200 <= (getattr(r, "status", 200) or 200) < 500
    except Exception:
        return False


def _format_size(n: int) -> str:
    if n < 1024:
        return f"{n} b"
    if n < 1024 * 1024:
        return f"{n / 1024:.1f} kb"
    return f"{n / (1024 * 1024):.1f} mb"


def run_visualization_mode(wizard: BedWizard) -> None:
    ui = wizard.ui
    rows = scan_project_mesh_files(max_files=500)
    if not rows:
        ui.warn(wizard._t("view3d.warn_none", ""))
        ui.pause("enter...")
        return

    try:
        from rich.table import Table
        from rich.panel import Panel
        from rich import box as rich_box
    except ImportError:
        Table = None  # type: ignore

    while True:
        ui.clear()
        wizard.print_header(
            wizard._t("view3d.title", "visualizacao 3d"),
            wizard._t("view3d.subtitle", "malhas geradas pelo projeto"),
        )
        ui.breadcrumbs("setup", wizard._t("view3d.crumb", "visualizacao 3d"))
        ui.println()
        ui.muted(wizard._t("view3d.scan_hint", ""))
        ui.println()
        render_view3d_education_panels(ui, wizard)
        ui.println()
        ui.muted(
            wizard._t(
                "view3d.footer_hint",
                "0 ou c menu principal  ·  l lista  ·  ? ajuda do campo  ·  h ajuda global",
            )
        )
        ui.println()

        q = ui.ask_line(wizard._t("view3d.search", "pesquisar:")).strip()
        qlow = q.lower()
        if qlow in ("c", "cancel", "cancelar", "voltar", "back", "q") or qlow == "0":
            return
        if qlow == "?" or qlow == "h":
            for ln in global_keys_hint(wizard.lang).splitlines():
                ui.muted(ln)
            ui.pause("enter...")
            continue
        filtered: List[Dict[str, Any]] = list(rows)
        qnorm = q.lower()
        # "lista" e sinonimos nao sao filtro — o utilizador espera ver todos os ficheiros
        if q and qnorm not in ("lista", "list", "l", "todos", "all", "*"):
            ql = qnorm
            filtered = [
                r
                for r in rows
                if ql in r["relative_path"].lower() or ql in r["filename"].lower()
            ]

        filtered = filtered[:80]
        _console = getattr(ui, "console", None)
        if Table is not None and _console is not None:
            table = Table(
                box=rich_box.ROUNDED,
                title=wizard._t("view3d.table_title", "modelos"),
                show_lines=True,
            )
            table.add_column("#", style="bold", justify="right")
            table.add_column(wizard._t("view3d.col.file", "ficheiro"))
            table.add_column(wizard._t("view3d.col.format", "formato"), justify="center")
            table.add_column(wizard._t("view3d.col.size", "tamanho"), justify="right")
            table.add_column("mesh_id", overflow="fold", max_width=14)
            table.add_column(wizard._t("view3d.col.origin", "origem"), overflow="fold", max_width=20)
            table.add_column(wizard._t("view3d.col.rec", "recomendado"), overflow="fold", max_width=26)
            for i, r in enumerate(filtered, start=1):
                table.add_row(
                    str(i),
                    r["filename"],
                    r["format"],
                    _format_size(int(r["size_bytes"])),
                    r["mesh_id"],
                    str(r.get("source_hint") or "—"),
                    str(r.get("recommended_modes") or "—"),
                )
            _console.print(table)
        else:
            for i, r in enumerate(filtered, start=1):
                ui.println(
                    f"  {i:2}  [{r['format']}]  {r['filename']}  "
                    f"| {r.get('source_hint', '')} | {r.get('recommended_modes', '')}"
                )

        ui.println()
        for ln in view3d_mesh_pick_aux_lines(len(filtered)):
            if getattr(ui, "_rich", False) and getattr(ui, "console", None):
                from rich.text import Text as _RT

                ui.console.print(_RT(ln, style="setup.muted"))
            else:
                ui.muted(ln)
        ui.println()
        pick = ui.ask_line(wizard._t("view3d.pick", "numero do modelo:")).strip()
        plow = pick.lower()
        if plow == "?" or plow == "h":
            for ln in global_keys_hint(wizard.lang).splitlines():
                ui.muted(ln)
            ui.pause("enter...")
            continue
        if not pick:
            ui.warn(wizard._t("view3d.warn_pick_idx", ""))
            ui.pause("enter...")
            continue
        if pick == "0" or plow in ("c", "q", "cancel", "cancelar", "voltar", "back"):
            continue
        if not pick.isdigit() or int(pick) < 1 or int(pick) > len(filtered):
            ui.warn(wizard._t("view3d.warn_num_invalid", ""))
            ui.pause("enter...")
            continue
        chosen = filtered[int(pick) - 1]
        rel = chosen["relative_path"]
        mid = chosen["mesh_id"]
        abs_path = resolve_validated_mesh_path(rel)
        if abs_path is None:
            ui.err(wizard._t("view3d.err_path_invalid", ""))
            ui.pause("enter...")
            continue

        ui.println()
        if Table is not None and getattr(ui, "console", None) is not None:
            ui.console.print(
                Panel.fit(
                    f"[bold]{chosen['filename']}[/bold]\n"
                    f"path: {rel}\n"
                    f"id: {mid}\n"
                    f"tamanho: {_format_size(int(chosen['size_bytes']))}\n"
                    f"origem (heuristica): {chosen.get('source_hint', '—')}\n"
                    f"recomendado: {chosen.get('recommended_modes', '—')}",
                    title=wizard._t("view3d.preview", "preview"),
                )
            )
        else:
            ui.println(
                f"ficheiro: {chosen['filename']}\npath: {rel}\nid: {mid}\n"
                f"origem: {chosen.get('source_hint', '—')}\n"
                f"recomendado: {chosen.get('recommended_modes', '—')}"
            )

        ui.println()
        lab_web = wizard._t("view3d.opt.web", "navegador (three.js no frontend)")
        lab_desk = wizard._t("view3d.opt.desktop", "visualizador desktop (open3d, stl/obj/ply)")
        lab_blend = wizard._t("view3d.opt.blender", "abrir no blender")
        try:
            dest = wizard.get_choice(
                wizard._t("view3d.choose_dest", "onde visualizar"),
                [lab_web, lab_desk, lab_blend],
                None,
                "",
                with_param_review=False,
            )
        except _WizardCancelled:
            continue

        ext = abs_path.suffix.lower()
        if dest == lab_web:
            if ext == ".blend":
                ui.warn(wizard._t("view3d.warn_blend_web", ""))
                ui.pause("enter...")
                continue
            if ext not in (".stl", ".obj", ".ply", ".gltf", ".glb"):
                ui.warn(wizard._t("view3d.warn_web_fmt", ""))
                ui.pause("enter...")
                continue
            fe = _env_frontend_url()
            api = _env_api_url()
            if not _try_http_ok(f"{api}/api/status"):
                ui.warn(
                    wizard._t("view3d.warn_api", "").format(api=api, fe=fe)
                )
            url = f"{fe}/?meshViewerId={mid}"
            ui.ok(wizard._t("view3d.ok_opening", "").format(url=url))
            webbrowser.open(url)
            ui.pause("enter...")

        elif dest == lab_desk:
            if ext == ".blend":
                ui.warn(wizard._t("view3d.warn_blend_desk", ""))
                ui.pause("enter...")
                continue
            script = _REPO / "scripts" / "python_modeling" / "mesh_viewer_desktop.py"
            if not script.is_file():
                ui.err(wizard._t("view3d.err_script", "").format(path=str(script)))
                ui.pause("enter...")
                continue
            ui.muted(
                wizard._t("view3d.exec_viewer", "").format(
                    script=script.name, path=str(abs_path)
                )
            )
            rc = subprocess.call([sys.executable, str(script), str(abs_path)])
            if rc == 2:
                ui.warn(wizard._t("view3d.warn_open3d", ""))
            elif rc != 0:
                ui.warn(wizard._t("view3d.warn_viewer_rc", "").format(rc=rc))
            ui.pause("enter...")

        elif dest == lab_blend:
            exe = wizard.find_blender_executable()
            if not exe:
                ui.warn(wizard._t("view3d.warn_blender_missing", ""))
                ui.pause("enter...")
                continue
            wizard.open_blender_with_file(exe, abs_path)
            ui.pause("enter...")
