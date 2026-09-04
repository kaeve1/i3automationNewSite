# -*- coding: utf-8 -*-
"""Pipeline de imagens do site i3Automations.

Gera, para cada origem: AVIF + WebP + JPEG/PNG em cada largura declarada, mais
a MASCARA DE TRACO (XDoG) usada pela lente de revelacao. A mascara sai como
RGBA branco+alfa: um arquivo serve tema claro e escuro, porque a cor vem do
CSS (mask-image sobre bloco solido) ou de um uniform no shader.

Uso: python ferramentas/build_imagens.py
"""
import os
import sys
import numpy as np
from PIL import Image, ImageFilter

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import recorte as rec
import linha as lin

RAIZ = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
ORIG = os.path.join(RAIZ, 'referencia', 'universodoclp-assets')
DEST = os.path.join(RAIZ, 'site', 'img')
FOTOS = os.path.join(ORIG, 'referencia', 'universodoclp', 'fotosproduto')
NOVAS = os.path.join(FOTOS, 'new')

Image.MAX_IMAGE_PIXELS = None

GAL01 = 'gal-01-qxsbc8l2owvricr08p276z541glmf3eyt7ai3nir8w.jpg'
GAL02 = 'gal-02-qxsbc6peb8t6v4tqjo8y1zm6uouvzp7i4xzj53ljlc.jpg'
GAL04 = 'gal-04-qxsbc3vvqqpbwaxu0512cibt2j8sclwb4k12p9pq40.jpg'
GAL05 = 'gal-05-qxsbc207d2mr930kb47t7isvvri1x7ougaq3qpsigg.jpg'
PAINEL = '20240413_091814-rotated-qxscob1y6won8gxejz2d7cgpntod1v8t34bem28z1s.jpg'


def salvar(im, base, larguras, fmt_base='jpg', qualidade=78, so_base=False):
    """Exporta AVIF + WebP + formato base em cada largura. Devolve relatorio."""
    os.makedirs(os.path.dirname(base), exist_ok=True)
    saida = []
    for w in larguras:
        h = max(1, round(im.height * w / im.width))
        r = im if (w == im.width) else im.resize((w, h), Image.LANCZOS)
        # O formato base e so o FALLBACK do <img>, e o <img> aponta sempre para
        # a maior largura. Emitir jpg em toda largura gerava 27 arquivos que
        # nenhuma pagina referenciava (medido: 61 orfaos na primeira passada).
        # so_base: a mascara de traco e lida por mask-image e por gl.texImage2D,
        # e as duas so consomem o PNG. AVIF e WebP dela eram 10 arquivos mortos.
        if so_base:
            formatos = (fmt_base,)
        else:
            formatos = ('avif', 'webp', fmt_base) if w == larguras[-1] else ('avif', 'webp')
        for ext in formatos:
            p = '%s-%d.%s' % (base, w, ext)
            if ext == 'avif':
                r.save(p, quality=max(30, qualidade - 12))
            elif ext == 'webp':
                r.save(p, quality=qualidade, method=6)
            elif ext == 'jpg':
                r.convert('RGB').save(p, quality=qualidade + 4, optimize=True,
                                      progressive=True)
            else:
                # PNG indexado guarda o alfa no chunk tRNS, e o Pillow so o
                # escreve se ele vier por parametro. Sem esta linha a mascara
                # sai OPACA -- e o sintoma nao e erro nenhum, e o card inteiro
                # coberto de navy.
                extra = {}
                if r.mode == 'P' and 'transparency' in r.info:
                    extra['transparency'] = r.info['transparency']
                r.save(p, optimize=True, **extra)
            saida.append((os.path.relpath(p, RAIZ), os.path.getsize(p)))
    return saida


def recortar_cobrir(im, prop, ancora=0.42):
    """Recorta ao centro para a proporcao pedida (largura/altura).

    ancora < .5 sobe o recorte: em foto industrial o assunto quase sempre
    esta acima do centro geometrico, e o chao nao interessa.
    """
    a = im.width / im.height
    if a > prop:
        w = round(im.height * prop)
        x = round((im.width - w) * .5)
        return im.crop((x, 0, x + w, im.height))
    h = round(im.width / prop)
    y = round((im.height - h) * ancora)
    return im.crop((0, y, im.width, y + h))


NIVEIS_MASCARA = 32


def mascara_rgba(mascara_l):
    """L -> PNG INDEXADO branco com alfa = traco. Um arquivo, dois temas.

    O nome ficou por compatibilidade com os dois call sites; o que ele devolve
    e modo 'P'. A conversao e o achado de 21/08, e ela vale 409 KB na home:

      RGBA .......... 740 KB   4 bytes/px, e TRES deles sao a mesma constante
      LA posterizado  502 KB   a receita que o epson.py ja usava (-32%)
      P com tRNS .... 331 KB   1 byte/px + 32 entradas de alfa (-54%)

    Medido: o RGB destas mascaras e 255 em TODO pixel dos cinco arquivos, entao
    jogar fora os tres canais nao perde nada -- e o consumo confirma, porque
    nenhum dos dois consumidores le RGB. O CSS `mask-image` le so o alfa; o
    shader da lente le `texture(uTraco, ...).a`.

    Por que nao WebP, que media 290 KB (-60%): esta mascara E a via de reserva
    de quem nao tem WebGL2. Trocar o formato do fallback por 41 KB poe uma
    negociacao de formato no unico caminho que existe para NAO falhar. PNG
    indexado continua sendo PNG em qualquer navegador que exista.

    32 niveis: o erro maximo introduzido no alfa e 5/255, em traco
    antisserrilhado de 1 px. E o mesmo numero que epson.py escolheu.
    """
    a = mascara_l.convert('L')
    n = NIVEIS_MASCARA
    # Quantiza para indice 0..n-1. O tRNS mapeia indice -> alfa, entao a
    # quantizacao acontece UMA vez, aqui, e nao de novo no encoder.
    idx = a.point(lambda v: int(round(v / 255 * (n - 1))))
    pal = Image.new('P', mascara_l.size)
    pal.putdata(list(idx.getdata()))
    # As n entradas sao TODAS brancas: a cor da mascara vem do CSS (bloco
    # solido sob mask-image) ou de um uniform no shader, nunca do arquivo.
    pal.putpalette(bytes([255, 255, 255]) * n + bytes(3 * (256 - n)))
    pal.info['transparency'] = bytes(round(i / (n - 1) * 255) for i in range(n))
    return pal


