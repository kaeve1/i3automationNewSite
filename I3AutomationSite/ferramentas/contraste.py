# -*- coding: utf-8 -*-
"""Contraste WCAG 2.1 dos pares que o site usa de verdade.

Regra do projeto (CLAUDE.md #3): se um numero entra no CSS, existe a conta que
o produziu. Este arquivo E a conta. Rodar de novo apos qualquer mexida em cor.

REESCRITO EM 2026-08-25. Duas coisas mudaram a matriz:

  1. TEMA UNICO (design.md §1.4 regra 6). A tabela tinha um par por tema e
     agora tem metade do tamanho. Nao e simplificacao cosmetica: a matriz
     antiga tinha 28 linhas de texto, e 14 delas verificavam um tema que nao
     existe mais.

  2. O DOURADO SAIU DO SITE (design.md §1.4 regra 1). #FDC500 vive so dentro
     do logo. A linha "ALERTA dourado sobre branco", que existia para provar
     que ele nao servia de texto, deixou de ser um alerta e virou a razao de
     ele nao estar mais aqui. Ela sai; entra a familia azul.

A ARMADILHA QUE ESTA RODADA REVELOU, e que este arquivo agora cobre: as bordas
brancas com alfa foram todas medidas sobre #001D3D. Com o bloco escuro
clareando para --azul-bloco #0D4477, o MESMO alfa passou a dar menos
contraste — superficie mais clara pede MAIS alfa, nao menos. O feixe a .38
caiu de 3,47:1 para 2,79:1 e passou a reprovar sem que nada acusasse.

Uso: python ferramentas/contraste.py
"""


def canal(c):
    c = c / 255
    return c / 12.92 if c <= 0.04045 else ((c + 0.055) / 1.055) ** 2.4


def lum(h):
    h = h.lstrip('#')
    r, g, b = (int(h[i:i + 2], 16) for i in (0, 2, 4))
    return 0.2126 * canal(r) + 0.7152 * canal(g) + 0.0722 * canal(b)


def razao(a, b):
    la, lb = lum(a), lum(b)
    return (max(la, lb) + 0.05) / (min(la, lb) + 0.05)


def sobre(fundo, fg, alfa):
    """Achata uma cor com alfa sobre o fundo — rgba nao tem contraste sozinho."""
    f = [int(fundo.lstrip('#')[i:i + 2], 16) for i in (0, 2, 4)]
    c = [int(fg.lstrip('#')[i:i + 2], 16) for i in (0, 2, 4)]
    m = [round(cc * alfa + ff * (1 - alfa)) for cc, ff in zip(c, f)]
    return '#%02X%02X%02X' % tuple(m)


# ---------------------------------------------------------------- a paleta
T = {
    # marca — a unica cor medida
    'navy':        '#003566',
    # familia azul, derivada em HSL preservando o matiz 209
    'azul':        '#4D8ECB',
    'azul-txt':    '#2C6396',
    'azul-luz':    '#88B4DD',
    'azul-bloco':  '#0D4477',
    'azul-chip':   '#DCE9F5',
    # superficies
    'sup-1':       '#FFFFFF',
    'sup-2':       '#F2F5F8',
    'sup-q':       '#F7F3EC',
    'sup-3':       '#0D4477',   # = azul-bloco
    'sup-3-fundo': '#082A49',
    # tinta
    'tinta':       '#1A1A1A',
    'tinta-2':     '#40607F',
    'tinta-suave': '#5A5A5A',
    'borda-ui':    '#6E8093',
    # o azul que serve sobre FOTOGRAFIA velada, onde --azul-luz nao serve
    'azul-foto':   '#B9D2EA',
}

CLARAS = ('sup-1', 'sup-2', 'sup-q')

# (rotulo, texto, fundo, minimo exigido)
PARES = []

# --- corpo e hierarquia de tinta sobre as tres superficies claras
for s in CLARAS:
    PARES.append(('corpo sobre %s' % s, T['tinta'], T[s], 4.5))
for s in CLARAS:
    PARES.append(('eyebrow sobre %s' % s, T['tinta-2'], T[s], 4.5))
for s in CLARAS:
    PARES.append(('legenda sobre %s' % s, T['tinta-suave'], T[s], 4.5))
for s in CLARAS:
    PARES.append(('titulo navy sobre %s' % s, T['navy'], T[s], 4.5))

