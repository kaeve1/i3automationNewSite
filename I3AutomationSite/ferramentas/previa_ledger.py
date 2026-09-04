# -*- coding: utf-8 -*-
"""Mede o veu da fotografia de fundo de "The ledger" (past-performance).

Regra critica no3: se um numero entra no CSS, existe a conta que o produziu.

Duas perguntas, e a ordem importa -- a segunda so vale se a primeira passar:

  1. a FONTE e reduzida ou ampliada na caixa? Ampliar e o erro que a secao
     "Since 2000" custou, e por isso a proporcao se confere ANTES de escolher
     a foto pelo assunto.
  2. com o veu composto sobre a foto DE VERDADE, cada cor de texto passa AA?

O pior caso VIRA COM O TEMA, e e contraintuitivo: com texto escuro sobre veu
claro o ponto perigoso e o mais ESCURO da foto; com texto claro sobre veu
escuro e o mais CLARO. Os dois sao medidos.

Media local de 12x12, nao pixel a pixel: pixel a pixel condena letra grande
que le perfeitamente -- armadilha ja registrada em memoria.md.

Uso: python ferramentas/previa_ledger.py
"""
import os
import sys

import numpy as np
from PIL import Image

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from contraste import razao

RAIZ = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

# Trocada em 20/08: `robotica` repetia a faixa da home E, sob o veu off-white,
# devolvia amplitude de so 34,8 -- "praticamente invisivel". Esta da 46,2.
FOTO = 'faixa/engrenagem-2560.jpg'  # so a maior largura sai em jpg
LARG = 1440                 # largura de referencia do projeto

# --- o que o CSS declara --------------------------------------------------
FAIXA = 0.62                # --faixa-foto
# ATENCAO AO PRIMEIRO STOP DOS DOIS: no CSS ele e `var(--sup-N)`, uma cor
# OPACA -- alfa 1,0, nao 0. O gradiente comeca SOLIDO (foto invisivel) e abre
# para o veu; nao o contrario. Errar esse sinal faz a medicao acusar #0F151C
# de pior fundo e reprovar tudo, que foi o que aconteceu na primeira volta.
PARADAS_V = (0.00, 0.18, 0.42, FAIXA)   # gradiente 180deg
ALFA_V = (1.0, 0.78, 0.78, 1.0)
LADO_A, LADO_B = 0.00, 0.58             # gradiente 90deg
ALFA_H = (1.0, 0.56)

# (nome, tinta, superficie, veu) por tema
TEMAS = {
    'claro': {
        'sup': (242, 245, 248),          # --sup-2
        'veu': (242, 245, 248),
        'textos': [
            ('h2 / numero  --tinta-titulo', (0, 53, 102), 'grande'),
            ('corpo        --tinta',        (26, 26, 26), 'pequeno'),
            ('eyebrow      --tinta-2',      (64, 96, 127), 'pequeno'),
            ('dd           --tinta-suave',  (90, 90, 90), 'pequeno'),
        ],
        'pior': 'escuro',                # ponto mais ESCURO da foto
    },
    'escuro': {
        'sup': (0, 20, 39),              # --sup-2 no tema escuro
        'veu': (0, 20, 39),
        'textos': [
            ('h2 / numero  --tinta-titulo', (232, 237, 243), 'grande'),
            ('corpo        --tinta',        (232, 237, 243), 'pequeno'),
            ('eyebrow      --tinta-2',      (159, 190, 224), 'pequeno'),
            ('dd           --tinta-suave',  (168, 186, 203), 'pequeno'),
        ],
        'pior': 'claro',                 # ponto mais CLARO da foto
    },
}


def cobrir(rel, larg, alt):
    """object-fit: cover, e devolve tambem a escala aplicada."""
    im = Image.open(os.path.join(RAIZ, 'site', 'img', rel)).convert('RGB')
    esc = max(larg / im.width, alt / im.height)
    nw, nh = int(round(im.width * esc)), int(round(im.height * esc))
    im = im.resize((nw, nh), Image.LANCZOS)
    x = (nw - larg) // 2
    y = int((nh - alt) * 0.42)           # mesma ancora de recortar_cobrir()
    return im.crop((x, y, x + larg, y + alt)), esc, (im.width, im.height)


def rampa(t, paradas, valores):
    """Interpola o alfa do gradiente em t (0..1)."""
    if t <= paradas[0]:
        return valores[0]
    for i in range(1, len(paradas)):
        if t <= paradas[i]:
            f = (t - paradas[i - 1]) / max(1e-6, paradas[i] - paradas[i - 1])
            return valores[i - 1] + f * (valores[i] - valores[i - 1])
    return valores[-1]


def palco(foto, larg, alt_secao, tema):
    """A secao inteira: a foto ocupa a faixa de cima, o resto e superficie."""
    sup = np.array(TEMAS[tema]['sup'], np.float32)
    cena = np.tile(sup, (alt_secao, larg, 1)).astype(np.float32)
    f = np.asarray(foto, np.float32)
    cena[:f.shape[0]] = f
    return cena


def compor(cena, alt_secao, tema):
    """Aplica os dois gradientes do CSS sobre a cena, como o navegador faz."""
    px = np.asarray(cena, np.float32)
    h, w, _ = px.shape
    veu = np.array(TEMAS[tema]['veu'], np.float32)
    sup = np.array(TEMAS[tema]['sup'], np.float32)

    ys = (np.arange(h) / float(alt_secao))
    av = np.array([rampa(t, PARADAS_V, ALFA_V) for t in ys], np.float32)
    xs = np.arange(w) / float(w)
    ah = np.array([rampa(t, (LADO_A, LADO_B), ALFA_H) for t in xs], np.float32)

    # ORDEM DAS CAMADAS: em `background: A, B` o A e o de CIMA. No CSS o
    # vertical vem primeiro, entao ele pinta SOBRE o horizontal -- e nao
    # depois dele, como a primeira versao fazia.
    out = px * (1 - ah[None, :, None]) + veu[None, None, :] * ah[None, :, None]
    out = out * (1 - av[:, None, None]) + sup[None, None, :] * av[:, None, None]
    return out