def heroi(rel):
    """Recorte + traco do braco ABB (engcontrole.png).

    DESLIGADO no fluxo normal desde que o heroi virou geometria gerada
    (js/braco.js): nada no site aponta mais para img/heroi/braco-*, e emitir
    esses seis arquivos devolvia 949 KB de orfao a site/ a cada build. A
    funcao fica porque a receita continua valendo -- rodar
    `python ferramentas/build_imagens.py --braco` traz tudo de volta.
    """
    print('== heroi: braco robotico ==')
    im = Image.open(os.path.join(FOTOS, 'engcontrole.png')).convert('RGB')
    a = np.asarray(im).astype(np.float32) / 255
    corpo = rec.segmentar(a)
    alfa = Image.fromarray((corpo * 255).astype(np.uint8))
    alfa = alfa.filter(ImageFilter.GaussianBlur(1.1))
    cut = im.convert('RGBA')
    cut.putalpha(alfa)
    cut = cut.crop(cut.getbbox())

    # margem de 2%: a silhueta do traco tem 2px de meia-largura e nao pode
    # encostar na borda do arquivo, ou o desenho sai cortado no eixo.
    m = round(cut.width * .02)
    tela = Image.new('RGBA', (cut.width + m * 2, cut.height + m * 2), (0, 0, 0, 0))
    tela.paste(cut, (m, m))
    cut = tela
    print('   recorte nativo: %dx%d' % cut.size)

    rel += salvar(cut, os.path.join(DEST, 'heroi', 'braco'),
                  [cut.width, cut.width * 2], fmt_base='png', qualidade=82)
    traco = mascara_rgba(lin.desenhar(cut, escala=2))
    rel += salvar(traco, os.path.join(DEST, 'heroi', 'braco-traco'),
                  [cut.width * 2], fmt_base='png', so_base=True)
    return rel, cut.size


SETORES = [
    ('oil-gas', os.path.join(FOTOS, 'gas.jpg'), 4 / 3),
    ('agua', os.path.join(NOVAS, GAL04), 1.0),
    ('automotivo', os.path.join(NOVAS, GAL01), 1.0),
    ('papel', os.path.join(FOTOS, 'pexels-mazhar-ulazhar-50963217-31352672.jpg'), 4 / 3),
    ('solar', os.path.join(FOTOS, 'michael_pointner-solar-8244680_1920.jpg'), 4 / 3),
]

# Fotografia de campo entregue pelo cliente em melhorias/gallery. Todas 600x600
# -- e todas AUTORAIS, o que as torna mais valiosas que qualquer banco de imagem
# (design.md §6.5). Ficam aqui, e nao em referencia/, porque chegaram depois.
NOVA_GAL = os.path.join(RAIZ, 'melhorias', 'gallery')

