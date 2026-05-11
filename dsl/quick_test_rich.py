# camada visual do modo testes rapidos usando a biblioteca rich quando existe
# se rich nao estiver instalada _RICH fica false e cada funcao cai no ramo print simples
# cores e estilos copiam a ideia do wizard terminal ui chrome vermelho escuro e acento bege
# nenhuma destas funcoes altera geometria so mostra texto tabelas e barras de progresso
from __future__ import annotations

from contextlib import contextmanager
from pathlib import Path
from typing import Any, Dict, Iterator, List, Optional, Sequence, Tuple

try:
    from rich import box
    from rich.align import Align
    from rich.console import Console, Group
    from rich.panel import Panel
    from rich.progress import Progress, SpinnerColumn, TextColumn, TimeElapsedColumn
    from rich.rule import Rule
    from rich.table import Table
    from rich.text import Text

    _RICH = True
except ImportError:
    _RICH = False

from wizard_terminal_ui import (
    MenuRow,
    PICK_LIST_SHORT_HINT,
    render_menu_table_plain,
    render_menu_table_rich,
)

# strings de estilo rich repetidas para manter o mesmo look do menu principal
_CHROME = "bold white on rgb(95,25,35)"
_ACCENT = "bold rgb(240,212,168)"
_BORDER_MAIN = "rgb(95,25,35)"


def rich_available() -> bool:
    # devolve true se o import rich correu sem erro no arranque deste modulo
    return _RICH


def get_console(wizard_ui: Any) -> Optional["Console"]:
    # rich wizard ui guarda self console plain ui nao tem esse atributo
    # quando nao ha console devolvemos none e o chamador usa print
    if not _RICH:
        return None
    return getattr(wizard_ui, "console", None)


@contextmanager
def progress_phase(console: Optional[Console], description: str) -> Iterator[None]:
    # context manager que mostra spinner mais texto mais tempo decorrido
    # transient true apaga a barra ao sair para nao poluir o ecra
    # description e uma frase curta explicando a fase atual ao utilizador
    if console and _RICH:
        with Progress(
            SpinnerColumn(),
            TextColumn("[bold cyan]{task.description}"),
            TimeElapsedColumn(),
            console=console,
            transient=True,
        ) as progress:
            progress.add_task(description, total=None)
            yield
    else:
        print(f"  ... {description}")
        yield


def render_rigid_body_notice(console: Optional[Any]) -> None:
    """avisos visuais sobre limitacoes do modo rigid_body no blender."""
    body = (
        "o modo rigid_body delega colisao e repouso ao motor de fisica do blender.\n"
        "pode ser nao determinista (semente, passos, gpu) e apresentar "
        "interpenetracoes ou contactos visuais imperfeitos.\n"
        "nao usa o mesmo validador geometrico fechado que spherical_packing e hexagonal_3d.\n"
        "use spherical_packing ou hexagonal_3d quando precisar de validacao por distancia minima."
    )
    if console and _RICH:
        from rich.panel import Panel as RP
        from rich.text import Text as RT

        console.print(
            RP(
                RT(body, style="dim"),
                title="aviso rigid_body",
                border_style="yellow",
                box=box.ROUNDED,
            )
        )
    else:
        print("\naviso rigid_body:")
        print(body)


def render_test_header(console: Optional[Console], subtitle: str = "") -> None:
    # painel grande de abertura com titulo bicolor e subtitulo em cinza
    # no fallback sem rich usa linhas de igualdade estilo ascii antigo
    title = Text()
    title.append(" testes rapidos ", style=_CHROME)
    title.append(" validacao de leito ", style=_ACCENT)
    if console and _RICH:
        console.print(
            Panel(
                Align.left(Group(title, Text(subtitle or "fluxo guiado com preview no terminal", style="dim"))),
                box=box.HEAVY,
                border_style="rgb(95,25,35)",
                padding=(0, 1),
            )
        )
        console.print()
    else:
        print("=" * 62)
        print("  testes rapidos")
        if subtitle:
            print(f"  {subtitle}")
        print("=" * 62)
        print()


def render_step_title(console: Optional[Console], step: str, title: str) -> None:
    # separador visual entre perguntas do fluxo em cinco passos
    # step e o numero title e o nome curto da pergunta
    line = f"{step} — {title}"
    if console and _RICH:
        console.print(Rule(Text(line.lower(), style=_ACCENT), style="rgb(95,25,35)"))
    else:
        print(f"\n--- {line} ---")


def _choice_menu_rows(rows: Sequence[Tuple[str, str]]) -> List[MenuRow]:
    """converte (tecla, texto longo) em MenuRow para a tabela padrao do wizard."""
    out: List[MenuRow] = []
    for key, label in rows:
        s = (label or "").strip()
        if "—" in s:
            modo, rest = s.split("—", 1)
            modo, rest = modo.strip(), rest.strip()
        elif " - " in s:
            modo, rest = s.split(" - ", 1)
            modo, rest = modo.strip(), rest.strip()
        else:
            modo = s[:34] + ("…" if len(s) > 34 else "")
            rest = s
        out.append((key, modo, rest))
    return out


