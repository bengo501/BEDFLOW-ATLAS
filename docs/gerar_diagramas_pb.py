"""
Gerador de diagramas de arquitetura BEDFLOW-ATLAS-TCC-2 — versao preto e branco
Fundo branco, escala de cinzas, adequado para impressao em documentos academicos
"""

import matplotlib.pyplot as plt
import matplotlib.patches as mpatches
from matplotlib.patches import FancyBboxPatch
import math
import os

OUT_DIR = os.path.dirname(os.path.abspath(__file__))

# ── Paleta P&B ─────────────────────────────────────────────────────────────────
BG        = "#ffffff"   # fundo branco
HDR_BG    = "#111111"   # header do modulo (preto)
HDR_TEXT  = "#ffffff"   # texto do header
BOX_STD   = "#f0f0f0"   # box padrao (cinza claro)
BOX_PROC  = "#e0e0e0"   # box de processo (cinza medio)
BOX_OUT   = "#ffffff"   # box de saida (branco com borda dupla)
BOX_NEW   = "#d8d8d8"   # box destacado como novo (cinza mais escuro)
BORDER    = "#333333"   # borda padrao
BORDER_HV = "#000000"   # borda forte (saida / primeiro)
ARROW_C   = "#000000"   # setas pretas
LABEL_C   = "#111111"   # texto dos labels
ICON_C    = "#000000"   # icones pretos
NOTE_BG   = "#f8f8f8"   # fundo da nota rodape
NOTE_BD   = "#555555"   # borda da nota


def make_fig(n_cols, title, wide=False):
    col_w = 1.55 if not wide else 1.38
    fig_w = max(10, n_cols * col_w + 2.4)
    fig_h = 4.4
    fig, ax = plt.subplots(figsize=(fig_w, fig_h))
    fig.patch.set_facecolor(BG)
    ax.set_facecolor(BG)
    ax.set_xlim(0, fig_w)
    ax.set_ylim(0, fig_h)
    ax.axis("off")

    # header preto com texto branco
    hdr = FancyBboxPatch((0.15, 3.52), fig_w - 0.3, 0.65,
                          boxstyle="square,pad=0", linewidth=0,
                          facecolor=HDR_BG, zorder=2)
    ax.add_patch(hdr)
    ax.text(fig_w / 2, 3.845, title, color=HDR_TEXT, fontsize=11,
            fontweight="bold", ha="center", va="center", zorder=3)
    return fig, ax, fig_w


def icon_shape(ax, cx, cy, kind):
    """Icone vetorial simples em preto."""
    c = ICON_C
    if kind == "file":
        rect = FancyBboxPatch((cx-.16, cy-.20), .32, .40,
                               boxstyle="square,pad=0", linewidth=1.2,
                               edgecolor=c, facecolor="white", zorder=6)
        ax.add_patch(rect)
        for dy in [.06, -.02, -.10]:
            ax.plot([cx-.09, cx+.09], [cy+dy, cy+dy], color=c, lw=0.9, zorder=7)
    elif kind == "gear":
        circle = plt.Circle((cx, cy), .17, color=c, fill=False, lw=1.8, zorder=6)
        ax.add_patch(circle)
        inner = plt.Circle((cx, cy), .07, color=c, fill=True, zorder=6)
        ax.add_patch(inner)
        for a in range(0, 360, 45):
            rad = a * math.pi / 180
            ax.plot([cx + .17*math.cos(rad), cx + .25*math.cos(rad)],
                    [cy + .17*math.sin(rad), cy + .25*math.sin(rad)],
                    color=c, lw=2.2, zorder=6)
    elif kind == "db":
        for dy in [.13, .04, -.05]:
            ell = mpatches.Ellipse((cx, cy+dy), .34, .11,
                                    edgecolor=c, facecolor="white",
                                    linewidth=1.2, zorder=6)
            ax.add_patch(ell)
        ax.plot([cx-.17, cx-.17], [cy-.05, cy+.13], color=c, lw=1.2, zorder=5)
        ax.plot([cx+.17, cx+.17], [cy-.05, cy+.13], color=c, lw=1.2, zorder=5)
    elif kind == "api":
        ax.text(cx, cy, "API", color=c, fontsize=11, fontweight="bold",
                ha="center", va="center", zorder=6)
    elif kind == "check":
        # checkmark
        ax.plot([cx-.14, cx-.03, cx+.14], [cy-.02, cy-.14, cy+.14],
                color=c, lw=2.2, solid_capstyle="round", zorder=6)
    elif kind == "cut":
        # plus / cross
        ax.plot([cx-.18, cx+.18], [cy, cy], color=c, lw=2, zorder=6)
        ax.plot([cx, cx], [cy-.18, cy+.18], color=c, lw=2, zorder=6)
    elif kind == "hash":
        ax.text(cx, cy, "#", color=c, fontsize=17, fontweight="bold",
                ha="center", va="center", zorder=6)
    elif kind == "out":
        # box duplo para saida
        for off in [0.04, 0]:
            r = FancyBboxPatch((cx-.17+off, cy-.13+off), .34, .26,
                                boxstyle="square,pad=0", linewidth=1.3,
                                edgecolor=c, facecolor="white", zorder=6)
            ax.add_patch(r)
        ax.text(cx+0.02, cy+0.01, "STL", color=c, fontsize=7.5, fontweight="bold",
                ha="center", va="center", zorder=7)
    elif kind == "job":
        rect = FancyBboxPatch((cx-.16, cy-.16), .32, .32,
                               boxstyle="square,pad=0", linewidth=1.3,
                               edgecolor=c, facecolor="white", zorder=6)
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
        ax.text(cx, cy, "?", color=c, fontsize=12, ha="center", va="center", zorder=6)


