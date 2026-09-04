# -*- coding: utf-8 -*-
"""Conteudo das nove paginas do site i3Automations.

build_paginas.py tem o CHROME (nav, rodape, cabecalho, componentes repetidos);
este arquivo tem o CONTEUDO. A separacao existe porque as duas coisas mudam por
motivos diferentes: o chrome muda quando o sistema de design muda, o conteudo
muda quando o cliente tem novidade.

TOM DE VOZ (design.md §4). O site atual do cliente esta escrito em jargao de
marketing — "revolutionize", "cutting-edge", "game-changing", "unparalleled".
O §4.1 proibe todos. O FATO de cada frase foi preservado; a EMBALAGEM foi
refeita em registro declarativo, primeira pessoa do plural, prova antes de
promessa. Nenhum numero, nome de cliente ou credencial foi inventado: tudo o
que esta aqui veio do site atual ou de memoria.md.

Uso: python ferramentas/build_site.py
"""
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from build_paginas import (
    pagina, cabecalho, cta, imagem, marca_nav, marca_lockup, lente, lista_capacidades,
    grade_plataformas, grade_setores, prancha, registro_obras, ofertas, contratos, feixe,
    cobertura,
    traco, unidade, marcas_certificacao,
    diagrama,
    secao_com_foto, NUMEROS, peca, cota_peca, sitemap, robots, cabecalhos_deploy,
    redirecionamentos_deploy, htaccess_deploy,
    GOVERNO,
    CONTATO_CTA, TEL_VENDAS, TEL_SUPORTE, EMAIL, WHATSAPP, REDES, DEST,
)



# ----------------------------------------------------------------- BRACO
#  O robo de 6 eixos. Nao carrega imagem: a geometria e gerada em js/braco.js a
#  partir de circulos, e as juntas se movem por cinematica direta na GPU. O
#  <div> estatico so aparece quando nao ha WebGL2 -- e ai ele usa a mascara de
#  traco do MESMO braco, para o desenho ser o mesmo.
#
#  SAIU DO HEROI E FOI PARA O 404 em 2026-08-25 (design.md §8). O texto do
#  `aria-label` mudou junto: ele prometia que "o ponteiro acende o desenho em
#  DOURADO", e o dourado saiu do site -- vive so dentro do logo. O aceso agora
#  e `--azul-luz`. Um rotulo de acessibilidade que descreve uma cor que a peca
#  nao tem e pior que um rotulo generico: quem depende dele nao tem como
#  conferir.
BRACO = (
    '<div class="braco" data-braco role="img" '
    'aria-label="Interactive line drawing of a six-axis industrial robot arm '
    'at work: drag to orbit it, and the pointer lights the drawing.">'
    '<canvas class="braco__tela"></canvas>'
    '<div class="braco__estatico" aria-hidden="true"></div>'
    '</div>'
)

# =========================================================================
#  HOME
#
#  A ESTRUTURA VIROU UM SISTEMA em 2026-08-26 (segunda rodada), a pedido do
#  usuario depois de ver a dobra "The line does not care how clever the code
#  is" no ar:
#
#      video pequeno + um texto  ->  video em tela cheia + outro texto
#
#  ...repetido TRES vezes, e e nele que a informacao do site vive. Cada
#  unidade sai de `unidade()`, em build_paginas.py, que carrega a nota sobre a
#  contradicao com `design.md` §5 e sobre o que a repeticao custa.
#
#      1  heroi          video full-bleed, veu 25%          solar
#      2  numeros        branco, entrando um a um
#      3  texto          branco    eyebrow -> H2 -> CTA
#      4  a TESE         QUENTE    a faixa morna que faltava
#      5  o FILME        montagem de 3 cortes                agua/robo/maquina
#      6  texto          branco    abre as tres unidades
#      7  UNIDADE 1      atuadores pneumaticos   caixa a ESQ producao
#      8  UNIDADE 2      operador na tela        caixa a DIR controle
#      9  UNIDADE 3      engenheiro na estacao   caixa a ESQ projeto
#     10  plataformas    off-white
#     11  governo        --azul-bloco
#     12  CTA final      --azul-bloco
#     13  rodape         revelado por sticky
#
#  O RITMO DE SUPERFICIE volta a alternar. Antes desta rodada a home corria
#  escuro -> escuro -> escuro -> escuro do filme ate a unidade 3, sem uma
#  unica superficie clara no meio -- 1.010vh de campo escuro continuo.
#
#  OS BLOCOS DE TEXTO SOLTOS ENTRE OS MOMENTOS SAIRAM, e nao por economia: a
#  coluna de cada unidade E o bloco de texto, no mesmo formato de sempre
#  (eyebrow -> H2 -> paragrafo -> CTA) e com o mesmo destino. Manter os dois
#  daria DEZ blocos de texto na home -- quatro soltos mais seis dentro das
#  unidades -- para uma pagina cuja regra numero 1 e "uma ideia por dobra".
#
#  A DOBRA DA REFINARIA SAIU, substituida pela unidade 3. Oil & gas nao perde
#  representacao no site: `setor/oil-gas` continua em past-performance, e e um
#  recorte da mesma `gas.jpg`. A home passa a falar de oil & gas por texto --
#  na unidade 3 e no bloco de governo -- e nao por imagem.
#
#  A SEQUENCIA DE ASSUNTO continua cobrindo a empresa, e agora com um video em
#  cada etapa em vez de um por vertical:
#
#      heroi     painel solar e nuvem            o campo
#      filme     agua, celula com robo, maquina  a amplitude
#      unidade 1 atuadores pneumaticos           a linha
#      unidade 2 operador na tela                o controle
#      unidade 3 engenheiro na estacao           o projeto
# =========================================================================
def home():
    corpo = '''
<section class="heroi" id="top">
  <!-- O HEROI E A UNICA MIDIA AUTORIZADA A CARREGAR ADIANTADO.
       As tres unidades e o filme ficam em `preload="none"` e so tocam quando
       entram na tela; este toca desde o inicio, porque ele E a primeira dobra.

       `poster` com `fetchpriority="high"`: o poster e o LCP. Ele pinta antes
       de qualquer quadro de video existir, e e tambem o que fica para sempre
       na tela de quem pede movimento reduzido. -->
  <!-- `id` E NAO `data-heroi-video`: o gancho da pausa virou `data-pausa`
       apontando para um `id` quando o modulo 14 passou a servir mais de um
       video (who-we-are ganhou fundo em video). O atributo antigo ficou sem
       leitor nenhum -- e gancho morto no HTML e o que faz o proximo leitor
       procurar o codigo que o consome durante dez minutos. -->
  <video class="heroi__midia" id="heroi-video"
         autoplay muted loop playsinline preload="auto"
         poster="img/video/heroi.jpg"
         aria-label="Solar panel surface reflecting moving clouds.">
    <source src="video/heroi.webm" type="video/webm">
    <source src="video/heroi.mp4" type="video/mp4">
  </video>
  <div class="heroi__veu" aria-hidden="true"></div>

  <div class="heroi__container">
    <div class="heroi__texto">
      <h1 class="heroi__titulo">
        <span class="entra-linha" style="--i:0">Good control strategy</span>
        <span class="entra-linha" style="--i:1">beats more expensive</span>
        <span class="entra-linha" style="--i:2">instrumentation.</span>
      </h1>
      <p class="heroi__apoio">
        <svg class="heroi__regua" viewBox="0 0 2 100" preserveAspectRatio="none"
             aria-hidden="true" focusable="false">
          <line x1="1" y1="0" x2="1" y2="100" pathLength="100"/>
        </svg>
        Control panels, PLC and SCADA integration, instrumentation
        and commissioning. Lakewood Ranch, Florida, in the field since 2000.
      </p>
    </div>
  </div>

  <!-- WCAG 2.2.2: conteudo em movimento que comeca sozinho, dura mais de 5
       segundos e divide a tela com outro conteudo precisa de pausa. -->
  <button class="heroi__pausa" type="button" data-pausa="heroi-video"
          aria-pressed="false" aria-label="Pause background video">
    <svg class="heroi__pause" viewBox="0 0 16 16" aria-hidden="true"><rect x="3" y="2" width="3.6" height="12"/><rect x="9.4" y="2" width="3.6" height="12"/></svg>
    <svg class="heroi__play" viewBox="0 0 16 16" aria-hidden="true"><path d="M3.5 2l10 6-10 6z"/></svg>
  </button>
</section>

<!-- DOBRAS 2 e 3 — A ABERTURA, agora UMA seção com três movimentos.

     O QUE ESTAVA ERRADO, e o usuário mandou um print da área: eram DUAS
     seções com a mesma estrutura em sequência — eyebrow à esquerda, título e
     parágrafo à direita — e a única diferença entre elas era o tom do fundo.
     Liam como o mesmo bloco duas vezes. Três defeitos somados:

       1. a coluna esquerda ficava ~430px VAZIA sob um eyebrow de três
          palavras, porque o split 4/8 supõe uma coluna direita alta e aqui
          ela tinha só título e um parágrafo;
       2. sobrava vão morto sob cada parágrafo — 65vh e 55vh de seção para
          ~40vh e ~35vh de conteúdo;
       3. duas estruturas idênticas coladas não dão ao olho nada que as
          distinga.

     O QUE INTEGRA AS DUAS é a faixa de plataformas no MEIO, e ela integra
     porque usa o MESMO grid 4/8: o rótulo dela alinha com os dois eyebrows,
     os chips alinham com os dois títulos. Três linhas de rótulo à esquerda e
     três blocos à direita passam a ler como uma coluna, e não como dois
     blocos e um enfeite.

     E ela devolve conteúdo que a home tinha perdido: as certificações saíram
     daqui quando a grade de plataformas foi substituída pelas oito
     disciplinas. O chip com ponto cheio diz "somos certificados"; o chip liso
     diz "operamos". É a mesma distinção da escada de capabilities, compacta.

     UMA superfície só (`--sup-2`), porque agora é uma seção só. O ritmo
     continua alternando: navy do herói → esta faixa clara → o bloco escuro
     do filme. -->
<section class="secao secao--intro">
  <div class="container">
    <div class="bloco reveal">
      <div class="bloco__esq">
        <p class="eyebrow">Controls, automation and software</p>
      </div>
      <div class="bloco__dir">
        <h2>Dedicated to exceeding your needs with unwavering commitment</h2>
        <p>i3Automation delivers advanced industrial controls solutions,
        specializing in control panels and SCADA systems. With certifications in
        top software and expertise in wastewater treatment, paper mills and solar
        energy, we design, program and commission systems that enhance efficiency
        and reliability. Our work includes government contracts and solar plant
        projects across the U.S.</p>
      </div>
    </div>

    <div class="bloco reveal">
      <div class="bloco__esq">
        <p class="eyebrow">Certified on</p>
      </div>
      <div class="bloco__dir">
        %(marcas)s
      </div>
    </div>

    <div class="bloco reveal">
      <div class="bloco__esq">
        <p class="eyebrow">Our mission</p>
      </div>
      <div class="bloco__dir">
        <h2>Innovative, high-quality automation that drives efficiency and
        reliability</h2>
        <p>Empowering our clients to succeed in both traditional and renewable
        energy sectors, with customized solutions and a focus on
        innovation that survives the day the plant has to run without us.</p>
      </div>
    </div>
  </div>
</section>

<!-- DOBRA 5 — O FILME. A janela abre de faixa a full-bleed e SUSTENTA.
     Montagem de tres cortes de 4,5s: a frase fala de repertorio, e um plano
     unico nao ilustra repertorio. -->
<section class="filme" data-progresso aria-labelledby="filme-frase">
  <div class="filme__palco">
    <div class="filme__janela">
      <video class="filme__video" data-momento-video
             muted loop playsinline preload="none"
             poster="img/video/momento-1-montagem.jpg"
             aria-label="Warehouse worker carrying a box, robotic assembly cell, water treatment plant and machine detail.">
        <source src="video/momento-1-montagem.webm" type="video/webm">
        <source src="video/momento-1-montagem.mp4" type="video/mp4">
      </video>
      <!-- Scrim obrigatorio: sem ele, branco sobre esta aerea diurna cai muito
           abaixo de 4,5:1 em varios quadros. -->
      <div class="filme__scrim" aria-hidden="true"></div>
    </div>
    <div class="filme__texto">
      <p class="filme__frase" id="filme-frase">Senior control experts know things
      they do not teach in school.</p>
      <p class="filme__legenda">Water treatment plant, robotic assembly cell,
      machine detail.</p>
    </div>
  </div>
</section>
<!-- DOBRA 5 — A DOBRA FUNDIDA, a pedido: "what we actually do e os numeros
     vao para cima da secao what follows, mescle e refaca o layout".

     Sao tres partes que antes eram tres secoes, e a fusao tem logica de
     leitura: O QUE FAZEMOS -> EM QUE ESCALA -> O QUE VEM A SEGUIR. As duas
     primeiras se sustentam mutuamente (a afirmacao e a prova dela), e a
     terceira abre as tres unidades.

     `.secao--fundida` da o respiro INTERNO entre as tres partes: `--s-8`
     (96px) entre elas contra os `--sec-y` (160px) que separam a secao das
     vizinhas. A razao de 1,67x e o que faz as tres lerem como uma dobra com
     tres tempos, e nao como tres dobras coladas.

     A COPY das partes 1 e 3 ja existia e nao mudou; os numeros sao os
     mesmos. O que mudou foi so onde elas vivem. -->
<section class="secao secao--fundida" id="who-we-are">
  <div class="container">
    <div class="bloco reveal">
      <div class="bloco__esq">
        <p class="eyebrow">What we actually do</p>
      </div>
      <div class="bloco__dir">
        <h2>We build the control system and hand you the plant that runs it</h2>
        <p>i3 Automations &amp; Controls has been integrating industrial control
        systems since 2000: panel, code, network, and drawings that match
        the wall. Oil and gas in Houston, water and wastewater across Florida,
        automotive body shops, paper mills, and utility-scale solar.</p>
        %(cta)s
      </div>
    </div>

    %(numeros)s

    <div class="bloco reveal">
      <div class="bloco__esq">
        <p class="eyebrow">What follows</p>
      </div>
      <div class="bloco__dir">
        <h2>What changes between a refinery and a body shop is the process</h2>
        <p>Not the rigor the control system deserves. Three things decide
        whether a plant runs: what gets built, how it gets decided, and who
        reads the screen at three in the morning.</p>
      </div>
    </div>
  </div>
</section>
%(unidade_1)s%(unidade_2)s%(unidade_3)s
<!-- DOBRA 9 — AS OITO DISCIPLINAS, a pedido: "a secao platform (certified
     where it matters) deve ser substituida por what we deliver de
     capabilities".

     A troca melhora a dobra por um motivo que vale registrar: a grade de
     plataformas listava FERRAMENTAS (Rockwell, Siemens, Ignition), e
     ferramenta e o que qualquer integrador tem. As oito disciplinas listam
     o que a empresa ENTREGA, que e a unica coisa que a diferencia -- e e a
     resposta direta ao "what follows" tres dobras acima.

     As plataformas nao se perdem: a grade continua inteira em
     capabilities.html, que e a pagina do assunto. -->
<section class="secao secao--offwhite" id="capabilities">
  <div class="container">
    <div class="bloco reveal">
      <div class="bloco__esq">
        <p class="eyebrow">What we deliver</p>
      </div>
      <div class="bloco__dir">
        <h2>Eight disciplines, one contractor</h2>
        <p>Each of these can be bought on its own. Bought together, they stop
        being four vendors pointing at each other. Nobody owns the gaps
        between them but us.</p>
      </div>
    </div>
    %(capacidades)s
  </div>
</section>

<!-- DOBRAS 10 e 11 — governo e CTA final, sob UMA fotografia.
     A pedido: "adicione uma unica imagem para Federal contracting e Talk to
     an engineer assim como e em who we are".

     `.dupla` e exatamente esse componente -- duas secoes escuras conectadas
     partilhando UMA fotografia, com o veu abrindo na faixa livre entre os
     dois blocos de texto. who-we-are e past-performance ja o usam com este
     mesmo par de secoes.

     `--d-abre/--d-fecha` em 56-64%%: a faixa livre aqui cai entre o fim das
     credenciais federais e o eyebrow do CTA. Sao os mesmos valores de
     who-we-are porque a caixa contem exatamente o mesmo par de secoes.

     A FOTO passou por medicao antes de entrar. A nota de who-we-are registra
     que `baterias` foi a unica do acervo a passar AA nesta caixa; medido na
     caixa da home, `fiacao` da 10,47:1 sob o veu fechado e 5,15:1 sob o
     aberto -- acima do piso de 4,5 nos dois. -->
<div class="dupla" style="--d-abre:56%%; --d-fecha:64%%">
  %(foto_fecho)s
%(governo)s%(contato)s
</div>
''' % {
        'numeros': NUMEROS,
        'marcas': marcas_certificacao(),
        'cta': cta('who-we-are.html', 'Who we are'),
        'capacidades': lista_capacidades(),
        'governo': GOVERNO,
        'foto_fecho': imagem(
            'dupla/fiacao', [1280, 1920],
            'Circular knitting machine with pneumatic lines and yarn guides',
            '100vw', classe='dupla__foto'),
        'contato': CONTATO_CTA,

        # ---- UNIDADE 1: a linha de producao -----------------------------
        # `webm=False`: medido, o VP9 deste clipe saiu MAIOR que o h264 (2.644
        # KB contra 2.122). O build descarta o arquivo, entao apontar para ele
        # daria 404. E uma fileira de hastes metalicas finas -- alta frequencia
        # em todo quadro --, que e onde o VP9 perde.
        'unidade_1': unidade(
            'linha', 'momento-atuadores',
            'Row of pneumatic actuators running on a production machine.',
            # A COPY MUDOU porque "Eight disciplines" passou a ser o titulo da
            # dobra 9, que agora lista as oito. Duas dobras da mesma pagina
            # abrindo com a mesma frase leem como erro de montagem.
            #
            # O que entra e o assunto do CLIPE desta unidade -- atuadores numa
            # maquina de producao --, com copy de capabilities ("Motor
            # Controls: MCC design, VFD configuration and starter logic, from a
            # single skid to a full lineup"), ja escrita e verificada.
            'Motor controls',
            'From a single skid to a full lineup',
            'MCC design, VFD configuration and starter logic, plus the '
            'interlocks that keep a jam on one station from stopping the whole '
            'line.',
            cta('capabilities.html', 'All capabilities'),
            'The line does not care how clever the code is.',
            'Row of pneumatic actuators on a production machine.',
            webm=False, lado='esq'),

        # ---- UNIDADE 2: o controle --------------------------------------
        # A legenda descreve o que se ve e NUNCA afirma que o sistema e da
        # casa: e material de banco de imagem, e a tela esta em tcheco. O
        # trecho escolhido (a partir de 13s) mostra leitura numerica ao vivo,
        # que e neutra de idioma.
        'unidade_2': unidade(
            'controle', 'momento-ihm',
            # A LEGENDA DESCREVE O CLIPE INTEIRO, e ela mudou junto com ele.
            # "live axis readouts" so aparece a partir dos ~13s; com o clipe
            # completo no ar, a frase prometia o que os primeiros 13 segundos
            # nao mostram. A regra de legenda do projeto (design.md §7.1) vale
            # para video: descreve o que se ve, e nada alem.
            'Operator working a machine HMI touchscreen.',
            'Method',
            'Understand the process, then choose the strategy that fits it',
            'We write to your standard when you have one, and we document the '
            'one we write when you do not. The plant runs before we leave, and '
            'the as-built drawings match what is on the wall.',
            cta('services.html', 'All services'),
            'Screens an operator can read at three in the morning.',
            'Operator at a machine HMI touchscreen, selecting a program.',
            lado='dir'),

        # ---- UNIDADE 3: o projeto ---------------------------------------
        # Substitui a dobra da refinaria. Oil & gas continua no site por
        # `setor/oil-gas` em past-performance, e aqui aparece no TEXTO.
        # ---- UNIDADE 3: a geracao -----------------------------------------
        # O clipe mudou para a superficie da placa a pedido, e a FRASE mudou
        # junto: "Oil and gas does not forgive a drawing that lies" era do
        # tanque e da tocha, e sobre uma placa solar seria legenda errada.
        # A frase nova vem de past-performance, ja escrita e verificada:
        # "Generation assets are only worth what the supervision layer can
        # prove they produced."
        'unidade_3': unidade(
            'geracao', 'momento-solar',
            'Sunlit surface of a photovoltaic module on a utility-scale array.',
            'Industries',
            'Five verticals, one way of working',
            'Oil and gas, water and wastewater, automotive, pulp and paper, and '
            'utility-scale solar. The process changes; the discipline does not '
            'and the drawing has to match the plant either way.',
            cta('past-performance.html', 'What already runs'),
            'A generation asset is worth what the supervision layer can prove '
            'it produced.',
            'Photovoltaic module surface on a utility-scale array.',
            lado='esq'),
    }
    return pagina(
        'index.html',
        'i3Automations | Industrial Control Panels, PLC and SCADA',
        'Control panels, PLC and SCADA programming, instrumentation and commissioning '
        'for oil and gas, water, automotive and solar. Federal contractor since 2000.',
        corpo, sobre_heroi=True, intro=True,
        # `braco.js` e `planta.js` sairam da home (design.md §8). Nao ha mais
        # peca em canvas aqui: a grade de setores, que era a ultima a usar a
        # lente, foi para past-performance.
        scripts_extra=())


