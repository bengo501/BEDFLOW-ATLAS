"""
interface do wizard no terminal: layout limpo, tipo barra de endereco + tabela de opcoes.
usa rich se estiver instalado; caso contrario, modo texto simples compativel.
"""

from __future__ import annotations

import os
import textwrap
from typing import Any, Callable, List, Optional, Sequence, Tuple

try:
    from rich import box
    from rich.align import Align
    from rich.console import Console
    from rich.markup import escape
    from rich.panel import Panel
    from rich.prompt import Confirm
    from rich.rule import Rule
    from rich.table import Table
    from rich.text import Text
    from rich.theme import Theme

    _HAS_RICH = True
except ImportError:
    escape = None  # type: ignore
    _HAS_RICH = False

try:
    from prompt_toolkit import PromptSession
    from prompt_toolkit.auto_suggest import AutoSuggestFromHistory
    from prompt_toolkit.completion import WordCompleter
    from prompt_toolkit.history import InMemoryHistory
    from prompt_toolkit.key_binding import KeyBindings

    _HAS_PROMPT_TOOLKIT = True
except ImportError:
    PromptSession = None  # type: ignore
    _HAS_PROMPT_TOOLKIT = False

MenuRow = Tuple[str, str, str]

# texto completo de ajuda (h em confirm, pick_from_list e menus que reutilizam a constante)
GLOBAL_KEYS_HINT = (
    "menus numerados (tabelas com 0 1 2 …):\n"
    "- 0 ou c regressa ou cancela esse passo (equivalentes neste menu).\n"
    "- 1–n escolhe a linha; enter vazio so confirma quando o menu indicar padrao explicito.\n"
    "- ? ajuda do campo (se existir), * rever parametros (quando activo), h este texto.\n\n"
    "perguntas internas (s/n, caminhos, numeros):\n"
    "- c cancela o fluxo actual (equivalente a voltar um nivel).\n"
    "- h ajuda; * rever parametros quando disponivel.\n\n"
    "linha de comando (prompt_toolkit): setas, ctrl+r historico, tab completa atalhos.\n\n"
    "no menu principal da aplicacao, 0 encerra."
)

# linha curta sob listas numeradas / ecra de ajuda por seccoes (detalhe completo com h)
PICK_LIST_SHORT_HINT = "0 ou c voltar  ·  ? ajuda do campo  ·  h ajuda global"


def _numeric_menu_aux_lines(
    *,
    n_opt: int,
    has_zero_back: bool,
    help_callback: Optional[Callable[[], None]],
    review_callback: Optional[Callable[[], None]],
    menu_default_index: Optional[int],
) -> List[str]:
    """linhas discretas por baixo da tabela de menu numerado."""
    parts: List[str] = []
    if has_zero_back:
        parts.append("0 ou c voltar")
    parts.append(f"1–{n_opt} escolher")
    if help_callback:
        parts.append("? ajuda do campo")
    if review_callback:
        parts.append("* rever parametros")
    parts.append("h ajuda global")
    lines = ["  " + "  ·  ".join(parts)]
    if menu_default_index is not None:
        lines.append(f"  enter vazio = opcao {menu_default_index + 1}")
    else:
        lines.append("  enter vazio nao escolhe linha")
    return lines


def view3d_mesh_pick_aux_lines(n_models: int) -> List[str]:
    """rodape do passo 'escolher modelo' no modo visualizacao 3d (sem tabela 0)."""
    n = max(1, int(n_models))
    row1 = (
        "0 ou c voltar a pesquisa  ·  "
        f"1–{n} escolher  ·  "
        "? ajuda do campo  ·  "
        "h ajuda global"
    )
    return [row1, "enter vazio nao escolhe linha"]


def _internal_prompt_aux_lines(
    *,
    cancel: bool,
    review: bool,
    require_explicit: bool = False,
    extra_bits: Sequence[str] = (),
) -> List[str]:
    bits = ["h ajuda"]
    if cancel:
        bits.append("c cancelar")
    if review:
        bits.append("* rever parametros")
    for x in extra_bits:
        t = (x or "").strip()
        if t:
            bits.append(t)
    lines = ["  " + "  ·  ".join(bits)]
    if require_explicit:
        lines.append("  enter vazio nao confirma; digite s ou n")
    return lines


