# -*- coding: utf-8 -*-
"""Gera os assets de marca a partir da ARTE REAL do cliente.

POR QUE ISTO EXISTE. O site publicava um REDESENHO em SVG do logo, e o
cliente reparou: "mudei a logo". Ele nao tinha mandado um logo novo -- mandou
o dele de VOLTA. Medido, `logo/logonova.png` e pixel-identico a
`referencia/i3automations/logo-i3.png`: mesmas dimensoes, mesmo histograma,
44.534 px de navy e 23.370 px de dourado nos dois.

O que o redesenho tinha jogado fora (memorianew.md §3.1):

  logo real                              | o SVG publicado
  ---------------------------------------|--------------------------------
  notebook: tampa + base com entalhe      | monitor: retangulo e barra lisa
  cantos ARREDONDADOS                     | cantos retos
  tela facetada em 5 tons                 | chapado #FDC500
  "i3" em geometrica de terminal redondo  | <rect> e um "3" de lados retos
  wordmark numa terceira face             | nao existia

Deste arquivo saem 12 PNGs. Nada e desenhado aqui: tudo e RECORTE e
RECOLORACAO da arte que o cliente mandou.

----------------------------------------------------------------------------
O KNOCKOUT -- e o metodo importa mais que o resultado

Para fundo escuro a moldura, a base e o wordmark viram branco. O "i3"
CONTINUA NAVY, porque ele fica sobre o dourado e branco sobre #FDC500 daria
1,6:1 -- ilegivel.

BOUNDING BOX NAO FUNCIONA, e isto e um beco sem saida ja registrado
(memorianew.md §3.2). A primeira tentativa foi "preservar o navy dentro da
caixa da tela dourada". A caixa englobava parte da moldura, entao metade dela
virou branca e a outra metade ficou navy -- visivel na prancha de conferencia.

O metodo correto e TOPOLOGICO, nao geometrico: FLOOD FILL a partir da borda
da imagem, atravessando tudo que NAO e dourado. O anel dourado da tela e a
unica fronteira fechada do desenho, entao o que sobra inalcancavel e
exatamente o glifo. Nao ha caixa nenhuma envolvida, e por isso nao ha como a
caixa englobar o que nao devia.

QUANTIZAR ANTES DE RECOLORIR. O arquivo tem 1.914 cores distintas, mas so 7
sao o desenho -- o resto e anti-aliasing. Sem o snap para as 7, os pixels
intermediarios da fronteira navy/dourado nao sao "dourado" para o flood fill,
ele vaza por eles para dentro do anel, e o glifo e alcancado junto. O
anti-aliasing volta correto e mais limpo no downsample com LANCZOS.

Uso: python ferramentas/build_marca.py
"""
import os
import shutil
import sys
from collections import deque

from PIL import Image

RAIZ = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
FONTE = os.path.join(os.path.dirname(RAIZ), 'logo', 'logonova.png')
DEST = os.path.join(RAIZ, 'referencia', 'marca')
BRAND = os.path.join(RAIZ, 'site', 'brand')

# As 7 cores EXATAS do arquivo, por contagem de pixel. Nao sao aproximacoes
# nem uma paleta escolhida: sao as sete cores que a arte tem.
#   #003566  44.534 px  navy da marca            <- valor MEDIDO, um dos dois
#   #FDC500  23.370 px  dourado da marca         <- valor MEDIDO, o outro
#   #F7CA3C  17.099 px  faceta clara da tela
#   #EAB306   7.863 px  faceta media
#   #E0AC0B   7.162 px  faceta escura
#   #FFFFFF   4.741 px  vinco e brilho
#   #FFDC6E   4.344 px  faceta mais clara
PALETA = [
    (0x00, 0x35, 0x66),
    (0xFD, 0xC5, 0x00),
    (0xF7, 0xCA, 0x3C),
    (0xEA, 0xB3, 0x06),
    (0xE0, 0xAC, 0x0B),
    (0xFF, 0xFF, 0xFF),
    (0xFF, 0xDC, 0x6E),
]
NAVY = PALETA[0]
# As cinco faces da tela. Sao ELAS que fecham a fronteira do flood fill, e por
# isso o dourado tem de ser reconhecido em todos os seus tons -- reconhecer so
# o #FDC500 deixaria o anel furado nas facetas e o flood entraria por ali.
OURO = set(PALETA[1:5]) | {PALETA[6]}

