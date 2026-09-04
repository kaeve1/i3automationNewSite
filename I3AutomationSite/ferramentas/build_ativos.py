# -*- coding: utf-8 -*-
"""Publica CSS e JS: da FONTE comentada para o `site/` enxuto.

POR QUE ISTO EXISTE, e a decisao vale mais que o codigo.

O usuario pediu para "retirar todos os comentarios do codigo". O ganho e real
-- 49% do CSS+JS deste site sao comentario, 195 KB. Mas apagar da FONTE
contradiz a regra critica no3 do CLAUDE.md: "se um numero entrar no CSS, tem
que existir a conta que o produziu". Sao 88 medicoes so no style.css: cada
contraste WCAG, cada proporcao conferida, cada armadilha que custou uma sessao.

Entao a separacao: a fonte fica em `fonte/`, comentada; o `site/` recebe a
versao publicada, sem comentario. O deploy continua sendo "publicar a pasta
site/" -- este script roda na AUTORIA, junto com build_site.py, exatamente
como o gerador de paginas ja fazia.

O QUE ELE NAO FAZ, de proposito: nao renomeia variavel, nao reordena regra,
nao junta seletor, nao remove ponto-e-virgula. Minificador agressivo troca
bytes por risco, e este site nao tem teste automatizado que pegue uma
regressao dessas. O que sai e o que e SEGURO tirar: comentario, indentacao e
linha em branco.

A ARMADILHA DO STRIPPER DE JS, que e o motivo de ele nao ser um regex de tres
linhas: `//` aparece dentro de string -- `"https://i3automations.com"` -- e
dentro de expressao regular. Um stripper ingenuo come a URL inteira a partir
do `//` e o arquivo continua com sintaxe valida, entao nem o `node --check`
acusa. Por isso aqui ha uma maquina de estados que sabe onde esta: string
simples, dupla, template, regex ou codigo.

Uso: python ferramentas/build_ativos.py
"""
import hashlib
import json
import os
import re
import shutil

RAIZ = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
FONTE = os.path.join(RAIZ, 'fonte')
DEST = os.path.join(RAIZ, 'site')


def tirar_comentarios_js(src):
    """Remove comentarios de JS respeitando string, template e regex.

    Devolve (saida, literais) -- a lista de literais serve de PROVA: se um
    deles mudou, o stripper comeu conteudo em vez de comentario.
    """
    out = []
    literais = []
    i, n = 0, len(src)
    # o ultimo token significativo decide se `/` abre regex ou e divisao
    anterior = ''
    while i < n:
        c = src[i]
        d = src[i:i + 2]

        if d == '//':
            j = src.find('\n', i)
            i = n if j < 0 else j
            continue
        if d == '/*':
            j = src.find('*/', i + 2)
            i = n if j < 0 else j + 2
            # comentario entre tokens vira espaco, senao `a/*x*/b` colaria
            out.append(' ')
            continue

        if c in '"\'`':
            fim = c
            j = i + 1
            while j < n:
                if src[j] == '\\':
                    j += 2
                    continue
                if src[j] == fim:
                    break
                j += 1
            lit = src[i:j + 1]
            out.append(lit)
            literais.append(lit)
            anterior = 'lit'
            i = j + 1
            continue

        if c == '/' and anterior not in ('ident', ')', ']', 'lit'):
            # expressao regular: consome ate a barra de fecho, pulando classes
            j = i + 1
            classe = False
            while j < n:
                if src[j] == '\\':
                    j += 2
                    continue
                if src[j] == '[':
                    classe = True
                elif src[j] == ']':
                    classe = False
                elif src[j] == '/' and not classe:
                    break
                elif src[j] == '\n':
                    break
                j += 1
            out.append(src[i:j + 1])
            anterior = 'lit'
            i = j + 1
            continue

        out.append(c)
        if c.isalnum() or c in '_$':
            anterior = 'ident'
        elif c in ')]':
            anterior = c
        elif not c.isspace():
            anterior = c
        i += 1
    return ''.join(out), literais