# ============================================================ WHO WE ARE
#
#  REFEITA DO ZERO EM 2026-08-26, a pedido: "a pagina who we are precisamos
#  refazer completamente... pegar as info do site original e adicionar essas
#  informacoes junto a mais algumas para vender a empresa."
#
#  O QUE A VERSAO ANTERIOR TINHA DE ERRADO, e nao era a copy:
#
#  1. ELA REPETIA SERVICES INTEIRA. A dobra "How we work / Strategy first,
#     hardware second" mais `diagrama()` com os quatro passos era, palavra por
#     palavra, a dobra "How the work runs / Strategy first, hardware second" de
#     services.html. Duas paginas do mesmo site com o mesmo titulo e o mesmo
#     componente. O metodo pertence a services, que descreve o ENGAJAMENTO;
#     who-we-are descreve a CASA.
#
#  2. ELA NAO VENDIA NADA. Havia o que a empresa e (desde 2000, certificada,
#     federal) e a missao, e no meio nao havia UM argumento -- nenhuma razao
#     para o comprador preferir esta casa a outra com as mesmas certificacoes.
#
#  3. O MELHOR ARGUMENTO DO CLIENTE ESTAVA FORA DO SITE. O site antigo tem uma
#     secao inteira -- "Senior control experts know things they do not teach in
#     school", o transmissor de $45.000, o loop que se retuna por anos -- e a
#     migracao tinha ficado so com a MANCHETE dela, no filme da home. O
#     raciocinio, que e a parte que convence, nao estava em lugar nenhum.
#
#  A ESTRUTURA NOVA, e cada dobra e uma afirmacao so (plano.md §1 regra 1):
#
#      cabecalho ... quem somos          "We are problem solvers"
#      branco ...... o historico         26 anos + os cinco numeros
#      ESCURO ...... O ARGUMENTO         o transmissor de $45.000
#      off-white ... o retorno           os cinco ganhos, em `.dados`
#      branco ...... a missao            citacao + os setores em chips
#      dupla ....... governo + CTA       inalterada
#
#  Ritmo de superficie: navy -> branco -> escuro -> off-white -> branco ->
#  escuro x2. Alterna em toda emenda.
#
#  NENHUM COMPONENTE NOVO, E NENHUMA LINHA DE CSS. Tudo o que a pagina usa ja
#  existia: `.bloco`, `.pilha`, `.citacao`, `.numeros`, `.dados` (de services),
#  `.marca` (dos chips da home) e `.dupla`. O sistema ja tinha as pecas -- o que
#  faltava era o argumento.
#
#  O CABECALHO CONTINUA COM O VEU FECHADO (.72/.92), e e decisao e nao
#  esquecimento. As outras cinco paginas de conteudo passam
#  `classe='cabecalho--foto'`, que abre o veu para .52/.86 e poe a fotografia
#  como ASSUNTO. Aqui nao da: `cabecalho/quem-somos` sai de `foto.png`, a foto
#  autoral do cliente, que tem 1127 px de largura -- num cabecalho de 1440 px
#  ela e AMPLIADA 1,28x. Ela e o assunto certo (dois engenheiros lendo a tela de
#  uma maquina; e literalmente "who we are") e a resolucao errada para ficar
#  exposta. Sob o veu fechado ela e textura, e textura ampliada 1,28x ninguem
#  ve. Trocar por uma foto de banco de 5.000 px resolveria a nitidez e perderia
#  o assunto -- numa pagina chamada "Who We Are", uma engrenagem generica e pior
#  que uma foto macia da propria equipe.
def quem_somos():
    # A MESMA `faixa/ferramental` que a secao de missao usava, no papel trocado.
    # Ela e a de maior amplitude do acervo sob o veu navy (63,5) -- e amplitude
    # e o que faz uma foto sobreviver a camada que a cobre. O assunto continua
    # servindo: ferramental e pilares-guia sob uma prensa sao processo
    # industrial, que e do que o argumento fala.
    #
    # ENTRA POR CONCATENACAO E NAO POR `% extras`, e a razao e uma pegadinha do
    # Python: `%` liga mais forte que `+`, entao numa expressao com `cta()` no
    # meio o `% extras` cairia so no ULTIMO trecho e o `%(foto)s` de um trecho
    # anterior sairia literal no HTML. Concatenar nao tem esse lado.
    foto_argumento = imagem('faixa/ferramental', [1280, 1920, 2560],
                            'Tooling and guide pillars under an industrial press',
                            '100vw', classe='secao__foto')
    corpo = cabecalho(
        'Who we are', 'We are <br>problem solvers',
        'Consultants and integrators since 2000. Control panels, PLC and SCADA software '
        'out of Lakewood Ranch, Florida, with an oil and gas operation in Houston, '
        'Texas.',
        'cabecalho/quem-somos', [1127],
        'Two engineers in hard hats reading a machine control screen on a shop floor',
        'Who We Are',
        reticula=False,
        ) + '''
<section class="secao">
  <div class="container">
    <div class="bloco reveal">
      <div class="bloco__esq">
        <p class="eyebrow">Since 2000</p>
        <h2>Twenty-six years <br>of plants that run</h2>
      </div>
      <div class="bloco__dir">
        <!-- ENXUGADO EM 2026-08-27, a pedido: *"a pagina who we are esta com
             muito texto, e isso tira o ar que a pagina precisa ter,
             principalmente no mobile"*. 221 palavras -> 89.

             O QUE SAIU, E POR QUE CADA COISA:

             - A LISTA DE VERTICAIS ("water and wastewater, paper mills, oil
               and gas, utility-scale solar") — os chips de setor mais abaixo
               nesta MESMA página já a mostram, e past-performance dá uma
               ficha por setor. Era a terceira vez.
             - "certified on the leading supervisory platforms" — é a
               afirmação-âncora de capabilities, com a escada inteira por
               baixo. Aqui era só a afirmação, sem a prova.
             - O PARÁGRAFO DO "wrong partner is expensive twice" — é uma
               versão abstrata e mais fraca do argumento do transmissor de
               $45.000, que vem na dobra SEGUINTE com números e mecanismo.
               Ele gastava o soco 200 palavras antes de o soco acontecer.
             - "projects delivered across five industries" e "twenty-six
               years" em prosa — o bloco `NUMEROS`, logo abaixo, diz 279
               projetos, 158 nos EUA, 78 na Flórida, 150.000 tags e desde
               2000. Prosa repetindo número é a prosa perdendo.

             O QUE FICA É O QUE SÓ ESTA DOBRA DIZ: o que a casa é (consultora
             e integradora, não linha de produto) e o que ela vende
             (julgamento e documentação). O resto da dobra são os números, e
             agora eles têm espaço para respirar. -->
        <p class="lead">We are consultants and integrators, not a product line. We design,
        program and commission the systems that keep industrial processes running,
        and we stay reachable after startup.</p>
        <div class="pilha">
          <p>Control panels and SCADA are the centre of the practice, from a single skid to
          a plant delivered under federal contract.</p>
          <p>What we sell is not the equipment. It is the judgement to pick a control
          strategy that fits the process, and the discipline to document it so the next
          engineer, ours or yours, can pick it up.</p>
        </div>
      </div>
    </div>
    ''' + NUMEROS + '''
  </div>
</section>
<!-- O ARGUMENTO. Esta dobra e a razao de a pagina ter sido refeita: e o unico
     lugar do site que mostra COMO um especialista em controle pensa, em vez de
     afirmar que a casa tem especialistas.

     O texto e do proprio cliente, do site antigo, e entra quase inteiro. Duas
     mudancas, as duas de forma e nenhuma de fato:

       - "This statement may upset some" saiu. E hedge, e o tom do site pede
         declarativo: a frase seguinte ja assume o desconforto sem anuncia-lo.
       - O FECHO E NOVO, e e a unica coisa aqui que o cliente nao escreveu. O
         original termina no DIAGNOSTICO ("por que o loop nao se deixa tunar") e
         nunca diz o que se faz no lugar -- ou seja, para o comprador ele para
         uma frase antes de vender. Feedforward, controle por razao e cascata
         sao as tres respostas de livro para as tres perturbacoes que o proprio
         texto enumera, na mesma ordem em que ele as enumera. Nao ha invencao
         nenhuma: e o nome das estrategias.

     A CIFRA FICA EM $45.000 porque e a do cliente. Arredondar para "um
     transmissor caro" perderia o que faz o paragrafo morder.

     O FUNDO VIROU VIDEO em 2026-08-26 (nona rodada), a pedido. `pc.mp4` --
     o engenheiro na estacao -- estava no acervo sem consumidor, e e o assunto
     EXATO de uma dobra chamada "why it matters WHO DOES THE WORK": todo o
     resto do acervo mostra equipamento, este mostra alguem projetando. A foto
     que ele substitui (`faixa/ferramental`) mostrava ferramental sob uma
     prensa -- processo industrial generico, nao quem o pensa.

     CONTRASTE MEDIDO SOBRE OS 10 QUADROS PUBLICADOS, e nao sobre o poster:
     um fundo em movimento tem de passar em TODO quadro, nao no que a gente
     escolheu para a medicao. Pior quadro do clipe, sob o veu .55/.35:

         fundo mais claro do miolo    #40556C
         branco (titulo e citacao)     7,68:1   ok
         corpo --sobre-3-2             4,78:1   ok
         eyebrow #B9D2EA               4,93:1   ok

     A variacao ao longo do clipe e de 4,78 a 4,93 no corpo -- o plano e
     continuo e a luz nao muda, que e o que torna este clipe utilizavel como
     fundo. Um clipe com corte ou com mudanca de exposicao reprovaria em
     algum quadro e passaria no poster.

     `preload="none"`: quem nao chega nesta dobra nao baixa os 549 KB. E
     `data-momento-video` poe o clipe sob o observador do modulo 13 -- ele so
     toca enquanto esta na tela, e um decodificador de cada vez no site
     inteiro. -->
<section class="secao secao--escura secao--foto secao--video" id="argument">
  <video class="secao__fundo" id="video-argumento" data-momento-video
         muted loop playsinline preload="none"
         poster="img/video/fundo-solar.jpg"
         aria-label="Aerial view travelling over rows of solar panels in a field.">
    <!-- SEM WEBM, e o build decidiu: o VP9 saiu em 4.781 KB contra 2.959 do
         h264 na primeira passagem, e o descarte e automatico. Uma grade fina
         de celulas em movimento e onde o VP9 perde para o x264 -- e um WebM
         maior nao e neutro: o navegador fica com a primeira `<source>` que
         sabe tocar, entao Chrome e Firefox baixariam MAIS que o Safari. -->
    <source src="video/fundo-solar.mp4" type="video/mp4">
  </video>

  <div class="container">
    <!-- O PARALAXE SAIU EM 2026-08-26, a pedido: "nao quero o paralax na secao
         'Why it matters who does the work', deixe como estava (mantenha o
         video atual)".

         Saiu inteiro, e nao so a aparicao em camadas: a secao perdeu o
         `data-progresso`, entao o fundo tambem parou de derivar. Era a leitura
         literal do pedido -- "nao quero o paralax NA SECAO" --, e ela leva
         junto o defeito que a deriva tinha criado: sem curso, o video nao
         precisa mais ser 12% maior que a caixa, e nao ha o que vazar.

         O video FICA, como pedido. O que volta e o bloco com `reveal` simples,
         que e como a dobra era antes da nona rodada. -->
    <div class="bloco reveal">
      <div class="bloco__esq">
        <p class="eyebrow">Why it matters who does the work</p>
        <h2>The loop nobody <br>could ever tune</h2>
      </div>
      <div class="bloco__dir">
        <p class="citacao">Senior control experts know things they do not teach in
        school.</p>
        <!-- `.pilha` E NAO tres `.corpo` soltos: paragrafo colado em paragrafo
             nao tem vao nenhum no sistema (`.corpo` so declara medida), e o
             argumento saia como um bloco de texto so. A pilha e o componente
             que existe para isto, e a regra de vao mora nela. -->
        <!-- APERTADO EM 2026-08-27, pelo mesmo pedido de ar. 194 palavras ->
             143, e aqui o corte foi CIRÚRGICO e não generoso: esta é a única
             dobra do site que mostra COMO um especialista em controle pensa,
             em vez de afirmar que a casa tem especialistas. É a razão de a
             página ter sido refeita (ver a nota da nona rodada acima).

             NADA DE FATO SAIU. Continuam inteiros: a cifra de $45.000, que é
             do cliente e é o que faz o parágrafo morder; as três perturbações
             na ordem em que ele as enumera; as três estratégias que respondem
             a elas uma a uma (feedforward, razão, cascata); e o fecho de 2000.

             O QUE SAIU FOI FÔLEGO DE FRASE. A enumeração das perturbações era
             três orações completas — "An inlet temperature change arrives...
             A header pressure change moves... A production rate change
             demands..." — e virou uma lista pontuada dentro de uma oração só.
             O argumento é o mesmo; o que muda é quanto ar ele ocupa numa tela
             de 390px, por cima de um vídeo. -->
        <!-- O "SEE MORE" E SO DO CELULAR, pedido em 2026-08-27: *"esta boa no
             web, mas no mobile tem muito texto, adicione uma opcao de ler
             mais"*.

             E UM `<details>` DE VERDADE, e nao uma classe com `max-height`.
             Tres razoes, e nenhuma e de gosto:

               - o conteudo continua no DOM e continua achavel pelo Ctrl+F do
                 navegador, que num argumento tecnico e o que o leitor usa;
               - o `<summary>` ja e um botao para o teclado e para o leitor de
                 tela, com `aria-expanded` de graca -- um `<div>` com `onclick`
                 precisaria de tres atributos e um listener para empatar;
               - sem JS ele ainda abre. A pagina nao tem script proprio, e um
                 acordeao que depende de JS seria o unico ponto do site em que
                 texto some se um arquivo falhar.

             NO DESKTOP ELE DESAPARECE COMO COMPONENTE: `open` fica forcado e o
             `summary` sai do fluxo, entao o que resta e a `.pilha` de sempre.
             O primeiro paragrafo fica FORA do `details` -- ele carrega a
             cifra de $45.000 e o "muito simples e muito errado", que e o
             gancho; esconder o gancho seria esconder o argumento. -->
        <div class="pilha">
          <p>On a consistency, density or temperature loop, the standard move is a $45,000
          transmitter on the main flow, wired straight to the valve on the controlled flow.
          Virtually every major engineering house does it. It is very simple, and it is very
          wrong.</p>
          <details class="mais">
            <summary class="mais__botao">Read why<span aria-hidden="true"></span></summary>
            <div class="mais__corpo pilha">
              <p>Wrong because the deviation rarely starts at the valve. It arrives from
              upstream: inlet temperature, header pressure, a production rate the
              loop was never asked to absorb. So the loop gets retuned, for years, with no
              success: tuning was never the problem.</p>
              <p>What fixes it is a strategy aimed at where the disturbance starts:
              feedforward on the variable that moves first, ratio control where the ratio is
              what matters, cascade where the header shifts. That costs engineering hours,
              not forty-five thousand dollars of instrument. It is the judgement we were
              hired for in 2000, and it is still what we sell.</p>
            </div>
          </details>
        </div>
        ''' + cta('capabilities.html', 'What we do') + '''
      </div>
    </div>
  </div>

  <!-- WCAG 2.2.2, e vale aqui pelo mesmo motivo que no heroi: movimento que
       comeca sozinho, dura mais de 5 s e divide a tela com outro conteudo.
       O botao aponta para o `id` do video que controla -- ver modulo 14. -->
  <button class="heroi__pausa" type="button" data-pausa="video-argumento"
          aria-pressed="false" aria-label="Pause background video">
    <svg class="heroi__pause" viewBox="0 0 16 16" aria-hidden="true"><rect x="3" y="2" width="3.6" height="12"/><rect x="9.4" y="2" width="3.6" height="12"/></svg>
    <svg class="heroi__play" viewBox="0 0 16 16" aria-hidden="true"><path d="M3.5 2l10 6-10 6z"/></svg>
  </button>
</section>

<!-- O RETORNO. Os cinco ganhos vem do site antigo -- "revenue growth, cost
     reduction, market expansion, enhanced partner collaboration, and
     streamlined production cycles" --, que e a lista certa escrita na lingua
     errada: sao os cinco substantivos de qualquer folheto de consultoria, e o
     redline 10 recusa exatamente esse registro.

     Cada um foi reescrito para o que ele E NA PLANTA. "Revenue growth" nao diz
     nada; "mais produto pelo mesmo ativo, porque o loop segura setpoint em vez
     de cacar em volta dele" diz a mesma coisa e pode ser conferido.

     O LAYOUT VIROU `.retorno` em 2026-08-26 (nona rodada), a pedido: "refatore
     com uma forma mais interativa em momentos de cada um dos five things".
     Era `.dados` -- cinco linhas de mesmo peso, todas ao mesmo tempo. Agora
     cada uma tem o seu momento: `data-passos="5"` faz o modulo 7 publicar
     `data-n` de 0 a 4 conforme a rolagem, e o item da vez acende. O ponteiro
     vence a rolagem, que e o que torna a peca interativa de fato.

     E A CENA FICOU PRESA na decima rodada, no mesmo dia: "precisa ficar
     antiscroll ate o scroll ir de output a cycle time; ele precisa passar por
     todos e so depois pode mudar de secao". O trilho tem 375vh e o palco e
     `sticky` -- 55vh de rolagem por item, e a secao so solta depois do quinto.

     ISSO CONTRADIZ O QUE EU TINHA ARGUMENTADO NA RODADA ANTERIOR, e a
     contradicao fica registrada: eu recusei o painel preso citando
     past-performance, onde ele existiu e saiu a pedido. O usuario viu a versao
     sem prisao e pediu a prisao -- decisao dele, com a alternativa na frente.
     A diferenca entre esta e a de la esta no CSS 8.2.1: aquela TROCAVA a
     fotografia inteira a cada passo, e era isso que lia como apresentacao de
     produto; esta e uma lista parada em que muda qual linha esta acesa.

     A ROLAGEM CONTINUA NATIVA: nao ha `wheel` sequestrado nem biblioteca. E um
     trilho alto com um palco `sticky`, entao teclado, `End`, barra e ancora
     seguem funcionando -- que e o que faz "antiscroll" aqui nao custar
     acessibilidade. -->
<section class="secao secao--offwhite secao--presa" id="returns"
         data-progresso data-passos="5">
  <div class="presa__palco">
  <div class="container">
    <div class="bloco">
      <div class="bloco__esq">
        <p class="eyebrow">What the work returns</p>
        <h2>Five things a plant <br>gets back</h2>

        <!-- A MEDIDA DA PRISAO. Ela nao e enfeite: e o que faz a cena presa se
             explicar sem uma frase ensinando a usa-la (regra 10 de clean).
             Quem fica preso sem saber por quanto tempo rola mais forte; quem
             ve "03 / 05" e tres segmentos acesos sabe que faltam dois.

             `aria-hidden` nos dois: o leitor de tela recebe a lista inteira de
             uma vez, com os cinco itens, e um marcador de posicao numa
             encenacao que para ele nao acontece so atrapalha. -->
        <div class="presa__medida" aria-hidden="true">
          <p class="presa__contador"></p>
          <div class="presa__regua">
            <span class="presa__seg"></span><span class="presa__seg"></span>
            <span class="presa__seg"></span><span class="presa__seg"></span>
            <span class="presa__seg"></span>
          </div>
        </div>
      </div>
      <div class="bloco__dir">
        <p class="corpo">These are what a control project is bought for. Naming them keeps
        the scope honest: if a change does not move one of the five, it is decoration, and
        we will say so before you pay for it.</p>
      </div>
    </div>

    <!-- `<ol>` e nao `<div>`: sao cinco itens numerados, e a numeracao esta na
         tela. Um leitor de tela anuncia "lista de 5 itens" e o numero vem de
         graca -- o `.retorno__num` visivel e decorativo por cima disso, e por
         isso NAO leva `aria-hidden`: ele repete o que a lista ja diz, e some
         do fluxo de leitura sem que ninguem precise marcar nada. -->
    <!-- SEM `data-progresso` PROPRIO, e isto e um conserto e nao uma omissao.
         A lista tinha o dela quando a secao era de altura normal. Presa, ela
         nao atravessa mais nada: o palco e `sticky`, entao o retangulo dela
         fica parado na tela e o `--p` que ela mediria seria uma constante --
         o item aceso travaria no primeiro e nunca andaria.

         Quem mede agora e a SECAO, que e o trilho de 375vh, e e ela que
         publica `data-n`. Um alvo, uma medida. -->
    <ol class="retorno">
      <li class="retorno__item" style="--i:0">
        <span class="retorno__regua" aria-hidden="true"></span>
        <p class="retorno__num">01</p>
        <h3 class="retorno__nome">Output</h3>
        <p class="retorno__valor">More product through the same asset, because the loop holds setpoint instead of hunting around it.</p>
      </li>
      <li class="retorno__item" style="--i:1">
        <span class="retorno__regua" aria-hidden="true"></span>
        <p class="retorno__num">02</p>
        <h3 class="retorno__nome">Cost to run</h3>
        <p class="retorno__valor">Less over-dosing, less rework and less energy spent correcting a process that was never stable to begin with.</p>
      </li>
      <li class="retorno__item" style="--i:2">
        <span class="retorno__regua" aria-hidden="true"></span>
        <p class="retorno__num">03</p>
        <h3 class="retorno__nome">Reach</h3>
        <p class="retorno__valor">Capacity and traceability that qualify a plant for contracts it could not bid on before, including federal ones.</p>
      </li>
      <li class="retorno__item" style="--i:3">
        <span class="retorno__regua" aria-hidden="true"></span>
        <p class="retorno__num">04</p>
        <h3 class="retorno__nome">Shared view</h3>
        <p class="retorno__valor">Operators, contractors and corporate reading the same historized data instead of three spreadsheets that disagree.</p>
      </li>
      <li class="retorno__item" style="--i:4">
        <span class="retorno__regua" aria-hidden="true"></span>
        <p class="retorno__num">05</p>
        <h3 class="retorno__nome">Cycle time</h3>
        <p class="retorno__valor">Shorter production cycles, because each step stops waiting for someone to confirm the last one finished.</p>
      </li>
    </ol>
  </div>
  </div>
</section>

<!-- A MISSAO E O PORQUE, FUNDIDOS NUMA SECAO SO.

     Os chips de setor ficam com a missao e nao viram bloco proprio: a missao
     diz "energia tradicional E renovavel", e os chips sao a prova dessa frase.
     Separa-los poria a afirmacao numa dobra e a evidencia noutra.

     Chip LISO, sem o ponto de `.marca--certificada`: aqui o estado e "setor em
     que operamos", nao "plataforma em que somos certificados". Os chips com
     ponto vivem no bloco de governo, mais abaixo, e a distincao entre os dois e
     o que faz o componente valer -- ver a nota da dobra de abertura da home.

     Contraste medido sobre branco: rotulo `--tinta` = 17,40:1, folgado. A
     BORDA do chip liso e `--filete-forte` = rgba(0,0,0,.24), que composto da
     #C2C2C2 e 1,78:1 -- abaixo do piso de 3:1 do WCAG 1.4.11, e de proposito.
     Aquele piso vale para o que IDENTIFICA um controle ou o estado dele; aqui
     o chip nao e controle e nao tem estado: o nome do setor esta escrito
     dentro, em 17,40:1, e a moldura so agrupa. E o mesmo chip liso que a dobra
     de abertura da home ja usa, com a mesma borda. Quem carrega estado e
     `.marca--certificada`, e essa tem borda `--azul` -- 3,47:1 sobre branco,
     acima do piso, que e por isso que a distincao entre as duas se enxerga.

     "WHY US" ENTROU EM 2026-08-26 (nona rodada), a pedido: "adicione uma secao
     mesclada a our mission para dizer a quem esta olhando 'why us'".

     MESCLADA E NAO SEGUINTE: os dois rotulos caem na MESMA coluna esquerda, um
     sob o outro, e `.secao--fundida` da o vao de `--s-8` entre os movimentos.
     Dois blocos de mesma estrutura em sequencia leem como o mesmo bloco duas
     vezes -- e a coluna esquerda ficaria vazia sob um eyebrow de duas
     palavras. E o mesmo conserto que a dobra de abertura da home levou.

     AS QUATRO RESPOSTAS SAO VERIFICAVEIS NO PROPRIO SITE, e isso e requisito e
     nao capricho: o cliente e fornecedor federal, e o §8.3 do plano proibe
     afirmacao nao verificavel. Arcadia e os tres anos estao em
     past-performance; Daimler e BMW tambem; o codigo comentado em formato
     nativo esta em services; as duas linhas telefonicas estao no rodape de
     todas as paginas. A quarta amarra no argumento e nos cinco ganhos acima --
     que e o que faz a pagina fechar em vez de terminar. -->
<section class="secao secao--fundida" id="why-us">
  <div class="container">
    <div class="bloco reveal">
      <div class="bloco__esq">
        <p class="eyebrow">Our mission</p>
      </div>
      <div class="bloco__dir">
        <p class="citacao">Deliver automation that drives efficiency and reliability, in
        traditional and renewable energy alike.</p>
        <p class="corpo" style="margin-top: var(--s-5)">Stated plainly, because the version
        with adjectives helps nobody: high-quality automation, built so our clients succeed
        in the sectors they already operate in and the ones they are moving into.</p>

        <div class="marcas" style="margin-top: var(--s-6)">
          <span class="marca">Oil &amp; Gas</span>
          <span class="marca">Water &amp; wastewater</span>
          <span class="marca">Power generation</span>
          <span class="marca">Utility-scale solar</span>
          <span class="marca">Automotive</span>
          <span class="marca">Pulp &amp; paper</span>
        </div>
      </div>
    </div>

    <div class="bloco reveal">
      <div class="bloco__esq">
        <p class="eyebrow">Why us</p>
        <h2>Four answers, <br>before you ask</h2>
      </div>
      <div class="bloco__dir">
        <p class="corpo">Every integrator says they are experienced and certified. So are
        we, and it is on this page. These are the four things that actually differ, written
        as the objections we hear.</p>

        <div class="porque">
          <div class="porque__item">
            <p class="porque__rotulo">&ldquo;Support ends when the job ends.&rdquo;</p>
            <p class="porque__texto">Not here. Two lines, and the engineer who wrote the
            code picks up. One Florida wastewater plant has run under our support for over
            three years, across three successive contracts.</p>
          </div>
          <div class="porque__item">
            <p class="porque__rotulo">&ldquo;The code belongs to the integrator.&rdquo;</p>
            <p class="porque__texto">Not ours. Commented PLC and HMI source, in the
            platform&rsquo;s native format, delivered to you. An integrator who keeps the
            source is selling you a dependency, not a control system.</p>
          </div>
          <div class="porque__item">
            <p class="porque__rotulo">&ldquo;You will write it your way.&rdquo;</p>
            <p class="porque__texto">We write to your standard when you have one. The
            Daimler and BMW body shops were programmed to the customer&rsquo;s own PLC
            standard end to end. The harder way, and the correct one.</p>
          </div>
          <div class="porque__item">
            <p class="porque__rotulo">&ldquo;You will sell us what we don&rsquo;t
            need.&rdquo;</p>
            <p class="porque__texto">If a bigger transmitter or another panel will not move
            one of the five above, we say so before you pay for it. Losing that scope costs
            us less than being wrong about it.</p>
          </div>
        </div>
      </div>
    </div>
  </div>
</section>
''' + '''
<!-- DUPLA: credenciais federais + CTA sob UMA fotografia, a pedido (20/08), no
     mesmo par que home e services ja usam.

     `--d-abre/--d-fecha` em 56-64% e nao no padrao 34-42%: a faixa livre desta
     pagina cai MAIS BAIXO que nas outras, porque o bloco de credenciais e
     longo. Abrir no padrao poria o veu aberto em cima da propria lista de
     UEI/CAGE/NAICS -- medido, o corpo caia para 1,9:1. Os dois valores
     continuam validos depois da reescrita: a caixa depende so do que esta
     DENTRO dela, e dentro dela estao os mesmos dois blocos.

     A FOTO TROCOU EM 2026-08-26 (decima rodada), a pedido -- "troque a imagem
     de fundo das ultimas duas secoes". E a troca desenterrou um defeito que
     `baterias` escondia havia rodadas: **A FAIXA LIVRE ESTAVA NO LUGAR
     ERRADO.**

     56-64% era o numero herdado de uma versao anterior desta pagina. Medido
     AGORA, no navegador, sobre a pagina como ela e (dupla de 1431 px):

         11,2% a 39,3%   texto do bloco de governo
         39,3% a 61,6%   FAIXA LIVRE de verdade
         61,6% a 88,8%   texto do CTA

     Ou seja: o veu abria em 56% e fechava em 64%, e a rampa de fechamento vai
     ate 70% -- em cima do eyebrow e do titulo do CTA, que comecam em 61,6%. A
     fotografia aparecia debaixo de letra, e so ali.

     `baterias` era escura e chapada, entao ninguem via. `prototipagem` tem uma
     protoboard BRANCA, e o defeito virou ilegivel na hora.

     44% E 54% SAO OS NUMEROS CERTOS: a rampa de abertura comeca em 40 (o
     governo ja terminou em 39,3) e a de fechamento termina em 60 (o CTA so
     comeca em 61,6). Nenhuma letra em veu aberto, dos dois lados.

     E COM A FAIXA NO LUGAR O VEU PADRAO VOLTA A SERVIR. A primeira tentativa
     desta rodada foi `--veu-d-meio: .88`, para compensar o branco da protoboard
     -- e ela estava compensando a faixa mal posta, nao a foto. Medido nas zonas
     de texto REAIS:

         veu   pior fundo   branco   corpo   rotulo
         .72   #455C73       6,93    4,31    4,44    reprova
         .78   #364E67       8,60    5,35    5,51    <- o PADRAO, e passa
         .88   #1D3854      12,03    7,49    7,71    escuro sem precisar

     Fica o padrao: menos um override, mais contraste que a versao com .88
     tinha, e a fotografia visivel. A amplitude na faixa livre e 157 -- a foto
     aparece inteira ali, que e o que a peca existe para fazer.

     E O ENQUADRAMENTO DA FOTO ENTROU JUNTO (`janela` em build_imagens.py): sem
     ele a protoboard cai a ~49% da altura e a faixa livre pegava so fundo
     preto. Com `(.75, .16)` ela vai para ~60% da fonte, que cai dentro de
     44-54% na caixa. Foto certa, no lugar certo, sob o veu certo. -->
<div class="dupla" style="--d-abre:44%; --d-fecha:54%">
  ''' + imagem('dupla/prototipagem', [1280, 1920, 2560],
               'Prototyping breadboards with a microcontroller board, LEDs and jumper '
               'wires, seen from above',
               '100vw', classe='dupla__foto') + '''
''' + GOVERNO + CONTATO_CTA + '''
</div>'''
    return pagina(
        'who-we-are.html', 'Who We Are | i3 Automations &amp; Controls',
        'Industrial automation consultants and integrators in Lakewood Ranch, Florida '
        'since 2000. Control panels, SCADA and PLC software for oil and gas, water, power '
        'and solar. Certified on Ignition, VTScada and Canary.',
        corpo, og_img='img/og/who-we-are-1200.jpg', trilha_seo='Who We Are')


