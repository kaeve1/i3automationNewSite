# -*- coding: utf-8 -*-
"""Gerador das paginas do site i3Automations.

POR QUE ISTO EXISTE. O site e HTML estatico puro e continua sendo: a saida em
site/*.html nao depende de nada para ser publicada, e nao ha build step no
deploy. Mas nav e rodape sao identicos em nove paginas, e no UnidoCLP eles
eram mantidos a mao com um comentario dizendo "sincronizar ao alterar" — que e
como um deles inevitavelmente fica para tras. Aqui o chrome vive num lugar so
e as nove paginas saem dele.

IDIOMA: o site e EN-US (decisao confirmada 2026-08-18). Os comentarios e a
estrutura deste arquivo ficam em PT-BR, porque quem le e o usuario.

CAMINHOS: relativos, sempre. Os 204 href="/css/..." do UnidoCLP amarraram
aquele site a raiz de um dominio e eliminaram GitHub Pages de projeto.

Uso: python ferramentas/build_paginas.py
"""
import os
import re

RAIZ = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DEST = os.path.join(RAIZ, 'site')

# Quebra de linha como constante: escrever a sequencia de escape direto
# neste arquivo ja foi consumida por camada de ferramenta mais de uma vez.
NL = chr(10)

SITE = 'https://i3automations.com'
EMPRESA = 'i3 Automations &amp; Controls'

MENU = [
    ('index.html', 'Home'),
    ('who-we-are.html', 'Who We Are'),
    ('capabilities.html', 'Capabilities'),
    ('past-performance.html', 'Past Performance'),
    ('services.html', 'Services'),
    ('gallery.html', 'Gallery'),
    ('contact.html', 'Contact'),
]

TEL_VENDAS = '+1 (407) 820-0299'
TEL_SUPORTE = '+1 (941) 666-1880'
EMAIL = 'acastro@i3automations.com'
WHATSAPP = 'https://wa.me/14078200299'

REDES = [
    ('LinkedIn', 'https://www.linkedin.com/company/i3automations/'),
    ('Facebook', 'https://www.facebook.com/i3automations'),
    ('YouTube', 'https://www.youtube.com/@i3automations'),
    ('Instagram', 'https://www.instagram.com/i3automations.plc'),
]


# ---------------------------------------------------------------- fragmentos
def seta():
    return ('<span class="cta__chip" aria-hidden="true">'
            '<svg viewBox="0 0 16 16" fill="none" stroke="currentColor" '
            'stroke-width="1.6"><path d="M2 8h11M9 4l4 4-4 4"/></svg></span>')


def cta(href, texto, classe=''):
    c = ('cta ' + classe).strip()
    return '<a class="%s" href="%s">%s%s</a>' % (c, href, seta(), texto)


# ---------------------------------------------------------------- a marca
#  REESCRITO EM 2026-08-25 (doit.md Fase 3).
#
#  Ate aqui o site desenhava o logo em SVG inline -- moldura em <path>, tela
#  chapada, "i3" em <rect> mais um "3" de lados retos. O cliente reparou e
#  disse "mudei a logo"; ele nao tinha mandado logo novo, tinha mandado o dele
#  de VOLTA. Medido, `logo/logonova.png` e pixel-identico ao arquivo que ja
#  estava em `referencia/i3automations/` (memorianew.md §3.1).
#
#  O que o redesenho jogava fora: o NOTEBOOK virava monitor; os cantos
#  ARREDONDADOS viravam retos; a tela FACETADA em 5 tons virava chapada; o
#  "i3" em geometrica de terminais redondos virava retangulo; e o WORDMARK,
#  que e uma terceira face tipografica, simplesmente nao existia.
#
#  Agora a marca e a arte real, servida em PNG por `ferramentas/build_marca.py`.
#  Vetorizar entra como polimento depois (design.md §3.6): PNG em 1x/2x/3x e
#  pixel-fiel por definicao, e o UnidoCLP ja serve marca em PNG.
#
#  A ISENCAO, ESCRITA: repor a arte real faz do logo o unico objeto
#  ARREDONDADO, com DEGRADE e em TIPOGRAFIA ESTRANGEIRA do site inteiro. Isso
#  nao e acidente nem descuido -- e isencao, e esta em design.md §3.2 e na
#  regra critica 5 do CLAUDE.md. Nenhum outro elemento herda arredondamento,
#  faceta ou tipo de fora do sistema por proximidade com ele.

def _srcset(base, alturas):
    """srcset com descritores de DENSIDADE, nao de largura. Cabe aqui porque
    o slot tem tamanho FIXO em CSS -- o navegador so precisa escolher entre
    1x, 2x e 3x, e nao entre larguras de layout."""
    return ', '.join('brand/%s-%d.png %dx' % (base, a, i + 1)
                     for i, a in enumerate(alturas))


def marca_nav(classe='nav__icone'):
    """A MARCA ISOLADA, para o nav.

    O lockup completo NAO sobrevive em tamanho de navegacao, e isto foi
    medido (memorianew.md §3.3): o wordmark tem duas linhas e ocupa ~55% da
    altura do lockup, dividido por dois.

        altura do lockup | largura | cada linha do wordmark
        32px             |  116px  |  8,8px
        40px             |  145px  | 11,0px
        48px             |  174px  | 13,2px

    Entre 8,8 e 11px e borrao, e fica abaixo do piso de 12px. Entao o nav usa
    a marca isolada -- proporcao 1,571:1, muito mais eficiente em largura --
    mais o nome composto em Outfit, que e o que `.nav__nome` ja fazia
    estruturalmente. O lockup completo vai para a intro, o rodape e a OG,
    onde ha altura.

    `alt` vazio de proposito: o link que envolve a marca ja tem `aria-label`,
    e um alt aqui leria a marca duas vezes."""
    return ('<img class="%s" src="brand/logo-marca-32.png" srcset="%s" '
            'width="50" height="32" alt="" decoding="async">'
            % (classe, _srcset('logo-marca', [32, 64, 96])))


def marca_lockup(classe='intro__marca', knockout=True, alt='', extra=''):
    """O LOCKUP COMPLETO -- marca mais wordmark, 3,530:1.

    `knockout=True` e a versao para fundo escuro: moldura, base e wordmark em
    branco, e o "i3" CONTINUA NAVY, porque ele fica sobre o dourado e branco
    sobre #FDC500 daria 1,6:1. O metodo que produz esse recorte e topologico e
    esta em `build_marca.py` -- bounding box foi tentado e falhou.

    UM ARQUIVO SO, EM RESOLUCAO NATIVA -- e o srcset saiu em 2026-08-26, junto
    com o borrao reportado ("melhorar na animacao principalmente, esta
    embacado").

    O DEFEITO. O srcset era por DENSIDADE (1x/2x/3x) dimensionado para o slot
    de 339 px do RODAPE. A intro rende o mesmo lockup em `min(72vw, 560px)`, e
    descritor de densidade nao sabe disso: ele troca de arquivo quando o DPR
    troca, nunca quando o slot muda. Medido no navegador a 1440 px:

        DPR   arquivo escolhido   px de tela   ampliacao
        1     339x96              560          1,65x
        2     678x192            1120          1,65x
        3     1017x288           1680          1,65x

    **A mesma ampliacao em todos.** Nao era o DPR do avaliador: era um erro
    fixo, e todo mundo via o mesmo borrao.

    POR QUE UM ARQUIVO E MELHOR QUE CONSERTAR O SRCSET. Medido no build:

        logo-completo-branco-96.png    339x96    17,4 KB
        logo-completo-branco-192.png   678x192   39,7 KB
        logo-completo-branco-268.png   946x268   25,3 KB   <- a NATIVA

    A nativa tem 7,8x mais pixel que a de 96 e pesa 1,5x -- e pesa MENOS que a
    intermediaria. Nao e anomalia de compressao: a arte e chapada em 7 cores
    (`build_marca.py`), e PNG comprime regiao chapada quase de graca. O que
    engorda os derivados e o anti-aliasing que o LANCZOS introduz ao reduzir.

    Ou seja: o srcset gastava banda para entregar menos resolucao. Com um
    arquivo so nao ha descritor para errar, o rodape (141 px de largura) recebe
    uma reducao limpa em qualquer DPR, e a intro fica em 1,18x no pior caso
    (DPR 2), contra os 1,65x de antes. 946 px e o teto real da arte do cliente
    -- o recorte do lockup em `logo/logonova.png` tem 946x268 e nao existe
    versao vetorial.

    `width`/`height` sao os da arte, entao a proporcao declarada e a verdadeira
    nos dois slots: a intro fixa a largura e o rodape fixa a altura."""
    base = 'logo-completo-branco' if knockout else 'logo-completo'
    a = (' alt="%s"' % alt) if alt else ' alt="" aria-hidden="true"'
    return ('<img class="%s" src="brand/%s-268.png" '
            'width="946" height="268"%s decoding="async"%s>'
            % (classe, base, a, extra))


def registro_obras(setores):
    """Past performance: um REGISTRO DE OBRAS, seis fichas em serie.

    `setores` = [(setor, titulo, corpo, [(rotulo, valor), ...], base, larguras,
    alt), ...].

    O QUE SAIU, E POR QUE. Antes isto era um painel PRESO: uma secao de
    `6 x 82vh` com um `position: sticky` dentro, trocando de setor conforme a
    rolagem. Duas coisas o condenaram, e as duas foram reportadas pelo usuario:

      1. ELE NAO COMBINAVA COM O SITE. O resto das paginas se le como
         documentacao tecnica -- filete, cota, rotulo em mono, bloco de dados.
         Um carrossel de tela cheia e vocabulario de apresentacao de produto, e
         era a unica peca da pagina falando essa lingua.

      2. AS SECOES NAO SE CONECTAVAM. Uma secao de 492vh entre o cabecalho e o
         resumo abre um vao em que nada se encadeia: o visitante rola meia
         dezena de telas dentro de UM bloco, e os dois vizinhos ficam longe
         demais um do outro para lerem como a mesma pagina.

    E, de quebra, ele carregava um defeito silencioso: as classes `.setores` e
    `.setor` ja eram da GRADE DE SETORES DA HOME (CSS §12). Como o painel foi
    escrito depois no arquivo, as regras dele venciam por ordem em cascata e
    caiam na home tambem -- que e por que a secao "Industries served" aparecia
    quebrada. Este componente nasce com nome proprio (`.obra`) e o conflito
    morre com o nome antigo.

    O QUE ENTROU: a ficha de obra, que e o bloco de titulo de uma folha de
    desenho. Trilho no topo com indice e setor, e embaixo a placa fotografica
    ao lado da tese e dos dados. Seis fichas empilhadas, separadas por filete,
    dentro de uma secao de altura normal -- a pagina volta a ter um fluxo so.

    A PLACA CONTINUA SENDO PLACA, e a razao continua sendo de resolucao: o
    acervo autoral do cliente e todo 600x600, entao sangrado numa moldura de
    1440 px ele seria AMPLIADO 2,4x. Montado em ~420 px ele e REDUZIDO, que e a
    unica forma de ficar nitido. Isso ja estava medido e nao muda com o layout.

    O LADO DA PLACA ALTERNA. Nao e zigue-zague decorativo: e a convencao de um
    conjunto encadernado, em que o bloco de titulo fica na margem EXTERNA da
    folha -- esquerda na par, direita na impar. Da ritmo a uma pilha de seis
    sem que nenhuma ficha mude de estrutura.
    """
    fichas = []
    for i, (setor, titulo, corpo, dados, base, larg, alt) in enumerate(setores):
        linhas = ''.join(
            '<div class="obra__linha">'
            '<dt class="obra__rotulo">%s</dt>'
            '<dd class="obra__valor">%s</dd></div>'
            % (r, v) for r, v in dados)
        fichas.append(
            '<article class="obra reveal" style="--i:%d">'
            # O trilho e a aresta da ficha: indice, setor, e o filete que
            # atravessa o resto da largura. A regua dourada que se desenha
            # nele no hover e o mesmo sinal do nav e do diagrama.
            '<div class="obra__trilho">'
            '<span class="obra__idx">%02d</span>'
            '<span class="obra__setor">%s</span>'
            '<span class="obra__cota" aria-hidden="true"></span>'
            '<span class="obra__regua" aria-hidden="true"></span>'
            '</div>'
            '<div class="obra__corpo">'
            '<div class="obra__placa">%s</div>'
            '<div class="obra__texto">'
            '<h2 class="obra__titulo">%s</h2>'
            '<p class="obra__lead">%s</p>'
            '<dl class="obra__dados">%s</dl>'
            '</div></div></article>'
            % (i, i + 1, setor,
               imagem(base, larg, alt,
                      '(max-width: 767px) 92vw, (max-width: 1023px) 300px, '
                      'min(420px, 30vw)'),
               titulo, corpo, linhas))

    # Sem emenda: as juntas sairam do site em 2026-08-26 (ver a nota de
    # `juntar()` mais abaixo). Cada ficha ja entra pelo `reveal` dos filhos.
    return ('<section class="secao obras" '
            'id="record">'
            '<div class="container">%s</div></section>' % ''.join(fichas))


