# -*- coding: utf-8 -*-
"""Monta a secao "what we actually do" FORA do navegador.

Reproduz a aritmetica do CSS -- container centrado, cabecalho em coluna unica,
fileira de 4 fotos ALINHADAS, cadeia de cota no topo, moldura, legenda em mono
e a linha de dimensao embaixo. Serve para responder "a composicao fecha?" sem
abrir o Chrome.

DUAS COISAS MUDARAM AQUI EM 20/08, e as duas a pedido do usuario:

  a escada saiu. O `nth-child(even) { margin-top: --s-7 }` deslocava as folhas
    pares 64 px para baixo. Nasceu como ritmo de folha montada a mao, e essa e
    a lingua errada: o resto do site e desenho tecnico, e desenho tecnico
    ALINHA. O ritmo passou para a cadeia de cota no topo;

  o realce dourado mudou de linha. Estava sobre a tese ("We build the control
    system") e passou para o rotulo da secao ("What we actually do"), que e
    onde um marcador de capitulo pertence.

Uso: python ferramentas/previa_prancha.py [largura]
"""
import os
import sys

from PIL import Image, ImageDraw, ImageFont

RAIZ = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
IMG = os.path.join(RAIZ, 'site', 'img')

BRANCO = (255, 255, 255)
TINTA = (26, 26, 26)
TINTA2 = (64, 96, 127)
DOURADO = (253, 197, 0)
FILETE = (222, 222, 222)
FILETE_F = (196, 196, 196)
GRADE = (233, 238, 243)

CONTAINER, PAD = 1280, 32
S3, S4, S5, S6, S7, S8 = 16, 24, 32, 48, 64, 96

FOTOS = [
    ('galeria/scada-600.jpg', 'SCADA', 'Effluent station discharge flow, on shift'),
    ('galeria/painel-campo-600.jpg', 'CONTROL PANEL', 'Pump station, door open for commissioning'),
    ('galeria/bomba-600.jpg', 'INSTRUMENTATION', 'Submersible set going into the wet well'),
    ('galeria/obra-agua-600.jpg', 'FIELD BUILD', 'Weir gate structure, controls going in'),
]


def fonte(tam, mono=False):
    cams = ([r'C:\Windows\Fonts\consola.ttf'] if mono else
            [r'C:\Windows\Fonts\segoeuil.ttf', r'C:\Windows\Fonts\segoeui.ttf'])
    for c in cams:
        if os.path.exists(c):
            return ImageFont.truetype(c, tam)
    return ImageFont.load_default()


def centrado(d, y, txt, f, cor, x0, larg):
    w = d.textbbox((0, 0), txt, font=f)[2]
    d.text((x0 + (larg - w) / 2, y), txt, font=f, fill=cor)