def enxugar(txt):
    """Tira indentacao e linha em branco, preservando o resto verbatim.

    NAO colapsa espacos dentro da linha: `calc(100% - 20px)` PRECISA dos
    espacos em volta do `-`, e um minificador que os remove quebra o calc sem
    erro nenhum -- o valor simplesmente vira invalido e a declaracao cai.
    """
    linhas = []
    for ln in txt.split('\n'):
        ln = ln.rstrip()
        if not ln.strip():
            continue
        linhas.append(ln.strip())
    return '\n'.join(linhas) + '\n'


# PECAS GUARDADAS, NAO APAGADAS -- e a distincao e do design.md §8:
# "Nada do que sai e apagado do repositorio -- sai da pagina, fica no
# `fonte/js/`." O que a regra protege e a FONTE, e ela continua intacta.
#
# Publicar em `site/js/` e outra coisa: e mandar ao ar 31 KB de JavaScript que
# nenhuma das nove paginas carrega. `varredura.py` os acusava como orfaos, e
# eles eram mesmo -- so que apagar a fonte teria sido o conserto errado.
#
#   clp.js ..... o CLP explodido, saiu de capabilities (o lugar dele agora e a
#                macro do modulo de reles)
#   planta.js .. a planta isometrica, saiu da home (que virou video e tres
#                momentos)
#   marca.js ... a marca extrudada, saiu de who-we-are -- e esta e a mais
#                importante das tres: ela extruda o RE-DESENHO da marca, e
#                mante-la no ar reintroduziria exatamente o erro que o cliente
#                reclamou.
#   lente.js ... a lente de revelacao dos cards de setor. A grade de setores
#                saiu da home em 2026-08-26 e a lente ficou sem nenhum
#                consumidor -- `varredura.py` a acusou como orfa. O CSS dela
#                (§7) continua no arquivo, e o `lente()` continua em
#                build_paginas.py.
# O QUE FICA NA FONTE E NAO VAI PARA O DEPLOY.
#
# `design.md` §8 manda guardar a peca que sai da pagina: *"Nada do que sai e
# apagado do repositorio -- sai da pagina, fica no `fonte/js/`."*
#
# `aposentado.css` ENTROU EM 2026-08-27, na vistoria de acabamento, e ele
# fecha uma metade que faltava da mesma regra: o JS das pecas aposentadas ja
# ficava de fora do deploy, mas o CSS DELAS continuava viajando dentro de
# `style.css` -- 16.776 bytes, 18,3% do arquivo publicado, em 116 regras que
# nao casavam com um unico elemento das dez paginas. CSS segura a primeira
# pintura; 18% dele morto custa em toda visita.
GUARDADAS = {'clp.js', 'planta.js', 'marca.js', 'lente.js', 'aposentado.css'}


MANIFESTO = os.path.join(os.path.dirname(os.path.abspath(__file__)),
                         '_publicado.json')


def _manifesto():
    try:
        with open(MANIFESTO, encoding='utf-8') as fh:
            return json.load(fh)
    except (IOError, ValueError):
        return {}


def conferir_mao(caminho, novo):
    """Avisa quando o arquivo publicado foi editado A MAO desde o ultimo build.

    SUBSTITUI O BANNER `/* GERADO ... */`, e substitui com vantagem. O banner
    era um aviso passivo: so servia se a pessoa abrisse o arquivo E lesse a
    primeira linha. Esta conferencia e ativa -- ela compara o que esta no disco
    com o que o ultimo build escreveu, e fala ANTES de sobrescrever.

    O acidente que as duas previnem e real e esta registrado: `memorianew.md`
    §94 conta o usuario reescrevendo uma frase direto em
    `site/capabilities.html`, que o build seguinte teria apagado sem sinal
    nenhum. Foi preciso portar a frase para o gerador as pressas.

    NAO ABORTA, so avisa. Abortar transformaria um arquivo editado por engano
    numa parede: o build inteiro pararia e o jeito de sair seria apagar o
    arquivo, que e exatamente o trabalho que se queria salvar. O aviso deixa a
    decisao com quem leu.
    """
    if not os.path.exists(caminho):
        return
    esperado = _manifesto().get(os.path.basename(caminho))
    if esperado is None:
        return                      # primeiro build depois da mudanca
    with open(caminho, encoding='utf-8') as fh:
        atual = hashlib.sha1(fh.read().encode('utf-8')).hexdigest()
    if atual != esperado and atual != hashlib.sha1(novo.encode('utf-8')).hexdigest():
        print('   AVISO  %s foi editado a mao desde o ultimo build.'
              % os.path.relpath(caminho))
        print('          O conteudo vai ser SOBRESCRITO agora. A fonte e'
              ' fonte/%s.' % os.path.basename(caminho))


