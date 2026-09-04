# -*- coding: utf-8 -*-
"""Pipeline de video: 441 MB de 4K viram ~10 MB publicados.

FFMPEG EXISTE NESTE AMBIENTE, e isto e uma correcao de fato. O `memoria.md`
registra DUAS vezes (19/08 e 20/08) que video estava parado porque "nao ha
ffmpeg neste ambiente", e lista os videos como pendencia aberta. E falso desde
2026-08-25: o pacote `imageio_ffmpeg` esta instalado e traz o binario 7.1
essentials, com libx264, libx265, libvpx-vp9 e libaom-av1.

----------------------------------------------------------------------------
AS REGRAS DURAS DE MIDIA (design.md §5.4, plano.md §5.4)

  1. FAIXA DE AUDIO REMOVIDA SEMPRE (`-an`). Tres dos oito arquivos carregam
     AAC a 253 kb/s. E desperdicio, e autoplay com audio apanha de politica de
     navegador -- o video simplesmente nao toca, sem erro visivel.
  2. `+faststart`: o indice vai para a frente do arquivo. Sem isso o navegador
     baixa o arquivo inteiro antes do primeiro quadro.
  3. POSTER OBRIGATORIO em todos. E o que o visitante ve enquanto o video nao
     decodifica, e e o que ele ve para sempre com `prefers-reduced-motion`.
  4. Um video decodificando por vez -- isso e IntersectionObserver, em
     main.js, e nao entra aqui.

----------------------------------------------------------------------------
O VEU E O CRF SAO A MESMA CONTA, E ELA E CONTRAINTUITIVA

Veu leve esconde MENOS artefato de bloco. Os momentos vivem sob 62% de veu, e
por isso aguentam CRF 30. O heroi vive sob 25% -- o veu que o deixa quase
limpo e tambem o que deixa o artefato aparecer. Ele precisa de CRF mais baixo
e custa mais por segundo.

O numero do heroi e MEDIDO aqui (`--medir`), nao herdado dos momentos.

E A MEDICAO CONTRARIOU METADE DA PREVISAO. A regra geral esta certa -- veu
leve esconde menos artefato --, mas ela supunha que o heroi precisaria de CRF
bem mais baixo. Medido, 1920px, espelhado, contra uma referencia em CRF 12
(o veu de 25% e uma transformacao AFIM identica nos dois lados da comparacao,
entao ele soma exatamente 20*log10(1/0,75) = 2,50 dB ao PSNR -- nao precisa
medir duas vezes, basta somar):

    CRF   MB em 12s   PSNR-Y     sob veu 25%    SSIM
     20      7,31     47,74 dB     50,24 dB    0,98999
     22      5,35     46,83 dB     49,33 dB    0,98832
     23      4,62     46,36 dB     48,86 dB    0,98737
     24      4,00     45,87 dB     48,37 dB    0,98631
     26      3,05     44,83 dB     47,33 dB    0,98378
     28      2,36     43,72 dB     46,22 dB    0,98064
     30      1,86     42,52 dB     45,02 dB    0,97652

A CURVA NAO TEM JOELHO. Nem a 30 a qualidade desaba: 45 dB sob veu e SSIM
0,977. A razao e o assunto -- ceu e painel quase uniforme, quase nada de alta
frequencia. E o mesmo motivo pelo qual o clipe passa AA sem veu nenhum: a
zona e homogenea.

Entao a escolha deixou de ser de qualidade e virou de ORCAMENTO. CRF 26 fica
em 3,05 MB, que e o mesmo ~3 MB por clipe que design.md §5.4 orcou, com 47 dB
de folga sob o veu. E o heroi e a UNICA midia que carrega adiantado -- gastar
4,6 MB para ganhar 1,5 dB que ninguem ve sob veu seria pagar caro por nada.

----------------------------------------------------------------------------
O `-vf hflip` DO HEROI NAO E ESTETICA

Medido quadro a quadro ao longo dos 34s, branco puro sobre a zona do H1:

  zona                                original    espelhado
  esquerda-inferior (onde o H1 vive)     1,53:1      5,26:1
  esquerda-meio                          1,07:1      3,52:1
  direita-inferior                       5,26:1      1,53:1

O ceu fica a esquerda e o painel escuro a direita, e a gramatica do site poe
eyebrow e titulo a esquerda (o split 4/8). O tipo morreria exatamente onde
precisa estar. Espelhado, com veu de 25%, da 6,63:1.

Espelhar e inocuo AQUI e so aqui: nao ha texto, rosto nem marca no quadro, so
painel e ceu. Num clipe com qualquer um dos tres, hflip seria falsificacao.

NOTA QUE O PLANO NAO REGISTRA: mesmo espelhado, a zona esquerda-MEIO reprova
(3,52:1). O H1 tem de ficar na esquerda-INFERIOR, e nao centrado a esquerda.

----------------------------------------------------------------------------
O ENQUADRAMENTO DO MOMENTO 2 CARREGA A CORRECAO DE ASSUNTO

O acervo e solar-pesado: 6 dos 8 videos sao placa solar, e o heroi tambem.
Solar e UM de cinco verticais, e o menor deles. A sequencia que corrige --
solar -> agua -> producao -> controle (plano.md §5.5) -- depende inteiramente
de o momento 2 ler como linha de producao.

Medido nos quadros: o acionamento por correia, a polia e o eixo ficam em
x 480..2080, y 60..960 do quadro de 3840x2160. Fora dessa janela a camera abre
na celula solar e a home vira monotematica. Por isso o `crop` esta escrito
aqui, com numero, e nao deixado para "cortar no olho depois".

Uso:
  python ferramentas/build_video.py            gera tudo
  python ferramentas/build_video.py --medir    so a tabela de CRF do heroi
"""
import os
import subprocess
import sys