def box(ax, cx, cy, kind, label, style="std"):
    """
    style: 'std' cinza claro | 'proc' cinza medio | 'out' branco borda dupla
           'new' cinza escuro (destaque novo)
    """
    w, h = 1.28, 1.15
    fills = {"std": BOX_STD, "proc": BOX_PROC, "out": BOX_OUT, "new": BOX_NEW}
    borders = {"std": BORDER, "proc": BORDER, "out": BORDER_HV, "new": BORDER_HV}
    lw = 1.8 if style in ("out", "new") else 1.0

    rect = FancyBboxPatch((cx - w/2, cy - h/2), w, h,
                           boxstyle="round,pad=0.07", linewidth=lw,
                           edgecolor=borders[style], facecolor=fills[style],
                           zorder=4)
    ax.add_patch(rect)
    icon_shape(ax, cx, cy + 0.2, kind)
    ax.text(cx, cy - 0.2, label, color=LABEL_C,
            fontsize=7.3, ha="center", va="top",
            multialignment="center", zorder=5, linespacing=1.3)


def arrow(ax, x0, x1, y=2.2):
    ax.annotate("", xy=(x1, y), xytext=(x0, y),
                arrowprops=dict(arrowstyle="-|>", color=ARROW_C,
                                lw=1.5, mutation_scale=13), zorder=3)


def note(ax, fw, text, dashed=False):
    ls = (0, (4, 3)) if dashed else "solid"
    ax.text(fw/2, 0.55, text, color="#333333", fontsize=6.8,
            ha="center", va="center",
            bbox=dict(boxstyle="round,pad=0.32", facecolor=NOTE_BG,
                      edgecolor=NOTE_BD, lw=0.9, linestyle=ls))


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
    fig, ax, fw = make_fig(5, "Modulo DSL  (Compilador)")
    y, xs = 2.2, [1.1, 2.6, 4.1, 5.6, 7.1]
    box(ax, xs[0], y, "file",  "Entrada\n.bed", style="std")
    box(ax, xs[1], y, "check", "Validacao\nsintaxe &\nsemantica", style="proc")
    box(ax, xs[2], y, "dsl",   "Normalizacao\nunidades SI\n(ANTLR 4)", style="proc")
    box(ax, xs[3], y, "hash",  "Hash SHA-256\n8 chars\n(_metadata)", style="proc")
    box(ax, xs[4], y, "out",   ".bed.json\n(hash embutido\nem _metadata)", style="out")
    for i in range(4): arrow(ax, xs[i]+0.64, xs[i+1]-0.64, y)
    note(ax, fw,
         "Diferenca do doc: saida e um unico .bed.json com hash em _metadata.hash "
         "-- nao sao arquivos separados params.json e params.hash")
    save(fig, "pb_fig08_dsl_compilador.png")


