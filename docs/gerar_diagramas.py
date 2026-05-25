"""
Gerador de diagramas de arquitetura BEDFLOW-ATLAS-TCC-2
Ícones via texto curto + formas — sem dependência de fonte emoji
"""

import matplotlib.pyplot as plt
import matplotlib.patches as mpatches
from matplotlib.patches import FancyBboxPatch
import os

OUT_DIR = os.path.dirname(os.path.abspath(__file__))

# ── Paleta ─────────────────────────────────────────────────────────────────────
BG     = "#111827"
PANEL  = "#1f2937"
BORDER = "#374151"
ARROW  = "#9ca3af"
TITLE  = "#f9fafb"
LABEL  = "#d1d5db"
ICON   = "#f3f4f6"
ACCENT = "#3b82f6"
GREEN  = "#10b981"
YELLOW = "#f59e0b"
PURPLE = "#8b5cf6"
TEAL   = "#14b8a6"
ORANGE = "#f97316"

ICON_COLORS = {
    "file":   "#60a5fa",
    "gear":   "#a78bfa",
    "db":     "#34d399",
    "api":    "#fb923c",
    "arrow":  "#f472b6",
    "check":  "#4ade80",
    "cut":    "#22d3ee",
    "job":    "#facc15",
    "hash":   "#c084fc",
    "out":    "#6ee7b7",
}


def make_fig(n_cols, title, module_color=ACCENT, wide=False):
    col_w = 1.55 if not wide else 1.35
    fig_w = max(10, n_cols * col_w + 2.4)
    fig_h = 4.4
    fig, ax = plt.subplots(figsize=(fig_w, fig_h))
    fig.patch.set_facecolor(BG)
    ax.set_facecolor(BG)
    ax.set_xlim(0, fig_w)
    ax.set_ylim(0, fig_h)
    ax.axis("off")

    # ── header ──────────────────────────────────────────────────────────────
    hdr = FancyBboxPatch((0.15, 3.52), fig_w - 0.3, 0.65,
                          boxstyle="round,pad=0.06", linewidth=0,
                          facecolor=module_color, zorder=2)
    ax.add_patch(hdr)
    ax.text(fig_w / 2, 3.845, title, color="white", fontsize=11,
            fontweight="bold", ha="center", va="center", zorder=3)
    return fig, ax, fig_w