def render_choice_table(
    console: Optional[Console],
    caption: str,
    rows: Sequence[Tuple[str, str]],
    reference_key: Optional[str] = None,
) -> None:
    """menu numerado com o mesmo layout que o menu principal (tabela # modo | resumo)."""
    menu_rows = _choice_menu_rows(rows)
    ref_line = ""
    if reference_key:
        ref_line = (
            f"referencia do ficheiro (so informativo, nao e escolha automatica): [{reference_key}]\n"
        )
    tail = f"{ref_line}{PICK_LIST_SHORT_HINT}  |  digite o numero; 0 cancelar o fluxo"
    if console and _RICH:
        console.print(Text(caption, style="bold rgb(240,212,168)"))
        render_menu_table_rich(console, menu_rows, title="opcoes")
        console.print(Text(tail, style="dim"))
    else:
        print(caption)
        render_menu_table_plain(menu_rows, title="opcoes")
        print(f"  {tail}")


def render_technical_before(
    console: Optional[Console],
    data: Dict[str, Any],
    *,
    input_label: str,
    input_path: str,
    backend: str,
    packing: str,
    geometry_mode: str,
    slice_detail: Optional[Dict[str, Any]],
    exec_label: str,
    post_label: str,
) -> None:
    # blocos separados: fluxo, geometria leito, packing, modo geometrico, fatia, execucao
    bed = dict(data.get("bed") or {})
    particles = dict(data.get("particles") or {})
    packing_d = dict(data.get("packing") or {})
    d = float(bed.get("diameter") or 0.0)
    wt = float(bed.get("wall_thickness") or 0.0)
    h = float(bed.get("height") or 0.0)
    r_ext = d / 2.0
    r_int = max(r_ext - wt, 0.0)
    pd = float(particles.get("diameter") or 0.0)
    rs = pd / 2.0
    n = int(particles.get("count") or 0)
    gap = packing_d.get("gap")
    if gap is None:
        gap = packing_d.get("collision_margin")
    gap_f = float(gap) if gap is not None else 0.0

    def _emit_rule(title: str) -> None:
        if console and _RICH:
            console.print(Rule(Text(title.lower(), style=_ACCENT), style=_BORDER_MAIN))
        else:
            print(f"\n--- {title} ---")

    def _emit_pairs(title: str, pairs: List[Tuple[str, str]]) -> None:
        t = Table(
            box=box.ROUNDED,
            border_style=_BORDER_MAIN,
            show_header=False,
            title=title,
            title_style="dim",
        )
        t.add_column("campo", style="dim", width=30)
        t.add_column("valor", style="")
        for a, b in pairs:
            t.add_row(a, b)
        if console and _RICH:
            console.print(Panel(t, box=box.SIMPLE, padding=(0, 0)))
        else:
            print(f"\n{title}")
            for a, b in pairs:
                print(f"  {a}: {b}")

    _emit_rule("resumo tecnico antes da execucao")
    _emit_pairs(
        "fluxo e ficheiros",
        [
            ("entrada", f"{input_label}  {input_path}"),
            ("backend", backend),
            ("execucao", exec_label),
            ("pos-execucao", post_label),
        ],
    )
    _emit_pairs(
        "geometria do leito",
        [
            ("raio externo (m)", f"{r_ext:.6f}"),
            ("raio interno (m)", f"{r_int:.6f}"),
            ("altura leito (m)", f"{h:.6f}"),
            ("raio esferas (m)", f"{rs:.6f}"),
            ("quantidade pedida", str(n)),
            ("gap / margem (m)", f"{gap_f:.6f}"),
        ],
    )
    _emit_pairs(
        "packing (metodo de distribuicao)",
        [
            ("packing.method", packing),
            ("nota", "independente do modo geometrico full_3d vs fatia fina"),
        ],
    )
    slice_rows: List[Tuple[str, str]] = [("geometry_mode", geometry_mode)]
    if slice_detail:
        slice_rows.extend(
            [
                ("eixo normal do corte", str(slice_detail.get("slice_axis", "?"))),
                ("espessura (m)", str(slice_detail.get("slice_thickness", "?"))),
                ("posicao centro (m)", str(slice_detail.get("slice_position", "?"))),
                (
                    "so intersectantes",
                    str(slice_detail.get("keep_only_intersecting_particles", "?")),
                ),
                (
                    "preservar coords originais",
                    str(slice_detail.get("preserve_original_packing", "?")),
                ),
            ]
        )
    _emit_pairs("geometria de saida (nao e packing)", slice_rows)



