# -*- coding: utf-8 -*-
"""Monta o mosaico da galeria FORA do navegador.

Reproduz a aritmetica do CSS §22.5: mosaico full-bleed com padding lateral,
tres colunas de verdade (nao `columns`), empilhamento guloso pela coluna mais
curta, proporcao NATIVA de cada chapa, legenda com numero em mono.

O que so esta previa responde: "o mosaico tem ritmo?". Ate 20/08 as 29 fotos
saiam recortadas em 1:1 e o mosaico era uma grade uniforme de quadrados --
nenhuma animacao conserta isso, e nenhuma conta mostra isso. So olhando.

`--deriva` desenha a paralaxe num instante escolhido da rolagem, para conferir
que ela le como profundidade e nao como desalinhamento.

Uso: python ferramentas/previa_galeria.py [largura] [p]
     p = posicao da rolagem 0..1 (padrao 0, as colunas no prumo)
"""
import os
import sys

from PIL import Image, ImageDraw, ImageFont

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

RAIZ = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
IMG = os.path.join(RAIZ, 'site', 'img')

BRANCO = (255, 255, 255)
TINTA_SUAVE = (90, 90, 90)
TINTA2 = (64, 96, 127)
PAD, S3, S4 = 48, 16, 24

# --amp do CSS: coluna 1 parada, 2 e 3 derivam.
AMP = (0, -44, -88)


def fonte(tam, mono=False):
    cams = ([r'C:\Windows\Fonts\consola.ttf'] if mono else
            [r'C:\Windows\Fonts\segoeui.ttf'])
    for c in cams:
        if os.path.exists(c):
            return ImageFont.truetype(c, tam)
    return ImageFont.load_default()


def arquivo(base, larguras):
    """O mesmo arquivo que o <img src> da pagina aponta: a maior largura."""
    caminho = os.path.join(IMG, base.replace('/', os.sep))
    for suf in ('jpg', 'png'):
        f = '%s-%d.%s' % (caminho, larguras[-1], suf)
        if os.path.exists(f):
            return f
    raise SystemExit('sem arquivo para %s' % base)


def montar(W=1440, p=0.0, saida=None):
    import build_site as B

    itens = [(b, l, a, g, B._proporcao(b, l)) for b, l, a, g in B.GALERIA]
    ordem = {id(it): i + 1 for i, it in enumerate(itens)}
    n = 1 if W <= 700 else (2 if W <= 1100 else 3)
    pilhas = B._empilhar(itens, n)

    col = (W - 2 * PAD - (n - 1) * S4) / n
    f_num = fonte(12, True)
    f_leg = fonte(15)

    # altura total: a coluna mais alta, com a legenda de verdade
    def altura(pilha):
        h = 0
        for it in pilha:
            h += round(col / it[4]) + S3 + 20 + S3 + S3
        return h

    H = int(max(altura(c) for c in pilhas)) + 120
    im = Image.new('RGB', (W, H), BRANCO)
    d = ImageDraw.Draw(im, 'RGBA')

    for c, pilha in enumerate(pilhas):
        x = PAD + c * (col + S4)
        y = 40 + p * AMP[c]
        for it in pilha:
            base, larg, alt, leg, ar = it
            w = int(col)
            h = max(1, round(col / ar))
            foto = Image.open(arquivo(base, larg)).convert('RGB')
            foto = foto.resize((w, h), Image.LANCZOS)
            im.paste(foto, (int(x), int(y)))
            # marca de registro branca no canto
            d.rectangle((x, y, x + 22, y + 2), fill=(255, 255, 255, 140))
            d.rectangle((x, y, x + 2, y + 22), fill=(255, 255, 255, 140))
            ly = y + h + S3
            d.text((x, ly + 2), '%02d' % ordem[id(it)], font=f_num, fill=TINTA2)
            d.text((x + 34, ly), leg[:44], font=f_leg, fill=TINTA_SUAVE)
            d.line((x, ly + 20 + S3, x + w, ly + 20 + S3), fill=(222, 222, 222))
            y = ly + 20 + S3 + S3

    saida = saida or os.path.join(RAIZ, 'ferramentas', '_galeria.png')
    im.save(saida)
    print('%dx%d  %d colunas, coluna %d px, --p %.2f  -> %s'
          % (W, H, n, col, p, saida))
    return saida


if __name__ == '__main__':
    a = sys.argv[1:]
    montar(int(a[0]) if a else 1440, float(a[1]) if len(a) > 1 else 0.0)