GALERIA = [
    ('painel', os.path.join(NOVAS, PAINEL)),
    ('obra-agua', os.path.join(
        NOVA_GAL, '20210205_132240-scaled-qxscmwanxur5tiz4sd4igp9tl0mji7naw536p4c8ds.jpg')),
    ('painel-campo', os.path.join(
        NOVA_GAL, '20240427_161747-qxscoyjwxrktapz9qr81foj8iggjeau3icmjlza4q8.jpg')),
    ('bomba', os.path.join(
        NOVA_GAL, 'gal-03-qxsbc4tpxkqm7wwgunfox039nx45kb01gook6jobxs.jpg')),
    ('scada', os.path.join(
        NOVA_GAL, 'gal-06-qxsbc12d68lgxh1xglt6n11fadmopil4462m9ftwmo.jpg')),
    ('body-in-white', os.path.join(NOVAS, GAL01)),
    ('bancada', os.path.join(NOVAS, GAL02)),
    ('captacao', os.path.join(NOVAS, GAL04)),
    ('comissionamento', os.path.join(NOVAS, GAL05)),
    ('sala-controle', os.path.join(FOTOS, 'image1.png')),
    ('campo', os.path.join(FOTOS, 'foto.png')),
    ('celula', os.path.join(FOTOS, 'smpliderautomacao.png')),

    # --- Ampliacao de 20/08: a galeria passou a mostrar o acervo inteiro, e
    # nao so a fotografia autoral. A pagina deixou de AFIRMAR autoria por causa
    # disso (ver o lead reescrito em build_site.py) -- a alternativa seria uma
    # galeria de 12 fotos afirmando uma coisa e mostrando outra.
    #
    # FICARAM DE FORA, e o motivo importa:
    #   image.png e 3d.png .... captura da ilustracao de marketing de OUTRA
    #                           empresa ("24/7 Clean Energy as a Service").
    #                           Conteudo de marca de terceiro nao entra.
    #   bet.png, fotologo.png . identidade do Universo do CLP, outro produto.
    ('clarificador', os.path.join(FOTOS, 'agua.png')),
    ('solar-campo', os.path.join(FOTOS, 'solar.png')),
    ('fiacao', os.path.join(FOTOS, 'foto1.png')),
    ('braco-bancada', os.path.join(FOTOS, 'engcontrole.png')),
    ('refinaria', os.path.join(FOTOS, 'gas.jpg')),
    ('bornes', os.path.join(FOTOS, 'pexels-maltelu-5276099.jpg')),
    ('teclado', os.path.join(FOTOS, 'pexels-shvetsa-5953589.jpg')),
    ('prensas', os.path.join(FOTOS, 'pexels-mazhar-ulazhar-50963217-31352672.jpg')),
    ('prensa-detalhe', os.path.join(FOTOS, 'pexels-julio-muebles-3330448-4980786.jpg')),
    ('agv', os.path.join(FOTOS, 'pexels-peter-xie-371876898-36522028.jpg')),
    ('engrenagens', os.path.join(FOTOS, 'pexels-pixabay-159298.jpg')),
    ('britagem', os.path.join(FOTOS, 'pexels-valentin-ilas-2154050328-38862400.jpg')),
    ('baterias', os.path.join(FOTOS, 'pexels-warren-yip-1081272606-37982526.jpg')),
    ('fiacao-textil', os.path.join(FOTOS,
                                   'pexels-salim-serdar-bali-2159840407-36327501.jpg')),
    ('solar-aereo', os.path.join(FOTOS, 'michael_pointner-solar-8244680_1920.jpg')),
    ('solar-painel', os.path.join(FOTOS, 'mrganso-photovoltaic-system-2742302_1920.jpg')),
    ('linha-solar', os.path.join(FOTOS, 'tylijura-technology-10404349_1920.jpg')),

    # --- Entradas de 20/08: as quatro fontes novas de `referencia/`.
    # Duas delas ja servem de fundo das secoes duplas (`dupla/clp` e
    # `dupla/comando`); aqui saem de novo, na proporcao NATIVA e nas larguras
    # da galeria. Nao e duplicacao a toa -- e o mesmo padrao que `refinaria`
    # ja segue, que existe em `faixa/` e em `galeria/` com recortes diferentes.
    ('painel-clp', os.path.join(RAIZ, 'referencia',
                                'raymond-sime-KDkU44ikiko-unsplash.jpg')),
    ('mesa-comando', os.path.join(RAIZ, 'referencia',
                                  'martinelle-desk-2905361.jpg')),
    ('robo-linha', os.path.join(RAIZ, 'referencia',
                                'homa-appliances-sz1CHL7Pky0-unsplash.jpg')),
    ('solda-placa', os.path.join(RAIZ, 'referencia',
                                 'theaflowers-soldering-7897827.jpg')),
]

CABECALHOS = [
    # `fotovoltaico` (tylijura-technology-10404349_1920.jpg) esteve aqui por
    # uma entrega e SAIU: o cabecalho de who-we-are ficou sem fotografia, com
    # navy chapado e a reticula. A receita fica registrada aqui caso volte --
    # 1920x1076 recorta para 1920/620 sem ampliar, com folga vertical de 456 px
    # e a ancora .42 padrao mantendo o capacete inteiro.
    ('quem-somos', os.path.join(FOTOS, 'foto.png')),
    # `capacidades` (1024x331) SAIU DA GERACAO em 2026-08-25. Ela nunca chegou
    # a vestir capabilities: naquele cabecalho de 620 px de altura ela seria
    # AMPLIADA 1,87x e sairia borrada, entao a pagina usa `faixa/refinaria`
    # (2560x979, REDUZIDA 0,63x na mesma caixa). O unico consumidor que
    # sobrava era o cabecalho de terms-and-conditions -- e as duas paginas
    # legais perderam a fotografia de cabecalho, porque vestiam a mesma foto
    # de uma pagina de conteudo e porque um documento legal nao tem hero.
    # Sem consumidor, eram 72 KB de deploy que `varredura.py` acusava.
    ('projetos', os.path.join(FOTOS, 'smpliderautomacao.png')),
    # `servicos` (pexels-maltelu-5276099.jpg, o macro de reles) SAIU DA
    # GERACAO em 2026-08-27: services deixou de ter cabecalho fotografico e
    # passou a abrir em VIDEO, como a home. Sem consumidor, eram 5 arquivos
    # que `varredura.py` acusaria -- o mesmo destino de `capacidades` e
    # `ferramental`, e pela mesma razao.
    #
    # A FONTE NAO SE PERDE, e isso importa: `pexels-maltelu` continua em
    # `galeria/bornes`, e plano.md §8.2 sempre a destinou a CAPABILITIES (o
    # macro do modulo de reles). Tira-la daqui devolve a foto ao papel para
    # o qual ela foi escolhida, em vez de gasta-la num cabecalho.
    ('galeria', os.path.join(FOTOS, 'engcontrole.png')),
    ('contato', os.path.join(FOTOS, 'pexels-shvetsa-5953589.jpg')),
]


# PLACAS DOS SETORES — o painel preso de past-performance.
#
# Sao QUADRADAS e sao PLACAS MONTADAS, nao fundo sangrado, e a razao e de
# resolucao. A fotografia autoral do cliente e toda 600x600 (teto do acervo, ja
# registrado em memoria.md): sangrada numa moldura de 1440 px ela seria AMPLIADA
# 2,4x e viraria papa. Montada numa placa de ~440 px ela e REDUZIDA -- que e a
# unica forma de ficar nitida.
#
# O efeito colateral e bom: com a foto numa placa, o texto do setor nunca cai
# em cima dela. O esboco do usuario mostra o texto brigando com uma imagem
# cheia de detalhe, e nenhum veu resolve isso sem apagar a foto.
#
# Onde ha fonte grande, sai tambem em 900 -- o srcset escolhe sozinho e os
# setores com fonte boa ficam nitidos em tela de alta densidade.
SETOR_PLACAS = [
    ('automotivo', os.path.join(NOVAS, GAL01)),
    ('oil-gas', os.path.join(FOTOS, 'gas.jpg')),
    ('agua', os.path.join(NOVAS, GAL04)),
    ('papel', os.path.join(FOTOS, 'pexels-mazhar-ulazhar-50963217-31352672.jpg')),
    ('solar', os.path.join(FOTOS, 'michael_pointner-solar-8244680_1920.jpg')),
    ('federal', os.path.join(NOVAS, GAL05)),
]