# =========================================================== CAPABILITIES
def capacidades():
    # A foto de "Since 2000" fica sob veu BRANCO (.78 no miolo, .56 nas
    # laterais): com texto escuro sobre veu claro o pior caso e o ponto mais
    # ESCURO da foto, e ali o corpo mede 14,21:1.
    extras = {
        'foto_desde': imagem('faixa/robotica', [1280, 1920],
                             'Robotic handling cell in a distribution facility',
                             '100vw', classe='secao__foto'),
        'foto_missao': imagem('cabecalho/servicos', [1280, 1920],
                              'Relay and terminal wiring inside a control panel',
                              '100vw', classe='secao__foto'),
        'diagrama': diagrama([
            ('01', 'Understand the process',
             'P&amp;IDs, existing logic, and a conversation with whoever runs the '
             'plant at night. The constraints are rarely in the drawings.'),
            ('02', 'Choose the strategy',
             'Control philosophy, alarm rationalisation and the instrument list '
             'that follows from them, in that order, never the reverse.'),
            ('03', 'Build and test',
             'The panel is wired and tested in our shop, and the code is simulated '
             'against it before either one reaches your site.'),
            ('04', 'Commission and hand over',
             'Loop checks, startup, operator training, and as-built drawings that '
             'match the installation. Then annual support if you want it.'),
        ]),
    }
    corpo = cabecalho(
        'Capabilities', 'Eight disciplines, <br>one contractor',
        'Panel, code, network and commissioning under one roof, so nobody owns the '
        'gaps between them but us.',
        # TROCOU EM 2026-08-26, e a razao e de acervo e nao de composicao.
        # Este cabecalho usava `faixa/refinaria`, que e um recorte de
        # `gas.jpg` -- a UNICA fotografia de oil & gas que existe no projeto.
        # A mesma foto estava recortada em cinco lugares, e o usuario reparou.
        # Ela passou a aparecer UMA vez, no momento 4 da home, em full-bleed
        # com o traco por cima; aqui entra outra planta de processo.
        #
        # `britagem-planta` (9504x6336) tambem resolve o problema que
        # `cabecalho/capacidades` tinha: aquela e 1024x331 e seria AMPLIADA
        # 1,87x num cabecalho de 620 px de altura. Esta e REDUZIDA.
        'faixa/britagem-planta', [1280, 1920, 2560],
        'Aggregate processing plant with conveyor and silos',
        'Capabilities', classe='cabecalho--foto', reticula=False) + '''
<section class="secao">
  <div class="container">
    <div class="bloco reveal">
      <div class="bloco__esq">
        <p class="eyebrow">What we deliver</p>
      </div>
      <div class="bloco__dir">
        <p class="lead">Each of these can be bought on its own. Bought together, they stop
        being four vendors pointing at each other.</p>
      </div>
    </div>
    ''' + lista_capacidades(nivel=2) + '''
  </div>
</section>
<!-- A CENA DA COBERTURA. Substitui a `.figura` estatica que morava aqui, em
     2026-08-26 (decima rodada), a pedido -- com quatro quadros de referencia
     do efeito e a foto nova (`quadrados/final.jpg`).

     A FOTO MUDOU, E ERA HORA. A anterior era a macro de um modulo de 4 reles
     SRD-05VDC-SL-C -- acessorio de Arduino, com "4 Relay Module" serigrafado
     na placa. Ela tinha uma legenda escrita para NAO chamar aquilo de CLP,
     porque chamar seria afirmacao falsa sobre a competencia de quem programa
     ControlLogix e S7 e e fornecedora federal. Uma pagina chamada "Eight
     disciplines, one contractor", que abre com painel, CLP, rede e
     comissionamento, ilustrada por um modulo de bancada.

     A nova e o produto: interior de painel montado, CLPs Siemens em trilho,
     disjuntores, reguas de bornes, canaleta e chicote. E a primeira das oito
     disciplinas, fotografada.

     O QUE A CENA FAZ. A tela prende, e a fotografia e apagada em blocos ate
     sumir. Os quadrados pintam `--sup-2` -- o off-white da secao SEGUINTE --
     entao, quando o ultimo cai, a tela inteira ja e "Platforms and
     certifications" e o `sticky` solta sem troca de cor visivel. Nao e uma
     dobra que termina e outra que comeca: e a mesma tela terminando de virar.

     A conta de cada quadrado, a razao de ser `scale` e nao `opacity`, e a
     sustentacao de 15% com a tela ja coberta estao no CSS §8.4. A ordem dos
     84 quadrados sai de `cobertura()`, em build_paginas.py.

     A LEGENDA DESCREVE O QUE SE VE E NADA ALEM -- nao afirma que o painel e
     da casa. A regra vale aqui como em toda foto do site: o acervo mistura
     autoral com banco de imagem, e o cliente e fornecedor federal. -->
''' + cobertura('momento/painel', [1280, 1920, 2560],
                'Interior of an assembled control panel with PLCs on DIN rail, '
                'circuit breakers, terminal blocks and wiring duct',
                'Assembled control panel: PLCs on DIN rail, breakers, terminal '
                'blocks and field wiring.',
                # A FRASE DO FECHO, e ela e o que acabou de acontecer na tela.
                # O painel -- a coisa que da para apontar -- foi apagado na
                # frente do visitante; a primeira oracao chega em cima do
                # apagamento e a segunda nomeia o que ficou. O mecanismo e a
                # copy dizem a mesma coisa, que e a razao de ela morar aqui e
                # nao em outra dobra.
                #
                # E irma das outras duas do site ("Good control strategy beats
                # more expensive instrumentation", no heroi; "Senior control
                # experts know things they do not teach in school", no filme e
                # em who-we-are) -- mesma familia, uma por pagina.
                #
                # E NAO REPETE a abertura de "Platforms and certifications"
                # logo abaixo, que fala de software de terceiros: aqui o
                # assunto e hardware contra julgamento.
                # A FRASE E DO USUARIO. Ele a reescreveu em 2026-08-26 e a
                # escreveu direto em `site/capabilities.html`, que e GERADO --
                # portada para ca antes do build seguinte, que a teria apagado.
                # (A minha era "You can see the hardware. / You are paying for
                # the judgement."; esta e melhor: nomeia quem entende, e nao so
                # o que se paga.)
                #
                # `&rsquo;` e nao apostrofo reto: e a convencao tipografica do
                # site inteiro (`platform&rsquo;s`, `customer&rsquo;s`).
                fecho=('Anyone can see the panel.',
                       'We understand what&rsquo;s behind it.')) + '''

<!-- PLATAFORMAS, REFEITA em 2026-08-26 (decima rodada): "esta secao precisa
     ser refeita de acordo com o design do nosso site e nossas mudancas".

     O QUE ELA TINHA DE ERRADO, e nao era a escada. A escada e boa e e a unica
     peca do site que usa notacao de engenharia de controle para carregar
     informacao: contato ENERGIZADO = certificados aqui, contato ABERTO =
     operamos aqui. O defeito era que ela punha as OITO plataformas num rail
     so, e o visitante tinha de DEDUZIR o que o contato cheio significa. A
     regra 10 de clean nao deixa consertar isso com uma legenda ("filled
     contact means certified") -- entao o conserto e estrutural.

     AGORA SAO DOIS RAILS, cada um com o proprio rotulo na coluna esquerda:

         Certified on   3 degraus energizados   Ignition, VTScada, Canary
         Fluent in      5 degraus abertos       Rockwell, Siemens, Schneider,
                                                PI System, SQL Server

     O rotulo do grupo E a traducao da notacao. A escada para de precisar de
     legenda porque o titulo ja diz o que o estado quer dizer.

     E o bloco cai no padrao que a home e o "why us" de who-we-are ja usam:
     TRES ROTULOS EMPILHADOS na coluna esquerda em vez de um eyebrow sozinho
     com ~400px de vazio embaixo. `.secao--fundida` da o vao entre os
     movimentos.

     A DOBRA ABRE COM O QUE ACABOU DE ACONTECER. "The panel above is the first
     of the eight" amarra a cena da cobertura ao texto -- sem isso a secao
     seria um bloco novo que por acaso comeca onde a foto sumiu. -->
<section class="secao secao--offwhite secao--fundida" id="platforms">
  <div class="container">
    <div class="bloco reveal">
      <div class="bloco__esq">
        <p class="eyebrow">Platforms and certifications</p>
        <h2>Certified where <br>it matters</h2>
      </div>
      <div class="bloco__dir">
        <p class="corpo">The panel above is the first of the eight disciplines. The other
        seven run on somebody else&rsquo;s software, and this is whose. Three SCADA
        platforms we are certified on, and five more we work in every week, the
        historian layer included, because a plant that cannot prove what happened cannot
        improve and cannot pass an audit.</p>
      </div>
    </div>

    <div class="bloco reveal">
      <div class="bloco__esq">
        <p class="eyebrow">Certified on</p>
      </div>
      <div class="bloco__dir">
        ''' + grade_plataformas(certificadas=True) + '''
      </div>
    </div>

    <div class="bloco reveal">
      <div class="bloco__esq">
        <p class="eyebrow">Fluent in</p>
      </div>
      <div class="bloco__dir">
        ''' + grade_plataformas(certificadas=False) + '''
      </div>
    </div>
  </div>
</section>
''' + CONTATO_CTA
    return pagina(
        'capabilities.html', 'Capabilities | i3 Automations &amp; Controls',
        'Control panels, PLC programming, SCADA, commissioning, instrumentation, '
        'industrial networks, motor controls and software development.',
        corpo, og_img='img/og/capabilities-1200.jpg',
        trilha_seo='Capabilities')