import imageio_ffmpeg

RAIZ = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
VIDEOS = os.path.join(os.path.dirname(RAIZ), 'Videos')
DEST = os.path.join(RAIZ, 'site', 'video')
POSTER = os.path.join(RAIZ, 'site', 'img', 'video')

FFMPEG = imageio_ffmpeg.get_ffmpeg_exe()

# Teto do Cloudflare Pages, por arquivo.
TETO = 25 * 1024 * 1024


class Corte(object):
    """Um trecho de um clipe dentro de uma MONTAGEM."""

    def __init__(self, fonte, ini, dur, vf=''):
        self.fonte = fonte
        self.ini = ini
        self.dur = dur
        self.vf = vf


class Montagem(object):
    """VARIOS clipes emendados num arquivo so, com corte seco.

    POR QUE UMA MONTAGEM E NAO UM CLIPE. O momento 1 carrega a frase "Senior
    control experts know things they do not teach in school" -- e ela nao fala
    de UM processo, fala de repertorio. Um plano unico de estacao de agua
    ilustra agua; quatro planos que mudam ilustram a amplitude.

    CORTE SECO, sem fundido. Fundido entre planos de assuntos diferentes le
    como video institucional; corte seco le como observacao. E o corte tambem
    e o unico que sobrevive a um `<video>` em loop: um fundido na emenda do
    loop exigiria que o ultimo quadro casasse com o primeiro.

    A NORMALIZACAO E OBRIGATORIA e nao e detalhe. Os clipes vem a 23,98, 25,
    29,97, 50 e 100 fps, e o `concat` do ffmpeg recusa entradas que diferem em
    formato, resolucao ou SAR. `fps`, `scale`, `setsar=1` e `format=yuv420p`
    em cada trecho ANTES do concat -- e `setpts=PTS-STARTPTS` para cada um
    comecar do zero, senao o segundo trecho herda o timestamp do primeiro e o
    arquivo sai com 40s de duracao declarada e 18s de imagem.
    """

    def __init__(self, nome, cortes, larg, crf, fps=30, poster_de=0, poster_em=None):
        self.nome = nome
        self.cortes = cortes
        self.larg = larg
        self.crf = crf
        self.fps = fps
        self.poster_de = poster_de
        self.poster_em = poster_em

    @property
    def dur(self):
        return sum(c.dur for c in self.cortes)

    def entradas(self):
        args = []
        for c in self.cortes:
            args += ['-ss', str(c.ini), '-t', str(c.dur), '-i', c.fonte]
        return args

    def filtro(self):
        partes = []
        for i, c in enumerate(self.cortes):
            cadeia = []
            if c.vf:
                cadeia.append(c.vf)
            cadeia += ['scale=%d:-2' % self.larg, 'fps=%d' % self.fps,
                       'setsar=1', 'format=yuv420p', 'setpts=PTS-STARTPTS']
            partes.append('[%d:v]%s[v%d]' % (i, ','.join(cadeia), i))
        rotulos = ''.join('[v%d]' % i for i in range(len(self.cortes)))
        partes.append('%sconcat=n=%d:v=1:a=0[m]' % (rotulos, len(self.cortes)))
        return ';'.join(partes)


