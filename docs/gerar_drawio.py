"""
Gerador de arquivo draw.io com 12 diagramas BEDFLOW-ATLAS-TCC-2
Abre em: https://app.diagrams.net  (File > Import ou arraste o .drawio)
Cada diagrama fica em uma aba/pagina separada — clique e edite livremente.
"""

import html as _html
import os

OUT_DIR = os.path.dirname(os.path.abspath(__file__))
OUT_FILE = os.path.join(OUT_DIR, "bedflow_diagramas.drawio")

# ── helpers ───────────────────────────────────────────────────────────────────

def x(s):
    """XML-escape para uso em atributos."""
    return _html.escape(str(s), quote=True)

def label(icon, *lines):
    """Label HTML: icone grande em cima, descricao pequena embaixo."""
    desc = "<br/>".join(lines)
    raw = (
        f'<div style="text-align:center;">'
        f'<b style="font-size:17px;">{icon}</b>'
        f'<br/><font style="font-size:9px;line-height:1.35;">{desc}</font>'
        f'</div>'
    )
    return x(raw)

# ── estilos draw.io ───────────────────────────────────────────────────────────

_BASE = "html=1;align=center;verticalAlign=middle;whiteSpace=wrap;"

STYLE = {
    # box entrada — cinza claro
    "std":  f"rounded=1;arcSize=8;fillColor=#f0f0f0;strokeColor=#444444;strokeWidth=1;{_BASE}",
    # box processo — cinza medio
    "proc": f"rounded=1;arcSize=8;fillColor=#e0e0e0;strokeColor=#444444;strokeWidth=1;{_BASE}",
    # box saida — branco, borda dupla/forte
    "out":  f"rounded=1;arcSize=8;fillColor=#ffffff;strokeColor=#111111;strokeWidth=2.5;{_BASE}",
    # box novo — cinza escuro, borda forte
    "new":  f"rounded=1;arcSize=8;fillColor=#d0d0d0;strokeColor=#111111;strokeWidth=2;{_BASE}",
}

HDR  = "fillColor=#111111;fontColor=#ffffff;strokeColor=none;fontSize=13;fontStyle=1;align=center;verticalAlign=middle;"
ARW  = ("edgeStyle=orthogonalEdgeStyle;orthogonalLoop=1;jettySize=auto;"
        "exitX=1;exitY=0.5;exitDx=0;exitDy=0;"
        "entryX=0;entryY=0.5;entryDx=0;entryDy=0;"
        "strokeColor=#111111;strokeWidth=1.6;endArrow=block;endFill=1;")
NOTE = ("rounded=1;arcSize=5;fillColor=#f8f8f8;strokeColor=#666666;"
        "strokeWidth=1;dashed=1;fontSize=9;fontColor=#333333;"
        "align=center;verticalAlign=middle;html=1;whiteSpace=wrap;")

# ── classe construtora ────────────────────────────────────────────────────────

