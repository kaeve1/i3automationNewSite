# -*- coding: utf-8 -*-
"""
Par EPSON: a foto e o desenho da MESMA peca, registrados um sobre o outro.

Por que existe:
  A foto e um braco BRANCO sobre fundo BRANCO em cima de um pedestal BRANCO.
  Nao ha limiar de cor que separe a peca do fundo -- o discriminante nao esta
  na cor, esta na FORMA. E a forma ja existe pronta: o desenho de linha e a
  mesma peca, na mesma pose. Entao a silhueta sai do DESENHO e vira a matte
  da FOTO, depois de registrar os dois por busca de escala + deslocamento.

  Isso tambem resolve o pedestal de graca: o desenho nao tem pedestal, logo a
  intersecao com a silhueta do desenho apaga a caixa branca do fundo sem
  precisar de corte manual em y.
"""
import sys

import numpy as np
from PIL import Image, ImageFilter

FOTO = "referencia/Gemini_Generated_Image_rboreirboreirbor.jpg"
DESENHO = "referencia/ChatGPT Image 18_08_2026, 22_29_53.png"


def fora(mascara_solida):
    """Inundacao a partir da borda: devolve o que esta CONECTADO ao lado de fora.

    BFS em fila sobre os pixels 'vazios'. O complemento disso e a silhueta com
    os buracos internos ja preenchidos -- que e exatamente o que se quer, porque
    o miolo branco do braco nao pode virar transparencia.
    """
    h, w = mascara_solida.shape
    visto = np.zeros((h, w), bool)
    fila = []
    for x in range(w):
        for y in (0, h - 1):
            if not mascara_solida[y, x] and not visto[y, x]:
                visto[y, x] = True; fila.append((y, x))
    for y in range(h):
        for x in (0, w - 1):
            if not mascara_solida[y, x] and not visto[y, x]:
                visto[y, x] = True; fila.append((y, x))
    i = 0
    while i < len(fila):
        y, x = fila[i]; i += 1
        for dy, dx in ((1, 0), (-1, 0), (0, 1), (0, -1)):
            ny, nx = y + dy, x + dx
            if 0 <= ny < h and 0 <= nx < w and not visto[ny, nx] and not mascara_solida[ny, nx]:
                visto[ny, nx] = True; fila.append((ny, nx))
    return visto


def silhueta_desenho():
    im = Image.open(DESENHO).convert("L")
    a = np.asarray(im).astype(np.float32) / 255.0
    # A linha e ocre sobre papel quase branco. 0.93 pega a linha inteira,
    # inclusive o traco fino da grade de detalhe, sem pegar o papel.
    linha = a < 0.93
    # Fecha vaos de 1-2 px do traco antes de inundar, senao a inundacao
    # escapa por dentro pelas frestas entre segmentos.
    lin = Image.fromarray((linha * 255).astype(np.uint8))
    lin = lin.filter(ImageFilter.MaxFilter(5))
    linha = np.asarray(lin) > 127
    sil = ~fora(linha)
    return sil, a


def silhueta_foto():
    im = Image.open(FOTO).convert("RGB")
    a = np.asarray(im).astype(np.float32) / 255.0
    lum = a.mean(2)
    # O fundo e branco PURO (1.0) e a peca e branca SOMBREADA. 0.985 e o
    # limiar; nao ha dilatacao aqui de proposito -- dilatar a silhueta da foto
    # foi o que trouxe a franja branca de ringing do JPEG junto com a aresta.
    corpo = lum < 0.985
    return ~fora(corpo), a


def caixa(m):
    ys, xs = np.nonzero(m)
    return xs.min(), ys.min(), xs.max() + 1, ys.max() + 1


if __name__ == "__main__":
    sd, _ = silhueta_desenho()
    sf, _ = silhueta_foto()
    print("desenho", sd.shape, "px", int(sd.sum()), "caixa", caixa(sd))
    print("foto   ", sf.shape, "px", int(sf.sum()), "caixa", caixa(sf))
    # as silhuetas so viram arquivo com --ver: sao diagnostico de registro,
    # nao entrega, e sujavam ferramentas/ a cada execucao
    if "--ver" in sys.argv:
        Image.fromarray((sd * 255).astype(np.uint8)).save("ferramentas/_sil_desenho.png")
        Image.fromarray((sf * 255).astype(np.uint8)).save("ferramentas/_sil_foto.png")