def setor_placas(rel):
    print('== placas dos setores (past-performance) ==')
    for nome, src in SETOR_PLACAS:
        im = recortar_cobrir(Image.open(src).convert('RGB'), 1.0)
        larg = [w for w in (600, 900) if w <= im.width] or [im.width]
        rel += salvar(im, os.path.join(DEST, 'setor', nome), larg, qualidade=80)
        print('   %-11s %dx%d -> %s' % (nome, im.width, im.height, larg))
    return rel


def setores(rel):
    """Cada setor sai em dois mapas: a fotografia e o TRACO dela.

    A lente de revelacao precisa dos dois pixel a pixel alinhados, entao o
    traco e gerado do MESMO recorte ja enquadrado — nunca do original, ou o
    desenho apareceria deslocado sob o ponteiro.
    """
    print('== setores ==')
    for nome, src, prop in SETORES:
        im = recortar_cobrir(Image.open(src).convert('RGB'), prop)
        larg = [336, 672] if im.width >= 672 else [im.width]
        rel += salvar(im, os.path.join(DEST, 'setores', nome), larg)

        # foto opaca: contorno(alfa) da zero e so o interno da XDoG sobrevive,
        # que e exatamente o desenho de dentro da cena que queremos.
        base = im if im.width <= 900 else im.resize(
            (900, round(im.height * 900 / im.width)), Image.LANCZOS)
        traco = mascara_rgba(lin.desenhar(base.convert('RGBA'), escala=1))
        rel += salvar(traco, os.path.join(DEST, 'setores', nome + '-traco'),
                      [traco.width], fmt_base='png', so_base=True)
        print('   %-11s %dx%d -> %s  (traco %dpx)'
              % (nome, im.width, im.height, larg, traco.width))
    return rel


