# -*- coding: utf-8 -*-
"""Monta o REGISTRO DE OBRAS de past-performance FORA do navegador.

Reproduz a aritmetica do CSS §23: container centrado, trilho com indice/setor e
a cota que atravessa a largura restante, corpo em 5/7 (invertido nas fichas
pares), placa quadrada de 420 px com marca de registro, e a lista de dados em
4fr/8fr.

Serve para responder as perguntas que so a composicao responde -- "a alternancia
le como paginacao ou como zigue-zague?", "a placa compete com o texto?", "o
trilho separa as fichas o suficiente?" -- sem abrir o Chrome.

Uso: python ferramentas/previa_obra.py [largura]
"""
import os
import sys

from PIL import Image, ImageDraw, ImageFont

RAIZ = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
IMG = os.path.join(RAIZ, 'site', 'img')

BRANCO = (255, 255, 255)
TINTA = (26, 26, 26)
TINTA_SUAVE = (90, 90, 90)
TINTA_TIT = (0, 53, 102)
TINTA2 = (64, 96, 127)
FILETE = (222, 222, 222)
FILETE_F = (196, 196, 196)

CONTAINER, PAD = 1376, 48
S1, S2, S3, S4, S5, S6, S7, S8 = 4, 8, 16, 24, 32, 48, 64, 96

# As tres primeiras fichas de SETORES_PP, com o conteudo real.
FICHAS = [
    ('Automotive', 'Body shops,|to their standard',
     'Automotive plants do not accept a contractor\u2019s house style. Both of '
     'these programs were written to the customer\u2019s own PLC standard.',
     [('DAIMLER / MERCEDES-BENZ',
       'Plant automation for the New Body Shop, following the Integra '
       'standard for PLC programming end to end.'),
      ('BMW',
       'F15 / F16 / F25 / F26 Body Shop SSB, integrating BMW\u2019s specific '
       'PLC standard programs.')],
     'setor/automotivo-600.jpg'),
    ('Oil & Gas', 'Houston, and|150,000 tags',
     'Our oil and gas client base sits in Houston, Texas. The work is PI System '
     'expertise at scale: more than 150,000 historized tags.',
     [('HISTORIAN', 'AVEVA PI System, 150,000+ historized tags under support.'),
      ('SCOPE', 'Ongoing support and optimisation of existing control and data '
                'systems, plus new project work.')],
     'setor/oil-gas-900.jpg'),
    ('Water & wastewater', 'Florida plants,|under annual support',
     'Controls maintenance, PLC and HMI programming, and integration of the '
     'entire SCADA system. Daily reports come straight from the SQL database.',
     [('MAINTENANCE', 'Annual support keeping control systems safe and efficient.'),
      ('PROGRAMMING', 'PLC and HMI development, with the full SCADA layer '
                      'integrated rather than bolted on.'),
      ('REPORTING', 'Daily reports generated from SQL databases; alerts '
                    'delivered to the operator on shift.')],
     'setor/agua-600.jpg'),
]


def fonte(tam, mono=False, leve=False):
    cams = ([r'C:\Windows\Fonts\consola.ttf'] if mono else
            ([r'C:\Windows\Fonts\segoeuil.ttf'] if leve else
             [r'C:\Windows\Fonts\segoeui.ttf']))
    for c in cams:
        if os.path.exists(c):
            return ImageFont.truetype(c, tam)
    return ImageFont.load_default()


def quebrar(d, txt, f, larg):
    linhas, atual = [], ''
    for p in txt.split(' '):
        teste = (atual + ' ' + p).strip()
        if d.textbbox((0, 0), teste, font=f)[2] <= larg:
            atual = teste
        else:
            if atual:
                linhas.append(atual)
            atual = p
    if atual:
        linhas.append(atual)
    return linhas


