# -*- coding: utf-8 -*-
"""Gera a familia de icones a partir da ARTE REAL do cliente.

REESCRITO EM 2026-08-25 (doit.md Fase 3). E TROCA DE FONTE, NAO PATCH.

Ate aqui este arquivo rasterizava `site/brand/favicon.svg` -- um REDESENHO do
logo, feito com `<rect>` e um "3" de lados retos. Era a terceira copia do
glifo no repositorio, e foi exatamente o que o cliente reparou: "mudei a
logo". Ele nao tinha mandado logo novo; mandou o dele de volta.

A fonte de verdade agora e `logo/logonova.png`, via os PNGs que
`build_marca.py` recorta dela. O `favicon.svg` SAIU do site junto com o
`<link rel="icon" type="image/svg+xml">` que o servia: manter um SVG que
desenha uma marca diferente da marca so recria o problema numa quarta copia.
Vetorizar a arte real e polimento para depois (design.md §3.6) -- PNG em
1x/2x/3x e pixel-fiel por definicao, e o UnidoCLP ja serve marca em PNG.

----------------------------------------------------------------------------
POR QUE DOIS RECORTES, E NAO UM

Medido, renderizando os candidatos nos tamanhos reais: a marca inteira e
1,571:1, entao num quadrado de 16px ela ocupa 16x10 e a moldura do notebook
vira uma barra de 1px. O "i3" dentro dela fica com 4px de altura e some.

  tamanho | marca inteira            | so a tela
  --------|--------------------------|---------------------------
   16px   | borrao, moldura de 1px   | campo dourado + glifo, le
   32px   | limite, ja da            | le
   48px+  | le bem                   | perde a moldura, que e o desenho

Entao o recorte muda com o tamanho, e isso NAO e inconsistencia: e a mesma
decisao que o SVG antigo tomava ("no favicon a moldura vira so a base"),
tomada agora sobre a arte certa.

  16/32/48 -> a TELA (330x215 na arte, a maior regiao dourada conexa).
              Campo dourado com o glifo navy: a assinatura de cor da marca,
              que e tudo que sobrevive nesse tamanho.
  180/192/512 -> a MARCA INTEIRA em knockout, sobre navy. Aqui ha altura para
              a moldura, a base e o entalhe do trackpad existirem.

O campo e sempre NAVY CHAPADO, e nao alfa: o iOS ignora transparencia no
atalho e compoe sobre preto, o que engrossaria a moldura do notebook.

Uso: python ferramentas/build_icones.py   (depois de build_marca.py)
"""
import json
import os
import sys
from collections import deque

from PIL import Image

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from build_marca import quantizar, alcancavel, OURO, FONTE  # noqa: E402

RAIZ = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SITE = os.path.join(RAIZ, 'site')
BRAND = os.path.join(SITE, 'brand')

NAVY = (0, 53, 102)

# As larguras nao sao gosto. Cada uma tem um consumidor nomeado:
#   16/32/48 -> dentro do .ico (aba, favoritos, e o que o Google mostra)
#   180 ..... -> apple-touch-icon, o tamanho que o iOS pede desde o iPhone 6+
#   192/512 . -> manifesto do Android; 512 e o minimo para o splash
PEQUENOS = [16, 32, 48]
GRANDES = [180, 192, 512]

# Respiro dentro do quadrado. O icone pequeno usa quase tudo porque nao ha o
# que sacrificar; o grande respira porque a moldura branca do knockout ja
# funciona como margem optica.
PAD_PEQUENO = 0.04
PAD_GRANDE = 0.10


def maior_regiao_dourada(w, h, rgb, alfa):
    """A TELA. Achada como o maior componente conexo de pixel dourado -- nao
    por coordenada escrita a mao, para o recorte sobreviver a qualquer ajuste
    futuro da arte."""
    e = [alfa[i] >= 8 and rgb[i] in OURO for i in range(w * h)]
    visto = bytearray(w * h)
    melhor = None
    for s in range(w * h):
        if not e[s] or visto[s]:
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
                if ok and e[j] and not visto[j]:
                    visto[j] = 1
                    q.append(j)
        if melhor is None or n > melhor[0]:
            melhor = (n, x0, y0, x1, y1)
    return melhor


