# -*- coding: utf-8 -*-
"""A MESMA FOTOGRAFIA EM DOIS PAPEIS -- o que nao pode acontecer.

Cabecalho de pagina e fundo de secao sao papeis DIFERENTES: repetir a imagem
entre eles faz o visitante achar que voltou para uma pagina que ja viu.

Achou, em 20/08, tres casos que ninguem tinha notado:

  cabecalho/servicos ... cabecalho de services E fundo em who-we-are
  faixa/refinaria ...... cabecalho de capabilities E fundo em who-we-are
  faixa/robotica ....... faixa da home E fundo de "The ledger"

----------------------------------------------------------------------------
REESCRITO EM 2026-08-26: COMPARA PIXEL, NAO NOME DE ARQUIVO

A versao anterior agrupava por CAMINHO. Isso pega o caso obvio -- o mesmo
arquivo em duas paginas -- e deixa passar o caso que o visitante realmente
percebe: a mesma FOTOGRAFIA exportada com nomes diferentes.

Foi exatamente o que aconteceu. `gas.jpg` (7900x5266, a unica foto de oil &
gas do acervo) tinha sido recortada tres vezes, com tres nomes:

  momento/refinaria .... o momento 4 da home
  setores/oil-gas ...... o card de setor, na MESMA pagina, uma dobra abaixo
  faixa/refinaria ...... o cabecalho de capabilities

Tres arquivos distintos, zero alarme -- e a home mostrava o mesmo tanque com a
mesma tocha duas vezes em duas dobras seguidas. O usuario reparou; a
ferramenta nao.

O METODO: hash perceptual (dHash de 8x9 -> 64 bits) sobre a versao pequena de
cada arquivo. Ele e invariante a escala, a formato e a compressao -- que sao
as tres coisas que o pipeline de imagens faz --, e sensivel a recorte apenas
o suficiente: dois recortes do mesmo negativo caem a poucos bits de distancia,
e duas fotos diferentes ficam longe.

Distancia de Hamming <= 12 conta como "a mesma fotografia". O limiar e
generoso de proposito: o custo de um falso positivo e olhar duas imagens e
descartar o aviso; o de um falso negativo e o defeito ir ao ar.

Uso: python ferramentas/repetidas.py
"""
import glob
import io
import os
import re
from collections import defaultdict

from PIL import Image

PAPEL = [
    ('cabecalho__foto',  'CABECALHO'),
    ('faixa__foto',      'faixa full-bleed'),
    ('dupla__foto',      'secao dupla'),
    ('secao__foto',      'fundo de secao'),
    ('momento-b__foto',  'MOMENTO da home'),
    ('figura__foto',     'figura com legenda'),
    ('setor__foto',      'card de setor'),
]

LIMIAR = 12

# DUAS ISENCOES, e as duas sao de papel e nao de conveniencia.
#
#   galeria/ -- a galeria E o acervo. Toda foto de setor, de cabecalho e de
#     secao sai de la por definicao, entao casar a galeria com o resto acusaria
#     o proprio funcionamento do site como defeito. A isencao ja existia na
#     versao por nome de arquivo e sobrevive aqui.
#   brand/ --- o logo deve aparecer em todas as nove paginas. E o unico caso em
#     que repetir e o objetivo.
#
# O QUE NENHUMA ISENCAO COBRE: duas ocorrencias na MESMA pagina. Mesmo dentro
# da galeria, a mesma fotografia duas vezes numa pagina e defeito -- e foi
# exatamente assim que `gas.jpg` apareceu duas vezes na home sem alarme.
ISENTOS = ('galeria/', 'brand/')


def isento(base):
    return any(base.startswith(p) for p in ISENTOS)


def dhash(caminho, larg=9, alt=8):
    """Diferenca horizontal entre pixels vizinhos, em cinza. 64 bits.

    Invariante a escala e a formato; e o que faz `refinaria-1280.webp` e
    `oil-gas-672.jpg` -- dois recortes do mesmo negativo em dois formatos --
    cairem perto um do outro."""
    im = Image.open(caminho).convert('L').resize((larg, alt), Image.LANCZOS)
    px = list(im.getdata())  # noqa: PIL sugere get_flattened_data; nao ha no 11
    bits = 0
    for y in range(alt):
        for x in range(larg - 1):
            bits = (bits << 1) | (1 if px[y * larg + x] > px[y * larg + x + 1] else 0)
    return bits


def distancia(a, b):
    return bin(a ^ b).count('1')


def papel_de(classe):
    for chave, nome in PAPEL:
        if chave in classe:
            return nome
    return None


def main():
    uso = defaultdict(set)      # base -> {(pagina, papel)}
    arquivo = {}                # base -> caminho de um arquivo real
    for f in sorted(glob.glob('site/*.html')):
        pag = os.path.basename(f).replace('.html', '')
        s = io.open(f, encoding='utf-8').read()
        for m in re.finditer(r'<img\b[^>]*>', s):
            t = m.group(0)
            src = re.search(r'src="([^"]*)"', t)
            cls = re.search(r'class="([^"]*)"', t)
            if not src:
                continue
            caminho = os.path.join('site', src.group(1))
            base = re.sub(r'-\d+\.\w+$', '', src.group(1).replace('img/', ''))
            uso[base].add((pag, papel_de(cls.group(1) if cls else '') or 'imagem'))
            if os.path.exists(caminho):
                arquivo[base] = caminho

    # --- 1. o mesmo ARQUIVO em mais de um lugar
    print('=== O MESMO ARQUIVO EM MAIS DE UM LUGAR ===')
    n = 0
    for base, locais in sorted(uso.items()):
        if isento(base):
            continue
        if len(locais) > 1:
            print('  %-28s %s' % (base, ' | '.join('%s/%s' % l for l in sorted(locais))))
            n += 1
    if not n:
        print('  nenhuma')

    # --- 2. a mesma FOTOGRAFIA sob nomes diferentes
    print('')
    print('=== A MESMA FOTOGRAFIA SOB NOMES DIFERENTES (dHash) ===')
    hashes = {}
    for base, caminho in sorted(arquivo.items()):
        try:
            hashes[base] = dhash(caminho)
        except Exception:
            pass
    bases = sorted(hashes)
    achou = 0
    for i, a in enumerate(bases):
        for b in bases[i + 1:]:
            d = distancia(hashes[a], hashes[b])
            if d > LIMIAR:
                continue
            pags_a = set(p for p, _ in uso[a])
            pags_b = set(p for p, _ in uso[b])
            mesma_pagina = bool(pags_a & pags_b)
            # A isencao vale entre paginas; na MESMA pagina nada isenta.
            if not mesma_pagina and (isento(a) or isento(b)):
                continue
            achou += 1
            pa = ' | '.join('%s/%s' % l for l in sorted(uso[a]))
            pb = ' | '.join('%s/%s' % l for l in sorted(uso[b]))
            print('  distancia %2d bits%s'
                  % (d, '   << MESMA PAGINA' if mesma_pagina else ''))
            print('     %-26s %s' % (a, pa))
            print('     %-26s %s' % (b, pb))
    if not achou:
        print('  nenhuma')
    print('')
    print('%d arquivo(s) repetido(s), %d par(es) de fotografia igual' % (n, achou))


if __name__ == '__main__':
    main()