class Diagram:
    def __init__(self, pid, name, n, wide=False):
        self.pid  = pid
        self.name = name
        self.cells: list[str] = []
        self._cid = 1          # IDs por diagrama (reset a cada pagina)
        self.box_ids: list[str] = []

        # geometria
        if n == 7 or wide:
            self.cw, self.bw = 1420, 122
        elif n == 6:
            self.cw, self.bw = 1310, 132
        else:                        # 5 colunas
            self.cw, self.bw = 1200, 145

        self.ch   = 430
        self.bh   = 112
        self.by   = 90            # y topo dos boxes

        # centros horizontais dos boxes
        usable   = self.cw - 40
        gap      = (usable - n * self.bw) / (n + 1)
        self.cx  = [int(20 + gap + i * (self.bw + gap) + self.bw / 2)
                    for i in range(n)]

    # ── utilitarios internos ─────────────────────────────────────────────────

    def _id(self):
        self._cid += 1
        return f"p{self.pid}_{self._cid}"

    def _cell(self, cid, val, style, gx, gy, gw, gh):
        self.cells.append(
            f'        <mxCell id="{cid}" value="{val}" style="{style}" '
            f'vertex="1" parent="1">\n'
            f'          <mxGeometry x="{gx}" y="{gy}" width="{gw}" '
            f'height="{gh}" as="geometry"/>\n'
            f'        </mxCell>'
        )

    # ── API publica ──────────────────────────────────────────────────────────

    def header(self, title):
        cid = self._id()
        self._cell(cid, x(title), HDR, 20, 15, self.cw - 40, 58)

    def box(self, i, icon, *lines, sty="proc"):
        cid = self._id()
        self.box_ids.append(cid)
        bx = self.cx[i] - self.bw // 2
        self._cell(cid, label(icon, *lines), STYLE[sty], bx, self.by, self.bw, self.bh)

    def arrows(self):
        for a, b in zip(self.box_ids, self.box_ids[1:]):
            cid = self._id()
            self.cells.append(
                f'        <mxCell id="{cid}" style="{ARW}" edge="1" '
                f'source="{a}" target="{b}" parent="1">\n'
                f'          <mxGeometry relative="1" as="geometry"/>\n'
                f'        </mxCell>'
            )

    def note(self, text, dashed=False):
        sty = NOTE if dashed else NOTE.replace("dashed=1;", "dashed=0;")
        cid = self._id()
        self._cell(cid, x(text), sty, 20, 318, self.cw - 40, 62)

    def xml(self):
        inner = "\n".join(self.cells)
        return (
            f'  <diagram id="d{self.pid}" name="{x(self.name)}">\n'
            f'    <mxGraphModel dx="1200" dy="800" grid="0" gridSize="10" '
            f'guides="1" tooltips="1" connect="1" arrows="1" fold="1" '
            f'page="0" pageScale="1" pageWidth="{self.cw}" '
            f'pageHeight="{self.ch}" math="0" shadow="0" background="#ffffff">\n'
            f'      <root>\n'
            f'        <mxCell id="0" />\n'
            f'        <mxCell id="1" parent="0" />\n'
            f'{inner}\n'
            f'      </root>\n'
            f'    </mxGraphModel>\n'
            f'  </diagram>'
        )


# ═════════════════════════════════════════════════════════════════════════════
# Definicoes de cada diagrama
# ═════════════════════════════════════════════════════════════════════════════

def d_dsl():
    d = Diagram(1, "Fig 08 - DSL Compilador", 5)
    d.header("Modulo DSL  (Compilador)")
    d.box(0, "[ ]",  "Entrada", ".bed",                          sty="std")
    d.box(1, "OK",   "Validacao", "sintaxe &amp;", "semantica",  sty="proc")
    d.box(2, "DSL",  "Normalizacao", "unidades SI", "(ANTLR 4)", sty="proc")
    d.box(3, "#",    "Hash SHA-256", "8 chars", "(_metadata)",   sty="proc")
    d.box(4, "{ }",  ".bed.json", "(hash em", "_metadata)",      sty="out")
    d.arrows()
    d.note("Diferenca do doc: saida e um unico .bed.json com hash em _metadata.hash "
           "-- nao sao arquivos separados params.json e params.hash")
    return d.xml()

def d_blender():
    d = Diagram(2, "Fig 09a - Modelagem Blender", 6)
    d.header("Modulo de Modelagem Geometrica  (Blender 4.x)")
    d.box(0, "[ ]",  ".bed.json", "+ hash",                        sty="std")
    d.box(1, "Cfg",  "Cilindro", "+ tampas", "(Python API)",        sty="proc")
    d.box(2, "Cfg",  "Empacot.", "particulas", "(seed fixa)",       sty="proc")
    d.box(3, "OK",   "Manifold", "watertight", "check",             sty="proc")
    d.box(4, "#",    "Porosidade", "efetiva", "(calculo)",          sty="proc")
    d.box(5, "{ }",  "leito.stl", ".blend", ".obj / .glb",         sty="out")
    d.arrows()
    d.note("Diferenca do doc: exporta tambem .blend, .obj, .glb alem de .stl. "
           "Alternativa Python Puro disponivel (ver Fig 09b)")
    return d.xml()