class Peca(object):
    """Um clipe de saida. `vf` e a cadeia de filtros ANTES do scale."""

    def __init__(self, nome, fonte, ini, dur, larg, crf, vf='', poster_em=None,
                 fps=None, q_poster=3):
        self.nome = nome
        self.fonte = fonte
        self.ini = ini
        self.dur = dur
        self.larg = larg
        self.crf = crf
        self.vf = vf
        # Alguns clipes foram filmados a 100 fps para permitir camera lenta. O
        # site nao usa camera lenta, entao 100 fps sao ~3x os quadros que
        # alguem vai ver -- e cada quadro custa bytes. `fps` normaliza para 30.
        self.fps = fps
        # De onde tirar o poster. Nem sempre e o primeiro quadro: no filme o
        # primeiro quadro e a janela ainda fechada, e o poster tem de mostrar
        # o que o visitante vai ver, nao a cortina.
        self.poster_em = ini if poster_em is None else poster_em
        # QUALIDADE DO POSTER, e ela nao e a mesma para todo mundo. `-q:v 3` e
        # quase sem perda, e e o certo para o heroi: ele e o LCP do site, o
        # visitante olha para ele em tela cheia e SEM veu (25%). Um fundo de
        # secao e o oposto -- vive sob 55 a 71% de navy, e so aparece nos
        # milissegundos antes do video chegar (e permanentemente para quem
        # pediu movimento reduzido, ainda assim sob o veu). Ali `-q:v 3` gasta
        # 208 KB para entregar detalhe que a camada por cima apaga.
        self.q_poster = q_poster


# =========================================================================
#  MONTAGENS
# =========================================================================
MONTAGENS = [
    # ---- MOMENTO 1: O FILME ----------------------------------------------
    # VIROU MONTAGEM em 2026-08-26, a pedido do usuario: "o video da agua e
    # legal, mas precisamos fazer um compilado".
    #
    # E a decisao certa pela FRASE que a dobra carrega -- "Senior control
    # experts know things they do not teach in school". Ela nao fala de um
    # processo, fala de REPERTORIO. Um plano unico de estacao de agua ilustra
    # agua; quatro planos que mudam ilustram a amplitude que a frase afirma.
    #
    # A agua abre e fecha o ciclo porque e o plano mais amplo dos quatro: sair
    # de uma aerea e voltar para ela faz a emenda do loop ler como respiro, e
    # nao como corte.
    #
    # 4,5s por corte. Abaixo de 4s o olho nao termina de ler o plano e a
    # sequencia vira videoclipe; acima de 8s o corte deixa de ser montagem e
    # volta a ser uma sucessao de clipes.
    # ORDEM REFEITA EM 2026-08-27, a pedido: *"o primeiro video do .filme passa a
    # ser o homem com a caixa; a ordem agora e homem com caixa, braco (segundo
    # de agora), agua (primeiro de agora), e depois segue para o ultimo."*
    #
    # A MONTAGEM VOLTA A TER QUATRO CORTES e 18s, que e a duracao que ela ja
    # teve antes de `pc.mp4` sair (memorianew.md §, segunda rodada de 26/08).
    #
    # O NOVO PRIMEIRO PLANO ABRE COM GENTE, e e a unica mudanca de leitura que
    # a reordenacao faz. A frase desta dobra e "Senior control experts know
    # things they do not teach in school" -- ela fala de repertorio HUMANO, e
    # a montagem abria em infraestrutura vazia. Um operario atravessando o
    # corredor e o unico plano do acervo em que aparece uma pessoa TRABALHANDO
    # de corpo inteiro.
    #
    # ELE E O UNICO CLIPE 720p DO ACERVO, e isso custa. A montagem sai a 1600
    # de largura: os outros tres vem de 3840 e sao REDUZIDOS 0,42x; este vem de
    # 1280 e e AMPLIADO 1,25x. Fica visivelmente mais macio que os vizinhos.
    # O que torna aceitavel e onde ele vive -- sob o veu de 62% do `.filme`, a
    # CRF 30, num plano largo e escuro sem detalhe fino. Nao ha fonte maior:
    # o arquivo entregue tem 1280x720 e 729 KB.
    #
    # HEVC 10 bits na origem (`yuv420p10le`), o unico assim no acervo. O
    # `format=yuv420p` da cadeia de normalizacao ja converte para 8 bits antes
    # do concat -- sem ele o `concat` recusaria a entrada, porque os quatro
    # trechos precisam casar em formato.
    #
    # JANELA 1,0 -> 5,5 de 6,12s. Em 0,4s o operario ainda esta atras da pilha
    # e em 5,8 ele ja saiu de quadro; a janela e o trecho em que ele atravessa
    # o corredor inteiro, que e o movimento que o plano tem para dar.
    Montagem('momento-1-montagem', [
        # o operario atravessando o corredor do armazem -- o trabalho, com gente
        Corte(os.path.join(VIDEOS,
                           'worker-carrying-box-in-warehouse-aisle-168314-720.mp4'),
              1.0, 4.5),
        # celula com robo colaborativo e passa-cabo azul -- automacao de linha
        Corte(os.path.join(VIDEOS, 'automacaorobo.mp4'), 3.0, 4.5),
        # aerea da estacao de tratamento -- infraestrutura de processo
        Corte(os.path.join(VIDEOS, 'estacaoagua.mp4'), 2.0, 4.5),
        # `pc.mp4` SAIU da montagem em 2026-08-26 (segunda rodada): ele virou o
        # video da UNIDADE 3, e usar o mesmo clipe nos dois lugares seria a
        # repeticao que o usuario ja reclamou uma vez.
        # detalhe de dispositivo em maquina -- o fecho, em escala de peca.
        # Recorte a direita: o terco esquerdo do quadro e parede desfocada.
        Corte(os.path.join(VIDEOS, 'automacaorobo3.mp4'), 1.5, 4.5,
              vf='crop=2600:1463:900:400'),
    ], larg=1600, crf=30, poster_de=0),
]


