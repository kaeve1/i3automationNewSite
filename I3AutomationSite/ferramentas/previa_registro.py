# -*- coding: utf-8 -*-
"""Confere FORA DO NAVEGADOR as tres composicoes que mudaram nesta entrega.

Regra do projeto (CLAUDE.md #3): se um numero entra no CSS, existe a conta que
o produziu. Este arquivo e essa conta para:

  1. o TEMPO da prancha da home -- em que ponto da rolagem cada folha fecha, e
     onde a fileira esta na tela nesse instante. Era o defeito reportado ("as
     fotos so aparecem quando voce arrasta para quase depois delas") e a
     correcao e aritmetica, nao gosto;

  2. a FICHA DE OBRA de past-performance -- se a coluna de texto cabe, se o
     rotulo em mono cabe na propria coluna, e se a placa e REDUZIDA (nunca
     ampliada) na moldura em que ela vive;

  3. o EQUILIBRIO DAS COLUNAS da galeria, no empilhamento guloso, nas tres
     larguras de coluna que o CSS usa.

Uso: python ferramentas/previa_registro.py
"""
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

RAIZ = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

# --- tokens, copiados do CSS -------------------------------------------------
CONTAINER = 1376
PAD = 48
S3, S4, S5, S6, S7, S8 = 16, 24, 32, 48, 64, 96


def fluido(minimo, vw, maximo, largura):
    """clamp() do CSS, em px."""
    return max(minimo, min(maximo, vw / 100 * largura))


def conteudo(largura):
    return min(CONTAINER, largura) - 2 * PAD


# =============================================================== 1. PRANCHA
# Os valores sao os do CSS §22.1. A ultima folha fecha em .385.
JANELA, PASSO, ATRASO = .16, .055, .06


def altura_prancha(largura):
    """Altura renderizada da prancha, refeita da aritmetica do CSS."""
    c = conteudo(largura)
    col = (c - 3 * S5) / 4          # 4 colunas, gap --s-5
    return (
        1                            # .prancha__datum
        + S5                         # .prancha__vista (height: --s-5)
        + col                        # .prancha__moldura (aspect-ratio 1/1)
        + S3 + 2 * round(12.5 * 1.45)  # legenda: margin-top + 2 linhas
        + S6 + 17                    # .prancha__cota: margin-top + linha
    ), col


def prancha():
    print('== 1. PRANCHA DA HOME — quando cada folha fecha ==')
    print('   A prancha e mais BAIXA que a janela, entao main.js §7 mede a')
    print('   travessia inteira: --p = (vh - topo) / (vh + altura).')
    print('   --p NAO e "quanto dela esta visivel" — e onde ela esta no percurso.')
    print('')
    for vw, vh in ((1440, 900), (1368, 768), (1920, 1080), (1100, 800)):
        h, col = altura_prancha(vw)
        print('   %dx%d — placa %d px, prancha %d px de altura' % (vw, vh, col, h))
        for i in range(4):
            p = ATRASO + i * PASSO + JANELA          # onde a folha i fecha
            topo = vh - p * (vh + h)
            base = topo + h
            estado = ('fileira INTEIRA na tela' if topo >= 0 and base <= vh
                      else ('topo %d px acima da dobra' % -topo if topo < 0
                            else 'pe %d px abaixo da dobra' % (base - vh)))
            print('      folha %02d fecha em --p %.3f  ->  topo y=%4d  %s'
                  % (i + 1, p, round(topo), estado))
        # ponto em que a fileira acaba de caber inteira
        p_inteira = h / (vh + h)
        print('      (a fileira cabe inteira a partir de --p %.3f;'
              ' a ultima folha fecha em %.3f)' % (p_inteira, ATRASO + 3 * PASSO + JANELA))
        print('')
    print('   ANTES: --janela .25 / passo .72 punha a folha 04 em --p .89 —')
    print('   com a prancha ja praticamente fora da tela pelo topo.')
    print('')