def icon_shape(ax, cx, cy, kind, color=None):
    """Desenha ícone vetorial simples dentro do box."""
    c = color or ICON_COLORS.get(kind, "#9ca3af")
    if kind == "file":
        rect = FancyBboxPatch((cx-.18, cy-.22), .36, .44,
                               boxstyle="square,pad=0", linewidth=1.2,
                               edgecolor=c, facecolor="#1f2937", zorder=6)
        ax.add_patch(rect)
        for dy in [.06, -.02, -.10]:
            ax.plot([cx-.1, cx+.1], [cy+dy, cy+dy], color=c, lw=1, zorder=7)
    elif kind == "gear":
        circle = plt.Circle((cx, cy), .18, color=c, fill=False, lw=1.8, zorder=6)
        ax.add_patch(circle)
        inner = plt.Circle((cx, cy), .07, color=c, fill=True, zorder=6)
        ax.add_patch(inner)
        import numpy as np
        for a in range(0, 360, 45):
            rad = a * 3.14159 / 180
            ax.plot([cx + .18*__import__('math').cos(rad),
                     cx + .26*__import__('math').cos(rad)],
                    [cy + .18*__import__('math').sin(rad),
                     cy + .26*__import__('math').sin(rad)],
                    color=c, lw=2.2, zorder=6)
    elif kind == "db":
        for dy in [.14, .04, -.06]:
            ell = mpatches.Ellipse((cx, cy+dy), .36, .12,
                                    edgecolor=c, facecolor="#1f2937",
                                    linewidth=1.2, zorder=6)
            ax.add_patch(ell)
        ax.plot([cx-.18, cx-.18], [cy-.06, cy+.14], color=c, lw=1.2, zorder=5)
        ax.plot([cx+.18, cx+.18], [cy-.06, cy+.14], color=c, lw=1.2, zorder=5)
    elif kind == "api":
        ax.text(cx, cy, "API", color=c, fontsize=11, fontweight="bold",
                ha="center", va="center", zorder=6)
    elif kind == "check":
        ax.text(cx, cy, "OK", color=c, fontsize=12, fontweight="bold",
                ha="center", va="center", zorder=6)
    elif kind == "cut":
        ax.plot([cx-.2, cx+.2], [cy, cy], color=c, lw=2, zorder=6)
        ax.plot([cx, cx], [cy-.2, cy+.2], color=c, lw=2, zorder=6)
    elif kind == "hash":
        ax.text(cx, cy, "#", color=c, fontsize=17, fontweight="bold",
                ha="center", va="center", zorder=6)
    elif kind == "out":
        rect = FancyBboxPatch((cx-.18, cy-.14), .36, .28,
                               boxstyle="round,pad=0.04", linewidth=1.4,
                               edgecolor=c, facecolor="#1f2937", zorder=6)
        ax.add_patch(rect)
        ax.text(cx, cy, "STL", color=c, fontsize=7.5, fontweight="bold",
                ha="center", va="center", zorder=7)
    elif kind == "job":
        rect = FancyBboxPatch((cx-.17, cy-.17), .34, .34,
                               boxstyle="round,pad=0.03", linewidth=1.3,
                               edgecolor=c, facecolor="#1f2937", zorder=6)
        ax.add_patch(rect)
        ax.text(cx, cy, "JOB", color=c, fontsize=7.5, fontweight="bold",
                ha="center", va="center", zorder=7)
    elif kind == "seed":
        ax.text(cx, cy, "S", color=c, fontsize=16, fontweight="bold",
                ha="center", va="center", family="monospace", zorder=6)
    elif kind == "py":
        ax.text(cx, cy, "PY", color=c, fontsize=13, fontweight="bold",
                ha="center", va="center", zorder=6)
    elif kind == "cli":
        ax.text(cx, cy, ">_", color=c, fontsize=12, fontweight="bold",
                ha="center", va="center", family="monospace", zorder=6)
    elif kind == "react":
        ax.text(cx, cy, "R", color=c, fontsize=16, fontweight="bold",
                ha="center", va="center", zorder=6)
    elif kind == "lock":
        ax.text(cx, cy, "[1]", color=c, fontsize=10, fontweight="bold",
                ha="center", va="center", zorder=6)
    elif kind == "dsl":
        ax.text(cx, cy, "DSL", color=c, fontsize=10, fontweight="bold",
                ha="center", va="center", zorder=6)
    else:
        ax.text(cx, cy, "?", color=c, fontsize=12, ha="center",
                va="center", zorder=6)


def box(ax, cx, cy, kind, label, color=PANEL, border=BORDER, icon_color=None):
    w, h = 1.28, 1.15
    rect = FancyBboxPatch((cx - w/2, cy - h/2), w, h,
                           boxstyle="round,pad=0.07", linewidth=1,
                           edgecolor=border, facecolor=color, zorder=4)
    ax.add_patch(rect)
    icon_y = cy + 0.2
    icon_shape(ax, cx, icon_y, kind, icon_color)
    lines = label.split("\n")
    ax.text(cx, cy - 0.2, "\n".join(lines), color=LABEL,
            fontsize=7.3, ha="center", va="top",
            multialignment="center", zorder=5, linespacing=1.3)


def arrow(ax, x0, x1, y=2.2):
    ax.annotate("", xy=(x1, y), xytext=(x0, y),
                arrowprops=dict(arrowstyle="-|>", color=ARROW,
                                lw=1.6, mutation_scale=13), zorder=3)


def note(ax, fw, text, color=YELLOW):
    ax.text(fw/2, 0.55, text, color=color, fontsize=6.8,
            ha="center", va="center",
            bbox=dict(boxstyle="round,pad=0.32", facecolor="#1c1917",
                      edgecolor=color, lw=0.9))


