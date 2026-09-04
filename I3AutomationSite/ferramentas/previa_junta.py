# -*- coding: utf-8 -*-
"""Desenha a JUNTA entre duas secoes FORA do navegador.

Refaz a aritmetica do CSS -- a linha de eixo ISO 128 (traco 22, vao 5, ponto 2,
vao 5), a borda do container calculada por max(), o rotulo em mono no registro
da linha de cota -- e responde as tres perguntas que a peca faz:

  1. o rotulo pousa EXATAMENTE na borda direita do container, em qualquer
     largura de janela? A conta do CSS e
     max(--pad-lateral, 50% - --container/2 + --pad-lateral).
  2. a linha de eixo LE como traco-ponto a 1 px, ou vira pontilhado?
  3. o tracado por clip-path mantem o padrao no TAMANHO VERDADEIRO durante o
     percurso -- que e a razao de a peca nao poder usar scaleX?

A pergunta 3 e o motivo de esta ferramenta existir. Ela desenha a mesma junta
pelas duas tecnicas em varios instantes e a diferenca aparece: por clip-path o
traco mede 22 px desde o primeiro quadro; por scaleX ele mede 1,8 px no comeco
e so chega a 22 no ultimo. Nao e a mesma linha entrando devagar -- e outro
padrao, que so vira o certo no fim.

Uso: python ferramentas/previa_junta.py
"""
import os
import re

from PIL import Image, ImageDraw, ImageFont

RAIZ = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

# --- tokens, os mesmos de tokens.css --------------------------------------
CONTAINER = 1376

# (fundo, --tinta-2, --filete-forte ACHATADO sobre o fundo)
# filete-forte e rgba(0,0,0,.24) no claro e rgba(255,255,255,.30) no escuro;
# aqui ele entra ja composto, que e o que a tela mostra.
SUP = {
    'papel':     ((255, 255, 255), (64, 96, 127),   (194, 194, 194)),
    'off-white': ((242, 245, 248), (64, 96, 127),   (184, 186, 189)),
    'navy':      ((0, 29, 61),     (143, 180, 220), (77, 97, 118)),
}

def _receita():
    """Le a geometria da linha de eixo DO PROPRIO style.css.

    Guardar copia dos numeros aqui seria repetir o erro que memoria.md ja
    registrou na previa do braco: em meia hora a copia divergiu do original e
    a previa passou a confirmar uma peca que nao existe mais. Previa que
    diverge do original nao e previa, e ficcao.
    """
    css = os.path.join(RAIZ, 'fonte', 'css', 'style.css')
    with open(css, encoding='utf-8') as fh:
        s = fh.read()
    i = s.index('.junta::after')
    trecho = s[i:i + 2000]
    m = re.search(
        r'repeating-linear-gradient\(90deg,\s*'
        r'var\(--filete-forte\)\s*0\s*(\d+)px,\s*'
        r'transparent\s*\d+px\s*(\d+)px,\s*'
        r'var\(--filete-forte\)\s*\d+px\s*(\d+)px,\s*'
        r'transparent\s*\d+px\s*(\d+)px\)', trecho)
    if not m:
        raise SystemExit('previa_junta: nao achei a linha de eixo em style.css')
    a, b, c, d = (int(g) for g in m.groups())
    return a, b - a, c - b, d - c


# linha de eixo ISO 128 (traco-ponto), lida de style.css
TRACO, VAO_A, PONTO, VAO_B = _receita()
PERIODO = TRACO + VAO_A + PONTO + VAO_B

INSTANTES = [0.08, 0.18, 0.35, 0.60, 1.00]


def fonte(tam):
    for c in (r'C:\Windows\Fonts\consola.ttf', r'C:\Windows\Fonts\cour.ttf'):
        if os.path.exists(c):
            return ImageFont.truetype(c, tam)
    return ImageFont.load_default()


def margem(largura, pad):
    """A borda do container, exatamente como o CSS a calcula."""
    return max(pad, largura / 2.0 - CONTAINER / 2.0 + pad)


