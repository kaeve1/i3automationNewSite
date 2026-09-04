# -*- coding: utf-8 -*-
"""Converte o recorte fotografico em TRACO de desenho tecnico.

Metodo: XDoG (extended difference-of-Gaussians). Um Sobel cru devolve ruido
granulado; a XDoG devolve traco continuo, com espessura coerente, que le como
tinta e nao como filtro. O resultado sai como MASCARA ALFA (linhas brancas em
fundo transparente) — assim um unico arquivo serve tema claro e escuro: a cor
vem do CSS (mask-image sobre bloco solido) ou de um uniform no shader.

Uso: python ferramentas/linha.py
"""
import numpy as np
from PIL import Image, ImageFilter

# --- parametros medidos no proprio braco, nao herdados de tutorial ---
SIGMA = 0.9      # gaussiana fina
K     = 1.7      # razao entre as duas gaussianas
TAU   = 0.985    # quanto da gaussiana larga e subtraida
EPS   = 0.0      # limiar do detector
PHI   = 34.0     # dureza da transicao (maior = traco mais seco)
PISO  = 0.06     # abaixo disto e poeira de sensor, nao aresta
TETO  = 0.34     # medido: p99 da saida crua — acima disto ja e tinta cheia
GAMA  = 0.72     # < 1 engrossa o meio-tom do traco


def borra(a, sigma):
    return np.asarray(
        Image.fromarray((np.clip(a, 0, 1) * 255).astype(np.uint8))
        .filter(ImageFilter.GaussianBlur(sigma))
    ).astype(np.float32) / 255


def xdog(cinza, sigma=SIGMA, k=K, tau=TAU, eps=EPS, phi=PHI):
    d = borra(cinza, sigma) - tau * borra(cinza, sigma * k)
    tinta = np.where(d >= eps, 0.0, -np.tanh(phi * (d - eps)))
    tinta = np.clip(tinta, 0, 1)
    # A XDoG crua entrega valores esmagados na base (medido: p99 = .35), o que
    # renderiza cinza-claro em vez de tinta. A curva reabre a faixa util.
    return np.clip((tinta - PISO) / (TETO - PISO), 0, 1) ** GAMA


def contorno(alfa, largura=2):
    """Silhueta: dilata menos erode. E a linha mais grossa do desenho."""
    im = Image.fromarray((alfa * 255).astype(np.uint8))
    d = np.asarray(im.filter(ImageFilter.MaxFilter(largura * 2 + 1))).astype(np.float32) / 255
    e = np.asarray(im.filter(ImageFilter.MinFilter(largura * 2 + 1))).astype(np.float32) / 255
    return np.clip(d - e, 0, 1)


def desenhar(rgba, escala=2, forca_interna=0.88):
    """rgba: PIL RGBA ja recortado. Devolve mascara alfa L do traco."""
    if escala != 1:
        rgba = rgba.resize((rgba.width * escala, rgba.height * escala), Image.LANCZOS)
    a = np.asarray(rgba).astype(np.float32) / 255
    alfa = a[..., 3]

    # Luminancia perceptual; fora do recorte usa branco para o detector nao
    # inventar aresta na borda do canvas.
    lum = 0.2126 * a[..., 0] + 0.7152 * a[..., 1] + 0.0722 * a[..., 2]
    lum = np.where(alfa > .5, lum, 1.0)

    interno = xdog(lum) * (alfa > .5) * forca_interna
    silhueta = contorno(alfa, largura=escala)          # borda externa, cheia
    linha = np.clip(np.maximum(interno, silhueta), 0, 1)

    # tira a poeira de 1px que a XDoG deixa em superficie lisa
    im = Image.fromarray((linha * 255).astype(np.uint8))
    limpo = np.asarray(im.filter(ImageFilter.MedianFilter(3))).astype(np.float32) / 255
    linha = np.maximum(limpo, silhueta)
    return Image.fromarray((np.clip(linha, 0, 1) * 255).astype(np.uint8), 'L')


if __name__ == '__main__':
    S = 'C:/Users/kegit/AppData/Local/Temp/claude/C--Users-kegit-I3Automations/1ff73b39-2722-4fb2-82c1-a7071f805473/scratchpad'
    src = Image.open(S + '/recorte.png').crop(Image.open(S + '/recorte.png').getbbox())
    m = desenhar(src, escala=2)
    m.save(S + '/linha-mascara.png')
    # prova: linhas navy sobre branco
    prova = Image.new('RGB', m.size, '#FFFFFF')
    prova.paste(Image.new('RGB', m.size, '#003566'), (0, 0), m)
    prova.save(S + '/linha-prova.png')
    print('traco:', m.size, '| cobertura %.1f%%' % ((np.asarray(m) > 40).mean() * 100))