def save(fig, name):
    path = os.path.join(OUT_DIR, name)
    fig.savefig(path, dpi=150, bbox_inches="tight",
                facecolor=BG, edgecolor="none")
    plt.close(fig)
    print(f"  salvo: {name}")


# ════════════════════════════════════════════════════════════════════
# Fig 08 — DSL Compilador  [ATUALIZADO]
# ════════════════════════════════════════════════════════════════════
def fig_dsl():
    fig, ax, fw = make_fig(5, "Modulo DSL  (Compilador)", ACCENT)
    y, xs = 2.2, [1.1, 2.6, 4.1, 5.6, 7.1]
    box(ax, xs[0], y, "file",  "Entrada\n.bed")
    box(ax, xs[1], y, "check", "Validacao\nsintaxe &\nsemantica", color="#1e3a5f")
    box(ax, xs[2], y, "dsl",   "Normalizacao\nunidades SI\n(ANTLR 4)", color="#1e3a5f", icon_color="#60a5fa")
    box(ax, xs[3], y, "hash",  "Hash SHA-256\n8 chars\n(_metadata)", color="#1e3a5f", icon_color="#c084fc")
    box(ax, xs[4], y, "out",   ".bed.json\n(hash embutido\nem _metadata)", color="#14432a", icon_color="#6ee7b7")
    for i in range(4): arrow(ax, xs[i]+0.64, xs[i+1]-0.64, y)
    note(ax, fw,
         "Diferenca do doc: saida e um unico .bed.json com hash em _metadata.hash "
         "-- nao sao arquivos separados params.json e params.hash")
    save(fig, "fig08_dsl_compilador.png")


# ════════════════════════════════════════════════════════════════════
# Fig 09a — Modelagem Blender  [ATUALIZADO]
# ════════════════════════════════════════════════════════════════════
def fig_blender():
    fig, ax, fw = make_fig(6, "Modulo de Modelagem Geometrica  (Blender 4.x)", "#b45309")
    y, xs = 2.2, [0.9, 2.25, 3.6, 4.95, 6.3, 7.65]
    box(ax, xs[0], y, "file",  ".bed.json\n+ hash")
    box(ax, xs[1], y, "gear",  "Cilindro\n+ tampas\n(Python API)", color="#2d1b00", icon_color="#a78bfa")
    box(ax, xs[2], y, "gear",  "Empacot.\nparticulas\n(seed fixa)", color="#2d1b00", icon_color="#a78bfa")
    box(ax, xs[3], y, "check", "Manifold\n& watertight\ncheck", color="#2d1b00", icon_color="#4ade80")
    box(ax, xs[4], y, "hash",  "Porosidade\nefetiva\n(calculo)", color="#2d1b00", icon_color="#facc15")
    box(ax, xs[5], y, "out",   "leito.stl\n.blend\n.obj / .glb", color="#14432a", icon_color="#6ee7b7")
    for i in range(5): arrow(ax, xs[i]+0.62, xs[i+1]-0.62, y)
    note(ax, fw,
         "Diferenca do doc: exporta tambem .blend, .obj, .glb alem de .stl. "
         "Alternativa Python Puro disponivel (ver Fig 09b)")
    save(fig, "fig09a_modelagem_blender.png")


# ════════════════════════════════════════════════════════════════════
# Fig 09b — Motor Python Puro  [NOVO]
# ════════════════════════════════════════════════════════════════════
def fig_python_engine():
    fig, ax, fw = make_fig(6, "Motor de Modelagem Python Puro  [NOVO]", GREEN)
    y, xs = 2.2, [0.9, 2.25, 3.6, 4.95, 6.3, 7.65]
    box(ax, xs[0], y, "file",  ".bed.json\n+ hash")
    box(ax, xs[1], y, "py",    "Stdlib only\n(math, struct)\nstl_mesh_utils", color="#052e16", icon_color="#4ade80")
    box(ax, xs[2], y, "gear",  "Empacotar\nhex_3d /\nRSA / rigido", color="#052e16", icon_color="#a78bfa")
    box(ax, xs[3], y, "cut",   "Modo geo:\nfull_3d ou\nthin_slice", color="#052e16", icon_color="#22d3ee")
    box(ax, xs[4], y, "hash",  "Metadados:\nseed, hash,\ncentros", color="#052e16", icon_color="#c084fc")
    box(ax, xs[5], y, "out",   "leito.stl\n(binario)\n+sidecar .json", color="#14432a", icon_color="#6ee7b7")
    for i in range(5): arrow(ax, xs[i]+0.62, xs[i+1]-0.62, y)
    note(ax, fw,
         "NOVO: sem Blender. Usa apenas Python stdlib. "
         "Input: params JSON  |  Output: STL binario + _pure_bed.json sidecar (seed, porosidade, centros)",
         color=GREEN)
    save(fig, "fig09b_motor_python_puro.png")