def montar(W=1440, saida=None):
    cx0 = max(PAD, (W - CONTAINER) // 2 + PAD)
    cx1 = W - cx0
    larg = cx1 - cx0

    f_mono = fonte(13, True)
    f_mono_p = fonte(12, True)
    f_setor = fonte(15)
    f_h2 = fonte(40, leve=True)
    f_lead = fonte(20, leve=True)
    f_corpo = fonte(16)

    im = Image.new('RGB', (W, 2400), BRANCO)
    d = ImageDraw.Draw(im, 'RGBA')

    y = 60
    for i, (setor, titulo, lead, dados, rel) in enumerate(FICHAS):
        par = (i % 2 == 1)          # nth-child(even) -> placa a DIREITA
        if i:
            d.line((cx0, y, cx1, y), fill=FILETE)   # border-top da ficha
            y += S7            # .obra { padding-block: var(--s-7) }
        else:
            y += S5            # .obra:first-child { padding-top: var(--s-5) }

        # ---------- trilho ----------
        ty = y
        d.text((cx0, ty), '%02d' % (i + 1), font=f_mono, fill=TINTA2)
        iw = d.textbbox((0, 0), '%02d' % (i + 1), font=f_mono)[2]
        sx = cx0 + iw + S4
        d.text((sx, ty - 2), setor, font=f_setor, fill=TINTA_TIT)
        sw = d.textbbox((0, 0), setor, font=f_setor)[2]
        # a cota fecha a largura que sobra, com tique na ponta
        qx = sx + sw + S4
        qy = ty + 8
        d.line((qx, qy, cx1, qy), fill=FILETE_F)
        d.line((cx1, qy - 4, cx1, qy + 4), fill=FILETE_F)
        y = ty + S5 + 12   # .obra__trilho { margin-bottom: var(--s-5) }

        # ---------- corpo: 5/7 ou 7/5 ----------
        vao = larg - S8
        wp = min(420, vao * 5 / 12)
        wt = vao * 7 / 12
        if par:
            tx, px = cx0, cx1 - wp
        else:
            tx, px = cx0 + wp + S8, cx0

        # placa
        foto = Image.open(os.path.join(IMG, rel)).convert('RGB')
        lado = int(wp)
        foto = foto.resize((lado, lado), Image.LANCZOS)
        # repouso: saturate(.2) contrast(1.05)
        cinza = foto.convert('L').convert('RGB')
        foto = Image.blend(cinza, foto, .2)
        im.paste(foto, (int(px), int(y)))
        d.rectangle((px, y, px + lado, y + lado), outline=FILETE)
        d.rectangle((px - 1, y - 1, px + 23, y + 1), fill=FILETE_F)
        d.rectangle((px - 1, y - 1, px + 1, y + 23), fill=FILETE_F)

        # texto
        # .obra__titulo { margin-top: -.19em } — alinhamento optico
        # da maiuscula com a borda de cima da placa (h2 a 40px aqui).
        tyy = y - round(.19 * 40)
        for ln in titulo.split('|'):
            d.text((tx, tyy), ln, font=f_h2, fill=TINTA_TIT)
            tyy += 44
        tyy += S4 - 8
        for ln in quebrar(d, lead, f_lead, min(wt, 52 * 10)):
            d.text((tx, tyy), ln, font=f_lead, fill=TINTA_SUAVE)
            tyy += 28
        tyy += S6 - 10

        d.line((tx, tyy, tx + wt, tyy), fill=FILETE)
        tyy += S3
        for rot, val in dados:
            wr = wt * 4 / 12
            for k, ln in enumerate(quebrar(d, rot, f_mono_p, wr)):
                d.text((tx, tyy + k * 17), ln, font=f_mono_p, fill=TINTA2)
            vx = tx + wr + S4
            linhas = quebrar(d, val, f_corpo, wt - wr - S4)
            for k, ln in enumerate(linhas):
                d.text((vx, tyy - 2 + k * 24), ln, font=f_corpo, fill=TINTA_SUAVE)
            tyy += max(len(linhas) * 24, 24) + S3
            d.line((tx, tyy - 8, tx + wt, tyy - 8), fill=FILETE)

        y = max(y + lado, tyy) + S7

    saida = saida or os.path.join(RAIZ, 'ferramentas', '_obra.png')
    im.crop((0, 0, W, int(y))).save(saida)
    print('%dx%d -> %s' % (W, int(y), saida))
    return saida


if __name__ == '__main__':
    a = sys.argv[1:]
    montar(int(a[0]) if a else 1440)