# ---------------------------------------------------------------- registro
def transformar(sd, s, dx, dy, forma):
    """Rasteriza a silhueta do desenho na grade da foto: escala s, desloca (dx,dy)."""
    h, w = forma
    d = Image.fromarray((sd * 255).astype(np.uint8))
    nw, nh = max(1, int(round(d.width * s))), max(1, int(round(d.height * s)))
    d = d.resize((nw, nh), Image.BILINEAR)
    tela = Image.new("L", (w, h), 0)
    tela.paste(d, (int(round(dx)), int(round(dy))))
    return np.asarray(tela) > 110


def registrar(sd, sf, teto_foto=940, verboso=True):
    """Escala + deslocamento que assentam o DESENHO sobre a FOTO.

    Modelo: (x, y)_foto = (X * s + dx, Y * s + dy). So similaridade -- as duas
    imagens vem da mesma origem, entao nao ha rotacao nem cisalhamento a achar.

    O score e IoU calculado SO acima de `teto_foto`. Medido: o pedestal branco
    entra na silhueta da foto a partir de y~950, quando a largura da linha salta
    de 317 para 721 px. Sem essa restricao o otimo global seria encolher o
    desenho para dentro do bloco do pedestal, que e a maior mancha solida.

    O candidato e RASTERIZADO na grade da foto antes de comparar. Amostrar
    ponto a ponto -- que foi a primeira versao -- conta o mesmo pixel da foto
    varias vezes quando s < 1, e devolve IoU acima de 1. Interseccao tem de ser
    contada sobre mascaras, nao sobre pares de indices.
    """
    forma = sf.shape
    alvo = sf[:teto_foto]

    def iou(s, dx, dy):
        m = transformar(sd, s, dx, dy, forma)[:teto_foto]
        inter = np.count_nonzero(m & alvo)
        uniao = np.count_nonzero(m | alvo)
        return inter / float(uniao) if uniao else 0.0

    def varrer(escalas, dxs, dys):
        melhor = (-1.0, 1.0, 0.0, 0.0)
        for s in escalas:
            for dx in dxs:
                for dy in dys:
                    v = iou(s, dx, dy)
                    if v > melhor[0]:
                        melhor = (v, float(s), float(dx), float(dy))
        return melhor

    r = varrer(np.arange(0.60, 1.05, 0.04),
               np.arange(-180, 181, 30), np.arange(-180, 181, 30))
    if verboso: print("  grosso  IoU=%.4f  s=%.4f  dx=%.0f dy=%.0f" % r)
    for ds, dd in ((0.015, 12), (0.005, 4), (0.002, 1)):
        r = varrer(np.arange(r[1] - ds * 3, r[1] + ds * 3.5, ds),
                   np.arange(r[2] - dd * 3, r[2] + dd * 3.5, dd),
                   np.arange(r[3] - dd * 3, r[3] + dd * 3.5, dd))
        if verboso: print("  refino  IoU=%.4f  s=%.4f  dx=%.0f dy=%.0f" % r)
    return r


# ------------------------------------------------------------------ assets
def matte_foto(sd, sf, s, dx, dy, margem=3, erosao=2):
    """Alfa da FOTO = silhueta da foto INTERSECTADA com a do desenho registrada.

    A intersecao e o que apaga o pedestal branco: ele existe na foto e nao
    existe no desenho. A dilatacao de `margem` px devolve a aresta real da
    foto, que o desenho nao acompanha pixel a pixel (IoU medido: 0,936).

    A EROSAO final nao e acabamento, e correcao: peca branca sobre fundo
    branco em JPEG deixa um halo de ringing de 2-3 px que passa em qualquer
    limiar de luminancia, e sobre o navy do heroi esse halo lia como purpurina
    em volta do braco. Comer 2 px de uma silhueta de 739 px de largura custa
    nada e resolve -- o contorno verdadeiro ja veio do desenho, nao daqui.
    """
    d = transformar(sd, s, dx, dy, sf.shape)
    d = np.asarray(Image.fromarray((d * 255).astype(np.uint8))
                   .filter(ImageFilter.MaxFilter(margem * 2 + 1))) > 127
    m = sf & d
    m = np.asarray(Image.fromarray((m * 255).astype(np.uint8))
                   .filter(ImageFilter.MinFilter(erosao * 2 + 1))) > 127
    return m


def tinta_desenho():
    """Alfa do TRACO, lido no canal AZUL.

    O traco e ocre (medido: RGB 0.926 / 0.665 / 0.017) sobre papel 0.996. Em
    LUMINANCIA ele so alcanca 0.46 de tinta, porque R e G continuam altos --
    ler ai obrigaria a esticar a curva e traria o papel junto. No AZUL a
    separacao e quase binaria: 0.017 contra 0.996. Mesma licao do recorte do
    braco laranja, em outro canal.
    """
    a = np.asarray(Image.open(DESENHO).convert("RGB")).astype(np.float32) / 255.0
    azul = a[..., 2]
    papel = float(np.percentile(azul, 99.0))
    tinta = np.clip((papel - azul) / max(papel, 1e-4), 0.0, 1.0)
    return tinta