def ofertas(itens):
    """As formas de contratar, uma FICHA por forma.

    SUBSTITUIU A MATRIZ EM 2026-08-27, a pedido: *"a sessao Engagements esta
    muito complexa e nao funciona bem no celular, preciso que voce resuma e
    escolha bem as informacoes"*.

    A matriz nao era um formato errado -- ela deixava comparar quatro ofertas
    num criterio lendo uma linha. Mas ela cobrava caro por isso: com a quarta
    coluna virou 4x4 = 16 celulas, `table-layout: fixed`, largura minima de
    928px e um ramo de celular que empilhava tudo de novo. Dois layouts para
    manter, e o do celular -- que e onde a maior parte do trafego le -- era o
    pior dos dois.

    E O QUE FOI CORTADO ERA REPETICAO. Dos quatro criterios:

        "Starts when"      \  os dois descreviam a MESMA coisa: a situacao em
        "Typical trigger"  /  que o comprador se reconhece. Viraram um.
        "What we do"          fica
        "You end up with"     fica

    Tres campos por ficha, e com tres campos a comparacao nao precisa mais de
    grade: o olho compara quatro blocos curtos lado a lado sem ajuda de linha
    nenhuma. Some a rolagem horizontal, some a largura minima, e o desktop e o
    celular passam a ser o MESMO layout em numero de colunas diferente.

    O terminal aberto de cada ficha e o mesmo da matriz anterior -- as quatro
    formas continuam sendo derivacoes paralelas, e nao uma sequencia. E a
    razao de nunca terem sido numeradas.

    `itens` = [(nome, situacao, o_que_fazemos, o_que_fica), ...]
    """
    fichas = ''.join(
        '<div class="oferta reveal" style="--i:%d">'
        '<span class="oferta__terminal" aria-hidden="true"></span>'
        '<h3 class="oferta__nome">%s</h3>'
        '<p class="oferta__quando">%s</p>'
        '<dl class="oferta__campos">'
        '<dt>We do</dt><dd>%s</dd>'
        '<dt>You get</dt><dd>%s</dd>'
        '</dl>'
        '</div>' % (i, nome, quando, fazemos, fica)
        for i, (nome, quando, fazemos, fica) in enumerate(itens))
    return '<div class="ofertas">%s</div>' % fichas

def contratos(programa, linhas, total, nota):
    """Registro de CONTRATOS: uma linha por contrato, com data e valor.

    POR QUE NAO REUSAR `oferta()`. As duas sao `<table>`, e a tentacao de
    reaproveitar e forte -- mas a FORMA dos dados e oposta. Em `oferta()` as
    linhas sao CRITERIOS e as colunas sao as tres ofertas, porque a pergunta la
    e "como estas tres se comparam neste quesito". Aqui cada linha e um
    REGISTRO e as colunas sao os campos dele. Forcar um no outro poria os
    contratos nas colunas, e a tabela deixaria de crescer quando o quarto
    entrasse.

    POR QUE ISTO EXISTE. O site antigo publica tres contratos com data de
    inicio, valor e "contact provided upon request", e a migracao tinha
    perdido os tres -- a pagina nova contava a mesma historia por SETOR, que le
    melhor mas nao serve ao comprador federal. Avaliacao de past performance
    pede data, valor e referencia; narrativa nao substitui isso.

    O CAMPO VAZIO E UM TRACO, NAO UMA INVENCAO. Dois dos tres contratos tem
    data de inicio e nenhuma data de fim na fonte. Escrever "ongoing" seria
    afirmar o que a fonte nao diz, e a data de hoje seria pior. O traco diz
    exatamente o que se sabe.

    A COLUNA "REFERENCE" SAIU, e a remocao e o conserto principal do layout.
    Ela trazia "Provided upon request" nas TRES linhas -- o mesmo texto,
    repetido -- e a nota logo abaixo da tabela ja dizia exatamente isso. Uma
    coluna cujo valor nunca muda nao e coluna: e uma nota de rodape ocupando
    431 px de largura. Medido a 1440, ela sozinha respondia por um terco da
    tabela e empurrava as outras tres para 293 px cada, com a de data de fim
    segurando um travessao no meio de 279 px de vazio.

    `linhas` = [(inicio, fim, valor), ...]; `total` = (rotulo, valor);
    `nota` = o texto ao lado da tabela.
    """
    trs = []
    for inicio, fim, valor in linhas:
        trs.append(
            '<tr>'
            '<th scope="row"><span class="contratos__rotulo" aria-hidden="true">Start</span>'
            '<span class="contratos__data">%s</span></th>'
            '<td><span class="contratos__rotulo" aria-hidden="true">End</span>'
            '<span class="contratos__data">%s</span></td>'
            '<td class="contratos__num">'
            '<span class="contratos__rotulo" aria-hidden="true">Value</span>'
            '<span class="contratos__valor">%s</span></td>'
            '</tr>' % (inicio, fim, valor))
    return (
        '<div class="contratos-rolo reveal">'
        '<p class="contratos__programa">%s</p>'
        '<div class="contratos__quadro">'
        '<table class="contratos">'
        '<caption class="sr-so">Contracts delivered under this program, '
        'with start date, end date and value</caption>'
        '<thead><tr>'
        '<th scope="col">Start date</th><th scope="col">End date</th>'
        '<th scope="col" class="contratos__num">Value</th>'
        '</tr></thead>'
        '<tbody>%s</tbody>'
        '<tfoot><tr><th scope="row" colspan="2">%s</th>'
        '<td class="contratos__num"><span class="contratos__valor">%s</span></td>'
        '</tr></tfoot>'
        '</table></div>'
        '<p class="contratos__nota">%s</p>'
        '</div>' % (programa, ''.join(trs), total[0], total[1], nota))


def prancha(itens, cota):
    """Prancha de fotografia de campo: quatro folhas numa fileira ALINHADA.

    `itens` = [(base, larguras, alt, referencia, legenda), ...]; `cota` e o
    rotulo da linha de dimensao embaixo, que nomeia o que a fileira mostra.

    O DESLOCAMENTO ALTERNADO SAIU, a pedido -- "esse estilo escada que sobe e
    desce nao combinou com o site". Ele nasceu como ritmo de folha montada a
    mao, e essa e justamente a lingua errada: o resto do site nao e colagem,
    e desenho tecnico, e desenho tecnico ALINHA. Quatro placas na mesma linha
    de base, penduradas na mesma linha de referencia, leem como quatro vistas
    de uma folha so -- que e o que elas sao.

    O que substitui a escada como ritmo e a CADEIA DE COTA no topo: uma linha
    de referencia continua atravessa a fileira inteira, com um tique sobre cada
    placa e o indice da vista logo abaixo. E a mesma gramatica da regua que ja
    fecha a fileira embaixo, e agora ela abre e fecha o bloco.

    O NUMERO DA VISTA CARREGA INFORMACAO, nao e enfeite de card: ele e a
    referencia que a legenda repete (`REF 01`), que e como uma folha de desenho
    aponta de uma vista para a descricao dela.
    """
    saida = []
    for i, (base, larg, alt, ref, legenda) in enumerate(itens):
        # SEM `reveal`. As folhas nao entram por observador: elas seguem a
        # POSICAO da rolagem (`--p` -> `--avanco`, CSS §22.1), entao subir a
        # pagina desfaz a entrada. `.reveal` marcaria `is-visivel` uma vez e
        # travaria a opacidade em 1, matando o efeito inteiro.
        #
        # `ansioso=True`: ver a nota longa em `imagem()`. Sao as primeiras
        # fotografias da home e o defeito reportado era elas chegarem tarde.
        saida.append(
            '<figure class="prancha__item reveal" style="--i:%d">'
            '<div class="prancha__vista">'
            '<span class="prancha__tique" aria-hidden="true"></span>'
            '<span class="prancha__idx">%02d</span>'
            '</div>'
            '<div class="prancha__moldura">%s</div>'
            '<figcaption class="prancha__legenda">'
            '<span class="prancha__ref">%s</span>%s</figcaption>'
            '</figure>'
            % (i, i + 1,
               imagem(base, larg, alt,
                      '(max-width: 560px) 92vw, (max-width: 1023px) 44vw, 22vw',
                      ansioso=True),
               ref, legenda))
    # `data-progresso` liga a prancha ao modulo 7 do main.js.
    return ('<div class="prancha" data-progresso>'
            '<div class="prancha__datum" aria-hidden="true"></div>'
            '<div class="prancha__linha">%s</div>'
            '<p class="prancha__cota">%s</p>'
            '</div>' % (''.join(saida), cota))


# As quatro pistas do barramento, em % da largura da secao. Ficam nas margens,
# fora da coluna de texto: a 1440 px o conteudo comeca em 80 px e a pista mais
# interna da esquerda cai em 69 px.
ESQ = (1.2, 2.4, 3.6, 4.8)
DIR = (95.2, 96.4, 97.6, 98.8)


def feixe(entra='esq', sai='esq', comeca=0):
    """Um TRECHO do barramento que atravessa a pagina who-we-are.

    Quatro pistas ORTOGONAIS -- so vertical e horizontal, nenhuma curva. E o que
    faz o desenho ler como roteamento de barramento e nao como cabo trancado, e
    e a unica geometria que sobrevive a `preserveAspectRatio: none`: segmento
    alinhado a eixo continua alinhado sob escala nao uniforme, curva nao.

    `entra`/`sai` dizem de que lado o barramento chega e de que lado ele sai --
    e assim ele TROCA DE LADO ao longo da pagina. `comeca` recua o inicio da
    pista (usado no cabecalho, para o barramento nascer no meio da secao).

    A ordem em que as pistas viram nao e enfeite: quem termina mais longe vira
    PRIMEIRO, mais acima. Com a ordem invertida os trechos horizontais cruzariam
    as verticais das vizinhas -- que e exatamente o erro que um roteamento real
    evita.
    """
    a = ESQ if entra == 'esq' else DIR
    b = ESQ if sai == 'esq' else DIR
    troca = (entra != sai)
    # quem chega mais longe do destino vira antes; 7..16% cai dentro do respiro
    # superior da secao, entao o trecho horizontal nao passa por cima do texto
    ys = (16, 13, 10, 7) if sai == 'dir' else (7, 10, 13, 16)

    linhas = ['<div class="feixe" aria-hidden="true">',
              '    <svg class="feixe__svg" viewBox="0 0 100 100"'
              ' preserveAspectRatio="none">']
    for i in range(4):
        if troca:
            d = 'M %s %d V %d H %s V 100' % (a[i], comeca, ys[i], b[i])
        else:
            d = 'M %s %d V 100' % (a[i], comeca)
        linhas.append('      <path class="feixe__pista" d="%s"/>' % d)
        linhas.append('      <path class="feixe__pulso" pathLength="100"'
                      ' style="--f:%d" d="%s"/>' % (i, d))
    linhas.append('    </svg>')
    linhas.append('  </div>')
    return NL.join(linhas)


def diagrama(passos):
    """O metodo como DIAGRAMA DE BLOCOS: quatro etapas em serie, com o sinal
    percorrendo as ligacoes.

    Substituiu quatro cards iguais -- o conteiner preguicoso que nao dizia nada
    sobre o assunto. `passos` = [(num, nome, texto), ...].
    """
    blocos = []
    for i, (num, nome, txt) in enumerate(passos):
        blocos.append(
            '<div class="diagrama__passo reveal" style="--i:%d;--s:%d">'
            '<p class="diagrama__num">%s</p>'
            '<h3 class="diagrama__nome">%s</h3>'
            '<p class="diagrama__txt">%s</p>'
            '<span class="diagrama__topo" aria-hidden="true"></span>'
            '<span class="diagrama__sinal" aria-hidden="true"></span>'
            '</div>' % (i, i, num, nome, txt))
    return '<div class="diagrama">%s</div>' % ''.join(blocos)


def secao_com_foto(bloco, base, larguras, alt):
    """Poe uma fotografia por baixo de uma secao escura ja montada.

    Injeta a classe e o <picture> logo apos a tag de abertura, em vez de
    parametrizar os blocos compartilhados: GOVERNO e CONTATO_CTA aparecem em
    cinco paginas, e so a home pediu fundo fotografico.
    """
    i = bloco.index('>')
    tag = bloco[:i].replace('class="secao secao--escura',
                            'class="secao secao--escura secao--foto" data-progresso')
    foto = imagem(base, larguras, alt, '100vw', classe='secao__foto')
    return tag + '>' + foto + bloco[i + 1:]


def imagem(base, larguras, alt, sizes, classe='', extra='', ext_base='jpg',
           ansioso=False):
    """<picture> com AVIF + WebP + base. `larguras` ja existem no disco.

    `ansioso=True` tira o `loading="lazy"` e pede prioridade alta. Existe por
    um defeito reportado: as quatro folhas da prancha da home so apareciam
    quando o visitante ja tinha rolado quase alem delas.

    Eram DUAS causas somadas, e so corrigir uma nao resolveria:

      o tempo -- a janela de revelacao terminava em `--p` .89, ou seja, com a
        prancha praticamente fora da tela pelo topo (corrigido no CSS §22.1);

      a rede -- `loading="lazy"` so dispara o download quando o navegador julga
        que a imagem esta perto da janela, e ai ainda ha decodificacao pela
        frente. Numa conexao lenta a folha chega DEPOIS de a animacao dela ja
        ter acabado, entao ela "aparece" no fim.

    Lazy continua sendo o padrao e continua certo para as 29 fotos da galeria.
    O ansioso e para a fotografia que e PROVA logo abaixo da primeira dobra, e
    sao quatro arquivos de ~600 px: o custo e pequeno e o defeito e visivel."""
    def srcset(ext):
        return ', '.join('img/%s-%d.%s %dw' % (base, w, ext, w) for w in larguras)
    maior = larguras[-1]
    carga = ('decoding="async" fetchpriority="high"' if ansioso
             else 'loading="lazy" decoding="async"')
    return (
        '<picture>'
        '<source type="image/avif" srcset="%s" sizes="%s">'
        '<source type="image/webp" srcset="%s" sizes="%s">'
        '<img class="%s" src="img/%s-%d.%s" alt="%s" %s %s>'
        '</picture>'
    ) % (srcset('avif'), sizes, srcset('webp'), sizes, classe, base, maior,
         ext_base, alt, carga, extra)


