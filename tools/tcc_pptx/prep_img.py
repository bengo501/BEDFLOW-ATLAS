#!/usr/bin/env python3
"""prepara imagens recortadas (aspecto apresentavel) para o deck do TCC."""
import shutil
from pathlib import Path
from PIL import Image

ROOT = Path(__file__).resolve().parents[2]
WEB = ROOT / "generated" / "prints_web"
TERM = ROOT / "generated" / "prints_terminal"
OUT = Path(__file__).resolve().parent / "img"
OUT.mkdir(exist_ok=True)


def crop(src, name, box):
    im = Image.open(src)
    im.crop(box).save(OUT / name)
    print("crop", name, im.crop(box).size)


def top(src, name, ratio=0.58):
    im = Image.open(src)
    w, h = im.size
    ch = min(h, int(w * ratio))
    im.crop((0, 0, w, ch)).save(OUT / name)
    print("top ", name, (w, ch))


def copyim(src, name):
    shutil.copy(src, OUT / name)
    print("copy", name)


# web — recorte do topo (cabecalho + conteudo principal)
for n, r in [("W1_dashboard", 0.60), ("W2_wizard_geometria", 0.62),
             ("W10_monitoramento_jobs", 0.62), ("W11_detalhe_execucao", 0.58),
             ("W12_banco_de_dados", 0.66), ("W13_relatorios", 0.66),
             ("W14_configuracoes", 0.42), ("W15_perfil", 0.66),
             ("W5_templates_editor", 0.62)]:
    top(WEB / f"{n}.png", f"{n}.png", r)

# web viewer 3d / corte — janela com o modelo
crop(WEB / "W8_visualizador_3d.png", "W8_visualizador_3d.png", (0, 150, 2048, 1780))
crop(WEB / "W9_visualizador_corte.png", "W9_visualizador_corte.png", (0, 150, 2048, 1780))

# reprodutibilidade — viewer com modelo + metadados (1a viewport)
for n in ["R1a_mesma_seed_hashA", "R1b_mesma_seed_hashB",
          "R2a_seed_diferente_hashA", "R2b_seed_diferente_hashB"]:
    crop(WEB / f"{n}.png", f"{n}.png", (0, 120, 2048, 1640))

# sidecar / download e terminal — ja tem bom aspecto
for n in ["R3_sidecar_json", "R4_download_stl"]:
    copyim(WEB / f"{n}.png", f"{n}.png")
for n in ["T1_menu_principal", "T2_wizard_interativo", "T3_arquivo_bed",
          "T4_compile_ok", "T5_compile_erro", "T6_geracao_3d",
          "T7_arvore_artefatos", "T8_corte_3d", "T9_open3d_leito_completo"]:
    copyim(TERM / f"{n}.png", f"{n}.png")

# logos
copyim(ROOT / "generated" / "apresentacao_sic" / "logo_proj_branco.png", "logo_proj.png")
copyim(ROOT / "generated" / "apresentacao_sic" / "template_imgs" / "p7_Image33.png", "logo_pucrs.png")
print("OK img em", OUT)
