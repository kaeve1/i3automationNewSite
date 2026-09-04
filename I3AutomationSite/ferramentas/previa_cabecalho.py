# -*- coding: utf-8 -*-
"""Monta o CABECALHO de who-we-are fora do navegador.

Nao e um motor de layout. Refaz a aritmetica do CSS -- container centrado e
limitado, padding lateral, a banda vertical entre `nav-altura + s-7` e `s-8`,
e a reserva da coluna da marca -- e desenha a peca 3D REAL por cima, com
previa_marca. E o suficiente para responder as duas perguntas que so a
composicao responde:

  1. a marca colide com o texto?
  2. ela esta no tamanho certo em relacao ao h1?

Os retangulos de texto sao CAIXAS, nao tipografia: o que se julga aqui e
ocupacao e colisao. Para julgar a tipografia existe specs/tipografia.html.

Uso: python ferramentas/previa_cabecalho.py [largura] [altura]
"""
import os
import sys

from PIL import Image, ImageDraw

import previa_marca

RAIZ = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

NAVY = (0, 29, 61)          # --navy-fundo
DOURADO = (253, 197, 0)     # --dourado
BRANCO = (255, 255, 255)


def espacos(w):
    """--pad-lateral e --nav-altura mudam por media query."""
    if w <= 767:
        return 20, 64
    if w <= 1023:
        return 32, 80
    return 48, 96


def marca_larg(w):
    """clamp(220px, 26vw, 380px)"""
    return max(220, min(380, 0.26 * w))


def montar(W=1440, H=620, saida=None):
    pad, nav = espacos(W)
    S6, S7, S8 = 48, 64, 96
    CONTAINER = 1376

    # a caixa do container, centrada e limitada
    cw = min(W, CONTAINER)
    cx0 = (W - cw) / 2 + pad
    cx1 = (W + cw) / 2 - pad

    # a banda vertical do conteudo: padding-top = nav + s-7, padding-bottom = s-8
    topo = nav + S7
    base = H - S8

    im = Image.new("RGB", (W, H), NAVY)
    dr = ImageDraw.Draw(im, "RGBA")

    # SEM FOTOGRAFIA desde 19/08: navy chapado. A reticula entra como a grade
    # de 96 e 24 px do CSS, com a mascara radial em 34%/78% -- sob o titulo,
    # deixando o lado da marca em navy limpo.
    import math
    for passo, alfa in ((96, 0.07), (24, 0.028)):
        for x in range(0, W, passo):
            for y in range(0, H, 2):
                dx, dy = (x - 0.34 * W) / (1.20 * W), (y - 0.78 * H) / (0.90 * H)
                m = max(0.0, min(1.0, 1 - (math.hypot(dx, dy) - 0.20) / 0.58))
                if m > 0:
                    dr.point((x, y), fill=(255, 255, 255, int(255 * alfa * m)))
        for y in range(0, H, passo):
            for x in range(0, W, 2):
                dx, dy = (x - 0.34 * W) / (1.20 * W), (y - 0.78 * H) / (0.90 * H)
                m = max(0.0, min(1.0, 1 - (math.hypot(dx, dy) - 0.20) / 0.58))
                if m > 0:
                    dr.point((x, y), fill=(255, 255, 255, int(255 * alfa * m)))

    tem_marca = W > 1023
    ml = marca_larg(W) if tem_marca else 0
    # `.cabecalho--marca .container { padding-right: pad + larg + s-6 }`
    tx1 = cx1 - (ml + S6) if tem_marca else cx1

    # ---- as caixas de texto, na ordem e nas alturas do CSS ----
    fs_h1 = max(40, min(88, 0.064 * W))          # clamp(2.5rem, 6.4vw, 5.5rem)
    fs_lead = max(20, min(28, 0.0146 * W))       # --fs-lead
    linhas_h1 = 2                                 # o <br> do titulo
    alt_h1 = linhas_h1 * fs_h1 * 0.98
    alt_lead = 2 * fs_lead * 1.36
    blocos = [("eyebrow", 15, 0), ("h1", alt_h1, 16),
              ("lead", alt_lead, 24), ("trilha", 15, 32)]
    total = sum(a + m for _, a, m in blocos)
    y = base - total
    inicio_texto = y
    caixas = []
    for nome, a, m in blocos:
        y += m
        caixas.append((nome, y, y + a))
        y += a

    for nome, y0, y1 in caixas:
        cor = DOURADO if nome == "eyebrow" else BRANCO
        larg = tx1 - cx0
        if nome == "h1":
            larg = min(larg, 18 * fs_h1 * 0.55)     # max-width: 18ch
        elif nome == "lead":
            larg = min(larg, 46 * fs_lead * 0.5)    # max-width: 46ch
        dr.rectangle((cx0, y0, cx0 + larg, y1), fill=cor + (52,),
                     outline=cor + (150,))

    # ---- a peca 3D, desenhada de verdade ----
    if tem_marca:
        mh = base - topo
        png = previa_marca.render(saida=os.path.join(
            RAIZ, "ferramentas", "_previa_marca_tmp.png"),
            larg=int(ml), alt=int(mh), calado=True)
        peca = Image.open(png).convert("RGB")
        # o canvas e transparente sobre o cabecalho; aqui a previa ja vem com o
        # navy de fundo, entao clareia por diferenca para nao dobrar o fundo
        base_img = Image.new("RGB", peca.size, NAVY)
        mask = Image.eval(Image.merge("L", [
            Image.eval(peca.convert("L"), lambda v: v)]), lambda v: v)
        im.paste(peca, (int(cx1 - ml), int(topo)), mask)
        os.remove(png)

    dr.line((cx0, 0, cx0, H), fill=(255, 255, 255, 26))
    dr.line((cx1, 0, cx1, H), fill=(255, 255, 255, 26))
    if tem_marca:
        dr.line((cx1 - ml, 0, cx1 - ml, H), fill=(253, 197, 0, 40))
        dr.line((tx1, 0, tx1, H), fill=(253, 197, 0, 40))

    folga = (cx1 - ml) - (cx0 + min(tx1 - cx0, 18 * fs_h1 * 0.55))
    print("%dx%d  container %.0f..%.0f  banda y %.0f..%.0f" % (W, H, cx0, cx1, topo, base))
    print("  marca      %.0f px de largura, coluna x %.0f..%.0f"
          % (ml, cx1 - ml, cx1))
    print("  h1         teto %.0f px (18ch a %.0f px), texto ate x %.0f"
          % (min(tx1 - cx0, 18 * fs_h1 * 0.55), fs_h1, tx1))
    print("  FOLGA entre o fim do h1 e o inicio da marca: %.0f px" % folga)
    print("  texto y %.0f..%.0f   marca y %.0f..%.0f" % (inicio_texto, base, topo, base))

    saida = saida or os.path.join(RAIZ, "ferramentas", "_previa_cabecalho.png")
    im.save(saida)
    print("-> %s" % saida)
    return saida


if __name__ == "__main__":
    a = sys.argv[1:]
    montar(int(a[0]) if a else 1440, int(a[1]) if len(a) > 1 else 620)