def lente(base, larguras, traco, alt, sizes, classe='', retangulo=True, extra=''):
    """O componente novo: sob o ponteiro, a foto vira desenho tecnico.

    data-foto e data-traco alimentam o shader; as tres camadas encaixadas
    abaixo sao a via CSS, que roda quando nao ha WebGL2. As duas desenham a
    mesma coisa — a diferenca esta na borda.
    """
    maior = larguras[-1]
    mod = ' lente--retangulo' if retangulo else ''
    papel_mask = '' if retangulo else (
        'style="-webkit-mask-image:url(img/%s-%d.png);mask-image:url(img/%s-%d.png)"'
        % (base, maior, base, maior))
    return (
        '<div class="lente%s %s" data-lente data-foto="img/%s-%d.webp" '
        'data-traco="img/%s.png">'
        '%s'
        '<canvas class="lente__gl" aria-hidden="true"></canvas>'
        '<div class="lente__revelo" aria-hidden="true">'
        '<div class="lente__papel" %s>'
        '<div class="lente__tinta" style="-webkit-mask-image:url(img/%s.png);'
        'mask-image:url(img/%s.png)"></div>'
        '</div></div>'
        '<div class="lente__anel" aria-hidden="true"></div>'
        '</div>'
    ) % (mod, classe, base, maior, traco,
         imagem(base, larguras, alt, sizes, classe='lente__foto', extra=extra,
                ext_base='png' if not retangulo else 'jpg'),
         papel_mask, traco, traco)


def cobertura(base, larguras, alt, legenda, fecho=None):
    """A cena PRESA em que a fotografia e tapada por quadrados ao rolar.

    Componente novo de 2026-08-26 (decima rodada), pedido com quatro quadros
    de referencia. O CSS e a razao de cada numero estao na §8.4; aqui fica so
    o que gera a trama.

    A ORDEM DOS QUADRADOS E CALCULADA AQUI, E NAO SORTEADA NO NAVEGADOR, e as
    duas razoes valem:

      1. `Math.random()` no cliente daria uma trama DIFERENTE a cada carga --
         e um efeito que nunca e o mesmo nao pode ser conferido, nem por mim
         nem pelo usuario na proxima rodada.
      2. Sortear no cliente exige JS para escrever 84 estilos. Assim o JS do
         site continua publicando `--p` e mais nada, que e o contrato do
         modulo 7.

    O PADRAO E DE BAIXO PARA CIMA, COM RUIDO. Nao e sorteio puro: nos quatro
    quadros da referencia a cobertura CRESCE do rodape, e o sorteio uniforme
    daria confete. A pontuacao de cada celula e

        peso = (1 - linha_normalizada) * 0.55  +  ruido * 0.45

    com `linha_normalizada` = 0 no topo e 1 embaixo. A parcela de posicao
    (0,55) garante a direcao; a de ruido (0,45) garante que a fronteira nunca
    seja uma linha reta subindo -- que e o que faria a peca ler como uma
    persiana e nao como quadrados.

    O RUIDO E DETERMINISTICO e cabe em uma linha: `sin(i * 12.9898) * 43758.5`
    e a funcao de hash canonica de shader, e o que importa dela aqui e so ser
    reproduzivel entre execucoes. `random.seed()` serviria igual; isto evita
    depender do algoritmo do `random` do Python nao mudar entre versoes.

    84 CELULAS = 12x7 no desktop e 14x6 no celular. Os dois fatoram 84, entao
    a mesma marcacao cobre as duas grades sem nenhum quadrado orfao -- ver a
    nota da grade na §8.4.
    """
    import math
    COLS, LINHAS = 12, 7
    n = COLS * LINHAS

    pesos = []
    for i in range(n):
        linha = i // COLS
        ln = linha / float(LINHAS - 1)          # 0 no topo, 1 embaixo
        ruido = math.sin((i + 1) * 12.9898) * 43758.5453
        ruido -= math.floor(ruido)              # fracao, 0..1
        pesos.append(((1.0 - ln) * 0.55 + ruido * 0.45, i))

    # a ordem e o POSTO na lista ordenada, normalizado -- assim `--o` cobre
    # 0..1 por igual, seja qual for a distribuicao dos pesos.
    ordem = [0] * n
    for posto, (_, i) in enumerate(sorted(pesos)):
        ordem[i] = posto / float(n - 1)

    quadrados = ''.join('<i style="--o:%.3f"></i>' % o for o in ordem)

    # `ansioso=True` E OBRIGATORIO AQUI, e custou um quadro em branco para
    # ficar claro. Numa cena `sticky` a fotografia e o PRIMEIRO pixel que o
    # visitante ve ao chegar -- e com `loading="lazy"` o navegador so a pede
    # quando ela entra na janela, ou seja, no mesmo quadro em que a cena
    # prende. Medido no navegador: em `--p = 0` o palco estava branco, com a
    # legenda boiando sozinha. E o mesmo defeito que a prancha da home ja
    # pagou, no mesmo lugar da explicacao de `imagem()`.
    # `fecho` = (oracao 1, oracao 2). A frase que ocupa a tela depois de os
    # quadrados a esvaziarem -- ver §8.4.1 no CSS para os tempos e a razao.
    #
    # DUAS ORACOES EM DOIS `<span>` E NAO UMA FRASE SO: elas chegam em tempos
    # diferentes, e o que se anima e cada uma. Num `<p>` unico nao ha onde
    # pendurar dois tempos sem partir o texto em nos que o leitor de tela
    # anunciaria como pedacos soltos -- `display: block` num `<span>` dentro do
    # mesmo paragrafo mantem a frase INTEIRA para quem le e separada para quem
    # anima. Mesma solucao do `.rodape__headline`, que quebra o fecho do site
    # em palavras pela mesma razao.
    #
    # SEM `aria-hidden`: e conteudo de verdade, e a ordem de leitura sem visao
    # fica correta -- alt da foto, legenda, frase, e a proxima secao.
    peca_fecho = ''
    if fecho:
        peca_fecho = ('<div class="cobertura__fecho">'
                      '<p class="cobertura__frase">'
                      '<span>%s</span><span>%s</span>'
                      '</p></div>' % fecho)
    return (
        '<section class="secao cobertura" data-progresso>'
        '<div class="cobertura__palco">'
        '%s'
        '<div class="cobertura__grade" aria-hidden="true">%s</div>'
        '%s'
        '<p class="cobertura__legenda">%s</p>'
        '</div></section>'
    ) % (imagem(base, larguras, alt, '100vw', classe='cobertura__foto',
                ansioso=True),
         quadrados, peca_fecho, legenda)


def nav(atual, sobre_heroi=False):
    """A barra de navegacao.

    CONTATO APARECE UMA VEZ SO, e e o botao. Ate 2026-08-26 o cabecalho
    carregava as duas coisas -- a aba "Contact" no meio dos links e o botao
    "Contact Us" com moldura na direita --, apontando para a MESMA pagina a 5
    cm de distancia. O usuario reportou como duas abas de contato, e e o que
    era. Ficou o botao, porque ele e o unico item do cabecalho com moldura:
    tirar o botao para ficar com a aba trocaria o CTA da barra por um link
    igual aos outros seis.

    `MENU` continua com as sete paginas -- ele tambem alimenta a lista de
    navegacao do rodape, onde `contact.html` e um link de pagina como outro
    qualquer e nao uma aba repetida. Quem filtra e a barra, aqui.

    E o botao herda o `aria-current`: em `contact.html` nenhuma das seis abas
    e a pagina corrente, e sem isto a barra deixaria de anunciar onde o
    visitante esta.
    """
    classe = 'nav nav--sobre-heroi' if sobre_heroi else 'nav nav--solido'
    abas = [(h, t) for h, t in MENU if h != 'contact.html']
    links = ''.join(
        '<li><a href="%s"%s>%s</a></li>'
        % (h, ' aria-current="page"' if h == atual else '', t)
        for h, t in abas
    )
    painel = ''.join(
        '<a href="%s"%s>%s</a>' % (h, ' aria-current="page"' if h == atual else '', t)
        for h, t in abas
    )
    atual_contato = ' aria-current="page"' if atual == 'contact.html' else ''
    return '''
<header class="%s">
  <div class="nav__interno">
    <a class="nav__marca" href="index.html" aria-label="i3Automations home">
      %s
      <span class="nav__nome">i3Automations<span>Automations &amp; Controls</span></span>
    </a>

    <ul class="nav__links" role="list">%s</ul>

    <div class="nav__acoes">
      <a class="nav__cta" href="contact.html"%s>Contact Us</a>
      <button class="nav__hamburguer" type="button" aria-expanded="false"
              aria-controls="menu-mobile" aria-label="Open menu"><span></span></button>
    </div>
  </div>

  <nav class="nav__painel" id="menu-mobile" aria-label="Main menu">
    %s
    <a class="botao botao--principal" href="contact.html"%s>Contact Us</a>
  </nav>
</header>''' % (classe, marca_nav(), links, atual_contato, painel, atual_contato)


# A frase de fecho do site, a mesma nas nove paginas. Sai em PALAVRAS porque
# cada uma entra separada -- ver .rodape__headline no style.css.
FECHO = 'Industrial control systems, integrated and commissioned.'


def fecho_em_palavras():
    ps = FECHO.split()
    return ('<span style="--i:%d">%s</span>' % (i, w) for i, w in enumerate(ps)), len(ps)


def rodape():
    nav_links = ''.join('<li><a href="%s">%s</a></li>' % (h, t) for h, t in MENU)
    palavras, n = fecho_em_palavras()
    headline = ('<p class="rodape__headline reveal reveal--limpo" style="--n:%d">%s</p>'
                % (n, ' '.join(palavras)))
    redes = ''.join(
        '<li><a href="%s" target="_blank" rel="noopener">%s</a></li>' % (u, n)
        for n, u in REDES
    )
    return '''
<footer class="rodape">
  <div class="container">
    %s

    <div class="rodape__colunas">
      <div class="reveal" style="--i:1">
        <p class="rodape__titulo">Navigation</p>
        <ul class="rodape__lista" role="list">%s</ul>
      </div>
      <div class="reveal" style="--i:2">
        <p class="rodape__titulo">Contact</p>
        <ul class="rodape__lista" role="list">
          <li><a href="tel:+14078200299">Sales &amp; Services <span class="nowrap">%s</span></a></li>
          <li><a href="tel:+19416661880">Support <span class="nowrap">%s</span></a></li>
          <li><a href="mailto:%s">%s</a></li>
          <li><a href="%s" target="_blank" rel="noopener">WhatsApp</a></li>
        </ul>
      </div>
      <div class="reveal" style="--i:3">
        <p class="rodape__titulo">Vendor profile</p>
        <ul class="rodape__lista" role="list">
          <li>UEI <span class="mono">XUZ4WKEZLS67</span></li>
          <li>CAGE <span class="mono">9ZJM6</span></li>
          <li>NAICS <span class="mono">541511</span></li>
          <li>Lakewood Ranch, Florida</li>
        </ul>
      </div>
      <div class="reveal" style="--i:4">
        <p class="rodape__titulo">Social</p>
        <ul class="rodape__lista" role="list">%s</ul>
      </div>
    </div>

    <div class="rodape__base reveal" style="--i:5">
      <!-- O lockup JA CONTEM o wordmark "Automations & Controls". Repetir o
           nome ao lado dele escrevia a marca duas vezes na mesma linha -- era
           o que fazia sentido quando a peca era so o icone. O `alt` carrega o
           nome para quem nao ve a imagem. -->
      <span class="rodape__marca">%s</span>
      <span>&copy; <span data-ano>2026</span>. All rights reserved.</span>
      <span class="rodape__legais">
        <a href="privacy-policy.html">Privacy Policy</a>
        <a href="terms-and-conditions.html">Terms and Conditions</a>
      </span>
    </div>
  </div>
</footer>''' % (headline, nav_links, TEL_VENDAS, TEL_SUPORTE, EMAIL, EMAIL,
                WHATSAPP, redes, marca_lockup('rodape__marca-arte', knockout=True,
                                           alt='i3 Automations &amp; Controls'))


def migalhas(arquivo, nome):
    """BreadcrumbList da pagina interna, no formato que o buscador espera."""
    return ("""
<script type="application/ld+json">
{"@context":"https://schema.org","@type":"BreadcrumbList","itemListElement":[
{"@type":"ListItem","position":1,"name":"Home","item":"%s/"},
{"@type":"ListItem","position":2,"name":"%s","item":"%s"}]}
</script>""" % (SITE, nome, url_canonica(arquivo)))


DADOS_ESTRUTURADOS = '''
<script type="application/ld+json">
{
  "@context": "https://schema.org",
  "@type": "ProfessionalService",
  "name": "i3 Automations & Controls",
  "alternateName": "i3Automations",
  "url": "%s/",
  "logo": "%s/brand/icon-512.png",
  "image": "%s/img/og/og-1200.jpg",
  "email": "%s",
  "telephone": "+1-407-820-0299",
  "foundingDate": "2000",
  "address": {
    "@type": "PostalAddress",
    "addressLocality": "Lakewood Ranch",
    "addressRegion": "FL",
    "addressCountry": "US"
  },
  "areaServed": "US",
  "description": "Industrial automation integration: control panels, PLC and SCADA programming, commissioning and instrumentation. Federal contractor since 2000.",
  "knowsAbout": [
    "PLC programming", "SCADA", "HMI", "Control panels", "Commissioning",
    "Instrumentation", "Motor control centers", "Rockwell Automation", "Siemens",
    "Schneider Electric", "Ignition", "VTScada", "Canary Labs", "AVEVA PI System"
  ],
  "sameAs": [%s]
}
</script>''' % (SITE, SITE, SITE, EMAIL,
                ', '.join('"%s"' % u for _, u in REDES))