def render_ascii_section(
    console: Optional[Console],
    ascii_block: str,
    *,
    title: str = "secao transversal (esquematica)",
) -> None:
    # painel monoespacado com texto dim para nao competir com tabelas numericas
    # ascii_block pode ter varias linhas com quebras ja embutidas
    if console and _RICH:
        console.print(
            Panel(
                Text(ascii_block, style="dim"),
                title=title,
                border_style=_BORDER_MAIN,
                box=box.ROUNDED,
            )
        )
    else:
        print(f"\n{title}")
        print(ascii_block)


def render_coordinate_table(
    console: Optional[Console],
    rows: List[Tuple[int, float, float, float]],
) -> None:
    # cada tuplo e id inteiro seguido de tres floats xyz em metros
    # lista vazia significa nada a mostrar
    if not rows:
        return
    t = Table(
        title="amostra de coordenadas",
        box=box.ROUNDED,
        border_style=_BORDER_MAIN,
        header_style=_ACCENT,
        show_header=True,
    )
    t.add_column("id", justify="right")
    t.add_column("x (m)", justify="right")
    t.add_column("y (m)", justify="right")
    t.add_column("z (m)", justify="right")
    for i, x, y, z in rows:
        t.add_row(str(i), f"{x:.6f}", f"{y:.6f}", f"{z:.6f}")
    if console and _RICH:
        console.print(t)
    else:
        print("\namostra coordenadas")
        for i, x, y, z in rows:
            print(f"  {i}  {x:.6f}  {y:.6f}  {z:.6f}")


def render_height_distribution(console: Optional[Console], lines: List[str]) -> None:
    # lines ja vem formatadas uma string por faixa de z com hashtags
    # quick test preview height distribution lines produz essa lista
    body = "\n".join(lines) if lines else "(sem dados de altura)"
    if console and _RICH:
        console.print(
            Panel(
                Text(body, style=""),
                title="distribuicao vertical (faixas de z)",
                border_style=_BORDER_MAIN,
                box=box.ROUNDED,
            )
        )
    else:
        print("\ndistribuicao por z")
        print(body)


def render_result_panel(
    console: Optional[Console],
    ok: bool,
    lines: List[Tuple[str, str]],
    title: str = "resultado",
) -> None:
    # painel alinhado ao tema principal: borda vermelha escura; estado ok em verde
    t = Table(box=box.ROUNDED, show_header=False, border_style=_BORDER_MAIN)
    t.add_column("k", style="dim", width=28)
    t.add_column("v", style="")
    for k, v in lines:
        t.add_row(k, v)
    edge = "green" if ok else "red"
    if console and _RICH:
        console.print(
            Panel(
                t,
                title=title,
                border_style=edge,
                box=box.ROUNDED,
            )
        )
    else:
        print(f"\n{title}")
        for k, v in lines:
            print(f"  {k}: {v}")


def render_success_panel(console: Optional[Console], message: str, title: str = "sucesso") -> None:
    if console and _RICH:
        console.print(
            Panel(
                Text(message, style="green"),
                title=title,
                border_style="green",
                box=box.ROUNDED,
            )
        )
    else:
        print(f"\n{title}: {message}")


def render_warning_panel(console: Optional[Console], message: str, title: str = "aviso") -> None:
    if console and _RICH:
        console.print(
            Panel(
                Text(message, style="yellow"),
                title=title,
                border_style="yellow",
                box=box.ROUNDED,
            )
        )
    else:
        print(f"\n{title}: {message}")


def render_error_panel(console: Optional[Console], message: str) -> None:
    # mensagem curta de falha sem traceback aqui
    if console and _RICH:
        console.print(
            Panel(
                Text(message, style="bold red"),
                title="erro",
                border_style="red",
                box=box.ROUNDED,
            )
        )
    else:
        print(f"\nerro: {message}")


def render_blender_open_confirmation(console: Optional[Console], path: Path, kind: str) -> None:
    # kind explica se abrimos stl ou blend para o utilizador distinguir
    if console and _RICH:
        msg = Text()
        msg.append("blender aberto em segundo plano\n", style="green")
        msg.append(str(path), style="cyan")
        msg.append(f"\ntipo: {kind}", style="dim")
        console.print(Panel(msg, title="sucesso blender", border_style="green", box=box.ROUNDED))
    else:
        print(f"\nblender aberto: {path}")


def load_packing_report(blend_path: Optional[Path]) -> Optional[Dict[str, Any]]:
    # o script leito extracao grava json ao lado do blend em modos cientificos
    # nome e stem do blend mais sufixo packing report
    # rigid body legacy pode nao criar este ficheiro
    if not blend_path:
        return None
    p = blend_path.parent / f"{blend_path.stem}_packing_report.json"
    if not p.is_file():
        return None
    try:
        import json

        with p.open("r", encoding="utf-8") as f:
            d = json.load(f)
        return d if isinstance(d, dict) else None
    except OSError:
        return None
