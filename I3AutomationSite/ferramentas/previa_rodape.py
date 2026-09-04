# -*- coding: utf-8 -*-
"""O RODAPE REVELADO: a folha sobe e descobre o fecho, como pagina de livro.

Refaz a geometria do CSS fora do navegador e responde as duas perguntas que o
efeito faz -- e a segunda so existe por causa desta paleta:

  1. o rodape CABE na janela? Um sticky mais alto que a tela e puxado ate o pe
     encostar no pe da janela, e o topo dele -- que e onde a frase de fecho
     mora -- fica fora da tela o tempo todo. Por isso a revelacao tem guarda
     de tamanho, e a guarda saiu desta medicao.
  2. a ARESTA da folha e visivel? Sete das nove paginas terminam numa secao
     navy e o rodape e um navy so um degrau mais fundo: sem a aresta, a folha
     sobe e nada muda na tela.

Uso: python ferramentas/previa_rodape.py
"""
import os
import sys

from PIL import Image, ImageDraw, ImageFont

RAIZ = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from contraste import razao

# --- tokens ---------------------------------------------------------------
TEMAS = {
    'claro':  {'sup1': (255, 255, 255), 'sup3': (0, 29, 61),
               'rod': (0, 8, 20), 'dourado': (253, 197, 0)},
    'escuro': {'sup1': (0, 12, 24), 'sup3': (0, 53, 102),
               'rod': (0, 5, 9), 'dourado': (253, 197, 0)},
}
ARESTA_A = 0.55                     # alfa da borda de baixo do <main>

# guarda do CSS
MIN_LARG, MIN_ALT = 900, 780

# altura medida do rodape por faixa de largura
def altura_rodape(vw):
    pad = 48 if vw > 1023 else (32 if vw > 767 else 20)
    cont = min(vw, 1376) - 2 * pad
    colunas = max(1, cont // 196)
    linhas = -(-4 // colunas)
    alt_linha = 14 + 16 + 7 * (17 * 1.45 + 10)
    return int(96 + (2 * 26 + 96) + linhas * alt_linha + (linhas - 1) * 48
               + (96 + 32 + 40) + 48)


def fonte(t, mono=False):
    c = (r'C:\Windows\Fonts\consola.ttf' if mono
         else r'C:\Windows\Fonts\segoeuil.ttf')
    return (ImageFont.truetype(c, t) if os.path.exists(c)
            else ImageFont.load_default())


def mistura(a, cor, fundo):
    return tuple(round(cor[i] * a + fundo[i] * (1 - a)) for i in range(3))


def quadro(tema, vw, vh, subiu):
    """Uma janela: o <main> deslocado `subiu` px para cima sobre o rodape."""
    t = TEMAS[tema]
    im = Image.new('RGB', (vw, vh), t['rod'])
    d = ImageDraw.Draw(im)

    h_rod = altura_rodape(vw)
    topo_rod = vh - h_rod                 # sticky bottom:0
    pad = 48 if vw > 1023 else (32 if vw > 767 else 20)
    m = max(pad, vw / 2.0 - 1376 / 2.0 + pad)

    # --- o rodape, desenhado onde ele fica preso ---
    y = topo_rod + 96
    for k, ln in enumerate(['Industrial control systems,',
                            'integrated and commissioned.']):
        d.text((m, y + k * 30), ln, font=fonte(26), fill=(255, 255, 255))
    y += 60 + 96
    for k, tit in enumerate(['NAVIGATION', 'CONTACT', 'VENDOR PROFILE', 'SOCIAL']):
        x = m + k * ((vw - 2 * m) / 4.0)
        d.text((x, y), tit, font=fonte(14), fill=t['dourado'])
        for j in range(4):
            d.text((x, y + 26 + j * 25), '\u2014\u2014\u2014\u2014\u2014',
                   font=fonte(15), fill=(160, 175, 190))

    # --- o <main>: opaco, cobre o rodape, deslocado para cima ---
    fim_main = vh - subiu
    if fim_main > 0:
        d.rectangle([0, 0, vw, fim_main], fill=t['sup3'])
        # a ARESTA da folha, composta sobre o rodape
        cor = mistura(ARESTA_A, (255, 255, 255), t['rod'])
        d.line([0, fim_main, vw, fim_main], fill=cor)
        d.text((m, max(8, fim_main - 120)), 'ultima secao da pagina',
               font=fonte(15), fill=(160, 190, 220))

    cabe = (vw >= MIN_LARG and vh >= MIN_ALT)
    d.text((10, vh - 20),
           '%s  %dx%d  rodape %d px  %s' % (tema, vw, vh, h_rod,
           'revelacao LIGADA' if cabe else 'guarda: rodape ESTATICO'),
           font=fonte(12, True), fill=(150, 150, 150))
    return im


def main():
    print('1. O RODAPE CABE NA JANELA?')
    print('   %-14s %-12s %-10s %s' % ('janela', 'rodape', 'guarda', 'veredito'))
    for vw, vh in ((1920, 1080), (1440, 900), (1366, 768), (1024, 800),
                   (900, 780), (768, 1024), (414, 896)):
        h = altura_rodape(vw)
        liga = vw >= MIN_LARG and vh >= MIN_ALT
        ok = h <= vh
        print('   %-14s %-12s %-10s %s'
              % ('%dx%d' % (vw, vh), '%d px' % h,
                 'liga' if liga else 'desliga',
                 'cabe' if ok else 'NAO cabe -- por isso a guarda'))
    print()

    print('2. A ARESTA DA FOLHA')
    for tema in ('claro', 'escuro'):
        t = TEMAS[tema]
        rod = '#%02X%02X%02X' % t['rod']
        sec = '#%02X%02X%02X' % t['sup3']
        cor = '#%02X%02X%02X' % mistura(ARESTA_A, (255, 255, 255), t['rod'])
        print('   %-7s aresta %s   vs rodape %5.2f:1   vs ultima secao %5.2f:1'
              % (tema, cor, razao(cor, rod), razao(cor, sec)))
        print('           sem a aresta, o par secao/rodape daria %5.2f:1'
              % razao(sec, rod))
    print()

    # --- render: tres instantes da subida, nos dois temas ---
    vw, vh = 1440, 900
    passos = [0, int(vh * 0.28), int(vh * 0.62)]
    tiras = []
    for tema in ('claro', 'escuro'):
        linha = [quadro(tema, vw, vh, s) for s in passos]
        faixa = Image.new('RGB', (vw * 3 + 16, vh), (20, 20, 20))
        for i, q in enumerate(linha):
            faixa.paste(q, (i * (vw + 8), 0))
        tiras.append(faixa)
    fora = Image.new('RGB', (tiras[0].width, vh * 2 + 8), (20, 20, 20))
    fora.paste(tiras[0], (0, 0))
    fora.paste(tiras[1], (0, vh + 8))
    fora = fora.resize((fora.width // 2, fora.height // 2), Image.LANCZOS)
    cam = os.path.join(RAIZ, 'ferramentas', '_rodape.png')
    fora.save(cam)
    print(cam)


if __name__ == '__main__':
    main()