# ------------------------------------------------------------------- juntas
#
# APOSENTADA EM 2026-08-26, A PEDIDO: "retire todos os sheet n / n do site".
# `pagina()` nao chama mais `juntar()`, e o CSS de `.junta` saiu de
# `fonte/css/style.css`. A funcao fica aqui inteira -- nada do que sai e
# apagado do repositorio -- e voltar custa uma linha em `pagina()`.
#
# E O ROTULO NAO FOI O UNICO A SAIR. O pedido era so a referencia de folha
# ("SHEET 03 OF 05"), mas a linha de eixo que a acompanhava sai junto, e por
# regra e nao por gosto: `plano.md` §1 regra 5 diz "separacao por ESPACO,
# nunca por linha -- filete so onde carrega informacao". Quem carregava a
# informacao era o rotulo. Sem ele a linha tracejada vira ornamento na dobra
# entre duas secoes, que e exatamente o que a regra 5 proibe.
#
# O que a `.junta` tambem fazia de util: acrescentar `reveal reveal--limpo` a
# secao para o observador enxerga-la. Isso existia SO para a linha poder ser
# desenhada por `clip-path` -- sem a linha, a marca nao tem consumidor, e as
# secoes seguem revelando os filhos como sempre (cada `.bloco` ja tem o seu
# `reveal` proprio).
#
# A emenda entre secoes deixou de ser escrita a mao. O que decide o tipo de
# junta e um FATO da pagina -- a superficie mudou ou nao --, e fato que o
# gerador consegue ler. Escrever a classe a mao em 30 secoes seria pedir para
# uma delas ficar para tras, que e a razao de este gerador existir.
#
# E mata a armadilha registrada em memoria.md: `.secao--emenda` sozinha nunca
# acendia, porque quem escreve `is-visivel` e o observador do main.js 4, que
# observa `.reveal` e mais nada. Faltando o par `reveal reveal--limpo` a
# emenda ficava travada em `scaleX(0)`, invisivel para sempre, e nada acusava.
# Agora o marcador entra junto com a junta, sempre, e a pegadinha some.
import re as _re

_SEC = _re.compile(r'<section([^>]*)>', _re.S)


def _superficie(classe):
    """A FOLHA a que a secao pertence. Duas secoes de mesma superficie sao a
    mesma folha, e entre elas nao ha corte a marcar."""
    if 'heroi' in classe or 'cabecalho' in classe:
        return 'topo'
    if 'faixa' in classe:
        return 'faixa'
    if 'secao--escura' in classe:
        return 'navy'
    if 'secao--offwhite' in classe:
        return 'off'
    return 'papel'


def juntar(corpo):
    """Marca cada emenda com o tipo de junta que ela e de fato.

    superficie MUDA  -> `.junta`   linha de eixo + referencia da folha
    superficie IGUAL -> nada       e a mesma folha, e nada precisa dizer isso

    A `.faixa` fica de fora e nao entra na contagem. Nao e excecao de gosto:
    o `::after` dela ja e o degrade da fotografia, e uma banda fotografica
    full-bleed nao e folha do conjunto -- e a chapa inserida entre duas. Ela
    ja tem entrada propria, a foto revelada de baixo para cima.
    """
    achados = []
    for m in _SEC.finditer(corpo):
        attrs = m.group(1)
        c = _re.search(r'class="([^"]*)"', attrs, _re.S)
        classe = c.group(1) if c else ''
        achados.append((m, classe, _superficie(classe)))

    # 1a passagem: quantas FOLHAS tem esta pagina -- e folha e a corrida de
    # superficie, nao a secao. Duas secoes navy seguidas sao uma folha so, e e
    # por isso que a contagem nao pode ser `len(secoes)`: os rotulos pularam
    # numeros na primeira versao ("02 OF 05" e depois "04 OF 05") porque a
    # secao sem corte gastava um numero que nunca aparecia na tela.
    folhas = 0
    ant = None
    for _, _, sup in achados:
        if sup != 'faixa' and sup != ant:
            folhas += 1
        ant = sup

    # 2a passagem, de tras para a frente: reescrever de frente moveria os
    # offsets de todos os `<section>` seguintes.
    plano = []
    n = 0
    anterior = None
    for m, classe, sup in achados:
        muda = (anterior is not None and sup != anterior and sup != 'faixa')
        if sup != 'faixa' and sup != anterior:
            n += 1
        if anterior is None or sup == 'faixa':
            anterior = sup
            continue
        plano.append((m, classe, muda, n, folhas))
        anterior = sup

    for m, classe, muda, n, folhas in reversed(plano):
        attrs = m.group(1)
        inversa = 'data-junta="inversa"' in attrs

        # Superficie IGUAL nao ganha marca nenhuma: o tique `_._._` de "mesma
        # folha" saiu a pedido em 20/08. Dentro de uma dupla ele contradizia a
        # peca -- duas secoes que dividem uma fotografia se leem como um bloco
        # so, e um marcador de comeco no meio dela e ruido.
        if not muda:
            continue
        novas = ['junta']
        if inversa:
            novas.append('junta--inversa')
        # O par que faz o observador enxergar a secao sem move-la.
        if 'reveal' not in classe:
            novas += ['reveal', 'reveal--limpo']

        classe_nova = (classe + ' ' + ' '.join(novas)).strip()
        attrs_novo = _re.sub(r'class="[^"]*"',
                             lambda _m: 'class="%s"' % classe_nova, attrs, count=1)
        attrs_novo = attrs_novo.replace(' data-junta="inversa"', '')
        if muda:
            attrs_novo += ' data-folha="%02d OF %02d"' % (n, folhas)

        corpo = corpo[:m.start()] + '<section' + attrs_novo + '>' + corpo[m.end():]

    return corpo


# As nove paginas, com a PRIORIDADE relativa que o sitemap declara. Nao e
# adivinhacao: a home e a raiz, as cinco de conteudo sao o que o comprador
# procura, e as duas legais existem por obrigacao e nao por trafego.
PAGINAS_SEO = [
    ('index.html', '1.0'),
    ('capabilities.html', '0.9'),
    ('services.html', '0.9'),
    ('past-performance.html', '0.9'),
    ('who-we-are.html', '0.8'),
    ('gallery.html', '0.7'),
    ('contact.html', '0.8'),
    ('privacy-policy.html', '0.2'),
    ('terms-and-conditions.html', '0.2'),
]


# ================================================== DEPLOY: CACHE E ROTAS
# A HOSPEDAGEM REAL E APACHE, e isso descobriu um problema.
#
# Medido em 21/08: i3automations.com responde `Server: Apache`, roda WordPress
# e resolve por ns78/ns79.hostgator.com.br -- HostGator compartilhado, cPanel.
# `_headers` e `_redirects` sao convencao de Cloudflare Pages e Netlify: em
# Apache os dois arquivos sao INERTES. Ficariam no servidor sem fazer nada, e
# o sintoma seria "o cache nao funciona" sem erro em lugar nenhum.
#
# Entao o deploy passa a emitir OS DOIS conjuntos, e a decisao de qual vale e
# de quem publica:
#
#   .htaccess ..... Apache / HostGator / cPanel -- o alvo de hoje
#   _headers ...... Cloudflare Pages, Netlify
#   _redirects .... Cloudflare Pages, Netlify
#
# UMA TABELA, TRES EMISSORES. As regras de cache moram em `CACHE` e os tres
# arquivos saem dela. Escrever a mesma politica duas vezes a mao e como as
# duas divergem -- e a divergencia so aparece no dia em que alguem troca de
# hospedagem e o comportamento muda sem ninguem ter mudado nada.
#
# Cache longo em imagem e fonte porque o NOME carrega a largura
# (`refinaria-2560.jpg`), entao aquele nome nunca muda de conteudo. Curto em
# CSS e JS, que tem nome fixo e mudam a cada entrega: cache longo ali serviria
# a folha velha para quem ja visitou, e o sintoma seria "o site nao atualizou
# para mim". O dia em que isso muda e o dia em que os ativos ganharem hash no
# nome.
ANO = 31536000
SEMANA = 604800
HORA = 3600

CACHE = [
    # (rotulo, padrao de caminho, extensoes, segundos, immutable)
    ('imagens', '/img/*',   ('jpg', 'jpeg', 'png', 'webp', 'avif'), ANO, True),
    ('fontes',  '/fonts/*', ('woff2',),                             ANO, True),
    ('marca',   '/brand/*', ('svg',),                               SEMANA, False),
    ('folhas',  '/*.css',   ('css',),                               HORA, False),
    ('scripts', '/*.js',    ('js',),                                HORA, False),
]

SEGURANCA = [
    ('X-Content-Type-Options', 'nosniff'),
    ('Referrer-Policy', 'strict-origin-when-cross-origin'),
]

MIME = {'jpg': 'image/jpeg', 'jpeg': 'image/jpeg', 'png': 'image/png',
        'webp': 'image/webp', 'avif': 'image/avif', 'svg': 'image/svg+xml',
        'woff2': 'font/woff2', 'css': 'text/css', 'js': 'text/javascript'}

# AS URLS DO WORDPRESS, e por que 301 e nao "deixa dar 404".
#
# O site atual usa pasta (`/who-we-are/`) e o novo usa arquivo
# (`/who-we-are.html`). Sem redirecionamento, TODA URL que o buscador tem
# indexada -- e toda que estiver impressa em proposta, assinatura de e-mail ou
# Capabilities Statement ja enviado a um orgao -- passa a devolver 404.
#
# E a diferenca nao e de conveniencia: uma URL que devolve 404 PERDE a posicao
# que tinha; uma que devolve 301 TRANSFERE. Este arquivo e a diferenca entre
# mudar de endereco e desaparecer.
ROTAS = [
    ('/who-we-are/',           '/who-we-are.html'),
    ('/capabilities/',         '/capabilities.html'),
    ('/past-performance/',     '/past-performance.html'),
    ('/services/',             '/services.html'),
    ('/gallery/',              '/gallery.html'),
    ('/contact-us/',           '/contact.html'),
    ('/privacy-policy/',       '/privacy-policy.html'),
    ('/terms-and-conditions/', '/terms-and-conditions.html'),
    # `/home/` era apelido da home no WordPress e ja devolvia 301 para `/`.
    ('/home/',                 '/'),
]

# Restos do WordPress. Eles NAO viram 301 para a home, e a distincao importa:
# 301 diz "isto mudou de lugar" e o buscador vai atras; 410 diz "isto acabou"
# e ele tira do indice. Mandar um feed RSS para uma pagina HTML e pior que
# devolver erro -- o leitor de feed nao entende e o buscador registra conteudo
# duplicado.
IDOS = ['/feed/', '/comments/feed/', '/wp-json/', '/xmlrpc.php',
        '/wp-login.php', '/wp-admin/']


def cabecalhos_deploy(demo=False):
    """`_headers` -- Cloudflare Pages e Netlify. INERTE em Apache.

    `demo=True` acrescenta `X-Robots-Tag: noindex, nofollow`. NAO e opcional
    num endereco de demonstracao, e a razao esta registrada desde 18/08:
    enquanto o dominio oficial ainda serve o site velho, uma copia indexavel
    em `*.pages.dev` COMPETE com ele no buscador -- duas URLs com o mesmo
    conteudo, e quem decide qual sobrevive e o Google, nao voce.

    POR QUE ISTO E UM PARAMETRO E NAO O PADRAO. Se `noindex` fosse o padrao,
    ele viajaria junto para o dominio real no dia da troca e o site oficial
    sairia do Google -- com o sintoma aparecendo semanas depois da causa,
    quando as posicoes ja cairam. O padrao falha para o lado seguro; quem
    publica numa demo pede o modo demo explicitamente.

    E POR QUE NAO `Disallow: /` NO ROBOTS.TXT, que seria o reflexo obvio: o
    rastreador precisa BUSCAR a pagina para ver o cabecalho `noindex`. Bloqueado
    no robots.txt ele nao busca, nao ve o noindex, e ainda pode indexar a URL
    crua por causa de links externos. Deixar rastrear e mandar noindex e a
    combinacao que realmente tira do indice.
    """
    L = ['# Cloudflare Pages / Netlify. Em Apache quem vale e o .htaccess.', '']
    if demo:
        L = ['# ' + '=' * 66,
             '# MODO DEMONSTRACAO -- este arquivo carrega noindex.',
             '# APAGUE o bloco X-Robots-Tag abaixo (ou republique sem --demo)',
             '# no dia em que este conteudo for para o dominio real, ou o site',
             '# oficial sai do Google.',
             '# ' + '=' * 66,
             ''] + L
    for _rot, padrao, _ext, seg, imut in CACHE:
        L += [padrao, '  Cache-Control: public, max-age=%d%s'
              % (seg, ', immutable' if imut else ''), '']
    # favicon.ico e site.webmanifest moram na RAIZ por obrigacao -- o navegador
    # pede `/favicon.ico` sem consultar link nenhum --, entao ficam fora dos
    # padroes acima. Sem regra propria cairiam no `/*` final, que nao declara
    # cache, e o favicon seria rebaixado a cada visita.
    for arq in ('/favicon.ico', '/site.webmanifest'):
        L += [arq, '  Cache-Control: public, max-age=%d' % SEMANA, '']
    L.append('/*')
    for k, v in SEGURANCA:
        L.append('  %s: %s' % (k, v))
    if demo:
        L.append('  X-Robots-Tag: noindex, nofollow')
    # NAO HA `X-Robots-Tag: noindex` AQUI, e a ausencia e deliberada. Endereco
    # de DEMONSTRACAO precisa dele para nao competir com o dominio oficial --
    # mas esse arquivo tem de ser APAGADO quando o dominio real entrar, ou o
    # site oficial sai do Google. Escrever `noindex` por padrao e criar
    # exatamente essa armadilha, e o sintoma aparece semanas depois da causa.
    return NL.join(L) + NL