# ════════════════════════════════════════════════════════════════════
# Fig 09c — Thin Slice / Pseudo-2D  [NOVO]
# ════════════════════════════════════════════════════════════════════
def fig_thin_slice():
    fig, ax, fw = make_fig(6, "Modulo de Corte Pseudo-2D  (Thin Slice)  [NOVO]", TEAL)
    y, xs = 2.2, [0.9, 2.25, 3.6, 4.95, 6.3, 7.65]
    box(ax, xs[0], y, "file",  "Leito 3D\n(centros\n+ shell)")
    box(ax, xs[1], y, "gear",  "Config fatia\neixo x/y/z\npos + esp.", color="#042f2e", icon_color="#2dd4bf")
    box(ax, xs[2], y, "cut",   "Filtro\nparticulas\nc/ plano", color="#042f2e", icon_color="#22d3ee")
    box(ax, xs[3], y, "cut",   "Clipagem\nshell\n(slab min/max)", color="#042f2e", icon_color="#22d3ee")
    box(ax, xs[4], y, "hash",  "Relatorio:\nretidas /\ndescartadas", color="#042f2e", icon_color="#facc15")
    box(ax, xs[5], y, "out",   "fatia.stl\n(pseudo-2D)\n+metadados", color="#14432a", icon_color="#6ee7b7")
    for i in range(5): arrow(ax, xs[i]+0.62, xs[i+1]-0.62, y)
    note(ax, fw,
         "NOVO: thin_slice_build.py + thin_slice_particles.py. "
         "Modo pseudo_2d_thin_slice. Tambem existe pseudo_2d_statistical (RSA 2D).",
         color=TEAL)
    save(fig, "fig09c_thin_slice_pseudo2d.png")


# ════════════════════════════════════════════════════════════════════
# Fig 10 — CFD OpenFOAM  [CONFIRMADO REAL]
# ════════════════════════════════════════════════════════════════════
def fig_openfoam():
    fig, ax, fw = make_fig(7, "Modulo de Simulacao CFD  (OpenFOAM)", "#7c3aed", wide=True)
    y, xs = 2.2, [0.85, 2.05, 3.25, 4.45, 5.65, 6.85, 8.1]
    box(ax, xs[0], y, "file",  "Geom STL\n+ porosity\n.json")
    box(ax, xs[1], y, "gear",  "Estrutura\ndiret.\ncaso OF", color="#2e1065", icon_color="#a78bfa")
    box(ax, xs[2], y, "cut",   "blockMesh\n(malha hex\nfundo)", color="#2e1065", icon_color="#818cf8")
    box(ax, xs[3], y, "gear",  "snappyHex\nMesh\n(refinamento)", color="#2e1065", icon_color="#a78bfa")
    box(ax, xs[4], y, "gear",  "Cond. cont.\np / U / k/e\ncontrolDict", color="#2e1065", icon_color="#a78bfa")
    box(ax, xs[5], y, "py",    "simpleFoam\n(solver\nestac.)", color="#2e1065", icon_color="#4ade80")
    box(ax, xs[6], y, "out",   "Metricas\ndP, Re,\ncels, CSV", color="#14432a", icon_color="#6ee7b7")
    for i in range(6): arrow(ax, xs[i]+0.58, xs[i+1]-0.58, y)
    note(ax, fw,
         "Confirmado: setup_openfoam_case.py gera blockMeshDict, snappyHexMeshDict, "
         "controlDict, fvSchemes, fvSolution e 0/ (BC). Requer OpenFOAM instalado no sistema/WSL.",
         color="#a78bfa")
    save(fig, "fig10_cfd_openfoam.png")