def quadrado(peca, t, pad):
    """Encaixa `peca` centrada num quadrado navy de t px, preservando a
    proporcao. LANCZOS na reducao."""
    ch = Image.new('RGB', (t, t), NAVY)
    alvo = int(round(t * (1 - 2 * pad)))
    w, h = peca.size
    if w >= h:
        nw = alvo
        nh = max(1, int(round(alvo * h / float(w))))
    else:
        nh = alvo
        nw = max(1, int(round(alvo * w / float(h))))
    r = peca.resize((nw, nh), Image.LANCZOS)
    ch.paste(r, ((t - nw) // 2, (t - nh) // 2), r)
    return ch


def main():
    marca = os.path.join(RAIZ, 'referencia', 'marca', 'logo-marca-branco-288.png')
    if not os.path.exists(marca):
        raise SystemExit('rode ferramentas/build_marca.py primeiro: falta ' + marca)
    if not os.path.isdir(BRAND):
        os.makedirs(BRAND)

    # --- a tela, recortada da arte em resolucao plena e ja em knockout, para
    #     o glifo continuar navy sobre o dourado (branco sobre #FDC500 daria
    #     1,6:1) e o que porventura vazar da tela sair branco, nao navy.
    from build_marca import montar
    w, h, rgb, alfa = quantizar(Image.open(FONTE))
    ko = alcancavel(w, h, rgb, alfa)
    cheia = montar(w, h, rgb, alfa, ko)
    n, x0, y0, x1, y1 = maior_regiao_dourada(w, h, rgb, alfa)
    tela = cheia.crop((x0, y0, x1 + 1, y1 + 1))
    print('tela: maior regiao dourada conexa, %d px, %dx%d (%.3f:1)'
          % (n, tela.size[0], tela.size[1], tela.size[0] / float(tela.size[1])))

    inteira = Image.open(marca).convert('RGBA')
    print('marca: %dx%d (%.3f:1)'
          % (inteira.size[0], inteira.size[1], inteira.size[0] / float(inteira.size[1])))

    rel = []

    for t in GRANDES:
        nome = 'apple-touch-icon.png' if t == 180 else 'icon-%d.png' % t
        p = os.path.join(BRAND, nome)
        quadrado(inteira, t, PAD_GRANDE).save(p, optimize=True)
        rel.append((os.path.relpath(p, RAIZ), os.path.getsize(p)))

    # O .ico vai na RAIZ do site, nao em brand/: o pedido automatico do
    # navegador e para `/favicon.ico` e nao passa por link nenhum do HTML.
    quadros = [quadrado(tela, t, PAD_PEQUENO) for t in PEQUENOS]
    p = os.path.join(SITE, 'favicon.ico')
    quadros[-1].save(p, format='ICO', sizes=[(t, t) for t in PEQUENOS])
    rel.append((os.path.relpath(p, RAIZ), os.path.getsize(p)))

    # O SVG redesenhado sai. Se ficasse no diretorio, o proximo deploy o
    # publicaria e a marca errada voltaria pela porta dos fundos.
    svg = os.path.join(BRAND, 'favicon.svg')
    if os.path.exists(svg):
        os.remove(svg)
        print('removido: brand/favicon.svg (redesenho; a fonte agora e a arte real)')
    icone_svg = os.path.join(BRAND, 'logo-icone.svg')
    if os.path.exists(icone_svg):
        os.remove(icone_svg)
        print('removido: brand/logo-icone.svg (idem)')

    manifesto = {
        'name': 'i3 Automations & Controls',
        'short_name': 'i3Automations',
        'start_url': '.',
        'display': 'browser',
        # #001D3D morreu com a alternancia suavizada (design.md §1.4 regra 4).
        'background_color': '#0D4477',
        'theme_color': '#003566',
        'icons': [
            {'src': 'brand/icon-192.png', 'sizes': '192x192', 'type': 'image/png'},
            {'src': 'brand/icon-512.png', 'sizes': '512x512', 'type': 'image/png'},
        ],
    }
    p = os.path.join(SITE, 'site.webmanifest')
    with open(p, 'w', encoding='utf-8') as f:
        json.dump(manifesto, f, indent=2)
    rel.append((os.path.relpath(p, RAIZ), os.path.getsize(p)))

    print('== icones ==')
    for nome, tam in rel:
        print('   %-34s %6.1f KB' % (nome, tam / 1024))
    print('   TOTAL %.1f KB' % (sum(t for _, t in rel) / 1024))


if __name__ == '__main__':
    main()