def d_python():
    d = Diagram(3, "Fig 09b - Motor Python Puro  [NOVO]", 6)
    d.header("Motor de Modelagem Python Puro  [NOVO]")
    d.box(0, "[ ]",  ".bed.json", "+ hash",                          sty="std")
    d.box(1, "PY",   "Stdlib only", "(math, struct)", "stl_mesh_utils", sty="new")
    d.box(2, "Cfg",  "Empacotar", "hex_3d /", "RSA / rigido",        sty="proc")
    d.box(3, "+",    "Modo geo:", "full_3d ou", "thin_slice",         sty="proc")
    d.box(4, "#",    "Metadados:", "seed, hash,", "centros",          sty="proc")
    d.box(5, "{ }",  "leito.stl", "(binario)", "+sidecar .json",      sty="out")
    d.arrows()
    d.note("NOVO: sem Blender. Usa apenas Python stdlib (math, struct). "
           "Output: STL binario + _pure_bed.json sidecar (seed, porosidade, centros)",
           dashed=True)
    return d.xml()

def d_slice():
    d = Diagram(4, "Fig 09c - Thin Slice / Pseudo-2D  [NOVO]", 6)
    d.header("Modulo de Corte Pseudo-2D  (Thin Slice)  [NOVO]")
    d.box(0, "[ ]",  "Leito 3D", "(centros", "+ shell)",              sty="std")
    d.box(1, "Cfg",  "Config fatia", "eixo x/y/z", "pos + esp.",      sty="new")
    d.box(2, "+",    "Filtro", "particulas", "c/ plano",               sty="proc")
    d.box(3, "+",    "Clipagem", "shell", "(slab min/max)",            sty="proc")
    d.box(4, "#",    "Relatorio:", "retidas /", "descartadas",         sty="proc")
    d.box(5, "{ }",  "fatia.stl", "(pseudo-2D)", "+metadados",         sty="out")
    d.arrows()
    d.note("NOVO: thin_slice_build.py + thin_slice_particles.py. "
           "Modo pseudo_2d_thin_slice. Tambem existe pseudo_2d_statistical (RSA 2D).",
           dashed=True)
    return d.xml()

def d_openfoam():
    d = Diagram(5, "Fig 10 - CFD OpenFOAM", 7, wide=True)
    d.header("Modulo de Simulacao CFD  (OpenFOAM)")
    d.box(0, "[ ]",  "Geom STL", "+ porosity", ".json",              sty="std")
    d.box(1, "Cfg",  "Estrutura", "diret.", "caso OF",               sty="proc")
    d.box(2, "+",    "blockMesh", "(malha hex", "fundo)",             sty="proc")
    d.box(3, "Cfg",  "snappyHex", "Mesh", "(refinamento)",           sty="proc")
    d.box(4, "Cfg",  "Cond. cont.", "p / U / k/e", "controlDict",    sty="proc")
    d.box(5, "PY",   "simpleFoam", "(solver", "estac.)",             sty="proc")
    d.box(6, "{ }",  "Metricas", "dP, Re,", "cels, CSV",            sty="out")
    d.arrows()
    d.note("Confirmado: setup_openfoam_case.py gera blockMeshDict, snappyHexMeshDict, "
           "controlDict, fvSchemes, fvSolution e 0/ (BC). Requer OpenFOAM no sistema/WSL.")
    return d.xml()