# ════════════════════════════════════════════════════════════════════
# Fig 09a — Modelagem Blender  [ATUALIZADO]
# ════════════════════════════════════════════════════════════════════
def fig_blender():
    fig, ax, fw = make_fig(6, "Modulo de Modelagem Geometrica  (Blender 4.x)")
    y, xs = 2.2, [0.9, 2.25, 3.6, 4.95, 6.3, 7.65]
    box(ax, xs[0], y, "file",  ".bed.json\n+ hash", style="std")
    box(ax, xs[1], y, "gear",  "Cilindro\n+ tampas\n(Python API)", style="proc")
    box(ax, xs[2], y, "gear",  "Empacot.\nparticulas\n(seed fixa)", style="proc")
    box(ax, xs[3], y, "check", "Manifold\n& watertight\ncheck", style="proc")
    box(ax, xs[4], y, "hash",  "Porosidade\nefetiva\n(calculo)", style="proc")
    box(ax, xs[5], y, "out",   "leito.stl\n.blend\n.obj / .glb", style="out")
    for i in range(5): arrow(ax, xs[i]+0.62, xs[i+1]-0.62, y)
    note(ax, fw,
         "Diferenca do doc: exporta tambem .blend, .obj, .glb alem de .stl. "
         "Alternativa Python Puro disponivel (ver Fig 09b)")
    save(fig, "pb_fig09a_modelagem_blender.png")


# ════════════════════════════════════════════════════════════════════
# Fig 09b — Motor Python Puro  [NOVO]
# ════════════════════════════════════════════════════════════════════
def fig_python_engine():
    fig, ax, fw = make_fig(6, "Motor de Modelagem Python Puro  [NOVO]")
    y, xs = 2.2, [0.9, 2.25, 3.6, 4.95, 6.3, 7.65]
    box(ax, xs[0], y, "file",  ".bed.json\n+ hash", style="std")
    box(ax, xs[1], y, "py",    "Stdlib only\n(math, struct)\nstl_mesh_utils", style="new")
    box(ax, xs[2], y, "gear",  "Empacotar\nhex_3d /\nRSA / rigido", style="proc")
    box(ax, xs[3], y, "cut",   "Modo geo:\nfull_3d ou\nthin_slice", style="proc")
    box(ax, xs[4], y, "hash",  "Metadados:\nseed, hash,\ncentros", style="proc")
    box(ax, xs[5], y, "out",   "leito.stl\n(binario)\n+sidecar .json", style="out")
    for i in range(5): arrow(ax, xs[i]+0.62, xs[i+1]-0.62, y)
    note(ax, fw,
         "NOVO: sem Blender. Usa apenas Python stdlib (math, struct). "
         "Output: STL binario + _pure_bed.json sidecar (seed, porosidade, centros)",
         dashed=True)
    save(fig, "pb_fig09b_motor_python_puro.png")


# ════════════════════════════════════════════════════════════════════
# Fig 09c — Thin Slice / Pseudo-2D  [NOVO]
# ════════════════════════════════════════════════════════════════════
def fig_thin_slice():
    fig, ax, fw = make_fig(6, "Modulo de Corte Pseudo-2D  (Thin Slice)  [NOVO]")
    y, xs = 2.2, [0.9, 2.25, 3.6, 4.95, 6.3, 7.65]
    box(ax, xs[0], y, "file",  "Leito 3D\n(centros\n+ shell)", style="std")
    box(ax, xs[1], y, "gear",  "Config fatia\neixo x/y/z\npos + esp.", style="new")
    box(ax, xs[2], y, "cut",   "Filtro\nparticulas\nc/ plano", style="proc")
    box(ax, xs[3], y, "cut",   "Clipagem\nshell\n(slab min/max)", style="proc")
    box(ax, xs[4], y, "hash",  "Relatorio:\nretidas /\ndescartadas", style="proc")
    box(ax, xs[5], y, "out",   "fatia.stl\n(pseudo-2D)\n+metadados", style="out")
    for i in range(5): arrow(ax, xs[i]+0.62, xs[i+1]-0.62, y)
    note(ax, fw,
         "NOVO: thin_slice_build.py + thin_slice_particles.py. "
         "Modo pseudo_2d_thin_slice. Tambem existe pseudo_2d_statistical (RSA 2D).",
         dashed=True)
    save(fig, "pb_fig09c_thin_slice_pseudo2d.png")