def gerar(dest="site/img/heroi", larguras=(560, 1120), larg_traco=920):
    import os
    sd, _ = silhueta_desenho()
    sf, foto_rgb = silhueta_foto()
    iou, s, dx, dy = registrar(sd, sf)
    print("registro: IoU=%.4f  s=%.4f  dx=%.0f dy=%.0f" % (iou, s, dx, dy))

    alfa_foto = matte_foto(sd, sf, s, dx, dy)

    # o traco entra na MESMA grade da foto, com a MESMA transformacao: e o que
    # faz as duas camadas registrarem no fade da intro
    t = tinta_desenho()
    ti = Image.fromarray((t * 255).astype(np.uint8))
    nw, nh = int(round(ti.width * s)), int(round(ti.height * s))
    tela = Image.new("L", (sf.shape[1], sf.shape[0]), 0)
    tela.paste(ti.resize((nw, nh), Image.LANCZOS), (int(round(dx)), int(round(dy))))
    alfa_traco = np.asarray(tela).astype(np.float32) / 255.0

    # caixa comum: uniao do que as duas camadas ocupam, com folga de 4 px
    ocupa = alfa_foto | (alfa_traco > 0.08)
    x0, y0, x1, y1 = caixa(ocupa)
    x0, y0 = max(0, x0 - 4), max(0, y0 - 4)
    x1, y1 = min(ocupa.shape[1], x1 + 4), min(ocupa.shape[0], y1 + 4)
    print("caixa comum: %dx%d" % (x1 - x0, y1 - y0))

    # foto RGBA: alfa suavizado em 1 px, senao a aresta serrilha no fundo navy
    af = Image.fromarray((alfa_foto * 255).astype(np.uint8)).filter(
        ImageFilter.GaussianBlur(0.8))
    rgba = np.dstack([(foto_rgb * 255).astype(np.uint8),
                      np.asarray(af)[..., None]])
    im_foto = Image.fromarray(rgba, "RGBA").crop((x0, y0, x1, y1))

    # traco RGBA: BRANCO + alfa. Um arquivo serve os dois temas e serve tambem
    # o preenchimento dourado, porque a cor vem sempre do CSS ou de um uniform.
    br = np.full(alfa_traco.shape + (3,), 255, np.uint8)
    im_traco = Image.fromarray(
        np.dstack([br, (alfa_traco * 255).astype(np.uint8)]), "RGBA"
    ).crop((x0, y0, x1, y1))

    os.makedirs(dest, exist_ok=True)
    rel = []
    # A FOTO nao vai mais para o site. Ela existia para a intro, e a intro
    # passou a ser a marca -- o par foto/traco do braco nunca coincidia com a
    # peca 3D do heroi, porque sao a mesma maquina em poses diferentes. O que
    # sobrou em uso e a MASCARA DE TRACO, que serve de reserva para quem nao
    # tem WebGL2. Passe --foto para emitir a fotografia tambem.
    for w in (larguras if "--foto" in sys.argv else ()):
        h = max(1, round(im_foto.height * w / im_foto.width))
        f = im_foto.resize((w, h), Image.LANCZOS)
        for ext in ("avif", "webp"):
            p = "%s/epson-%d.%s" % (dest, w, ext)
            f.save(p, quality=62) if ext == "avif" else f.save(p, quality=80, method=6)
            rel.append((p, os.path.getsize(p)))

    # O TRACO sai em LA (cinza + alfa) com o alfa posterizado em 32 niveis.
    # Medido a 920 px: RGBA 555 KB, LA 432 KB, LA posterizado 201 KB. O alfa e
    # o unico canal que alguem le -- mask-image e texImage2D -- e 32 niveis
    # bastam para linha antialiasada; os outros tres canais eram peso morto.
    w = larg_traco
    h = max(1, round(im_traco.height * w / im_traco.width))
    al = np.asarray(im_traco.resize((w, h), Image.LANCZOS))[..., 3]
    al = ((al.astype(np.int32) // 8) * 8).astype(np.uint8)
    p = "%s/epson-traco-%d.png" % (dest, w)
    Image.fromarray(np.dstack([np.full_like(al, 255), al]), "LA").save(p, optimize=True)
    rel.append((p, os.path.getsize(p)))

    for p, n in rel:
        print("  %-44s %7.1f KB" % (p, n / 1024.0))
    print("proporcao: %d / %d = %.4f" % (im_foto.width, im_foto.height,
                                         im_foto.width / im_foto.height))
    return im_foto.size