def d_persist():
    d = Diagram(6, "Fig 11 - Persistencia", 6)
    d.header("Modulo de Persistencia  (SQLite + Filesystem Local)")
    d.box(0, "Cfg",  "Resultados", "(CFD, Blender", "Python)",        sty="std")
    d.box(1, "Cfg",  "Normalizacao", "dados p/", "armazenam.",        sty="proc")
    d.box(2, "DB",   "SQLite", "(hash, tempo", "porosidade, status)", sty="proc")
    d.box(3, "[ ]",  "Filesystem", "local", "(STL, CSV, logs)",       sty="proc")
    d.box(4, "#",    "Indexacao", "hash &lt;-&gt; path", "(SHA-256)", sty="proc")
    d.box(5, "API",  "SQLAlchemy", "+ API REST", "(acesso)",          sty="out")
    d.arrows()
    d.note("Diferenca do doc: SEM MinIO e SEM PostgreSQL. "
           "Usa SQLite (local_data/cfd_pipeline.db) + filesystem local. MinIO nao existe no codigo.")
    return d.xml()

def d_api():
    d = Diagram(7, "Fig 12 - API FastAPI", 6)
    d.header("API  (FastAPI)")
    d.box(0, "API",  "Requisicoes", "HTTP REST",                      sty="std")
    d.box(1, "OK",   "Validacao", "Pydantic", "+ parse",              sty="proc")
    d.box(2, "#",    "X-User-ID", "header", "(sem JWT)",              sty="proc")
    d.box(3, "Cfg",  "Roteamento", "endpoints", "negocio",            sty="proc")
    d.box(4, "DB",   "Persistencia", "(SQLite", "Filesystem)",        sty="proc")
    d.box(5, "{ }",  "Resp. JSON", "(OpenAPI", "/docs)",              sty="out")
    d.arrows()
    d.note("Diferenca do doc: SEM JWT. Auth via header X-User-ID (deps_user.py). "
           "Multi-tenant por user_id na query. Docs em /docs e /redoc.")
    return d.xml()

def d_dashboard():
    d = Diagram(8, "Fig 13 - Dashboard React", 6)
    d.header("Dashboard  (React + Three.js + Recharts)")
    d.box(0, "R",    "Interface", "React 18", "(Vite)",               sty="std")
    d.box(1, "API",  "Consumo", "API HTTP", "REST",                   sty="proc")
    d.box(2, "+",    "Viewer 3D", "STL/OBJ/GLB", "(Three.js / R3F)", sty="proc")
    d.box(3, "#",    "Graficos", "Recharts", "+ SVG custom",          sty="proc")
    d.box(4, "[ ]",  "Lista runs", "filtros hash", "status, datas",   sty="proc")
    d.box(5, "OK",   "Sem acesso", "direto artefatos", "(so via API)",sty="out")
    d.arrows()
    d.note("Diferenca do doc: usa Recharts (nao Plotly). "
           "3D via @react-three/fiber + drei. DonutChart e StatusBar em SVG custom.")
    return d.xml()

def d_wizard():
    d = Diagram(9, "Fig 14 - CLI Wizard  [NOVO]", 6)
    d.header("CLI Wizard  (Terminal Interativo)  [NOVO]")
    d.box(0, "&gt;_", "Entrada", ".bed /", "template / --spec",       sty="std")
    d.box(1, "Cfg",  "Modo:", "interativo ou", "headless (flags)",     sty="new")
    d.box(2, "DSL",  "Geracao .bed", "+ compilacao", "-> .json",       sty="proc")
    d.box(3, "PY",   "Motor", "Python Puro", "ou Blender",             sty="proc")
    d.box(4, "OK",   "Preview", "terminal", "(Rich)",                  sty="proc")
    d.box(5, "{ }",  ".stl / .blend", "+templates", "DB",             sty="out")
    d.arrows()
    d.note("NOVO: wizard_cli.py + dsl/cli/ (Typer). "
           "Comandos: generate, compile, test, pipeline, templates, docs. "
           "Interativo com Rich ou headless via flags.",
           dashed=True)
    return d.xml()