# ════════════════════════════════════════════════════════════════════
# Fig 11 — Persistencia  [ATUALIZADO — sem MinIO]
# ════════════════════════════════════════════════════════════════════
def fig_persistencia():
    fig, ax, fw = make_fig(6, "Modulo de Persistencia  (SQLite + Filesystem Local)", "#0f766e")
    y, xs = 2.2, [0.9, 2.25, 3.6, 4.95, 6.3, 7.65]
    box(ax, xs[0], y, "gear",  "Resultados\n(CFD, Blender\nPython)")
    box(ax, xs[1], y, "gear",  "Normalizacao\ndados p/\narmazenam.", color="#022c22", icon_color="#2dd4bf")
    box(ax, xs[2], y, "db",    "SQLite\n(hash, tempo\nporosidade\nstatus)", color="#022c22", icon_color="#34d399")
    box(ax, xs[3], y, "file",  "Filesystem\nlocal\n(STL, .blend\nCSV, logs)", color="#022c22")
    box(ax, xs[4], y, "hash",  "Indexacao\nhash <-> path\n(SHA-256)", color="#022c22", icon_color="#c084fc")
    box(ax, xs[5], y, "api",   "SQLAlchemy\n+ API REST\n(acesso)", color="#14432a", icon_color="#fb923c")
    for i in range(5): arrow(ax, xs[i]+0.62, xs[i+1]-0.62, y)
    note(ax, fw,
         "Diferenca do doc: SEM MinIO e SEM PostgreSQL. "
         "Usa SQLite (local_data/cfd_pipeline.db) + filesystem local. MinIO nao existe no codigo.")
    save(fig, "fig11_persistencia.png")


# ════════════════════════════════════════════════════════════════════
# Fig 12 — API FastAPI  [ATUALIZADO — sem JWT]
# ════════════════════════════════════════════════════════════════════
def fig_api():
    fig, ax, fw = make_fig(6, "API  (FastAPI)", "#0369a1")
    y, xs = 2.2, [0.9, 2.25, 3.6, 4.95, 6.3, 7.65]
    box(ax, xs[0], y, "api",   "Requisicoes\nHTTP REST", icon_color="#fb923c")
    box(ax, xs[1], y, "check", "Validacao\nPydantic\n+ parse", color="#082f49", icon_color="#4ade80")
    box(ax, xs[2], y, "hash",  "X-User-ID\nheader\n(sem JWT)", color="#082f49", icon_color="#facc15")
    box(ax, xs[3], y, "gear",  "Roteamento\nendpoints\nnegocio", color="#082f49", icon_color="#a78bfa")
    box(ax, xs[4], y, "db",    "Persistencia\n(SQLite\nFilesystem)", color="#082f49", icon_color="#34d399")
    box(ax, xs[5], y, "file",  "Resp. JSON\n(OpenAPI\n/docs)", color="#14432a")
    for i in range(5): arrow(ax, xs[i]+0.62, xs[i+1]-0.62, y)
    note(ax, fw,
         "Diferenca do doc: SEM JWT. Auth via header X-User-ID (deps_user.py). "
         "Multi-tenant por user_id na query. Docs em /docs e /redoc.")
    save(fig, "fig12_api_fastapi.png")