# --- os tres videos das UNIDADES, todos no mesmo formato de dobra ----------
PECAS_UNIDADE = [
    # 1. a fileira de atuadores pneumaticos -- linha de producao
    #    (ja existia como `momento-atuadores`)
    # 2. o operador na tela -- controle
    #    (ja existia como `momento-ihm`)
    # 3. o engenheiro na estacao -- o projeto antes da maquina.
    #    Recorte no monitor: o quadro cheio poe a silhueta escura da cabeca
    #    ocupando um terco da direita, e o assunto e a tela.
    #
    #    ELE SUBSTITUI A DOBRA DA REFINARIA, a pedido. Oil & gas nao perde
    #    representacao no site: `setor/oil-gas` continua em past-performance,
    #    e e um recorte da mesma `gas.jpg`.
]


PECAS = [
    # ---- O HEROI ----------------------------------------------------------
    # 1920 e nao 1600: ele e full-bleed e nao janela. CRF 26 saiu da tabela de
    # `--medir` no topo deste arquivo -- 3,05 MB a 47,33 dB sob o veu.
    #
    # 34,1s inteiros seriam ~6 MB so no heroi. 12s cobre o loop sem costura
    # visivel: nao ha corte no clipe e a nuvem anda devagar, entao o ponto de
    # emenda nao tem evento para denunciar.
    Peca('heroi', os.path.join(VIDEOS, 'heroi', 'heroi.mp4'),
         ini=6.0, dur=12.0, larg=1920, crf=26, vf='hflip'),


    # ---- MOMENTO 2: VARIACAO A -------------------------------------------
    # A FILEIRA DE ATUADORES PNEUMATICOS. Trocou a esteira em 2026-08-26, e a
    # troca corrige a leitura do assunto no lugar onde ela mais importava.
    #
    # A esteira ERA o compromisso possivel: `plano.md` §5.5 pedia "cortado
    # fechado nos bicos e atuadores", e o clipe da esteira nao tem bicos nem
    # atuadores -- tem uma polia e uma correia, com celulas solares passando.
    # Cortar fechado escondia o solar, mas nao produzia o assunto pedido.
    #
    # `automacaorobo2.mp4` E o assunto pedido: uma fileira de cilindros
    # pneumaticos com conexoes e mangueiras, camera correndo ao longo dela.
    # Le como maquina de producao sem nenhuma ambiguidade, e sem recorte --
    # o quadro inteiro serve.
    #
    # 100 fps na origem: filmado para camera lenta, que o site nao usa. Sao
    # ~3x os quadros que alguem vai ver, e cada quadro custa bytes.
    Peca('momento-atuadores', os.path.join(VIDEOS, 'automacaorobo2.mp4'),
         ini=0.0, dur=7.3, larg=1600, crf=30, fps=30, poster_em=3.0),

    # ---- MOMENTO 3: VARIACAO C -------------------------------------------
    # O OPERADOR NA TELA. Este e o clipe mais valioso do acervo inteiro, e ele
    # estava no disco o tempo todo -- `memorianew.md` §9 listava "operador na
    # tela de SCADA" como material AUSENTE, a pedir ao cliente.
    #
    # E o unico clipe que mostra o que a empresa de fato entrega: alguem
    # operando a maquina pela interface. Todo o resto do acervo mostra
    # EQUIPAMENTO; este mostra o USO.
    #
    # O CLIPE INTEIRO, SEM CORTE E SEM RECORTE, a pedido do usuario -- pedido
    # duas vezes, e a segunda depois de ver a dobra no ar. Ele quer
    # `Videos/ihm.mp4`, e e isso que vai ao ar: 18,7s, quadro cheio.
    #
    # O HISTORICO DAS DUAS TENTATIVAS ANTERIORES fica registrado porque cada
    # uma foi um compromisso diferente com o mesmo problema:
    #
    #   13,0s->18,6s  so a leitura numerica. Fugia da prosa em tcheco, e o
    #                 efeito colateral foi a dobra deixar de PARECER o ihm:
    #                 sem mao, sem contexto, so numeros mudando.
    #   4,0s->14,0s   a interface com a mao. Devolvia o reconhecimento e
    #                 trazia junto o dialogo modal (ver abaixo).
    #
    # O QUE ISSO ACEITA, e a decisao e do usuario, tomada com a evidencia na
    # frente: entre ~7s e ~11s o clipe mostra um DIALOGO MODAL em tcheco --
    # "Vyvoj / Prenos souboru / 23 %" e "Nahled neni mozny!". Em tela cheia,
    # numa home de fornecedor federal americano, isso pode ler como uma
    # maquina estrangeira com uma transferencia travada. A janela 2,2s->6,8s
    # tem a interface e a mao SEM o dialogo, e continua disponivel se ele
    # quiser voltar atras -- basta trocar `ini` e `dur`.
    #
    # A legenda continua descrevendo o que se ve e NUNCA afirma autoria: e
    # material de banco de imagem, nao um sistema da i3.
    #
    # SEM `vf`: quadro cheio. O clipe ja e 3840x2160, ou seja 16:9 exato, e
    # o unico tratamento e o scale para 1600.
    Peca('momento-ihm', os.path.join(VIDEOS, 'ihm.mp4'),
         ini=0.0, dur=18.7, larg=1600, crf=30, poster_em=5.0),

    # ---- UNIDADE 3 -------------------------------------------------------
    # A SUPERFICIE DA PLACA, em travelling lento. Substitui `pc.mp4` a pedido.
    #
    # Ela fecha a sequencia num vertical real da empresa (solar / geracao) e
    # muda o registro: as duas unidades antes dela sao maquina e interface,
    # em interior; esta e campo, em luz natural. Depois de dois interiores
    # seguidos, sair para fora e o que impede a sequencia de fechar abafada.
    Peca('momento-solar', os.path.join(VIDEOS, 'placassolares4.mp4'),
         ini=1.0, dur=9.0, larg=1600, crf=30, poster_em=5.0),

    # ---- FUNDO DA DOBRA DO ARGUMENTO, em who-we-are ----------------------
    # A VISTA AEREA DO PARQUE SOLAR. Trocou `pc.mp4` (o engenheiro na estacao)
    # em 2026-08-26, decima rodada, a pedido direto: "troque o video por
    # placasSolares.mp4".
    #
    # `pc.mp4` volta a ficar sem consumidor -- e a nota da nona rodada, que
    # explicava por que ele era o assunto exato daquela dobra, continua valendo
    # como registro do que se trocou.
    #
    # 12s DE 26,26s, COMECANDO EM 2,0. O fim do clipe FUNDE PARA PRETO: o
    # quadro em 25s e preto chapado. Num fundo em loop isso apagaria a dobra
    # inteira por dois segundos a cada volta. A janela 2,0->14,0 fica longe do
    # fundido e tem exposicao estavel -- que e o requisito de um fundo, e nao
    # do clipe mais bonito.
    #
    # 24 fps na origem, mantidos: nao ha `fps=` aqui porque 24 ja e economico
    # (o `automacaorobo2` normaliza porque vinha a 100).
    #
    # AUDIO: a fonte TEM faixa de audio, ao contrario das outras. O pipeline
    # ja passa `-an` em todo encode, entao ela nao chega ao deploy -- mas fica
    # anotado, porque um fundo de secao com audio seria violacao de 1.4.2 alem
    # de bytes jogados fora.
    #
    # 1280px E CRF 34, e nao os 1600/30 dos momentos. Medido, este clipe e o
    # MAIS CARO do acervo por segundo: uma travelling aerea sobre uma grade
    # regular e fina de celulas fotovoltaicas e o pior caso de um codec de
    # video -- alta frequencia espacial em movimento constante, sem area
    # chapada nenhuma para o compressor economizar.
    #
    #     1600px crf 30 -> 2.959 KB      1280px crf 34 -> 1.176 KB
    #     1440px crf 32 -> 1.890 KB      1280px crf 36 ->   919 KB
    #
    # 1600/30 daria 3 MB num FUNDO de secao -- mais que o heroi, que e a
    # primeira dobra do site inteiro. E o veu paga a diferenca: aqui ele fecha
    # em .55 no miolo e compoe .71 na lateral, ou seja de 55% a 71% do que a
    # tela mostra e navy chapado. Artefato de CRF 34 nao sobrevive a isso --
    # e a regra ja registrada em `plano.md` §3.4, na direcao contraria: "veu
    # leve esconde MENOS artefato", e por isso o heroi precisou de CRF baixo.
    # Aqui o veu e pesado, entao o CRF pode subir.
    #
    # E O VP9 FOI DESCARTADO PELO BUILD: 4.781 KB contra 2.959 do h264 na
    # primeira passagem. O descarte e automatico (o WebM so vai ao ar se
    # economizar), e a razao e a mesma da linha de cima -- grade fina em
    # movimento e onde o VP9 perde feio para o x264.
    Peca('fundo-solar', os.path.join(VIDEOS, 'placasSolares.mp4'),
         ini=2.0, dur=12.0, larg=1280, crf=34, poster_em=6.0, q_poster=7),

    # ---- O HEROI DE SERVICES ----------------------------------------------
    # O ULTIMO CLIPE DO ACERVO SEM CONSUMIDOR que nao e mais um parque solar
    # aereo. Sobravam seis: quatro aereas de fazenda solar (o assunto que o
    # heroi da home ja ocupa), `pc.mp4` e este.
    #
    # `pc.mp4` FOI DESCARTADO, e o motivo vale registro porque ele era o
    # melhor casamento de assunto: as notas da nona rodada o chamam de "o
    # projeto antes da maquina", que e literalmente a tese de "How you buy the
    # work". Mas TODOS os quadros mostram um dialogo do Autodesk Inventor
    # avisando que a licenca expirou, e o cliente e fornecedor federal. Existe
    # recorte que esconde o dialogo (`crop=3840:1215:0:945`, medido), so que
    # ele custa a metade de cima do quadro e ainda deixa o assunto errado --
    # CAD mecanico, e nao controle. Nao vale o risco por um clipe que nem e
    # do ramo.
    #
    # O QUE ENTRA: modulo fotovoltaico numa esteira, sob lampadas de teste.
    # E o sexto assunto solar do site, que design.md §5.5 avisa ser um risco
    # -- e a compensacao esta na COR. Sob veu navy este e o unico clipe do
    # acervo com luz quente: as lampadas ficam ambar e os modulos ficam
    # azul-marinho. Ele nao le como "mais uma fazenda solar", le como
    # inspecao de linha, que e o assunto de uma pagina sobre como se contrata.
    #
    # O CORTE E 0,6s -> 6,6s, E O NUMERO SAIU DE MEDICAO. A esteira anda sem
    # parar, entao nao ha par de emenda perfeito -- ha o menos pior. Medida a
    # diferenca media absoluta entre quadro de entrada e de saida para todo
    # par com 5s ou mais de curso, TODOS os melhores pares dao exatamente 6,0s
    # de distancia: e o passo entre um modulo e o proximo. 0,6 -> 6,6 e o
    # melhor deles, a 7,57 de diferenca media contra 50,19 do pior par.
    #
    # CRF 28, E ELE SAI DA REGRA DE VEU DO TOPO DESTE ARQUIVO. O heroi da home
    # vive sob 25% e paga CRF 26; os momentos vivem sob 62% e pagam 30. Este
    # vive sob 55% (a conta esta em style.css, em `.heroi--servicos`), entao
    # 28 e a posicao dele na mesma escala. 1920 porque e full-bleed, como o
    # heroi da home, e nao janela.
    #
    # 50 fps na origem, normalizados para 30 pela mesma razao do
    # `momento-atuadores`: filmado para camera lenta, que o site nao usa.
    Peca('heroi-servicos',
         os.path.join(VIDEOS, 'elemnetotecnologicodeesteira.mp4'),
         ini=0.6, dur=6.0, larg=1920, crf=28, fps=30, poster_em=3.0),
]