def registrar_mao(caminho, escrito):
    m = _manifesto()
    m[os.path.basename(caminho)] = hashlib.sha1(escrito.encode('utf-8')).hexdigest()
    with open(MANIFESTO, 'w', encoding='utf-8') as fh:
        json.dump(m, fh, indent=1, sort_keys=True)


def publicar():
    rel = []
    for sub, ext in (('css', '.css'), ('js', '.js')):
        origem = os.path.join(FONTE, sub)
        destino = os.path.join(DEST, sub)
        if not os.path.isdir(origem):
            continue
        os.makedirs(destino, exist_ok=True)
        for nome in sorted(os.listdir(origem)):
            if not nome.endswith(ext):
                continue
            if nome in GUARDADAS:
                continue
            with open(os.path.join(origem, nome), encoding='utf-8') as fh:
                src = fh.read()
            antes = len(src.encode('utf-8'))

            if ext == '.js':
                saida, lit_antes = tirar_comentarios_js(src)
                _, lit_depois = tirar_comentarios_js(saida)
                # PROVA: nenhum literal pode ter mudado. Se mudou, o stripper
                # comeu conteudo -- e conteudo comido continua compilando.
                assert lit_antes == lit_depois, \
                    '%s: literal alterado pelo stripper' % nome
            else:
                saida = re.sub(r'/\*.*?\*/', '', src, flags=re.S)

            saida = enxugar(saida)
            # O BANNER SAIU EM 2026-08-27, a pedido: *"elimine todo resquicio
            # de comentario desse repositorio"*, com o escopo fechado no que
            # vai ao ar. Ele era a unica linha de comentario que sobrevivia ao
            # deploy -- 11 arquivos, uma linha cada.
            #
            # ELE TINHA UMA FUNCAO, E ELA NAO FOI JOGADA FORA. O banner
            # avisava quem abrisse `site/css/style.css` que o proximo build
            # sobrescreve o arquivo -- e o aviso existe porque o acidente ja
            # aconteceu: `memorianew.md` §94 registra o usuario editando uma
            # frase direto em `site/capabilities.html`, que o build seguinte
            # teria apagado sem dizer nada.
            #
            # Quem faz esse trabalho agora e `conferir_mao()`, e faz melhor: o
            # banner dependia de alguem LER; a conferencia PEGA a edicao e
            # avisa antes de sobrescrever. Zero byte no deploy, e a guarda
            # passou de passiva a ativa.
            caminho = os.path.join(destino, nome)
            conferir_mao(caminho, saida)
            with open(caminho, 'w', encoding='utf-8') as fh:
                fh.write(saida)
            registrar_mao(caminho, saida)
            depois = len(saida.encode('utf-8'))
            rel.append((sub + '/' + nome, antes, depois))
    return rel


def main():
    if not os.path.isdir(FONTE):
        raise SystemExit('fonte/ nao existe -- nada a publicar')
    rel = publicar()
    print('== ativos publicados (fonte/ -> site/) ==')
    ta = td = 0
    for nome, a, d in rel:
        ta += a
        td += d
        print('   %-22s %7.1fK -> %6.1fK   -%2.0f%%'
              % (nome, a / 1024, d / 1024, 100 * (a - d) / a))
    print('   %-22s %7.1fK -> %6.1fK   -%2.0f%%'
          % ('TOTAL', ta / 1024, td / 1024, 100 * (ta - td) / ta))


if __name__ == '__main__':
    main()