def montar(W=1440, saida=None):
    cx0 = max(PAD, (W - CONTAINER) // 2 + PAD)
    cx1 = W - cx0
    larg = cx1 - cx0

    H = 1180
    im = Image.new('RGB', (W, H), BRANCO)
    d = ImageDraw.Draw(im, 'RGBA')

    # ---------- cabecalho centrado (bloco--centro, 54ch) ----------
    f_eye = fonte(14)
    f_lead = fonte(26)
    f_corpo = fonte(17)
    col = min(int(48 * 9.3), larg)          # ~48ch na escala do corpo
    kx = cx0 + (larg - col) // 2
    y = 80
    # O REALCE: faixa dourada com tinta navy, o par do logo (7,74:1). A caixa
    # tem 1,22em de altura, deslocada .10em — os mesmos numeros do CSS, so que
    # em px na escala desta previa.
    eye = 'What we actually do'
    ew = d.textbbox((0, 0), eye, font=f_eye)[2]
    ex = kx + (col - ew) / 2
    em = 14
    d.rectangle((ex - .03 * em, y + em - .90 * em,
                 ex + ew + .16 * em, y + em + .32 * em), fill=DOURADO)
    d.text((ex, y), eye, font=f_eye, fill=(0, 53, 102))
    y += 40
    for ln in ('We build the control system and hand you the plant that',
               'runs it — panel, code, network, and drawings that match the wall.'):
        centrado(d, y, ln, f_lead, TINTA, kx, col); y += 36
    y += 26
    for ln in ('i3 Automations & Controls has been integrating industrial control',
               'systems since 2000. Control panels, PLC and SCADA programming,',
               'instrumentation, commissioning. Oil and gas in Houston, water and',
               'wastewater across Florida, automotive body shops, paper mills.'):
        centrado(d, y, ln, f_corpo, TINTA, kx, col); y += 27
    y += 18
    for ln in ('We are a registered federal contractor, certified on Ignition,',
               'VTScada and Canary. The work is the same either way.'):
        centrado(d, y, ln, f_corpo, TINTA, kx, col); y += 27
    y += 24
    centrado(d, y, '\u2192   Who we are', fonte(15), TINTA, kx, col)
    y += 60

    # ---------- prancha ----------
    linha_y = y + S6        # .prancha { margin-top: var(--s-6) }
    gap = S5
    cel = (larg - gap * 3) / 4

    # chao de retícula, apagado nas bordas
    grade = Image.new('RGB', (W, H), BRANCO)
    gd = ImageDraw.Draw(grade)
    for gx in range(0, W, 28):
        gd.line((gx, 0, gx, H), fill=GRADE)
    for gy in range(0, H, 28):
        gd.line((0, gy, W, gy), fill=GRADE)
    masc = Image.new('L', (W, H), 0)
    md = ImageDraw.Draw(masc)
    md.ellipse((cx0 - 260, linha_y - 120, cx1 + 260, linha_y + int(cel) + 320), fill=90)
    im.paste(grade, (0, 0), masc)

    # ---------- a linha de referencia, em cima ----------
    d.line((cx0, linha_y, cx1, linha_y), fill=FILETE_F)
    # a ORIGEM da cadeia de cota: o unico dourado do componente
    d.rectangle((cx0, linha_y - 5, cx0 + 1, linha_y + 5), fill=DOURADO)

    topo_foto = linha_y + S5
    for i, (rel, ref, leg) in enumerate(FOTOS):
        x = cx0 + i * (cel + gap)
        # O TIQUE cai sobre a borda esquerda da folha, que e onde uma cadeia de
        # cota real marca a extremidade da medida.
        d.line((x, linha_y, x, linha_y + 11), fill=FILETE_F)
        d.text((x + 8, linha_y + 8), '%02d' % (i + 1),
               font=fonte(11, True), fill=TINTA2)

        yy = topo_foto           # ALINHADAS: nenhuma folha desce
        foto = Image.open(os.path.join(IMG, rel)).convert('RGB')
        lado = int(cel)
        foto = foto.resize((lado, lado), Image.LANCZOS)
        im.paste(foto, (int(x), int(yy)))
        d.rectangle((x, yy, x + lado, yy + lado), outline=FILETE)
        # marca de registro: FILETE, nao dourado. Quatro marcas douradas na
        # mesma dobra estouravam a regra critica n5 (teto de duas).
        d.rectangle((x - 1, yy - 1, x + 21, yy + 1), fill=FILETE_F)
        d.rectangle((x - 1, yy - 1, x + 1, yy + 21), fill=FILETE_F)

        ly = yy + lado + S3
        d.text((x, ly), ref, font=fonte(12, True), fill=(0, 53, 102))
        d.text((x, ly + 18), leg[:34], font=fonte(11, True), fill=TINTA2)
        if len(leg) > 34:
            d.text((x, ly + 33), leg[34:], font=fonte(11, True), fill=TINTA2)

    # ---------- linha de cota, embaixo ----------
    cy = topo_foto + int(cel) + 78 + S6
    rot = 'WATER  ·  WASTEWATER  ·  PANEL SHOP  ·  SUPERVISION'
    fr = fonte(12, True)
    rw = d.textbbox((0, 0), rot, font=fr)[2]
    meio_x0 = cx0 + (larg - rw) / 2
    for a, b in ((cx0, meio_x0 - S4), (meio_x0 + rw + S4, cx1)):
        d.line((a, cy, b, cy), fill=FILETE_F)
        d.line((a, cy - 4, a, cy + 4), fill=FILETE_F)
        d.line((b, cy - 4, b, cy + 4), fill=FILETE_F)
    d.text((meio_x0, cy - 7), rot, font=fr, fill=TINTA2)

    saida = saida or os.path.join(RAIZ, 'ferramentas', '_prancha.png')
    im.crop((0, 0, W, cy + 60)).save(saida)
    print('%dx%d -> %s' % (W, cy + 60, saida))
    return saida


if __name__ == '__main__':
    a = sys.argv[1:]
    montar(int(a[0]) if a else 1440)