# ======================================================= PAST PERFORMANCE
SETORES_PP = [
    ('Automotive', 'Body shops, <br>to their standard',
     'Automotive plants do not accept a contractor&rsquo;s house style. Both of these '
     'programs were written to the customer&rsquo;s own PLC standard, which is the '
     'harder and correct way to do it.',
     [('Daimler / Mercedes-Benz',
       'Plant automation for the New Body Shop, following the Integra standard '
       'for PLC programming end to end.'),
      ('BMW',
       'F15 / F16 / F25 / F26 Body Shop SSB, integrating BMW&rsquo;s specific PLC '
       'standard programs.')],
     'setor/automotivo', [600],
     'Robotic welding line in an automotive body shop'),

    ('Oil &amp; Gas', 'Houston, and <br>150,000 tags',
     'Our oil and gas client base sits in Houston, Texas. The work is PI System '
     'expertise at scale: more than 150,000 historized tags, and the support '
     'contract that keeps them trustworthy.',
     [('Historian',
       'AVEVA PI System, 150,000+ historized tags under support.'),
      ('Scope',
       'Ongoing support and optimisation of existing control and data systems, '
       'plus new project work.')],
     'setor/oil-gas', [600, 900],
     'Process units and storage tanks at a refinery'),

    # ARCADIA ENTRA NOMEADA (21/08). O site antigo diz "a massive wastewater
    # treatment plant in Arcadia" e a migracao tinha deixado o setor sem lugar
    # nenhum. A planta e tambem a do registro de contratos logo abaixo, entao
    # nomea-la aqui e o que costura a folha de setor a tabela de cifras.
    ('Water &amp; wastewater', 'Florida plants, <br>under annual support',
     'Controls maintenance, PLC and HMI programming, and integration of the entire '
     'SCADA system. Daily reports are pulled straight from the SQL database, and '
     'every operator gets the alarm the moment something moves out of band.',
     [('Arcadia, Florida',
       'A municipal wastewater treatment plant supported for over three years: '
       'SCADA, PLC and motor control, under three successive contracts.'),
      ('Maintenance',
       'Annual support keeping control systems safe and efficient.'),
      ('Programming',
       'PLC and HMI development, with the full SCADA layer integrated rather '
       'than bolted on.'),
      ('Reporting',
       'Daily reports generated from SQL databases; alerts and alarm messages '
       'delivered to the operator on shift.')],
     'setor/agua', [600],
     'Large-diameter pipework at a water intake station'),

    # A WESTROCK VOLTOU (21/08). Ela estava nomeada no site antigo e a migracao
    # a perdeu -- e e o nome que faltava, porque ao lado de Daimler e BMW ela
    # fecha a leitura de grandes contas em TRES setores, nao em um.
    #
    # E a prosa mudou junto, por consequencia e nao por gosto: a versao anterior
    # descrevia "drives, interlocks e alarm rationalisation", que e o que um
    # controle de fabrica de papel costuma envolver -- mas NAO e o escopo que a
    # fonte registra para esta conta. Escrever o nome do cliente e manter ao
    # lado um escopo diferente do dele seria pior que nao nomear ninguem.
    # O escopo abaixo e o da fonte, palavra por palavra: painel de controle,
    # diagnostico de processo, sistemas de monitoramento e CAMERAS.
    ('Paper', 'Mill process <br>controls',
     'Paper mill process controls, where a stopped machine costs more per hour '
     'than the control system did. The work is the unglamorous kind: the '
     'panel, the fault nobody can reproduce, and the camera that finally shows '
     'what the operator has been describing for a week.',
     [('WestRock',
      'Control panel services and process troubleshooting across paper and mill '
      'operations, with monitoring systems and camera installations.'),
      ('Why it matters',
       'Continuous process: an unplanned stop is measured in tonnes, not minutes.')],
     'setor/papel', [600, 900],
     'Row of industrial presses on a mill floor'),

    ('Solar', 'Utility-scale, <br>across the country',
     'Controls and monitoring for utility-scale photovoltaic plants across the '
     'United States. Generation assets are only worth what the supervision layer '
     'can prove they produced, so the historian matters as much as the inverter.',
     [('Scope',
       'Plant controls and monitoring for utility-scale solar generation.'),
      ('Reach', 'Projects delivered across the United States.')],
     'setor/solar', [600, 900],
     'Utility-scale photovoltaic array'),

    ('Federal', 'Delivered under <br>government contract',
     'We are a registered federal contractor, and the vendor profile below is the '
     'one procurement systems ask for. The engineering does not change under a '
     'federal contract. The documentation does, and we write it either way.',
     [('UEI &middot; CAGE',
       '<span class="mono">XUZ4WKEZLS67</span> &middot; '
       '<span class="mono">9ZJM6</span>'),
      ('Primary NAICS',
       '<span class="mono">541511</span>, custom computer programming '
       'services, with six secondary codes on file.')],
     'setor/federal', [600],
     'Engineer commissioning a control system at a command station'),
]