# --- o accent, e a disciplina de DOIS TOKENS que ele exige
for s in CLARAS:
    PARES.append(('link --azul-txt sobre %s' % s, T['azul-txt'], T[s], 4.5))
PARES += [
    # A prova de que --azul e preenchimento de FORMA e nunca texto sobre claro.
    # 3,47:1 passa como elemento grafico e reprova como texto — e por isso que
    # --azul-txt existe (design.md §1.4 regra 2).
    ('--azul como regua sobre branco', T['azul'], T['sup-1'], 3.0),
    ('--azul como regua sobre quente', T['azul'], T['sup-q'], 3.0),

    # --- o bloco escuro
    ('branco sobre --azul-bloco', '#FFFFFF', T['sup-3'], 4.5),
    ('paragrafo .78 sobre o bloco', sobre(T['sup-3'], '#FFFFFF', .78), T['sup-3'], 4.5),
    ('--azul-luz sobre o bloco', T['azul-luz'], T['sup-3'], 4.5),
    ('--azul-luz sobre --navy', T['azul-luz'], T['navy'], 4.5),
    ('branco sobre o rodape', '#FFFFFF', T['sup-3-fundo'], 4.5),
    ('--azul-luz sobre o rodape', T['azul-luz'], T['sup-3-fundo'], 4.5),

    # --- o chip do CTA
    ('navy sobre --azul-chip', T['navy'], T['azul-chip'], 4.5),

    # --- fotografia velada: o override local que .secao--foto declara
    ('--azul-foto sobre foto velada', T['azul-foto'], '#33587D', 4.5),
]

# OS QUATRO MOMENTOS DA HOME. Cada um tem uma superficie diferente sob o
# mesmo texto branco, e a diferenca entre elas e grande: o bloco chapado da
# variacao A da 9,95:1 de graca, e a tela de IHM da variacao C da 1,47:1 e
# precisa do scrim mais forte do site.
#
# Os valores de "sob scrim" abaixo sao o PIOR PONTO da faixa onde o texto
# vive, medido no poster (percentil 90 da luminancia). O calculo completo por
# quadro esta no cabecalho de cada bloco em style.css §6c.
MOMENTOS = [
    ('M1 filme   frase sobre a agua, sob scrim', '#FFFFFF', '#2E4A63', 4.5),
    ('M2 var.A   corpo sobre o bloco chapado',
     sobre(T['sup-3'], '#FFFFFF', .78), T['sup-3'], 4.5),
    ('M2 var.A   legenda .62 sobre o bloco',
     sobre(T['sup-3'], '#FFFFFF', .62), T['sup-3'], 4.5),
    ('M3 var.C   frase sobre a IHM, sob scrim', '#FFFFFF', '#28455F', 4.5),
    ('M4 var.B   frase sobre a refinaria velada', '#FFFFFF', '#2C4A6B', 4.5),
    ('M4 var.B   o traco .85 sobre a foto velada',
     '#DCE4EC', '#2C4A6B', 3.0),
]

# --- o hover, a tabela inteira de plano.md §6.1
HOVER = [
    ('claro  .botao         campo --navy', '#FFFFFF', T['navy'], 4.5),
    ('claro  .botao         campo vs sup-1', T['navy'], T['sup-1'], 3.0),
    ('claro  .botao         campo vs sup-q', T['navy'], T['sup-q'], 3.0),
    ('claro  .botao--princ  campo --azul-txt', '#FFFFFF', T['azul-txt'], 4.5),
    ('escuro ambos          campo --azul-luz', T['navy'], T['azul-luz'], 4.5),
    ('escuro ambos          campo vs bloco', T['azul-luz'], T['sup-3'], 3.0),
    # A seta e ICONE: o piso e o de conteudo nao-textual, 3:1.
    ('claro  .cta__chip     seta navy', T['navy'], T['azul'], 3.0),
    ('escuro .cta__chip     seta navy', T['navy'], T['azul-luz'], 3.0),
]

