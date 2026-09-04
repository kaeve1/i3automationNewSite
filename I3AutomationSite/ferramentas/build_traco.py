# -*- coding: utf-8 -*-
"""Extrai o TRACADO DE ARESTA de uma fotografia e emite SVG que se desenha.

POR QUE SVG E NAO PNG, e por que nao Lottie.

O projeto ja tem esse vocabulario: `site/img/setores/*-traco-*.png` sao o
tracado de aresta da propria fotografia, em branco sobre transparente. Mas PNG
nao se DESENHA -- ele so pode ser revelado por clip-path, que e um gesto de
cortina e nao de caneta.

Lottie faria o traco se desenhar, e custa `lottie-web` (~250 KB gzip) mais os
JSON: dependencia de runtime que quebra a regra de sem framework e sem build
step no deploy (design.md §6.3). E um JSON de Lottie nao herda os tokens de
cor do site -- ele carrega as cores dentro.

SVG com `stroke-dasharray`/`stroke-dashoffset` faz exatamente o que Lottie
faria aqui, custa zero KB de biblioteca, e herda `currentColor`. O site JA faz
isso na regua do heroi. Este arquivo so leva o mesmo gesto para uma
fotografia.

----------------------------------------------------------------------------
O METODO, em cinco passos

  1. Cinza, com um desfoque leve antes. Sem o desfoque o detector encontra o
     GRAO do sensor e devolve dez mil segmentos de tres pixels.
  2. Sobel em dois eixos, por convolucao 3x3 com o kernel do PIL. Nao ha
     scipy neste ambiente e nao faz falta: Sobel e uma convolucao, e
     `ImageFilter.Kernel` faz convolucao.
  3. Limiar por PERCENTIL, nao por valor absoluto. Um limiar fixo funciona
     numa foto e reprova na seguinte, porque depende do contraste da cena.
  4. Afinamento e caminhada 8-conectada: cada cadeia de pixel de aresta vira
     uma polilinha.
  5. Douglas-Peucker para simplificar. Uma aresta reta de 400 px nao precisa
     de 400 pontos -- precisa de dois, e a diferenca aparece no tamanho do
     arquivo, que aqui e HTML inline.

`pathLength="100"` em todo caminho normaliza os comprimentos: um unico par
dasharray/dashoffset no CSS serve para todos, e nenhuma medicao de caminho
precisa acontecer em JS. E a mesma tecnica que a intro usava.

Uso:
  python ferramentas/build_traco.py <entrada.jpg> <saida.svg> [--largura 1600]
"""
import math
import os
import sys

from PIL import Image, ImageFilter


def sobel(im):
    """Magnitude do gradiente. Duas convolucoes 3x3 e uma hipotenusa."""
    kx = ImageFilter.Kernel((3, 3), [-1, 0, 1, -2, 0, 2, -1, 0, 1], scale=1, offset=128)
    ky = ImageFilter.Kernel((3, 3), [-1, -2, -1, 0, 0, 0, 1, 2, 1], scale=1, offset=128)
    gx = im.filter(kx).load()
    gy = im.filter(ky).load()
    w, h = im.size
    mag = Image.new('L', (w, h))
    p = mag.load()
    for y in range(h):
        for x in range(w):
            a = gx[x, y] - 128
            b = gy[x, y] - 128
            v = int(math.sqrt(a * a + b * b))
            p[x, y] = 255 if v > 255 else v
    return mag


def limiar_percentil(mag, manter):
    """Devolve o valor que deixa passar `manter` da imagem. Percentil e nao
    valor fixo: um limiar absoluto acerta numa foto e erra na proxima."""
    h = mag.histogram()
    total = sum(h)
    alvo = total * (1 - manter)
    acc = 0
    for v, n in enumerate(h):
        acc += n
        if acc >= alvo:
            return v
    return 255


def afinar(pix, w, h):
    """Afinamento barato: um pixel de aresta so sobrevive se for o MAXIMO
    local na direcao em que a aresta e mais forte. Nao e Canny -- nao precisa
    ser. O que se quer aqui e uma linha de um pixel para caminhar, e nao uma
    deteccao otima."""
    fino = bytearray(w * h)
    for y in range(1, h - 1):
        for x in range(1, w - 1):
            v = pix[x, y]
            if not v:
                continue
            if v >= pix[x - 1, y] and v >= pix[x + 1, y]:
                fino[y * w + x] = 1
            elif v >= pix[x, y - 1] and v >= pix[x, y + 1]:
                fino[y * w + x] = 1
    return fino


VIZ = ((1, 0), (1, 1), (0, 1), (-1, 1), (-1, 0), (-1, -1), (0, -1), (1, -1))