def _options_to_menu_rows(options: List[str]) -> List[MenuRow]:
    """converte lista de textos longos em linhas # | modo | resumo (como menu principal)."""
    out: List[MenuRow] = []
    for i, label in enumerate(options, start=1):
        key = str(i)
        s = (label or "").strip()
        if "—" in s:
            modo, rest = s.split("—", 1)
            modo, rest = modo.strip(), rest.strip()
        elif " - " in s:
            modo, rest = s.split(" - ", 1)
            modo, rest = modo.strip(), rest.strip()
        else:
            modo = s[:36] + ("…" if len(s) > 36 else "")
            rest = s
        out.append((key, modo, rest))
    return out


def _help_entries_to_menu_rows(
    entries: Sequence[Tuple[str, str]], back_key: str
) -> List[MenuRow]:
    rows: List[MenuRow] = []
    for key, label in entries:
        s = (label or "").strip()
        k = str(key).strip()
        if "—" in s:
            modo, rest = s.split("—", 1)
            rows.append((k, modo.strip(), rest.strip()))
        elif " - " in s:
            modo, rest = s.split(" - ", 1)
            rows.append((k, modo.strip(), rest.strip()))
        else:
            rows.append((k, s[:36] + ("…" if len(s) > 36 else ""), s))
    bk = str(back_key).strip()
    rows.append((bk, "voltar", "menu principal"))
    return rows


def _menu_resume_two_lines(text: str, line_width: int) -> str:
    """quebra o resumo em exatamente 2 linhas (ascii); ellipsis se nao couber tudo."""
    text = " ".join((text or "").split())
    if not text:
        return "\n "
    w = max(12, int(line_width))
    wrapped = textwrap.wrap(text, width=w, break_long_words=True, break_on_hyphens=False)
    if not wrapped:
        return "\n "
    if len(wrapped) == 1:
        return f"{wrapped[0]}\n "
    first, second = wrapped[0], wrapped[1]
    if len(wrapped) > 2:
        room = max(1, w - 3)
        second = (second[:room] + "...") if len(second) > room else (second + "...")
    return f"{first}\n{second}"


def render_menu_table_plain(rows: Sequence[MenuRow], title: str = "opcoes") -> None:
    """imprime o mesmo layout logico do menu principal (fallback sem rich)."""
    print()
    print(f"  {title}")
    print("  " + "-" * 56)
    for key, titulo, desc in rows:
        desc2 = _menu_resume_two_lines(desc, 52)
        print(f"  [{key}]  {titulo}")
        for ln in desc2.splitlines():
            print(f"       {ln}")
        print()


def render_menu_table_rich(console: Any, rows: Sequence[MenuRow], title: str = "opcoes") -> None:
    """tabela principal do wizard: # | modo | | resumo (mesmo estilo que menu inicial)."""
    if not _HAS_RICH:
        render_menu_table_plain(rows, title=title)
        return
    table = Table(
        box=box.ROUNDED,
        show_header=True,
        show_lines=True,
        header_style="bold rgb(240,212,168)",
        border_style="rgb(95,25,35)",
        expand=True,
        pad_edge=True,
        title=title,
        title_style="wizard.muted",
    )
    table.add_column(
        "#",
        justify="center",
        style="wizard.accent",
        width=4,
        no_wrap=True,
    )
    table.add_column(
        "modo",
        style="bold default",
        min_width=24,
        max_width=36,
        no_wrap=True,
        overflow="ellipsis",
    )
    table.add_column(
        "",
        justify="center",
        style="wizard.muted",
        width=1,
        no_wrap=True,
    )
    table.add_column(
        "resumo",
        style="wizard.muted",
        ratio=1,
        no_wrap=False,
        overflow="fold",
    )
    term_w = int(getattr(console, "width", None) or 80)
    resume_w = max(16, term_w - 52)
    for key, titulo, desc in rows:
        desc_cell = _menu_resume_two_lines(desc, resume_w)
        table.add_row(key, titulo, "|", desc_cell)
    console.print()
    console.print(table)
    console.print()