# ========================================================= 2. FICHA DE OBRA
def obra():
    print('== 2. FICHA DE OBRA — past-performance ==')
    LEAD_CH, TITULO_CH = 52, 16
    # largura media de caractere em Outfit, medida no especime: ~.50em para
    # corpo em peso 400 e ~.48em para titulo em peso 300.
    for vw in (1440, 1368, 1920, 1100):
        c = conteudo(vw)
        vao = c - S8
        placa = min(420, vao * 5 / 12)
        texto = vao * 7 / 12
        fs_lead = fluido(20, 1.46, 28, vw)
        fs_h2 = fluido(28, 2.3, 44, vw)
        lead_px = LEAD_CH * .50 * fs_lead
        titulo_px = TITULO_CH * .48 * fs_h2
        # linha de dado: 4fr / 8fr
        rotulo = texto * 4 / 12
        # o rotulo mais largo do conteudo real
        maior = 'WHY IT MATTERS'
        rot_px = len(maior) * 13 * .60 * 1.12    # mono 13px + tracking .12em
        # A MEDIDA EFETIVA e o menor dos dois: `max-width` OU a coluna. Onde
        # a coluna e mais estreita e ela quem manda, e o `max-width` nunca
        # chega a valer -- o que importa e a medida resultante ficar na faixa
        # legivel, nunca larga demais.
        medida = min(lead_px, texto) / (.50 * fs_lead)
        quem = 'a coluna' if texto < lead_px else 'o max-width'
        print('   %d px — placa %d px, coluna de texto %d px' % (vw, placa, texto))
        print('      lead    max-width %dch = %d px; quem limita e %s'
              % (LEAD_CH, lead_px, quem))
        print('              medida efetiva %.0fch  %s'
              % (medida, 'ok' if 40 <= medida <= 75 else 'FORA DA FAIXA'))
        print('      titulo  %3dch -> %4d px  (cabe em %d? %s)'
              % (TITULO_CH, titulo_px, texto, 'sim' if titulo_px <= texto else 'NAO'))
        print('      rotulo  "%s" -> %d px  (coluna %d px? %s)'
              % (maior, rot_px, rotulo, 'sim' if rot_px <= rotulo else 'NAO'))
    print('')
    print('   A PLACA E REDUZIDA, nunca ampliada — que e a unica forma de a')
    print('   fotografia de 600x600 do cliente ficar nitida:')
    for vw in (1440, 1920):
        c = conteudo(vw)
        placa = min(420, (c - S8) * 5 / 12)
        for fonte in (600, 900):
            print('      %d px: fonte %d -> escala %.2fx  %s'
                  % (vw, fonte, placa / fonte,
                     'REDUZ' if placa < fonte else 'AMPLIA'))
    print('')


# =========================================================== 3. GALERIA
def galeria():
    import build_site as B
    print('== 3. GALERIA — equilibrio das colunas no empilhamento guloso ==')
    itens = [(b, l, a, g, B._proporcao(b, l)) for b, l, a, g in B.GALERIA]
    props = sorted(set(round(i[4], 2) for i in itens))
    print('   %d chapas, %d proporcoes distintas: %.2f .. %.2f'
          % (len(itens), len(props), props[0], props[-1]))
    print('   (ate 20/08 eram 29 QUADRADOS iguais — build_imagens recortava tudo')
    print('   em 1.0, entao o "mosaico" era uma grade uniforme.)')
    print('')
    for n, vw in ((3, 1440), (2, 1000), (1, 600)):
        # largura de coluna: mosaico e full-bleed com padding lateral
        largura = (vw - 2 * PAD - (n - 1) * S4) / n
        pilhas = B._empilhar(itens, n)
        px = [sum(1 / i[4] + .16 for i in c) * largura for c in pilhas]
        desvio = (max(px) - min(px)) / max(px) * 100
        print('   %d colunas a %d px de janela (coluna %d px):' % (n, vw, largura))
        print('      chapas por coluna %s' % [len(c) for c in pilhas])
        print('      altura estimada   %s px' % [int(v) for v in px])
        print('      desvio maximo     %d px (%.1f%%)  %s'
              % (max(px) - min(px), desvio,
                 'ok' if desvio < 10 else 'DESEQUILIBRADO'))
    print('')
    alta = max(sum(1 / i[4] + .16 for i in c) * 430
               for c in B._empilhar(itens, 3))
    print('   DERIVA: --amp -44 e -88 px ao longo da travessia INTEIRA do')
    print('   mosaico. A coluna mais alta a 3 colunas mede ~%d px, entao a'
          % alta)
    print('   deriva maxima e %.2f%% da altura dela — lenta de proposito.'
          % (88 / alta * 100))
    print('   Deriva rapida em galeria vira enjoo, e e ela que faz o visitante')
    print('   perder a foto que estava olhando.')


if __name__ == '__main__':
    prancha()
    obra()
    galeria()