def faixas(rel):
    print('== faixas full-bleed ==')
    # AS TRES ULTIMAS ENTRARAM EM 20/08 PARA MATAR REPETICAO, e a auditoria que
    # as pediu esta em /tmp/repete.py -> ferramentas/repetidas.py: tres fotos
    # apareciam em DOIS papeis ao mesmo tempo.
    #
    #   cabecalho/servicos ... cabecalho de services E fundo em who-we-are
    #   faixa/refinaria ...... cabecalho de capabilities E fundo em who-we-are
    #   faixa/robotica ....... faixa da home E fundo de "The ledger"
    #
    # A escolha das substitutas NAO foi por assunto sozinho: foi por AMPLITUDE
    # depois do veu. Uma foto so aparece se a variacao dela sobreviver a camada
    # que a cobre, e os dois veus do site sao opostos -- o navy de
    # `.secao--foto` ESCURECE (foto clara rende), o off-white de
    # `.secao--foto-corpo` CLAREIA (foto escura rende).
    BANDA, SECAO = 1920 / 734, 1.6
    fontes = [
              # `robotica` e `refinaria` SAIRAM da geracao em 2026-08-26.
              #   robotica ... era a faixa full-bleed da home, que virou video
              #                e quatro momentos. Sem consumidor.
              #   refinaria .. era o cabecalho de capabilities, e e um recorte
              #                de `gas.jpg`. A mesma fotografia estava em cinco
              #                lugares do site; agora aparece uma vez, no
              #                momento 4 da home. Capabilities recebeu
              #                `britagem-planta` no lugar.
              # As duas linhas ficam comentadas em vez de apagadas: a receita
              # continua ai se o papel voltar.
              # ('robotica', os.path.join(ORIG, 'site', 'img', 'faixa',
              #                           'robotica-1920.jpg'), BANDA),
              # ('refinaria', os.path.join(FOTOS, 'gas.jpg'), BANDA),
              # BRITAGEM: planta de agregado com esteira e silos, 9504x6336.
              # Entrou em 2026-08-26 para tirar `gas.jpg` do cabecalho de
              # capabilities. `gas.jpg` e a UNICA foto de oil & gas do acervo
              # inteiro, e estava recortada em CINCO lugares -- inclusive duas
              # vezes na mesma pagina, a home. Ela agora aparece uma vez so,
              # no momento 4, em full-bleed com o traco. Quando so ha um
              # exemplar de um assunto, usa-lo bem uma vez vale mais do que
              # espalha-lo.
              ('britagem-planta', os.path.join(
                  FOTOS, 'pexels-valentin-ilas-2154050328-38862400.jpg'), BANDA),
              # GABINETE: interior de painel com CLPs, borneiras e chicote,
              # 7008x4672 -- a maior fonte do acervo depois de `britagem`, e a
              # unica que ate agora so tinha aparecido em MINIATURA. Ela existe
              # desde 20/08 como `galeria/painel-clp`, num mosaico de 400-800px;
              # e a primeira vez que sai em tamanho de secao.
              #
              # DESTINO: o fundo de "What leaves with you", em services. O
              # assunto e o argumento: os quatro entregaveis da dobra --
              # esquema, codigo, registro de ensaio, treinamento -- descrevem
              # exatamente este gabinete. A lista fica POR CIMA da coisa que
              # ela documenta.
              #
              # E O VEU E ESCURO, o que decidiu a superficie da secao inteira.
              # A dobra era off-white e o pedido foi "foto de fundo"; medido
              # (media local 12x12, p2 dos blocos), nenhum veu claro serve:
              #
              #   veu                corpo    secundario   accent   amplitude
              #   navy .55/.35       7,18:1     4,61:1      4,61:1     46,5
              #   off-white .72      8,28:1     3,28:1      3,00:1     44,9
              #   off-white .80     10,15:1     4,02:1      3,68:1     32,1
              #   quente .78         9,59:1     3,80:1      3,47:1     35,3
              #
              # Sob veu claro o texto SECUNDARIO reprova em toda linha, e
              # fecha-lo ate passar apaga a fotografia (amplitude cai a 32).
              # O veu navy ja medido de `.secao--foto` passa nos tres e deixa
              # 46,5 de amplitude. A secao vira escura, e o ritmo da pagina
              # continua alternando em toda emenda.
              ('gabinete', os.path.join(
                  RAIZ, 'referencia', 'raymond-sime-KDkU44ikiko-unsplash.jpg'),
               SECAO),
              # `ferramental` SAIU DA GERACAO em 2026-08-26 (nona rodada). Ele
              # era o fundo da dobra do argumento em who-we-are -- detalhe de
              # ferramental de prensa, a maior amplitude do acervo sob navy
              # (63,5) --, e aquela dobra passou a ter FUNDO EM VIDEO
              # (`fundo-projeto`, o engenheiro na estacao) a pedido do usuario.
              #
              # Sem consumidor eram 7 arquivos e 1,0 MB que `varredura.py`
              # acusava. A receita fica comentada e nao apagada, como as de
              # `robotica` e `refinaria` logo acima: se o papel voltar, ela
              # continua aqui.
              # ('ferramental', os.path.join(
              #     FOTOS, 'pexels-julio-muebles-3330448-4980786.jpg'), SECAO),
              # "Vendor profile" (who-we-are, veu navy): a copy nomeia
              # "controls work on SOLAR GENERATION across the United States",
              # entao a foto passa a dizer o que o texto diz. Amplitude 47,7.
              # "The ledger" (past-performance, veu OFF-WHITE): engrenagem e
              # corrente. Mecanismo neutro, que e o certo para "six sectors,
              # one discipline" -- nao aponta setor nenhum. E amplitude 46,2
              # contra os 34,8 de `robotica`, que era a queixa: praticamente
              # invisivel sob o veu claro.
              ]
    # A PROPORCAO E POR ENTRADA, e nao uma so, porque os destinos sao dois.
    # `.faixa` e o cabecalho sao BANDAS (2,6 e 2,3); `.secao--foto` cobre a
    # secao INTEIRA, que a 1440 tem 720 a 900 px de altura -- proporcao ~1,6.
    # Recortar um fundo de secao a 2,62 joga fora justamente a altura de que
    # ele precisa, e a foto acaba AMPLIADA na caixa. Foi o que aconteceu com
    # `solar-estrutura` na primeira volta: 1,23x, o erro que "Since 2000" custou.
    for nome, src, prop in fontes:
        im = recortar_cobrir(Image.open(src).convert('RGB'), prop)
        larg = [w for w in (1280, 1920, 2560) if w <= im.width] or [im.width]
        rel += salvar(im, os.path.join(DEST, 'faixa', nome), larg, qualidade=74)
        print('   %-10s %dx%d -> %s' % (nome, im.width, im.height, larg))
    return rel


# A galeria e um MOSAICO POR COLUNAS, e um mosaico so existe se as pecas
# tiverem alturas diferentes. Estes sao os limites da proporcao que ele aceita.
#
# Ate 20/08 a galeria inteira saia recortada em 1.0 -- `recortar_cobrir(im, 1.0)`
# --, entao as 29 fotos eram 29 QUADRADOS IDENTICOS e o "mosaico" era uma grade
# uniforme. Era essa a causa real de a pagina parecer parada: nao faltava
# animacao, faltava VARIACAO. O comentario do CSS ja descrevia proporcoes de
# 0,56 a 1,50 -- descrevia as FONTES, nao o que estava sendo publicado.
#
# POR QUE HA LIMITE, e nao a proporcao nativa crua. Duas fontes sao extremas:
# `fiacao` e 0,563 (retrato bem estreito) e `linha-solar`/`prensas` passam de
# 1,77. Numa coluna de ~430 px o retrato de 0,563 fica com 764 px de altura --
# uma tira que sozinha desequilibra a coluna inteira -- e a paisagem de 1,78
# vira uma faixa de 241 px em que o assunto some. Os limites cortam so o
# excesso: 20 das 29 passam sem tocar em nada.
PROP_MIN = 0.66      # retrato 2:3
PROP_MAX = 1.60      # paisagem 8:5


def galeria(rel):
    print('== galeria ==')
    for nome, src in GALERIA:
        im = Image.open(src).convert('RGB')
        # PROPORCAO NATIVA, so aparada nas pontas. As 9 fotos autorais do
        # cliente sao 600x600 e continuam quadradas -- e a fonte que elas tem.
        prop = min(PROP_MAX, max(PROP_MIN, im.width / im.height))
        im = recortar_cobrir(im, prop)
        larg = [400, 800] if im.width >= 800 else [im.width]
        rel += salvar(im, os.path.join(DEST, 'galeria', nome), larg)
        print('   %-16s %dx%d (%.2f) -> %s'
              % (nome, im.width, im.height, prop, larg))
    return rel


