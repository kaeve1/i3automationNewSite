# -*- coding: utf-8 -*-
"""Varredura de referencias do site: nada quebrado, nada orfao.

Regra do projeto: arquivo que ninguem cita nao entra em site/. Este script e
o que confere -- roda depois de qualquer mexida em asset ou em template.
"""
import glob
import json
import os
import re

RAIZ = 'site'


def referencias():
    refs = set()
    alvos = glob.glob(RAIZ + '/**/*.html', recursive=True) + \
        glob.glob(RAIZ + '/css/*.css') + glob.glob(RAIZ + '/js/*.js')
    for f in alvos:
        t = open(f, encoding='utf-8').read()
        base = os.path.dirname(os.path.relpath(f, RAIZ)).replace(os.sep, '/')
        # `poster` entra na mesma leitura que `src` e `href`, e ele NAO estava
        # aqui. O sintoma era silencioso e enganoso ao mesmo tempo: os tres
        # posteres de video apareciam na lista de ORFAOS, sugerindo que dava
        # para apaga-los -- quando na verdade sao obrigatorios por spec
        # (design.md §5.4) e sao o que o visitante ve enquanto o video nao
        # decodifica, e para sempre com `prefers-reduced-motion`.
        # Uma varredura que chama de orfao o que e obrigatorio e pior que
        # varredura nenhuma: ela convida a apagar o arquivo certo.
        for m in re.findall(r'(?:src|href|poster)="([^"#:]+)"', t):
            refs.add(os.path.normpath(os.path.join(base, m)))
        for m in re.findall(r'url\(\s*"?([^")]+?)"?\s*\)', t):
            # `data:` PRECISA sair ANTES do join. O filtro la embaixo testa o
            # prefixo, e depois de `os.path.join('css', 'data:image/...')` o
            # prefixo ja e "css/" -- o teste passava batido e um SVG embutido
            # virava referencia quebrada. Icone desenhado inline em mask-image
            # e tecnica normal aqui, entao o alarme era 100% falso.
            if m.startswith('data:'):
                continue
            refs.add(os.path.normpath(os.path.join(base, m)))
        for m in re.findall(r'srcset="([^"]+)"', t):
            for parte in m.split(','):
                refs.add(os.path.normpath(os.path.join(base, parte.strip().split(' ')[0])))
        # og:image e o JSON-LD apontam pelo dominio absoluto, nao por caminho
        # relativo. Sem esta linha o og-1200.jpg e o logo-icone.svg apareciam
        # como orfaos a cada varredura -- alarme falso que treina a ignorar.
        for m in re.findall(r'https://i3automations\.com/([^"\s]+)', t):
            refs.add(os.path.normpath(m))
    # O MANIFESTO TAMBEM APONTA PARA ARQUIVOS, e por uma chave que nenhum dos
    # padroes acima casa (`"src"`, dentro de JSON). Sem esta leitura os dois
    # icones do Android apareciam como orfaos -- e a tentacao seria isenta-los
    # a mao, que e como um icone de verdade sem uso passa despercebido depois.
    # Os caminhos do manifesto sao relativos a ELE, ou seja a raiz do site.
    manifesto = os.path.join(RAIZ, 'site.webmanifest')
    if os.path.exists(manifesto):
        dados = json.load(open(manifesto, encoding='utf-8'))
        for icone in dados.get('icons', []):
            if icone.get('src'):
                refs.add(os.path.normpath(icone['src']))

    limpo = set()
    for r in refs:
        r = r.replace(os.sep, '/')
        if r.startswith(('http', 'mailto', 'tel', 'data:')):
            continue
        limpo.add(r)
    return limpo


def arquivos():
    saida = set()
    for pasta, _, nomes in os.walk(RAIZ):
        for n in nomes:
            saida.add(os.path.relpath(os.path.join(pasta, n), RAIZ).replace(os.sep, '/'))
    return saida


if __name__ == '__main__':
    refs, arq = referencias(), arquivos()
    quebradas = sorted(r for r in refs if r not in arq)
    # SITEMAP E ROBOTS NAO SAO ORFAOS. Eles existem justamente para NAO serem
    # linkados de dentro do site: sao a porta por onde o rastreador entra, e
    # ele os procura pelo nome, na raiz. Sem esta linha os dois apareceriam
    # como orfaos a cada varredura -- alarme falso que treina a ignorar, que e
    # o mesmo motivo pelo qual o og:image absoluto ja tinha excecao acima.
    # `_headers` e `404.html` entram pelo mesmo motivo, por vias diferentes:
    # o primeiro e lido pela HOSPEDAGEM, nunca pelo navegador; o segundo e
    # servido quando o caminho NAO EXISTE, entao por definicao nenhum link
    # aponta para ele. Link para a 404 seria justamente o defeito.
    # `favicon.ico` e o terceiro caso do mesmo tipo: o navegador o pede em
    # `/favicon.ico` por conta propria, e o buscador olha para la. Ele TEM
    # link no HTML tambem, entao nao chega a ser orfao -- fica listado aqui
    # como documentacao de que a ausencia do link nao seria defeito.
    # `.htaccess`, `_headers` e `_redirects` entram pelo mesmo motivo: sao
    # lidos pela HOSPEDAGEM, nunca pelo navegador, e por definicao nenhum link
    # aponta para eles. Sao TRES porque a hospedagem decide qual vale --
    # `.htaccess` em Apache (que e o caso hoje: i3automations.com roda Apache
    # na HostGator), `_headers` e `_redirects` em Cloudflare Pages ou Netlify.
    # Os inertes nao atrapalham, e publicar os dois conjuntos e o que faz uma
    # troca de hospedagem nao exigir uma entrega.
    PORTAS = {'sitemap.xml', 'robots.txt', '_headers', '_redirects',
              '.htaccess', '404.html', 'favicon.ico', 'site.webmanifest'}
    orfaos = sorted(a for a in arq
                    if a not in refs and not a.endswith('.html') and a not in PORTAS)
    print('%d referencias unicas, %d arquivos' % (len(refs), len(arq)))
    for q in quebradas:
        print('  QUEBRADA  %s' % q)
    for o in orfaos:
        print('  ORFAO     %s  (%.1f KB)' % (o, os.path.getsize(RAIZ + '/' + o) / 1024))
    if not quebradas and not orfaos:
        print('  tudo certo: 0 quebradas, 0 orfaos')