def media_local(a, k=12):
    h, w, _ = a.shape
    h2, w2 = (h // k) * k, (w // k) * k
    b = a[:h2, :w2].reshape(h2 // k, k, w2 // k, k, 3).mean(axis=(1, 3))
    return b.reshape(-1, 3)


def main():
    # altura da secao, pela aritmetica do CSS a 1440
    SEC_Y, GAP = 160, 64
    bloco, numeros = 100, 148
    alt = SEC_Y + bloco + GAP + numeros + SEC_Y
    alt_faixa = int(round(alt * FAIXA))

    print('caixa a %d px de largura: secao %d px, faixa da foto %d px (%.0f%%)'
          % (LARG, alt, alt_faixa, FAIXA * 100))
    print()

    foto, esc, nativo = cobrir(FOTO, LARG, alt_faixa)
    im = Image.open(os.path.join(RAIZ, 'site', 'img', FOTO))
    print('1. PROPORCAO')
    print('   fonte %dx%d  ->  caixa %dx%d' % (im.width, im.height, LARG, alt_faixa))
    print('   escala %.3fx  ->  %s' % (esc, 'REDUZ (nitida)' if esc < 1
                                       else 'AMPLIA -- REPROVA'))
    if esc >= 1.0:
        print('   a fonte nao tem resolucao para esta caixa. Parar aqui.')
        return
    print()

    print('2. CONTRASTE, veu composto sobre a foto de verdade')
    for tema in ('claro', 'escuro'):
        comp = compor(palco(foto, LARG, alt, tema), alt, tema)
        blocos = media_local(comp)
        lum = blocos @ np.array([.2126, .7152, .0722], np.float32)
        idx = int(np.argmin(lum) if TEMAS[tema]['pior'] == 'escuro'
                  else np.argmax(lum))
        fundo = blocos[idx]
        fh = '#%02X%02X%02X' % tuple(int(round(c)) for c in fundo)
        print('   tema %-7s pior fundo %s' % (tema, fh))
        for nome, tinta, tam in TEMAS[tema]['textos']:
            r = razao('#%02X%02X%02X' % tinta, fh)
            piso = 3.0 if tam == 'grande' else 4.5
            print('      %-30s %6.2f:1   %s' % (nome, r,
                  'AA' if r >= piso else 'REPROVA (piso %.1f)' % piso))
        print()

    render(foto, alt, alt_faixa)


def render(foto, alt, alt_faixa):
    """Desenha a secao nos dois temas, com o texto nas posicoes do CSS."""
    from PIL import ImageDraw, ImageFont

    def fonte(t, mono=False):
        c = (r'C:\Windows\Fonts\consola.ttf' if mono
             else r'C:\Windows\Fonts\segoeuil.ttf')
        return (ImageFont.truetype(c, t) if os.path.exists(c)
                else ImageFont.load_default())

    PAD, CONT = 48, 1376
    m = max(PAD, LARG / 2.0 - CONT / 2.0 + PAD)      # borda do container
    col = (LARG - 2 * m) / 12.0                       # grade de 12

    tiras = []
    for tema in ('claro', 'escuro'):
        comp = compor(palco(foto, LARG, alt, tema), alt, tema)
        im = Image.fromarray(np.clip(comp, 0, 255).astype(np.uint8))
        d = ImageDraw.Draw(im)
        t = TEMAS[tema]['textos']
        titulo, corpo, eyebrow, dd = t[0][1], t[1][1], t[2][1], t[3][1]

        y = 160                                        # --sec-y
        d.text((m, y), 'THE LEDGER', font=fonte(15), fill=eyebrow)
        d.text((m, y + 30), 'Twenty-six years,', font=fonte(33), fill=titulo)
        d.text((m, y + 68), 'counted', font=fonte(33), fill=titulo)
        xd = m + 4 * col
        for k, ln in enumerate(['Six sectors, one discipline. What changes between a',
                                'refinery and a body shop is the process and the',
                                'consequence of getting it wrong - not the rigor the',
                                'control system deserves.']):
            d.text((xd, y + 4 + k * 23), ln, font=fonte(16), fill=corpo)

        yn = 160 + 100 + 64                            # + bloco + --gap-bloco
        d.line([m, yn, LARG - m, yn], fill=tuple(int(c) for c in
               (np.array(TEMAS[tema]['sup']) * .82)), width=1)
        for k, (num, rot) in enumerate([('279+', 'projects delivered'),
                                        ('158+', 'in the United States'),
                                        ('78+', 'in Florida'),
                                        ('150,000+', 'PI System tags'),
                                        ('2000', 'in business since')]):
            x = m + k * ((LARG - 2 * m) / 5.0)
            d.text((x, yn + 48), num, font=fonte(42), fill=titulo)
            d.text((x, yn + 100), rot, font=fonte(15), fill=dd)

        d.text((12, alt - 22), 'tema %s   faixa da foto ate y=%d (62%%)'
               % (tema, alt_faixa), font=fonte(13, True), fill=dd)
        tiras.append(im)

    fora = Image.new('RGB', (LARG, alt * 2 + 8), (20, 20, 20))
    fora.paste(tiras[0], (0, 0))
    fora.paste(tiras[1], (0, alt + 8))
    cam = os.path.join(RAIZ, 'ferramentas', '_ledger.png')
    fora.save(cam)
    print(cam)


if __name__ == '__main__':
    main()
