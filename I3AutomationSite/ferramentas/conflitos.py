# -*- coding: utf-8 -*-
"""Acusa a regra que vence EM SILENCIO.

Mesmo seletor, mesmo contexto de media, mesma propriedade declarada duas
vezes: a de baixo ganha por ordem de cascata, sem erro, sem aviso, e sem
aparecer em nenhuma lista de codigo morto -- porque a classe ESTA em uso.

E a classe de defeito que memoria.md registra mais vezes neste projeto:
`.setores` colidindo entre duas paginas, `.botao:hover` vencendo o repouso
escrito depois, `.nav__painel a` batendo `.botao`. Todas do mesmo formato.

Achou, em 20/08: `.galeria__item`, `.galeria__item img` e `.galeria__legenda`
declaradas duas vezes -- a copia velha, da grade quadrada, carregava
`aspect-ratio: 1`. Estava sombreada pela boa e nao fazia mal NENHUM hoje; mas
com a mesma especificidade, qualquer reordenacao do arquivo colocaria as 29
fotos do mosaico de volta em quadrado, desfazendo as 8 proporcoes nativas.

Uso: python ferramentas/conflitos.py
"""
import re, io
from collections import defaultdict

s = io.open('fonte/css/style.css', encoding='utf-8').read()
s = re.sub(r'/\*.*?\*/', '', s, flags=re.S)

# quebra em (contexto_media, seletor, corpo)
regras = []
i = 0
pilha = []
buf = ''
tok = re.finditer(r'([^{}]*)([{}])', s)
for m in tok:
    txt, br = m.group(1), m.group(2)
    if br == '{':
        cab = txt.strip()
        if cab.startswith('@'):
            pilha.append(cab)
        else:
            pilha.append(None)
            corpo_ini = m.end()
            # acha o fecho correspondente
            prof = 1
            j = corpo_ini
            while prof and j < len(s):
                if s[j] == '{': prof += 1
                elif s[j] == '}': prof -= 1
                j += 1
            ctx = ' && '.join(x for x in pilha if x)
            regras.append((ctx, re.sub(r'\s+', ' ', cab), s[corpo_ini:j-1], corpo_ini))
    else:
        if pilha: pilha.pop()

mapa = defaultdict(list)
for ctx, sel, corpo, pos in regras:
    for d in re.finditer(r'([-a-zA-Z]+)\s*:', corpo):
        prop = d.group(1)
        if prop.startswith('--'): continue
        mapa[(ctx, sel, prop)].append(pos)

conf = {k: v for k, v in mapa.items() if len(v) > 1}
# ignora repeticao DENTRO da mesma regra (fallback proposital, ex: overflow)
reais = {}
for (ctx, sel, prop), pos in conf.items():
    if len(set(pos)) > 1:
        reais[(ctx, sel, prop)] = sorted(set(pos))

print('seletores duplicados com propriedade repetida: %d' % len(reais))
print()
for (ctx, sel, prop), pos in sorted(reais.items(), key=lambda x: x[1][0]):
    lns = [s[:p].count('\n') + 1 for p in pos]
    print('  %-46s %-18s linhas %s%s'
          % (sel[:46], prop, lns, ('   [%s]' % ctx[:40]) if ctx else ''))