def redirecionamentos_deploy():
    """`_redirects` -- Cloudflare Pages e Netlify. INERTE em Apache."""
    L = ['# Cloudflare Pages / Netlify. Em Apache quem vale e o .htaccess.',
         '# origem  destino  codigo', '']
    larg = max(len(a) for a, _ in ROTAS) + 2

    # O ALVO AQUI E SEM `.html`, E ISSO CONSERTA UM LACO INFINITO.
    #
    # O Cloudflare Pages canonicaliza sozinho: pedir `/who-we-are.html` devolve
    # **308 para `/who-we-are`**, sem extensao. Nao ha como desligar isso pelo
    # `_redirects`.
    #
    # A primeira versao deste arquivo apontava para `/who-we-are.html` e ainda
    # emitia a variante sem barra (`/who-we-are` -> `/who-we-are.html`), que e
    # a regra CERTA em Apache. No Pages as duas coisas se perseguem:
    #
    #   /who-we-are.html  --308-->  /who-we-are     (o Pages canonicaliza)
    #   /who-we-are       --301-->  /who-we-are.html  (a nossa regra)
    #
    # Medido no ar: **50 saltos e o curl desiste**. O site inteiro ficou
    # inacessivel, porque todo link interno aponta para `.html`.
    #
    # Entao: alvo sem extensao, e NENHUMA regra para a forma sem barra -- o
    # Pages ja serve `/who-we-are` nativamente, e qualquer regra ali recria o
    # laco. Em Apache continua valendo o oposto, e por isso o `.htaccess` e
    # gerado a parte em vez de os dois saírem do mesmo texto.
    #
    # REGRA QUE FICA: redirecionamento correto numa plataforma pode ser LACO em
    # outra. Regra de rota nao se copia entre hospedagens sem testar no ar.
    for velho, novo in ROTAS:
        alvo = novo[:-5] if novo.endswith('.html') else novo
        L.append('%-*s %-26s 301' % (larg, velho, alvo))
    # 404 AQUI, 410 NO APACHE, e a diferenca e da PLATAFORMA, nao da intencao.
    #
    # O `_redirects` do Cloudflare Pages aceita 200, 301, 302, 303, 307, 308 e
    # 404 -- e mais nada. Uma linha com 410 nao vira "410": ela e descartada na
    # publicacao, em silencio, e o caminho passa a nao ter regra nenhuma.
    #
    # 410 continua sendo o codigo CERTO para isto ("acabou", nao "mudou de
    # lugar") e e o que o .htaccess emite, porque em Apache da para emiti-lo.
    # Onde a plataforma nao deixa, 404 e o mais proximo que existe: tambem tira
    # do indice, so um pouco mais devagar.
    # SIMETRIA COM O .htaccess, e ela nasceu de um vazamento real: publicado no
    # Cloudflare Pages, `/.htaccess` respondia 200 e entregava a configuracao de
    # servidor inteira para quem pedisse. `_headers` e `_redirects` nao vazam
    # porque o Pages os CONSOME; o arquivo do Apache ele so serve.
    #
    # O Apache ja faz o inverso -- nega `_headers` e `_redirects` por FilesMatch.
    # Aqui a ferramenta disponivel e o proprio `_redirects`, entao e por ele.
    L += ['', '# Cada plataforma esconde o arquivo de configuracao da outra.',
          '%-*s %-26s 404' % (larg, '/.htaccess', '/404.html'),
          '',
          '# 410 seria o certo, mas o Cloudflare Pages so aceita ate 404.',
          '# O .htaccess, em Apache, emite 410 nestes mesmos caminhos.']
    for ido in IDOS:
        L.append('%-*s %-26s 404' % (larg, ido + '*', '/404.html'))
    return NL.join(L) + NL


def htaccess_deploy():
    """`.htaccess` -- Apache, que e onde este site vai de fato morar.

    Cinco coisas que SO existem aqui, e cada uma some em silencio se faltar:

      ErrorDocument .. sem ele o Apache serve a pagina de erro DELE, e o
                       404.html que este projeto escreveu nunca aparece.
      mod_deflate .... medido: o servidor atual ja comprime, mas quem liga isso
                       e o .htaccess do WordPress. Trocando o arquivo sem repor
                       a regra, `style.css` passa de 12,7 KB a 70,4 KB.
      mod_expires .... medido: o servidor atual NAO manda `Cache-Control` em
                       nada -- nunca foi configurado. Sem ele a segunda visita
                       baixa tudo de novo.
      AddType ........ se o Apache nao conhece `.avif`, ele o serve como
                       `application/octet-stream` e o <picture> nao pinta nada.
                       Sao 101 arquivos AVIF: o site inteiro ficaria sem
                       fotografia, e sem um erro no console.
      https + non-www  o site atual ja faz os dois por 301, e quem faz e este
                       arquivo. Substitui-lo sem repor as regras quebraria a
                       canonica que o buscador ja conhece.
    """
    L = ['# ' + '=' * 68,
         '# i3 Automations & Controls -- Apache (HostGator / cPanel)',
         '# Gerado por ferramentas/build_paginas.py. Nao editar a mao.',
         '# ' + '=' * 68,
         '',
         'Options -Indexes',
         'DirectoryIndex index.html',
         '',
         '# Os arquivos da OUTRA hospedagem ficam na pasta, mas nao no ar.',
         '# `_headers` e `_redirects` sao inertes em Apache -- so que inerte',
         '# nao quer dizer invisivel: sem esta regra o servidor os entrega como',
         '# texto para quem pedir. Ficam no disco para o dia de uma mudanca',
         '# para Cloudflare Pages, e fora do alcance ate la.',
         '<FilesMatch "^(_headers|_redirects)$">',
         '  Require all denied',
         '</FilesMatch>',
         '',
         '# A pagina de erro do PROJETO, nao a do Apache: ela leva noindex e o',
         '# bloco de contato inteiro, para o visitante ter para onde ir.',
         'ErrorDocument 404 /404.html',
         '',
         '<IfModule mod_rewrite.c>',
         '  RewriteEngine On',
         '',
         '  # --- canonica: https, e sem www ---',
         '  # O site atual ja resolve as duas por 301. Estao aqui porque a regra',
         '  # vivia no .htaccess do WordPress, que este arquivo substitui.',
         '  RewriteCond %{HTTPS} !=on',
         '  RewriteRule ^(.*)$ https://%{HTTP_HOST}/$1 [R=301,L]',
         '  RewriteCond %{HTTP_HOST} ^www\\.(.+)$ [NC]',
         '  RewriteRule ^(.*)$ https://%1/$1 [R=301,L]',
         '',
         '  # --- index.html nao e uma segunda home ---',
         '  # As duas formas servem a mesma pagina, que e a definicao de',
         '  # conteudo duplicado. A canonica do HTML ja aponta para a barra;',
         '  # isto faz o servidor concordar com ela.',
         '  RewriteRule ^index\\.html$ / [R=301,L]',
         '',
         '  # --- as URLs do WordPress ---']
    for velho, novo in ROTAS:
        alvo = velho.strip('/')
        if alvo:
            L.append('  RewriteRule ^%s/?$ %s [R=301,L]' % (alvo, novo))
    L += ['',
          '  # --- o que nao existe mais ---',
          '  # [G] devolve 410 Gone. 410 e nao 301 porque isto ACABOU, nao mudou',
          '  # de lugar: 301 mandaria o buscador atras de um destino, e um feed',
          '  # RSS redirecionado para pagina HTML confunde o leitor de feed.']
    for ido in IDOS:
        L.append('  RewriteRule ^%s - [G,L]' % ido.strip('/').replace('.', '\\.'))
    L += ['</IfModule>',
          '',
          '# --- compressao ---',
          '# Sem isto o CSS sai a 70,4 KB em vez de 12,7 KB. Imagem e fonte ficam',
          '# de FORA de proposito: AVIF, WebP e WOFF2 ja sao comprimidos, e passa-',
          '# los pelo gzip gasta CPU para CRESCER alguns bytes.',
          '<IfModule mod_deflate.c>',
          '  AddOutputFilterByType DEFLATE text/html text/css text/plain',
          '  AddOutputFilterByType DEFLATE text/javascript application/javascript',
          '  AddOutputFilterByType DEFLATE application/json application/manifest+json',
          '  AddOutputFilterByType DEFLATE application/xml image/svg+xml',
          '</IfModule>',
          '',
          '# --- tipos que o Apache pode nao conhecer ---',
          '<IfModule mod_mime.c>',
          '  AddType image/avif .avif',
          '  AddType image/webp .webp',
          '  AddType application/manifest+json .webmanifest',
          '  AddType font/woff2 .woff2',
          '</IfModule>',
          '',
          '# --- cache ---',
          '<IfModule mod_expires.c>',
          '  ExpiresActive On']
    vistos = set()
    for rotulo, _p, exts, seg, _i in CACHE:
        novos = [MIME[e] for e in exts if MIME[e] not in vistos]
        if not novos:
            continue
        L.append('  # %s' % rotulo)
        for t in novos:
            if t in vistos:
                continue
            vistos.add(t)
            # OS ROTULOS VAO EM LINHA PROPRIA, e isso custou um 500.
            # O parser de configuracao do Apache so reconhece `#` no INICIO da
            # linha: `ExpiresByType image/jpeg "..." # imagens` faz o `#` e o
            # rotulo virarem argumentos extras, e a diretiva aceita exatamente
            # dois. O erro nao e de sintaxe de arquivo -- e por isso que
            # `httpd -t` passou limpo: .htaccess so e lido no momento do
            # PEDIDO. O sintoma foi 500 na home, e a causa estava aqui.
            L.append('  ExpiresByType %-16s "access plus %d seconds"'
                     % (t, seg))
    L += ['  # favicon',
          '  ExpiresByType %-16s "access plus %d seconds"'
          % ('image/x-icon', SEMANA),
          '</IfModule>',
          '',
          '<IfModule mod_headers.c>']
    for k, v in SEGURANCA:
        L.append('  Header always set %s "%s"' % (k, v))
    # AS DUAS CAMADAS DE CACHE SAO DELIBERADAS, e saem da MESMA tabela.
    #
    # `mod_expires` e a base, e ele escreve so `max-age=N` -- sem `public`,
    # sem `immutable`, e nao ha como pedir mais a ele. `mod_headers` refina
    # com o valor completo, que e exatamente o que o `_headers` manda em
    # Cloudflare.
    #
    # Sem esta segunda camada o MESMO arquivo teria politica diferente em
    # Apache e em Cloudflare -- que e a divergencia que gerar tudo de uma
    # tabela so existe para impedir. Medido antes da correcao: o CSS saia com
    # `max-age=3600` aqui e `public, max-age=3600` la.
    #
    # E se `mod_headers` faltar no servidor, sobra o `max-age` do mod_expires:
    # o cache continua funcionando, so perde a dica. Degrada, nao quebra.
    L.append('  # o valor completo, identico ao que o _headers manda')
    for _rot, _pad, exts, seg, imut in CACHE:
        alt = '|'.join(dict.fromkeys(
            'jpe?g' if e in ('jpg', 'jpeg') else e for e in exts))
        L += ['  <FilesMatch "\\.(%s)$">' % alt,
              '    Header set Cache-Control "public, max-age=%d%s"'
              % (seg, ', immutable' if imut else ''),
              '  </FilesMatch>']
    # favicon.ico e site.webmanifest moram na raiz e nao casam nenhum padrao
    # de CACHE, pelo mesmo motivo que precisam de regra propria no _headers.
    L += ['  <FilesMatch "^(favicon\\.ico|site\\.webmanifest)$">',
          '    Header set Cache-Control "public, max-age=%d"' % SEMANA,
          '  </FilesMatch>',
          '</IfModule>',
          '']
    return NL.join(L)


def sitemap(data):
    """sitemap.xml a partir da MESMA lista que gera as paginas.

    Escrito pelo gerador e nao a mao pelo motivo de sempre: sitemap mantido a
    mao e o primeiro arquivo a ficar para tras quando uma pagina entra ou sai,
    e o sintoma -- pagina nova que o buscador nao acha -- demora semanas para
    aparecer.
    """
    linhas = ['<?xml version="1.0" encoding="UTF-8"?>',
              '<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">']
    for arq, prio in PAGINAS_SEO:
        linhas += ['  <url>',
                   '    <loc>%s</loc>' % url_canonica(arq),
                   '    <lastmod>%s</lastmod>' % data,
                   '    <priority>%s</priority>' % prio,
                   '  </url>']
    linhas.append('</urlset>')
    return NL.join(linhas) + NL


def robots():
    """robots.txt: libera tudo e aponta o sitemap.

    NAO ha `Disallow` de nada: o site inteiro e publico e existe para ser
    achado. A unica linha que importa e o `Sitemap`, que e como o buscador
    descobre as nove paginas sem depender de rastrear link por link.
    """
    return NL.join(['User-agent: *',
                    'Allow: /',
                    '',
                    'Sitemap: %s/sitemap.xml' % SITE]) + NL


