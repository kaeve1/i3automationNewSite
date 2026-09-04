# -*- coding: utf-8 -*-
"""Extrai o contorno do Golfo/Sudeste para a carta de contact (js/carta.js).

POR QUE EXISTE. A primeira versao da carta era so reticula e duas cruzes, sem
contorno nenhum -- eu me recusei a desenhar litoral de memoria, que seria
inventar geografia. O usuario nao entendeu a peca, e ele tem razao: uma
reticula com duas marcas nao le como mapa.

A saida honesta nao era desenhar de cabeca, era usar DADO DE VERDADE. A fonte
esta em `referencia/us-states.geojson` -- fronteiras estaduais dos EUA,
dominio publico (derivadas do TIGER do US Census). Guardada no repositorio de
proposito: a extracao roda offline e o resultado e reproduzivel.

O QUE ELE FAZ. Recorta os estados que aparecem na janela da carta, descarta os
aneis inteiramente fora dela, simplifica por Douglas-Peucker e imprime o array
pronto para colar em `carta.js`.

  eps 0.06 -> 381 pontos     detalhe que a escala da carta nao mostra
  eps 0.10 -> 246 pontos     ESCOLHIDO
  eps 0.15 -> 172 pontos     a peninsula da Florida comeca a ficar reta

Uso: python ferramentas/extrair_costa.py [eps]
"""
import json
import math
import os
import sys

RAIZ = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
FONTE = os.path.join(RAIZ, 'referencia', 'us-states.geojson')

# Os estados que a janela da carta alcanca. Nao e "todos": cada anel a mais e
# peso no arquivo por um contorno que sai da moldura.
ALVO = {'Texas', 'Louisiana', 'Mississippi', 'Alabama', 'Florida', 'Georgia',
        'Arkansas', 'Oklahoma', 'Tennessee', 'South Carolina', 'New Mexico'}
JANELA = (-101.5, -75.5, 23.0, 35.5)      # oeste, leste, sul, norte


def douglas_peucker(pts, eps):
    if len(pts) < 3:
        return pts
    def dist(p, a, b):
        dx, dy = b[0] - a[0], b[1] - a[1]
        if dx == 0 and dy == 0:
            return math.hypot(p[0] - a[0], p[1] - a[1])
        t = max(0, min(1, ((p[0] - a[0]) * dx + (p[1] - a[1]) * dy) / (dx * dx + dy * dy)))
        return math.hypot(p[0] - (a[0] + t * dx), p[1] - (a[1] + t * dy))
    dmax, idx = 0, 0
    for i in range(1, len(pts) - 1):
        d = dist(pts[i], pts[0], pts[-1])
        if d > dmax:
            dmax, idx = d, i
    if dmax > eps:
        return douglas_peucker(pts[:idx + 1], eps)[:-1] + douglas_peucker(pts[idx:], eps)
    return [pts[0], pts[-1]]


def main():
    eps = float(sys.argv[1]) if len(sys.argv) > 1 else 0.10
    O, L, S, N = JANELA
    with open(FONTE, encoding='utf-8') as fh:
        d = json.load(fh)

    aneis, total = [], 0
    for f in d['features']:
        if f['properties'].get('name') not in ALVO:
            continue
        g = f['geometry']
        polis = (g['coordinates'] if g['type'] == 'Polygon'
                 else [c[0] for c in g['coordinates']])
        for anel in polis:
            pts = [(p[0], p[1]) for p in anel]
            if len(pts) < 8:
                continue
            # anel inteiramente fora da janela nao entra: e peso por nada
            if all(not (O <= x <= L and S <= y <= N) for x, y in pts):
                continue
            simp = douglas_peucker(pts, eps)
            if len(simp) < 6:
                continue
            aneis.append(simp)
            total += len(simp)

    print('/* Contorno do Golfo/Sudeste, extraido de referencia/us-states.geojson')
    print('   por ferramentas/extrair_costa.py (Douglas-Peucker, eps %.2f).' % eps)
    print('   %d aneis, %d pontos. Fonte de dominio publico (US Census TIGER).' % (len(aneis), total))
    print('   Duas casas decimais = ~1 km, muito abaixo do que esta escala mostra. */')
    print('  var COSTA = [')
    for a in aneis:
        print('    [' + ','.join('%.2f,%.2f' % (x, y) for x, y in a) + '],')
    print('  ];')
    sys.stderr.write('%d aneis, %d pontos\n' % (len(aneis), total))


if __name__ == '__main__':
    main()
