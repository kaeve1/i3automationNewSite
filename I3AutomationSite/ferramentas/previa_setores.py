# -*- coding: utf-8 -*-
"""Monta o PAINEL PRESO de past-performance fora do navegador.

Nao e um motor de layout. Refaz a aritmetica do CSS -- container centrado e
limitado, banda vertical `100svh - nav`, grade 7fr/5fr, placa de 440 px -- e
desenha a fotografia REAL na placa. Responde as tres perguntas que so a
composicao responde:

  1. o texto do setor cabe na altura da janela, com os dados?
  2. a placa e a coluna de texto se equilibram?
  3. os controles cabem embaixo sem espremer o conteudo?

Os retangulos de texto sao CAIXAS, nao tipografia: aqui se julga ocupacao e
transbordo. Para julgar tipografia existe specs/tipografia.html.

Uso: python ferramentas/previa_setores.py [largura] [altura]
"""
import os
import sys

from PIL import Image, ImageDraw

RAIZ = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
NAVY = (0, 29, 61)
DOURADO = (253, 197, 0)
BRANCO = (255, 255, 255)


def espacos(w):
    if w <= 767:
        return 20, 64
    if w <= 1023:
        return 32, 80
    return 48, 96


def montar(W=1440, H=900, saida=None):
    pad, nav = espacos(W)
    S2, S3, S4, S6, S7, S8 = 8, 16, 24, 48, 64, 96
    CONTAINER = 1376
    alt_painel = H - nav                      # height: calc(100svh - nav)

    cw = min(W, CONTAINER)
    cx0 = (W - cw) / 2 + pad
    cx1 = (W + cw) / 2 - pad
    largura_util = cx1 - cx0

    empilha = W <= 1023
    if empilha:
        col_txt = largura_util
        placa = min(260, largura_util)
    else:
        # grid 7fr / 5fr com gap s-8
        livre = largura_util - S8
        col_txt = livre * 7 / 12
        col_placa = livre * 5 / 12
        placa = min(440, col_placa)

    im = Image.new("RGB", (W, H), NAVY)
    dr = ImageDraw.Draw(im, "RGBA")
    dr.rectangle((0, 0, W, nav), fill=(0, 20, 42))
    dr.line((0, nav, W, nav), fill=(255, 255, 255, 40))

    # ---- alturas do conteudo, na ordem do CSS ----
    fs_h2 = max(28, min(44, 0.023 * W))
    fs_corpo = max(16, min(20, 0.0104 * W))
    fs_small = 17
    n_dados = 3                               # o setor mais denso: agua
    alt_h2 = 2 * fs_h2 * 1.05
    alt_corpo = 3 * fs_corpo * 1.5
    alt_linha = S3 * 2 + 2 * fs_small * 1.5   # padding-block s-3 + 2 linhas
    alt_dados = n_dados * alt_linha
    blocos = [("eyebrow", 15, 0), ("h2", alt_h2, S3),
              ("corpo", alt_corpo, S4), ("dados", alt_dados, S6)]
    alt_texto = sum(a + m for _, a, m in blocos)
    alt_controles = 48 + S7                   # setas 48px + margin-top s-7

    if empilha:
        alt_conteudo = placa + S4 + alt_texto + alt_controles
    else:
        alt_conteudo = max(alt_texto, placa) + alt_controles

    # o palco e centrado verticalmente na banda do painel
    topo = nav + max(0, (alt_painel - alt_conteudo) / 2)

    # ---- desenha ----
    y = topo
    if empilha:
        dr.rectangle((cx0, y, cx0 + placa, y + placa), outline=(255, 255, 255, 120))
        y += placa + S4
    for nome, a, m in blocos:
        y += m
        cor = DOURADO if nome == "eyebrow" else BRANCO
        larg = col_txt
        if nome == "h2":
            larg = min(larg, 14 * fs_h2 * 0.55)
        elif nome == "corpo":
            larg = min(larg, 46 * fs_corpo * 0.5)
        dr.rectangle((cx0, y, cx0 + larg, y + a), fill=cor + (48,),
                     outline=cor + (150,))
        if nome == "dados":
            for k in range(1, n_dados):
                yy = y + k * alt_linha
                dr.line((cx0, yy, cx0 + larg, yy), fill=(255, 255, 255, 60))
        y += a
    fim_texto = y

    if not empilha:
        py = topo + max(0, (max(alt_texto, placa) - placa) / 2)
        px = cx1 - placa
        try:
            foto = Image.open(os.path.join(
                RAIZ, "site", "img", "galeria", "captacao-600.jpg")).convert("RGB")
            foto = foto.resize((int(placa), int(placa)), Image.LANCZOS)
            im.paste(foto, (int(px), int(py)))
        except Exception:
            dr.rectangle((px, py, px + placa, py + placa), fill=(0, 8, 20))
        dr.rectangle((px, py, px + placa, py + placa), outline=(255, 255, 255, 110))
        dr.line((px, py, px + 26, py), fill=DOURADO, width=2)
        dr.line((px, py, px, py + 26), fill=DOURADO, width=2)
        fim_placa = py + placa
    else:
        fim_placa = topo + placa

    # controles
    cy = max(fim_texto, fim_placa) + S7
    for k in range(6):
        x = cx0 + k * (34 + S2)
        cor = DOURADO if k == 0 else (255, 255, 255, 112)
        dr.rectangle((x, cy + 16, x + 34, cy + 18 + (2 if k else 2)),
                     fill=cor if k == 0 else (255, 255, 255, 112))
    for k, x in enumerate((cx1 - 48 - S4 - 48, cx1 - 48)):
        dr.rectangle((x, cy, x + 48, cy + 48), outline=(255, 255, 255, 115))
    fim = cy + 48

    dr.line((cx0, 0, cx0, H), fill=(255, 255, 255, 22))
    dr.line((cx1, 0, cx1, H), fill=(255, 255, 255, 22))
    dr.line((0, nav + alt_painel - 1, W, nav + alt_painel - 1), fill=(253, 197, 0, 70))

    folga = (nav + alt_painel) - fim
    print("%dx%d  nav %d  painel y %d..%d (%d px)" % (W, H, nav, nav, nav + alt_painel,
                                                      alt_painel))
    print("  coluna de texto %.0f px   placa %.0f px" % (col_txt, placa))
    print("  conteudo %.0f px (texto %.0f + controles %.0f)"
          % (alt_conteudo, alt_texto, alt_controles))
    print("  conteudo ocupa y %.0f..%.0f" % (topo, fim))
    print("  FOLGA ate o fim do painel: %.0f px  %s"
          % (folga, "OK" if folga >= 0 else "TRANSBORDA"))

    saida = saida or os.path.join(RAIZ, "ferramentas", "_previa_setores.png")
    im.save(saida)
    print("-> %s" % saida)
    return folga


if __name__ == "__main__":
    a = sys.argv[1:]
    montar(int(a[0]) if a else 1440, int(a[1]) if len(a) > 1 else 900)