# Cada altura tem um consumidor, e nenhuma esta aqui "por garantia":
#   MARCA   32/64/96 -> o nav, que a rende com 32 px de altura. Sao os
#           1x/2x/3x exatos desse slot. 192 e 288 servem quem precisar dela
#           maior sem voltar a arte.
#   LOCKUP  96/192/268 -> rodape (40 px de altura) e INTRO (560 px de
#           LARGURA, que e o slot que decide tudo aqui -- ver abaixo).
#
# 268 E A RESOLUCAO NATIVA DO LOCKUP, e ele entrou em 2026-08-26 para
# consertar um borrao reportado: "melhorar na animacao principalmente, esta
# embacado".
#
# O QUE ESTAVA ERRADO. `marca_lockup()` emitia srcset por DENSIDADE (1x/2x/3x)
# calculada para um slot de 339 px -- que e a largura com que o rodape rende o
# lockup, nao a intro. A intro rende `min(72vw, 560px)`. Medido no navegador,
# a 1440 px e DPR 1:
#
#     natural 339x96   renderizado 560x159   -> AMPLIACAO de 1,65x
#
# E o descritor de densidade nao salva em DPR nenhum, porque ele so troca de
# arquivo quando o DPR troca: em 2x pede 678 para 1120 px de tela, em 3x pede
# 1017 para 1680. **1,65x em todos.** O conserto e trocar densidade por
# descritor de LARGURA com `sizes` (feito em build_paginas.py), e para isso o
# acervo precisa de um arquivo do tamanho que o slot pede.
#
# E O 288 SAIU, porque ele era resolucao FALSA. O recorte do lockup na arte do
# cliente tem 268 px de altura; pedir 288 fazia `gravar()` AMPLIAR 1,07x com
# LANCZOS e gravar 1017x288 de pixel inventado. Um arquivo que se anuncia como
# "3x" e que nao tem a informacao de 3x e pior que nao ter o arquivo: o
# navegador o escolhe e paga a banda por nada. 268 e o teto real da arte, e a
# intro em 560 px passa de 1,65x para 1,18x no pior caso (DPR 2).
ALT_MARCA = [32, 64, 96, 192, 268]
ALT_LOCKUP = [96, 192, 268]

# O ACERVO E O QUE VAI AO AR SAO COISAS DIFERENTES. `referencia/marca/` guarda
# os 17 arquivos -- inclusive os que nenhuma pagina usa hoje, porque gerar de
# novo custa uma rodada de flood fill e ter a variante pronta custa 20 KB no
# repositorio, que nao e deploy.
#
# `site/brand/` recebe SO o que alguma pagina referencia. `varredura.py`
# acusava dez PNGs orfaos ali, ~200 KB de deploy que nenhum <img> pedia:
#
#   nav ............... logo-marca-32/64/96          (1x/2x/3x de 32px)
#   intro e rodape .... logo-completo-branco-268           (UM arquivo, nativo)
#
# O lockup deixou de ter srcset em 2026-08-26: a nativa (946x268, 25,3 KB)
# pesa MENOS que a de 192 (678x192, 39,7 KB) e tem 2x mais pixel, porque a
# arte e chapada em 7 cores e quem engorda os derivados e o anti-aliasing do
# LANCZOS. A razao inteira esta em `marca_lockup()`, em build_paginas.py.
#
# O lockup NAVY e a marca em knockout nao tem consumidor: toda superficie que
# carrega o lockup hoje e escura, e o nav carrega a marca sobre superficie
# clara. No dia em que houver um lockup sobre branco, ele ja esta gerado --
# basta acrescentar o nome aqui.
PUBLICADOS = frozenset(
    ['logo-marca-%d.png' % a for a in (32, 64, 96)]
    + ['logo-completo-branco-268.png']
)


def quantizar(im):
    """Snap de cada pixel opaco para a cor mais proxima das 7. Devolve
    (rgb, alfa) como listas planas, porque o flood fill trabalha em indices."""
    im = im.convert('RGBA')
    w, h = im.size
    px = list(im.getdata())
    rgb = [None] * (w * h)
    alfa = [0] * (w * h)
    cache = {}
    for i, (r, g, b, a) in enumerate(px):
        alfa[i] = a
        if a < 8:
            continue
        k = (r, g, b)
        c = cache.get(k)
        if c is None:
            # distancia euclidiana no RGB. Basta: as 7 cores estao longe umas
            # das outras, e o que se decide aqui e so "de qual face este pixel
            # de anti-aliasing veio".
            c = min(PALETA, key=lambda p: (p[0] - r) ** 2 + (p[1] - g) ** 2 + (p[2] - b) ** 2)
            cache[k] = c
        rgb[i] = c
    return w, h, rgb, alfa