# Bordas e reguas: alvo 3:1 (componente nao-textual, WCAG 1.4.11).
# Filete DECORATIVO e isento e nao aparece aqui — a distincao esta em
# tokens.css, na secao LINHAS, e tratar as duas familias como uma so e o erro
# comum.
BORDAS = [
    ('--borda-ui sobre sup-1', T['borda-ui'], T['sup-1'], 3.0),
    ('--borda-ui sobre sup-2', T['borda-ui'], T['sup-2'], 3.0),
    ('--borda-ui sobre sup-q', T['borda-ui'], T['sup-q'], 3.0),
    ('--borda-ui-esc .45 sobre o bloco',
     sobre(T['sup-3'], '#FFFFFF', .45), T['sup-3'], 3.0),
    ('feixe .45 sobre o bloco',
     sobre(T['sup-3'], '#FFFFFF', .45), T['sup-3'], 3.0),
    ('aresta do rodape .55 sobre o rodape',
     sobre(T['sup-3-fundo'], '#FFFFFF', .55), T['sup-3-fundo'], 3.0),
    ('foco --navy sobre sup-1', T['navy'], T['sup-1'], 3.0),
    ('foco branco sobre o bloco', '#FFFFFF', T['sup-3'], 3.0),
]

# O que MORREU na medicao, e continua aqui para nao ser reinventado. Estas
# linhas DEVEM reprovar: cada uma e um token que alguem vai propor de novo.
LAPIDES = [
    ('--azul sobre o bloco escuro', T['azul'], T['sup-3'], 3.0,
     'por isso --azul-luz existe'),
    ('--navy como campo no bloco escuro', T['navy'], T['sup-3'], 3.0,
     'navy morre no escuro: 1,24:1'),
    ('--azul-luz como campo no claro', T['azul-luz'], T['sup-1'], 3.0,
     '--azul-luz morre no claro: 2,18:1'),
    ('--azul como texto sobre branco', T['azul'], T['sup-1'], 4.5,
     'e forma, nao texto — use --azul-txt'),
    ('#FDC500 como texto sobre branco', '#FDC500', T['sup-1'], 4.5,
     'o dourado saiu do site; vive so no logo'),
    ('--navy-hover #002647 vs --navy', '#002647', T['navy'], 1.5,
     'delta 1,24x: imperceptivel. Quem ocupa o papel e --azul-txt, a 1,96x'),
    ('feixe .38 sobre o bloco novo', sobre(T['sup-3'], '#FFFFFF', .38),
     T['sup-3'], 3.0, 'era 3,47:1 sobre #001D3D; o bloco clareou e caiu'),
    ('--azul-luz sobre foto velada', T['azul-luz'], '#33587D', 4.5,
     'campo chapado nao e fotografia: .secao--foto troca para #B9D2EA'),
    ('M3 var.C   frase SEM scrim sobre a IHM', '#FFFFFF', '#C9CFD6', 4.5,
     'uma tela de IHM e interface CLARA: 1,47:1. Dai o scrim mais forte do site'),
    ('M1 filme   frase no MEIO do quadro', '#FFFFFF', '#7E8C99', 4.5,
     'o scrim tem buraco no meio de proposito; por isso a frase vive no pe'),
]


def tabela(titulo, pares):
    print('\n%s' % titulo)
    print('-' * 74)
    falhas = 0
    for rotulo, fg, bg, minimo in pares:
        r = razao(fg, bg)
        ok = r >= minimo
        if not ok:
            falhas += 1
        print('%-42s %6.2f:1  min %.1f  %s' % (rotulo, r, minimo, 'ok' if ok else 'FALHA'))
    return falhas


def lapides():
    print('\nO QUE MORREU NA MEDICAO — estas linhas DEVEM reprovar')
    print('-' * 74)
    surpresas = 0
    for rotulo, fg, bg, minimo, porque in LAPIDES:
        r = razao(fg, bg)
        if r >= minimo:
            surpresas += 1
            print('%-42s %6.2f:1  PASSOU?! revisar' % (rotulo, r))
        else:
            print('%-42s %6.2f:1  reprova, como esperado' % (rotulo, r))
            print('%44s%s' % ('', porque))
    return surpresas


if __name__ == '__main__':
    f = tabela('TEXTO E ACCENT', PARES)
    f += tabela('OS QUATRO MOMENTOS DA HOME', MOMENTOS)
    f += tabela('HOVER (plano.md §6.1)', HOVER)
    f += tabela('BORDAS E REGUAS (nao-textual, 3:1)', BORDAS)
    s = lapides()
    print('\n%d falha(s) na matriz viva.' % f)
    if s:
        print('%d lapide(s) passaram e nao deveriam — a paleta mudou embaixo delas.' % s)
