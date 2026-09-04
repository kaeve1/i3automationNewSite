# -*- coding: utf-8 -*-
"""Corta a arte real da marca na DOBRADICA do notebook: TAMPA e BASE.

POR QUE CORTAR E NAO DESENHAR. A intro nova abre o notebook, e abrir exige
duas pecas que giram uma em relacao a outra. A tentacao e desenhar um notebook
em SVG -- e seria repetir exatamente o erro que `design.md` §3.5 registra: a
PRIMEIRA intro do projeto morreu porque desenhava o REDESENHO da marca, e o
cliente reparou. Aqui nao ha desenho nenhum: as duas pecas sao RECORTES da arte
real, no pixel, como tudo o que `build_marca.py` produz.

TUDO AQUI E MEDIDO NO ARQUIVO, nao estimado. Varrendo `logo-original.png`
(1024x387) por perfil de coluna e de linha:

    notebook (marca isolada) ... x 40..459   y  64..333
    wordmark ................... x ~470..985 y 114..263
    aresta de cima da tampa .... y  65..68    (362 px brancos)
    DOBRADICA .................. y 298..300   (280 px brancos)
    entalhe do trackpad ........ y 306..308   (116 px brancos)
    aresta de baixo da base .... y 329..332   (382 px brancos)

A dobradica e a linha em que a tampa acaba e a barra da base comeca. Ela nao e
o pico de brancos -- o pico e a aresta INFERIOR da base, em 329. Procurar o
pico foi a primeira tentativa e cortou a marca no lugar errado, deixando uma
"base" de 5px.

Uso: python ferramentas/corte_marca.py
"""
import os

from PIL import Image

RAIZ = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
FONTE = os.path.join(RAIZ, 'referencia', 'marca', 'logo-original.png')
DEST = os.path.join(RAIZ, 'site', 'brand')

# A faixa em que a dobradica pode estar, em fracao da altura da marca. Ela
# existe para o detector nao confundir a dobradica com a aresta de baixo da
# base: as duas sao linhas brancas longas, e so a POSICAO as distingue.
FAIXA = (0.80, 0.92)


def branco_por_linha(px, x0, x1, alt):
    """Quantos pixels quase-brancos e opacos por linha, dentro da marca."""
    return [sum(1 for x in range(x0, x1, 2)
                if px[x, y][3] > 128 and min(px[x, y][:3]) > 200)
            for y in range(alt)]


def caixa_notebook(im):
    """A marca isolada, com a BASE INTEIRA.

    A primeira versao pegava as colunas com tinta na faixa do TOPO -- o que
    separa o notebook do wordmark sem depender de um vao transparente entre os
    dois, e nao ha. Mas devolvia x 61..439, e **a base do notebook e MAIS LARGA
    que a tampa** (x 40..459): e o resalto que faz a peca ler como laptop, e o
    corte estava comendo 21px de cada lado dele.

    O DISCRIMINADOR E A FAIXA DE BAIXO, e ele e exato em vez de tolerante.
    Tolerar "vaos de ate N px" foi a segunda tentativa e engoliu o wordmark: o
    vao entre a marca e ele tem ~10 colunas, perto demais de qualquer N que
    ainda absorva as folgas internas do desenho.

    So a BASE do notebook chega ao ultimo quinto da altura -- o wordmark vive
    em y 114..263, bem acima. Entao as colunas com tinta nas 20 linhas de
    baixo sao a base, e a base e a parte mais larga da marca.

    E A BORDA DIREITA NAO E A DA BASE, e este foi um defeito de verdade, visto
    no render: sobrava *"um pedaco do texto a direita do notebook"* -- um risco
    branco de 3x18px colado na borda da tampa.

    A BASE E O WORDMARK SE SOBREPOEM EM UMA COLUNA. Medido:

        x=458   base 23 linhas   wordmark  0
        x=459   base 21 linhas   wordmark 10   <- a ponta arredondada da base
        x=460   base  0 linhas   wordmark 20      e a primeira letra dividem

    Cortar pela base (x1=460) levava junto 10 pixels da primeira letra do
    wordmark, e eles reapareciam flutuando ao lado do notebook na intro.

    A regra certa: a DIREITA DA TAMPA (x>438) qualquer tinta na faixa do
    wordmark (y 114..263) e wordmark, porque a tampa nao chega ali. O corte vai
    ate a primeira coluna assim. Custa a ponta anti-serrilhada do canto da
    base, que tem 21 linhas de 1px -- invisivel; o risco branco nao era."""
    px = im.load()
    W, H = im.size
    y_fim = im.split()[3].getbbox()[3]
    cols = [x for x in range(W)
            if any(px[x, y][3] > 128 for y in range(y_fim - 20, y_fim))]
    x0 = min(cols)
    x1 = max(cols) + 1

    # onde o wordmark comeca, a direita da tampa
    # ONDE O WORDMARK COMECA, achado pelo VAO e nao por um x de partida fixo.
    #
    # Na faixa de altura do wordmark (y 114..263) so existem duas coisas: a
    # TAMPA, a esquerda, e o WORDMARK, a direita. Entre as duas ha um vao de
    # colunas totalmente vazias. Achar esse vao e tomar o fim dele da o comeco
    # do wordmark sem depender de nenhum numero chutado -- partir de x=439
    # fixo caiu dentro da franja da propria tampa e cortou a marca em 439.
    #
    # E O TESTE E `alfa > 0`, nao `> 128`. Cortar no primeiro pixel OPACO do
    # wordmark ainda deixava a franja anti-serrilhada dele (alfa ate 73 na
    # coluna 458), e ela aparecia na intro como um risco tenue no mesmo lugar
    # do risco forte -- mais fraco, e ainda visivel. O corte tem de cair antes
    # de QUALQUER tinta do wordmark.
    faixa_wm = range(114, 264)
    tem_wm = [any(px[x, y][3] > 0 for y in faixa_wm) for x in range(W)]
    # A varredura comeca na TAMPA (o primeiro x com tinta nessa faixa) e nao em
    # `x0`: `x0` e a borda da BASE, que nasce ~20 colunas a esquerda da tampa,
    # e essas 20 colunas vazias na faixa do wordmark ja contavam como vao --
    # o corte caia em 61, na propria tampa.
    esq_tampa = next(x for x in range(W) if tem_wm[x])
    vao = 0
    for x in range(esq_tampa, W):
        if tem_wm[x]:
            if vao > 12:          # o vao entre a tampa e o wordmark
                x1 = min(x1, x)
                break
            vao = 0
        else:
            vao += 1

    linhas = [y for y in range(H) if any(px[x, y][3] > 128 for x in range(x0, x1))]
    return x0, min(linhas), x1, max(linhas) + 1