# O resumo que fecha a pagina. Curto de proposito: o painel acima ja e o
# conteudo, e isto e a conta que o comprador leva embora.
# A fotografia de fundo entra numa FAIXA de 62%, nao na secao inteira: a fonte
# e 1920x734 e a secao tem ~630 px de altura a 1440 -- cobrir tudo obrigaria a
# ampliar, que e o erro que "Since 2000" custou. Na faixa ela e REDUZIDA 0,750x.
# A FOTO MUDOU EM 20/08, POR DOIS MOTIVOS SOMADOS.
#
#   repeticao -- `faixa/robotica` ja e a faixa full-bleed da home, e a mesma
#     foto em dois papeis foi o que a auditoria proibiu;
#   VISIBILIDADE -- o veu daqui e OFF-WHITE e cobre .78, entao so 22% da foto
#     chega a tela. O que sobrevive a isso nao e o assunto, e a AMPLITUDE.
#     Medido o p95-p5 da luminancia DEPOIS do veu: `robotica` dava 34,8, no
#     terco inferior do acervo -- por isso lia como lavagem cinza. A nova da
#     46,2.
#
# E engrenagem com corrente e um MECANISMO NEUTRO, que e o certo para "six
# sectors, one discipline": nao aponta setor nenhum, ao contrario da celula
# robotica, que apontava so o automotivo.
# Medicao completa em ferramentas/previa_ledger.py.
# A SECAO DEIXOU DE SER OFF-WHITE. Ela e agora a metade de cima de uma DUPLA,
# e a dupla e escura por construcao -- as duas secoes cedem o fundo para o
# involucro que segura a fotografia. A alternancia de superficie que esta
# secao trazia (registrada em 20/08) se perde; o que entra no lugar e o par
# lendo como um bloco unico, que foi o pedido.
# O SINOPTICO GANHOU SECAO PROPRIA (20/08). Ele estava dentro do bloco de
# abertura, espremido logo abaixo do texto de introducao: a secao e
# `--compacta` (96 px de respiro contra os 160 normais) e a peca ficava sem
# ar nenhum, encostada no paragrafo. E chegava ANTES das seis fichas, ou seja,
# antes de o visitante saber o que a pagina e.
#
# Agora ela vem DEPOIS do registro de obras, que e a ordem que a pagina conta:
# primeiro o que foi entregue, depois a tela que ficou rodando. E abre com o
# mesmo bloco de duas colunas de todas as outras secoes do site.
SINOPTICO = '''
<section class="secao secao--offwhite">
  <div class="container">
    <div class="bloco reveal">
      <div class="bloco__esq">
        <p class="eyebrow">What stays behind</p>
        <h2>The screen that <br>runs the shift</h2>
      </div>
      <div class="bloco__dir">
        <p class="corpo">Every one of those projects ends the same way: an operator gets a
        screen. This is what one looks like: levels, flow, pump state and the alarm
        that matters, on a plant that never stops long enough to be forgiving.</p>
      </div>
    </div>
    ''' + peca(
        'mimico', 'data-mimico',
        'SUPERVISORY MIMIC &middot; DEMONSTRATION',
        cota_peca([('SCADA', 'screen as delivered'),
                   ('TAGS', 'generic'), ('VALUES', 'simulated')])) + '''
  </div>
</section>
'''



# ============================================ REGISTRO DE CONTRATOS
# A CAMADA QUE FALTAVA, e ela e a que o comprador federal le primeiro.
#
# O site antigo publica tres contratos com data de inicio e valor. A migracao
# tinha perdido os tres: a pagina nova contava a mesma coisa por SETOR, que le
# muito melhor para um visitante comercial e nao serve para avaliacao de past
# performance -- ali o que se pede e data, valor e referencia, e narrativa nao
# substitui nenhum dos tres.
#
# ONDE ELA ENTRA, e por que nao no fim. A ordem da pagina passa a ser:
#
#   as seis folhas de setor .... o que a empresa faz, qualitativo
#   o registro de contratos .... o que foi comprado, com data e cifra
#   o sinoptico ................ a tela que fica rodando
#   a conta final .............. 279 / 158 / 78, o agregado
#
# Especifico depois de qualitativo, agregado por ultimo. Pos-lo no fim jogaria
# o dado duro DEPOIS do numero redondo, e o numero redondo e o que menos prova.
#
# OS TRES SAO DO MESMO CLIENTE, e isso e o achado da conferencia: na fonte o
# paragrafo de Arcadia precede os tres projetos e nao ha outro cliente na
# pagina. Apresenta-los como tres clientes diferentes seria inventar alcance;
# apresenta-los como um programa de tres contratos e o que a fonte diz -- e le
# melhor, porque relacao que se renova tres vezes em tres anos prova mais que
# tres trabalhos avulsos.
#
# ORDEM CRONOLOGICA, nao a da fonte. La eles saem 09/2022, 03/2024, 08/2021 --
# sem ordem nenhuma. Em ordem, a tabela conta que a relacao comecou em 2021 e
# ainda estava sendo renovada em 2024, que e exatamente a leitura que "over
# three years" afirma em prosa.
CONTRATOS_PP = '''
<section class="secao secao--offwhite">
  <div class="container">
    <div class="bloco reveal">
      <div class="bloco__esq">
        <p class="eyebrow">Contract record</p>
        <h2>Three contracts, <br>one plant</h2>
      </div>
      <div class="bloco__dir">
        <p class="corpo">The sheets above are what we do. This is what was bought. A
        municipal wastewater treatment plant in Arcadia, Florida has renewed with us
        three times since 2021: SCADA, PLC and motor control on a facility that
        cannot be taken offline to be fixed.</p>
      </div>
    </div>
    ''' + contratos(
        'SCADA support, wastewater treatment plant, Arcadia, Florida',
        [('08 / 16 / 2021', '', '$150,000.00'),
         ('09 / 21 / 2022', '', '$35,000.00'),
         ('03 / 18 / 2024', '04 / 30 / 2024', '$99,450.00')],
        ('Three contracts, combined', '$284,450.00'),
        # A nota absorveu a coluna "Reference", que trazia o MESMO texto nas
        # tres linhas. Ela diz o que a coluna dizia, uma vez so, e no lugar
        # onde uma nota de rodape pertence.
        '<b>References for all three are provided on request</b>, with the '
        'plant&rsquo;s consent. Where no end date is shown, none is recorded '
        'against that contract.') + '''
  </div>
</section>
'''

RESUMO_PP = '''
<section class="secao secao--escura">
  <div class="container">
    <div class="bloco reveal">
      <div class="bloco__esq">
        <p class="eyebrow">The ledger</p>
        <h2>Twenty-six years, <br>counted</h2>
      </div>
      <div class="bloco__dir">
        <p class="corpo">Six sectors, one discipline. What changes between a refinery and
        a body shop is the process and the consequence of getting it wrong, not the
        rigor the control system deserves. The numbers below are projects delivered, not
        proposals written.</p>
      </div>
    </div>
    ''' + NUMEROS + '''
  </div>
</section>
'''


def desempenho():
    """Past performance: a pagina que o cliente marcou como o diferencial.

    Era uma pilha de quatro secoes iguais -- bloco de texto mais tabela de
    dados, repetido. Cada setor tinha o mesmo peso visual e o mesmo layout,
    entao a pagina lia como relatorio: nada dizia onde olhar, e um comprador
    que entrasse procurando o SEU setor tinha de varrer tudo.

    Agora e um painel PRESO: um setor por vez, a rolagem avanca, as setas
    giram e a volta e infinita. Cada setor ocupa a tela quando e a vez dele,
    com a fotografia montada ao lado da tese e dos dados.
    """
    # O bloco que apresenta o registro. Ele existe porque a pagina nao pode
    # saltar do cabecalho direto para a primeira ficha: sem uma frase que diga
    # o que a pilha e, as seis fichas comecam do nada -- que era metade da
    # queixa de "as secoes nao se conectam suavemente". As outras oito paginas
    # do site abrem toda secao com este mesmo bloco de duas colunas; esta era a
    # unica que nao abria.
    abertura = '''
<section class="secao secao--compacta">
  <div class="container">
    <div class="bloco reveal">
      <div class="bloco__esq">
        <p class="eyebrow">The record</p>
        <h2>Six sectors, <br>one discipline</h2>
      </div>
      <div class="bloco__dir">
        <p class="corpo">Each sheet below is one sector: what the plant had to do, who it
        was for, and what we were responsible for. What changes between a refinery and a
        body shop is the process and the consequence of getting it wrong, not the
        rigor the control system deserves.</p>
      </div>
    </div>
  </div>
</section>'''

    corpo = cabecalho(
        'Past performance', 'What already <br>runs in the field',
        '279 automation projects worldwide, 158 in the United States, 78 in Florida. '
        'These are some of them.',
        'cabecalho/projetos', [1125],
        'Robotic cell assembling a vehicle body',
        'Past Performance', reticula=False) + abertura + registro_obras(SETORES_PP) + CONTRATOS_PP + SINOPTICO         + '''
<!-- DUPLA: o resumo e o CTA sob UMA fotografia. `--d-abre/--d-fecha` em
     42-52%: a faixa livre daqui fica entre o fim da banda de numeros e o
     eyebrow do CTA. -->
<div class="dupla" style="--d-abre:42%; --d-fecha:52%">
  ''' + imagem('dupla/engrenagem', [1280, 1920, 2560],
               'Gear and roller chain drive on industrial machinery',
               '100vw', classe='dupla__foto') + '''
''' + RESUMO_PP + CONTATO_CTA + '''
</div>'''
    return pagina(
        'past-performance.html', 'Past Performance | i3 Automations &amp; Controls',
        'Daimler/Mercedes-Benz New Body Shop, BMW F15/F16/F25/F26 SSB, PI System with '
        '150,000+ tags in Houston, Florida water utilities and U.S. solar.',
        # `setores.js` SAIU junto com o carrossel: o registro nao tem estado, e
        # a unica coisa que se move nele e `reveal`, que o main.js ja resolve.
        corpo, scripts_extra=('mimico.js',), og_img='img/og/past-performance-1200.jpg', trilha_seo='Past Performance')