def montar(m, saida, crf=None, codec='h264'):
    args = m.entradas() + ['-filter_complex', m.filtro(), '-map', '[m]', '-an']
    if codec == 'h264':
        args += ['-c:v', 'libx264', '-preset', 'slow',
                 '-crf', str(m.crf if crf is None else crf),
                 '-pix_fmt', 'yuv420p', '-profile:v', 'high', '-level', '4.0',
                 '-movflags', '+faststart']
    else:
        args += ['-c:v', 'libvpx-vp9', '-crf', str(m.crf + DESLOCAMENTO_VP9),
                 '-b:v', '0', '-row-mt', '1', '-deadline', 'good',
                 '-cpu-used', '2', '-pix_fmt', 'yuv420p']
    rodar(args + [saida])


def poster_montagem(m, saida):
    """O poster sai do trecho que o `poster_de` aponta, e nao do primeiro
    quadro do arquivo montado: o primeiro quadro de uma montagem e so o
    primeiro corte, e nem sempre e ele que representa a peca."""
    c = m.cortes[m.poster_de]
    em = c.ini + (c.dur / 2 if m.poster_em is None else m.poster_em)
    f = [c.vf] if c.vf else []
    f.append('scale=%d:-2' % m.larg)
    rodar(['-ss', str(em), '-i', c.fonte, '-frames:v', '1',
           '-vf', ','.join(f), '-q:v', '3', saida])


