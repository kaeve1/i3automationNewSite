# -*- coding: utf-8 -*-
"""Contraste do TEXTO sobre as fotografias de fundo -- medido, nao estimado.

Regra do projeto (CLAUDE.md #3): se um numero entra no CSS, existe a conta que
o produziu. Este arquivo e a conta do veu que cobre as fotos das secoes
escuras da home.

Metodo: compoe o veu do CSS sobre a FOTO DE VERDADE, amostra a regiao em que o
texto vive, e calcula o contraste WCAG contra cada cor de texto. Media local de
12x12 (nao pixel a pixel): pixel a pixel condena letra grande que le
perfeitamente -- armadilha ja registrada em memoria.md.

Uso: python ferramentas/sobreposicao.py
"""
import os
import sys

import numpy as np
from PIL import Image

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from contraste import razao

RAIZ = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
NAVY = np.array([0, 29, 61], np.float32)


def carregar(rel, larg=1400, alt=520):
    im = Image.open(os.path.join(RAIZ, 'site', 'img', rel)).convert('RGB')
    # object-fit: cover
    escala = max(larg / im.width, alt / im.height)
    im = im.resize((max(1, round(im.width * escala)), max(1, round(im.height * escala))),
                   Image.LANCZOS)
    x = (im.width - larg) // 2
    y = (im.height - alt) // 2
    return np.asarray(im.crop((x, y, x + larg, y + alt))).astype(np.float32)


def veu_secao(forma, topo, meio, esq, dir_, centro=None):
    """Reproduz o ::before de .secao--foto: vertical por cima do horizontal.

    `centro` liga a variante SIMETRICA (.secao--foto-centro): o veu fecha no
    meio, onde o texto centralizado vive, e abre nas duas laterais, onde a
    fotografia respira. A variante padrao e assimetrica -- opaca a esquerda --
    porque foi desenhada para bloco de texto alinhado a esquerda.
    """
    h, w = forma
    ys = np.linspace(0, 1, h)[:, None]
    # vertical: opaco nas pontas, `meio` no miolo (22%..78%)
    av = np.where(ys < .22, topo + (meio - topo) * (ys / .22),
                  np.where(ys > .78, meio + (topo - meio) * ((ys - .78) / .22), meio))
    xs = np.linspace(0, 1, w)[None, :]
    if centro is None:
        ah = np.clip(esq + (dir_ - esq) * (xs / .62), min(esq, dir_), max(esq, dir_))
    else:
        borda, meio_h = centro
        t = np.abs(xs - .5) / .5                      # 0 no centro, 1 nas bordas
        t = np.clip((t - .10) / .35, 0, 1)            # patamar de 10% no miolo
        ah = meio_h + (borda - meio_h) * t
    return 1 - (1 - av) * (1 - ah)      # alfa combinado das duas camadas


def media_local(a, k=12):
    h, w, _ = a.shape
    hh, ww = h // k * k, w // k * k
    b = a[:hh, :ww].reshape(hh // k, k, ww // k, k, 3).mean(axis=(1, 3))
    return b


def medir(rel, cores, topo=1.0, meio=.55, esq=1.0, dir_=.35, faixa=(.18, .82),
          centro=None, faixa_x=(0.0, 1.0)):
    foto = carregar(rel)
    alfa = veu_secao(foto.shape[:2], topo, meio, esq, dir_, centro)[..., None]
    comp = foto * (1 - alfa) + NAVY * alfa
    blocos = media_local(comp)
    h = blocos.shape[0]
    lw = blocos.shape[1]
    reg = blocos[int(h * faixa[0]):int(h * faixa[1]),
                 int(lw * faixa_x[0]):int(lw * faixa_x[1])]
    print('  %-34s  fundo mais CLARO do miolo: #%02X%02X%02X'
          % (rel, *[int(v) for v in reg.reshape(-1, 3)[
              reg.reshape(-1, 3).sum(1).argmax()]]))
    pior = reg.reshape(-1, 3)[reg.reshape(-1, 3).sum(1).argmax()]
    hexa = '#%02X%02X%02X' % tuple(int(v) for v in pior)
    for nome, c in cores:
        r = razao(c, hexa)
        print('      %-22s %s  %5.2f:1  %s'
              % (nome, c, r, 'ok' if r >= 4.5 else ('AA grande' if r >= 3 else 'FALHA')))
    return hexa


if __name__ == '__main__':
    # As cores sao as que a secao--foto usa DE VERDADE: --tinta-2 e --navy-luz
    # sao sobrescritos la para #B9D2EA justamente porque #8FB4DC reprovava.
    CORES = [('titulo #fff', '#FFFFFF'),
             ('eyebrow/link', '#B9D2EA'),
             ('corpo 80% branco', '#CCCCCC'),
             ('(rejeitado) #8FB4DC', '#8FB4DC')]
    print('SECOES COM FOTO — veu vertical .55 no miolo, horizontal 1.0 -> .35')
    for rel in ('faixa/refinaria-2560.jpg', 'cabecalho/contato-1920.jpg',
                'cabecalho/servicos-1920.jpg'):
        medir(rel, CORES)