# ════════════════════════════════════════════════════════════════════
# Fig 13 — Dashboard React  [ATUALIZADO — Recharts nao Plotly]
# ════════════════════════════════════════════════════════════════════
def fig_dashboard():
    fig, ax, fw = make_fig(6, "Dashboard  (React + Three.js + Recharts)", "#1d4ed8")
    y, xs = 2.2, [0.9, 2.25, 3.6, 4.95, 6.3, 7.65]
    box(ax, xs[0], y, "react", "Interface\nReact 18\n(Vite)", icon_color="#60a5fa")
    box(ax, xs[1], y, "api",   "Consumo\nAPI HTTP\nREST", color="#172554", icon_color="#fb923c")
    box(ax, xs[2], y, "cut",   "Viewer 3D\nSTL/OBJ/GLB\n(Three.js\nR3F+Drei)", color="#172554", icon_color="#22d3ee")
    box(ax, xs[3], y, "hash",  "Graficos\nRecharts\n+ SVG custom\n(nao Plotly)", color="#172554", icon_color="#facc15")
    box(ax, xs[4], y, "file",  "Lista runs\nfiltros hash\nstatus datas", color="#172554")
    box(ax, xs[5], y, "check", "Sem acesso\ndireto arts.\n(so via API)", color="#1c1c1c", icon_color="#4ade80")
    for i in range(5): arrow(ax, xs[i]+0.62, xs[i+1]-0.62, y)
    note(ax, fw,
         "Diferenca do doc: usa Recharts (nao Plotly). "
         "3D via @react-three/fiber + drei. DonutChart e StatusBar em SVG custom.")
    save(fig, "fig13_dashboard_react.png")


# ════════════════════════════════════════════════════════════════════
# Fig 14 — CLI Wizard  [NOVO]
# ════════════════════════════════════════════════════════════════════
def fig_cli_wizard():
    fig, ax, fw = make_fig(6, "CLI Wizard  (Terminal Interativo)  [NOVO]", PURPLE)
    y, xs = 2.2, [0.9, 2.25, 3.6, 4.95, 6.3, 7.65]
    box(ax, xs[0], y, "cli",   "Entrada\n.bed /\ntemplate\n--spec", icon_color="#c084fc")
    box(ax, xs[1], y, "gear",  "Modo\ninterativo\nou headless\n(flags)", color="#2e1065", icon_color="#a78bfa")
    box(ax, xs[2], y, "dsl",   "Geracao\n.bed +\ncompilacao\n-> .json", color="#2e1065", icon_color="#60a5fa")
    box(ax, xs[3], y, "py",    "Motor\nPython Puro\nou Blender\n(selecion.)", color="#2e1065", icon_color="#4ade80")
    box(ax, xs[4], y, "check", "Preview\nterminal\n(Rich)", color="#2e1065", icon_color="#4ade80")
    box(ax, xs[5], y, "out",   ".stl / .blend\n+templates\nDB", color="#14432a", icon_color="#6ee7b7")
    for i in range(5): arrow(ax, xs[i]+0.62, xs[i+1]-0.62, y)
    note(ax, fw,
         "NOVO: wizard_cli.py + dsl/cli/ (Typer). "
         "Comandos: generate, compile, test, pipeline, templates, docs. "
         "Interativo com Rich ou headless via flags.",
         color="#c4b5fd")
    save(fig, "fig14_cli_wizard.png")


# ════════════════════════════════════════════════════════════════════
# Fig 15 — Sistema de Jobs  [NOVO]
# ════════════════════════════════════════════════════════════════════
def fig_jobs():
    fig, ax, fw = make_fig(6, "Sistema de Jobs Assincronos  [NOVO]", ORANGE)
    y, xs = 2.2, [0.9, 2.25, 3.6, 4.95, 6.3, 7.65]
    box(ax, xs[0], y, "api",   "POST API\n(generate /\npipeline /\nCFD)", icon_color="#fb923c")
    box(ax, xs[1], y, "job",   "Criar Job\nUUID\nstatus=\nqueued", color="#431407", icon_color="#facc15")
    box(ax, xs[2], y, "lock",  "Fila unica\n_MESH_LOCK\n(1 job mesh\npor vez)", color="#431407", icon_color="#f87171")
    box(ax, xs[3], y, "py",    "Exec bgtask\nprogresso\n[bedflow N%]\nparsing", color="#431407", icon_color="#4ade80")
    box(ax, xs[4], y, "db",    "JobRecord\nDB: status\nlogs / files\nerros", color="#431407", icon_color="#34d399")
    box(ax, xs[5], y, "api",   "GET /job/\n{id}\n(polling\ncliente)", color="#14432a", icon_color="#fb923c")
    for i in range(5): arrow(ax, xs[i]+0.62, xs[i+1]-0.62, y)
    note(ax, fw,
         "NOVO: mesh_job_runner.py + job_persistence.py. Tabela JobRecord (SQLite). "
         "Tipos: mesh_generation, openfoam_case, cfd_simulation, full_pipeline.",
         color="#fdba74")
    save(fig, "fig15_sistema_jobs.png")


