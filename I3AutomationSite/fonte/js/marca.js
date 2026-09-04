/* ============================================================================
   Marca — o logo i3 extrudado, em WebGL2 escrito à mão
   i3Automations · cabeçalho de who-we-are

   Terceiro desenho em aresta do site, irmão de `planta.js` (a instalação) e
   `braco.js` (o robô do herói). O núcleo comum dos três — matriz, parser de
   token, compilação de shader, enquadramento — está em `gl.js`; aqui fica só
   o que é DESTA peça.

   POR QUE A MARCA E NÃO OUTRO OBJETO. O bloco pede um desenho à direita do
   cabeçalho de "Who We Are", e a página fala da empresa. Um terceiro
   equipamento genérico seria só mais uma máquina; a marca é o único objeto que
   a página pode mostrar que É o assunto dela. E a geometria coopera: moldura,
   base, tela e o glifo "i3" são todos PERFIS PLANOS EXTRUDADOS EM LINHA RETA —
   nenhuma superfície varrida, nenhuma curva no eixo de extrusão. É o objeto
   3D mais barato que este site poderia ter, e é o mais próprio.

   A GEOMETRIA SAI DO DOM, E ISSO NÃO É PREGUIÇA.
   O perfil não está escrito neste arquivo. Ele é LIDO do `<svg>` que
   `icone_marca()` (ferramentas/build_paginas.py) já emite dentro do
   componente. O docstring daquela função avisa: "a geometria continua saindo
   daqui e de lugar nenhum mais — três cópias do mesmo caminho e uma fica para
   trás." Copiar os `d` para cá seria a terceira cópia, e o dia em que o logo
   mudasse o site passaria a ter duas marcas diferentes na mesma página: a
   plana no nav e a extrudada no cabeçalho.

   Lendo do DOM, o desenho 3D é literalmente a mesma marca. E vem de brinde a
   RESERVA: quem não tem WebGL2 fica com o SVG plano, que já estava lá.

   O achatamento das curvas é do NAVEGADOR, via `getPointAtLength` — não há
   parser de bezier aqui. O "3" do glifo é a única forma curva da marca, e
   pedir ao mecanismo que já a rasteriza para andar sobre ela é mais barato e
   mais fiel do que reimplementar cúbicas.
   ============================================================================ */