# =============================================================== SERVICES
def servicos():
    """Mode PERSUADE: o visitante decide e age.

    A pagina apresenta o PRODUTO, em quatro perguntas na ordem em que um
    comprador as faz: como eu contrato, o que vem na caixa, como o trabalho
    corre, e em que voces trabalham. Cada uma tem um componente proprio, e
    nenhum deles e um card generico.
    """
    corpo = '''
<!-- O HERÓI DE SERVICES, pedido em 2026-08-27: "a pagina services precisa
     começar com um video, tipo o heroi da home".

     É `.heroi` INTEIRO E NÃO UMA CÓPIA: a caixa, o vídeo em `cover`, o botão
     de pausa (WCAG 2.2.2), o nav transparente e a entrada linha a linha vêm
     todos de lá. A única diferença é `--veu-heroi`, que fecha de .25 para .55
     porque o clipe é claro no quadro inteiro — a medição está em style.css,
     em `.heroi--servicos`.

     A TRILHA ENTRA AQUI. O cabeçalho fotográfico saiu, e com ele a única
     navegação de contexto da página; ela desce para o herói em vez de
     desaparecer. É a diferença entre esta dobra e a da home, que não tem
     trilha porque a home é a raiz. -->
<section class="heroi heroi--servicos" id="top">
  <video class="heroi__midia" id="heroi-servicos-video"
         autoplay muted loop playsinline preload="auto"
         poster="img/video/heroi-servicos.jpg"
         aria-label="Photovoltaic module moving along a conveyor under test lamps.">
    <source src="video/heroi-servicos.webm" type="video/webm">
    <source src="video/heroi-servicos.mp4" type="video/mp4">
  </video>
  <div class="heroi__veu" aria-hidden="true"></div>

  <div class="heroi__container">
    <div class="heroi__texto">
      <!-- SEM EYEBROW, e a medição decidiu antes do gosto. Sobre este clipe
           velado a .55, na faixa em que o eyebrow nasceria (rgb 84,108,130 no
           pior quadro), nenhum dos dois azuis de accent serve como texto
           pequeno:

             --azul-luz  #88B4DD ... 2,50:1   REPROVA
             sobre foto  #B9D2EA ... 3,50:1   REPROVA
             branco      #FFFFFF ... 5,45:1   passa

           Branco é a única cor que passa — e branco aqui poria uma segunda
           coisa branca a competir com o H1, que é quem manda na dobra.

           E ele não faz falta: a trilha logo abaixo já diz "Home / Services",
           o nav marca a página com `aria-current`, e o herói da home — que é o
           modelo desta dobra — nunca teve eyebrow. Seria a mesma palavra duas
           vezes na mesma dobra, na única cor que disputaria com o título. -->
      <h1 class="heroi__titulo">
        <span class="entra-linha" style="--i:0">How you buy</span>
        <span class="entra-linha" style="--i:1">the work.</span>
      </h1>
      <p class="heroi__apoio">
        <svg class="heroi__regua" viewBox="0 0 2 100" preserveAspectRatio="none"
             aria-hidden="true" focusable="false">
          <line x1="1" y1="0" x2="1" y2="100" pathLength="100"/>
        </svg>
        New system, retrofit, panel services or annual support, and the
        option to design your own system with us instead of taking ours off
        the shelf.
      </p>
      <p class="trilha"><a href="index.html">Home</a><span>/</span>Services</p>
    </div>
  </div>

  <button class="heroi__pausa" type="button" data-pausa="heroi-servicos-video"
          aria-pressed="false" aria-label="Pause background video">
    <svg class="heroi__pause" viewBox="0 0 16 16" aria-hidden="true"><rect x="3" y="2" width="3.6" height="12"/><rect x="9.4" y="2" width="3.6" height="12"/></svg>
    <svg class="heroi__play" viewBox="0 0 16 16" aria-hidden="true"><path d="M3.5 2l10 6-10 6z"/></svg>
  </button>
</section>

<section class="secao" id="engagements">
  <div class="container">
    <div class="bloco reveal">
      <div class="bloco__esq">
        <p class="eyebrow">Engagements</p>
        <h2>Four ways <br>this usually starts</h2>
      </div>
      <div class="bloco__dir">
        <p class="corpo">Most of our work arrives as one of these four. Any of them can
        turn into the others, and often does: a support contract that uncovers an
        obsolete PLC becomes a retrofit, and a panel call that keeps repeating becomes
        the next new system.</p>
      </div>
    </div>
    ''' + ofertas([
        ('New system', 'You have a process and no control system, or one at the end '
         'of its life.',
         'Control philosophy, panel build, PLC and SCADA, instrumentation, '
         'commissioning.',
         'A documented system, and drawings that match what is on the wall.'),
        ('Retrofit &amp; migration', 'The plant runs, but the PLC, HMI or historian is '
         'obsolete or unsupported.',
         'Assessment, migration plan, and a cutover that fits the outage window you '
         'actually have.',
         'Current hardware on the same process, without the operators relearning '
         'their plant.'),
        ('Panel services', 'One panel or one intermittent fault keeps coming back and '
         'nobody can reproduce it.',
         'Panel repair and modification, troubleshooting on the floor, and the '
         'drawing corrected.',
         'The fault found and written down, so the next person does not start from '
         'zero.'),
        ('Annual support', 'A system is live and has to stay live, ours or '
         'someone else&rsquo;s.',
         'Scheduled checks, remote diagnosis, corrective work, and the reporting '
         'that proves the plant behaved.',
         'An engineer who already knows your process before you call.'),
    ]) + '''
  </div>
</section>

<!-- "IN EVERY SCOPE" GANHOU FOTOGRAFIA DE FUNDO em 2026-08-27, a pedido:
     "esta boa, mas precisa de uma foto de fundo e animações de hover no
     texto".

     E A FOTOGRAFIA DECIDIU A SUPERFÍCIE. A dobra era off-white; medido sobre
     `faixa/gabinete` (média local 12x12, p2 dos blocos), nenhum véu claro
     serve — o texto secundário reprova em toda linha, e fechar o véu até
     passar apaga a foto. A tabela está em style.css, em `.dados--entrega`.
     A seção vira escura e usa o véu já medido de `.secao--foto`.

     O ASSUNTO É O ARGUMENTO. `faixa/gabinete` é o interior de um painel com
     CLPs, borneiras e chicote — e os quatro entregáveis desta dobra
     (esquema, código, registro de ensaio, treinamento) são exatamente o que
     documenta este gabinete. A lista fica POR CIMA da coisa que ela descreve.

     A foto existe desde 20/08 como `galeria/painel-clp`, num mosaico de
     400-800px. A fonte tem 7008px: esta é a primeira vez que ela sai em
     tamanho de seção. -->
''' + secao_com_foto('''<section class="secao secao--escura" id="deliverables">
  <div class="container">
    <div class="bloco reveal">
      <div class="bloco__esq">
        <p class="eyebrow">In every scope</p>
        <h2>What leaves <br>with you</h2>
      </div>
      <div class="bloco__dir">
        <p class="corpo">The same four things ship with every engagement above, and they
        are yours. An integrator who keeps the source code is selling you a dependency,
        not a control system.</p>
      </div>
    </div>

    <div class="dados dados--entrega reveal" style="margin-top: var(--gap-bloco)">
      <div class="dados__linha"><p class="dados__rotulo">Drawings</p>
      <p class="dados__valor">Panel schematics, loop sheets and as-builts that match what
      is installed, not what was designed six months earlier.</p></div>
      <div class="dados__linha"><p class="dados__rotulo">Code</p>
      <p class="dados__valor">Commented PLC and HMI source, delivered to you, in the
      platform&rsquo;s native format. No locked blocks, no runtime we hold the key to.</p></div>
      <div class="dados__linha"><p class="dados__rotulo">Test records</p>
      <p class="dados__valor">Factory acceptance results from our shop, and site
      loop-check records signed off during commissioning.</p></div>
      <div class="dados__linha"><p class="dados__rotulo">Training</p>
      <p class="dados__valor">Operator and maintenance handover at your console, on your
      process, with the people who will run it at 3 a.m.</p></div>
    </div>
  </div>
</section>''', 'faixa/gabinete', [1280, 1920, 2560],
        'Control cabinet interior with PLCs on DIN rail, terminal blocks and '
        'field wiring') + '''

<!-- MÉTODO E PLATAFORMAS VIRARAM UMA SEÇÃO SÓ em 2026-08-27, a pedido:
     "How the work runs e platforms precisam ser mesclado em uma unica
     sessão".

     E A COSTURA JÁ EXISTIA NO TEXTO. O passo 02 é "Choose the strategy", e o
     parágrafo das plataformas dizia, sozinho numa seção separada, que a
     escolha de plataforma "is a decision about the process and about who
     maintains it after we leave". Isso não é outro assunto — é o passo 02
     contado por outro lado. Separadas, a página fazia duas vezes a mesma
     pergunta; juntas, a escada vira a resposta concreta de um dos quatro
     passos que acabaram de ser desenhados.

     A ESCADA CONTINUA EM CAPABILITIES, e a repetição é deliberada agora que
     está anotada: lá as oito plataformas respondem "em que somos
     certificados", partidas em dois rails rotulados; aqui respondem "qual
     delas o SEU projeto vai usar, e quem mantém depois". Mesmo dado, duas
     perguntas — e por isso o parágrafo daqui não repete o argumento de
     certificação, aponta para ele. -->
<!-- OFF-WHITE E NÃO BRANCO. Com a mesclagem a página perdeu uma seção, e com
     ela perdeu a única faixa de meio-tom que tinha: o ritmo ficaria herói
     escuro → branco → escuro → BRANCO → escuro → escuro, que alterna mas só
     tem dois tons. `design.md` §1.4 é explícito — o salto de quase-branco a
     quase-preto sem faixa média é a causa raiz do feedback do cliente que
     originou a revisão inteira. Esta é a seção que devolve o meio-tom. -->
<section class="secao secao--offwhite" id="method">
  <div class="container">
    <div class="bloco reveal">
      <div class="bloco__esq">
        <p class="eyebrow">How the work runs</p>
        <h2>Strategy first, <br>hardware second</h2>
      </div>
      <div class="bloco__dir">
        <p class="corpo">The same four steps on every engagement. The numbers here are a
        real sequence: each step is the input to the next, and skipping one is how
        a project ends up with a bigger PLC and the same bad loop.</p>
      </div>
    </div>
    ''' + diagrama([
        ('01', 'Understand the process',
         'P&amp;IDs, existing logic, and a conversation with whoever runs the '
         'plant at night. The constraints are rarely in the drawings.'),
        ('02', 'Choose the strategy',
         'Control philosophy, alarm rationalisation and the instrument list '
         'that follows from them, in that order, never the reverse.'),
        ('03', 'Build and test',
         'The panel is wired and tested in our shop, and the code is simulated '
         'against it before either one reaches your site.'),
        ('04', 'Commission and hand over',
         'Loop checks, startup, operator training, and as-built drawings that '
         'match the installation. Then annual support if you want it.'),
    ]) + '''

    <!-- A ESCADA DE OITO DEGRAUS SAIU DAQUI em 2026-08-27, e a pergunta que a
         tirou foi do usuário: *"faz sentido existir isso e a tabela de
         tecnologias ali?"*. Faz sentido a PERGUNTA; não fazia sentido o
         CATÁLOGO. Quatro razões, e nenhuma é de gosto:

         1. ERA DUPLICATA LITERAL DA ÂNCORA DE CAPABILITIES. As mesmas oito
            plataformas, com os mesmos sub-rótulos. E capabilities é a página
            chamada "Certified where it matters" — a escada é o argumento
            dela, não um adorno.

         2. E ERA A VERSÃO VELHA. Capabilities partiu a escada em dois rails
            rotulados ("Certified on" / "Fluent in") em 26/08, justamente
            porque num rail só o visitante tinha de DEDUZIR que contato cheio
            significa certificação — e `plano.md` §1 regra 10 não deixa
            explicar isso numa legenda. Services tinha ficado com o rail único.

         3. AS PLATAFORMAS JÁ APARECEM DUAS VEZES EM CAPABILITIES — na lista
            das oito disciplinas ("Rockwell, Siemens and Schneider" em PLC
            Programming; "Ignition, VTScada and Canary" em SCADA Programming)
            e na escada. Com services eram quatro aparições da mesma lista.

         4. O PRÓPRIO PARÁGRAFO ENTREGAVA O JOGO: ele terminava em "The
            certifications themselves are on Capabilities". Mostrar uma cópia
            logo acima do link que aponta para o original é redundância
            assumida.

         O QUE FICA É A DECISÃO, NÃO O CATÁLOGO. Em services o comprador não
         quer a lista comentada; quer duas coisas — "vocês trabalham com a
         minha?", que é uma olhada, e "quem mantém isso depois que vocês
         saem?", que já estava escrito. `marcas_certificacao()` responde a
         primeira sem componente novo: o chip com ponto cheio é certificação,
         o chip liso é operação, e é a mesma notação da escada na forma
         compacta que a home já usa.

         OITO CHIPS E NÃO OS SEIS DA HOME. Lá `AVEVA PI System` e `SQL Server`
         ficam de fora por serem camada de historiador e não plataforma de
         controle. Aqui entram, e a razão é a pergunta desta página: quem
         compra quer saber quem mantém o dado depois, e o historiador é
         exatamente essa parte da resposta.

         E O EYEBROW DEIXOU DE APONTAR PARA O DIAGRAMA. "Inside step 02" só
         funcionava para quem tinha acabado de ler os quatro passos: era
         navegação, não rótulo. "What it runs on" nomeia o assunto. -->
    <div class="bloco bloco--continua reveal">
      <div class="bloco__esq">
        <p class="eyebrow">What it runs on</p>
      </div>
      <div class="bloco__dir">
        <p class="corpo">Choosing the strategy is also choosing what it runs on. A filled
        dot is a platform we are certified on; the rest we work in every week. Which one
        your project uses is a decision about the process and about who maintains it
        after we leave, never about which logo we prefer. We will say so if
        the one you already own is the right answer.</p>
        ''' + marcas_certificacao(
        ('Ignition', 'VTScada', 'Canary Labs', 'Rockwell Automation', 'Siemens',
         'Schneider Electric', 'AVEVA PI System', 'SQL Server')) + '''
        <p class="corpo corpo--nota"><a href="capabilities.html">What each certification
        covers is on Capabilities</a>.</p>
      </div>
    </div>
  </div>
</section>

''' + '''
<!-- AS DUAS SECOES QUE FECHAM SERVICES DIVIDEM UMA FOTOGRAFIA SO. Antes eram
     duas fotos diferentes (refinaria em cima, teclado embaixo) e a emenda
     saltava no meio de um bloco que se le como um so.

     `dupla/comando` -- mesa de comando, mao no joystick -- e nao um painel:
     o cabecalho desta pagina ja e um close de reles e bornes, e duas fotos de
     painel na mesma pagina leem como a mesma foto duas vezes. A fonte tem
     6000 px de largura, entao a maior saida (2560) ja e uma REDUCAO de 0,43x,
     e na caixa de 1440 ela cai para 0,69x. -->
<div class="dupla">
  ''' + imagem('dupla/comando', [1280, 1920, 2560],
               'Operator hand on a joystick at a control desk with pushbuttons '
               'and HMI screens',
               '100vw', classe='dupla__foto') + '''
<section class="secao secao--escura" id="reporting">
  <div class="container">
    <div class="bloco reveal">
      <div class="bloco__esq">
        <p class="eyebrow">Your design or ours</p>
        <h2>Total control <br>and monitoring</h2>
      </div>
      <div class="bloco__dir">
        <p class="corpo">You can take one of our proven designs, or build a new one with
        us. Either way the outcome is the same: daily reporting that runs itself, and
        every operator getting the alert and the alarm message the moment an issue
        appears.</p>
        ''' + cta('contact.html', 'Send us the scope') + '''
      </div>
    </div>
    ''' + peca(
        'malha', 'data-malha',
        'PID CONTROL LOOP &middot; DRAG THE SETPOINT',
        cota_peca([('PLANT', 'first order + dead time'),
                   ('LOOP', 'PID, tuned to the process'),
                   ('DRAG', 'the setpoint')])) + '''
  </div>
</section>
''' + CONTATO_CTA + '''
</div>'''
    return pagina(
        'services.html', 'Services | i3 Automations &amp; Controls',
        'New control systems, retrofit and migration, and annual controls support. '
        'Drawings, commented code, test records and operator training in every scope.',
        # `sobre_heroi=True` desde 2026-08-27: a página abre em vídeo full-bleed,
        # então o nav nasce transparente e solidifica na rolagem, como na home.
        # Sem isto o nav sólido cortaria uma faixa navy chapada no alto do
        # clipe — que é exatamente o defeito que o herói existe para não ter.
        corpo, sobre_heroi=True,
        scripts_extra=('malha.js',), og_img='img/og/services-1200.jpg',
        trilha_seo='Services')


# ================================================================ GALLERY
GALERIA = [
    # Legenda descreve a CENA, `alt` descreve para quem nao ve. Os dois foram
    # escritos olhando cada arquivo -- alt escrito longe da imagem envelhece
    # errado, e este projeto ja corrigiu dois por isso.
    #
    # A ORDEM E CURADORIA, E ELA TEM UMA CONSEQUENCIA VISUAL. As 9 fotografias
    # autorais do cliente sao todas 600x600, e elas lideram o acervo -- e a
    # escolha editorial certa, sao o material mais valioso da pagina. Mas
    # enfileiradas em bloco elas dao ao empilhamento nove pecas de altura
    # IDENTICA, e as duas primeiras fileiras do mosaico voltavam a ser uma
    # grade -- exatamente o defeito que a proporcao nativa veio corrigir.
    #
    # Por isso `clarificador` (0,80, retrato) e `celula` (1,50, paisagem) foram
    # trazidas para as posicoes 3 e 6: a terceira coluna se desloca ja na
    # primeira fileira e o mosaico le como mosaico desde o topo. As duas sao
    # aberturas fortes por conta propria -- bacias de decantacao e celula
    # robotizada --, entao a curadoria nao perde nada com a troca.
    ('galeria/painel', [600], 'Technician working inside a live control panel',
     'Panel maintenance in the field'),
    ('galeria/scada', [600],
     'SCADA screen showing effluent station discharge flow, with a hard hat in '
     'the foreground', 'Effluent discharge flow, on shift'),
    ('galeria/clarificador', [400, 800],
     'Rectangular clarifier basins with walkways at a wastewater treatment plant',
     'Clarifier basins, wastewater treatment'),
    ('galeria/painel-campo', [600],
     'Field-installed control panel with pilot lights and selector switches, '
     'door open', 'Pump station panel, open for commissioning'),
    ('galeria/bomba', [600],
     'Submersible pump set being lowered by crane into a wet well',
     'Submersible set going into the wet well'),
    ('galeria/celula', [400, 800], 'Robotic cell assembling a vehicle body',
     'Robotic assembly cell'),
    ('galeria/obra-agua', [600],
     'Controls cabinet being installed beside weir gates under construction',
     'Weir gate structure, controls going in'),
    ('galeria/captacao', [600], 'Large-diameter pipework at a raw water intake',
     'Raw water intake, Florida'),
    ('galeria/body-in-white', [600],
     'Robots welding a car body on an automotive line',
     'Automotive body shop, body-in-white'),
    # 1,59 entre dois 1,00: quebra a corrida de quadrados das autorais, e
    # fica junto do bloco automotivo, que e onde ela pertence.
    ('galeria/robo-linha', [400, 800],
     'Six-axis robot arm serving an automated assembly line inside a '
     'production hall',
     'Robot on the assembly line'),
    ('galeria/bancada', [600], 'Engineer programming at a control panel workbench',
     'Panel programming and bench testing'),
    # Mesma fonte de `dupla/clp`, aqui na proporcao nativa. Fecha o grupo de
    # painel -- manutencao, programacao, interior e fiacao em sequencia.
    ('galeria/painel-clp', [400, 800],
     'Open control panel with PLC racks, circuit breakers, terminal blocks and '
     'wiring ducts',
     'Control panel interior, PLC racks'),
    ('galeria/fiacao', [422],
     'Hands wiring contactors and circuit breakers inside a control panel',
     'Panel wiring, contactors and breakers'),
    ('galeria/comissionamento', [600],
     'Engineer commissioning a system from a laptop at a command station',
     'Commissioning from the command station'),
    # Mesma fonte de `dupla/comando`. Entra ANTES de `sala-controle` (0,80)
    # de proposito: 1,00 / 1,50 / 0,80 / 1,50 alterna, enquanto depois dela
    # cairia num corredor de quatro 1,50 seguidos.
    ('galeria/mesa-comando', [400, 800],
     'Operator hand on a joystick at a control desk with illuminated '
     'pushbuttons and HMI screens',
     'Control desk, operator station'),
    ('galeria/sala-controle', [400, 800],
     'Operator in a high-visibility vest at a control room console with SCADA screens',
     'Control room, live process'),
    ('galeria/campo', [400, 800],
     'Two technicians in coveralls at a robot teach pendant on a plant floor',
     'Field review at the teach pendant'),
    ('galeria/braco-bancada', [400, 800],
     'Orange six-axis industrial robot arm mounted on a workbench',
     'Six-axis arm, bench setup'),
    ('galeria/bornes', [400, 800],
     'Relay modules wired to a terminal block inside a control panel',
     'Relays and terminal block'),
    ('galeria/teclado', [400, 800],
     'Hand pressing an illuminated membrane keypad on a machine control panel',
     'Membrane keypad, machine control'),
    ('galeria/refinaria', [400, 800],
     'Process units and storage tanks at a refinery',
     'Refinery process units'),
    ('galeria/prensas', [400, 800],
     'Row of industrial stamping presses on a mill floor',
     'Press line, mill floor'),
    ('galeria/prensa-detalhe', [400, 800],
     'Close view of the tooling under an industrial press',
     'Press tooling, close'),
    # 1,33 no meio da corrida mais longa de 1,50 do acervo (posicoes 17 a 23):
    # e o unico lugar em que ela paga aluguel na composicao.
    ('galeria/solda-placa', [400, 800],
     'Soldering iron working on a control board with switches and indicator '
     'LEDs',
     'Control board assembly, bench detail'),
    ('galeria/engrenagens', [400, 800],
     'Meshed gears and chain drive on industrial machinery',
     'Gear and chain drive'),
    ('galeria/agv', [400, 800],
     'Automated guided vehicle handling totes in warehouse racking',
     'Automated handling in racking'),
    ('galeria/britagem', [400, 800],
     'Conveyor and stockpile at an aggregate processing plant',
     'Conveyor and stockpile'),
    ('galeria/fiacao-textil', [400, 800],
     'Continuous filament running through a fibre processing machine',
     'Continuous filament, process line'),
    ('galeria/baterias', [400, 800],
     'Racked battery modules in an energy storage installation',
     'Battery modules, energy storage'),
    ('galeria/solar-campo', [400, 800],
     'Aerial view of a ground-mounted solar farm beside farmland',
     'Ground-mounted solar, from the air'),
    ('galeria/solar-aereo', [400, 800],
     'Rows of photovoltaic panels on a utility-scale solar plant',
     'Utility-scale photovoltaic rows'),
    ('galeria/solar-painel', [400, 800],
     'Close view of photovoltaic modules on a mounting structure',
     'Module and mounting structure'),
    ('galeria/linha-solar', [400, 800],
     'Worker in a hard hat looking down a photovoltaic module production line',
     'Module production line'),
]