def _wizard_prompt_session() -> Any:
    """sessao prompt_toolkit: historico, tab em atalhos comuns, sugestao do historico."""
    return PromptSession(
        history=InMemoryHistory(),
        completer=WordCompleter(
            [
                "?",
                "*",
                "h",
                "c",
                "cancelar",
                "n",
                "p",
                "s",
                "sim",
                "nao",
            ],
            ignore_case=True,
        ),
        auto_suggest=AutoSuggestFromHistory(),
        enable_history_search=True,
        complete_while_typing=False,
        multiline=False,
    )


def _parse_float_or(value: str, fallback: float) -> float:
    try:
        return float(str(value).strip())
    except Exception:
        return fallback


def _format_number_for_prompt(x: float) -> str:
    # mantem legivel e estavel: sem notacao cientifica "surpresa"
    if abs(x) >= 1e6 or (abs(x) > 0 and abs(x) < 1e-4):
        return f"{x:.6g}"
    s = f"{x:.10f}".rstrip("0").rstrip(".")
    return s if s else "0"


def _clamp(x: float, min_val: Optional[float], max_val: Optional[float]) -> float:
    if min_val is not None and x < min_val:
        return min_val
    if max_val is not None and x > max_val:
        return max_val
    return x


def _number_prompt_key_bindings(
    *,
    step: float,
    big_step: float,
    min_val: Optional[float],
    max_val: Optional[float],
) -> Any:
    kb = KeyBindings()

    def set_buffer(event: Any, new_value: float) -> None:
        v = _clamp(new_value, min_val, max_val)
        buf = event.app.current_buffer
        buf.text = _format_number_for_prompt(v)
        buf.cursor_position = len(buf.text)

    @kb.add("left")
    def _dec(event: Any) -> None:
        cur = _parse_float_or(event.app.current_buffer.text, 0.0)
        set_buffer(event, cur - step)

    @kb.add("right")
    def _inc(event: Any) -> None:
        cur = _parse_float_or(event.app.current_buffer.text, 0.0)
        set_buffer(event, cur + step)

    @kb.add("c-left")
    def _dec_big(event: Any) -> None:
        cur = _parse_float_or(event.app.current_buffer.text, 0.0)
        set_buffer(event, cur - big_step)

    @kb.add("c-right")
    def _inc_big(event: Any) -> None:
        cur = _parse_float_or(event.app.current_buffer.text, 0.0)
        set_buffer(event, cur + big_step)

    @kb.add("home")
    def _to_min(event: Any) -> None:
        if min_val is not None:
            set_buffer(event, min_val)

    @kb.add("end")
    def _to_max(event: Any) -> None:
        if max_val is not None:
            set_buffer(event, max_val)

    return kb


_WIZARD_THEME = Theme(
    {
        "wizard.chrome": "bold white on rgb(95,25,35)",
        "wizard.path": "dim italic",
        "wizard.path_seg": "bold rgb(240,212,168)",
        "wizard.accent": "bold rgb(240,212,168)",
        "wizard.section": "bold rgb(240,212,168)",
        "wizard.muted": "dim",
        "wizard.hint": "italic dim",
        "wizard.warn": "yellow",
        "wizard.err": "bold red",
        "wizard.ok": "green",
        "wizard.label": "bold",
    }
)