# FUNDO UNICO DAS SECOES DUPLAS CONECTADAS.
#
# Duas secoes escuras seguidas (a citacao + o CTA na home; "Your design or
# ours" + o CTA em services) compartilhavam UMA superficie mas carregavam DUAS
# fotografias diferentes. A emenda saltava: a foto de cima terminava e outra
# comecava no meio de um bloco que se le como um so. Agora e uma imagem so,
# atravessando as duas.
#
# GRAVADAS EM 3:2, que e a proporcao NATIVA das duas fontes -- entao nao ha
# recorte nenhum aqui e o `object-fit: cover` do CSS decide o enquadramento por
# janela. As fontes sao enormes (7008 e 6000 px de largura), entao mesmo a
# maior saida e uma REDUCAO forte: 0,37x e 0,43x.
DUPLAS = [
    # painel de controle aberto: CLPs, disjuntores, bornes e canaleta. E
    # literalmente o produto da i3, e o par da home ("Senior control experts
    # know things they do not teach in school") fala do conhecimento que mora
    # dentro dele. A home nao tem foto no cabecalho -- a peca de la e o braco
    # em 3D -- entao nao ha assunto repetido na pagina.
    # `clp` SAIU da geracao: era a dupla da HOME, e a home deixou de ter uma
    # quando virou video e momentos. Ela voltou ao deploy sem querer nesta
    # rodada, porque gerar `fiacao` regenera a lista inteira -- e
    # `varredura.py` a pegou de novo. Comentada, e nao apagada: a receita
    # continua aqui se o papel voltar.
    # ('clp', os.path.join(RAIZ, 'referencia',
    #                      'raymond-sime-KDkU44ikiko-unsplash.jpg')),
    # mesa de comando: mao do operador no joystick, botoeira e IHM. Vai em
    # services de proposito, e NAO o painel: o cabecalho daquela pagina ja e um
    # close de reles e bornes, e duas fotos de painel na mesma pagina leem como
    # a mesma foto duas vezes -- armadilha ja registrada em memoria.md.
    ('comando', os.path.join(RAIZ, 'referencia',
                             'martinelle-desk-2905361.jpg')),
    # A DUPLA DA HOME: governo + CTA sob UMA fotografia, como who-we-are e
    # past-performance ja fazem. Maquina de malha circular com linhas
    # pneumaticas -- 2080x3120, RETRATO, que e o formato de que uma caixa
    # empilhada precisa.
    #
    # A restricao desta caixa e de CONTRASTE e ja custou uma medicao antes:
    # a nota de who-we-are registra que `baterias` foi a unica do acervo a
    # passar AA la. Medido agora, na caixa da home (1440x1700):
    #   veu .78 (fechado) .. 10,47:1      veu .50 (aberto) .. 5,15:1
    # Passa nos dois. A referencia `baterias` da 11,61 e 6,47 -- esta e um
    # degrau abaixo e continua acima do piso de 4,5.
    # 1440/1700: a caixa da home e um pouco mais ALTA que a de who-we-are
    # (1440/1560) porque o bloco de governo dela e o mesmo mas o CTA fecha a
    # pagina. Sem a proporcao por entrada a foto sairia recortada em 3:2 e
    # jogaria fora metade da altura de um original que e RETRATO.
    ('fiacao', os.path.join(FOTOS,
                            'pexels-salim-serdar-bali-2159840407-36327501.jpg'),
     1440 / 1700),

    # --- 20/08: mais duas duplas, a pedido. AQUI A PROPORCAO E POR ENTRADA e
    # nao 3:2 fixo, porque estas duas caixas sao MUITO mais altas: a de
    # who-we-are tem 1560 px a 1440 de largura (proporcao 0,92, quase
    # retrato), porque a secao de credenciais federais e longa. Gravar 3:2 e
    # cobrir uma caixa dessas jogaria fora quase metade da altura.
    #
    # `baterias` foi a UNICA do acervo a passar AA na caixa de who-we-are --
    # as outras reprovam o corpo entre 3,5 e 4,1. Fonte 4164x5552 em RETRATO,
    # que e o formato de que uma caixa alta precisa. E modulos de armazenamento
    # conversam com a copy, que fala de geracao solar.
    # `baterias` SAIU DE WHO-WE-ARE em 2026-08-26 (decima rodada), a pedido:
    # "troque a imagem de fundo das ultimas duas secoes". Ele fica na geracao
    # porque o nome continua servindo a quem quiser a caixa alta -- e porque
    # apagar a receita perderia a medicao que o comentario acima carrega.
    ('baterias', os.path.join(FOTOS,
                              'pexels-warren-yip-1081272606-37982526.jpg'), 1440 / 1560),
    # A DUPLA DE WHO-WE-ARE, desde 2026-08-26: bancada de prototipagem vista de
    # cima -- placa de microcontrolador, duas protoboards, LEDs e jumpers sobre
    # superficie preta. Fonte 6000x4000, entregue pelo usuario em `mudanca/`.
    #
    # Proporcao 1440/1560, a mesma que `baterias` usava: a caixa e a mesma (o
    # bloco de credenciais federais e longo e deixa o conjunto quase retrato),
    # e gravar 3:2 jogaria fora quase metade da altura.
    #
    # A LEGENDA NAO AFIRMA AUTORIA, e aqui isso pesa mais que de costume: o
    # objeto e uma montagem de bancada em protoboard, nao equipamento
    # industrial instalado. `alt` descreve o que se ve e para ai -- e nenhuma
    # legenda visivel acompanha, porque a foto e fundo de secao e nao figura.
    #
    # `(.75, .16)` POE A PROTOBOARD NA FAIXA LIVRE. Sem a janela ela cai a ~49%
    # da altura -- o centro geometrico, que aqui e exatamente onde o veu esta
    # FECHADO e onde o texto vive. Resultado medido: o corpo caia para 3,95:1
    # (o objeto e branco) E a faixa aberta, em 56-64%, pegava so fundo preto,
    # ou seja a foto nao aparecia em lugar nenhum. Com a janela ela vai para
    # ~60% -- o meio da faixa aberta.
    ('prototipagem', os.path.join(RAIZ, '..', 'mudanca',
                                  'jorge-ramirez-1GLDpzTIcRU-unsplash.jpg'),
     1440 / 1560, (.75, .16)),
    # `engrenagem` ja era o fundo de "The ledger" e continua: mecanismo neutro,
    # certo para "six sectors, one discipline". Regravada na proporcao da dupla
    # em vez da de banda, para nao desperdicar altura.
    ('engrenagem', os.path.join(FOTOS, 'pexels-pixabay-159298.jpg'), 1440 / 1292),
]


