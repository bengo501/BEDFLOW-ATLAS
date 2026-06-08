#!/usr/bin/env python3
"""
captura prints do fluxo web do BEDFLOW-ATLAS via Playwright e salva PNGs.

pre-requisitos (ja rodando):
  - backend:  http://127.0.0.1:8000   (uvicorn backend.app.main:app, SEED_DEMO_DATA=1)
  - frontend: http://localhost:5173   (npm --prefix frontend run dev)

uso:
  python tools/web_prints/capture_flows.py            # todos
  python tools/web_prints/capture_flows.py W1 W12 ... # subset
saida: generated/prints_web/Wxx_*.png  (tema claro, full-page @2x)
"""
from __future__ import annotations

import sys
from pathlib import Path

from playwright.sync_api import sync_playwright

FRONT = "http://localhost:5173"
OUT = Path(__file__).resolve().parents[2] / "generated" / "prints_web"
OUT.mkdir(parents=True, exist_ok=True)


def _settle(page, ms=600):
    page.wait_for_timeout(ms)


def js(page, expr):
    return page.evaluate(f"(()=>{{ {expr} }})()")


def close_user_modal(page):
    try:
        btn = page.get_by_role("button", name="fechar")
        if btn.count() and btn.first.is_visible():
            btn.first.click()
            _settle(page, 300)
    except Exception:
        pass


def force_light(page):
    try:
        for _ in range(2):
            light = page.get_by_role("button", name="toggle light mode")
            if light.count() and light.first.is_visible():
                light.first.click()
                _settle(page, 300)
            else:
                break
    except Exception:
        pass


NAV = {0: "dashboard", 1: "criação", 2: "visualização 3d",
       3: "banco de dados", 4: "perfil", 5: "configurações"}


def nav(page, key):
    """navega por ROTULO do item (robusto ao acordeao, que muda indices)."""
    name = NAV.get(key, key) if isinstance(key, int) else key
    js(page, (
        "const want=" + repr(name) + ".toLowerCase();"
        "const b=[...document.querySelectorAll('nav button.nav-item, nav button, aside button')]"
        ".find(x=>((x.getAttribute('aria-label')||x.title||x.textContent||'').trim().toLowerCase())===want);"
        "if(b)b.click();"
    ))
    _settle(page, 800)


def open_section(page, word):
    """abre UMA secao da sidebar (acordeao: abrir uma fecha as outras)."""
    js(page, f"const h=[...document.querySelectorAll('.nav-section-header')].find(x=>/{word}/i.test(x.textContent||'')); if(h && (h.textContent||'').includes('+')) h.click();")
    _settle(page, 600)


def click_subitem(page, pattern):
    js(page, (
        "const t=[...document.querySelectorAll('button,a,[role=button]')]"
        ".filter(e=>!e.classList.contains('nav-section-header') && !e.querySelector('.nav-section-title'))"
        f".find(e=>{pattern}.test((e.textContent||'').trim()));"
        "if(t)t.click();"
    ))
    _settle(page, 1000)


def click_regex(page, pattern, scope="button,a,[role=button],.nav-subitem,li"):
    """clica o primeiro elemento (nao-header) cujo texto casa o regex js."""
    js(page, (
        f"const els=[...document.querySelectorAll({scope!r})]"
        ".filter(e=>!e.classList.contains('nav-section-header') && !e.querySelector('.nav-section-title'));"
        f"const t=els.find(e=>{pattern}.test((e.textContent||'').trim()));"
        "if(t)t.click();"
    ))
    _settle(page, 900)


def shot(page, name, full_page=True):
    p = OUT / f"{name}.png"
    page.screenshot(path=str(p), full_page=full_page)
    print(f"  salvo: {p.name}")
    return p


# --------------------------------------------------------------------------- #
def w1_dashboard(page):
    nav(page, 0)
    _settle(page, 900)
    shot(page, "W1_dashboard")


def _open_wizard(page):
    nav(page, 1)  # Criação
    _settle(page, 500)
    page.click(".mode-card")  # Criar basico
    page.wait_for_function("/passo 1 de/.test(document.querySelector('main')?.textContent||'')", timeout=8000)
    _settle(page, 500)


def _next(page):
    js(page, "const b=[...document.querySelectorAll('button')].find(x=>/^próximo$/i.test((x.textContent||'').trim())); b&&b.click();")
    _settle(page, 500)


def w2_w3_w4_wizard(page):
    """abre o wizard uma vez e captura os passos geometria(1)/particulas(3)/empacotamento(4)."""
    _open_wizard(page)
    shot(page, "W2_wizard_geometria")        # passo 1
    _next(page); _next(page)                 # -> passo 3 particulas
    shot(page, "W3_wizard_particulas")
    _next(page)                              # -> passo 4 empacotamento
    shot(page, "W4_wizard_empacotamento")


def w2(page):
    w2_w3_w4_wizard(page)


def w3(page):
    pass  # capturado em W2 (mesma sessao do wizard)


def w4(page):
    pass  # capturado em W2 (mesma sessao do wizard)


def w5_templates(page):
    nav(page, 0)  # garante estado limpo (sai do wizard/viewer)
    _settle(page, 500)
    open_section(page, "templates")
    click_subitem(page, "/^templates$/i")  # subitem "templates" (editor)
    shot(page, "W5_templates_editor")