def alcancavel(w, h, rgb, alfa):
    """Flood fill 4-conectado a partir de TODA a borda da imagem, atravessando
    transparencia e qualquer cor que nao seja dourada. Devolve o conjunto de
    indices alcancados.

    O dourado e parede. Como o anel da tela e fechado, o miolo -- as facetas e
    o glifo "i3" -- fica do lado de dentro e nunca e alcancado."""
    visto = bytearray(w * h)
    q = deque()

    def semear(i):
        if not visto[i] and rgb[i] not in OURO:
            visto[i] = 1
            q.append(i)

    for x in range(w):
        semear(x)
        semear((h - 1) * w + x)
    for y in range(h):
        semear(y * w)
        semear(y * w + w - 1)

    while q:
        i = q.popleft()
        x = i % w
        y = i // w
        if x > 0:
            semear(i - 1)
        if x < w - 1:
            semear(i + 1)
        if y > 0:
            semear(i - w)
        if y < h - 1:
            semear(i + w)
    return visto


def caixa(alfa, w, h, x0=0, x1=None):
    """Menor retangulo que contem pixel opaco, opcionalmente limitado em x."""
    x1 = w - 1 if x1 is None else x1
    ax0, ay0, ax1, ay1 = w, h, -1, -1
    for y in range(h):
        linha = y * w
        for x in range(x0, x1 + 1):
            if alfa[linha + x] >= 8:
                if x < ax0: ax0 = x
                if x > ax1: ax1 = x
                if y < ay0: ay0 = y
                if y > ay1: ay1 = y
    return ax0, ay0, ax1, ay1


def componente_marca(w, h, alfa):
    """A MARCA ISOLADA e o maior componente conexo de pixel opaco: o notebook
    inteiro e um desenho so. Cada letra do wordmark e um componente separado e
    muito menor. Achar a marca assim -- e nao por um x de corte escrito a mao --
    e o que faz o recorte sobreviver a um logo com espacamento diferente."""
    visto = bytearray(w * h)
    melhor = None
    for s in range(w * h):
        if alfa[s] < 8 or visto[s]:
            continue
        q = deque([s])
        visto[s] = 1
        n = 0
        x0 = x1 = s % w
        y0 = y1 = s // w
        while q:
            i = q.popleft()
            n += 1
            x = i % w
            y = i // w
            if x < x0: x0 = x
            if x > x1: x1 = x
            if y < y0: y0 = y
            if y > y1: y1 = y
            for j, ok in ((i - 1, x > 0), (i + 1, x < w - 1),
                          (i - w, y > 0), (i + w, y < h - 1)):
                if ok and not visto[j] and alfa[j] >= 8:
                    visto[j] = 1
                    q.append(j)
        if melhor is None or n > melhor[0]:
            melhor = (n, x0, y0, x1, y1)
    return melhor


def montar(w, h, rgb, alfa, knockout=None):
    """Reconstroi uma imagem RGBA. Se `knockout` vier, os pixels ALCANCADOS
    pelo flood fill que forem navy ou branco viram branco -- e so eles."""
    saida = []
    for i in range(w * h):
        a = alfa[i]
        if a < 8:
            saida.append((0, 0, 0, 0))
            continue
        c = rgb[i]
        if knockout is not None and knockout[i] and c not in OURO:
            c = (0xFF, 0xFF, 0xFF)
        saida.append((c[0], c[1], c[2], a))
    im = Image.new('RGBA', (w, h))
    im.putdata(saida)
    return im


def gravar(im, corte, nome, alturas):
    """Recorta e reduz. LANCZOS porque e o filtro que devolve o anti-aliasing
    que a quantizacao tirou -- e devolve MELHOR do que o original tinha, porque
    reamostra de arestas limpas em vez de arestas ja borradas.

    E SO REDUZ. Pedir uma altura acima da nativa passava batido e gravava
    pixel inventado com cara de asset: era assim que `logo-completo-*-288.png`
    existia, 1017x288 LANCZOS-ado de um recorte de 270 px de altura. O
    navegador nao tem como saber que o arquivo nao tem a informacao que o nome
    promete -- ele escolhe pelo descritor e paga a banda. Agora o pedido acima
    da nativa GRITA no build em vez de virar arquivo."""
    peca = im.crop(corte)
    lw, lh = peca.size
    for alt in alturas:
        if alt > lh:
            print('   ! %s-%d: %d px acima da nativa (%d) -- NAO gravado'
                  % (nome, alt, alt, lh))
            continue
        larg = int(round(lw * alt / float(lh)))
        red = peca if alt == lh else peca.resize((larg, alt), Image.LANCZOS)
        larg = red.size[0]
        cam = os.path.join(DEST, '%s-%d.png' % (nome, alt))
        red.save(cam, optimize=True)
        print('   %-28s %4dx%-4d %6.1f KB' % (
            os.path.basename(cam), larg, alt, os.path.getsize(cam) / 1024.0))