# ════════════════════════════════════════════════════════════════════
# Fig 10 — CFD OpenFOAM  [CONFIRMADO REAL]
# ════════════════════════════════════════════════════════════════════
def fig_openfoam():
    fig, ax, fw = make_fig(7, "Modulo de Simulacao CFD  (OpenFOAM)", wide=True)
    y, xs = 2.2, [0.85, 2.05, 3.25, 4.45, 5.65, 6.85, 8.1]
    box(ax, xs[0], y, "file",  "Geom STL\n+ porosity\n.json", style="std")
    box(ax, xs[1], y, "gear",  "Estrutura\ndiret.\ncaso OF", style="proc")
    box(ax, xs[2], y, "cut",   "blockMesh\n(malha hex\nfundo)", style="proc")
    box(ax, xs[3], y, "gear",  "snappyHex\nMesh\n(refinamento)", style="proc")
    box(ax, xs[4], y, "gear",  "Cond. cont.\np / U / k/e\ncontrolDict", style="proc")
    box(ax, xs[5], y, "py",    "simpleFoam\n(solver\nestac.)", style="proc")
    box(ax, xs[6], y, "out",   "Metricas\ndP, Re,\ncels, CSV", style="out")
    for i in range(6): arrow(ax, xs[i]+0.58, xs[i+1]-0.58, y)
    note(ax, fw,
         "Confirmado: setup_openfoam_case.py gera blockMeshDict, snappyHexMeshDict, "
         "controlDict, fvSchemes, fvSolution e 0/ (BC). Requer OpenFOAM instalado no sistema/WSL.")
    save(fig, "pb_fig10_cfd_openfoam.png")


# ════════════════════════════════════════════════════════════════════
# Fig 11 — Persistencia  [ATUALIZADO — sem MinIO]
# ════════════════════════════════════════════════════════════════════
def fig_persistencia():
    fig, ax, fw = make_fig(6, "Modulo de Persistencia  (SQLite + Filesystem Local)")
    y, xs = 2.2, [0.9, 2.25, 3.6, 4.95, 6.3, 7.65]
    box(ax, xs[0], y, "gear",  "Resultados\n(CFD, Blender\nPython)", style="std")
    box(ax, xs[1], y, "gear",  "Normalizacao\ndados p/\narmazenam.", style="proc")
    box(ax, xs[2], y, "db",    "SQLite\n(hash, tempo\nporosidade\nstatus)", style="proc")
    box(ax, xs[3], y, "file",  "Filesystem\nlocal\n(STL, .blend\nCSV, logs)", style="proc")
    box(ax, xs[4], y, "hash",  "Indexacao\nhash <-> path\n(SHA-256)", style="proc")
    box(ax, xs[5], y, "api",   "SQLAlchemy\n+ API REST\n(acesso)", style="out")
    for i in range(5): arrow(ax, xs[i]+0.62, xs[i+1]-0.62, y)
    note(ax, fw,
         "Diferenca do doc: SEM MinIO e SEM PostgreSQL. "
         "Usa SQLite (local_data/cfd_pipeline.db) + filesystem local. MinIO nao existe no codigo.")
    save(fig, "pb_fig11_persistencia.png")