def url_canonica(arquivo):
    """A URL que o buscador deve indexar.

    `/index.html` e `/` servem a MESMA pagina em qualquer hospedagem estatica,
    e apontar o canonico para o arquivo cria duas URLs para um conteudo so --
    conteudo duplicado, que e o defeito de SEO mais comum de site estatico.
    A home canoniza para a raiz; as demais mantem o arquivo, que e a URL que
    os links internos usam.
    """
    return SITE + '/' if arquivo == 'index.html' else SITE + '/' + arquivo


def limpar(doc):
    """Tira comentario do HTML publicado -- inclusive de dentro dos scripts
    embutidos, que `build_ativos.py` NAO alcanca (ele so publica `fonte/`).

    Sao 39 comentarios e 8,9 KB no site inteiro, e a maior parte esta no
    script de tema, que e inline de proposito: ele tem de rodar antes da
    primeira pintura, e um arquivo externo chegaria tarde demais.

    A ORDEM E O CUIDADO. O documento e fatiado nos limites de `<script>`
    PRIMEIRO, e cada pedaco vai para o limpador que serve a ele: corpo de
    script para a maquina de estados de JS, o resto para o corte de `<!-- -->`.
    Invertido, um `<!--` dentro de uma string de JS levaria codigo junto, e o
    arquivo continuaria com sintaxe valida -- o defeito nao apareceria aqui,
    apareceria no navegador de alguem.

    O corte de HTML preserva comentario condicional (`<!--[if`) por seguranca:
    este site nao usa nenhum, mas comentario condicional CARREGA marcacao, e
    um limpador que nao sabe disso apaga conteudo.
    """
    import re
    import build_ativos

    partes = re.split(r'(<script(?![^>]*\ssrc=)[^>]*>)(.*?)(</script>)',
                      doc, flags=re.S)
    saida = []
    i = 0
    while i < len(partes):
        # fora de script: corta comentario de HTML
        saida.append(re.sub(r'<!--(?!\[if).*?-->', '', partes[i], flags=re.S))
        if i + 3 < len(partes) + 1 and i + 3 <= len(partes) - 1:
            abre, corpo_js, fecha = partes[i + 1], partes[i + 2], partes[i + 3]
            limpo, _ = build_ativos.tirar_comentarios_js(corpo_js)
            linhas = [ln.strip() for ln in limpo.split(NL) if ln.strip()]
            saida.append(abre + NL + NL.join(linhas) + NL + fecha)
            i += 4
        else:
            i += 1
    doc = ''.join(saida)
    # linha que ficou vazia por causa do comentario removido
    return NL.join(ln for ln in doc.split(NL) if ln.strip() or ln == '')



def aviso_armazenamento():
    """A faixa de consentimento, e ela diz a VERDADE deste site.

    O usuario pediu a faixa mesmo sem haver cookie -- comprador corporativo e
    orgao publico costumam exigi-la por politica interna, independentemente da
    lei. Isso torna o TEXTO a decisao dificil, nao o componente: escrever "we
    use cookies to improve your experience" numa pagina que nao poe cookie
    nenhum e uma afirmacao falsa, e a politica de privacidade a poucos cliques
    diz o contrario. Contradicao entre a faixa e a pagina legal e pior que
    faixa nenhuma.

    Entao ela declara o que existe: nenhum cookie, nenhum analytics, nenhum
    script de terceiro, e UM valor local. O botao nao diz "Accept": nao ha o
    que aceitar. Diz "Got it".

    O TEXTO MUDOU EM 2026-08-25, e a mudanca e de FATO e nao de estilo. Ele
    dizia que o unico valor guardado era a escolha de tema claro/escuro -- e o
    alternador de tema saiu (design.md §1.4 regra 6). A frase virou falsa no
    instante em que o botao saiu do nav, e uma faixa de consentimento que
    afirma o que nao acontece e exatamente o defeito que esta funcao existe
    para evitar. O que sobrou guardado e a dispensa DESTA faixa: ela guarda um
    registro de si mesma, e agora e isso que ela diz.

    Nasce com `hidden`: sem JavaScript ninguem consegue dispensa-la, e uma
    faixa que nao se dispensa e pior que faixa nenhuma. Quem revela e o
    main.js 12, depois de conferir o armazenamento.
    """
    return '''<aside class="aviso" id="aviso-armazenamento" role="region"
       aria-label="Storage notice" hidden>
  <div class="aviso__interno">
    <p class="aviso__texto">
      <b class="aviso__rotulo">Storage</b>
      This site sets no cookies, runs no analytics and loads no third-party
      scripts. The only thing kept in your browser is the fact that you
      dismissed this notice, and it never leaves your device.
    </p>
    <div class="aviso__acoes">
      <a class="aviso__link" href="privacy-policy.html">Privacy policy</a>
      <button class="aviso__botao" type="button" data-aviso-ok>Got it</button>
    </div>
  </div>
</aside>'''

def pagina(arquivo, titulo, descricao, corpo, sobre_heroi=False, scripts_extra=(),
           intro=False, og_img=None, trilha_seo=None, indexavel=True):
    intro_html = ''
    intro_script = ''
    if intro:
        intro_script = ('\n<script>\n'
                        '/* Marcado antes da primeira pintura: sem isto a peca do heroi\n'
                        '   nasceria visivel e piscaria duas vezes. */\n'
                        'document.documentElement.className += " intro-ativa";\n'
                        '</script>')
        # A intro passa a ser a MARCA, nao o braco. O par foto->traco do braco
        # nunca fechava com a peca do heroi: a garra do desenho e a garra em 3D
        # sao a mesma maquina em poses diferentes, e o encontro ficava torto.
        # O logo nao tem esse problema -- ele pousa exatamente sobre si mesmo.
        # A INTRO E O NOTEBOOK DA MARCA ABRINDO (v3, 2026-08-27). A v1 --
        # o lockup revelado da esquerda para a direita -- esta salva inteira
        # em `melhorias/intro-v1/`, com o procedimento de volta.
        #
        # AS DUAS PECAS SAO RECORTES DA ARTE REAL, cortados na dobradica por
        # `ferramentas/corte_marca.py`. Nao ha notebook desenhado em SVG aqui,
        # e a razao esta em `design.md` §3.5: a PRIMEIRA intro do projeto
        # morreu porque desenhava o REDESENHO da marca, e o cliente reparou.
        #
        # `logo-tampa.png` tem 12 KB e `logo-base.png` 1,4 KB -- juntas pesam
        # metade do lockup knockout que a v1 carregava (24 KB), entao a dobra
        # que carrega adiantado ficou mais leve, nao mais pesada.
        #
        # A ORDEM NO DOM E A ORDEM DE PINTURA: chao, paineis, notebook, frase.
        # O chao cobre a janela enquanto a tampa esta fechada; os paineis
        # assumem quando ela abre; ver a linha do tempo em style.css §5.
        #
        # `alt=""` nas duas: a intro inteira e `role="presentation"`, e o nome
        # da empresa ja esta no nav e no rodape de toda pagina. Marca decorativa
        # anunciada duas vezes e ruido para quem le com leitor de tela.
        intro_html = '''
<div class="intro" role="presentation">
  <div class="intro__chao"></div>
  <span class="intro__painel intro__painel--topo"></span>
  <span class="intro__painel intro__painel--baixo"></span>
  <span class="intro__painel intro__painel--esq"></span>
  <span class="intro__painel intro__painel--dir"></span>

  <div class="intro__nb">
    <img class="intro__tampa" src="brand/logo-tampa.png" width="418" height="234"
         alt="" decoding="sync" fetchpriority="high">
    <img class="intro__base" src="brand/logo-base.png" width="418" height="34"
         alt="" decoding="sync">
  </div>

  <p class="intro__frase">
    <span class="intro__texto"><span class="intro__linha">Good control strategy</span> <span class="intro__linha">beats expensive instrumentation</span></span><span class="intro__cursor" aria-hidden="true"></span>
  </p>
</div>
'''
    # Quem consome window.I3GL (js/gl.js). Scripts com `defer` executam na
    # ORDEM DO DOCUMENTO, entao basta gl.js aparecer antes -- mas depender de
    # quem escreve a tupla lembrar disso e como o nucleo some numa madrugada:
    # o sintoma seria a peca nao aparecer, sem erro visivel na pagina.
    # Dois nucleos, duas familias de peca. Quem consome `window.I3GL` recebe
    # `gl.js` na frente; quem consome `window.I3Tela` recebe `tela.js`. Ambos
    # entram POR DEDUCAO e nao por quem escreve a tupla lembrar da ordem --
    # e assim que um nucleo some numa madrugada, e o sintoma seria a peca nao
    # aparecer, sem erro nenhum na pagina.
    consumidores_gl = {'braco.js', 'marca.js', 'clp.js'}
    consumidores_tela = {'malha.js', 'mimico.js', 'carta.js'}
    lista = list(scripts_extra)
    if consumidores_tela.intersection(lista):
        lista.insert(0, 'tela.js')
    if consumidores_gl.intersection(lista):
        lista.insert(0, 'gl.js')
    extra = ''.join('\n<script src="js/%s" defer></script>' % s for s in lista)
    html = '''<!DOCTYPE html>
<html lang="en-US">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>%(titulo)s</title>
<meta name="description" content="%(descricao)s">
%(robots_meta)s%(tag_canonica)s
<meta name="theme-color" content="#003566">

<meta property="og:type" content="website">
<meta property="og:locale" content="en_US">
<meta property="og:site_name" content="i3 Automations &amp; Controls">
<meta property="og:title" content="%(titulo)s">
<meta property="og:description" content="%(descricao)s">
<meta property="og:url" content="%(canonica)s">
<meta property="og:image" content="%(og_img)s">
<meta property="og:image:type" content="image/jpeg">
<meta property="og:image:width" content="1200">
<meta property="og:image:height" content="630">
<meta property="og:image:alt" content="%(titulo)s">
<meta name="twitter:card" content="summary_large_image">

<link rel="icon" href="favicon.ico" sizes="16x16 32x32 48x48">
<link rel="apple-touch-icon" href="brand/apple-touch-icon.png">
<link rel="manifest" href="site.webmanifest">
<link rel="preload" href="fonts/outfit-latin.woff2" as="font" type="font/woff2" crossorigin>
<link rel="stylesheet" href="css/reset.css">
<link rel="stylesheet" href="css/tokens.css">
<link rel="stylesheet" href="css/style.css">

<script>
/* UMA LINHA, e ela existe para um caso especifico: SEM JavaScript, nenhum
   elemento recebe `--p`, e toda regra que deriva opacidade de `--p` resolve
   em 0. Ou seja, a faixa de numeros, as colunas dos momentos e as legendas
   ficariam INVISIVEIS -- nao degradadas, invisiveis.

   E a mesma armadilha que este projeto ja pagou duas vezes (a intro e a frase
   dela, ambas registradas em style.css §5): estado inicial de animacao que
   esconde conteudo. Com a classe, o CSS so esconde o que ele sabe que vai
   conseguir mostrar de novo; sem ela, tudo nasce no estado final.

   Inline e no <head>, DEPOIS do CSS: a classe precisa existir antes da
   primeira pintura, senao ha um lampejo do estado sem JS. */
document.documentElement.className += " js";
</script>
%(intro_script)s
</head>
<body>
%(intro)s
<a class="pular-conteudo" href="#conteudo">Skip to content</a>
%(nav)s
<main id="conteudo">
%(corpo)s
<!-- Marcador do FIM do conteudo. O rodape revelado fica preso ao pe da janela
     desde a carga, entao observar o rodape nao diz se ele esta visivel -- diz
     so que ele existe. Quem responde e este ponto: quando ele sobe ate o pe da
     tela, o que esta aparecendo e o rodape. Consumido por main.js 10. -->
<div data-fim-conteudo aria-hidden="true"></div>
</main>
%(rodape)s
%(aviso)s
<script src="js/main.js" defer></script>%(extra)s
%(dados)s
</body>
</html>
''' % {
        'titulo': titulo, 'descricao': descricao, 'site': SITE, 'arquivo': arquivo,
        # A canonica SO existe em pagina indexavel. Canonica que aponta para si
        # mesma numa pagina `noindex` e sinal contraditorio: uma diz "indexe
        # esta URL", a outra diz "nao indexe" -- e o buscador resolve o empate
        # como quiser. Pagina de erro nao tem canonica, tem status.
        # `canonica` e a URL CRUA, porque `og:url` tambem a consome. A TAG
        # e uma chave separada -- juntar as duas fez o og:url receber o
        # elemento <link> inteiro dentro do proprio content, e toda pagina
        # saiu com DUAS canonicas. Valor e marcacao nao dividem chave.
        'canonica': url_canonica(arquivo),
        'tag_canonica': ('<link rel="canonical" href="%s">'
                         % url_canonica(arquivo) if indexavel else ''),
        # Pagina de erro indexada e o proprio defeito que a 404 existe para
        # evitar -- por isso ela sai do indice pela meta, alem do status.
        'robots_meta': ('' if indexavel else
                        '<meta name="robots" content="noindex, follow">' + NL),
        # CADA PAGINA COM A SUA IMAGEM SOCIAL. Com uma so para as nove, todo
        # link partilhado no LinkedIn saia com o mesmo carta o -- e o cartao e
        # justamente o que diferencia um link do outro na linha do tempo.
        'og_img': SITE + '/' + (og_img or 'img/og/og-1200.jpg'),
        'intro': intro_html, 'intro_script': intro_script,
        'nav': nav(arquivo, sobre_heroi), 'corpo': corpo, 'rodape': rodape(),
        'aviso': aviso_armazenamento(),
        'extra': extra,
        # A TRILHA JA EXISTE NA PAGINA (`.trilha`, Home / Secao). O buscador
        # nao a le como hierarquia sem o JSON-LD -- e e ele que faz o
        # resultado sair com "i3automations.com > Capabilities" em vez da URL
        # crua.
        'dados': DADOS_ESTRUTURADOS + (migalhas(arquivo, trilha_seo) if trilha_seo else ''),
    }
    html = limpar(html)
    caminho = os.path.join(DEST, arquivo)
    with open(caminho, 'w', encoding='utf-8') as f:
        f.write(html)
    return caminho, len(html.encode('utf-8'))


