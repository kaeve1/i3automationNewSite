# -*- coding: utf-8 -*-
"""A SECAO DUPLA: uma fotografia so atravessando duas secoes escuras.

Duas secoes escuras seguidas compartilham uma superficie mas carregavam DUAS
fotografias diferentes -- a de cima terminava e outra comecava no meio de um
bloco que se le como um so. Aqui elas passam a dividir UMA imagem.

O que esta ferramenta responde:

  1. a fonte e reduzida na caixa? (regra que a secao "Since 2000" custou)
  2. onde fica a FAIXA LIVRE -- a banda vertical sem texto nenhum, entre o fim
     do texto de cima e o comeco do de baixo? E la, e so la, que a fotografia
     pode respirar; o resto e veu.
  3. com o veu composto sobre a foto de verdade, cada cor de texto passa AA,
     nos dois temas?

A faixa livre NAO e a mesma nas duas paginas -- home e services tem alturas
diferentes de secao --, entao o veu abre na INTERSECCAO das duas.

Uso: python ferramentas/previa_dupla.py
"""
import os
import sys

import numpy as np
from PIL import Image, ImageDraw, ImageFont

RAIZ = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from contraste import razao

LARG = 1440

# --- geometria das duas paginas, pela aritmetica do CSS a 1440 -------------
# (nome, altura da secao de cima, altura do CTA, foto)
PAGINAS = [
    ('home',     373, 660, 'dupla/clp-2560.jpg'),
    ('services', 510, 660, 'dupla/comando-2560.jpg'),
]

# fim do texto de cima e comeco do texto de baixo, em px dentro de cada secao
FIM_TEXTO_CIMA = {'home': 277, 'services': 350}
INICIO_TEXTO_BAIXO = 160          # --sec-y do CTA

# --- o veu proposto -------------------------------------------------------
# paradas em fracao da altura do conjunto; alfa por tema
# O VEU TEM DE ESTAR FECHADO ANTES DE O TEXTO DE BAIXO COMECAR. A primeira
# versao abria ate 50% e so voltava ao cheio em 58% -- e o eyebrow do CTA nasce
# em 52% (home), ou seja, DENTRO da rampa de fechamento, sob um veu ainda
# aberto. Fecha em 48%, com folga para as duas paginas.
PARADAS = (0.00, 0.09, 0.30, 0.34, 0.42, 0.48, 0.94, 1.00)
def _achatar(fg, a, bg):
    """`--sobre-3-2` e rgba: a cor que o olho ve e ela JA composta sobre a
    superficie. Aproximar por um cinza chapado (o erro da primeira versao)
    devolve um contraste que nao existe na tela."""
    return tuple(int(round(fg[i] * a + bg[i] * (1 - a))) for i in range(3))


# O VEU E MAIS FECHADO QUE O DE `.secao--foto`, e a comparacao engana. La sao
# DOIS gradientes sobrepostos -- vertical .55 e horizontal .35 -- que compoem
# para 1-(1-.55)(1-.35) = .71 no ponto mais aberto, nao .55. Aqui e um
# gradiente so, entao o numero declarado E o efetivo, e tem de valer ~.78.
#
# Resolvido por busca sobre as fotos de verdade: abaixo de .76 (claro) e .88
# (escuro) o `.corpo` cai de 4,5:1. O texto critico e sempre ele -- nao o
# branco da citacao, que e grande e tem piso 3:1.
TEMAS = {
    'claro': {
        'veu': (0, 29, 61), 'sup3': (0, 29, 61),
        'meio': .78, 'aberto': .50,
        'textos': [('branco (citacao, h2)', (255, 255, 255), 'grande'),
                   ('dourado (eyebrow)', (253, 197, 0), 'pequeno'),
                   ('corpo --sobre-3-2', _achatar((255, 255, 255), .72, (0, 29, 61)), 'pequeno'),
                   ('rotulo --navy-luz', (185, 210, 234), 'pequeno')],
        'pior': 'claro',           # texto claro -> perigo e o ponto mais CLARO
    },
    'escuro': {
        'veu': (0, 53, 102), 'sup3': (0, 53, 102),
        'meio': .88, 'aberto': .62,
        'textos': [('branco (citacao, h2)', (232, 237, 243), 'grande'),
                   ('dourado (eyebrow)', (253, 197, 0), 'pequeno'),
                   ('corpo --sobre-3-2', _achatar((232, 237, 243), .74, (0, 53, 102)), 'pequeno'),
                   ('rotulo --navy-luz', (185, 210, 234), 'pequeno')],
        'pior': 'claro',
    },
}


