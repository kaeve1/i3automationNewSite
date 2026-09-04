# -*- coding: utf-8 -*-
"""Desenha a previa da marca extrudada a partir do JSON de previa_marca.js.

Rasteriza com o par de cores REAL do site (traco #9FBEE0 e tela #FDC500 sobre
o navy do cabecalho #001D3D), para que o que se ve aqui seja o que o navegador
vai mostrar. A conta de alfa e a mesma do fragment shader.

Uso: python ferramentas/previa_marca.py [giro] [incl] [saida.png]
"""
import json
import os
import subprocess
import sys

from PIL import Image, ImageDraw

RAIZ = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
FUNDO = (0, 29, 61)      # --navy-fundo, o chao do cabecalho nos dois temas
LINHA = (159, 190, 224)  # --marca-traco
OURO = (253, 197, 0)     # --marca-ouro / --marca-aceso
ESCALA = 2               # supersampling: linha de 1 px nao se julga em tela cheia


def render(giro=-0.62, incl=0.18, saida=None, larg=340, alt=412,
           ponteiro=None, calado=False):
    """larg/alt sao a moldura REAL: clamp(200px,23vw,340px) por 620-144-64."""
    js = subprocess.run(
        ["node", os.path.join(RAIZ, "ferramentas", "previa_marca.js"),
         str(giro), str(incl), str(larg), str(alt)],
        capture_output=True, text=True, cwd=RAIZ)
    if js.returncode != 0:
        print(js.stderr)
        raise SystemExit(js.returncode)
    d = json.loads(js.stdout)

    xs = [v for s in d["segs"] for v in (s[0], s[2])]
    ys = [v for s in d["segs"] for v in (s[1], s[3])]
    if not calado:
        print("  elementos lidos   %s" % ", ".join(d["elementos"]))
        print("  caixa do desenho  x %.0f..%.0f de %d   y %.0f..%.0f de %d"
              % (min(xs), max(xs), d["larg"], min(ys), max(ys), d["alt"]))
        print("  preenchimento     %.0f%% da largura, %.0f%% da altura   "
              "distancia %.2f" % (100 * (max(xs) - min(xs)) / d["larg"],
                                  100 * (max(ys) - min(ys)) / d["alt"], d["dist"]))
        print("  folga             esq %.0f  dir %.0f  topo %.0f  base %.0f"
              % (min(xs), d["larg"] - max(xs), min(ys), d["alt"] - max(ys)))

    W, H = int(d["larg"]) * ESCALA, int(d["alt"]) * ESCALA
    im = Image.new("RGB", (W, H), FUNDO)
    dr = ImageDraw.Draw(im, "RGBA")
    # `ponteiro` reproduz a lente do fragment shader por SEGMENTO (o shader faz
    # por fragmento). Serve para julgar a leitura do dourado, nao para medir.
    for x0, y0, x1, y1, a, larg_l, tinta in d["segs"]:
        cor = OURO if tinta > .5 else LINHA
        ganho = 1.0
        if ponteiro:
            px, py = ponteiro[0] * d["larg"], ponteiro[1] * d["alt"]
            raio = 0.30 * d["alt"]
            mx, my = (x0 + x1) / 2, (y0 + y1) / 2
            r = ((mx - px) ** 2 + (my - py) ** 2) ** .5 / raio
            rev = max(0.0, min(1.0, 1 - (r - .80) / .24))
            rev = rev * rev * (3 - 2 * rev)
            cor = tuple(int(cor[i] + (OURO[i] - cor[i]) * rev) for i in range(3))
            ganho = 1 + rev * .42
        al = max(0, min(255, int(a * ganho * 255)))
        if al <= 2:
            continue
        dr.line((x0 * ESCALA, y0 * ESCALA, x1 * ESCALA, y1 * ESCALA),
                fill=cor + (al,), width=max(1, round(larg_l * ESCALA)))
    im = im.resize((int(d["larg"]), int(d["alt"])), Image.LANCZOS)
    saida = saida or os.path.join(RAIZ, "ferramentas", "_previa_marca.png")
    im.save(saida)
    if not calado:
        print("%d segmentos, raio %.2f -> %s" % (d["segmentos"], d["raio"], saida))
    return saida


if __name__ == "__main__":
    a = sys.argv[1:]
    render(float(a[0]) if len(a) > 0 else -0.62,
           float(a[1]) if len(a) > 1 else 0.18,
           a[2] if len(a) > 2 else None)