(function () {
  "use strict";

  var G = (typeof globalThis !== "undefined" ? globalThis : window).I3GL;
  if (!G) return;
  var mult = G.mult, perspectiva = G.perspectiva, olhar = G.olhar;
  var rgb = G.rgb, programa = G.programa;

  var reduzido = window.matchMedia("(prefers-reduced-motion: reduce)").matches;

  /* ============================ profundidade ============================
     Z em UNIDADES DO SVG (0..410 na horizontal), convertidas junto com x e y.
     A marca tem 410 x 258 de face; a profundidade total é 68, ou seja 17% da
     largura. Não é arbitrário: abaixo de ~10% a peça lê como adesivo girando
     e o giro não informa nada; acima de ~25% ela vira uma caixa e o desenho
     deixa de ser a marca. 17% é onde a extrusão se anuncia sem competir.

     O escalonamento em Z é o que faz o objeto ler como MONITOR e não como
     quatro placas soltas:

       moldura e base ..... -34 .. +34   (o corpo, a peça mais à frente)
       tela ............... -34 ..  +6   (recuada 28 — é o poço do monitor)
       glifo "i3" .........  +6 .. +26   (sobre a tela, 8 atrás da moldura)

     O glifo parar 8 unidades ANTES da frente da moldura é o detalhe que
     impede a leitura errada: se ele chegasse a +34 as duas frentes ficariam
     coplanares e, girando, o "i3" pareceria colado por fora do vidro. */
  var Z_FUNDO = -34, Z_FRENTE = 34, Z_TELA = 6, Z_GLIFO = 26;

  /* Fator de conversão SVG -> modelo. 100 deixa a marca com 4,1 de largura, na
     mesma ordem de grandeza do braço (~9 de altura) — o que importa só para
     as constantes de câmera abaixo terem valores legíveis. */
  var ESCALA = 100;

  /* ============================== amostragem ==============================
     Percorre o contorno de um elemento SVG e devolve os vértices do polígono,
     COM OS CANTOS PRESERVADOS.

     Amostrar por comprimento de arco em passo fixo é o caminho óbvio e está
     errado para esta marca: três dos seis elementos são retângulos, e um passo
     fixo quase nunca cai exatamente no canto — o canto sai chanfrado. Numa
     marca de cantos retos, num site cuja regra é "cantos retos em tudo", um
     chanfro de 5 unidades no logo é o tipo de erro que ninguém sabe nomear mas
     todo mundo vê.

     Então a varredura é FINA (passo ~1,2 unidade) e a decisão de guardar o
     ponto olha a CURVATURA local:

       giro > LIMIAR_CANTO ...... é canto: guarda sempre, e marca como canto
       giro > LIMIAR_RETO ....... é curva: guarda a cada `passo` de arco
       senão .................... é reta: descarta

     O terceiro caso é o que mantém a contagem baixa — a moldura devolve
     exatamente 4 pontos, e não 300 colineares. */
  var LIMIAR_CANTO = 0.35;   /* rad ~ 20°, bem acima do ruído de amostragem */
  var LIMIAR_RETO = 0.02;

  /* A AMOSTRAGEM FOI PARTIDA EM DUAS, e o motivo e medido.
     `getPointAtLength` nao guarda estado entre chamadas: cada uma re-percorre
     o caminho desde o inicio, entao amostrar n pontos custa O(n^2). Medido em
     who-we-are, com o Chrome estrangulado em 4x como o Lighthouse movel faz:

       moldura  M21 0h368v226H21z ....  990 amostras ...  1,1 ms
       tela     M41 20h328v186H41z ....  857 amostras ...  0,9 ms
       glifo    o "3" ................   382 amostras ... 66,6 ms

     As retas sao baratas porque o caminho tem 4 comandos; o "3" tem 6 curvas
     cubicas e cada chamada as re-avalia. UM elemento respondia por 95% do
     custo, e ele sozinho punha uma tarefa de 370 ms na thread principal --
     TBT de 488 ms, o pior numero de desempenho do site.

     Separar o BRUTO do FILTRO permite fatiar a parte cara no tempo sem tocar
     no resultado: `construirFatiado` alimenta `bruto` em varias tarefas e
     chama o mesmo `filtrar`. `amostrar()` continua sincrona e identica, porque
     `ferramentas/previa_marca.js` roda `construir()` deste arquivo. */
  function medirCaminho(el) {
    if (!el.getTotalLength || !el.getPointAtLength) return null;
    var total = 0;
    try { total = el.getTotalLength(); } catch (e) { return null; }
    if (!(total > 0)) return null;
    return { total: total, n: Math.max(64, Math.min(2400, Math.ceil(total / 1.2))) };
  }

  function amostrar(el, passo) {
    var m = medirCaminho(el);
    if (!m) return null;
    var bruto = [], i;
    for (i = 0; i < m.n; i++) {
      var p = el.getPointAtLength(m.total * i / m.n);
      bruto.push([p.x, p.y]);
    }
    return filtrar(bruto, passo);
  }

  function filtrar(bruto, passo) {
    var n = bruto.length, i;
    var pts = [], canto = [], acumulado = 1e9;
    for (i = 0; i < n; i++) {
      var a = bruto[(i - 1 + n) % n], b = bruto[i], c = bruto[(i + 1) % n];
      var v1x = b[0] - a[0], v1y = b[1] - a[1];
      var v2x = c[0] - b[0], v2y = c[1] - b[1];
      var l1 = Math.hypot(v1x, v1y), l2 = Math.hypot(v2x, v2y);
      acumulado += l1;
      if (l1 < 1e-6 || l2 < 1e-6) continue;
      /* ângulo de giro entre os dois segmentos, por atan2 do produto vetorial
         sobre o escalar — estável perto de 0 e de π, ao contrário de acos() */
      var cruzado = (v1x * v2y - v1y * v2x) / (l1 * l2);
      var escalar = (v1x * v2x + v1y * v2y) / (l1 * l2);
      var giro = Math.abs(Math.atan2(cruzado, escalar));

      if (giro > LIMIAR_CANTO) {
        pts.push(b); canto.push(true); acumulado = 0;
      } else if (giro > LIMIAR_RETO && acumulado >= passo) {
        pts.push(b); canto.push(false); acumulado = 0;
      }
    }
    /* Uma forma sem canto nenhum e sem curvatura suficiente sairia vazia. Não
       acontece com esta marca, mas um contorno vazio viraria buffer de tamanho
       zero e um `drawArraysInstanced` com 0 instâncias — falha silenciosa. */
    if (pts.length < 3) return null;
    return { pts: pts, canto: canto };
  }

  /* Retângulo lido dos ATRIBUTOS, sem amostrar. Dois dos seis elementos da
     marca são `<rect>`, e os quatro cantos deles são exatos por definição —
     não há por que passar por `getPointAtLength` e depois tentar recuperá-los.
     Também evita depender do suporte a SVGGeometryElement em `<rect>`, que é
     mais novo que o suporte em `<path>`. */
  function doRetangulo(el) {
    var x = parseFloat(el.getAttribute("x")) || 0;
    var y = parseFloat(el.getAttribute("y")) || 0;
    var w = parseFloat(el.getAttribute("width")) || 0;
    var h = parseFloat(el.getAttribute("height")) || 0;
    if (!(w > 0 && h > 0)) return null;
    return {
      pts: [[x, y], [x + w, y], [x + w, y + h], [x, y + h]],
      canto: [true, true, true, true]
    };
  }

  /* ============================== construção ==============================
     `L` é a lista de SEGMENTOS, 8 floats cada:
        ax ay az bx by bz peso tinta
     Mesmo empacotamento de braco.js (um segmento = uma instância de um quad
     de 6 vértices), com `elo` trocado por `tinta`: esta peça é rígida, então
     não há matriz por elo, mas tem duas famílias de cor. */
  function aresta(L, caixa, a, b, peso, tinta) {
    L.push(a[0], a[1], a[2], b[0], b[1], b[2], peso, tinta);
    for (var i = 0; i < 3; i++) {
      caixa[i] = Math.min(caixa[i], a[i], b[i]);
      caixa[i + 3] = Math.max(caixa[i + 3], a[i], b[i]);
    }
  }

  /* SVG -> modelo. Y INVERTE: em SVG cresce para BAIXO, no modelo para cima.
     É o mesmo espelho que `situar()` em braco.js precisa aplicar ao ponteiro,
     e o mesmo que custou uma sessão quando ficou faltando lá. */
  function ponto(cx, cy, sx, sy, sz) {
    return [(sx - cx) / ESCALA, (cy - sy) / ESCALA, sz / ESCALA];
  }

  /* Prisma reto: dois contornos paralelos e as nervuras que os costuram.
     As nervuras vão nos CANTOS — que é onde um desenho de extrusão as põe,
     porque é a aresta viva da peça — e não a cada N pontos. Num contorno todo
     curvo (o "3") isso deixaria zero nervuras, então há também um passo
     máximo. */
  function prisma(L, caixa, cx, cy, forma, z0, z1, peso, tinta) {
    var pts = forma.pts, canto = forma.canto, n = pts.length;
    var desdeNervura = 0;
    for (var i = 0; i < n; i++) {
      var a = pts[i], b = pts[(i + 1) % n];
      aresta(L, caixa, ponto(cx, cy, a[0], a[1], z0),
             ponto(cx, cy, b[0], b[1], z0), peso, tinta);
      aresta(L, caixa, ponto(cx, cy, a[0], a[1], z1),
             ponto(cx, cy, b[0], b[1], z1), peso, tinta);
      desdeNervura++;
      if (canto[i] || desdeNervura >= 6) {
        /* a nervura é mais leve que o contorno de propósito: ela descreve a
           profundidade, não a silhueta */
        aresta(L, caixa, ponto(cx, cy, a[0], a[1], z0),
               ponto(cx, cy, a[0], a[1], z1), peso * 0.5, tinta);
        desdeNervura = 0;
      }
    }
  }

  /* Papel de cada elemento, pela CLASSE que icone_marca() já escreve. A classe
     é o contrato: se o SVG ganhar uma peça nova, ela entra aqui sozinha desde
     que use um dos três nomes. Peça sem classe conhecida é ignorada — melhor
     faltar um detalhe do que extrudar algo com profundidade errada. */
  /* OS PESOS SÃO MEDIDOS, não estéticos. O alfa segue a mesma curva do braço,
     `(0,55 + 0,45 x peso) x ganho x profundidade`, e a profundidade tem piso
     0,55 — então o pior caso de toda aresta é ela no FUNDO da peça. Medido
     sobre o navy do cabeçalho (#001D3D), com a tinta #9FBEE0 e o ouro #FDC500:

       peso  aresta                     frente     fundo
       1,00  moldura e base .......... 7,60:1    3,19:1
       0,85  tela (ouro) ............. 7,99:1    3,18:1
       0,85  glifo "i3" .............. 7,99:1    3,18:1

     O glifo NASCEU em 0,70 e foi corrigido: naquele peso a aresta de fundo
     dava 2,72:1, abaixo do piso de 3:1 do WCAG 1.4.11 para elemento gráfico
     que carrega informação — e o "i3" carrega, é a marca. As NERVURAS ficam
     abaixo do piso de propósito (2,3 a 2,4:1): elas descrevem profundidade,
     que é sombreado, e o mesmo critério vale em braco.js. */
  var PAPEL = {
    moldura: { z0: Z_FUNDO, z1: Z_FRENTE, peso: 1.0, tinta: 0, passo: 26 },
    tela:    { z0: Z_FUNDO, z1: Z_TELA,   peso: 0.85, tinta: 1, passo: 26 },
    glifo:   { z0: Z_TELA,  z1: Z_GLIFO,  peso: 0.85, tinta: 0, passo: 7 }
  };

  function construir(svg) {
    var vb = svg.viewBox && svg.viewBox.baseVal;
    var largura = (vb && vb.width) || 410;
    var altura = (vb && vb.height) || 258;
    var cx = largura / 2, cy = altura / 2;

    var L = [], caixa = [1e9, 1e9, 1e9, -1e9, -1e9, -1e9];
    var fila = elegiveis(svg);
    for (var i = 0; i < fila.length; i++) {
      var el = fila[i].el, papel = fila[i].papel;
      var forma = (el.tagName.toLowerCase() === "rect")
        ? doRetangulo(el) : amostrar(el, papel.passo);
      if (!forma) continue;
      prisma(L, caixa, cx, cy, forma, papel.z0, papel.z1, papel.peso, papel.tinta);
    }
    return fechar(L, caixa);
  }

  /* Quais elementos entram, e com que papel. Fatorado porque os DOIS motores
     de construção precisam da mesma lista — duas cópias desta triagem
     divergiriam, e o sintoma seria a peça em WebGL diferindo da prévia. */
  function elegiveis(svg) {
    var fila = [], filhos = svg.querySelectorAll("path, rect");
    for (var i = 0; i < filhos.length; i++) {
      var el = filhos[i];
      /* a cópia de contorno da intro (`.marca__contorno`) repete moldura, tela
         e base — extrudá-la duplicaria metade da peça no mesmo lugar */
      if (el.closest && el.closest(".marca__contorno")) continue;
      var papel = null, cls = el.getAttribute("class") || "";
      for (var nome in PAPEL) {
        if (PAPEL.hasOwnProperty(nome) && cls.indexOf(nome) >= 0) {
          papel = PAPEL[nome]; break;
        }
      }
      if (papel) fila.push({ el: el, papel: papel });
    }
    return fila;
  }

  function fechar(L, caixa) {
    if (!L.length) return null;
    return { segmentos: new Float32Array(L), caixa: caixa };
  }

  /* Mesmo resultado que `construir`, entregue em VÁRIAS tarefas.

     O orçamento é de TEMPO (8 ms por fatia), não de contagem de amostras — e
     essa distinção é a mesma que a rolagem suave do main.js já paga: um
     orçamento em contagem calibrado num desktop vira uma tarefa de 200 ms no
     celular que justamente precisa da proteção. Medindo o relógio, a fatia
     encolhe sozinha no aparelho lento.

     8 ms e não 50: o limiar de "tarefa longa" é 50 ms, mas a fatia não é a
     tarefa inteira — ela divide o quadro com o resto do que o navegador
     estiver fazendo na carga. 8 ms deixa margem para isso e ainda assim
     termina a peça em poucos quadros.

     Nenhum vértice muda. É o MESMO `filtrar` sobre o MESMO `bruto`; só o
     momento em que cada amostra é colhida é outro. */
  var ORCAMENTO_MS = 8;

  function construirFatiado(svg, pronto) {
    var vb = svg.viewBox && svg.viewBox.baseVal;
    var largura = (vb && vb.width) || 410;
    var altura = (vb && vb.height) || 258;
    var cx = largura / 2, cy = altura / 2;

    var L = [], caixa = [1e9, 1e9, 1e9, -1e9, -1e9, -1e9];
    var fila = elegiveis(svg);
    var k = 0, medida = null, bruto = null, j = 0;

    function fatia() {
      var fim = (window.performance ? performance.now() : Date.now()) + ORCAMENTO_MS;
      while (k < fila.length) {
        var el = fila[k].el, papel = fila[k].papel, forma = null;

        if (el.tagName.toLowerCase() === "rect") {
          forma = doRetangulo(el);
        } else {
          if (!medida) { medida = medirCaminho(el); bruto = []; j = 0; }
          if (medida) {
            while (j < medida.n) {
              var p = el.getPointAtLength(medida.total * j / medida.n);
              bruto.push([p.x, p.y]);
              j++;
              /* o relógio é lido a cada 32 amostras: lê-lo a cada uma custaria
                 mais que a própria amostragem nas formas retas */
              if ((j & 31) === 0 &&
                  (window.performance ? performance.now() : Date.now()) > fim) {
                return window.requestAnimationFrame(fatia);
              }
            }
            forma = filtrar(bruto, papel.passo);
          }
          medida = null; bruto = null; j = 0;
        }

        if (forma) {
          prisma(L, caixa, cx, cy, forma, papel.z0, papel.z1, papel.peso, papel.tinta);
        }
        k++;
        if ((window.performance ? performance.now() : Date.now()) > fim) {
          return window.requestAnimationFrame(fatia);
        }
      }
      pronto(fechar(L, caixa));
    }

    fatia();
  }

  /* ============================== câmera ==============================
     A marca é RÍGIDA — não há pose nem ciclo —, então o enquadramento é uma
     conta só por ângulo, e não o máximo sobre seis fases como no braço.

     `MIRA` é 0 porque `ponto()` já centra o perfil na origem: o eixo de giro
     passa pelo meio da peça, que é o único lugar de onde ela não parece
     pendurada.

     `AR` É MENOR QUE 1, E O SINAL IMPORTA. A conta de enquadramento usa
     `tan(FOV/2) * AR` como meio-campo, mas a PROJEÇÃO usa `tan(FOV/2)` puro —
     então AR > 1 diz à câmera que ela tem mais campo do que tem, e a peça
     TRANSBORDA. Este arquivo nasceu com 1,06 justamente por essa inversão, e a
     varredura pegou: a base saía 11 px fora da moldura.

     Medido com ferramentas/previa_marca.js, varrendo 13 ângulos x 3
     inclinações numa moldura de 340x364:

       AR     folga mínima
       1,00     0,0 px      <- encosta, e em alguns ângulos corta
       0,96     6,8 px      <- fica
       0,92    13,6 px
       0,88    20,4 px

     Ficou 0,96 e não 0,98 como o braço porque aqui não há folga de graça: a
     caixa envolvente de um prisma reto É a peça, enquanto no braço o canto da
     caixa cai fora da silhueta arredondada e já devolve margem sozinho. */
  var FOV = 0.52, MIRA = 0, AR = 0.96;

  /* O ARCO DE GIRO É LIMITADO, e esta é a diferença de comportamento que
     separa a marca do braço.

     O braço é uma máquina: girar 360° mostra mais máquina, e ele orbita solto.
     A marca é uma MARCA — de perfil ela vira uma tira vertical e deixa de
     comunicar qualquer coisa. Medido na mesma varredura, a ocupação mínima de
     largura ao longo do arco:

       ±0,75 rad ..... 72%
       ±0,95 rad ..... 60%
       ±1,20 rad ..... 42%      <- a peça some

     Em ±0,80 a marca nunca cai abaixo de ~75% da largura da moldura: ela gira
     o bastante para a extrusão se anunciar e nunca o bastante para o logo
     deixar de ser legível. O arrasto para no limite; o repouso VOLTA nele. */
  var ARCO = 0.80;
  var ARCO_ARRASTO = 0.95;   /* o dedo pode ir um pouco além do repouso */

  /* ============================== shaders ============================== */
  var VS = [
    "#version 300 es",
    "in vec2 canto;",
    "in vec3 pa;",
    "in vec3 pb;",
    "in float peso;",
    "in float tinta;",
    "uniform mat4 uMVP;",
    "uniform vec2  uEscala;",
    "uniform float uFina;",
    "uniform float uGrossa;",
    "uniform float uDist;",
    "uniform float uRaioPeca;",
    "out float vPeso;",
    "out float vTinta;",
    "out float vProf;",
    "out vec2  vTela;",
    "out float vBorda;",
    "out float vMeia;",
    "void main() {",
    "  vec4 ca = uMVP * vec4(pa, 1.0);",
    "  vec4 cb = uMVP * vec4(pb, 1.0);",
    "  vec4 c = canto.y < 0.5 ? ca : cb;",
    /* ESPESSURA DE VERDADE, por expansão em quad — mesma razão de braco.js:
       `gl.LINES` desenha 1 pixel de DISPOSITIVO e `lineWidth > 1` é ignorado
       no Chrome, o que em DPR 2 é meio pixel de CSS e lê como fantasma. */
    "  vec2 sa = ca.xy / ca.w * uEscala;",
    "  vec2 sb = cb.xy / cb.w * uEscala;",
    "  vec2 d = sb - sa;",
    "  float comp = length(d);",
    "  vec2 nrm = comp > 1e-4 ? vec2(-d.y, d.x) / comp : vec2(0.0, 0.0);",
    "  float meia = mix(uFina, uGrossa, clamp(peso, 0.0, 1.0)) * 0.5;",
    "  vMeia = meia;",
    "  vBorda = canto.x * (meia + 0.8);",
    "  vec2 s = (canto.y < 0.5 ? sa : sb) + nrm * vBorda;",
    "  vec2 ndc = s / uEscala;",
    "  gl_Position = vec4(ndc * c.w, c.z, c.w);",
    /* Rampa de profundidade RELATIVA à câmera, como em braco.js: as
       constantes absolutas quebram assim que o enquadramento vira automático,
       porque a mesma aresta passa a cair em pontos diferentes da rampa. */
    "  vProf = clamp(1.0 - (c.w - (uDist - uRaioPeca)) / (2.0 * uRaioPeca), 0.55, 1.0);",
    "  vPeso = peso;",
    "  vTinta = tinta;",
    "  vTela = ndc * 0.5 + 0.5;",
    "}"
  ].join("\n");

  var FS = [
    "#version 300 es",
    /* highp e não mediump: o fBm da borda BANDA visivelmente em mediump e o
       degradê da lente vira degrau. Mesma correção já feita em planta.js. */
    "precision highp float;",
    "in float vPeso;",
    "in float vTinta;",
    "in float vProf;",
    "in vec2  vTela;",
    "in float vBorda;",
    "in float vMeia;",
    "uniform vec3  uTinta;",
    "uniform vec3  uOuro;",
    "uniform vec3  uAceso;",
    "uniform float uGanho;",
    "uniform vec2  uPonteiro;",
    "uniform float uRaio;",
    "uniform float uAtivo;",
    "uniform float uProp;",
    "uniform float uTempo;",
    "uniform float uEntrada;",
    "out vec4 cor;",
    G.RUIDO_GLSL,
    "void main() {",
    /* DUAS TINTAS, e aqui elas não são "acima e abaixo do corte" como no
       braço: são o PAPEL da peça. A tela do monitor é dourada na marca real e
       continua dourada no desenho; moldura, base e glifo ficam no azul-aço.
       É o que faz o objeto ser reconhecível como o logo e não como uma caixa
       de arame qualquer. */
    "  vec3 base = mix(uTinta, uOuro, vTinta);",
    "  float d = length((vTela - uPonteiro) * vec2(uProp, 1.0)) / max(uRaio, 1e-4);",
    "  float n = (fbm(vTela * 9.0 + uTempo * 0.05) - 0.5) * 0.17;",
    "  float rev = (1.0 - smoothstep(0.80, 1.04, d + n)) * uAtivo;",
    /* Mesma curva de alfa do braço: `peso` puro punha a aresta de detalhe em
       1,82:1 — ela existia no buffer e não na tela. 0,55 + 0,45 x peso mantém
       a hierarquia e levanta o piso acima dos 3:1 do WCAG 1.4.11. */
    "  float a = (0.55 + 0.45 * vPeso) * uGanho * vProf * uEntrada",
    "          * (1.0 + rev * 0.42);",
    "  vec3 c = mix(base, uAceso, rev);",
    /* Banda no limite da lente, pelo QUADRADO e não por pow(): em GLSL
       `pow(x, y)` é INDEFINIDO para x < 0, e aqui o argumento é negativo em
       toda a parte de dentro da lente — justamente onde a banda tem de valer
       zero. Vários drivers devolvem NaN, e NaN sobrevive à multiplicação por
       uAtivo (NaN x 0 = NaN). */
    "  float t = (d + n - 0.94) * 20.0;",
    "  float banda = exp(-t * t) * uAtivo * uEntrada;",
    "  c = mix(c, uAceso, clamp(banda * 0.85, 0.0, 1.0));",
    "  a = max(a, banda * vPeso * 0.75);",
    /* Antisserrilhado próprio na borda do quad — é o que permitiu desligar o
       MSAA, que em linha fina come justamente a intensidade que faz falta. */
    "  a *= 1.0 - smoothstep(vMeia - 0.5, vMeia + 0.5, abs(vBorda));",
    "  cor = vec4(c, clamp(a, 0.0, 1.0));",
    "}"
  ].join("\n");

  /* =============================== montagem =============================== */
  function montar(raiz) {
    var canvas = raiz.querySelector(".marca3d__tela");
    var svg = raiz.querySelector("svg");
    if (!canvas || !svg || !window.WebGL2RenderingContext) return;

    /* A GEOMETRIA É LIDA ANTES DE QUALQUER COISA, e a ordem importa:
       `getPointAtLength` precisa do elemento no documento. Se `is-gl` fosse
       aplicado primeiro, o CSS esconderia o SVG e a leitura devolveria zero —
       um desenho vazio, sem erro nenhum no console. */
    /* A construção corre FATIADA, e o resto da montagem espera por ela. Sem
       WebGL2 ou sem `requestAnimationFrame` nada disso acontece e o visitante
       fica com o SVG plano, que já está na tela — a reserva é o estado de
       partida, não um caminho de erro. */
    if (!window.requestAnimationFrame) return;
    construirFatiado(svg, function (cena) {
      if (cena) comGeometria(raiz, canvas, cena);
    });
  }

  function comGeometria(raiz, canvas, cena) {
    var gl = canvas.getContext("webgl2", {
      alpha: true, premultipliedAlpha: false, antialias: false,
      depth: false, powerPreference: "low-power"
    });
    if (!gl) return;

    var prog = programa(gl, VS, FS, "marca");
    if (!prog) return;

    var dados = cena.segmentos;
    var nSegmentos = dados.length / 8;

    var vao = gl.createVertexArray();
    gl.bindVertexArray(vao);

    var bufQuad = gl.createBuffer();
    gl.bindBuffer(gl.ARRAY_BUFFER, bufQuad);
    gl.bufferData(gl.ARRAY_BUFFER, new Float32Array([
      -1, 0,   1, 0,  -1, 1,
      -1, 1,   1, 0,   1, 1
    ]), gl.STATIC_DRAW);
    var aCanto = gl.getAttribLocation(prog, "canto");
    gl.enableVertexAttribArray(aCanto);
    gl.vertexAttribPointer(aCanto, 2, gl.FLOAT, false, 8, 0);

    var bufSeg = gl.createBuffer();
    gl.bindBuffer(gl.ARRAY_BUFFER, bufSeg);
    gl.bufferData(gl.ARRAY_BUFFER, dados, gl.STATIC_DRAW);
    [["pa", 3, 0], ["pb", 3, 12], ["peso", 1, 24], ["tinta", 1, 28]]
      .forEach(function (a) {
        var loc = gl.getAttribLocation(prog, a[0]);
        gl.enableVertexAttribArray(loc);
        gl.vertexAttribPointer(loc, a[1], gl.FLOAT, false, 32, a[2]);
        gl.vertexAttribDivisor(loc, 1);
      });

    /* Os 8 cantos da caixa, e o raio da peça em torno da mira. O braço mede o
       raio na pose de repouso; aqui a peça é rígida, então é uma medida só e
       para sempre. */
    var CANTOS = [G.cantosDaCaixa(cena.caixa)];
    var IDENT = [G.identidade()];
    var RAIO = (function () {
      var maior = 0.5, p = CANTOS[0];
      for (var i = 0; i < 8; i++) {
        maior = Math.max(maior, Math.hypot(p[i][0], p[i][1] - MIRA, p[i][2]));
      }
      return maior;
    })();

    gl.enable(gl.BLEND);
    gl.blendFuncSeparate(gl.SRC_ALPHA, gl.ONE_MINUS_SRC_ALPHA, gl.ONE,
                         gl.ONE_MINUS_SRC_ALPHA);
    gl.clearColor(0, 0, 0, 0);

    var u = {};
    ["uMVP", "uEscala", "uFina", "uGrossa", "uDist", "uRaioPeca", "uTinta",
     "uOuro", "uAceso", "uGanho", "uPonteiro", "uRaio", "uAtivo", "uProp",
     "uTempo", "uEntrada"].forEach(function (n) {
      u[n] = gl.getUniformLocation(prog, n);
    });

    /* ---------------------------- estado ---------------------------- */
    /* O ângulo de repouso mostra as TRÊS profundidades de uma vez: de frente a
       peça seria indistinguível do SVG plano que ela substitui, e é o
       escalonamento moldura/tela/glifo que justifica ela ser 3D. */
    var giro = -0.62, giroVel = 0, inclinacao = 0.18, sentido = 1;
    var arrastando = false, ultimoX = 0, ultimoY = 0;
    var pontX = -9, pontY = -9, ativo = 0, alvoAtivo = 0;
    var entrada = 0, dpr = 1, larg = 1, alt = 1;
    var corTinta = [0.62, 0.75, 0.88], corOuro = [0.99, 0.77, 0];
    var corAceso = [0.99, 0.77, 0], ganho = 0.92;
    var fina = 0.9, grossa = 1.8;
    var visivel = false, rodando = false, anterior = 0, relogio = 0;

    function lerTema() {
      var cs = getComputedStyle(raiz);
      corTinta = rgb(cs.getPropertyValue("--marca-traco"), [0.62, 0.75, 0.88]);
      corOuro = rgb(cs.getPropertyValue("--marca-ouro"), [0.99, 0.77, 0]);
      corAceso = rgb(cs.getPropertyValue("--marca-aceso"), corOuro);
      ganho = parseFloat(cs.getPropertyValue("--marca-ganho")) || 0.92;
      /* TOKENS PRÓPRIOS, não os do braço. A versão anterior lia
         `--braco-linha-fina/-grossa`, declarados em `.heroi` — que não é
         ancestral de `.marca3d`. A leitura vinha vazia e a peça caía nestes
         padrões sem aviso; o token existia no arquivo e não valia nada aqui.
         Largura em PIXELS DE CSS: o dpr entra só na hora de subir ao shader,
         então a espessura é a mesma numa tela comum e numa de alta densidade. */
      fina = parseFloat(cs.getPropertyValue("--marca-linha-fina")) || 1.4;
      grossa = parseFloat(cs.getPropertyValue("--marca-linha-grossa")) || 2.8;
    }

    /* TETO de 4096 px por lado, e o `return` quando a caixa ainda não tem
       tamanho. Não é otimização: `medir()` LÊ o retângulo e ESCREVE os
       atributos do canvas, que são o tamanho intrínseco dele. Se a altura em
       CSS deixar de resolver, o intrínseco vaza para o layout, o retângulo
       cresce e o quadro seguinte escreve um valor maior — a caixa DOBRA por
       quadro até a página ficar impossível de rolar. Já aconteceu neste site,
       com `height: 144%` sobre linha de grade automática. O CSS aqui põe o
       canvas em `position: absolute` justamente para o ciclo não ter por onde
       fechar; esta trava existe para a próxima regressão ser um desenho feio e
       não um site travado. */
    var TETO = 4096;

    function medir() {
      var c = raiz.getBoundingClientRect();
      if (c.width < 2 || c.height < 2) return;
      dpr = Math.min(window.devicePixelRatio || 1, 2);
      larg = Math.min(c.width, TETO / dpr);
      alt = Math.min(c.height, TETO / dpr);
      var w = Math.round(larg * dpr), h = Math.round(alt * dpr);
      if (canvas.width !== w || canvas.height !== h) {
        canvas.width = w; canvas.height = h;
        gl.viewport(0, 0, w, h);
      }
    }

    var dSuave = 0, dAlvo = 0, enqGiro = 1e9, enqIncl = 1e9, enqProp = 0;

    function distanciaDoAngulo() {
      var prop = larg / alt;
      if (Math.abs(giro - enqGiro) < 0.05 && Math.abs(inclinacao - enqIncl) < 0.05 &&
          prop === enqProp) return dAlvo;
      enqGiro = giro; enqIncl = inclinacao; enqProp = prop;
      dAlvo = G.enquadrarCaixas(CANTOS, IDENT, giro, inclinacao, prop, MIRA, FOV, AR);
      return dAlvo;
    }

    function mvp() {
      var alvo = distanciaDoAngulo();
      dSuave = dSuave ? dSuave + (alvo - dSuave) * 0.08 : alvo;
      var d = dSuave;
      var o = [
        Math.sin(giro) * Math.cos(inclinacao) * d,
        MIRA + Math.sin(inclinacao) * d,
        Math.cos(giro) * Math.cos(inclinacao) * d
      ];
      return mult(perspectiva(FOV, larg / alt, 1, 120),
                  olhar(o, [0, MIRA, 0], [0, 1, 0]));
    }

    function quadro(agora) {
      var dt = Math.min((agora - anterior) / 1000, 0.05);
      anterior = agora;
      relogio += dt;

      if (!arrastando) {
        giro += giroVel * dt;
        giroVel *= Math.pow(0.02, dt);
        /* Deriva de repouso: sem ela a peça parece congelada e o convite ao
           arrasto some. Mais lenta que a do braço (0,035) porque aqui não há
           ciclo de trabalho competindo — é o único movimento da peça.

           E ela VAI E VOLTA, em vez de girar sempre para o mesmo lado. Uma
           deriva de sentido único empurraria a marca contra o limite do arco e
           ela ficaria encostada lá para sempre — parada, que é exatamente o
           que a deriva existe para evitar. Invertendo nos extremos, a peça
           balança dentro da faixa legível indefinidamente. Um trecho leva
           perto de 70 s, então lê como respiração e não como animação. */
        if (Math.abs(giroVel) < 0.02 && !reduzido) {
          if (giro >= ARCO) sentido = -1;
          else if (giro <= -ARCO) sentido = 1;
          giro += sentido * 0.022 * dt;
        }
        /* o embalo do arrasto também para no limite, e morre ali */
        if (giro > ARCO_ARRASTO) { giro = ARCO_ARRASTO; giroVel = 0; }
        if (giro < -ARCO_ARRASTO) { giro = -ARCO_ARRASTO; giroVel = 0; }
      }
      entrada += ((visivel ? 1 : 0) - entrada) * (1 - Math.pow(0.02, dt));
      ativo += (alvoAtivo - ativo) *
               (1 - Math.pow(alvoAtivo > ativo ? 0.002 : 0.06, dt));

      medir();

      gl.clear(gl.COLOR_BUFFER_BIT);
      gl.useProgram(prog);
      gl.bindVertexArray(vao);
      gl.uniformMatrix4fv(u.uMVP, false, mvp());
      gl.uniform3fv(u.uTinta, corTinta);
      gl.uniform3fv(u.uOuro, corOuro);
      gl.uniform3fv(u.uAceso, corAceso);
      gl.uniform1f(u.uGanho, ganho);
      gl.uniform2f(u.uEscala, canvas.width / 2, canvas.height / 2);
      gl.uniform1f(u.uFina, fina * dpr);
      gl.uniform1f(u.uGrossa, grossa * dpr);
      gl.uniform1f(u.uDist, dSuave || 12);
      gl.uniform1f(u.uRaioPeca, RAIO);
      gl.uniform2f(u.uPonteiro, pontX, pontY);
      gl.uniform1f(u.uRaio, 0.30);
      gl.uniform1f(u.uAtivo, ativo);
      gl.uniform1f(u.uProp, larg / alt);
      gl.uniform1f(u.uTempo, relogio);
      gl.uniform1f(u.uEntrada, entrada);
      gl.drawArraysInstanced(gl.TRIANGLES, 0, 6, nSegmentos);

      if (visivel || entrada > 0.01) window.requestAnimationFrame(quadro);
      else rodando = false;
    }

    function acordar() {
      if (rodando) return;
      rodando = true; anterior = performance.now();
      window.requestAnimationFrame(quadro);
    }

    /* ---------------------------- interação ----------------------------
       A LENTE OUVE O CABEÇALHO INTEIRO, o arrasto só a peça — mesma divisão do
       herói, e pela mesma razão: ligada apenas na peça, a lente acenderia sobre
       a marca e apagaria sobre o texto, e o dourado SALTARIA de um para o
       outro em vez de varrer. `situar()` mede em relação ao canvas, então o
       ponteiro sobre o texto vira uma posição fora de 0..1 e a lente cai fora
       sozinha, sem nenhum caso especial. */
    function situar(e) {
      var c = raiz.getBoundingClientRect();
      pontX = (e.clientX - c.left) / Math.max(1, c.width);
      /* O Y INVERTE. `vTela` sai de NDC, onde +1 é o TOPO, e `clientY` cresce
         para baixo. Sem isto a lente aparece espelhada na vertical: ponteiro no
         alto, dourado embaixo. Foi o bug que custou uma sessão no herói. */
      pontY = 1 - (e.clientY - c.top) / Math.max(1, c.height);
    }

    var campo = (raiz.closest && raiz.closest(".cabecalho")) || raiz;
    campo.addEventListener("pointerenter", function () { alvoAtivo = 1; acordar(); });
    campo.addEventListener("pointerleave", function () {
      if (arrastando) return;
      alvoAtivo = 0; acordar();
    });
    campo.addEventListener("pointermove", function (e) {
      if (arrastando) return;
      situar(e); alvoAtivo = 1; acordar();
    });
    raiz.addEventListener("pointerdown", function (e) {
      arrastando = true;
      ultimoX = e.clientX; ultimoY = e.clientY;
      situar(e); alvoAtivo = 1;
      if (raiz.setPointerCapture) raiz.setPointerCapture(e.pointerId);
      acordar();
    });
    raiz.addEventListener("pointermove", function (e) {
      situar(e); alvoAtivo = 1;
      if (arrastando) {
        var dx = e.clientX - ultimoX, dy = e.clientY - ultimoY;
        ultimoX = e.clientX; ultimoY = e.clientY;
        /* o arrasto TAMBÉM para no arco: soltar a marca de perfil deixaria
           uma tira vertical na tela até alguém voltar a arrastar */
        giro = Math.max(-ARCO_ARRASTO,
                        Math.min(ARCO_ARRASTO, giro - dx * 0.007));
        giroVel = -dx * 0.14;
        /* trava a inclinação: passando de ±0,9 o visitante olha a marca de
           topo ou de baixo, e nas duas ela deixa de ser legível como marca */
        inclinacao = Math.max(-0.9, Math.min(0.9, inclinacao + dy * 0.004));
      }
      acordar();
    });
    function soltar(e) {
      if (!arrastando) return;
      arrastando = false;
      if (e && e.pointerId != null && raiz.hasPointerCapture &&
          raiz.hasPointerCapture(e.pointerId)) raiz.releasePointerCapture(e.pointerId);
      /* No toque não há hover: a lente fica acesa enquanto o dedo está na peça
         e apaga ao soltar, senão ficaria presa acesa para sempre. */
      if (window.matchMedia("(hover: none)").matches) alvoAtivo = 0;
      acordar();
    }
    raiz.addEventListener("pointerup", soltar);
    raiz.addEventListener("pointercancel", soltar);

    /* Teclado: a peça é conteúdo, e conteúdo se navega sem ponteiro. */
    raiz.addEventListener("keydown", function (e) {
      var passo = 0.18;
      if (e.key === "ArrowLeft") giro = Math.max(-ARCO_ARRASTO, giro - passo);
      else if (e.key === "ArrowRight") giro = Math.min(ARCO_ARRASTO, giro + passo);
      else if (e.key === "ArrowUp") inclinacao = Math.min(0.9, inclinacao + 0.08);
      else if (e.key === "ArrowDown") inclinacao = Math.max(-0.9, inclinacao - 0.08);
      else return;
      e.preventDefault();
      pontX = 0.5; pontY = 0.5; alvoAtivo = 1;
      acordar();
    });
    raiz.addEventListener("focus", function () {
      pontX = 0.5; pontY = 0.5; alvoAtivo = 1; acordar();
    });
    raiz.addEventListener("blur", function () { alvoAtivo = 0; acordar(); });

    lerTema();
    medir();
    var mm = window.matchMedia("(prefers-color-scheme: dark)");
    if (mm.addEventListener) {
      mm.addEventListener("change", function () { lerTema(); acordar(); });
    }
    document.addEventListener("temachange", function () { lerTema(); acordar(); });
    window.addEventListener("resize", function () { medir(); acordar(); });

    /* Só agora o SVG plano sai de cena e a peça entra na ordem de tabulação:
       focar um SVG estático não leva a lugar nenhum, e ponto de parada morto é
       pior que nenhum. */
    raiz.setAttribute("tabindex", "0");
    raiz.classList.add("is-gl");

    if (window.IntersectionObserver) {
      new IntersectionObserver(function (ent) {
        visivel = ent[0].isIntersecting;
        if (visivel) acordar();
      }, { rootMargin: "120px" }).observe(raiz);
    } else {
      visivel = true;
    }
    acordar();
  }

  function iniciar() {
    var els = document.querySelectorAll("[data-marca3d]");
    for (var i = 0; i < els.length; i++) montar(els[i]);
  }

  if (document.readyState === "loading") {
    document.addEventListener("DOMContentLoaded", iniciar);
  } else {
    iniciar();
  }
})();
