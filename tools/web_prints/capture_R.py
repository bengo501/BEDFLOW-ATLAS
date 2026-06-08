#!/usr/bin/env python3
"""
captura prints R1-R4 (reprodutibilidade / sidecar / download) do BEDFLOW-ATLAS.

gera malhas pela propria app (wizard "Criar basico", motor python_engine,
empacotamento spherical_packing) com seeds controladas e captura:
  R1a/R1b  duas execucoes de MESMA seed -> hashes SHA-256 identicos (viewer 3d)
  R2a/R2b  duas execucoes de seeds DIFERENTES -> hashes distintos (viewer 3d)
  R3       conteudo do sidecar JSON (geometry_mode, seed, hash, porosity_result)
  R4       download do STL + confirmacao do arquivo recebido localmente

pre-requisitos (ja rodando):
  backend  http://127.0.0.1:8000   (uvicorn app.main:app, repo backend/)
  frontend http://localhost:5173   (npm --prefix frontend run dev)

uso:
  python tools/web_prints/capture_R.py            # tudo (gera + captura)
  python tools/web_prints/capture_R.py --gen-only # so gera as malhas
  python tools/web_prints/capture_R.py --shots-only  # so captura (malhas ja geradas)
saida: generated/prints_web/Rxx_*.png
"""
from __future__ import annotations

import sys
import time
import json
import urllib.request
from pathlib import Path

from playwright.sync_api import sync_playwright

FRONT = "http://localhost:5173"
BACK = "http://127.0.0.1:8000"
ROOT = Path(__file__).resolve().parents[2]
OUT = ROOT / "generated" / "prints_web"
OUT.mkdir(parents=True, exist_ok=True)

# nome base -> (fileName no wizard, seed). prefixo zzR_ para achar facil e nao colidir.
GENS = [
    ("zzR_seed42_a", 42),
    ("zzR_seed42_b", 42),
    ("zzR_seed7", 7),
]


def _settle(page, ms=600):
    page.wait_for_timeout(ms)


def js(page, expr):
    return page.evaluate(f"(()=>{{ {expr} }})()")


def api_get(path):
    with urllib.request.urlopen(f"{BACK}{path}", timeout=30) as r:
        return json.loads(r.read().decode("utf-8"))


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


def nav(page, label):
    js(page, (
        "const want=" + repr(label.lower()) + ";"
        "const b=[...document.querySelectorAll('nav button, aside button')]"
        ".find(x=>((x.getAttribute('aria-label')||x.title||x.textContent||'').trim().toLowerCase())===want);"
        "if(b)b.click();"
    ))
    _settle(page, 800)


def _step_text(page):
    return page.evaluate(
        "(()=>{const m=document.querySelector('main');"
        "return (m&&m.textContent.match(/passo\\s*\\d+\\s*de\\s*\\d+/i)||[''])[0];})()"
    )


def _next(page):
    js(page, "const b=[...document.querySelectorAll('main button')].find(x=>/^pr[oó]ximo$/i.test((x.textContent||'').trim())); b&&b.click();")
    _settle(page, 500)


def _select_by_option(page, option_value):
    """seleciona, no <select> que possua a option dada, esse valor (React-friendly)."""
    page.evaluate(
        "(val)=>{const s=[...document.querySelectorAll('main select')]"
        ".find(se=>[...se.options].some(o=>o.value===val)); if(!s)return false;"
        "const setter=Object.getOwnPropertyDescriptor(window.HTMLSelectElement.prototype,'value').set;"
        "setter.call(s,val); s.dispatchEvent(new Event('input',{bubbles:true}));"
        "s.dispatchEvent(new Event('change',{bubbles:true})); return true;}",
        option_value,
    )
    _settle(page, 300)


def _set_input_by_id(page, el_id, value):
    ok = page.evaluate(
        "(args)=>{const [eid,val]=args; const i=document.getElementById(eid);"
        "if(!i)return false; const setter=Object.getOwnPropertyDescriptor(window.HTMLInputElement.prototype,'value').set;"
        "setter.call(i,String(val)); i.dispatchEvent(new Event('input',{bubbles:true}));"
        "i.dispatchEvent(new Event('change',{bubbles:true})); return i.value;}",
        [el_id, value],
    )
    _settle(page, 250)
    return ok