# ------------------------------------------------------------------- blocos
def peca(classe, gancho, reserva, cota='', extra=''):
    """A caixa comum das quatro pecas de pagina (CSS 20.1).

    `gancho` e o atributo `data-*` que o JS procura; `reserva` e o texto que
    fica no lugar quando nao ha canvas ou WebGL2 -- a peca nunca colapsa numa
    caixa vazia, ela vira um rotulo.

    A tela e SEMPRE `position: absolute` e quem da a caixa e o CSS. Nao e
    estilo: `tela.js` e `painel.js` leem o proprio retangulo e escrevem o
    proprio tamanho, e componente assim dentro do fluxo vira realimentacao --
    a pagina cresce sem parar. Ja custou uma sessao em 19/08.
    """
    # UMA classe so no canvas. Emitir tambem `<peca>__tela` deixava
    # `carta__tela` e `mimico__tela` no HTML sem nenhuma regra no CSS -- uso
    # sem classe e um contrato que ninguem esta cumprindo, e a varredura dos
    # dois sentidos acusa. Quem precisa de regra propria escreve
    # `.malha .peca__tela`, que nao inventa nome novo.
    return ('<div class="peca %s" %s>%s'
            '<canvas class="peca__tela"></canvas>'
            '<p class="peca__reserva">%s</p>'
            '</div>%s') % (classe, gancho, extra, reserva, cota)


def cota_peca(itens):
    """A legenda da peca, no registro da linha de cota da prancha."""
    return ('<p class="peca__cota">%s</p>'
            % ''.join('<span><strong>%s</strong> %s</span>' % (a, b) for a, b in itens))


def cabecalho(eyebrow, h1, lead, img_base, larguras, alt, trilha, extra='',
              classe='', marca='', reticula=True):
    """`extra` e o trecho de BARRAMENTO; `marca` e a peca 3D da direita.

    Os dois sao parametros separados de proposito. `extra` decide a classe
    `tem-feixe`, que liga a trama de pistas; passar a marca por ele ligaria o
    barramento num cabecalho que nao tem nenhum -- e o cabecalho de who-we-are
    e justamente aquele de onde o barramento FOI TIRADO, porque duas tramas no
    mesmo bloco brigam.

    `img_base=None` deixa o cabecalho SEM FOTOGRAFIA: navy chapado e a reticula
    por cima, que e o desenho dele. E o caso de who-we-are, onde a marca 3D ja
    ocupa a direita -- fotografia, reticula e peca em arame no mesmo bloco sao
    tres tramas disputando, e a peca perde. O veu `::after` continua declarado e
    nao faz nada: `rgba(0,29,61,a)` sobre `--navy-fundo` (#001D3D, que E
    rgb(0,29,61)) devolve a mesma cor em qualquer alfa.

    `reticula=False` tira a grade quadriculada e deixa a FOTOGRAFIA sozinha --
    a pedido do usuario em 20/08, nas cinco paginas de conteudo. Ela continua
    ligada em who-we-are, que NAO tem foto: la a grade e o desenho do bloco, e
    sem ela sobra navy chapado.

    Nao mexe em contraste, e a conta e curta: a reticula e branca a .07/.028 de
    alfa, ou seja CLAREIA o fundo. Tirar deixa o campo sob o texto branco um
    fio mais escuro, entao o contraste do h1 e do lead so pode subir.
    """
    # `ansioso=True`, e NAO um `loading="eager"` pelo `extra`.
    #
    # A versao anterior mandava a prioridade por `extra` sem ligar o
    # `ansioso` -- e `imagem()` ja escreve `loading="lazy"` por padrao.
    # O `<img>` saia com o atributo DUAS VEZES:
    #
    #   loading="lazy" decoding="async" fetchpriority="high" loading="eager"
    #
    # e o HTML manda o navegador ficar com a PRIMEIRA ocorrencia. O `eager`
    # era descartado em silencio: a foto do cabecalho -- que e o elemento
    # LCP de sete paginas, o maior bloco pintado na primeira dobra --
    # esperava o navegador decidir que ela estava perto da janela, o que so
    # acontece depois do layout, que so acontece depois do CSS e da fonte.
    #
    # Nada acusava: o atributo certo ESTAVA no arquivo, o validador aceita
    # duplicata, e a varredura de referencias so olha caminho.
    foto = '' if not img_base else imagem(
        img_base, larguras, alt, '100vw', classe='cabecalho__foto',
        ansioso=True)
    # `data-progresso` SO onde ha fotografia. Num cabecalho liso (as duas
    # paginas legais) o parallax nao teria o que mover, e o atributo custaria
    # uma leitura de `getBoundingClientRect` por quadro em troca de nada -- o
    # modulo 7 do main.js mede TODO elemento marcado, tenha ele o que animar
    # ou nao.
    return '''
<section class="cabecalho%s"%s>
  %s%s%s
  <div class="container">
    <p class="eyebrow">%s</p>
    <h1>%s</h1>
    <p class="cabecalho__lead">%s</p>
    <p class="trilha"><a href="index.html">Home</a><span>/</span>%s</p>
  </div>
</section>''' % (
        (' reticula' if reticula else '')
        + (' tem-feixe' if extra else '')
        + (' cabecalho--marca' if marca else '')
        + (' cabecalho--liso' if not img_base else '')
        + ((' ' + classe) if classe else ''),
        ' data-progresso' if img_base else '',
        foto, extra, marca, eyebrow, h1, lead, trilha)


# A faixa entra ATADA A ROLAGEM e nao por gatilho de entrada: os cinco numeros
# apareciam juntos, e juntos eles sao vistos; em ordem, sao lidos.
#
# NAO E CONTADOR ANIMADO. O redline 8 do plano.md proibe "contador animado,
# numero que sobe sozinho", e com razao: um numero que corre e ilegivel
# enquanto corre, e sugere precisao que ele nao tem. O que se move aqui e a
# ENTRADA de cada bloco -- o valor ja esta escrito quando aparece.
NUMEROS = '''
    <dl class="numeros" data-progresso>
      <div style="--i:0"><dt class="tabular">279+</dt><dd>automation projects delivered worldwide</dd></div>
      <div style="--i:1"><dt class="tabular">158+</dt><dd>of them in the United States</dd></div>
      <div style="--i:2"><dt class="tabular">78+</dt><dd>in Florida alone</dd></div>
      <div style="--i:3"><dt class="tabular">150,000+</dt><dd>tags historized in AVEVA PI System</dd></div>
      <div style="--i:4"><dt class="tabular">2000</dt><dd>the year we started, and we have not stopped</dd></div>
    </dl>'''

CAPACIDADES = [
    ('Control Panels',
     'UL-compliant enclosures built, wired and tested before they ship. You get the '
     'panel, the schematics and the bill of materials. Not a black box.'),
    ('PLC Programming',
     'Rockwell, Siemens and Schneider. We write to your standard when you have one, '
     'and we document the one we write when you do not.'),
    ('SCADA Programming',
     'Ignition, VTScada and Canary. Screens an operator can read at 3 a.m., alarms '
     'that mean something, and history that survives an audit.'),
    ('Commissioning',
     'Loop checks, I/O verification, startup and operator training. The plant runs '
     'before we leave, and the as-built drawings match what is on the wall.'),
    ('Instrumentation',
     'Specification, installation and calibration. Good control strategy usually '
     'beats a more expensive transmitter, and we will tell you which one you need.'),
    ('Industrial Networks',
     'EtherNet/IP, Modbus, PROFINET and OPC UA. The layer where control meets IT, '
     'segmented so a plant floor problem stays on the plant floor.'),
    ('Motor Controls',
     'MCC design, VFD configuration and starter logic, from a single skid to a '
     'full lineup.'),
    ('Software Development',
     'Reporting, SQL integration and the tools around the control system: daily '
     'reports pulled from the database, alerts routed to the operator on shift.'),
]


def lista_capacidades(reveal=True, nivel=3):
    """A lista numerada de competencias, com o DOMINO de hover.

    `data-i` e a posicao do item; main.js §8 le isso, calcula a distancia ate o
    item apontado e publica `--d` em cada um. O CSS (§22.2) converte distancia
    em atraso e em intensidade -- o item apontado reage primeiro, os vizinhos
    logo atras, e a onda morre nas pontas.

    `data-domino` no container e o interruptor: sem ele o JS nao se liga e a
    lista fica com o hover simples de antes. E o que permite a mesma lista
    servir a home e a pagina de capabilities sem duas implementacoes.
    """
    # O NIVEL DO TITULO E DA PAGINA, NAO DO COMPONENTE. Na home a lista mora
    # dentro de uma secao que ja tem <h2>, entao cada nome e um <h3>. Em
    # capabilities ela e o conteudo direto da pagina -- nao ha <h2> nenhum
    # acima dela -- e um <h3> ali faz o documento pular de h1 para h3, que e
    # violacao de WCAG 1.3.1. Mesmo componente, nivel diferente, porque o que
    # muda e a arvore em volta.
    linhas = []
    for i, (nome, txt) in enumerate(CAPACIDADES, 1):
        linhas.append(
            '<div class="capacidade%s" style="--i:%d" data-i="%d">'
            '<p class="capacidade__num">%02d</p>'
            '<h%d class="capacidade__nome">%s</h%d>'
            '<p class="capacidade__txt">%s</p></div>'
            % (' reveal' if reveal else '', i, i - 1, i,
               nivel, nome, nivel, txt))
    return '<div class="capacidades" data-domino>%s</div>' % ''.join(linhas)


PLATAFORMAS = [
    ('Rockwell Automation', 'Studio 5000 · FactoryTalk', False),
    ('Siemens', 'TIA Portal · WinCC', False),
    ('Schneider Electric', 'EcoStruxure · Unity', False),
    ('Ignition', 'Certified integrator', True),
    ('VTScada', 'Certified integrator', True),
    ('Canary Labs', 'Certified integrator', True),
    ('AVEVA PI System', '150,000+ historized tags', False),
    ('SQL Server', 'Reporting and historian integration', False),
]


def marcas_certificacao(nomes=None):
    """A faixa de plataformas em CHIP, para servir de ponte entre dois blocos.

    Nao e uma grade de cards nova: usa `.marca` e `.marca--certificada`, que
    ja existem e ja carregam ESTADO -- o ponto cheio diz "somos certificados
    aqui", o chip liso diz "operamos aqui". A mesma distincao que a escada de
    plataformas faz em capabilities, na versao compacta.

    POR QUE ELA EXISTE AQUI. As duas dobras de abertura da home tinham a
    mesma estrutura -- eyebrow a esquerda, titulo e paragrafo a direita -- e
    liam como o mesmo bloco duas vezes, com a coluna esquerda vazia por
    ~430px sob um eyebrow de tres palavras. Esta faixa entra no MEIO delas, no
    MESMO grid 4/8: o rotulo dela alinha com os dois eyebrows e os chips
    alinham com os dois titulos. E o alinhamento que integra as duas, e nao
    uma moldura em volta.

    SEIS CHIPS, e nao os oito de `PLATAFORMAS`. AVEVA PI System e SQL Server
    ficam de fora porque nao sao "plataforma em que somos certificados nem que
    operamos" no mesmo sentido -- sao a camada de historiador, e ela ja tem
    numero proprio na faixa de credibilidade (150.000+ tags). Seis leem como
    dois grupos de tres; oito leem como uma lista.
    """
    if nomes is None:
        nomes = ('Ignition', 'VTScada', 'Canary Labs',
                 'Rockwell Automation', 'Siemens', 'Schneider Electric')
    cert = {n: c for n, _, c in PLATAFORMAS}
    chips = ''.join(
        '<span class="marca%s">%s</span>'
        % (' marca--certificada' if cert.get(n) else '', n)
        for n in nomes)
    return '<div class="marcas">%s</div>' % chips