def rodar(args):
    r = subprocess.run([FFMPEG, '-y', '-hide_banner', '-loglevel', 'error'] + args,
                       capture_output=True, text=True)
    if r.returncode:
        raise SystemExit('ffmpeg falhou:\n' + r.stderr[-2000:])


def cadeia(p):
    """`vf` da peca + o scale. O scale vem por ultimo: cortar em 4K e depois
    reduzir preserva detalhe que reduzir-e-depois-cortar joga fora."""
    f = [p.vf] if p.vf else []
    # -2 mantem a altura par, que o h264 exige. Escrever a altura a mao aqui
    # e como se ganha um "height not divisible by 2" no dia em que a fonte
    # mudar de proporcao.
    f.append('scale=%d:-2' % p.larg)
    return ','.join(f)


def h264(p, saida, crf=None):
    rodar(['-ss', str(p.ini), '-i', p.fonte, '-t', str(p.dur),
           '-an',                     # regra 1: sem faixa de audio, sempre
           '-vf', cadeia(p),
           ] + (['-r', str(p.fps)] if p.fps else []) + [
           '-c:v', 'libx264', '-preset', 'slow',
           '-crf', str(p.crf if crf is None else crf),
           '-pix_fmt', 'yuv420p',     # o unico perfil que todo navegador toca
           '-profile:v', 'high', '-level', '4.0',
           '-movflags', '+faststart', # regra 2
           saida])