def _set_filename(page, name):
    page.evaluate(
        "(val)=>{const labels=[...document.querySelectorAll('main label')];"
        "const lab=labels.find(l=>/nome do arquivo/i.test(l.textContent||''));"
        "let i=lab&&lab.parentElement?lab.parentElement.querySelector('input'):null;"
        "if(!i)i=[...document.querySelectorAll('main input[type=text]')].find(x=>/leito|\\.bed|meu_/i.test(x.value||''));"
        "if(!i)return false; const setter=Object.getOwnPropertyDescriptor(window.HTMLInputElement.prototype,'value').set;"
        "setter.call(i,val); i.dispatchEvent(new Event('input',{bubbles:true}));"
        "i.dispatchEvent(new Event('change',{bubbles:true})); return true;}",
        name,
    )
    _settle(page, 250)


def generate_one(page, file_name, seed):
    """dirige o wizard 'Criar basico' ate gerar .bed + modelo 3d (motor python)."""
    print(f"  gerando {file_name} (seed={seed})...")
    nav(page, "criação")
    # clicar card "Criar basico"
    js(page, "const c=[...document.querySelectorAll('.mode-card')].find(x=>/criar basico/i.test((x.querySelector('h3')||{}).textContent||'')); c&&c.click();")
    page.wait_for_function("/passo 1 de/.test(document.querySelector('main')?.textContent||'')", timeout=8000)
    _settle(page, 400)

    # passo 1 (geometria) -> 2 (tampas) -> 3 (particulas)
    _next(page); _next(page)
    assert "passo 3" in _step_text(page).lower(), f"esperava passo 3, veio {_step_text(page)}"
    r_part = _set_input_by_id(page, "particles-seed", seed)

    # -> 4 (empacotamento): spherical_packing (deterministico) + SEED de empacotamento
    _next(page)
    assert "passo 4" in _step_text(page).lower(), f"esperava passo 4, veio {_step_text(page)}"
    _select_by_option(page, "spherical_packing")
    _settle(page, 400)
    r_pack = _set_input_by_id(page, "packing-random-seed", seed)
    print(f"      seeds setadas -> particles:{r_part} packing:{r_pack}")
    assert str(r_pack) == str(seed), f"falha ao setar packing seed (veio {r_pack})"

    # -> 5 (geometria e motor): full_3d + python_engine
    _next(page)
    assert "passo 5" in _step_text(page).lower(), f"esperava passo 5, veio {_step_text(page)}"
    _select_by_option(page, "full_3d")
    _select_by_option(page, "python_engine")

    # -> 6 (export) -> 7 (cfd) -> 8 (confirmacao)
    _next(page); _next(page); _next(page)
    assert "passo 8" in _step_text(page).lower(), f"esperava passo 8, veio {_step_text(page)}"
    _set_filename(page, file_name)
    _settle(page, 300)

    # clicar "gerar .bed" (dispara confirm gerar-3d + alert; dialogs auto-aceitos)
    js(page, "const b=[...document.querySelectorAll('main button')].find(x=>/gerar \\.bed/i.test((x.textContent||'').trim())); b&&b.click();")
    _settle(page, 2500)  # compila .bed + confirm + generateModel(job) + alert


def _gen_jobs():
    try:
        d = api_get("/api/jobs?limit=80")
        j = d if isinstance(d, list) else (d.get("jobs") or [])
        return [x for x in j if x.get("job_type") == "generate_model"]
    except Exception:
        return []


def wait_for_new_job(prev_ts, timeout=90):
    """espera um generate_model criado apos prev_ts concluir; retorna o job."""
    t0 = time.time()
    while time.time() - t0 < timeout:
        novos = [x for x in _gen_jobs() if x.get("created_at", "") > prev_ts]
        done = [x for x in novos if x.get("status") == "completed"]
        if done:
            done.sort(key=lambda x: x.get("created_at", ""))
            return done[-1]
        time.sleep(1.5)
    return None


def mesh_id_for_stl(stl_basename, timeout=20):
    """encontra o mesh_id no inventario do viewer pelo nome do .stl gerado."""
    t0 = time.time()
    while time.time() - t0 < timeout:
        try:
            data = api_get("/api/viewer/meshes?limit=300")
            for m in data["meshes"]:
                if m["filename"] == stl_basename and m.get("content_hash"):
                    return m
        except Exception:
            pass
        time.sleep(1.5)
    return None


def open_ready_page(ctx):
    page = ctx.new_page()
    page.on("dialog", lambda d: d.accept())
    page.goto(FRONT, wait_until="domcontentloaded")
    page.wait_for_timeout(2200)
    close_user_modal(page)
    force_light(page)
    close_user_modal(page)
    return page


def _latest_job_ts():
    jobs = _gen_jobs()
    return max((x.get("created_at", "") for x in jobs), default="")


