# -*- coding: utf-8 -*-
"""Recorte do braco robotico do fundo, sem rembg/cv2 — so numpy + Pillow.

Estrategia: o braco e laranja muito saturado sobre um fundo industrial
dessaturado. O laranja e a SEMENTE; a partir dela o mascaramento cresce por
componente conexo, tapa buracos e recupera as pecas cinzas (cabecote de
ferramenta, cabos) que estao encostadas no corpo laranja.

Uso: python ferramentas/recorte.py
"""
import numpy as np
from PIL import Image, ImageFilter
from collections import deque
import os, sys

FONTE = 'referencia/universodoclp-assets/referencia/universodoclp/fotosproduto/engcontrole.png'
SAIDA = os.environ.get('SAIDA', 'C:/Users/kegit/AppData/Local/Temp/claude/C--Users-kegit-I3Automations/1ff73b39-2722-4fb2-82c1-a7071f805473/scratchpad')


def maior_componente(m):
    """Maior componente conexo 4-vizinhos, por BFS em fila."""
    h, w = m.shape
    visto = np.zeros((h, w), bool)
    melhor, melhor_n = None, 0
    ys, xs = np.nonzero(m)
    for y0, x0 in zip(ys[::97], xs[::97]):          # sementes esparsas: rapido
        if visto[y0, x0]:
            continue
        q = deque([(y0, x0)]); visto[y0, x0] = True
        comp = [(y0, x0)]
        while q:
            y, x = q.popleft()
            for dy, dx in ((1, 0), (-1, 0), (0, 1), (0, -1)):
                ny, nx = y + dy, x + dx
                if 0 <= ny < h and 0 <= nx < w and m[ny, nx] and not visto[ny, nx]:
                    visto[ny, nx] = True; q.append((ny, nx)); comp.append((ny, nx))
        if len(comp) > melhor_n:
            melhor_n, melhor = len(comp), comp
    out = np.zeros((h, w), bool)
    if melhor:
        a = np.array(melhor)
        out[a[:, 0], a[:, 1]] = True
    return out


def tapa_buracos(m):
    """Inunda o fundo a partir da borda; o que nao for alcancado e buraco."""
    h, w = m.shape
    fora = np.zeros((h, w), bool)
    q = deque()
    for x in range(w):
        for y in (0, h - 1):
            if not m[y, x] and not fora[y, x]:
                fora[y, x] = True; q.append((y, x))
    for y in range(h):
        for x in (0, w - 1):
            if not m[y, x] and not fora[y, x]:
                fora[y, x] = True; q.append((y, x))
    while q:
        y, x = q.popleft()
        for dy, dx in ((1, 0), (-1, 0), (0, 1), (0, -1)):
            ny, nx = y + dy, x + dx
            if 0 <= ny < h and 0 <= nx < w and not m[ny, nx] and not fora[ny, nx]:
                fora[ny, nx] = True; q.append((ny, nx))
    return ~fora


def filtra(m, tipo, raio):
    """Morfologia via Pillow: MaxFilter dilata, MinFilter erode."""
    im = Image.fromarray((m * 255).astype(np.uint8))
    f = ImageFilter.MaxFilter if tipo == 'dilata' else ImageFilter.MinFilter
    return np.asarray(im.filter(f(raio))) > 127


def segmentar(a, verboso=True):
    """a: array HxWx3 normalizado em 0..1. Devolve mascara booleana do braco."""
    r, g, b = a[..., 0], a[..., 1], a[..., 2]
    mx, mn = a.max(2), a.min(2)
    s = np.where(mx > 0, (mx - mn) / np.maximum(mx, 1e-6), 0)
    v = mx

    # vermelho puro (placa "ST" e extintor do fundo) nao e o braco: o laranja
    # da ABB tem verde intermediario, o vermelho da placa nao tem nenhum.
    # O discriminante limpo entre o laranja da ABB e o vermelho do fundo esta
    # no verde: laranja tem G nitidamente acima de B (medido: G-B ~ .20);
    # vermelho puro tem G ~ B. Usar (r-g) sozinho comia a sombra do braco.
    vermelho = (r > 0.30) & ((r - g) > 0.30) & (np.abs(g - b) < 0.05)
    laranja = ((r - b) > 0.20) & (s > 0.30) & (v > 0.12) & ~vermelho
    if verboso: print('semente laranja: %.1f%%' % (laranja.mean() * 100))

    nucleo = filtra(filtra(laranja, 'dilata', 5), 'erode', 5)
    nucleo = maior_componente(nucleo)
    if verboso: print('maior componente: %d px' % nucleo.sum())

    # cresce para as pecas cinzas encostadas: dilata muito, tapa, volta
    largo = tapa_buracos(filtra(nucleo, 'dilata', 21))
    # dentro da regiao larga, aceita tambem cinza escuro/medio (cabos, cabecote)
    # o vermelho so barra o CRESCIMENTO: aplicado na mascara final ele abria
    # buracos nas sombras saturadas do proprio braco (medido: 26 mil px comidos).
    escuro = ((v < 0.62) | (s > 0.22)) & ~vermelho
    corpo = tapa_buracos((largo & escuro) | nucleo)
    corpo = maior_componente(corpo)
    corpo = tapa_buracos(corpo)
    corpo = filtra(filtra(corpo, 'erode', 3), 'dilata', 3)
    # Ultima limpeza: tira o vermelho e tapa de novo. O que era placa do fundo
    # encostada na borda sai; o que era sombra saturada DENTRO do braco virou
    # buraco e volta preenchido. Uma linha resolve os dois casos opostos.
    corpo = tapa_buracos(corpo & ~vermelho)
    if verboso: print('corpo final: %d px (%.1f%%)' % (corpo.sum(), corpo.mean() * 100))
    return corpo


def main():
    im = Image.open(FONTE).convert('RGB')
    a = np.asarray(im).astype(np.float32) / 255
    corpo = segmentar(a)

    alfa = Image.fromarray((corpo * 255).astype(np.uint8)).filter(ImageFilter.GaussianBlur(1.2))
    saida = im.convert('RGBA'); saida.putalpha(alfa)
    os.makedirs(SAIDA, exist_ok=True)
    saida.save(SAIDA + '/recorte.png')

    # prova visual: recorte sobre xadrez
    xad = Image.new('RGB', im.size, '#ffffff')
    px = np.asarray(xad).copy()
    yy, xx = np.mgrid[0:im.size[1], 0:im.size[0]]
    px[((yy // 16 + xx // 16) % 2) == 1] = 220
    xad = Image.fromarray(px)
    xad.paste(saida, (0, 0), saida)
    xad.save(SAIDA + '/prova.png')
    print('ok ->', SAIDA)


if __name__ == '__main__':
    main()