def _load_viewer_model(page, filt):
    nav(page, 2)  # Visualizacao 3D
    _settle(page, 900)
    sb = page.locator("main input").first
    sb.click(); sb.fill(""); sb.press_sequentially(filt, delay=70)
    try:
        page.wait_for_function(
            "(f)=>new RegExp('leito_'+f).test(document.querySelector('main')?.textContent||'')",
            arg=filt, timeout=6000,
        )
    except Exception:
        pass
    _settle(page, 500)
    js(page, f"const it=[...document.querySelectorAll('main *')].find(e=>new RegExp('leito_{filt}').test(e.textContent||'') && getComputedStyle(e).cursor==='pointer'); it&&it.click();")
    _settle(page, 500)
    js(page, "const b=[...document.querySelectorAll('main button')].find(x=>/carregar modelo/i.test(x.textContent||'')); b&&b.click();")
    try:
        page.wait_for_function("!/a carregar/i.test([...document.querySelectorAll('main button')].map(b=>b.textContent).join(''))", timeout=12000)
    except Exception:
        pass
    _settle(page, 1200)
    js(page, "const f=[...document.querySelectorAll('main input[type=checkbox]')].find(c=>/fundo claro/i.test((c.closest('label')||c.parentElement||{}).textContent||'')); if(f&&!f.checked)f.click(); const r=[...document.querySelectorAll('main button')].find(x=>/repor câmara/i.test(x.textContent||'')); r&&r.click();")
    _settle(page, 1800)


def w8_viewer(page):
    _load_viewer_model(page, "2026052")
    shot(page, "W8_visualizador_3d")


def w9_slice(page):
    # carrega um modelo de corte 2d (thin slice). filtro tenta nomes de slice.
    _load_viewer_model(page, "slice")
    shot(page, "W9_visualizador_corte")


def w10_jobs(page):
    nav(page, 0)
    _settle(page, 500)
    open_section(page, "histórico")
    click_subitem(page, "/jobs\\s*\\(\\d+\\)/i")
    shot(page, "W10_monitoramento_jobs")


def _open_jobs(page):
    nav(page, 0); _settle(page, 400)
    open_section(page, "histórico")
    click_subitem(page, "/jobs\\s*\\(\\d+\\)/i")
    _settle(page, 800)


def w6_job_running(page):
    """captura o monitoramento com um job em execucao (disparado via API antes)."""
    _open_jobs(page)
    _settle(page, 700)
    shot(page, "W6_job_running")


def w7_job_done(page):
    _open_jobs(page)
    js(page, "const t=[...document.querySelectorAll('main *')].find(e=>getComputedStyle(e).cursor==='pointer' && /(completed|conclu)/i.test(e.textContent||'') && /(Modelo 3D|leito)/i.test(e.textContent||'')); t&&t.click();")
    _settle(page, 1600)
    shot(page, "W7_job_done")


def w11_detalhe(page):
    # detalhe de execucao: dashboard -> botao 'detalhes' de uma simulacao
    nav(page, 0); _settle(page, 800)
    js(page, "const b=[...document.querySelectorAll('main button')].find(x=>/^detalhes$/i.test((x.textContent||'').trim())); b&&b.click();")
    _settle(page, 1500)
    shot(page, "W11_detalhe_execucao")


def w12_database(page):
    nav(page, 3)  # banco de dados
    _settle(page, 900)
    shot(page, "W12_banco_de_dados")


def w13_relatorios(page):
    nav(page, 0)
    _settle(page, 500)
    open_section(page, "análises")
    click_subitem(page, "/^relatórios$/i")
    shot(page, "W13_relatorios")


def w14_config(page):
    nav(page, 5)  # configurações
    _settle(page, 900)
    shot(page, "W14_configuracoes")


def w15_perfil(page):
    nav(page, 4)  # perfil
    _settle(page, 900)
    shot(page, "W15_perfil")


SHOTS = {
    "W1": w1_dashboard, "W2": w2, "W3": w3, "W4": w4, "W5": w5_templates,
    "W6": w6_job_running, "W7": w7_job_done, "W8": w8_viewer, "W9": w9_slice,
    "W10": w10_jobs, "W11": w11_detalhe, "W12": w12_database,
    "W13": w13_relatorios, "W14": w14_config, "W15": w15_perfil,
}


def main():
    want = [a.upper() for a in sys.argv[1:]] or list(SHOTS)
    with sync_playwright() as p:
        browser = p.chromium.launch()
        ctx = browser.new_context(viewport={"width": 1024, "height": 768}, device_scale_factor=2)
        page = ctx.new_page()
        print("abrindo o frontend...")
        page.goto(FRONT, wait_until="domcontentloaded")
        page.wait_for_timeout(2500)
        close_user_modal(page); force_light(page); close_user_modal(page)
        for key in want:
            fn = SHOTS.get(key)
            if not fn:
                continue
            print(f"capturando {key}...")
            try:
                fn(page)
            except Exception as exc:
                print(f"  [erro] {key}: {str(exc)[:120]}")
        browser.close()
    print(f"\nprints em: {OUT}")


if __name__ == "__main__":
    main()