def do_generations(ctx):
    results = {}
    page = open_ready_page(ctx)
    for file_name, seed in GENS:
        # reset para o hub limpo entre geracoes
        nav(page, "dashboard"); _settle(page, 600)
        prev_ts = _latest_job_ts()
        generate_one(page, file_name, seed)
        job = wait_for_new_job(prev_ts)
        if not job:
            print(f"    [ERRO] {file_name}: job de geracao nao concluiu")
            results[file_name] = None
            continue
        md = job.get("metadata", {})
        stl = (md.get("stl_path") or "").replace("\\", "/").split("/")[-1]
        info = mesh_id_for_stl(stl) or {}
        rec = {
            "file_name": file_name,
            "seed": seed,
            "stl": stl,
            "mesh_id": info.get("mesh_id"),
            "content_hash": md.get("content_hash") or info.get("content_hash"),
            "geometry_mode": md.get("geometry_mode") or info.get("geometry_mode"),
            "particles_seed": md.get("particles_seed"),
            "packing_random_seed": md.get("packing_random_seed"),
            "porosity_result": info.get("porosity_result"),
            "sidecar_json": info.get("sidecar_json"),
        }
        results[file_name] = rec
        print(f"    OK {stl}  hash={(rec['content_hash'] or '')[:16]}  seed={seed}  gm={rec['geometry_mode']}  eps={rec['porosity_result']}  mesh_id={rec['mesh_id']}")
    page.wait_for_timeout(800)
    return results


def shot(page, name, full_page=True):
    p = OUT / f"{name}.png"
    page.screenshot(path=str(p), full_page=full_page)
    print(f"  salvo: {p.name}")
    return p


def _meta_file(page):
    """le o valor do campo 'ficheiro' no painel DADOS DO MODELO (malha carregada)."""
    return page.evaluate(
        "()=>{const dts=[...document.querySelectorAll('.mesh-viewer-sidebar dt, .mesh-viewer-meta dt, dl dt')];"
        "const dt=dts.find(d=>/^ficheiro$/i.test((d.textContent||'').trim()));"
        "if(dt&&dt.nextElementSibling)return (dt.nextElementSibling.textContent||'').trim();"
        "return '';}"
    )


def load_mesh_in_viewer(page, mesh_id, stl_basename):
    """abre o viewer ja apontando para a malha via ?meshViewerId (auto-carrega)."""
    page.goto(f"{FRONT}/?meshViewerId={mesh_id}", wait_until="domcontentloaded")
    page.wait_for_timeout(2500)
    close_user_modal(page)
    force_light(page)
    close_user_modal(page)
    # espera carregar terminar e o painel mostrar o hash
    try:
        page.wait_for_function(
            "!/a carregar/i.test([...document.querySelectorAll('main button')].map(b=>b.textContent).join(''))",
            timeout=25000,
        )
    except Exception:
        pass
    try:
        page.wait_for_function(
            "()=>{const dts=[...document.querySelectorAll('dl dt')];"
            "return dts.some(d=>/^hash$/i.test((d.textContent||'').trim()));}",
            timeout=12000,
        )
    except Exception:
        pass
    got = _meta_file(page)
    if stl_basename not in got:
        print(f"      [aviso] painel mostra '{got}', esperado {stl_basename}")
    else:
        print(f"      painel OK: {got}")
    # fundo claro + repor camara para um shot limpo
    js(page, "const f=[...document.querySelectorAll('main input[type=checkbox]')].find(c=>/fundo claro/i.test((c.closest('label')||c.parentElement||{}).textContent||'')); if(f&&!f.checked)f.click(); const r=[...document.querySelectorAll('main button')].find(x=>/repor c[âa]mara/i.test(x.textContent||'')); r&&r.click();")
    _settle(page, 1800)


def capture_r1_r2(ctx, results):
    plan = [
        ("R1a_mesma_seed_hashA", "zzR_seed42_a"),
        ("R1b_mesma_seed_hashB", "zzR_seed42_b"),
        ("R2a_seed_diferente_hashA", "zzR_seed42_a"),
        ("R2b_seed_diferente_hashB", "zzR_seed7"),
    ]
    for shot_name, key in plan:
        rec = results.get(key)
        if not rec or not rec.get("stl"):
            print(f"  [skip] {shot_name}: sem malha para {key}")
            continue
        print(f"  {shot_name} <- {rec['stl']} (seed {rec['seed']}, hash {(rec['content_hash'] or '')[:12]})")
        page = ctx.new_page()  # pagina fresca = contexto WebGL limpo
        page.on("dialog", lambda d: d.accept())
        load_mesh_in_viewer(page, rec["mesh_id"], rec["stl"])
        shot(page, shot_name)
        page.close()