def unidade(ident, video, alt, eyebrow, h2, corpo, cta_html, frase, legenda,
            webm=True, lado='esq'):
    """UMA UNIDADE DE VIDEO da home, e o sistema inteiro sai daqui.

    O formato foi definido pelo usuario depois de ver a dobra "The line does
    not care how clever the code is" no ar: **video pequeno com um texto ao
    lado; o video cresce ate tela cheia; outro texto por cima**. Repetido tres
    vezes.

    ISSO CONTRARIA `design.md` §5, e a contradicao fica registrada. O §5 diz
    que "o mecanismo muda a cada volta -- repetir o filme tres vezes
    transforma um momento em padrao e um padrao em tique". A regra foi escrita
    ANTES de existir uma dobra deste tipo no ar; o usuario viu a dobra pronta,
    aprovou o formato e pediu a repeticao.

    O QUE A REPETICAO CUSTA, e vale saber para poder decidir de novo: a versao
    anterior tinha quatro gestos diferentes (janela que abre, caixa que cresce,
    portas que correm, parallax). Agora ha DOIS -- o filme da montagem, uma
    vez, e a unidade, tres vezes. O que impede o tique de se instalar e o
    ASSUNTO, que muda a cada volta, e o texto, que carrega informacao
    diferente em cada uma.

    Cada unidade tem DOIS textos, e eles nao dizem a mesma coisa:

      coluna  eyebrow -> H2 -> paragrafo. SO TEXTO: ela e uma camada que
              passa por cima de um video prestes a tomar a tela, e nao pode
              conter alvo de clique -- ver a nota de `pointer-events` no CSS.
      rodape  a frase cinematografica, a legenda descritiva e o CTA. Ele
              aparece quando o video ja tomou a tela e fica durante a
              SUSTENTACAO inteira, que e a fase mais longa e mais estavel da
              unidade: e o unico lugar dela onde um botao e clicavel sem
              exigir que o visitante pare a rolagem no instante certo.

    `webm=False` para o clipe em que o VP9 saiu MAIOR que o h264: o build de
    video descarta esse arquivo, e apontar para ele daria 404.

    `lado` alterna a caixa entre esquerda e direita. As tres unidades
    partilham mecanismo, superficie e altura de trilho DE PROPOSITO -- e um
    sistema, e sistema se reconhece por repeticao. Mas com a caixa sempre do
    mesmo lado o teste de meio-fechar os olhos nao distingue a unidade 1 da 2
    nem da 3: sao tres dobras escuras com a mesma silhueta. Trocar o lado da
    ao olho o que diferenciar sem mexer em mais nada.
    """
    fontes = ''
    if webm:
        fontes += '<source src="video/%s.webm" type="video/webm">' % video
    fontes += '<source src="video/%s.mp4" type="video/mp4">' % video
    modelo = (
        '\n<section class="unidade%(mod)s" data-progresso data-abriu-em="0.32"\n'
        '         aria-labelledby="%(id)s-h">\n'
        '  <div class="unidade__palco">\n'
        # A ORDEM NO HTML e a do CELULAR: texto, video, frase. No desktop
        # ela nao importa -- os tres sao absolutos dentro do palco --, mas
        # no celular tudo volta ao fluxo e a ordem do documento vira a
        # ordem da leitura.
        #
        # Reordenar por `order:` no flex resolveria o visual e QUEBRARIA o
        # teclado: `order` nao muda a ordem de tabulacao, entao o foco
        # continuaria percorrendo o video antes do texto. A ordem certa e
        # a do documento.
        '    <div class="unidade__coluna">\n'
        '      <p class="eyebrow" style="--i:0">%(eyebrow)s</p>\n'
        '      <h2 id="%(id)s-h" style="--i:1">%(h2)s</h2>\n'
        '      <p style="--i:2">%(corpo)s</p>\n'
        '    </div>\n'
        '\n'
        # `data-progresso` NA JANELA, e ele so tem consumidor no CELULAR.
        #
        # No desktop a janela abre por `--abre`, que a SECAO deriva do curso
        # dela -- a secao tem 250vh de trilho e um palco preso, entao ha curso
        # de sobra e o mecanismo e da secao inteira. No celular a secao vira
        # `height: auto` e o palco sai do `sticky`: nao ha mais curso de
        # secao, e a janela precisa do proprio.
        #
        # E TEM DE SER O PROPRIO, e nao uma janela recortada do `--p` da
        # secao: a altura da secao no celular depende do tamanho do texto da
        # coluna, que muda de unidade para unidade. Qualquer faixa fixa de
        # `--p` da secao acertaria numa unidade e erraria nas outras duas.
        # Lendo a travessia dela mesma, a janela acerta sempre.
        #
        # Custo: tres alvos a mais no modulo 7 do main.js (30 -> 33 na home).
        # Ele ja roda com 35 na galeria, em duas passagens separadas de
        # leitura e escrita, entao nao ha layout forcado a mais por quadro.
        '    <div class="unidade__janela" data-progresso>\n'
        '      <video class="unidade__video" data-momento-video\n'
        '             muted loop playsinline preload="none"\n'
        '             poster="img/video/%(video)s.jpg"\n'
        '             aria-label="%(alt)s">%(fontes)s</video>\n'
        '      <div class="unidade__scrim" aria-hidden="true"></div>\n'
        '    </div>\n'
        '\n'
        '    <div class="unidade__rodape">\n'
        '      <p class="unidade__frase">%(frase)s</p>\n'
        '      <p class="unidade__legenda">%(legenda)s</p>\n'
        '      %(cta)s\n'
        '    </div>\n'
        '  </div>\n'
        '</section>\n')
    return modelo % {'id': ident, 'video': video, 'alt': alt, 'fontes': fontes,
                     'mod': ' unidade--dir' if lado == 'dir' else '',
                     'eyebrow': eyebrow, 'h2': h2, 'corpo': corpo,
                     'cta': cta_html, 'frase': frase, 'legenda': legenda}


def traco(nome, classe='traco__svg'):
    """Le um SVG de `fonte/svg/` e devolve o markup para ir INLINE na pagina.

    Inline e nao <img>/<object>, e a razao nao e economia de requisicao: um SVG
    referenciado por <img> vive num documento SEPARADO, e o CSS da pagina nao
    alcanca os <path> dele. Este traco precisa de duas coisas que so o CSS da
    pagina pode dar -- herdar `currentColor` e receber `stroke-dashoffset`
    atado a `--p`. Fora do documento, ele seria uma imagem parada.

    E a mesma razao pela qual Lottie ficou de fora (design.md §6.3): um JSON de
    Lottie tambem carrega as cores DENTRO em vez de herda-las.

    Os arquivos saem de `ferramentas/build_traco.py`, que extrai o tracado de
    aresta da propria fotografia.
    """
    cam = os.path.join(RAIZ, 'fonte', 'svg', nome + '.svg')
    with open(cam, encoding='utf-8') as f:
        svg = f.read().strip()
    # A CLASSE VEM DE QUEM CHAMA, e nao do gerador. `build_traco.py` escreve
    # `traco__svg` como padrao; se o chamador nao puder trocar, o CSS da
    # pagina nunca alcanca o <svg> -- e o sintoma e traicoeiro: os <path>
    # continuam desenhando, so que herdando a tinta do CORPO (#1A1A1A) em vez
    # da cor que a secao queria. Num campo navy isso da linhas ESCURAS sobre
    # escuro, que leem como sujeira de compressao e nao como defeito.
    return svg.replace('class="traco__svg"', 'class="%s"' % classe, 1)


def grade_plataformas(certificadas=None):
    """As plataformas como diagrama LADDER -- um degrau por plataforma.

    Substituiu uma grade de oito celulas iguais, que era um card grid com outro
    nome. A notacao aqui carrega informacao: contato ENERGIZADO (preenchido) e
    plataforma em que somos certificados, contato ABERTO e plataforma que
    apenas operamos. O que era so cor de texto virou estado de circuito.

    `certificadas` PARTE A ESCADA EM DUAS, e entrou em 2026-08-26 (decima
    rodada) junto com a reforma da secao em capabilities:

        None   as oito num rail so, como sempre foi
        True   so os tres degraus energizados
        False  so os cinco abertos

    POR QUE PARTIR. A escada de oito misturava os dois estados numa lista so, e
    o visitante tinha de DEDUZIR que contato cheio significa certificacao. A
    regra 10 de clean nao deixa explicar isso numa legenda -- entao o conserto
    e estrutural: cada grupo ganha o proprio rotulo na coluna esquerda ("Certi-
    fied on", "Fluent in"), e o rotulo diz o que a notacao mostra. A notacao
    para de precisar de traducao porque o titulo do grupo ja e a traducao.

    E de quebra faz o bloco cair no padrao de tres rotulos empilhados na coluna
    esquerda -- o mesmo conserto de coluna vazia que a dobra de abertura da
    home e o "why us" de who-we-are ja levaram."""
    quais = PLATAFORMAS if certificadas is None else [
        p for p in PLATAFORMAS if p[2] is certificadas]
    degraus = ''.join(
        '<div class="escada__degrau%s reveal" style="--i:%d">'
        '<span class="escada__fio" aria-hidden="true"></span>'
        '<span class="escada__contato" aria-hidden="true"></span>'
        '<p class="escada__nome">%s</p>'
        '<p class="escada__papel">%s%s</p>'
        '<span class="escada__fio escada__fio--fim" aria-hidden="true"></span>'
        '</div>'
        % (' escada__degrau--certificada' if cert else '', i, nome, papel,
           '<span class="escada__selo">CERTIFIED</span>' if cert else '')
        for i, (nome, papel, cert) in enumerate(quais))
    return '<div class="escada">%s</div>' % degraus


SETORES = [
    ('setores/oil-gas', [336, 672], 'setores/oil-gas-traco-900',
     'Oil &amp; Gas', 'Houston, Texas',
     'PI System support across a client base concentrated in Houston, with more '
     'than 150,000 historized tags under our care.',
     'Refinery process units at dusk'),
    ('setores/agua', [600], 'setores/agua-traco-600',
     'Water &amp; Wastewater', 'Florida',
     'Annual controls support, PLC and HMI programming, full SCADA integration and '
     'daily reports pulled straight from the SQL database.',
     'Raw water intake with large-diameter pipe'),
    ('setores/automotivo', [600], 'setores/automotivo-traco-600',
     'Automotive', 'Body shop lines',
     'Daimler (Mercedes-Benz) New Body Shop to the Integra PLC standard, and BMW '
     'F15/F16/F25/F26 Body Shop SSB to theirs.',
     'Robots welding a car body on an automotive line'),
    ('setores/papel', [336, 672], 'setores/papel-traco-900',
     'Paper Mills', 'Process controls',
     'Machine controls and drive coordination, where a lost second of tension is a '
     'lost roll.',
     'Row of industrial presses on a mill floor'),
    ('setores/solar', [336, 672], 'setores/solar-traco-900',
     'Solar &amp; Renewables', 'Utility scale',
     'Plant controls and monitoring for solar generation across the U.S., including '
     'work delivered under government contract.',
     'Utility-scale photovoltaic array'),
]


def grade_setores():
    cards = []
    for i, (base, larg, traco, nome, local, txt, alt) in enumerate(SETORES):
        cards.append(
            '<article class="setor reveal" style="--i:%d">'
            '<div class="setor__midia">%s</div>'
            '<h3 class="setor__nome">%s</h3>'
            '<p class="setor__local">%s</p>'
            '<p class="setor__txt">%s</p>'
            '</article>'
            % (i, lente(base, larg, traco, alt,
                        '(max-width: 700px) 92vw, (max-width: 1100px) 46vw, 22vw'),
               nome, local, txt))
    return '<div class="setores">%s</div>' % ''.join(cards)


GOVERNO = '''
<section class="secao secao--escura" id="government">
  <div class="container">
    <div class="bloco reveal">
      <div class="bloco__esq">
        <p class="eyebrow">Federal contracting</p>
        <h2>Vendor profile</h2>
      </div>
      <div class="bloco__dir">
        <p class="corpo">We hold an active vendor registration and deliver under federal
        contract, including controls work on solar generation across the United States.
        Everything a contracting officer needs to find us is on this page, in the format
        they search for.</p>
      </div>
    </div>

    <div class="credencial reveal">
      <div class="credencial__item">
        <p class="credencial__rotulo">UEI</p>
        <p class="credencial__valor">XUZ4WKEZLS67</p>
      </div>
      <div class="credencial__item">
        <p class="credencial__rotulo">CAGE</p>
        <p class="credencial__valor">9ZJM6</p>
      </div>
      <div class="credencial__item">
        <p class="credencial__rotulo">Primary NAICS</p>
        <p class="credencial__valor">541511</p>
        <p class="contato__nota">Custom Computer Programming Services</p>
      </div>
      <div class="credencial__item">
        <p class="credencial__rotulo">Secondary NAICS</p>
        <p class="credencial__valor credencial__valor--multi">238210 · 334513 · 335313 ·
        518210 · 541330 · 541512</p>
      </div>
    </div>

    <div class="marcas reveal" style="margin-top: var(--s-6)">
      <span class="marca marca--certificada">Ignition Certified</span>
      <span class="marca marca--certificada">VTScada Certified</span>
      <span class="marca marca--certificada">Canary Certified</span>
      <span class="marca">Lakewood Ranch, Florida</span>
      <span class="marca">Houston, Texas</span>
    </div>
  </div>
</section>'''


CONTATO_CTA = '''
<section class="secao secao--escura" id="contact">
  <div class="container">
    <div class="bloco reveal">
      <div class="bloco__esq">
        <p class="eyebrow">Talk to an engineer</p>
        <h2>Tell us what the <br>process has to do</h2>
      </div>
      <div class="bloco__dir">
        <p class="corpo">Send the scope, the P&amp;ID, or just the problem. You will get an
        engineer on the reply, not a form letter. And if the answer is that you do not
        need us, we will say that too.</p>
        %s
      </div>
    </div>

    <div class="contato reveal">
      <div class="contato__bloco">
        <p class="contato__rotulo">Sales &amp; Services</p>
        <p class="contato__valor"><a href="tel:+14078200299">%s</a></p>
        <p class="contato__nota">Also on WhatsApp</p>
      </div>
      <div class="contato__bloco">
        <p class="contato__rotulo">Support</p>
        <p class="contato__valor"><a href="tel:+19416661880">%s</a></p>
        <p class="contato__nota">Existing systems and annual contracts</p>
      </div>
      <div class="contato__bloco">
        <p class="contato__rotulo">E-mail</p>
        <p class="contato__valor"><a href="mailto:%s">%s</a></p>
        <p class="contato__nota">Scope, drawings and RFQs</p>
      </div>
      <div class="contato__bloco">
        <p class="contato__rotulo">Where we are</p>
        <p class="contato__valor">Lakewood Ranch, FL</p>
        <p class="contato__nota">Oil &amp; Gas operation in Houston, TX</p>
      </div>
    </div>
  </div>
</section>''' % (cta('contact.html', 'Contact us'), TEL_VENDAS, TEL_SUPORTE, EMAIL, EMAIL)