class PlainWizardUi:
    """fallback sem rich — mantem o wizard utilizavel."""

    def __init__(self) -> None:
        self._rich = False
        self._pt_session: Optional[Any] = None

    def clear(self) -> None:
        os.system("cls" if os.name == "nt" else "clear")

    def header(self, title: str, subtitle: str = "") -> None:
        print("=" * 62)
        print(f"  {title}")
        print("=" * 62)
        if subtitle:
            print(f"  {subtitle}")
        print()

    def section(self, title: str) -> None:
        print(f"\n--- {title} ---")

    def breadcrumbs(self, *parts: str) -> None:
        if not parts:
            return
        print("  " + " > ".join(parts))
        print()

    def println(self, *args, **kwargs) -> None:
        print(*args, **kwargs)

    def muted(self, msg: str) -> None:
        print(f"  {msg}")

    def hint(self, msg: str) -> None:
        print(f"  {msg}")

    def warn(self, msg: str) -> None:
        print(f"  aviso: {msg}")

    def err(self, msg: str) -> None:
        print(f"  erro: {msg}")

    def ok(self, msg: str) -> None:
        print(f"  {msg}")

    def param_help(self, lines: Sequence[str]) -> None:
        for line in lines:
            print(f"  {line}")
        print()

    def print_aux_numeric_menu(
        self,
        *,
        n_opt: int,
        has_zero_back: bool,
        help_callback: Optional[Callable[[], None]],
        review_callback: Optional[Callable[[], None]],
        menu_default_index: Optional[int],
    ) -> None:
        for ln in _numeric_menu_aux_lines(
            n_opt=n_opt,
            has_zero_back=has_zero_back,
            help_callback=help_callback,
            review_callback=review_callback,
            menu_default_index=menu_default_index,
        ):
            print(ln)

    def print_aux_internal_prompt(
        self,
        *,
        cancel: bool,
        review: bool,
        require_explicit: bool = False,
        extra_bits: Sequence[str] = (),
    ) -> None:
        for ln in _internal_prompt_aux_lines(
            cancel=cancel,
            review=review,
            require_explicit=require_explicit,
            extra_bits=extra_bits,
        ):
            print(ln)

    def pause(self, msg: str = "pressione enter para continuar...") -> None:
        input(f"\n{msg}")

    def ask_line(self, prompt: str, default: str = "") -> str:
        if _HAS_PROMPT_TOOLKIT:
            if self._pt_session is None:
                self._pt_session = _wizard_prompt_session()
            try:
                return str(self._pt_session.prompt(prompt, default=default)).rstrip()
            except Exception:
                pass
        return input(prompt)

    def ask_number(
        self,
        prompt: str,
        default: str = "",
        *,
        step: float = 1.0,
        big_step: Optional[float] = None,
        min_val: Optional[float] = None,
        max_val: Optional[float] = None,
    ) -> str:
        if _HAS_PROMPT_TOOLKIT:
            if self._pt_session is None:
                self._pt_session = _wizard_prompt_session()
            start = _parse_float_or(default, min_val if min_val is not None else 0.0)
            start = _clamp(start, min_val, max_val)
            if big_step is None:
                big_step = step * 10.0
            try:
                kb = _number_prompt_key_bindings(
                    step=step,
                    big_step=big_step,
                    min_val=min_val,
                    max_val=max_val,
                )
                return str(
                    self._pt_session.prompt(
                        prompt,
                        default=_format_number_for_prompt(start),
                        key_bindings=kb,
                    )
                ).rstrip()
            except Exception:
                pass
        return self.ask_line(prompt, default=default)

    def pick_from_list(
        self,
        caption: str,
        options: List[str],
        menu_default_index: Optional[int] = None,
        help_callback: Optional[Callable[[], None]] = None,
        review_callback: Optional[Callable[[], None]] = None,
        cancel_callback: Optional[Callable[[], None]] = None,
        quit_callback: Optional[Callable[[], None]] = None,
    ) -> str:
        _ = quit_callback
        n = len(options)
        option_rows = _options_to_menu_rows(options)
        has_zero = cancel_callback is not None
        if has_zero:
            menu_rows: List[MenuRow] = [
                ("0", "voltar", "cancela este passo sem escolher uma linha da tabela"),
            ] + option_rows
        else:
            menu_rows = option_rows
        while True:
            print()
            print(caption)
            render_menu_table_plain(menu_rows, title="opcoes")
            print()
            self.print_aux_numeric_menu(
                n_opt=n,
                has_zero_back=has_zero,
                help_callback=help_callback,
                review_callback=review_callback,
                menu_default_index=menu_default_index,
            )
            print()
            try:
                raw = self.ask_line("opcao: ", default="").strip()
                low = raw.lower()
                if low == "h":
                    print()
                    for ln in GLOBAL_KEYS_HINT.splitlines():
                        print(f"  {ln}")
                    print()
                    continue
                if has_zero and (
                    raw == "0"
                    or low
                    in ("c", "q", "cancel", "cancelar", "voltar", "back")
                ):
                    cancel_callback()
                    continue
                if raw == "?" and help_callback:
                    help_callback()
                    continue
                if raw == "*" and review_callback:
                    review_callback()
                    continue
                if not raw:
                    if menu_default_index is None:
                        print(
                            "  aviso: indique um numero da tabela (0 ou c voltar)."
                        )
                        continue
                    return options[menu_default_index]
                idx = int(raw) - 1
                if 0 <= idx < n:
                    return options[idx]
                print(f"  aviso: escolha entre 1 e {n}!")
            except ValueError:
                print("  aviso: digite um numero valido!")

    def confirm(
        self,
        message: str,
        default: bool = True,
        cancel_callback: Optional[Callable[[], None]] = None,
        *,
        allow_empty_default: bool = True,
    ) -> bool:
        default_str = "sim" if default else "nao"
        while True:
            print(message)
            self.print_aux_internal_prompt(
                cancel=cancel_callback is not None,
                review=False,
                require_explicit=not allow_empty_default,
            )
            print()
            value = self.ask_line(f"(s/n) [{default_str}]: ", default="").strip()
            low = value.lower()
            if low == "h":
                print()
                for ln in GLOBAL_KEYS_HINT.splitlines():
                    print(f"  {ln}")
                print()
                continue
            if cancel_callback and low in (
                "c",
                "cancel",
                "cancelar",
                "voltar",
                "back",
                "q",
            ):
                cancel_callback()
                continue
            if not value:
                if allow_empty_default:
                    return default
                print("  aviso: digite s ou n (ou c para cancelar).")
                continue
            value = value.lower()
            if value in ("s", "sim", "y", "yes"):
                return True
            if value in ("n", "nao", "no"):
                return False
            print("  aviso: digite 's' para sim ou 'n' para nao!")

    def render_main_menu(self, rows: Sequence[MenuRow], title: str = "opcoes") -> None:
        render_menu_table_plain(rows, title=title)

    def render_help_section_menu(self, entries: Sequence[Tuple[str, str]], back_key: str = "0") -> None:
        rows = _help_entries_to_menu_rows(entries, back_key)
        render_menu_table_plain(rows, title="secoes de ajuda")
        print(f"  {PICK_LIST_SHORT_HINT}")
        print()

    def render_documentation_page(
        self,
        body: str,
        page_index: int,
        total_pages: int,
        control_hint: str,
    ) -> None:
        print()
        print(f"  --- documentacao  pagina {page_index + 1}/{total_pages} ---")
        print()
        for ln in body.splitlines():
            print(f"  {ln}")
        print()
        print(f"  {control_hint}")
        print()