def alfas(tema):
    m, a = TEMAS[tema]['meio'], TEMAS[tema]['aberto']
    return (1.0, m, m, a, a, m, m, 1.0)


def cobrir(rel, larg, alt):
    im = Image.open(os.path.join(RAIZ, 'site', 'img', rel)).convert('RGB')
    esc = max(larg / im.width, alt / im.height)
    nw, nh = int(round(im.width * esc)), int(round(im.height * esc))
    g = im.resize((nw, nh), Image.LANCZOS)
    x, y = (nw - larg) // 2, int((nh - alt) * 0.42)
    return g.crop((x, y, x + larg, y + alt)), esc, (im.width, im.height)


def rampa(t, paradas, valores):
    if t <= paradas[0]:
        return valores[0]
    for i in range(1, len(paradas)):
        if t <= paradas[i]:
            f = (t - paradas[i - 1]) / max(1e-6, paradas[i] - paradas[i - 1])
            return valores[i - 1] + f * (valores[i] - valores[i - 1])
    return valores[-1]


def compor(foto, tema):
    px = np.asarray(foto, np.float32)
    h, w, _ = px.shape
    veu = np.array(TEMAS[tema]['veu'], np.float32)
    a = np.array([rampa(y / float(h), PARADAS, alfas(tema))
                  for y in range(h)], np.float32)
    return px * (1 - a[:, None, None]) + veu[None, None, :] * a[:, None, None]