def _proporcao(base, larguras):
    """Proporcao real dos arquivos que ESTA PAGINA vai referenciar.

    Ela vai para o HTML como `--ar` e vira `aspect-ratio` na moldura, o que faz
    a coluna ter a altura CERTA antes de a fotografia chegar. Sem isso o
    mosaico monta com 29 caixas de altura zero e desaba para a altura final
    conforme cada imagem baixa -- e num acervo de 29 fotos esse rearranjo e
    justamente a sensacao de "as fotos demoram e a pagina pula".

    MEDE AS LARGURAS DECLARADAS, uma a uma, e EXIGE que concordem. Nao e
    paranoia: a primeira versao varria a pasta e devolvia a primeira largura
    que achasse, e isso escondeu um defeito real. Quando `build_imagens`
    passou a preservar a proporcao nativa, quatro fotos mudaram de faixa de
    largura (de 750 para 400/800) -- e os arquivos de 750, gerados no recorte
    QUADRADO antigo, continuaram no disco. A varredura de referencias passava
    (o arquivo existia), a pagina referenciava o quadrado velho, e `--ar`
    vinha medido dele: 1.0. Tudo consistente, tudo errado.

    Medindo o que a pagina realmente pede, o mesmo erro vira uma quebra de
    build com o nome do arquivo. Um arquivo que sobra e mais perigoso que um
    que falta, porque nada acusa.
    """
    from PIL import Image
    caminho = os.path.join(os.path.dirname(__file__), '..', 'site', 'img',
                           base.replace('/', os.sep))

    def medir(w, exts):
        for suf in exts:
            f = '%s-%d.%s' % (caminho, w, suf)
            if os.path.exists(f):
                with Image.open(f) as im:
                    return im.width / im.height
        raise SystemExit('%s-%d.{%s} nao existe: rode build_imagens.py'
                         % (base, w, ','.join(exts)))

    # A maior largura e a unica que tem o formato BASE (`salvar()` so emite jpg
    # ali; as menores saem em avif/webp, que sao o que o srcset consome). Ela e
    # tambem a que o `<img src>` aponta, entao e a medida certa.
    r = medir(larguras[-1], ('jpg', 'png'))
    # As menores existem? A proporcao delas e a mesma por construcao -- `salvar`
    # redimensiona proporcionalmente --, entao o que se confere aqui e
    # PRESENCA, nao forma. Sem esta linha, uma largura declarada e nunca
    # gerada vira um `srcset` apontando para o vazio, e o navegador cai no
    # `src` sem reclamar de nada.
    for w in larguras[:-1]:
        medir(w, ('webp',))
    return r


def _empilhar(itens, colunas):
    """Distribui as figuras em N colunas, sempre na MAIS CURTA ate agora.

    Round-robin (`i % n`) seria uma linha e esta errado: com proporcoes de 0,66
    a 1,60 as tres colunas terminariam com centenas de pixels de diferenca. O
    guloso pela coluna mais curta e o mesmo criterio que `columns` do CSS usa
    internamente -- a diferenca e que aqui as colunas sao elementos de verdade,
    e por isso cada uma pode ter a propria deriva de rolagem.

    A altura de cada peca em unidades de LARGURA DE COLUNA e `1 / proporcao`
    mais a legenda; e o suficiente para equilibrar, e nao depende de a imagem
    ja ter carregado.
    """
    LEGENDA = .18                      # legenda + goteira, em larguras de coluna
    pilhas = [[] for _ in range(colunas)]
    alturas = [0.0] * colunas
    for item in itens:
        k = alturas.index(min(alturas))
        pilhas[k].append(item)
        alturas[k] += 1 / item[4] + LEGENDA
    return pilhas


def galeria():
    """Mode EXPERIENCE: a fotografia lidera, a interface recua.

    O QUE FALTAVA AQUI ERA VARIACAO, NAO ANIMACAO. O pedido foi "uma biblioteca
    de imagens precisa de mais movimento", e a primeira medicao explicou por
    que a pagina parecia parada: `build_imagens.galeria()` recortava TODAS as
    29 fotos em 1:1, entao o "mosaico por colunas" era, na pratica, uma grade
    de 29 quadrados iguais. Nenhuma quantidade de animacao conserta isso -- uma
    grade uniforme continua uniforme se mexer.

    Corrigido na origem: a galeria passou a sair na proporcao NATIVA de cada
    fonte, aparada em 0,66..1,60. Agora ha retrato, quadrado e paisagem na
    mesma coluna, e o mosaico e um mosaico.

    COLUNAS DE VERDADE, NAO `columns`. A propriedade `columns` do CSS montava
    isto sozinha, e foi trocada por tres elementos por um motivo so: coluna que
    e elemento pode ter DERIVA PROPRIA na rolagem. E o que da profundidade a um
    acervo -- as colunas correm em velocidades ligeiramente diferentes, e o
    plano se abre. Com `columns` nao ha o que animar: e uma caixa so.

    E A DERIVA NAO E DESLOCAMENTO PARADO. As tres colunas nascem ALINHADAS no
    topo e so se separam enquanto a pagina rola. Escalonar a origem delas seria
    repetir a "escada que sobe e desce" que o usuario acabou de reprovar na
    prancha da home -- e ele tem razao: o site alinha, e o movimento e que
    quebra o alinhamento, nunca o repouso.
    """
    itens = [(base, larg, alt, leg, _proporcao(base, larg))
             for base, larg, alt, leg in GALERIA]

    def figura(item, n):
        base, larg, alt, leg, ar = item
        return (
            '<figure class="galeria__figura" data-progresso data-ar="%.4f" '
            'data-ordem="%d" style="--ar:%.4f">'
            '<div class="galeria__item">%s'
            '<span class="galeria__marca" aria-hidden="true"></span>'
            '</div>'
            '<figcaption class="galeria__legenda">'
            '<span class="galeria__num">%02d</span>'
            '<span class="galeria__txt">%s</span>'
            '</figcaption></figure>'
            % (ar, n - 1, ar,
               imagem(base, larg, alt,
                      '(max-width: 700px) 92vw, (max-width: 1100px) 46vw, 30vw'),
               n, leg))

    ordem = {id(it): i for i, it in enumerate(itens)}
    colunas = ''.join(
        '<div class="galeria__coluna" style="--c:%d">%s</div>'
        % (c, ''.join(figura(it, ordem[id(it)] + 1) for it in pilha))
        for c, pilha in enumerate(_empilhar(itens, 3)))

    corpo = cabecalho(
        'Gallery', 'The work, <br>and where it happens',
        'Panels, control rooms, plant floors and the plants themselves: '
        'the environments this company builds control systems for.',
        'cabecalho/galeria', [1125],
        'Industrial robot arm in a production cell',
        'Gallery', reticula=False) + '''
<section class="secao">
  <div class="container">
    <div class="bloco reveal">
      <div class="bloco__esq">
        <p class="eyebrow">The archive</p>
      </div>
      <div class="bloco__dir">
        <!-- A afirmacao "every photograph here is from a job we did" SAIU, e a
             saida foi deliberada: a galeria mostra o acervo inteiro, e nem toda
             foto e de obra propria. Uma pagina que AFIRMA autoria e mostra
             outra coisa e pior do que uma que nao afirma nada. -->
        <p class="lead">Some of these are our own jobs, photographed on site. Others are
        the kind of plant and equipment we work in every week. Together they are the
        environment the control systems on this site live in.</p>
        <p class="galeria__conta mono">%d plates &middot; panels, commissioning, control
        rooms, water, automotive and solar</p>
      </div>
    </div>
  </div>
  <div class="galeria__mosaico" data-mosaico data-progresso data-colunas="3">%s</div>
</section>
''' % (len(itens), colunas) + CONTATO_CTA
    return pagina(
        'gallery.html', 'Gallery | i3 Automations &amp; Controls',
        'Photographs from i3Automations projects and the industrial environments we '
        'work in: control panels, commissioning, control rooms, water plants and solar.',
        # `mosaico.js` so REEMPILHA quando o numero de colunas muda. O
        # empilhamento inicial vem pronto do gerador, entao a pagina sem
        # JavaScript continua com as tres colunas equilibradas.
        corpo, scripts_extra=('mosaico.js',), og_img='img/og/gallery-1200.jpg', trilha_seo='Gallery')


# ================================================================ CONTACT
def contato():
    redes = ''.join(
        '<li><a href="%s" target="_blank" rel="noopener">%s</a></li>'
        % (u, n) for n, u in REDES)

    # A foto de "Since 2000" fica sob veu BRANCO (.78 no miolo, .56 nas
    # laterais): com texto escuro sobre veu claro o pior caso e o ponto mais
    # ESCURO da foto, e ali o corpo mede 14,21:1.
    extras = {
        'foto_desde': imagem('faixa/robotica', [1280, 1920],
                             'Robotic handling cell in a distribution facility',
                             '100vw', classe='secao__foto'),
        'foto_missao': imagem('cabecalho/servicos', [1280, 1920],
                              'Relay and terminal wiring inside a control panel',
                              '100vw', classe='secao__foto'),
        'diagrama': diagrama([
            ('01', 'Understand the process',
             'P&amp;IDs, existing logic, and a conversation with whoever runs the '
             'plant at night. The constraints are rarely in the drawings.'),
            ('02', 'Choose the strategy',
             'Control philosophy, alarm rationalisation and the instrument list '
             'that follows from them, in that order, never the reverse.'),
            ('03', 'Build and test',
             'The panel is wired and tested in our shop, and the code is simulated '
             'against it before either one reaches your site.'),
            ('04', 'Commission and hand over',
             'Loop checks, startup, operator training, and as-built drawings that '
             'match the installation. Then annual support if you want it.'),
        ]),
    }
    corpo = cabecalho(
        'Contact', 'Tell us what the <br>process has to do',
        'Two phone lines, one inbox, and an engineer on the other end of all three.',
        'cabecalho/contato', [1280, 1920],
        'Hand pressing an illuminated membrane keypad on a machine control panel',
        'Contact', reticula=False) + '''
<!-- REPENSADO EM 2026-08-27, a pedido: *"repense o layout de contact us (...)
     deixe o mapa e redes sociais e contatos"*.

     O DIAGNOSTICO, e ele e de AGRUPAMENTO antes de ser de estilo.

     A pagina tinha quatro dobras e o endereco aparecia em DUAS delas, a tres
     secoes de distancia uma da outra: o bloco "Offices -- Lakewood Ranch, FL /
     Houston, TX" vivia na secao 2, e a CARTA que desenha exatamente esses dois
     pontos vivia no fim da secao 4. O mapa e a legenda dele estavam separados
     por toda a pagina.

     E a secao 4 juntava duas perguntas diferentes sob um titulo que so
     respondia uma: "Where else we show up" fala de redes sociais, e embaixo
     dela estava o mapa, que fala de geografia.

     TERCEIRO DEFEITO, de ordem de leitura: a secao 2 abria com DOIS paragrafos
     explicando por que a pagina nao tem formulario -- ou seja, a pagina se
     justificava antes de servir, no ponto de maior atencao dela. A decisao de
     nao ter formulario continua certa e continua dita; passa a caber numa
     frase, depois dos telefones.

     A ESTRUTURA NOVA, tres dobras em vez de quatro:

       branco ..... "Reach us"        os tres canais, primeiro
       escuro ..... "Where to find us" o mapa + as redes -- as duas formas de
                                       ACHAR a empresa, fisica e online
       off-white .. "For contracting officers"  as credenciais

     O bloco "Offices" sai de `.contato` porque a cota da carta ja nomeia as
     duas cidades: repetir ali seria dizer o mesmo duas vezes na mesma pagina
     pela segunda vez. `.contato` e `auto-fit`, entao tres blocos preenchem a
     linha sem nenhum ajuste.

     AS REDES FICAM NA DOBRA ESCURA e nao na branca, e a razao e de estilo e
     de sentido ao mesmo tempo: `.canais` foi desenhado para superficie escura
     (regua em `--filete`, hover em #fff), e "onde nos achar" e a mesma
     pergunta que o mapa responde -- uma no espaco, outra na rede. -->
<section class="secao" id="reach">
  <div class="container">
    <div class="bloco reveal">
      <div class="bloco__esq">
        <p class="eyebrow">Reach us</p>
        <h2>Three ways, <br>and a person on each</h2>
      </div>
      <div class="bloco__dir">
        <p class="lead">Send the scope, the P&amp;ID, or just the problem. If the answer
        is that you do not need us, we will say that too.</p>
      </div>
    </div>

    <div class="contato reveal">
      <div class="contato__bloco">
        <p class="contato__rotulo">Sales &amp; Services</p>
        <p class="contato__valor"><a href="tel:+14078200299">%(vendas)s</a></p>
        <p class="contato__nota">New projects, quotes and scoping. Also on
        <a class="link" href="%(zap)s" target="_blank" rel="noopener">WhatsApp</a>.</p>
      </div>
      <div class="contato__bloco">
        <p class="contato__rotulo">Support</p>
        <p class="contato__valor"><a href="tel:+19416661880">%(suporte)s</a></p>
        <p class="contato__nota">Systems already running, and annual support
        contracts.</p>
      </div>
      <div class="contato__bloco">
        <p class="contato__rotulo">E-mail</p>
        <p class="contato__valor"><a href="mailto:%(email)s">%(email)s</a></p>
        <p class="contato__nota">Best channel for drawings, scope documents and RFQs.</p>
      </div>
    </div>

    <p class="corpo corpo--nota">No contact form, on purpose: it adds a step and answers
    nothing. The three above reach the same people faster.</p>
  </div>
</section>

<section class="secao secao--escura" id="where">
  <div class="container">
    <div class="bloco reveal">
      <div class="bloco__esq">
        <p class="eyebrow">Where to find us</p>
        <!-- "AND A BENCH IN HOUSTON" SAIU, e a frase seguinte com ela.
             As duas afirmavam o que o acervo nao sustenta: nada no site diz
             que ha oficina ou pessoal fixo em Houston -- past-performance diz
             que a CARTEIRA de oil & gas fica la ("our oil and gas client base
             sits in Houston, Texas"), e o site antigo diz o mesmo. "Bench"
             promete bancada; "on site the same day" promete tempo de resposta
             de 1.289 km de distancia. Nenhuma das duas e verificavel, e o
             cliente e fornecedor federal (design.md §7.1).

             O que ficou e o que a propria carta desenha: HQ de um lado,
             OIL & GAS do outro, 801 milhas entre eles. -->
        <h2>An office in Florida, <br>a client base in Texas</h2>
      </div>
      <div class="bloco__dir">
        <p class="corpo">The office is in Lakewood Ranch, Florida. The oil and gas client
        base sits in Houston, Texas. 801 miles of Gulf coast between the two, and
        both lines above reach the same people.</p>
        <ul class="canais" role="list">%(redes)s</ul>
      </div>
    </div>
    %(carta)s
  </div>
</section>

<section class="secao secao--offwhite">
  <div class="container">
    <div class="bloco reveal">
      <div class="bloco__esq">
        <p class="eyebrow">For contracting officers</p>
        <h2>Everything you <br>need to register us</h2>
      </div>
      <div class="bloco__dir">
        <p class="corpo">Our vendor profile in the format procurement systems ask for. If
        something else is required for your solicitation, ask on either line and we will
        send it the same day.</p>
      </div>
    </div>

    <div class="credencial reveal">
      <div class="credencial__item"><p class="credencial__rotulo">Legal name</p>
      <p class="contato__valor" style="margin-top: var(--s-2)">i3 Automations &amp;
      Controls</p></div>
      <div class="credencial__item"><p class="credencial__rotulo">UEI</p>
      <p class="credencial__valor">XUZ4WKEZLS67</p></div>
      <div class="credencial__item"><p class="credencial__rotulo">CAGE</p>
      <p class="credencial__valor">9ZJM6</p></div>
      <div class="credencial__item"><p class="credencial__rotulo">Primary NAICS</p>
      <p class="credencial__valor">541511</p></div>
      <div class="credencial__item"><p class="credencial__rotulo">Secondary NAICS</p>
      <p class="credencial__valor credencial__valor--multi">238210 &middot; 334513 &middot;
      335313 &middot; 518210 &middot; 541330 &middot; 541512</p></div>
      <div class="credencial__item"><p class="credencial__rotulo">Certifications</p>
      <p class="contato__valor" style="margin-top: var(--s-2)">Ignition &middot; VTScada
      &middot; Canary</p></div>
    </div>
  </div>
</section>

''' % {'vendas': TEL_VENDAS, 'suporte': TEL_SUPORTE, 'email': EMAIL,
       'zap': WHATSAPP, 'redes': redes,
       # A peca entra pelo DICIONARIO e nao partindo a string. Partir troca
       # `'''A''' % d` por `'''A''' + x + '''B''' % d`, e em Python o `%` liga
       # mais forte que o `+`: so o ULTIMO fragmento recebe o dicionario, e
       # todos os `%(chave)s` anteriores ficam literais no HTML. Foi o que
       # aconteceu -- a varredura acusou `%(zap)s` como referencia quebrada.
       'carta': peca(
           'carta', 'data-carta',
           'LAKEWOOD RANCH, FL &middot; HOUSTON, TX',
           cota_peca([('2', 'operations'), ('MERCATOR', 'WGS 84'),
                      ('GREAT CIRCLE', 'plotted')]))}
    return pagina(
        'contact.html', 'Contact | i3 Automations &amp; Controls',
        'Sales and Services +1 (407) 820-0299, Support +1 (941) 666-1880, '
        'acastro@i3automations.com. Lakewood Ranch, Florida and Houston, Texas.',
        corpo, scripts_extra=('carta.js',), og_img='img/og/contact-1200.jpg',
        trilha_seo='Contact')