def d_jobs():
    d = Diagram(10, "Fig 15 - Jobs Assincronos  [NOVO]", 6)
    d.header("Sistema de Jobs Assincronos  [NOVO]")
    d.box(0, "API",  "POST API", "(generate /", "pipeline / CFD)",    sty="std")
    d.box(1, "JOB",  "Criar Job", "UUID", "status=queued",            sty="new")
    d.box(2, "[1]",  "Fila unica", "_MESH_LOCK", "(1 job/vez)",       sty="proc")
    d.box(3, "PY",   "Exec bgtask", "progresso", "[bedflow N%]",      sty="proc")
    d.box(4, "DB",   "JobRecord", "DB: status", "logs / erros",       sty="proc")
    d.box(5, "API",  "GET /job/", "{id}", "(polling cliente)",        sty="out")
    d.arrows()
    d.note("NOVO: mesh_job_runner.py + job_persistence.py. Tabela JobRecord (SQLite). "
           "Tipos: mesh_generation, openfoam_case, cfd_simulation, full_pipeline.",
           dashed=True)
    return d.xml()

def d_seed():
    d = Diagram(11, "Fig 16 - Rastreabilidade Seed+Hash  [NOVO]", 5)
    d.header("Sistema de Rastreabilidade  (Seed + Hash)  [NOVO]")
    d.box(0, "S",    "Seed", "packing /", "particulas",               sty="std")
    d.box(1, "Cfg",  "Execucao", "deterministica", "(mesmo seed)",     sty="new")
    d.box(2, "#",    "SHA-256", "do STL", "(content hash)",           sty="proc")
    d.box(3, "[ ]",  "Sidecar JSON", "_pure_bed.json", "seed, centros",sty="proc")
    d.box(4, "OK",   "Reproducao", "exata c/", "mesmo seed + hash",   sty="out")
    d.arrows()
    d.note("NOVO: packing_seed.py resolve seeds. bedflow_export_metadata.py calcula SHA-256. "
           "Seed + hash gravados em JobRecord e no sidecar JSON de cada malha.",
           dashed=True)
    return d.xml()

def d_templates():
    d = Diagram(12, "Fig 17 - Templates  [NOVO]", 5)
    d.header("Sistema de Templates  [NOVO]")
    d.box(0, "[ ]",  "Editor .bed", "(texto livre", "ou wizard)",      sty="std")
    d.box(1, "API",  "POST /api", "/templates/save", "nome + tag",     sty="new")
    d.box(2, "DB",   "BedTemplate", "SQLite", "id, name, content",     sty="proc")
    d.box(3, "OK",   "GET list", "busca, filtro", "paginacao",         sty="proc")
    d.box(4, "&gt;_","Reutilizar", "--template nome", "(CLI ou web)",  sty="out")
    d.arrows()
    d.note("NOVO: routes_templates.py. CRUD completo (save, list, get, update, delete). "
           "Fontes: editor manual ou import de arquivo. Integrado ao CLI e ao wizard web.",
           dashed=True)
    return d.xml()

# ── montagem do arquivo final ─────────────────────────────────────────────────

PAGES = [
    d_dsl, d_blender, d_python, d_slice, d_openfoam,
    d_persist, d_api, d_dashboard, d_wizard, d_jobs,
    d_seed, d_templates,
]

def main():
    diagrams_xml = "\n".join(fn() for fn in PAGES)
    content = (
        '<?xml version="1.0" encoding="UTF-8"?>\n'
        '<mxfile host="app.diagrams.net" version="21.1.2" '
        'type="device">\n'
        f'{diagrams_xml}\n'
        '</mxfile>\n'
    )
    with open(OUT_FILE, "w", encoding="utf-8") as f:
        f.write(content)
    print(f"Arquivo gerado: {OUT_FILE}")
    print("Abra em: https://app.diagrams.net")
    print("  -> File > Import From > Device  (ou arraste o arquivo)")

if __name__ == "__main__":
    main()