# ════════════════════════════════════════════════════════════════════
# Fig 12 — API FastAPI  [ATUALIZADO — sem JWT]
# ════════════════════════════════════════════════════════════════════
def fig_api():
    fig, ax, fw = make_fig(6, "API  (FastAPI)")
    y, xs = 2.2, [0.9, 2.25, 3.6, 4.95, 6.3, 7.65]
    box(ax, xs[0], y, "api",   "Requisicoes\nHTTP REST", style="std")
    box(ax, xs[1], y, "check", "Validacao\nPydantic\n+ parse", style="proc")
    box(ax, xs[2], y, "hash",  "X-User-ID\nheader\n(sem JWT)", style="proc")
    box(ax, xs[3], y, "gear",  "Roteamento\nendpoints\nnegocio", style="proc")
    box(ax, xs[4], y, "db",    "Persistencia\n(SQLite\nFilesystem)", style="proc")
    box(ax, xs[5], y, "file",  "Resp. JSON\n(OpenAPI\n/docs)", style="out")
    for i in range(5): arrow(ax, xs[i]+0.62, xs[i+1]-0.62, y)
    note(ax, fw,
         "Diferenca do doc: SEM JWT. Auth via header X-User-ID (deps_user.py). "
         "Multi-tenant por user_id na query. Docs em /docs e /redoc.")
    save(fig, "pb_fig12_api_fastapi.png")


# ════════════════════════════════════════════════════════════════════
# Fig 13 — Dashboard React  [ATUALIZADO — Recharts nao Plotly]
# ════════════════════════════════════════════════════════════════════
def fig_dashboard():
    fig, ax, fw = make_fig(6, "Dashboard  (React + Three.js + Recharts)")
    y, xs = 2.2, [0.9, 2.25, 3.6, 4.95, 6.3, 7.65]
    box(ax, xs[0], y, "react", "Interface\nReact 18\n(Vite)", style="std")
    box(ax, xs[1], y, "api",   "Consumo\nAPI HTTP\nREST", style="proc")
    box(ax, xs[2], y, "cut",   "Viewer 3D\nSTL/OBJ/GLB\n(Three.js\nR3F+Drei)", style="proc")
    box(ax, xs[3], y, "hash",  "Graficos\nRecharts\n+ SVG custom\n(nao Plotly)", style="proc")
    box(ax, xs[4], y, "file",  "Lista runs\nfiltros hash\nstatus datas", style="proc")
    box(ax, xs[5], y, "check", "Sem acesso\ndireto arts.\n(so via API)", style="out")
    for i in range(5): arrow(ax, xs[i]+0.62, xs[i+1]-0.62, y)
    note(ax, fw,
         "Diferenca do doc: usa Recharts (nao Plotly). "
         "3D via @react-three/fiber + drei. DonutChart e StatusBar em SVG custom.")
    save(fig, "pb_fig13_dashboard_react.png")


# ════════════════════════════════════════════════════════════════════
# Fig 14 — CLI Wizard  [NOVO]
# ════════════════════════════════════════════════════════════════════
def fig_cli_wizard():
    fig, ax, fw = make_fig(6, "CLI Wizard  (Terminal Interativo)  [NOVO]")
    y, xs = 2.2, [0.9, 2.25, 3.6, 4.95, 6.3, 7.65]
    box(ax, xs[0], y, "cli",   "Entrada\n.bed /\ntemplate\n--spec", style="std")
    box(ax, xs[1], y, "gear",  "Modo\ninterativo\nou headless\n(flags)", style="new")
    box(ax, xs[2], y, "dsl",   "Geracao\n.bed +\ncompilacao\n-> .json", style="proc")
    box(ax, xs[3], y, "py",    "Motor\nPython Puro\nou Blender\n(selecion.)", style="proc")
    box(ax, xs[4], y, "check", "Preview\nterminal\n(Rich)", style="proc")
    box(ax, xs[5], y, "out",   ".stl / .blend\n+templates\nDB", style="out")
    for i in range(5): arrow(ax, xs[i]+0.62, xs[i+1]-0.62, y)
    note(ax, fw,
         "NOVO: wizard_cli.py + dsl/cli/ (Typer). "
         "Comandos: generate, compile, test, pipeline, templates, docs. "
         "Interativo com Rich ou headless via flags.",
         dashed=True)
    save(fig, "pb_fig14_cli_wizard.png")