def media_local(a, k=12):
    h, w, _ = a.shape
    h2, w2 = (h // k) * k, (w // k) * k
    b = a[:h2, :w2].reshape(h2 // k, k, w2 // k, k, 3).mean(axis=(1, 3))
    return b


def main():
    tiras = {}
    print('1. FAIXA LIVRE — onde a fotografia pode respirar')
    livres = []
    for nome, alt_cima, alt_cta, _ in PAGINAS:
        total = alt_cima + alt_cta
        ini = FIM_TEXTO_CIMA[nome] / float(total)
        fim = (alt_cima + INICIO_TEXTO_BAIXO) / float(total)
        livres.append((ini, fim))
        print('   %-9s conjunto %d px   livre de %.0f%% a %.0f%%'
              % (nome, total, ini * 100, fim * 100))
    ini = max(l[0] for l in livres)
    fim = min(l[1] for l in livres)
    print('   intersecao das duas: %.0f%% a %.0f%%  ->  o véu abre em %.0f–%.0f%%'
          % (ini * 100, fim * 100, PARADAS[3] * 100, PARADAS[4] * 100))
    ok_faixa = PARADAS[3] >= ini - .01 and PARADAS[4] <= fim + .01
    print('   as paradas %.0f–%.0f%% caem dentro da intersecao: %s'
          % (PARADAS[3] * 100, PARADAS[4] * 100,
             'sim' if ok_faixa else 'NAO — rever'))
    print()

    print('2. PROPORCAO E CONTRASTE')
    reprovou = False
    for nome, alt_cima, alt_cta, foto in PAGINAS:
        total = alt_cima + alt_cta
        img, esc, nativo = cobrir(foto, LARG, total)
        print('   %s — %s' % (nome, foto.split('/')[-1]))
        print('      fonte %dx%d -> caixa %dx%d   escala %.3fx  %s'
              % (nativo[0], nativo[1], LARG, total, esc,
                 'REDUZ' if esc < 1 else 'AMPLIA — REPROVA'))
        # AMOSTRAR SO ONDE HA TEXTO. A faixa livre e, de proposito, a parte
        # mais aberta do veu -- medir o pior ponto do conjunto INTEIRO faz o
        # pior ponto cair justamente ali, num lugar onde nenhuma letra existe,
        # e reprova uma peca que esta certa.
        faixas_txt = [(0, FIM_TEXTO_CIMA[nome]),
                      (alt_cima + INICIO_TEXTO_BAIXO - 10, total)]
        for tema in ('claro', 'escuro'):
            comp = compor(img, tema)
            bl = media_local(comp)
            k = 12
            recortes = [bl[max(0, a // k):min(bl.shape[0], b // k)]
                        for a, b in faixas_txt]
            bl = np.concatenate([r.reshape(-1, 3) for r in recortes if r.size])
            lum = bl @ np.array([.2126, .7152, .0722], np.float32)
            fundo = bl[int(np.argmax(lum))]
            fh = '#%02X%02X%02X' % tuple(int(round(c)) for c in fundo)
            linha = '      %-7s pior fundo %s  ' % (tema, fh)
            for rot, tinta, tam in TEMAS[tema]['textos']:
                r = razao('#%02X%02X%02X' % tinta, fh)
                piso = 3.0 if tam == 'grande' else 4.5
                if r < piso:
                    reprovou = True
                linha += ' %s %.2f%s' % (rot.split()[0], r,
                                         '' if r >= piso else '!REPROVA')
            print(linha)
            tiras.setdefault(nome, {})[tema] = comp
        print()

    print('   veredito: %s' % ('HA REPROVACAO' if reprovou else 'tudo passa AA'))
    print()
    render(tiras)


def render(tiras):
    def fonte(t):
        c = r'C:\Windows\Fonts\segoeuil.ttf'
        return (ImageFont.truetype(c, t) if os.path.exists(c)
                else ImageFont.load_default())

    painel = []
    for nome, alt_cima, alt_cta, _ in PAGINAS:
        for tema in ('claro', 'escuro'):
            comp = tiras[nome][tema]
            im = Image.fromarray(np.clip(comp, 0, 255).astype(np.uint8))
            d = ImageDraw.Draw(im)
            m = max(48, LARG / 2.0 - 1376 / 2.0 + 48)
            t = TEMAS[tema]['textos']
            branco, dourado, corpo = t[0][1], t[1][1], t[2][1]

            if nome == 'home':
                cx = LARG / 2
                d.text((cx - 110, 96), 'WHY THE CALL IS WORTH MAKING',
                       font=fonte(15), fill=dourado)
                for k, ln in enumerate(['Senior control experts know',
                                        'things they do not teach',
                                        'in school.']):
                    w = d.textbbox((0, 0), ln, font=fonte(40))[2]
                    d.text((cx - w / 2, 132 + k * 46), ln, font=fonte(40), fill=branco)
            else:
                d.text((m, 160), 'YOUR DESIGN OR OURS', font=fonte(15), fill=dourado)
                for k, ln in enumerate(['Two ways in,', 'one standard out']):
                    d.text((m, 192 + k * 40), ln, font=fonte(34), fill=branco)

            y = alt_cima + 160
            d.text((m, y), 'TALK TO AN ENGINEER', font=fonte(15), fill=dourado)
            for k, ln in enumerate(['Tell us what the', 'process has to do']):
                d.text((m, y + 30 + k * 40), ln, font=fonte(34), fill=branco)
            xd = m + 4 * ((LARG - 2 * m) / 12.0)
            for k, ln in enumerate(['Send the scope, the P&ID, or just the problem.',
                                    'You will get an engineer on the reply.']):
                d.text((xd, y + 6 + k * 24), ln, font=fonte(16), fill=corpo)
            for k, rot in enumerate(['Sales & Services', 'Support', 'E-mail',
                                     'Where we are']):
                x = m + k * ((LARG - 2 * m) / 4.0)
                d.text((x, y + 300), rot, font=fonte(15), fill=corpo)
                d.text((x, y + 324), '+1 (000) 000-0000', font=fonte(20), fill=branco)

            d.line([0, alt_cima, LARG, alt_cima], fill=(226, 60, 60))
            d.text((10, im.height - 22), '%s / tema %s  (linha vermelha = emenda '
                   'das duas secoes; a FOTO nao se interrompe nela)'
                   % (nome, tema), font=fonte(13), fill=(200, 200, 200))
            painel.append(im)

    L = LARG * 2 + 8
    H = max(painel[0].height, painel[2].height) * 2 + 8
    fora = Image.new('RGB', (L, H), (20, 20, 20))
    fora.paste(painel[0], (0, 0)); fora.paste(painel[1], (LARG + 8, 0))
    y2 = painel[0].height + 8
    fora.paste(painel[2], (0, y2)); fora.paste(painel[3], (LARG + 8, y2))
    fora = fora.resize((fora.width // 2, fora.height // 2), Image.LANCZOS)
    cam = os.path.join(RAIZ, 'ferramentas', '_dupla.png')
    fora.save(cam)
    print(cam)


if __name__ == '__main__':
    main()