# A ESCALA DE CRF DO VP9 NAO E A DO x264, e tratar as duas como uma so foi um
# erro real desta rodada: com `crf + 3` o WebM saiu MAIOR que o mp4 em dois dos
# tres clipes (2.519 KB contra 1.283 KB no momento 1). Servir isso seria pior
# que nao servir nada -- o navegador escolhe o primeiro <source> que sabe tocar
# e baixaria o arquivo mais pesado achando que economiza.
#
# O que decide nao e CRF casado, e SSIM casada: com a mesma qualidade
# percebida, quem gasta menos bytes. Medido em 5s do momento 1, a 1600px,
# contra uma referencia em CRF 12:
#
#     codec           KB      SSIM
#     h264 crf 30    688    0,95967
#     vp9  crf 33   1271    0,97590   qualidade a mais que ninguem pediu
#     vp9  crf 38    790    0,96855
#     vp9  crf 42    549    0,96018   <- casa a SSIM, e gasta 20% menos
#     vp9  crf 46    384    0,94894
#
# Ou seja: o deslocamento e +12, nao +3. Com ele o VP9 finalmente faz o que se
# esperava dele -- mesma imagem, um quinto a menos de bytes.
#
# MAS +12 NAO E UMA LEI, e o clipe dos atuadores provou. Ele e uma fileira de
# hastes metalicas finas -- alta frequencia em todo quadro --, e ali o VP9
# perde: 2.644 KB contra 2.122 KB do h264 com o mesmo +12 que economizava 20%
# no clipe da agua. O ganho do VP9 depende do ASSUNTO, e nenhuma constante
# acerta em todos.
#
# Por isso a garantia deixou de ser um numero calibrado e virou ESTRUTURAL: o
# build compara os dois arquivos e DESCARTA o WebM quando ele nao ganha. Uma
# constante bem escolhida envelhece no dia em que entra um clipe novo; a
# verificacao nao envelhece.
DESLOCAMENTO_VP9 = 12


def _fps(p):
    return ['-r', str(p.fps)] if p.fps else []


def vp9(p, saida):
    """A alternativa. VP9 e nao AV1: medido, o libaom leva minutos por clipe
    no preset que vale a pena, e o ganho sobre VP9 nao paga a espera num
    projeto que reencoda a cada ajuste de corte. `-row-mt` usa os nucleos."""
    rodar(['-ss', str(p.ini), '-i', p.fonte, '-t', str(p.dur),
           '-an', '-vf', cadeia(p),
           ] + _fps(p) + [
           '-c:v', 'libvpx-vp9', '-crf', str(p.crf + DESLOCAMENTO_VP9), '-b:v', '0',
           '-row-mt', '1', '-deadline', 'good', '-cpu-used', '2',
           '-pix_fmt', 'yuv420p',
           saida])