# ════════════════════════════════════════════════════════════════════
# Fig 16 — Rastreabilidade Seed + Hash  [NOVO]
# ════════════════════════════════════════════════════════════════════
def fig_seed_hash():
    fig, ax, fw = make_fig(5, "Sistema de Rastreabilidade  (Seed + Hash)  [NOVO]", "#0f766e")
    y, xs = 2.2, [1.1, 2.6, 4.1, 5.6, 7.1]
    box(ax, xs[0], y, "seed",  "Seed\npacking /\nparticulas\n(fixo ou auto)", icon_color="#2dd4bf")
    box(ax, xs[1], y, "gear",  "Execucao\ndeterminis-\ntica\n(mesmo seed)", color="#022c22", icon_color="#2dd4bf")
    box(ax, xs[2], y, "hash",  "SHA-256\ndo STL\n(content\nhash)", color="#022c22", icon_color="#c084fc")
    box(ax, xs[3], y, "file",  "Sidecar JSON\n_pure_bed.json\nseed, hash\ncentros", color="#022c22")
    box(ax, xs[4], y, "check", "Reproducao\nexata c/\nmesmo seed\n+ hash", color="#14432a", icon_color="#4ade80")
    for i in range(4): arrow(ax, xs[i]+0.64, xs[i+1]-0.64, y)
    note(ax, fw,
         "NOVO: packing_seed.py resolve seeds. bedflow_export_metadata.py calcula SHA-256. "
         "Seed + hash gravados em JobRecord e no sidecar JSON de cada malha.",
         color=TEAL)
    save(fig, "fig16_seed_hash_rastreabilidade.png")


# ════════════════════════════════════════════════════════════════════
# Fig 17 — Templates  [NOVO]
# ════════════════════════════════════════════════════════════════════
def fig_templates():
    fig, ax, fw = make_fig(5, "Sistema de Templates  [NOVO]", "#7e22ce")
    y, xs = 2.2, [1.1, 2.6, 4.1, 5.6, 7.1]
    box(ax, xs[0], y, "file",  "Editor .bed\n(texto livre\nou wizard)")
    box(ax, xs[1], y, "api",   "POST /api\n/templates\n/save\nnome + tag", color="#3b0764", icon_color="#fb923c")
    box(ax, xs[2], y, "db",    "BedTemplate\nSQLite\nid, name,\ncontent", color="#3b0764", icon_color="#34d399")
    box(ax, xs[3], y, "check", "GET list\nbusca, filtro\npaginacao", color="#3b0764", icon_color="#4ade80")
    box(ax, xs[4], y, "cli",   "Reutilizar\n--template\nnome (CLI\nou web)", color="#14432a", icon_color="#c084fc")
    for i in range(4): arrow(ax, xs[i]+0.64, xs[i+1]-0.64, y)
    note(ax, fw,
         "NOVO: routes_templates.py. CRUD completo (save, list, get, update, delete). "
         "Fontes: editor manual ou import de arquivo. Integrado ao CLI e ao wizard web.",
         color="#d8b4fe")
    save(fig, "fig17_sistema_templates.png")


# ════════════════════════════════════════════════════════════════════
if __name__ == "__main__":
    print("Gerando diagramas de arquitetura...")
    fig_dsl()
    fig_blender()
    fig_python_engine()
    fig_thin_slice()
    fig_openfoam()
    fig_persistencia()
    fig_api()
    fig_dashboard()
    fig_cli_wizard()
    fig_jobs()
    fig_seed_hash()
    fig_templates()
    print("Concluido — 12 diagramas gerados em docs/")
