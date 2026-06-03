#!/usr/bin/env python3
"""
gera o icone (.ico) usado pelo atalho da area de trabalho do bed wizard.

a partir do logo do projeto (frontend/image/logoCFDpipeline.png), compoe o
desenho preto sobre um fundo branco arredondado e exporta um .ico multi-resolucao
(16..256 px) em tools/desktop/bed_wizard.ico.

uso:
    python tools/desktop/gerar_icone.py
"""
from __future__ import annotations

from pathlib import Path

from PIL import Image, ImageDraw

# pastas de referencia
_HERE = Path(__file__).resolve().parent          # tools/desktop
_REPO = _HERE.parent.parent                       # raiz do repo
_SRC = _REPO / "frontend" / "image" / "logoCFDpipeline.png"
_OUT = _HERE / "bed_wizard.ico"

# parametros do desenho
_CANVAS = 256          # tamanho base do icone em px
_PAD = 26              # margem entre o logo e a borda do canvas
_RADIUS = 46           # raio dos cantos arredondados do fundo
_BG = (255, 255, 255, 255)   # fundo branco opaco (visivel em qualquer tema)
_SIZES = [(16, 16), (24, 24), (32, 32), (48, 48), (64, 64), (128, 128), (256, 256)]


def gerar() -> Path:
    if not _SRC.is_file():
        raise FileNotFoundError(f"logo de origem nao encontrado: {_SRC}")

    logo = Image.open(_SRC).convert("RGBA")

    # redimensionar o logo preservando proporcao para caber no canvas com margem
    max_lado = _CANVAS - 2 * _PAD
    w, h = logo.size
    escala = min(max_lado / w, max_lado / h)
    nova = (max(1, int(w * escala)), max(1, int(h * escala)))
    logo = logo.resize(nova, Image.LANCZOS)

    # fundo branco com cantos arredondados
    mascara = Image.new("L", (_CANVAS, _CANVAS), 0)
    ImageDraw.Draw(mascara).rounded_rectangle(
        [0, 0, _CANVAS - 1, _CANVAS - 1], radius=_RADIUS, fill=255
    )
    fundo = Image.composite(
        Image.new("RGBA", (_CANVAS, _CANVAS), _BG),
        Image.new("RGBA", (_CANVAS, _CANVAS), (0, 0, 0, 0)),
        mascara,
    )

    # colar o logo centralizado, respeitando a transparencia
    ox = (_CANVAS - logo.width) // 2
    oy = (_CANVAS - logo.height) // 2
    fundo.alpha_composite(logo, (ox, oy))

    fundo.save(_OUT, sizes=_SIZES)
    return _OUT


if __name__ == "__main__":
    destino = gerar()
    print(f"icone gerado: {destino}")
