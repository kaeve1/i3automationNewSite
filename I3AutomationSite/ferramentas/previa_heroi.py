# -*- coding: utf-8 -*-
"""Monta o heroi inteiro FORA do navegador, para conferir composicao.

Nao e um motor de layout: reproduz a mesma aritmetica que o CSS faz -- grade de
12 colunas, container centrado com max-width, a peca na coluna 7..12 alinhada
ao fim, altura em % da linha do texto e o deslocamento de 8%. Serve para
responder "a peca esta onde o exemplo pede?" sem abrir o Chrome.

Uso: python ferramentas/previa_heroi.py [largura] [altura]
"""
import os
import subprocess
import sys

from PIL import Image, ImageDraw, ImageFont

RAIZ = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, os.path.join(RAIZ, 'ferramentas'))
import previa_braco as PB

NAVY = (0, 29, 61)
BRANCO = (255, 255, 255)
DOURADO = (253, 197, 0)
AZUL = (159, 190, 224)

CONTAINER = 1280
PAD = 32
NAV = 72
PB_BAIXO = 96          # padding-bottom do heroi (--s-8)


def fonte(tam, negrito=False):
    for nome in ('outfit-latin.woff2',):
        pass
    for cam in (r'C:\Windows\Fonts\segoeuil.ttf', r'C:\Windows\Fonts\segoeui.ttf',
                r'C:\Windows\Fonts\arial.ttf'):
        if os.path.exists(cam):
            return ImageFont.truetype(cam, tam)
    return ImageFont.load_default()