def cadeias(fino, w, h, minimo):
    """Caminhada 8-conectada. Cada cadeia de pixel de aresta vira uma
    polilinha; cadeias menores que `minimo` sao ruido e caem fora."""
    out = []
    for s in range(w * h):
        if not fino[s]:
            continue
        # so comeca a caminhar de uma PONTA (um vizinho) ou de um pixel solto,
        # para a polilinha sair na ordem certa em vez de partida ao meio
        x0, y0 = s % w, s // w
        n = 0
        for dx, dy in VIZ:
            nx, ny = x0 + dx, y0 + dy
            if 0 <= nx < w and 0 <= ny < h and fino[ny * w + nx]:
                n += 1
        if n > 1:
            continue
        pts = []
        i = s
        while i is not None and fino[i]:
            fino[i] = 0
            x, y = i % w, i // w
            pts.append((x, y))
            prox = None
            for dx, dy in VIZ:
                nx, ny = x + dx, y + dy
                if 0 <= nx < w and 0 <= ny < h and fino[ny * w + nx]:
                    prox = ny * w + nx
                    break
            i = prox
        if len(pts) >= minimo:
            out.append(pts)
    # o que sobrou sao aneis fechados, que nao tem ponta. Pega-os tambem.
    for s in range(w * h):
        if not fino[s]:
            continue
        pts = []
        i = s
        while i is not None and fino[i]:
            fino[i] = 0
            x, y = i % w, i // w
            pts.append((x, y))
            prox = None
            for dx, dy in VIZ:
                nx, ny = x + dx, y + dy
                if 0 <= nx < w and 0 <= ny < h and fino[ny * w + nx]:
                    prox = ny * w + nx
                    break
            i = prox
        if len(pts) >= minimo:
            out.append(pts)
    return out


def dp(pts, eps):
    """Douglas-Peucker. Uma aresta reta de 400 px precisa de dois pontos, e
    nao de 400 -- e a diferenca aparece no peso do HTML, porque este SVG vai
    INLINE na pagina."""
    if len(pts) < 3:
        return pts
    x0, y0 = pts[0]
    x1, y1 = pts[-1]
    dx, dy = x1 - x0, y1 - y0
    norma = math.hypot(dx, dy) or 1.0
    pior, idx = 0.0, 0
    for i in range(1, len(pts) - 1):
        px, py = pts[i]
        d = abs(dy * px - dx * py + x1 * y0 - y1 * x0) / norma
        if d > pior:
            pior, idx = d, i
    if pior <= eps:
        return [pts[0], pts[-1]]
    return dp(pts[:idx + 1], eps)[:-1] + dp(pts[idx:], eps)


def caminho(pts, esc):
    d = ['M%.1f %.1f' % (pts[0][0] * esc, pts[0][1] * esc)]
    for x, y in pts[1:]:
        d.append('L%.1f %.1f' % (x * esc, y * esc))
    return ''.join(d)


def main():
    if len(sys.argv) < 3:
        sys.exit(__doc__.strip().split('Uso:')[-1].strip())
    entrada, saida = sys.argv[1], sys.argv[2]
    larg_svg = 1600
    if '--largura' in sys.argv:
        larg_svg = int(sys.argv[sys.argv.index('--largura') + 1])

    im = Image.open(entrada).convert('L')
    orig = im.size
    # Trabalha pequeno: o tracado nao ganha nada com 5184 px de fonte, e a
    # caminhada e O(pixels). 900 px de largura da aresta de sobra e roda em
    # segundos em vez de minutos.
    trab = 900
    im = im.resize((trab, int(round(trab * orig[1] / float(orig[0])))), Image.LANCZOS)
    # Desfoque ANTES do gradiente. Sem ele o detector acha o grao do sensor e
    # devolve dez mil segmentos de tres pixels.
    im = im.filter(ImageFilter.GaussianBlur(1.4))
    w, h = im.size

    mag = sobel(im)
    lim = limiar_percentil(mag, 0.055)   # 5,5% dos pixels viram aresta
    px = mag.load()
    for y in range(h):
        for x in range(w):
            if px[x, y] < lim:
                px[x, y] = 0
    fino = afinar(px, w, h)

    sys.setrecursionlimit(10000)
    linhas = cadeias(fino, w, h, minimo=26)
    linhas = [dp(p, 1.6) for p in linhas]
    # As mais LONGAS sao as que carregam o desenho: a moldura do rele, a
    # regua de bornes, o vinco do fio. As curtas sao textura.
    linhas.sort(key=lambda p: -sum(math.hypot(p[i + 1][0] - p[i][0], p[i + 1][1] - p[i][1])
                                   for i in range(len(p) - 1)))
    linhas = linhas[:120]

    esc = larg_svg / float(w)
    alt_svg = int(round(h * esc))
    ds = [caminho(p, esc) for p in linhas]
    pontos = sum(len(p) for p in linhas)

    corpo = ''.join('<path pathLength="100" d="%s"/>' % d for d in ds)
    svg = ('<svg class="traco__svg" viewBox="0 0 %d %d" fill="none" '
           'stroke="currentColor" stroke-width="1.4" stroke-linecap="round" '
           'stroke-linejoin="round" aria-hidden="true" focusable="false" '
           'preserveAspectRatio="xMidYMid slice">%s</svg>'
           % (larg_svg, alt_svg, corpo))

    with open(saida, 'w', encoding='utf-8') as f:
        f.write(svg)

    print('%s  %dx%d' % (os.path.basename(entrada), orig[0], orig[1]))
    print('   limiar por percentil: %d (5,5%% dos pixels)' % lim)
    print('   %d caminhos, %d pontos apos Douglas-Peucker' % (len(linhas), pontos))
    print('   %s  %.1f KB  viewBox %dx%d'
          % (os.path.relpath(saida), os.path.getsize(saida) / 1024.0, larg_svg, alt_svg))


if __name__ == '__main__':
    main()