def sem_comentario_config(txt):
    """Tira os comentarios de `.htaccess`, `_headers` e `_redirects`.

    A MESMA DIVISAO QUE O RESTO DO PROJETO JA FAZ: a fonte fica comentada e a
    saida vai limpa. `build_ativos.py` faz isso com CSS e JS desde sempre; os
    tres arquivos de deploy tinham escapado -- iam ao ar com 42 linhas de
    comentario em PT-BR explicando decisao interna.

    Pedido em 2026-08-27: *"elimine todo resquicio de comentario desse
    repositorio"*, com o escopo fechado no que vai ao ar.

    NOS TRES FORMATOS `#` NO INICIO DA LINHA E COMENTARIO -- Apache, Cloudflare
    Pages e Netlify concordam nisso. O `#` no MEIO da linha NAO e, e por isso o
    teste e `lstrip().startswith('#')` e nao um `split('#')`: um cabecalho de
    seguranca pode conter `#` dentro de um valor, e cortar ali quebraria a
    diretiva sem erro nenhum.

    Linha em branco duplicada tambem sai: sem os comentarios, o que sobrava
    entre dois blocos eram tres linhas vazias seguidas.
    """
    linhas = []
    for l in txt.split(chr(10)):
        if l.lstrip().startswith('#'):
            continue
        if not l.strip() and linhas and not linhas[-1].strip():
            continue
        linhas.append(l.rstrip())
    return chr(10).join(linhas).strip() + chr(10)


# ================================================================= LEGAIS
def legal(arquivo, titulo, eyebrow, h1, lead, secoes, img, larg, alt, trilha):
    blocos = ''.join('<h2>%s</h2>%s' % (t, c) for t, c in secoes)
    # A foto de "Since 2000" fica sob veu BRANCO (.78 no miolo, .56 nas
    # laterais): com texto escuro sobre veu claro o pior caso e o ponto mais
    # ESCURO da foto, e ali o corpo mede 14,21:1.
    extras = {
        'foto_desde': imagem('faixa/robotica', [1280, 1920],
                             'Robotic handling cell in a distribution facility',
                             '100vw', classe='secao__foto'),
        'foto_missao': imagem('cabecalho/servicos', [1280, 1920],
                              'Relay and terminal wiring inside a control panel',
                              '100vw', classe='secao__foto'),
        'diagrama': diagrama([
            ('01', 'Understand the process',
             'P&amp;IDs, existing logic, and a conversation with whoever runs the '
             'plant at night. The constraints are rarely in the drawings.'),
            ('02', 'Choose the strategy',
             'Control philosophy, alarm rationalisation and the instrument list '
             'that follows from them, in that order, never the reverse.'),
            ('03', 'Build and test',
             'The panel is wired and tested in our shop, and the code is simulated '
             'against it before either one reaches your site.'),
            ('04', 'Commission and hand over',
             'Loop checks, startup, operator training, and as-built drawings that '
             'match the installation. Then annual support if you want it.'),
        ]),
    }
    corpo = cabecalho(eyebrow, h1, lead, img, larg, alt, trilha) + '''
<section class="secao">
  <div class="container">
    <div class="texto-legal reveal">%s</div>
  </div>
</section>''' % blocos
    # O nome da migalha sai do proprio titulo, ate o travessao -- assim ele
    # nao vira uma terceira copia de um texto que ja existe duas vezes.
    return pagina(arquivo, titulo, lead.replace('<br>', ' '), corpo,
                  trilha_seo=titulo.split('|')[0].strip())


PRIVACIDADE = [
    ('Who this policy covers',
     '<p>This policy applies to i3 Automations &amp; Controls (&ldquo;i3Automations&rdquo;, '
     '&ldquo;we&rdquo;, &ldquo;us&rdquo;) and to this website. It explains what we collect '
     'when you visit or contact us, and what we do with it.</p>'),
    ('What we collect',
     '<p>This site has no contact form, no analytics tags, no advertising pixels and no '
     'third-party scripts. Every asset, fonts included, is served from our '
     'own domain, so browsing these pages does not report your visit to anyone else.</p>'
     '<ul><li><strong>Nothing automatic beyond server logs.</strong> Our host records '
     'standard request data such as IP address, timestamp and requested URL, kept only for '
     'security and reliability.</li>'
     '<li><strong>What you send us.</strong> If you e-mail, call or message us on WhatsApp, '
     'we hold what you send: your name, contact details and the content of your '
     'enquiry.</li>'
     '<li><strong>One local value.</strong> Whether you have dismissed the storage '
     "notice is stored in your browser's local storage. It never leaves your device and "
     'we cannot read it.</li></ul>'),
    # A SECAO NOVA EXISTE PORQUE A FAIXA APONTA PARA CA. Uma faixa de
    # consentimento que leva a uma pagina sem nada sobre armazenamento deixa o
    # visitante sem como conferir o que ela afirmou -- e o que ela afirma aqui
    # e incomum (nenhum cookie), entao e justamente o que precisa de prova.
    # O texto NAO promete "we use cookies to improve your experience": este
    # site nao poe cookie nenhum, e escreve-lo criaria a contradicao que a
    # secao existe para fechar.
    ('Cookies and local storage',
     '<p><strong>This site sets no cookies.</strong> Not for analytics, not for '
     'advertising, not for sessions. Nothing this site stores is ever attached to a '
     'request, so nothing about your browsing reaches us or anyone else.</p>'
     '<p>One value is kept in your browser&rsquo;s local storage, which is a store '
     'that stays on your device and is never transmitted:</p>'
     '<ul><li><strong>Whether you have dismissed the storage notice</strong>, so the '
     'notice does not return on every page.</li></ul>'
     '<p>It is strictly functional and holds no identifier of any kind. Clearing your '
     'browser data removes it, and the site works exactly the same without it.</p>'),
    ('How we use it',
     '<p>We use the information you send us to answer your enquiry, prepare quotations and '
     'deliver contracted work. We do not sell, rent or trade personal information, and we '
     'do not use it for advertising.</p>'),
    ('Sharing',
     '<p>We share personal information only where it is necessary to perform a contract '
     'with you, or where the law requires it. Where a project involves a federal contract, '
     'we provide the information required by the contracting authority.</p>'),
    ('Retention',
     '<p>Project correspondence is kept for as long as we support the system it relates '
     'to, and for the period required by applicable record-keeping and contracting rules. '
     'Enquiries that do not become projects are removed when they are no longer '
     'useful.</p>'),
    ('Your choices',
     '<p>You may ask what we hold about you, ask us to correct it, or ask us to delete it. '
     'Write to <a href="mailto:acastro@i3automations.com">acastro@i3automations.com</a> and '
     'we will respond. To clear the stored value, clear site data for this domain in '
     'your browser.</p>'),
    ('Changes',
     '<p>If this policy changes materially, we will publish the revised version on this '
     'page.</p>'),
]

TERMOS = [
    ('Acceptance',
     '<p>By using this website you agree to these terms. If you do not agree with them, '
     'please do not use the site.</p>'),
    ('About the content',
     '<p>The material on this site describes services offered by i3 Automations &amp; '
     'Controls. It is provided for information and does not constitute engineering advice '
     'for any specific installation. No control philosophy, instrument selection or safety '
     'decision should be made on the basis of these pages alone.</p>'),
    ('No offer or contract',
     '<p>Nothing on this site is an offer capable of acceptance. Scope, price, schedule and '
     'liability are established only in a written proposal or contract signed by both '
     'parties.</p>'),
    ('Intellectual property',
     '<p>The text, drawings, photographs, code and design of this site belong to i3 '
     'Automations &amp; Controls unless stated otherwise. Third-party names ('
     'Rockwell Automation, Siemens, Schneider Electric, Ignition, VTScada, Canary Labs, '
     'AVEVA, Mercedes-Benz, BMW and others) are the trademarks of their respective '
     'owners and appear here to describe platforms and programs we have worked with.</p>'),
    ('External links',
     '<p>Where we link to another site, we do so for convenience. We do not control those '
     'sites and are not responsible for their content or their privacy practices.</p>'),
    ('Availability',
     '<p>We aim to keep this site available and accurate, but we do not warrant that it '
     'will be uninterrupted or free of error. We may change or withdraw any part of it '
     'without notice.</p>'),
    ('Limitation of liability',
     '<p>To the extent permitted by law, i3 Automations &amp; Controls is not liable for '
     'indirect or consequential loss arising from the use of this website. Nothing here '
     'limits liability that cannot lawfully be limited.</p>'),
    ('Governing law',
     '<p>These terms are governed by the laws of the State of Florida, United States.</p>'),
    ('Contact',
     '<p>Questions about these terms: '
     '<a href="mailto:acastro@i3automations.com">acastro@i3automations.com</a>, or '
     '+1 (407) 820-0299.</p>'),
]


def nao_encontrada():
    """A pagina 404.

    NAO E ENFEITE, e a memoria ja registrava o porque: hospedagem estatica
    (Cloudflare Pages, entre outras) devolve o `index.html` com status **200**
    para qualquer caminho inexistente. Inofensivo numa demo; no dominio real,
    cada URL errada vira uma COPIA DA HOME aos olhos do buscador -- conteudo
    duplicado multiplicado por quantos links quebrados existirem apontando
    para ca.

    Com este arquivo presente, a hospedagem serve ele e devolve 404 de
    verdade. E ele leva `noindex`: pagina de erro indexada e o proprio defeito
    que ela existe para evitar.

    O BRACO MORA AQUI DESDE 2026-08-25 (design.md §8), e a realocacao tem uma
    logica que vale registrar. O cliente disse que a peca era bonita mas fora
    de assunto -- "nao vendo robos" --, e ele tem razao SOBRE O HEROI: a
    primeira dobra de uma integradora de automacao industrial nao pode dizer
    "robotica" quando robotica nao e o que ela vende.

    Numa pagina de erro a conta inverte. Aqui nao ha proposta a fazer nem
    assunto a defender: quem chega ja errou o caminho, e o que a pagina precisa
    e nao ser um beco. Uma peca que se pode girar transforma um erro em algo
    que valeu a pena ter encontrado -- e continua sendo o mesmo desenho de 45 KB
    que ja estava escrito e testado.

    E AQUI A LEGENDA DE INSTRUCAO PODE FICAR. A regra 10 de clean usa a linha
    "Drag the arm to orbit" do heroi publicado como exemplo do que nao fazer --
    porque no heroi ela pedia um gesto para entender a PROPOSTA. Num easter egg
    a instrucao E o conteudo: sem ela ninguem descobre que ha o que girar, e um
    easter egg que ninguem acha nao e um easter egg.
    """
    corpo = '''
<section class="secao secao--escura secao--erro">
  <div class="container">
    <div class="bloco reveal">
      <div class="bloco__esq">
        <p class="eyebrow">404</p>
        <!-- `h1` E NAO `h2`: a 404 era a UNICA pagina do site sem h1
             nenhum -- achado na vistoria de acabamento de 2026-08-27. As
             outras nove recebem o h1 de `cabecalho()`, e esta nao usa
             cabecalho. Sem h1 a pagina nao tem raiz de estrutura: leitor de
             tela nao acha o comeco, e o indexador nao sabe do que ela trata.
             A escala continua a de `h2` (ver `.secao--erro h1` em style.css) --
             o nivel muda, o tipo nao. -->
        <h1>This page is not <br>on the drawing</h1>
      </div>
      <div class="bloco__dir">
        <p class="corpo">The link you followed points somewhere that does not exist. The
        work is still here. Start from the capabilities, the record of what already
        runs in the field, or talk to an engineer.</p>
        ''' + cta('capabilities.html', 'All capabilities') + '''
      </div>
    </div>

    <div class="erro__peca">''' + BRACO + '''</div>
  </div>
</section>
''' + CONTATO_CTA
    return pagina(
        '404.html', 'Page not found | i3 Automations &amp; Controls',
        'The page you asked for is not here.', corpo, indexavel=False,
        scripts_extra=('braco.js',))


def main():
    feitos = []
    feitos.append(home())
    feitos.append(quem_somos())
    feitos.append(capacidades())
    feitos.append(desempenho())
    feitos.append(servicos())
    feitos.append(galeria())
    feitos.append(contato())
    feitos.append(nao_encontrada())
    feitos.append(legal(
        'privacy-policy.html', 'Privacy Policy | i3 Automations &amp; Controls',
        'Legal', 'Privacy Policy',
        'What this site collects, what we do with it, and what you can ask us to do about '
        # AS DUAS PAGINAS LEGAIS PERDERAM A FOTOGRAFIA DE CABECALHO em
        # 2026-08-25, e a razao veio de `ferramentas/repetidas.py`: as duas
        # vestiam a MESMA foto que uma pagina de conteudo -- privacy usava
        # `cabecalho/quem-somos` e terms usava `cabecalho/capacidades`.
        #
        # Ate esta rodada a colisao era invisivel, porque who-we-are era a
        # unica pagina SEM foto de cabecalho (a marca 3D ocupava a direita).
        # Com `marca.js` fora, who-we-are recebeu a foto que leva o nome dela,
        # e a duplicata apareceu.
        #
        # Nao ha uma setima foto de cabecalho no acervo -- as seis existentes
        # pertencem, por assunto e por nome, as seis paginas de conteudo. E
        # inventar uma para uma politica de privacidade seria resolver o
        # problema errado: uma pagina legal e um DOCUMENTO, e nao tem hero.
        # `img_base=None` da o campo chapado com a reticula, que e o desenho
        # do bloco -- o mesmo que who-we-are usava ate agora.
        'it.', PRIVACIDADE, None, None, None, 'Privacy Policy'))
    feitos.append(legal(
        'terms-and-conditions.html',
        'Terms and Conditions | i3 Automations &amp; Controls',
        'Legal', 'Terms and <br>Conditions',
        'The terms that govern the use of this website.', TERMOS,
        None, None, None, 'Terms and Conditions'))

    # CSS e JS: da fonte comentada para o site/ enxuto. Roda ANTES do
    # relatorio para o total impresso ser o que vai ao ar.
    import build_ativos
    build_ativos.main()
    print('')

    # `--demo` marca a saida como endereco de DEMONSTRACAO: o `_headers` ganha
    # `X-Robots-Tag: noindex`. Publicar em *.pages.dev sem isso poe uma copia
    # do site competindo com o dominio oficial no buscador.
    DEMO = '--demo' in sys.argv

    # SEO: sitemap e robots saem do MESMO lugar que as paginas, e nao a mao.
    import datetime
    hoje = datetime.date.today().isoformat()
    # Tres arquivos de deploy, e SO UM deles vale por hospedagem: `.htaccess`
    # em Apache (que e onde este site vai), `_headers`/`_redirects` em
    # Cloudflare Pages ou Netlify. Os inertes nao atrapalham -- e publicar os
    # dois conjuntos e o que faz a troca de hospedagem nao exigir uma entrega.
    for nome, conteudo in (('sitemap.xml', sitemap(hoje)), ('robots.txt', robots()),
                           ('_headers', cabecalhos_deploy(demo=DEMO)),
                           ('_redirects', redirecionamentos_deploy()),
                           ('.htaccess', htaccess_deploy())):
        if nome in ('_headers', '_redirects', '.htaccess'):
            conteudo = sem_comentario_config(conteudo)
        caminho = os.path.join(DEST, nome)
        with open(caminho, 'w', encoding='utf-8') as fh:
            fh.write(conteudo)
        feitos.append((caminho, len(conteudo.encode('utf-8'))))

    total = 0
    for caminho, tam in feitos:
        total += tam
        print('   %6.1f KB  %s' % (tam / 1024, os.path.relpath(caminho, DEST)))
    print('')
    print('%d paginas, %.1f KB de HTML.' % (len(feitos), total / 1024))


if __name__ == '__main__':
    main()