def montar(W=1368, H=768, saida=None, lente=None):
    im = Image.new('RGB', (W, H), NAVY)
    d = ImageDraw.Draw(im, 'RGBA')

    # grade de fundo do heroi (96 e 24 px)
    for p, a in ((24, 7), (96, 18)):
        for x in range(0, W, p):
            d.line((x, 0, x, H), fill=(255, 255, 255, a))
        for y in range(0, H, p):
            d.line((0, y, W, y), fill=(255, 255, 255, a))

    cont_x0 = max(PAD, (W - CONTAINER) // 2 + PAD)
    cont_x1 = W - cont_x0
    col = (cont_x1 - cont_x0) / 12.0

    # --- alturas do bloco de texto, na mesma ordem do CSS ---
    fs_h1 = max(36, min(76, int(W * 0.052)))
    lh_h1 = int(fs_h1 * 1.02)
    fs_apoio = max(16, min(21, int(W * 0.0145)))
    marca_h, marca_gap = int(fs_h1 * 1.05), 32
    h1_h = lh_h1 * 5
    apoio_h = int(fs_apoio * 1.36) * 3
    texto_h = marca_h + marca_gap + h1_h + 32 + apoio_h

    rodape_h = 52 + 96                      # conteudo + margin-top --s-8
    texto_y1 = H - PB_BAIXO - rodape_h
    texto_y0 = texto_y1 - texto_h
    centro = (texto_y0 + texto_y1) / 2

    # --- a peca: coluna 7..12, justify-self:end, margin-right negativa ---
    peca_w = min(int(W * 0.62), 900)
    # top: -14% / bottom: -46% da linha do texto  ->  altura 1,60x, subindo 14%
    peca_h = int(texto_h * 1.60)
    peca_x1 = cont_x1 + PAD + int(W * 0.06)
    peca_x0 = peca_x1 - peca_w
    peca_y0 = int(texto_y0 - 0.14 * texto_h)

    js = subprocess.run(
        ['node', os.path.join(RAIZ, 'ferramentas', 'previa_braco.js'),
         '2.40', '0.16', '0.22', str(peca_w), str(peca_h), '0', '0'],
        capture_output=True, text=True, cwd=RAIZ)
    import json
    dados = json.loads(js.stdout)
    corte = 1 - 0  # o heroi acaba depois da peca nesta janela
    for x0, y0, x1, y1, a, larg in dados['segs']:
        al = max(0, min(255, int(a * 255)))
        if al <= 2:
            continue
        d.line((peca_x0 + x0, peca_y0 + y0, peca_x0 + x1, peca_y0 + y1),
               fill=AZUL + (al,), width=max(1, round(larg)))

    # --- texto ---
    y = texto_y0
    d.rectangle((cont_x0, y + 6, cont_x0 + marca_h * 1.55, y + marca_h),
                fill=DOURADO)
    d.rectangle((cont_x0, y + marca_h + 4, cont_x0 + marca_h * 1.55, y + marca_h + 9),
                fill=BRANCO)
    d.text((cont_x0 + marca_h * 1.55 + 14, y + marca_h * .30),
           'AUTOMATIONS\n& CONTROLS', font=fonte(int(fs_h1 * .21)),
           fill=(255, 255, 255, 184))
    y += marca_h + marca_gap
    for linha in ('Good control', 'strategy', 'beats more', 'expensive',
                  'instrumentation.'):
        d.text((cont_x0, y), linha, font=fonte(fs_h1), fill=BRANCO)
        y += lh_h1
    y += 32
    d.rectangle((cont_x0, y + 4, cont_x0 + 2, y + apoio_h - 4), fill=DOURADO)
    for linha in ('Control panels, PLC and SCADA integration, in-',
                  'strumentation and commissioning. Lakewood',
                  'Ranch, Florida — in the field since 2000.'):
        d.text((cont_x0 + 22, y), linha, font=fonte(fs_apoio),
               fill=(255, 255, 255, 200))
        y += int(fs_apoio * 1.36)

    # --- rodape ---
    ry = H - PB_BAIXO - 52
    d.line((cont_x0, ry, cont_x1, ry), fill=(255, 255, 255, 46))
    d.text((cont_x0, ry + 18), 'Industrial automation integration',
           font=fonte(13), fill=(255, 255, 255, 184))
    d.text((cont_x0 + 300, ry + 18), 'Federal contractor · UEI XUZ4WKEZLS67',
           font=fonte(13), fill=(255, 255, 255, 184))
    d.text((cont_x0 + 640, ry + 18), 'Drag the arm to orbit · the pointer lights the drawing',
           font=fonte(13), fill=(255, 255, 255, 184))

    # A LENTE: mesma do site -- raio 252 px, dourado cheio ate 77% dele. Como
    # o CSS recorta o gradiente na forma das letras, aqui basta compor o mesmo
    # gradiente sobre uma COPIA dourada do que ja foi desenhado, mascarada pelo
    # que nao e fundo. Nao e o mecanismo do navegador, e o mesmo resultado.
    if lente:
        import numpy as np
        px, py = lente
        base = np.asarray(im).astype(np.int16)
        fundo = np.asarray(Image.new('RGB', (W, H), NAVY)).astype(np.int16)
        tinta = np.abs(base - fundo).sum(2) > 26      # onde ha texto ou traco
        ys, xs = np.mgrid[0:H, 0:W]
        r = np.hypot(xs - px, ys - py) / 252.0
        forca = np.clip((1.04 - r) / 0.27, 0, 1)[..., None]
        ouro = np.array([253, 197, 0], np.int16)
        saida_arr = np.where(tinta[..., None],
                             (base * (1 - forca) + ouro * forca).astype(np.uint8),
                             base.astype(np.uint8))
        im = Image.fromarray(saida_arr.astype(np.uint8))
        d = ImageDraw.Draw(im, 'RGBA')

    saida = saida or os.path.join(RAIZ, 'ferramentas', '_heroi_%d.png' % W)
    im.save(saida)
    print('%dx%d  texto %d..%d (centro %.0f)  peca %d..%d x %d..%d  -> %s'
          % (W, H, texto_y0, texto_y1, centro, peca_x0, peca_x1,
             peca_y0, peca_y0 + peca_h, saida))
    return saida


if __name__ == '__main__':
    a = sys.argv[1:]
    montar(int(a[0]) if a else 1368, int(a[1]) if len(a) > 1 else 768)