def duplas(rel):
    """Fundo unico que atravessa duas secoes escuras conectadas.

    O 4o campo da entrada, `janela`, e opcional e vale `(fracao, ancora)`: um
    recorte VERTICAL da fonte, feito ANTES do recorte de cobertura.

    PARA QUE ELE EXISTE. O veu da dupla nao e uniforme -- ele fecha onde o
    texto vive e ABRE numa faixa livre (56% a 64% em who-we-are). A fotografia
    so aparece de verdade nessa faixa. Se o assunto da foto cair no centro
    geometrico, ele cai justamente sob a parte FECHADA do veu: paga contraste
    (obriga a fechar ainda mais) e nao aparece (a faixa aberta pega fundo
    vazio). Os dois lados perdem.

    `janela` desloca o assunto para dentro da faixa livre. Em `prototipagem`
    a protoboard esta a ~49% da altura da fonte; com `(.75, .16)` ela vai para
    ~60%, que e o meio da faixa aberta. Mesma foto, mesmo veu, e agora ela e
    vista onde da para ver.
    """
    print('== fundo das secoes duplas ==')
    for entrada in DUPLAS:
        nome, src = entrada[0], entrada[1]
        prop = entrada[2] if len(entrada) > 2 else 3 / 2
        janela = entrada[3] if len(entrada) > 3 else None
        im0 = Image.open(src).convert('RGB')
        if janela:
            fr, anc = janela
            h = round(im0.height * fr)
            y = round((im0.height - h) * anc)
            im0 = im0.crop((0, y, im0.width, y + h))
        im = recortar_cobrir(im0, prop)
        larg = [w for w in (1280, 1920, 2560) if w <= im.width] or [im.width]
        rel += salvar(im, os.path.join(DEST, 'dupla', nome), larg, qualidade=72)
        print('   %-9s %dx%d -> %s' % (nome, im.width, im.height, larg))
    return rel


def cabecalhos(rel):
    """Faixa de topo das paginas internas — foto com overlay navy."""
    print('== cabecalhos de pagina ==')
    for nome, src in CABECALHOS:
        im = recortar_cobrir(Image.open(src).convert('RGB'), 1920 / 620)
        larg = [w for w in (1280, 1920) if w <= im.width] or [im.width]
        rel += salvar(im, os.path.join(DEST, 'cabecalho', nome), larg, qualidade=72)
        print('   %-12s %dx%d -> %s' % (nome, im.width, im.height, larg))
    return rel


# IMAGEM SOCIAL POR PAGINA.
#
# Com uma so para as nove, todo link partilhado saia com o mesmo cartao -- e o
# cartao e justamente o que diferencia um link do outro numa linha do tempo.
#
# E ELAS SAO GERADAS, nao reaproveitadas de outro recorte. O cartao social e
# 1200x630 (1,91:1) e o acervo publicado nao tem nada nessa proporcao: as
# faixas sao 2,6 a 3,1 e `dupla/baterias` e RETRATO. Apontar `og:image` para
# um recorte de outra proporcao entrega ao LinkedIn uma imagem que ele vai
# cortar por conta propria, no lugar errado.
#
# As fontes foram escolhidas por REDUCAO, a regra que "Since 2000" custou. A
# versao anterior usava `engcontrole.png` (1125x750), que AMPLIAVA 1,07x --
# pouco, mas era ampliacao, e ninguem tinha medido.
OG_PAGINAS = [
    ('og',            os.path.join(RAIZ, 'referencia',
                                   'raymond-sime-KDkU44ikiko-unsplash.jpg')),
    ('who-we-are',    os.path.join(FOTOS, 'pexels-warren-yip-1081272606-37982526.jpg')),
    ('capabilities',  os.path.join(FOTOS, 'gas.jpg')),
    ('past-performance', os.path.join(FOTOS, 'pexels-pixabay-159298.jpg')),
    ('services',      os.path.join(FOTOS, 'pexels-maltelu-5276099.jpg')),
    ('gallery',       os.path.join(RAIZ, 'referencia',
                                   'homa-appliances-sz1CHL7Pky0-unsplash.jpg')),
    ('contact',       os.path.join(FOTOS, 'pexels-shvetsa-5953589.jpg')),
]


def og(rel):
    print('== imagens sociais (1200x630) ==')
    for nome, src in OG_PAGINAS:
        im0 = Image.open(src).convert('RGB')
        esc = max(1200 / im0.width, 630 / im0.height)
        im = recortar_cobrir(im0, 1200 / 630)
        # og:image e lido por robo de rede social, que so entende JPEG/PNG.
        rel += salvar(im, os.path.join(DEST, 'og', nome), [1200],
                      qualidade=80, so_base=True)
        print('   %-18s %dx%d -> 1200x630  esc %.2fx %s'
              % (nome, im0.width, im0.height, esc,
                 'reduz' if esc < 1 else 'AMPLIA -- REPROVA'))
    return rel