def capture_r3_sidecar(ctx, results):
    """renderiza o conteudo real do sidecar JSON (geometry_mode, seed, hash, porosity)."""
    page = ctx.new_page()
    rec = results.get("zzR_seed42_a") or next((v for v in results.values() if v and v.get("sidecar_json")), None)
    if not rec:
        print("  [skip] R3: sem registro")
        return
    # localizar o ficheiro sidecar no disco
    sc_name = rec.get("sidecar_json") or (rec["stl"].replace(".stl", "") + "_pure_bed.json")
    candidates = list(ROOT.rglob(sc_name))
    if not candidates:
        print(f"  [skip] R3: sidecar {sc_name} nao encontrado")
        return
    data = json.loads(candidates[0].read_text(encoding="utf-8"))
    # ordem amigavel: campos-chave primeiro
    seed = data.get("packing_random_seed", data.get("particles_seed"))
    porosity = data.get("porosity_result", data.get("porosity_estimate"))
    ordered = {
        "geometry_mode": data.get("geometry_mode"),
        "seed": seed,
        "packing_random_seed": data.get("packing_random_seed"),
        "particles_seed": data.get("particles_seed"),
        "content_hash": data.get("content_hash"),
        "porosity_result": porosity,
        "generation_backend": data.get("generation_backend"),
        "packing_method": data.get("packing_method"),
        "n_spheres_placed": data.get("n_spheres_placed"),
        "modeling_profile": data.get("modeling_profile"),
        "job_id": data.get("job_id"),
    }
    pretty = json.dumps(ordered, indent=2, ensure_ascii=False)
    highlight = {"geometry_mode", "seed", "content_hash", "porosity_result"}
    rows = []
    for line in pretty.split("\n"):
        key = line.strip().split(":")[0].strip().strip('"')
        cls = "hl" if key in highlight else ""
        rows.append(f'<div class="ln {cls}">{line.replace("<","&lt;")}</div>')
    html = (
        "<!doctype html><meta charset=utf-8><body style='margin:0;background:#0f1117;display:inline-block;'>"
        "<div id='card' style='font-family:Consolas,\"JetBrains Mono\",monospace;color:#e6e6e6;"
        "padding:28px 34px;font-size:16px;line-height:1.55;display:inline-block;'>"
        "<div style='color:#9aa4b2;font-size:13px;margin-bottom:14px;letter-spacing:.5px;'>"
        f"sidecar &middot; {sc_name}</div>"
        "<style>.ln{white-space:pre} .hl{background:#23314a;border-left:3px solid #4f86f7;"
        "padding-left:8px;margin-left:-11px;border-radius:3px}</style>"
        + "".join(rows) + "</div></body>"
    )
    page.set_content(html)
    _settle(page, 500)
    try:
        page.locator("#card").screenshot(path=str(OUT / "R3_sidecar_json.png"))
        print("  salvo: R3_sidecar_json.png")
    except Exception:
        shot(page, "R3_sidecar_json", full_page=True)
    page.close()


def _open_modelos3d(page):
    nav(page, "dashboard"); _settle(page, 400)
    js(page, "const h=[...document.querySelectorAll('.nav-section-header')].find(x=>/hist[oó]rico/i.test(x.textContent||'')); if(h&&(h.textContent||'').includes('+'))h.click();")
    _settle(page, 500)
    js(page, "const h=[...document.querySelectorAll('.nav-section-header')].find(x=>/resultados/i.test(x.textContent||'')); if(h&&(h.textContent||'').includes('+'))h.click();")
    _settle(page, 500)
    js(page, "const b=[...document.querySelectorAll('nav button, aside button')].find(x=>/modelos 3d/i.test((x.textContent||'').trim())); if(b)b.click();")
    _settle(page, 1200)