def main():
    if not os.path.exists(FONTE):
        sys.exit('arte nao encontrada: %s' % FONTE)
    for d in (DEST, BRAND):
        if not os.path.isdir(d):
            os.makedirs(d)

    original = Image.open(FONTE)
    print('fonte: %s  %dx%d  %d cores distintas'
          % (os.path.relpath(FONTE, RAIZ), original.size[0], original.size[1],
             len(original.convert('RGBA').getcolors(1 << 24) or [])))

    w, h, rgb, alfa = quantizar(original)
    opacos = sum(1 for a in alfa if a >= 8)
    print('quantizado para as 7 cores exatas: %d px opacos' % opacos)

    # --- os dois recortes
    n, mx0, my0, mx1, my1 = componente_marca(w, h, alfa)
    print('marca isolada: maior componente conexo, %d px, x %d..%d y %d..%d'
          % (n, mx0, mx1, my0, my1))
    lx0, ly0, lx1, ly1 = caixa(alfa, w, h)
    corte_marca = (mx0, my0, mx1 + 1, my1 + 1)
    corte_lock = (lx0, ly0, lx1 + 1, ly1 + 1)
    print('   marca   %dx%d  proporcao %.3f:1'
          % (mx1 - mx0 + 1, my1 - my0 + 1, (mx1 - mx0 + 1) / float(my1 - my0 + 1)))
    print('   lockup  %dx%d  proporcao %.3f:1'
          % (lx1 - lx0 + 1, ly1 - ly0 + 1, (lx1 - lx0 + 1) / float(ly1 - ly0 + 1)))

    # --- o knockout
    ko = alcancavel(w, h, rgb, alfa)
    alcancado = sum(1 for i in range(w * h) if ko[i] and alfa[i] >= 8)
    preservado = opacos - alcancado
    print('flood fill da borda atravessando nao-dourado:')
    print('   %6d px alcancados  -> knockout' % alcancado)
    print('   %6d px inalcancaveis -> preservados (o glifo e as facetas)' % preservado)

    normal = montar(w, h, rgb, alfa)
    branco = montar(w, h, rgb, alfa, ko)

    print('\n== navy ==')
    gravar(normal, corte_lock, 'logo-completo', ALT_LOCKUP)
    gravar(normal, corte_marca, 'logo-marca', ALT_MARCA)
    print('== knockout ==')
    gravar(branco, corte_lock, 'logo-completo-branco', ALT_LOCKUP)
    gravar(branco, corte_marca, 'logo-marca-branco', ALT_MARCA)

    # A arte de origem viaja junto com os derivados: sem ela, daqui a um ano
    # ninguem sabe de onde os 12 PNGs sairam.
    original.save(os.path.join(DEST, 'logo-original.png'))
    n = (len(ALT_LOCKUP) + len(ALT_MARCA)) * 2 + 1
    print('\n%d arquivos em %s' % (n, os.path.relpath(DEST, RAIZ)))

    # --- PUBLICA. `referencia/marca/` e o acervo; `site/brand/` e o que vai
    #     ao ar. Sem este passo os PNGs existem no repositorio e o <img> do nav
    #     aponta para o vazio -- que foi exatamente o que aconteceu na primeira
    #     passagem, e o sintoma foi um icone quebrado no nav de nove paginas.
    #     `logo-original.png` NAO e publicado: e a arte de origem, nao um asset
    #     de pagina.
    publicados = 0
    bytes_pub = 0
    for f in sorted(os.listdir(DEST)):
        if f not in PUBLICADOS:
            continue
        destino = os.path.join(BRAND, f)
        shutil.copy2(os.path.join(DEST, f), destino)
        publicados += 1
        bytes_pub += os.path.getsize(destino)
    print('%d publicados em %s  (%.1f KB)'
          % (publicados, os.path.relpath(BRAND, RAIZ), bytes_pub / 1024.0))

    # E VARRE O QUE DEIXOU DE SER PUBLICADO. Sem isto, tirar um nome de
    # `PUBLICADOS` nao tira o arquivo do deploy: ele fica em `site/brand/`
    # como orfao, e o unico a reclamar e `varredura.py`, depois. Foi o que
    # aconteceu ao aposentar os tres arquivos de srcset do lockup em
    # 2026-08-26 -- 125 KB continuaram no deploy sem nenhum <img> pedindo.
    #
    # So mexe no que ESTE script produz (`logo-*`): os icones de favicon e
    # apple-touch vivem no mesmo diretorio e saem de outro lugar.
    varridos = 0
    for f in sorted(os.listdir(BRAND)):
        if f.startswith('logo-') and f not in PUBLICADOS:
            os.remove(os.path.join(BRAND, f))
            print('   - %s (orfao, removido do deploy)' % f)
            varridos += 1
    if not varridos:
        print('   sem orfaos em %s' % os.path.relpath(BRAND, RAIZ))


if __name__ == '__main__':
    main()