def dobradica(im, caixa):
    x0, y0, x1, y1 = caixa
    cont = branco_por_linha(im.load(), x0, x1, im.size[1])
    alto = y1 - y0
    ini, fim = int(y0 + alto * FAIXA[0]), int(y0 + alto * FAIXA[1])
    return max(range(ini, fim), key=lambda y: cont[y]), cont


def main():
    im = Image.open(FONTE).convert('RGBA')
    caixa = caixa_notebook(im)
    y_dob, cont = dobradica(im, caixa)
    x0, y0, x1, y1 = caixa

    print('lockup ............ %dx%d' % im.size)
    print('notebook .......... x %d..%d  y %d..%d  (%dx%d)'
          % (x0, x1, y0, y1, x1 - x0, y1 - y0))
    print('DOBRADICA ......... y=%d  (%d px brancos, %.1f%% da altura)'
          % (y_dob, cont[y_dob], 100.0 * (y_dob - y0) / (y1 - y0)))
    print()

    tampa = im.crop((x0, y0, x1, y_dob))
    base = im.crop((x0, y_dob, x1, y1))
    for nome, peca in (('logo-tampa', tampa), ('logo-base', base)):
        p = os.path.join(DEST, nome + '.png')
        peca.save(p, optimize=True)
        print('   %-30s %3dx%-3d  %5.1f KB'
              % (os.path.relpath(p, RAIZ).replace('\\', '/'),
                 peca.width, peca.height, os.path.getsize(p) / 1024.0))

    tot = tampa.height + base.height
    print()
    print('OS NUMEROS QUE O CSS PRECISA (fracoes da LARGURA do notebook):')
    print('   --nb-alt ...... %.4f   altura total / largura' % (tot / float(x1 - x0)))
    print('   --nb-tampa .... %.4f   altura da tampa / largura' % (tampa.height / float(x1 - x0)))
    print('   --nb-base ..... %.4f   altura da base / largura' % (base.height / float(x1 - x0)))
    print('   tampa e %.2f%% da altura do notebook' % (100.0 * tampa.height / tot))
    print()
    print('A TELA DOURADA DENTRO DA TAMPA (para o veu abrir exatamente nela):')
    px = im.load()
    ouro = [(x, y) for y in range(y0, y_dob) for x in range(x0, x1, 2)
            if px[x, y][3] > 128 and px[x, y][0] > 180 and px[x, y][2] < 120]
    if ouro:
        gx0, gx1 = min(p[0] for p in ouro), max(p[0] for p in ouro)
        gy0, gy1 = min(p[1] for p in ouro), max(p[1] for p in ouro)
        print('   tela .......... x %d..%d  y %d..%d' % (gx0, gx1, gy0, gy1))
        print('   --tela-x ...... %.4f  (borda esquerda / largura do notebook)'
              % ((gx0 - x0) / float(x1 - x0)))
        print('   --tela-l ...... %.4f  (largura da tela / largura do notebook)'
              % ((gx1 - gx0) / float(x1 - x0)))
        print('   --tela-y ...... %.4f  (borda de cima / largura do notebook)'
              % ((gy0 - y0) / float(x1 - x0)))
        print('   --tela-a ...... %.4f  (altura da tela / largura do notebook)'
              % ((gy1 - gy0) / float(x1 - x0)))


if __name__ == '__main__':
    main()