def capture_r4_download(ctx, results):
    import hashlib
    page = open_ready_page(ctx)
    rec = results.get("zzR_seed42_a") or next((v for v in results.values() if v and v.get("stl")), None)
    if not rec:
        print("  [skip] R4: sem registro")
        return
    stl = rec["stl"]
    _open_modelos3d(page)
    # filtrar pela malha
    try:
        sb = page.locator("main input").first
        sb.click(); sb.fill(""); sb.type(stl.replace(".stl", ""), delay=25)
    except Exception:
        pass
    _settle(page, 1800)
    # garante que a linha da malha esta visivel (scroll ate o primeiro 'baixar')
    js(page, "const b=[...document.querySelectorAll('main button')].find(x=>/^baixar$|download/i.test((x.textContent||'').trim())); if(b)b.scrollIntoView({block:'center'});")
    _settle(page, 500)
    page_png = OUT / "_r4_page.png"
    page.screenshot(path=str(page_png), full_page=False)  # viewport: tela unica

    # download real via mesh-stream (FileResponse com Content-Disposition: attachment),
    # mesmo ficheiro servido pelo botao 'baixar' do dashboard
    dl_dir = OUT / "downloads"; dl_dir.mkdir(exist_ok=True)
    saved = dl_dir / stl
    urls = [
        f"{BACK}/api/viewer/mesh-stream?mesh_id={rec.get('mesh_id')}",
        f"{BACK}/files/models_3d/{stl}",
    ]
    ok = False
    for url in urls:
        try:
            with urllib.request.urlopen(url, timeout=60) as r:
                saved.write_bytes(r.read())
            if saved.stat().st_size > 0:
                ok = True
                print(f"      download via {url.split('?')[0]} ok")
                break
        except Exception as exc:
            print(f"  [aviso] download via {url.split('?')[0]} falhou: {str(exc)[:80]}")
    size_kb = saved.stat().st_size / 1024 if ok else 0
    sha = hashlib.sha256(saved.read_bytes()).hexdigest() if ok else ""
    match = (sha == rec.get("content_hash"))
    print(f"  R4 download: {saved}  {size_kb:.1f} KB  sha256 confere: {match}")

    # figura composta: screenshot da pagina (botao baixar) + banner de confirmacao
    import base64
    b64 = base64.b64encode(page_png.read_bytes()).decode("ascii")
    banner = (
        f"<div style='display:flex;gap:14px;align-items:center;background:#10331f;"
        f"border:1px solid #2e7d4f;border-radius:10px;padding:16px 20px;margin:0 0 16px 0;"
        f"font-family:Consolas,monospace;color:#d7f5e2;font-size:15px;'>"
        f"<span style='font-size:26px;color:#36d77a;'>&#10003;</span>"
        f"<div><b>STL recebido no sistema de arquivos local</b><br>"
        f"<span style='color:#9fe3bd'>arquivo:</span> generated/prints_web/downloads/{stl} "
        f"&nbsp;&middot;&nbsp; <span style='color:#9fe3bd'>tamanho:</span> {size_kb:.1f} KB<br>"
        f"<span style='color:#9fe3bd'>sha-256:</span> {sha[:48]}…<br>"
        f"<span style='color:#9fe3bd'>confere com content_hash do sidecar:</span> "
        f"<b style='color:{'#36d77a' if match else '#ff6b6b'}'>{'SIM' if match else 'NAO'}</b></div></div>"
    )
    html = (
        "<!doctype html><meta charset=utf-8><body style='margin:0;background:#0f1117;padding:24px;'>"
        "<div style='font-family:Segoe UI,Arial,sans-serif;color:#e6e6e6;max-width:1180px;margin:0 auto;'>"
        "<div style='font-size:18px;font-weight:600;margin-bottom:14px;'>Download do STL via dashboard &rarr; uso em solver externo</div>"
        + banner +
        f"<img src='data:image/png;base64,{b64}' style='width:100%;border-radius:10px;border:1px solid #2a2f3a;'>"
        "</div></body>"
    )
    page.set_content(html)
    _settle(page, 500)
    shot(page, "R4_download_stl", full_page=True)


def main():
    args = set(sys.argv[1:])
    gen_only = "--gen-only" in args
    shots_only = "--shots-only" in args
    with sync_playwright() as p:
        browser = p.chromium.launch()
        ctx = browser.new_context(viewport={"width": 1024, "height": 768}, device_scale_factor=2, accept_downloads=True)

        if shots_only:
            results = json.loads((OUT / "_R_results.json").read_text(encoding="utf-8"))
        else:
            print("abrindo o frontend / gerando malhas...")
            results = do_generations(ctx)
            (OUT / "_R_results.json").write_text(json.dumps(results, indent=2, ensure_ascii=False), encoding="utf-8")
            print("\nresultados salvos em generated/prints_web/_R_results.json")
            if gen_only:
                browser.close()
                return

        only_r4 = "--r4" in args
        if not only_r4:
            print("\ncapturando R1/R2 (viewer 3d)...")
            capture_r1_r2(ctx, results)
            print("\ncapturando R3 (sidecar json)...")
            capture_r3_sidecar(ctx, results)
        print("\ncapturando R4 (download stl)...")
        try:
            capture_r4_download(ctx, results)
        except Exception as exc:
            print(f"  [erro] R4: {str(exc)[:160]}")

        browser.close()
        print(f"\nprints em: {OUT}")


if __name__ == "__main__":
    main()