def cadeia(d, y, x0, x1, cor):
    """A linha de eixo, ancorada em x=0 da secao -- como background-position."""
    x = (int(x0) // PERIODO) * PERIODO
    while x < x1:
        for ini, fim in ((x, x + TRACO),
                         (x + TRACO + VAO_A, x + TRACO + VAO_A + PONTO)):
            a, b = max(ini, x0), min(fim, x1)
            if b - a >= 1:
                d.rectangle([a, y, b - 1, y], fill=cor)
        x += PERIODO


def escrever(d, x, y, txt, f, cor):
    """letter-spacing .14em na mao, e devolve a largura ocupada."""
    ini = x
    for ch in txt:
        d.text((x, y), ch, font=f, fill=cor)
        x += d.textbbox((0, 0), ch, font=f)[2] + 0.14 * 12
    return x - ini


def largura_rotulo(d, txt, f):
    return sum(d.textbbox((0, 0), c, font=f)[2] + 0.14 * 12 for c in txt)


def junta(d, y, largura, pad, sup, rotulo, p=1.0, inversa=False, tecnica='clip'):
    """Uma junta desenhada no instante p do tracado (0..1)."""
    _, tinta2, filete = SUP[sup]
    m = margem(largura, pad)

    if tecnica == 'clip':
        # clip-path: inset(0 (1-p)*100% 0 0) -- padrao no tamanho real
        x0, x1 = ((largura * (1 - p), largura) if inversa else (0, largura * p))
        cadeia(d, y, x0, x1, filete)
    else:
        # scaleX(p) -- o PADRAO encolhe junto, que e o defeito
        origem = largura if inversa else 0
        x = 0
        while x < largura:
            for ini, fim in ((x, x + TRACO),
                             (x + TRACO + VAO_A, x + TRACO + VAO_A + PONTO)):
                a = origem + (ini - origem) * p
                b = origem + (fim - origem) * p
                a, b = min(a, b), max(a, b)
                if b - a >= 1:
                    d.rectangle([a, y, b - 1, y], fill=filete)
            x += PERIODO

    # O rotulo mora na ponta em que o traco TERMINA, entao o mesmo tracado o
    # plota por ultimo: linha de construcao primeiro, anotacao depois.
    if rotulo:
        f = fonte(12)
        lt = largura_rotulo(d, rotulo, f)
        tx = m if inversa else largura - m - lt
        visivel = ((largura * (1 - p) <= tx) if inversa
                   else (tx + lt <= largura * p))
        if visivel:
            escrever(d, tx, y + 14, rotulo, f, tinta2)
    return m


def folha(nome, largura, pad, par, rotulo, inversa=False):
    """Duas secoes empilhadas com a junta entre elas, no estado final."""
    alto = 240
    de_cima, de_baixo = par
    im = Image.new('RGB', (largura, alto), SUP[de_baixo][0])
    d = ImageDraw.Draw(im)
    d.rectangle([0, 0, largura, 99], fill=SUP[de_cima][0])
    m = junta(d, 100, largura, pad, de_baixo, rotulo, 1.0, inversa)

    # a borda do container, para conferir onde o rotulo pousou
    for x in (m, largura - m):
        d.line([x, 0, x, alto], fill=(226, 60, 60))
    f = fonte(11)
    d.text((8, alto - 20), '%s   %d px   margem %.0f   %s'
           % (nome, largura, m, 'inversa' if inversa else 'normal'),
           font=f, fill=SUP[de_baixo][1])
    return im


CASOS = [
    ('1920 desktop', 1920, 48, ('papel', 'off-white'), 'SHEET 03 OF 07', False),
    ('1440 desktop', 1440, 48, ('off-white', 'navy'),  'SHEET 07 OF 07', False),
    ('1280 medio',   1280, 48, ('papel', 'off-white'), 'SHEET 04 OF 06', False),
    ('1000 tablet',  1000, 32, ('navy', 'papel'),      'SHEET 02 OF 05', True),
    ('600 celular',   600, 20, ('papel', 'navy'),      'SHEET 03 OF 04', False),
]


def main():
    # --- 1. alinhamento do rotulo em cinco janelas ------------------------
    fls = [folha(n, l, p, par, r, i) for n, l, p, par, r, i in CASOS]
    L, H = max(f.width for f in fls), sum(f.height for f in fls)
    tela = Image.new('RGB', (L, H), (18, 18, 18))
    y = 0
    for f in fls:
        tela.paste(f, (0, y))
        y += f.height
    p1 = os.path.join(RAIZ, 'ferramentas', '_junta_alinhamento.png')
    tela.save(p1)

    # --- 2. clip-path CONTRA scaleX, no meio do tracado -------------------
    larg, lin = 1440, 64
    tela2 = Image.new('RGB', (larg, lin * len(INSTANTES) * 2 + 56), (255, 255, 255))
    d2 = ImageDraw.Draw(tela2)
    f12 = fonte(12)
    y = 20
    for tec, nome in (('clip', 'clip-path   o que a peca usa'),
                      ('scale', 'scaleX      o que ela NAO pode usar')):
        for p in INSTANTES:
            d2.text((12, y - 14), '%s      p=%.2f' % (nome, p),
                    font=f12, fill=(120, 120, 120))
            junta(d2, y + 12, larg, 48, 'papel', '', p, False, tec)
            y += lin
        y += 16
    p2 = os.path.join(RAIZ, 'ferramentas', '_junta_tecnica.png')
    tela2.save(p2)

    # --- o que a conta diz ------------------------------------------------
    print('margem do container -- formula do CSS contra a borda real:')
    ok = True
    for nome, larg, pad, _, _, _ in CASOS:
        m = margem(larg, pad)
        real = (larg - min(larg, CONTAINER)) / 2.0 + pad
        bate = abs(m - real) < .01
        ok = ok and bate
        print('  %-14s %4d px   formula %6.1f   container %6.1f   %s'
              % (nome, larg, m, real, 'ok' if bate else 'DIVERGE'))

    print()
    print('linha de eixo: periodo %d px  (traco %d, vao %d, ponto %d, vao %d)'
          % (PERIODO, TRACO, VAO_A, PONTO, VAO_B))
    print()
    print('comprimento do TRACO no instante p:')
    for p in INSTANTES:
        print('  p=%.2f    clip-path %5.1f px    scaleX %5.1f px    %s'
              % (p, TRACO, TRACO * p,
                 'igual' if abs(TRACO - TRACO * p) < .01 else
                 'scaleX desenha OUTRO padrao'))
    print()
    print('alinhamento: %s' % ('todos batem' if ok else 'HA DIVERGENCIA'))
    print(p1)
    print(p2)


if __name__ == '__main__':
    main()