# ════════════════════════════════════════════════════════════════════
# Fig 15 — Sistema de Jobs  [NOVO]
# ════════════════════════════════════════════════════════════════════
def fig_jobs():
    fig, ax, fw = make_fig(6, "Sistema de Jobs Assincronos  [NOVO]")
    y, xs = 2.2, [0.9, 2.25, 3.6, 4.95, 6.3, 7.65]
    box(ax, xs[0], y, "api",   "POST API\n(generate /\npipeline /\nCFD)", style="std")
    box(ax, xs[1], y, "job",   "Criar Job\nUUID\nstatus=\nqueued", style="new")
    box(ax, xs[2], y, "lock",  "Fila unica\n_MESH_LOCK\n(1 job mesh\npor vez)", style="proc")
    box(ax, xs[3], y, "py",    "Exec bgtask\nprogresso\n[bedflow N%]\nparsing", style="proc")
    box(ax, xs[4], y, "db",    "JobRecord\nDB: status\nlogs / files\nerros", style="proc")
    box(ax, xs[5], y, "api",   "GET /job/\n{id}\n(polling\ncliente)", style="out")
    for i in range(5): arrow(ax, xs[i]+0.62, xs[i+1]-0.62, y)
    note(ax, fw,
         "NOVO: mesh_job_runner.py + job_persistence.py. Tabela JobRecord (SQLite). "
         "Tipos: mesh_generation, openfoam_case, cfd_simulation, full_pipeline.",
         dashed=True)
    save(fig, "pb_fig15_sistema_jobs.png")


# ════════════════════════════════════════════════════════════════════
# Fig 16 — Rastreabilidade Seed + Hash  [NOVO]
# ════════════════════════════════════════════════════════════════════
def fig_seed_hash():
    fig, ax, fw = make_fig(5, "Sistema de Rastreabilidade  (Seed + Hash)  [NOVO]")
    y, xs = 2.2, [1.1, 2.6, 4.1, 5.6, 7.1]
    box(ax, xs[0], y, "seed",  "Seed\npacking /\nparticulas\n(fixo ou auto)", style="std")
    box(ax, xs[1], y, "gear",  "Execucao\ndeterminis-\ntica\n(mesmo seed)", style="new")
    box(ax, xs[2], y, "hash",  "SHA-256\ndo STL\n(content\nhash)", style="proc")
    box(ax, xs[3], y, "file",  "Sidecar JSON\n_pure_bed.json\nseed, hash\ncentros", style="proc")
    box(ax, xs[4], y, "check", "Reproducao\nexata c/\nmesmo seed\n+ hash", style="out")
    for i in range(4): arrow(ax, xs[i]+0.64, xs[i+1]-0.64, y)
    note(ax, fw,
         "NOVO: packing_seed.py resolve seeds. bedflow_export_metadata.py calcula SHA-256. "
         "Seed + hash gravados em JobRecord e no sidecar JSON de cada malha.",
         dashed=True)
    save(fig, "pb_fig16_seed_hash_rastreabilidade.png")


# ════════════════════════════════════════════════════════════════════
# Fig 17 — Templates  [NOVO]
# ════════════════════════════════════════════════════════════════════
def fig_templates():
    fig, ax, fw = make_fig(5, "Sistema de Templates  [NOVO]")
    y, xs = 2.2, [1.1, 2.6, 4.1, 5.6, 7.1]
    box(ax, xs[0], y, "file",  "Editor .bed\n(texto livre\nou wizard)", style="std")
    box(ax, xs[1], y, "api",   "POST /api\n/templates\n/save\nnome + tag", style="new")
    box(ax, xs[2], y, "db",    "BedTemplate\nSQLite\nid, name,\ncontent", style="proc")
    box(ax, xs[3], y, "check", "GET list\nbusca, filtro\npaginacao", style="proc")
    box(ax, xs[4], y, "cli",   "Reutilizar\n--template\nnome (CLI\nou web)", style="out")
    for i in range(4): arrow(ax, xs[i]+0.64, xs[i+1]-0.64, y)
    note(ax, fw,
         "NOVO: routes_templates.py. CRUD completo (save, list, get, update, delete). "
         "Fontes: editor manual ou import de arquivo. Integrado ao CLI e ao wizard web.",
         dashed=True)
    save(fig, "pb_fig17_sistema_templates.png")


# ════════════════════════════════════════════════════════════════════
if __name__ == "__main__":
    print("Gerando diagramas P&B...")
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
    print("Concluido — 12 diagramas P&B gerados em docs/")