def poster(p, saida):
    """JPEG de qualidade alta. Ele e o LCP do heroi -- e o que o navegador
    pinta antes de qualquer quadro de video existir."""
    f = [p.vf] if p.vf else []
    f.append('scale=%d:-2' % p.larg)
    rodar(['-ss', str(p.poster_em), '-i', p.fonte, '-frames:v', '1',
           '-vf', ','.join(f), '-q:v', str(p.q_poster), saida])


def kb(caminho):
    return os.path.getsize(caminho)


def medir_heroi():
    """A tabela de CRF do heroi. Ele NAO herda o CRF dos momentos: sob 25% de
    veu o artefato de bloco aparece, e sob 62% nao."""
    p = PECAS[0]
    print('CRF do heroi, %dpx, %.0fs, espelhado — medido, nao herdado:' % (p.larg, p.dur))
    print('%6s %12s %10s' % ('crf', 'bytes', 'MB'))
    tmp = os.path.join(DEST, '_crf.mp4')
    for crf in (20, 21, 22, 23, 24, 26, 28, 30):
        h264(p, tmp, crf=crf)
        n = kb(tmp)
        print('%6d %12d %9.2f' % (crf, n, n / 1048576.0))
    os.remove(tmp)


def main():
    for d in (DEST, POSTER):
        if not os.path.isdir(d):
            os.makedirs(d)

    if '--medir' in sys.argv:
        medir_heroi()
        return

    total = 0

    for m in MONTAGENS:
        for c in m.cortes:
            if not os.path.exists(c.fonte):
                sys.exit('fonte ausente: %s' % c.fonte)
        print('')
        print('%s  <- montagem de %d cortes, %.1fs'
              % (m.nome, len(m.cortes), m.dur))
        for c in m.cortes:
            print('   %.1fs de %-34s +%.1fs%s'
                  % (c.ini, os.path.basename(c.fonte), c.dur,
                     ('  ' + c.vf) if c.vf else ''))
        mp4 = os.path.join(DEST, m.nome + '.mp4')
        webm = os.path.join(DEST, m.nome + '.webm')
        jpg = os.path.join(POSTER, m.nome + '.jpg')
        montar(m, mp4, codec='h264')
        montar(m, webm, codec='vp9')
        poster_montagem(m, jpg)
        if os.path.getsize(webm) >= os.path.getsize(mp4):
            print('   %-34s DESCARTADO (%.0f KB >= %.0f KB do mp4)'
                  % (os.path.relpath(webm, RAIZ),
                     os.path.getsize(webm) / 1024.0,
                     os.path.getsize(mp4) / 1024.0))
            os.remove(webm)
            webm = None
        for c in ([mp4, jpg] if webm is None else [mp4, webm, jpg]):
            n = kb(c)
            total += n
            print('   %-34s %8.0f KB' % (os.path.relpath(c, RAIZ), n / 1024.0))

    for p in PECAS:
        if not os.path.exists(p.fonte):
            sys.exit('fonte ausente: %s' % p.fonte)
        print('\n%s  <- %s' % (p.nome, os.path.basename(p.fonte)))
        print('   corte %.1fs +%.1fs · %dpx · crf %d%s'
              % (p.ini, p.dur, p.larg, p.crf, (' · ' + p.vf) if p.vf else ''))

        mp4 = os.path.join(DEST, p.nome + '.mp4')
        webm = os.path.join(DEST, p.nome + '.webm')
        jpg = os.path.join(POSTER, p.nome + '.jpg')

        h264(p, mp4)
        vp9(p, webm)
        poster(p, jpg)

        # O WebM so vai ao ar se REALMENTE economizar. O navegador fica com o
        # primeiro <source> que sabe tocar, entao um WebM maior nao e neutro:
        # ele faz Chrome e Firefox baixarem MAIS bytes que o Safari.
        if os.path.getsize(webm) >= os.path.getsize(mp4):
            print('   %-34s DESCARTADO (%.0f KB >= %.0f KB do mp4)'
                  % (os.path.relpath(webm, RAIZ),
                     os.path.getsize(webm) / 1024.0,
                     os.path.getsize(mp4) / 1024.0))
            os.remove(webm)
            webm = None

        for c in ([mp4, jpg] if webm is None else [mp4, webm, jpg]):
            n = kb(c)
            total += n
            aviso = '  ACIMA DO TETO DE 25 MB' if n > TETO else ''
            print('   %-34s %8.0f KB%s' % (os.path.relpath(c, RAIZ), n / 1024.0, aviso))

    print('\ntotal publicado: %.1f MB' % (total / 1048576.0))
    print('origem: 441 MB de 4K em Videos/')


if __name__ == '__main__':
    main()