# =========================================================================
#  MOMENTO 3 — a variacao B da home
#  E o UNICO dos tres momentos sem video, e e isso que impede a home de virar
#  tres telas de video seguidas (design.md §5.3).
#
#  ASSUNTO: a macro do modulo de reles. Ela e toda ARESTA DURA com FIOS EM
#  CURVA, entao traca excepcionalmente bem -- e e o unico momento da home que
#  fala de CONTROLE, que e o que a empresa vende. A sequencia de assunto da
#  home fecha nela: solar -> agua -> producao -> CONTROLE (plano.md §5.5).
#
#  A LEGENDA NAO PODE DIZER "PLC". O objeto e um modulo de 4 reles
#  SRD-05VDC-SL-C, acessorio de Arduino -- a placa diz "4 Relay Module" no
#  proprio serigrafado. A i3 programa ControlLogix e S7 e e fornecedora
#  federal: chamar isso de CLP numa legenda e afirmacao falsa sobre a
#  competencia dela, e nao um arredondamento. Por isso a foto foi DESCARTADA
#  como heroi e realocada para ca e para capabilities, onde ela e excelente
#  como o que e: fiacao de campo e borne.
# =========================================================================
MOMENTOS = [
    # `rele` SAIU DA GERACAO em 2026-08-26 (decima rodada). Ele era a figura
    # unica de capabilities -- macro de um modulo de 4 reles SRD-05VDC-SL-C,
    # acessorio de Arduino -- e a legenda dele existia justamente para NAO
    # chamar aquilo de CLP, porque nao era. A pagina agora abre `painel`.
    # ('rele', os.path.join(FOTOS, 'pexels-maltelu-5276099.jpg'), 16 / 9.0),
    #
    # A PLACA DA COBERTURA, em capabilities: interior de painel de controle
    # montado -- CLPs Siemens em trilho, disjuntores, reguas de bornes,
    # canaleta e chicote em azul, laranja e amarelo. Fonte 7008x4672, entregue
    # pelo usuario em `quadrados/final.jpg`.
    #
    # ELA E O ASSUNTO QUE A PAGINA SEMPRE DEVIA TER TIDO. "Eight disciplines,
    # one contractor" abre com painel, CLP, rede e comissionamento -- e a
    # figura mostrava um modulo de rele de bancada. Esta mostra o produto: o
    # painel montado, que e a primeira das oito disciplinas e o que a i3
    # entrega fisicamente.
    #
    # 16:9 e as tres larguras ate 2560: a placa vive numa cena FIXA de 100vh e
    # e coberta por quadrados ao rolar, entao ela e vista inteira e parada --
    # o oposto de uma faixa que passa. Largura justa apareceria na borda.
    ('painel', os.path.join(RAIZ, '..', 'quadrados', 'final.jpg'), 16 / 9.0),
    # `refinaria` SAIU da geracao em 2026-08-26 (segunda rodada). A dobra dela
    # na home foi substituida pela UNIDADE 3, em video, a pedido do usuario.
    #
    # Oil & gas nao perde representacao no site: `setor/oil-gas` continua em
    # past-performance e e um recorte da MESMA `gas.jpg`. A home passa a falar
    # do vertical por texto -- na coluna da unidade 3 e no bloco de governo --
    # e nao por imagem. A linha fica comentada porque a foto continua sendo a
    # unica de oil & gas do acervo: se a dobra voltar, ela volta com ela.
    # ('refinaria', os.path.join(FOTOS, 'gas.jpg'), 16 / 9.0),
]


def momentos(rel):
    print('== momentos da home ==')
    for nome, src, prop in MOMENTOS:
        im0 = Image.open(src).convert('RGB')
        im = recortar_cobrir(im0, prop)
        # 2560 porque o momento e full-bleed dentro do bloco e vive sob
        # parallax: ele desliza, entao a area realmente coberta e MAIOR que a
        # janela, e uma largura justa apareceria na borda no fim do curso.
        rel += salvar(im, os.path.join(DEST, 'momento', nome),
                      [1280, 1920, 2560], qualidade=76)
        print('   %-14s %dx%d -> %d:%d' % (nome, im0.width, im0.height,
                                           im.width, im.height))
    return rel


if __name__ == '__main__':
    relatorio = []
    if '--braco' in sys.argv:
        relatorio, tam = heroi(relatorio)
    # `setores()` NAO RODA MAIS, e a lista continua no arquivo de proposito.
    #
    # Ela gerava `img/setores/*` -- as cinco placas de vertical com a mascara
    # de traco -- e a UNICA consumidora era a grade da home. A grade saiu em
    # 2026-08-26 (ver a nota em build_site.py, no cabecalho da home): cinco
    # imagens numa secao contrariam a regra 7 de clean, e o card de oil & gas
    # era um recorte da mesma fotografia do momento 4, uma dobra acima.
    #
    # past-performance tem o proprio conjunto, em `img/setor/` (singular), que
    # continua sendo gerado logo abaixo por `setor_placas()`. Duas pastas com
    # nomes quase iguais e uma armadilha por si so, e agora so uma existe no
    # deploy.
    #
    # A funcao e a lista ficam: se a grade voltar, basta descomentar. Apagar
    # a receita para desligar o prato e como se perde a possibilidade.
    # relatorio = setores(relatorio)
    relatorio = setor_placas(relatorio)
    relatorio = faixas(relatorio)
    relatorio = galeria(relatorio)
    relatorio = cabecalhos(relatorio)
    relatorio = duplas(relatorio)
    relatorio = momentos(relatorio)
    relatorio = og(relatorio)
    total = sum(s for _, s in relatorio)
    print('')
    print('%d arquivos, %.2f MB' % (len(relatorio), total / 1048576))
    for p, s in sorted(relatorio, key=lambda x: -x[1])[:8]:
        print('   %6d KB  %s' % (s // 1024, p))
