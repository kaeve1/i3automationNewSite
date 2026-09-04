# -*- coding: utf-8 -*-
"""Desenha a previa do braco a partir do JSON de previa_braco.js.

Rasteriza com o mesmo par de cores do site (linha #9FBEE0 sobre o navy do
heroi #001D3D) para que o que se ve aqui seja o que o navegador vai mostrar.

Uso: python ferramentas/previa_braco.py [giro] [inclinacao] [fase] [saida.png]
"""
import json
import subprocess
import sys
import os

from PIL import Image, ImageDraw

RAIZ = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
FUNDO = (0, 29, 61)
LINHA = (159, 190, 224)
ACESO = (253, 197, 0)
ESCALA = 2          # supersampling: linha de 1 px nao se julga em tela cheia


def render(giro=2.40, incl=0.16, fase=0.22, saida=None, larg=430, alt=584,
           dist=0, alvo_y=0, calado=False, ponteiro=None, corte=None):
    """larg/alt sao a moldura REAL do heroi: min(34vw, 430px) em 729/991."""
    js = subprocess.run(
        ["node", os.path.join(RAIZ, "ferramentas", "previa_braco.js"),
         str(giro), str(incl), str(fase), str(larg), str(alt),
         str(dist), str(alvo_y)],
        capture_output=True, text=True, cwd=RAIZ)
    if js.returncode != 0:
        print(js.stderr)
        raise SystemExit(js.returncode)
    d = json.loads(js.stdout)

    # Enquadramento medido, nao estimado: a caixa do desenho projetado contra
    # a caixa do slot. Sobra grande em cima e a peca "flutua"; negativo e corte.
    xs = [v for s in d["segs"] if s[4] > .05 for v in (s[0], s[2])]
    ys = [v for s in d["segs"] if s[4] > .05 for v in (s[1], s[3])]
    cx0, cx1, cy0, cy1 = min(xs), max(xs), min(ys), max(ys)
    if not calado:
        print("  caixa do desenho  x %.0f..%.0f de %d   y %.0f..%.0f de %d"
              % (cx0, cx1, d["larg"], cy0, cy1, d["alt"]))
        print("  preenchimento     %.0f%% da largura, %.0f%% da altura   "
              "distancia %.1f" % (100 * (cx1 - cx0) / d["larg"],
                                  100 * (cy1 - cy0) / d["alt"], d["dist"]))
        print("  folga             esq %.0f  dir %.0f  topo %.0f  base %.0f"
              % (cx0, d["larg"] - cx1, cy0, d["alt"] - cy1))

    W, H = int(d["larg"]) * ESCALA, int(d["alt"]) * ESCALA
    im = Image.new("RGB", (W, H), FUNDO)
    dr = ImageDraw.Draw(im, "RGBA")
    # `ponteiro` reproduz a lente do fragment shader por SEGMENTO (o shader faz
    # por fragmento). Serve para julgar a leitura do dourado, nao para medir.
    # `corte` reproduz a troca de folha do shader: abaixo dele a peca esta sobre
    # a secao clara, e a tinta vira navy com ganho maior. Em fracao da ALTURA,
    # medida do topo do canvas -- igual ao que medirCorte() calcula.
    if corte is not None:
        dr.rectangle((0, corte * H, W, H), fill=(255, 255, 255))
        dr.line((0, corte * H, W, corte * H), fill=(0, 0, 0, 36))
    for x0, y0, x1, y1, a, larg in d["segs"]:
        cor, ganho = LINHA, 1.0
        if corte is not None and (y0 + y1) / 2 > corte * d["alt"]:
            cor, ganho = (0, 53, 102), 1.15
        if ponteiro:
            px, py = ponteiro[0] * d["larg"], ponteiro[1] * d["alt"]
            raio = 0.30 * d["alt"]
            mx, my = (x0 + x1) / 2, (y0 + y1) / 2
            r = ((mx - px) ** 2 + (my - py) ** 2) ** .5 / raio
            rev = max(0.0, min(1.0, 1 - (r - .80) / .24))
            rev = rev * rev * (3 - 2 * rev)
            cor = tuple(int(LINHA[i] + (ACESO[i] - LINHA[i]) * rev) for i in range(3))
            ganho = 1 + rev * .42
            t = (r - .94) * 20
            banda = 2.718 ** (-t * t)
            if banda > .35:
                cor = ACESO
                ganho = max(ganho, 1.2)
        al = max(0, min(255, int(a * ganho * 255)))
        if al <= 2:
            continue
        dr.line((x0 * ESCALA, y0 * ESCALA, x1 * ESCALA, y1 * ESCALA),
                fill=cor + (al,), width=max(1, round(larg * ESCALA)))
    im = im.resize((int(d["larg"]), int(d["alt"])), Image.LANCZOS)
    saida = saida or os.path.join(RAIZ, "ferramentas", "_previa_braco.png")
    im.save(saida)
    print("%d segmentos, raio %.1f -> %s" % (d["segmentos"], d["raio"], saida))
    return saida


if __name__ == "__main__":
    a = sys.argv[1:]
    render(float(a[0]) if len(a) > 0 else 2.40,
           float(a[1]) if len(a) > 1 else 0.16,
           float(a[2]) if len(a) > 2 else 0.22,
           a[3] if len(a) > 3 else None)