class RichWizardUi:
    """terminal com paineis, tabelas e prompts alinhados ao estilo web (chrome + conteudo)."""

    def __init__(self) -> None:
        self._rich = True
        self._pt_session: Optional[Any] = None
        # soft_wrap evita quebrar layout em caminhos longos
        self.console = Console(theme=_WIZARD_THEME, highlight=False, soft_wrap=True)

    def clear(self) -> None:
        self.console.clear()

    def header(self, title: str, subtitle: str = "") -> None:
        chrome = Text()
        chrome.append(" bedflow atlas ", style="wizard.chrome")
        chrome.append(" ", style="")
        chrome.append("setup://", style="wizard.path")
        chrome.append("setup-de-parametrizacao", style="wizard.path_seg")
        bar = Panel(
            Align.left(chrome),
            box=box.HEAVY,
            border_style="rgb(95,25,35)",
            padding=(0, 1),
        )
        self.console.print(bar)
        if subtitle:
            self.console.print(Text(subtitle, style="wizard.muted"), end="\n\n")
        else:
            self.console.print()

    def section(self, title: str) -> None:
        self.console.print()
        self.console.print(Rule(Text(title.lower(), style="wizard.section"), style="rgb(95,25,35)"))

    def breadcrumbs(self, *parts: str) -> None:
        if not parts:
            return
        t = Text()
        t.append("setup://", style="wizard.path")
        for i, p in enumerate(parts):
            if i:
                t.append(" / ", style="wizard.muted")
            t.append(p.lower(), style="wizard.path_seg")
        self.console.print(Align.left(t))
        self.console.print()

    def println(self, *args, **kwargs) -> None:
        self.console.print(*args, **kwargs)

    def muted(self, msg: str) -> None:
        self.console.print(Text(msg, style="wizard.muted"))

    def hint(self, msg: str) -> None:
        self.console.print(Text(msg, style="wizard.hint"))

    def warn(self, msg: str) -> None:
        self.console.print(Text(f"aviso: {msg}", style="wizard.warn"))

    def err(self, msg: str) -> None:
        self.console.print(Text(f"erro: {msg}", style="wizard.err"))

    def ok(self, msg: str) -> None:
        self.console.print(Text(msg, style="wizard.ok"))

    def param_help(self, lines: Sequence[str]) -> None:
        body = "\n".join(lines)
        self.console.print(
            Panel(
                body,
                title="ajuda",
                title_align="left",
                border_style="dim",
                box=box.ROUNDED,
                padding=(0, 1),
            )
        )

    def print_aux_numeric_menu(
        self,
        *,
        n_opt: int,
        has_zero_back: bool,
        help_callback: Optional[Callable[[], None]],
        review_callback: Optional[Callable[[], None]],
        menu_default_index: Optional[int],
    ) -> None:
        for ln in _numeric_menu_aux_lines(
            n_opt=n_opt,
            has_zero_back=has_zero_back,
            help_callback=help_callback,
            review_callback=review_callback,
            menu_default_index=menu_default_index,
        ):
            self.console.print(Text(ln, style="wizard.muted"))

    def print_aux_internal_prompt(
        self,
        *,
        cancel: bool,
        review: bool,
        require_explicit: bool = False,
        extra_bits: Sequence[str] = (),
    ) -> None:
        for ln in _internal_prompt_aux_lines(
            cancel=cancel,
            review=review,
            require_explicit=require_explicit,
            extra_bits=extra_bits,
        ):
            self.console.print(Text(ln, style="wizard.muted"))

    def pause(self, msg: str = "pressione enter para continuar...") -> None:
        self.console.input(f"\n[wizard.muted]{msg}[/] ")

    def ask_line(self, prompt: str, default: str = "") -> str:
        plain = escape(prompt) if escape else prompt
        if _HAS_PROMPT_TOOLKIT:
            if self._pt_session is None:
                self._pt_session = _wizard_prompt_session()
            try:
                return str(self._pt_session.prompt(plain, default=default)).rstrip()
            except Exception:
                pass
        return self.console.input(plain)

    def ask_number(
        self,
        prompt: str,
        default: str = "",
        *,
        step: float = 1.0,
        big_step: Optional[float] = None,
        min_val: Optional[float] = None,
        max_val: Optional[float] = None,
    ) -> str:
        plain = escape(prompt) if escape else prompt
        if _HAS_PROMPT_TOOLKIT:
            if self._pt_session is None:
                self._pt_session = _wizard_prompt_session()
            start = _parse_float_or(default, min_val if min_val is not None else 0.0)
            start = _clamp(start, min_val, max_val)
            if big_step is None:
                big_step = step * 10.0
            try:
                kb = _number_prompt_key_bindings(
                    step=step,
                    big_step=big_step,
                    min_val=min_val,
                    max_val=max_val,
                )
                return str(
                    self._pt_session.prompt(
                        plain,
                        default=_format_number_for_prompt(start),
                        key_bindings=kb,
                    )
                ).rstrip()
            except Exception:
                pass
        return self.ask_line(prompt, default=default)

    def pick_from_list(
        self,
        caption: str,
        options: List[str],
        menu_default_index: Optional[int] = None,
        help_callback: Optional[Callable[[], None]] = None,
        review_callback: Optional[Callable[[], None]] = None,
        cancel_callback: Optional[Callable[[], None]] = None,
        quit_callback: Optional[Callable[[], None]] = None,
    ) -> str:
        _ = quit_callback
        n_opt = len(options)
        option_rows = _options_to_menu_rows(options)
        has_zero = cancel_callback is not None
        if has_zero:
            menu_rows: List[MenuRow] = [
                ("0", "voltar", "cancela este passo sem escolher uma linha da tabela"),
            ] + option_rows
        else:
            menu_rows = option_rows
        while True:
            self.console.print()
            self.console.print(Text(caption, style="wizard.label"))
            render_menu_table_rich(self.console, menu_rows, title="opcoes")
            self.console.print()
            self.print_aux_numeric_menu(
                n_opt=n_opt,
                has_zero_back=has_zero,
                help_callback=help_callback,
                review_callback=review_callback,
                menu_default_index=menu_default_index,
            )
            self.console.print()
            raw = self.ask_line("opcao: ", default="").strip()
            low = raw.lower()
            if low == "h":
                for ln in GLOBAL_KEYS_HINT.splitlines():
                    self.console.print(Text(ln, style="wizard.hint"))
                self.console.print()
                continue
            if has_zero and (
                raw == "0"
                or low in ("c", "q", "cancel", "cancelar", "voltar", "back")
            ):
                cancel_callback()
                continue
            if raw == "?" and help_callback:
                help_callback()
                continue
            if raw == "*" and review_callback:
                review_callback()
                continue
            try:
                if not raw:
                    if menu_default_index is None:
                        self.warn("indique um numero da tabela (0 ou c voltar).")
                        continue
                    return options[menu_default_index]
                num = int(raw)
                idx = num - 1
                if 0 <= idx < n_opt:
                    return options[idx]
                self.warn(f"escolha entre 1 e {n_opt}!")
            except (ValueError, TypeError):
                self.warn("digite um numero valido!")

    def confirm(
        self,
        message: str,
        default: bool = True,
        cancel_callback: Optional[Callable[[], None]] = None,
        *,
        allow_empty_default: bool = True,
    ) -> bool:
        default_str = "sim" if default else "nao"
        while True:
            self.console.print(Text(message, style="wizard.label"))
            self.print_aux_internal_prompt(
                cancel=cancel_callback is not None,
                review=False,
                require_explicit=not allow_empty_default,
            )
            self.console.print()
            raw = self.ask_line(f"(s/n) [{default_str}]: ", default="").strip()
            low = raw.lower()
            if low == "h":
                for ln in GLOBAL_KEYS_HINT.splitlines():
                    self.console.print(Text(ln, style="wizard.hint"))
                self.console.print()
                continue
            if cancel_callback and low in (
                "c",
                "cancel",
                "cancelar",
                "voltar",
                "back",
                "q",
            ):
                cancel_callback()
                continue
            if not raw:
                if allow_empty_default:
                    return default
                self.warn("digite s ou n (ou c para cancelar).")
                continue
            v = raw.lower()
            if v in ("s", "sim", "y", "yes"):
                return True
            if v in ("n", "nao", "no"):
                return False
            self.warn("digite 's' para sim ou 'n' para nao!")

    def render_main_menu(self, rows: Sequence[MenuRow], title: str = "opcoes") -> None:
        render_menu_table_rich(self.console, rows, title=title)

    def render_help_section_menu(self, entries: Sequence[Tuple[str, str]], back_key: str = "0") -> None:
        rows = _help_entries_to_menu_rows(entries, back_key)
        render_menu_table_rich(self.console, rows, title="secoes de ajuda")
        self.console.print(Text(PICK_LIST_SHORT_HINT, style="wizard.hint"))
        self.console.print()

    def render_documentation_page(
        self,
        body: str,
        page_index: int,
        total_pages: int,
        control_hint: str,
    ) -> None:
        title = f"documentacao — pagina {page_index + 1}/{total_pages}"
        self.console.print(
            Panel(
                body,
                title=title,
                title_align="left",
                border_style="dim",
                box=box.ROUNDED,
                padding=(0, 1),
            )
        )
        self.console.print(Text(control_hint, style="wizard.hint"))


def make_terminal_ui():
    if _HAS_RICH:
        return RichWizardUi()
    return PlainWizardUi()


def rich_available() -> bool:
    return _HAS_RICH


def prompt_toolkit_available() -> bool:
    return _HAS_PROMPT_TOOLKIT
