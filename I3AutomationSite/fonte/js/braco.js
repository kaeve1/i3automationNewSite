/* ============================================================================
   Braço — o robô de 6 eixos do herói, em WebGL2 escrito à mão
   i3Automations

   Irmão da planta (js/planta.js) e do mesmo assunto: ARESTA, não face. O que
   muda é a escala do olhar — a planta é a topologia de uma instalação inteira,
   este é UMA peça vista de perto, com juntas que se movem.

   Três coisas aqui não existem na planta, e são o motivo de o arquivo existir:

   1. CINEMÁTICA DIRETA NA GPU. A geometria é gerada UMA vez, em espaço local
      de cada elo, e cada vértice carrega o índice do elo a que pertence. Por
      quadro sobem 9 matrizes (`uElo[]`) e o vertex shader faz
      `uMVP * uElo[elo] * pos`. Nenhum vértice é reescrito para animar: o braço
      trabalha sem tocar no buffer. É a diferença entre animar um robô e
      redesenhá-lo.

   2. PERFIL POR ENVOLTÓRIA DE CÍRCULOS. Todo elo deste braço é uma chapa de
      cantos arredondados — e a envoltória convexa de N círculos descreve
      exatamente isso. Para cada direção u, o ponto do contorno é
      `c_i + r_i·u` do círculo que maximiza `c_i·u + r_i`. Sete linhas de
      código dão braço, antebraço, punho e dedos, sem um único vértice à mão.

   3. REVELAÇÃO POR PONTEIRO EM ESPAÇO DE TELA. O desenho vive em azul-aço
      sobre o bloco escuro; sob o ponteiro as arestas acendem em `--azul-luz`, com
      a borda dissolvida pelo mesmo fBm da lente (js/lente.js) — para que os
      dois componentes leiam como o mesmo instrumento.

   Sem Three.js, sem .glb, sem loader (design.md §9). Medido no par de cores:
   #9FBEE0 sobre #001D3D dá 8,78:1 opaco. O alfa segue `0,55 + 0,45 x peso`
   vezes o ganho do lado (0,92 em cima, 1,15 embaixo do corte): a hierarquia de
   peso continua, mas nenhuma aresta cai abaixo de 3:1 — o peso .30 ia a
   1,82:1 quando o alfa era o peso puro, e sumia.

   4. ESPESSURA DE VERDADE, por expansão em quad. `gl.LINES` desenha 1 pixel de
      DISPOSITIVO e `lineWidth > 1` é ignorado no Chrome: em DPR 2 isso é meio
      pixel de CSS, e o desenho lia como fantasma por mais alfa que levasse.
      Cada segmento virou um retângulo de 6 vértices, expandido na direção
      normal à linha em PIXELS DE TELA, desenhado com `drawArraysInstanced` —
      seis vértices e 1421 instâncias. O `peso` da aresta finalmente escolhe
      LARGURA (tokens `--braco-linha-fina/-grossa`) em vez de fingir largura
      com transparência, e a borda tem rampa própria de antisserrilhado, o que
      permitiu desligar o MSAA — que em linha fina come justamente a
      intensidade que faz falta.
   ============================================================================ */
(function () {
  "use strict";

  var TAU = Math.PI * 2;
  var reduzido = window.matchMedia("(prefers-reduced-motion: reduce)").matches;

  /* ================================ núcleo ================================
     Matriz, parser de token e compilação de shader vivem em js/gl.js — a base
     é a mesma de planta.js e marca.js, e três cópias dela é como uma fica para
     trás (ver o cabeçalho de gl.js).

     O ALIAS LOCAL é deliberado: com ele os call sites deste arquivo continuam
     lendo `mult(a, b)`, `olhar(...)`, `rgb(...)` — exatamente como antes da
     extração. Nenhuma linha de geometria, cinemática ou desenho mudou por
     causa dela, e ferramentas/previa_braco.js continua exportando estes mesmos
     nomes do escopo do módulo. */
  var G = (typeof globalThis !== "undefined" ? globalThis : window).I3GL;
  var mult = G.mult, transladar = G.transladar, giroY = G.giroY, giroZ = G.giroZ;
  var perspectiva = G.perspectiva, normal = G.normal, cruz = G.cruz, olhar = G.olhar;
  var rgb = G.rgb, programa = G.programa;

  /* ============================== geometria ==============================
     `L` é a lista de SEGMENTOS. Cada segmento ocupa 8 floats:
        ax, ay, az, bx, by, bz, peso, elo
     e vira uma instância do retângulo de 6 vértices. Os dois extremos viajam
     juntos porque o vertex shader precisa da direção da linha para expandir.
     `peso` é prioridade de aresta (1 = contorno estrutural, .3 = detalhe) e
     controla largura e alfa; `elo` é o índice da matriz de cinemática.
     ============================================================================ */
  /* UM segmento por instância: ax ay az bx by bz peso elo.
     Era um par de vértices soltos para `gl.LINES`; agora cada segmento vira
     um quad de 6 vértices no vertex shader, e os dois extremos precisam
     chegar juntos ao mesmo vértice para dar a direção da linha. */
  function aresta(L, elo, a, b, p) {
    L.push(a[0], a[1], a[2], b[0], b[1], b[2], p, elo);
    /* Caixa local por elo, acumulada enquanto a geometria nasce. Serve ao
       enquadramento automático: são estes 8 cantos por elo que a câmera
       consulta por quadro para saber de quanto precisa se afastar. */
    var c = CAIXAS[elo] || (CAIXAS[elo] = [1e9, 1e9, 1e9, -1e9, -1e9, -1e9]);
    for (var i = 0; i < 3; i++) {
      c[i] = Math.min(c[i], a[i], b[i]);
      c[i + 3] = Math.max(c[i + 3], a[i], b[i]);
    }
  }

  var CAIXAS = [];

  /* Envoltória convexa de círculos coplanares. `circulos` = [[x, y, r], …].
     Para cada direção u escolhe o círculo de maior suporte e devolve o ponto
     de apoio: nos trechos em que o vencedor não muda sai um arco, e no quadro
     em que ele muda sai exatamente a reta tangente entre os dois. É por isso
     que o contorno de uma "cápsula" aparece sem nenhuma conta de tangente. */
  function contorno(circulos, n) {
    var pts = [], k, i;
    for (k = 0; k < n; k++) {
      var t = (k / n) * TAU, ux = Math.cos(t), uy = Math.sin(t);
      var venc = 0, melhor = -1e9;
      for (i = 0; i < circulos.length; i++) {
        var v = circulos[i][0] * ux + circulos[i][1] * uy + circulos[i][2];
        if (v > melhor) { melhor = v; venc = i; }
      }
      var c = circulos[venc];
      pts.push([c[0] + c[2] * ux, c[1] + c[2] * uy]);
    }
    return pts;
  }

  /* Mapeamentos de plano: o perfil é sempre desenhado em (u, v) e extrudado
     em w. XY extruda na profundidade (a vista lateral do braço); XZ extruda na
     altura (a base e o flange, que são plantas). */
  var XY = function (u, v, w) { return [u, v, w]; };
  var XZ = function (u, v, w) { return [u, w, v]; };

  /* Chapa: dois contornos paralelos e as nervuras que os costuram. É O
     primitivo desta peça — todo elo do robô é uma chapa de canto redondo. */
  function chapa(L, elo, circulos, w0, w1, p, opc) {
    opc = opc || {};
    var n = opc.n || 44;
    var salto = opc.nervura || 6;
    var plano = opc.plano || XY;
    var pts = contorno(circulos, n);
    for (var i = 0; i < n; i++) {
      var a = pts[i], b = pts[(i + 1) % n];
      aresta(L, elo, plano(a[0], a[1], w0), plano(b[0], b[1], w0), p);
      aresta(L, elo, plano(a[0], a[1], w1), plano(b[0], b[1], w1), p);
      if (i % salto === 0) {
        aresta(L, elo, plano(a[0], a[1], w0), plano(a[0], a[1], w1), p * 0.42);
      }
    }
    return pts;
  }

  /* Contorno solto, sem extrusão: recorte interno, vinco, junta aparafusada. */
  function traco(L, elo, circulos, w, p, opc) {
    opc = opc || {};
    var n = opc.n || 34;
    var plano = opc.plano || XY;
    var pts = contorno(circulos, n);
    for (var i = 0; i < n; i++) {
      var a = pts[i], b = pts[(i + 1) % n];
      aresta(L, elo, plano(a[0], a[1], w), plano(b[0], b[1], w), p);
    }
  }

  /* Cilindro de eixo Y: coluna da base, colar de junta, flange de ferramenta. */
  function coluna(L, elo, x, y, z, r0, r1, h, seg, p) {
    var ant = null;
    for (var i = 0; i <= seg; i++) {
      var a = (i / seg) * TAU;
      var c = Math.cos(a), s = Math.sin(a);
      var b0 = [x + c * r0, y, z + s * r0];
      var b1 = [x + c * r1, y + h, z + s * r1];
      if (ant) {
        aresta(L, elo, ant[0], b0, p);
        aresta(L, elo, ant[1], b1, p);
      }
      if (i % Math.max(1, Math.round(seg / 8)) === 0) aresta(L, elo, b0, b1, p * 0.5);
      ant = [b0, b1];
    }
  }

  /* ============================ o braço ============================
     Cadeia, medida em unidades do modelo (a peça inteira tem ~9 de altura):

       elo 0  base fixa .............. flange + coluna
       elo 1  J1 cintura ............. giro em Y     · y 1,72
       elo 2  J2 ombro ............... giro em Z     · y 1,05
       elo 3  J3 cotovelo ............ giro em Z     · y 3,45
       elo 4  J4 rolagem do antebraço  giro em Y     · y 2,95
       elo 5  J5 punho ............... giro em Z     · y 0,62
       elo 6  J6 rolagem da ferramenta giro em Y     · y 0,78
       elos 7 e 8  os dois dedos ..... giro em Z     · a partir do elo 6

     Os deslocamentos vivem em PIVO[], e são a única fonte da montagem: o
     shader não sabe nada disso, e a geometria de cada elo é escrita como se o
     elo estivesse na origem. */
  var PIVO = [
    null,
    [0, 1.72, 0],
    [0, 1.05, 0],
    [0, 3.45, 0],
    [0, 2.95, 0],
    [0, 0.62, 0],
    [0, 0.78, 0]
  ];
  var PIVO_DEDO = 0.92;   /* altura do nó do dedo no quadro da ferramenta */

  function construir() {
    var L = [];
    CAIXAS = [];   /* zera: construir() pode rodar uma vez por elemento */

    /* ---- elo 0: flange de chumbamento + coluna ---- */
    var f = 1.42;
    chapa(L, 0, [[-f, -f, 0.30], [f, -f, 0.30], [f, f, 0.30], [-f, f, 0.30]],
          0, 0.26, 0.95, { plano: XZ, n: 40, nervura: 5 });
    /* os quatro furos: é o detalhe que diz "isto se aparafusa no chão" */
    [[-f, -f], [f, -f], [f, f], [-f, f]].forEach(function (c) {
      traco(L, 0, [[c[0], c[1], 0.155]], 0.27, 0.5, { plano: XZ, n: 14 });
    });
    coluna(L, 0, 0, 0.26, 0, 1.06, 0.96, 1.30, 30, 0.9);
    traco(L, 0, [[0, 0, 0.99]], 1.30, 0.45, { plano: XZ, n: 30 });

    /* ---- elo 1: cintura ---- */
    coluna(L, 1, 0, -0.14, 0, 0.99, 1.02, 0.42, 30, 0.85);
    /* garfo do ombro: duas chapas laterais que abraçam o eixo J2 */
    [-1, 1].forEach(function (s) {
      chapa(L, 1, [[0, 0.30, 0.86], [0, 1.05, 1.02]],
            s * 0.62, s * 0.96, 0.8, { n: 34, nervura: 8 });
    });

    /* ---- elo 2: ombro e braço ----
       O corpo é uma cápsula de 1,02 a 0,80 de raio ao longo de 3,45 — a
       proporção lida no desenho de referência. O RECORTE interno é o que faz
       a peça ser reconhecível: sem ele o braço vira um bastão qualquer. */
    chapa(L, 2, [[0, 0, 1.04], [0, 3.45, 0.82]], -0.70, 0.70, 1, { nervura: 5 });
    [-0.70, 0.70].forEach(function (z) {
      traco(L, 2, [[0, 0.92, 0.52], [0, 2.62, 0.40]], z, 0.48, { n: 30 });
    });
    /* Tampa do eixo do ombro, uma de cada lado. Havia um anel interno de raio
       .40 em cada tampa: em aresta pura, sem remoção de linha oculta, os
       quatro círculos concêntricos se somavam e a peça lia como um par de
       rodas. Um círculo por lado basta para dizer "aqui gira". */
    [-1, 1].forEach(function (s) {
      chapa(L, 2, [[0, 0, 0.74]], s * 0.70, s * 0.80, 0.7, { n: 30, nervura: 9 });
    });

    /* ---- elo 3: antebraço ---- */
    chapa(L, 3, [[0, 0, 0.80], [0, 2.95, 0.50]], -0.54, 0.54, 1, { nervura: 5 });
    [-0.54, 0.54].forEach(function (z) {
      traco(L, 3, [[0, 0.62, 0.34], [0, 1.95, 0.26]], z, 0.42, { n: 26 });
    });
    /* a gravação "6-AXIS" do desenho vira um friso: duas linhas paralelas */
    [-0.545, 0.545].forEach(function (z) {
      aresta(L, 3, [-0.30, 1.10, z], [0.30, 1.16, z], 0.34);
      aresta(L, 3, [-0.30, 0.94, z], [0.30, 1.00, z], 0.34);
    });
    coluna(L, 3, 0, 2.62, 0, 0.46, 0.44, 0.36, 22, 0.75);

    /* ---- elo 4: rolagem do antebraço ---- */
    coluna(L, 4, 0, -0.06, 0, 0.43, 0.41, 0.60, 22, 0.8);
    traco(L, 4, [[0, 0, 0.30]], 0.55, 0.4, { plano: XZ, n: 18 });

    /* ---- elo 5: punho ---- */
    chapa(L, 5, [[0, 0, 0.42], [0, 0.62, 0.36]], -0.34, 0.34, 0.9, { n: 34, nervura: 7 });
    coluna(L, 5, 0, 0.60, 0, 0.34, 0.32, 0.20, 20, 0.7);

    /* ---- elo 6: ferramenta ----
       No desenho a garra tem duas engrenagens visíveis nos nós dos dedos. São
       o único lugar da peça com dentes, e por isso valem o custo: é o detalhe
       que denuncia que a garra ABRE. */
    chapa(L, 6, [[0, 0.16, 0.30], [0, 0.86, 0.40]], -0.30, 0.30, 0.9,
          { n: 32, nervura: 7 });
    traco(L, 6, [[0, 0.50, 0.17]], 0.305, 0.45, { n: 16 });
    [-1, 1].forEach(function (s) {
      var cx = s * PIVO_DEDO * 0.42;
      traco(L, 6, [[cx, PIVO_DEDO, 0.23]], 0.31, 0.6, { n: 20 });
      for (var d = 0; d < 12; d++) {
        var a0 = (d / 12) * TAU;
        aresta(L, 6,
          [cx + Math.cos(a0) * 0.17, PIVO_DEDO + Math.sin(a0) * 0.17, 0.31],
          [cx + Math.cos(a0) * 0.23, PIVO_DEDO + Math.sin(a0) * 0.23, 0.31], 0.4);
      }
    });

    /* ---- elos 7 e 8: os dedos ----
       Escritos com o nó na origem e crescendo em +Y — PARA FORA do punho. O
       perfil serve os dois lados pelo sinal de x, e a ponta curva para DENTRO
       (-s), que é o que faz duas peças isoladas lerem como uma garra: dedos
       que se afastam na ponta parecem antena, não pinça. */
    [7, 8].forEach(function (elo) {
      var s = elo === 7 ? -1 : 1;
      chapa(L, elo, [[0, 0, 0.19], [-s * 0.05, 0.50, 0.15], [-s * 0.17, 0.98, 0.11]],
            -0.14, 0.14, 0.95, { n: 30, nervura: 9 });
      /* estrias da face interna: é por onde a peça é segurada */
      for (var g = 0; g < 4; g++) {
        var t = g / 3;
        var x = -s * (0.06 + t * 0.13), y = 0.60 + t * 0.30;
        aresta(L, elo, [x, y, -0.14], [x, y, 0.14], 0.32);
      }
    });

    /* os 8 cantos de cada caixa, já em forma de lista de pontos */
    var cantos = CAIXAS.map(function (c) {
      var p = [];
      for (var i = 0; i < 8; i++) {
        p.push([c[(i & 1) ? 3 : 0], c[(i & 2) ? 4 : 1], c[(i & 4) ? 5 : 2]]);
      }
      return p;
    });
    return { segmentos: new Float32Array(L), cantos: cantos };
  }

  /* ---------------------------- cinemática ----------------------------
     Um ciclo de trabalho de 13 s: a peça alcança, fecha a garra, recolhe e
     abre. Não é enfeite — é o que a máquina faz, e é lento o bastante para
     não disputar leitura com a headline (design.md §7, regra 6).

     Vive no escopo do módulo, e não dentro de montar(), para que
     ferramentas/previa_braco.js rode ESTA função em vez de uma cópia. A cópia
     existiu por meia hora e já tinha divergido: a amplitude da cintura mudou
     aqui e não lá, e a prévia passou a medir um braço que o site não desenha.
     Prévia que diverge do original não é prévia, é ficção. */
  var CICLO = 13;

  function pose(t) {
    var f = reduzido ? 0.22 : (t / CICLO) % 1;
    var w = f * TAU;
    /* suavização por cosseno: nenhuma junta parte nem para de repente */
    var s1 = Math.sin(w), s2 = Math.sin(w + 0.85), s3 = Math.sin(w + 1.5);

    var a1 = s1 * 0.20;                    /* cintura varre o campo */
    var a2 = -0.12 + s2 * 0.10;            /* ombro */
    var a3 = -2.30 + s3 * 0.16;            /* cotovelo: dobra à frente */
    var a4 = s1 * 0.22;                    /* rolagem do antebraço */
    var a5 = -0.20 - s3 * 0.14;            /* punho mantém a garra no prumo */
    var a6 = s2 * 0.34;

    /* A garra fecha na metade do curso e reabre — meia onda, elevada a 3
       para SEGURAR fechada em vez de bater e voltar. */
    var fecha = Math.pow(Math.max(0, Math.sin(w - 0.5)), 3);
    var abertura = 0.30 - fecha * 0.26;

    var m = new Array(9);
    m[0] = transladar(0, 0, 0);
    m[1] = mult(mult(m[0], transladar(PIVO[1][0], PIVO[1][1], PIVO[1][2])), giroY(a1));
    m[2] = mult(mult(m[1], transladar(PIVO[2][0], PIVO[2][1], PIVO[2][2])), giroZ(a2));
    m[3] = mult(mult(m[2], transladar(PIVO[3][0], PIVO[3][1], PIVO[3][2])), giroZ(a3));
    m[4] = mult(mult(m[3], transladar(PIVO[4][0], PIVO[4][1], PIVO[4][2])), giroY(a4));
    m[5] = mult(mult(m[4], transladar(PIVO[5][0], PIVO[5][1], PIVO[5][2])), giroZ(a5));
    m[6] = mult(mult(m[5], transladar(PIVO[6][0], PIVO[6][1], PIVO[6][2])), giroY(a6));
    /* O sinal por lado não é simétrico por acaso: o dedo cresce em +Y, e
       girar +θ em Z leva +Y para (-sinθ, cosθ). Para o dedo de +x abrir
       (ir para +x) o ângulo tem de ser NEGATIVO. Com os dois sinais iguais
       a garra abria de lado, os dois dedos para o mesmo lado. */
    m[7] = mult(mult(m[6], transladar(-PIVO_DEDO * 0.42, PIVO_DEDO, 0)), giroZ(abertura));
    m[8] = mult(mult(m[6], transladar(PIVO_DEDO * 0.42, PIVO_DEDO, 0)), giroZ(-abertura));
    return m;
  }

  /* --------------------------- enquadramento ---------------------------
     A distância da câmera NÃO é uma constante. Não pode ser: a silhueta deste
     braço muda de PROPORÇÃO com o azimute — de pé ele é retrato (medido:
     218 x 313 px), aberto de lado é paisagem (498 x 371). Uma distância fixa
     ou corta a garra quando o visitante gira, ou deixa a peça pequena o tempo
     todo para caber no pior caso. As duas saídas são ruins.

     Então a câmera resolve a própria distância por quadro, a partir dos 8
     cantos da caixa de cada elo — já transformados pela cinemática, então o
     ciclo de trabalho entra na conta junto. Um ponto a `z` de profundidade e
     `x` de afastamento lateral só cabe se `d >= z + |x| / tan(meio campo)`; a
     resposta é o maior valor entre todos os cantos e os dois eixos.

     Fica FORA de montar() de propósito: é função pura, e é a mesma que
     ferramentas/previa_braco.js roda para medir enquadramento fora do
     navegador. Medida que vale para o site tem de sair do código do site. */
  var FOV = 0.52;
  var MIRA = 3.3;      /* altura visada: o meio da peça, não a base */
  /* Folga de respiro. Não é gosto: a caixa de cada elo SUPERESTIMA a silhueta
     (canto de caixa cai fora da peça arredondada), então parte da margem já
     vem de graça. Varrido a órbita inteira x o ciclo inteiro na moldura real
     430x584 — AR .86 dava 68% de ocupação em repouso e 34 px de folga no pior
     caso; AR 1.00 dava 78% mas só 2 px, apertado demais para linha com
     antisserrilhado. .96 ficava em 75% x 79% com 13 px garantidos.

     Subiu para 1,00 quando o traço ganhou espessura de verdade: a folga
     existia para o desenho não encostar na moldura, e a caixa de cada elo
     SUPERESTIMA a silhueta, então parte dela continua vindo de graça. Os 4%
     recuperados pagam quase toda a perda de tamanho que o movimento maior
     custou. Parou em 0,98 e não em 1,00: varrendo 180 quadros (12 ângulos x
     5 fases x 3 inclinações), 1,00 deixava a base transbordar 2 px no pior
     caso, e a garantia de nunca cortar vale mais que 2% de tamanho. */
  var AR = 0.98;

  /* A CONTA está em gl.js, porque é geométrica e não sabe nada de braço — a
     marca extrudada de marca.js usa a mesma. O que fica aqui é só a ligação
     dos três valores que SÃO deste desenho: MIRA, FOV e AR.

     A assinatura de 5 argumentos é preservada de propósito:
     ferramentas/previa_braco.js exporta e chama `enquadrar(cantos, matrizes,
     giro, incl, prop)`, e uma prévia que deixa de rodar não mede nada. */
  function enquadrar(cantos, matrizes, giro, inclinacao, prop) {
    return G.enquadrarCaixas(cantos, matrizes, giro, inclinacao, prop, MIRA, FOV, AR);
  }

  /* ============================== shaders ============================== */
  var VS = [
    "#version 300 es",
    /* `canto` é o único atributo NÃO instanciado: seis vértices que descrevem
       o retângulo em coordenadas locais (lado -1/+1, ponta A/B). O resto vem
       por instância, um conjunto por segmento. */
    "in vec2 canto;",
    "in vec3 pa;",
    "in vec3 pb;",
    "in float peso;",
    "in float elo;",
    "uniform mat4 uMVP;",
    "uniform mat4 uElo[9];",
    "uniform vec2  uEscala;",
    "uniform float uFina;",
    "uniform float uGrossa;",
    "uniform float uDist;",
    "uniform float uRaioPeca;",
    "out float vPeso;",
    "out float vProf;",
    "out vec2  vTela;",
    "out float vBorda;",
    "out float vMeia;",
    "void main() {",
    "  mat4 M = uElo[int(elo)];",
    "  vec4 ca = uMVP * M * vec4(pa, 1.0);",
    "  vec4 cb = uMVP * M * vec4(pb, 1.0);",
    "  vec4 c = canto.y < 0.5 ? ca : cb;",

    /* ESPESSURA DE VERDADE.
       `gl.LINES` desenha 1 pixel de DISPOSITIVO e `lineWidth > 1` é ignorado
       no Chrome — em DPR 2 isso é meio pixel de CSS, e o desenho lia como
       fantasma por mais alfa que levasse. Aqui cada segmento é expandido num
       retângulo na direção NORMAL à linha, medida em PIXELS de tela: a
       largura fica igual perto e longe, e o `peso` finalmente controla
       espessura em vez de fingir espessura com transparência. */
    "  vec2 sa = ca.xy / ca.w * uEscala;",
    "  vec2 sb = cb.xy / cb.w * uEscala;",
    "  vec2 d = sb - sa;",
    "  float comp = length(d);",
    "  vec2 nrm = comp > 1e-4 ? vec2(-d.y, d.x) / comp : vec2(0.0, 0.0);",
    "  float meia = mix(uFina, uGrossa, clamp(peso, 0.0, 1.0)) * 0.5;",
    "  vMeia = meia;",
    /* 0,8 px a mais de cada lado: é a rampa que o fragment usa para suavizar
       a borda sem depender de MSAA */
    "  vBorda = canto.x * (meia + 0.8);",
    "  vec2 s = (canto.y < 0.5 ? sa : sb) + nrm * vBorda;",
    "  vec2 ndc = s / uEscala;",
    "  gl_Position = vec4(ndc * c.w, c.z, c.w);",

    /* Atenuação por profundidade — o ÚNICO mecanismo de leitura de forma que
       este desenho tem, já que sem face não há remoção de linha oculta.

       A rampa é RELATIVA à câmera (`uDist`) e ao raio da peça, não a
       distâncias absolutas. As constantes antigas (15,0 e 7,5) foram medidas
       quando a câmera era fixa; depois o enquadramento virou automático e a
       distância passou a variar de 16,5 a 25,3 conforme a moldura — a mesma
       aresta caía em pontos diferentes da rampa. Assim ela acompanha o zoom.

       O piso subiu de 0,20 para 0,55: medido, o contorno estrutural no fundo
       dava 1,47:1 e sumia; agora dá 3,19:1, acima do piso do WCAG 1.4.11, e a
       frente continua em 7,60:1. A hierarquia de profundidade fica inteira —
       ela só deixou de APAGAR o que devia apenas recuar. */
    "  vProf = clamp(1.0 - (c.w - (uDist - uRaioPeca)) / (2.0 * uRaioPeca), 0.55, 1.0);",
    "  vPeso = peso;",
    /* posição em espaço de tela, 0..1 — é onde a lente do ponteiro vive */
    "  vTela = ndc * 0.5 + 0.5;",
    "}"
  ].join("\n");

  var FS = [
    "#version 300 es",
    "precision highp float;",
    "in float vPeso;",
    "in float vProf;",
    "in vec2  vTela;",
    "in float vBorda;",
    "in float vMeia;",
    "uniform vec3  uTinta;",
    "uniform vec3  uAceso;",
    "uniform vec3  uTintaB;",
    "uniform vec3  uAcesoB;",
    "uniform float uCorte;",
    "uniform float uGanhoA;",
    "uniform float uGanhoB;",
    "uniform vec2  uPonteiro;",
    "uniform float uRaio;",
    "uniform float uAtivo;",
    "uniform float uProp;",
    "uniform float uTempo;",
    "uniform float uEntrada;",
    "out vec4 cor;",

    /* Mesmo ruído da lente (js/lente.js) e da marca (js/marca.js): as
       revelações do site têm de ter a MESMA aresta, senão a página parece ter
       vários instrumentos diferentes apontados para ela. Fonte única em
       gl.js. */
    G.RUIDO_GLSL,

    "void main() {",
    /* A PEÇA ATRAVESSA DUAS FOLHAS.
       O braço sangra para fora do herói e entra na seção clara de baixo. Medido:
       #9FBEE0 sobre branco dá 1,92:1 — o desenho simplesmente sumiria ali. Então
       a tinta troca na altura exata em que o herói acaba (uCorte, em espaço de
       tela), como um desenho que segue na prancha seguinte: azul-aço sobre o
       navy, navy sobre o papel branco. O GANHO troca junto, porque tinta escura
       sobre claro precisa de mais alfa para o mesmo contraste — .92 em cima,
       1.15 embaixo, que é o que põe a aresta estrutural mais fraca em 4,92:1
       em vez de 3,33:1. A transição tem 4 milésimos de largura: é aresta de
       papel, não degradê. */
    "  float lado = smoothstep(uCorte - 0.004, uCorte + 0.004, vTela.y);",
    "  vec3  cTinta = mix(uTintaB, uTinta, lado);",
    "  vec3  cAceso = mix(uAcesoB, uAceso, lado);",
    "  float ganho  = mix(uGanhoB, uGanhoA, lado);",
    "  float d = length((vTela - uPonteiro) * vec2(uProp, 1.0)) / max(uRaio, 1e-4);",
    "  float n = (fbm(vTela * 9.0 + uTempo * 0.05) - 0.5) * 0.17;",
    "  float rev = (1.0 - smoothstep(0.80, 1.04, d + n)) * uAtivo;",

    /* A curva de alfa NÃO é mais `peso` puro. Com ela, o peso baixo caía perto
       do fundo: peso .30 dava 28% de alfa e 1,82:1 — a aresta existia no
       buffer e não existia na tela. `0,55 + 0,45 x peso` mantém a mesma
       HIERARQUIA e levanta o piso: medido sobre o navy do herói,

         peso 1,00 -> 92% -> 7,60:1     (era 7,60:1)
         peso 0,60 -> 75% -> 5,51:1     (era 3,58:1)
         peso 0,30 -> 63% -> 4,24:1     (era 1,82:1)

       Abaixo do corte, com o ganho 1,15, a mesma curva dá 10,47:1 no peso .60.
       Nenhuma aresta fica mais abaixo do piso de 3:1 do WCAG 1.4.11. */
    "  float a = (0.55 + 0.45 * vPeso) * ganho * vProf * uEntrada",
    "          * (1.0 + rev * 0.42);",
    "  vec3 c = mix(cTinta, cAceso, rev);",

    /* Banda dourada no limite da lente: a mesma gaussiana da lente, e a mesma
       função — provar que há um instrumento ali, não um borrão. */
    /* Gaussiana pelo QUADRADO, não por pow(). Em GLSL `pow(x, y)` é indefinido
       para x < 0, e aqui (d + n - 0.94) é negativo em toda a parte de dentro da
       lente — que é justamente onde a banda tem de valer zero. Vários drivers
       devolvem NaN nesse caso, e NaN sobrevive à multiplicação por uAtivo. */
    "  float t = (d + n - 0.94) * 20.0;",
    "  float banda = exp(-t * t) * uAtivo * uEntrada;",
    "  c = mix(c, cAceso, clamp(banda * 0.85, 0.0, 1.0));",
    "  a = max(a, banda * vPeso * 0.75);",

    /* Antisserrilhado próprio: a borda do retângulo vira uma rampa de 1 px em
       vez de depender do MSAA, que em linha fina resolve mal e come justamente
       a intensidade que se quer. `vBorda` é o afastamento lateral em pixels e
       `vMeia` a meia-largura pedida. */
    "  a *= 1.0 - smoothstep(vMeia - 0.5, vMeia + 0.5, abs(vBorda));",
    "  cor = vec4(c, clamp(a, 0.0, 1.0));",
    "}"
  ].join("\n");

  /* `compilar`, `programa` e `rgb` vivem em gl.js — ver o alias no topo. */

  /* =============================== montagem =============================== */
  function montar(raiz) {
    var canvas = raiz.querySelector(".braco__tela");
    if (!canvas || !window.WebGL2RenderingContext) {
      raiz.classList.add("is-indisponivel");
      return;
    }
    var gl = canvas.getContext("webgl2", {
      /* `antialias: false` de propósito: a borda do traço tem rampa própria
         no fragment shader, e o MSAA em linha fina resolve mal — come a
         intensidade justamente onde ela faz falta. */
      alpha: true, premultipliedAlpha: false, antialias: false,
      depth: false, powerPreference: "low-power"
    });
    if (!gl) { raiz.classList.add("is-indisponivel"); return; }

    var prog = programa(gl, VS, FS, "braco");
    if (!prog) { raiz.classList.add("is-indisponivel"); return; }

    var cena = construir();
    var dados = cena.segmentos;
    var nSegmentos = dados.length / 8;

    var vao = gl.createVertexArray();
    gl.bindVertexArray(vao);

    /* O retângulo: seis vértices, um triângulo de cada lado da diagonal.
       Não é instanciado — é o mesmo para os 1421 segmentos. */
    var bufQuad = gl.createBuffer();
    gl.bindBuffer(gl.ARRAY_BUFFER, bufQuad);
    gl.bufferData(gl.ARRAY_BUFFER, new Float32Array([
      -1, 0,   1, 0,  -1, 1,
      -1, 1,   1, 0,   1, 1
    ]), gl.STATIC_DRAW);
    var aCanto = gl.getAttribLocation(prog, "canto");
    gl.enableVertexAttribArray(aCanto);
    gl.vertexAttribPointer(aCanto, 2, gl.FLOAT, false, 8, 0);

    /* Um conjunto por SEGMENTO, com divisor 1. Instanciar em vez de duplicar
       os seis vértices na CPU derruba o buffer de 341 KB para 45 KB — e, mais
       importante, mantém a geometria escrita uma vez só. */
    var bufSeg = gl.createBuffer();
    gl.bindBuffer(gl.ARRAY_BUFFER, bufSeg);
    gl.bufferData(gl.ARRAY_BUFFER, dados, gl.STATIC_DRAW);
    [["pa", 3, 0], ["pb", 3, 12], ["peso", 1, 24], ["elo", 1, 28]]
      .forEach(function (a) {
        var loc = gl.getAttribLocation(prog, a[0]);
        gl.enableVertexAttribArray(loc);
        gl.vertexAttribPointer(loc, a[1], gl.FLOAT, false, 32, a[2]);
        gl.vertexAttribDivisor(loc, 1);
      });

    /* Raio da peça em torno do ponto visado: alimenta a rampa de profundidade,
       que agora é relativa à câmera. Medido uma vez, na pose de repouso. */
    var RAIO = (function () {
      var m = pose(0), maior = 1;
      for (var e = 0; e < cena.cantos.length; e++) {
        var pts = cena.cantos[e], M = m[e];
        if (!pts || !M) continue;
        for (var i = 0; i < 8; i++) {
          var q = pts[i];
          var x = M[0] * q[0] + M[4] * q[1] + M[8] * q[2] + M[12];
          var y = M[1] * q[0] + M[5] * q[1] + M[9] * q[2] + M[13] - MIRA;
          var z = M[2] * q[0] + M[6] * q[1] + M[10] * q[2] + M[14];
          maior = Math.max(maior, Math.hypot(x, y, z));
        }
      }
      return maior;
    })();

    gl.enable(gl.BLEND);
    gl.blendFuncSeparate(gl.SRC_ALPHA, gl.ONE_MINUS_SRC_ALPHA, gl.ONE,
                         gl.ONE_MINUS_SRC_ALPHA);
    gl.clearColor(0, 0, 0, 0);

    var u = {};
    ["uMVP", "uTinta", "uAceso", "uTintaB", "uAcesoB", "uCorte", "uGanhoA",
     "uGanhoB", "uPonteiro", "uRaio", "uAtivo", "uProp", "uTempo", "uEntrada",
     "uEscala", "uFina", "uGrossa", "uDist", "uRaioPeca"].forEach(function (n) {
      u[n] = gl.getUniformLocation(prog, n);
    });
    var uElo = [];
    for (var e = 0; e < 9; e++) uElo.push(gl.getUniformLocation(prog, "uElo[" + e + "]"));

    /* ---------------------------- estado ---------------------------- */
    var giro = 2.40, giroVel = 0, inclinacao = 0.16;
    var arrastando = false, ultimoX = 0, ultimoY = 0;
    /* `ativo` NASCE em 1 e decai: a peça chega acesa em accent e esfria
       para o azul de repouso em ~0,8 s. Não é enfeite de carregamento — é a
       costura com a entrada da seção, que entrega o desenho aceso ali.
       Sem isso o herói trocaria de cor em corte seco no instante da entrega. */
    var pontX = 0.5, pontY = 0.44, ativo = 1, alvoAtivo = 0;
    var entrada = 0, dpr = 1, larg = 1, alt = 1;
    var corTinta = [0.62, 0.75, 0.88], corAceso = [0.99, 0.77, 0];
    var corTintaB = [0, 0.21, 0.4], corAcesoB = [0.42, 0.31, 0];
    var ganhoA = 0.92, ganhoB = 1.15, corte = 0;
    var fina = 0.9, grossa = 1.8;
    var heroi = raiz.closest ? raiz.closest(".heroi") : null;
    var visivel = false, rodando = false, anterior = 0, relogio = 0;
    var matrizes = pose(0);

    function lerTema() {
      var cs = getComputedStyle(raiz);
      corTinta = rgb(cs.getPropertyValue("--braco-traco"), [0.62, 0.75, 0.88]);
      corAceso = rgb(cs.getPropertyValue("--braco-aceso"), [0.99, 0.77, 0]);
      corTintaB = rgb(cs.getPropertyValue("--braco-traco-baixo"), corTinta);
      corAcesoB = rgb(cs.getPropertyValue("--braco-aceso-baixo"), corAceso);
      ganhoB = parseFloat(cs.getPropertyValue("--braco-ganho-baixo")) || 1.15;
      /* Largura em PIXELS DE CSS, vinda de token — o dpr entra na hora de
         mandar para o shader. Assim a espessura é a mesma numa tela comum e
         numa de alta densidade, que é o defeito que `gl.LINES` tinha. */
      fina = parseFloat(cs.getPropertyValue("--braco-linha-fina")) || 0.9;
      grossa = parseFloat(cs.getPropertyValue("--braco-linha-grossa")) || 1.8;
    }

    /* Onde o herói acaba, em espaço de tela do canvas. Refeito por quadro
       porque a rolagem não move a peça em relação ao herói, mas o
       redimensionamento e a intro movem. Fora do herói, uCorte fica negativo e
       a folha de baixo simplesmente não existe. */
    function medirCorte() {
      if (!heroi) { corte = -1; return; }
      var c = canvas.getBoundingClientRect();
      if (!c.height) { corte = -1; return; }
      var fim = heroi.getBoundingClientRect().bottom;
      corte = 1 - (fim - c.top) / c.height;
    }

    /* TETO de 4096 px por lado. Não é otimização: é a trava que impede este
       componente de derrubar a página.

       `medir()` LÊ o retângulo e ESCREVE os atributos do canvas, e os
       atributos do canvas são o tamanho intrínseco dele. Se algum dia a
       altura em CSS voltar a não resolver, o intrínseco vaza para o layout,
       o retângulo cresce, e o próximo quadro escreve um valor maior ainda —
       a caixa dobra por quadro até a rolagem ficar impossível. Foi
       exatamente o que aconteceu com `height: 144%` sobre linha de grade
       automática. O CSS já foi corrigido (o canvas é absoluto); esta trava
       existe para que a próxima regressão seja um desenho feio, e não um
       site travado. */
    var TETO = 4096;

    function medir() {
      var c = raiz.getBoundingClientRect();
      /* sem caixa medida ainda: não há o que dimensionar, e escrever aqui é
         justamente o que alimentaria um ciclo */
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


    /* --------------------------- enquadramento ---------------------------
       A distância da câmera NÃO é uma constante. Não pode ser: a silhueta
       deste braço muda de proporção com o azimute — de pé ele é retrato
       (medido: 218 x 313 px), aberto de lado é paisagem (498 x 371). Uma
       distância fixa ou corta a garra quando o visitante gira, ou deixa a peça
       pequena o tempo todo para caber no pior caso. As duas saídas são ruins.

       Então a câmera resolve a própria distância por quadro, a partir dos 8
       cantos da caixa de cada elo — já transformados pela cinemática, então o
       ciclo de trabalho conta junto. Para cada canto, a distância mínima que o
       mantém dentro do tronco é `z + |x| / tan(meio campo)`, nos dois eixos; a
       resposta é o maior de todos. `AR` é a folga de respiro.

       O resultado se lê como uma câmera que acompanha: a peça fica grande
       parada e a vista recua o tanto exato quando o braço se abre. */
    /* Enquadramento por ÂNGULO, não por quadro.
       A primeira versão media a pose do instante, e a peça pulsava de tamanho:
       a cintura gira ±0,20 rad, então em parte do ciclo o braço aponta para a
       câmera (compacto, câmera entra) e em parte atravessa o quadro (largo,
       câmera recua). Medido, a escala oscilava perto de 40% a cada 13 s — leem
       como zoom involuntário, não como máquina trabalhando.

       Agora a distância é o máximo sobre SEIS fases do ciclo, e por isso só
       depende do ângulo de órbita: parada, a peça não muda de tamanho nunca.
       O cálculo é refeito só quando o ângulo muda de fato — girar custa seis
       poses, ficar parado não custa nada. O limiar é 0,05 rad e não 0,02: o
       arrasto move 0,007 rad por pixel, então 0,02 disparava o recálculo em
       praticamente todo quadro. A distância varia devagar com o ângulo e a
       suavização cobre o degrau. */
    var dSuave = 0, dAlvo = 0, enqGiro = 1e9, enqIncl = 1e9, enqProp = 0;

    function distanciaDoAngulo() {
      var prop = larg / alt;
      if (Math.abs(giro - enqGiro) < 0.05 && Math.abs(inclinacao - enqIncl) < 0.05 &&
          prop === enqProp) return dAlvo;
      enqGiro = giro; enqIncl = inclinacao; enqProp = prop;
      var maior = 0;
      for (var k = 0; k < 6; k++) {
        maior = Math.max(maior, enquadrar(cena.cantos, pose(k / 6 * CICLO),
                                          giro, inclinacao, prop));
      }
      dAlvo = maior;
      return dAlvo;
    }

    function mvp() {
      var alvo = distanciaDoAngulo();
      /* suavização: a mudança de escala ao girar chega, mas não em degrau */
      dSuave = dSuave ? dSuave + (alvo - dSuave) * 0.08 : alvo;
      var d = dSuave;
      var o = [
        Math.sin(giro) * Math.cos(inclinacao) * d,
        MIRA + Math.sin(inclinacao) * d,
        Math.cos(giro) * Math.cos(inclinacao) * d
      ];
      var proj = perspectiva(FOV, larg / alt, 1, 120);
      return mult(proj, olhar(o, [0, MIRA, 0], [0, 1, 0]));
    }

    function quadro(agora) {
      var dt = Math.min((agora - anterior) / 1000, 0.05);
      anterior = agora;
      relogio += dt;

      if (!arrastando) {
        giro += giroVel * dt;
        giroVel *= Math.pow(0.02, dt);
        /* deriva de repouso: sem ela a peça parece congelada quando ninguém
           toca, e o convite ao arrasto some */
        if (Math.abs(giroVel) < 0.02 && !reduzido) giro += 0.035 * dt;
      }
      entrada += ((visivel ? 1 : 0) - entrada) * (1 - Math.pow(0.02, dt));
      /* subir é rápido (o ponteiro chegou), descer é lento (a peça esfria) */
      ativo += (alvoAtivo - ativo) *
               (1 - Math.pow(alvoAtivo > ativo ? 0.002 : 0.06, dt));

      medir();
      medirCorte();
      matrizes = pose(relogio);

      gl.clear(gl.COLOR_BUFFER_BIT);
      gl.useProgram(prog);
      gl.bindVertexArray(vao);
      gl.uniformMatrix4fv(u.uMVP, false, mvp());
      for (var i = 0; i < 9; i++) gl.uniformMatrix4fv(uElo[i], false, matrizes[i]);
      gl.uniform3fv(u.uTinta, corTinta);
      gl.uniform3fv(u.uAceso, corAceso);
      gl.uniform3fv(u.uTintaB, corTintaB);
      gl.uniform3fv(u.uAcesoB, corAcesoB);
      gl.uniform1f(u.uCorte, corte);
      gl.uniform1f(u.uGanhoA, ganhoA);
      gl.uniform1f(u.uGanhoB, ganhoB);
      gl.uniform2f(u.uEscala, canvas.width / 2, canvas.height / 2);
      gl.uniform1f(u.uFina, fina * dpr);
      gl.uniform1f(u.uGrossa, grossa * dpr);
      gl.uniform1f(u.uDist, dSuave || 20);
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
       O mesmo ponteiro faz as duas coisas: acende a lente onde está e, com o
       botão apertado, orbita. Não há modo — é a peça que responde. */
    function situar(e) {
      var c = raiz.getBoundingClientRect();
      pontX = (e.clientX - c.left) / Math.max(1, c.width);
      /* O Y É INVERTIDO, e tem de ser.
         `vTela` sai de NDC (`p.xy / p.w * 0.5 + 0.5`), onde +1 é o TOPO — logo
         vTela.y vale 1 em cima e 0 embaixo. O ponteiro do DOM é o contrário:
         clientY cresce para baixo. Sem esta subtração a lente aparece
         espelhada na vertical: ponteiro no alto, dourado embaixo. É o mesmo
         eixo que `medirCorte()` já compensava — só este ponto tinha ficado
         para trás. */
      pontY = 1 - (e.clientY - c.top) / Math.max(1, c.height);
    }

    /* A LENTE OUVE O HERÓI INTEIRO, o arrasto só a peça.

       Ligada apenas em `.braco`, a lente acendia quando o ponteiro estava
       sobre a máquina e apagava sobre o texto — e como o texto também acende
       (ver main.js §8), o dourado SALTAVA de um para o outro em vez de varrer.
       Ouvindo a seção, a mesma passada acende os dois, e é a mesma coordenada
       que alimenta os dois: um instrumento, não dois.

       `situar()` continua medindo em relação ao CANVAS, então o ponteiro sobre
       o texto vira uma posição fora de 0..1 e a lente simplesmente cai fora —
       que é o comportamento certo, sem nenhum caso especial. */
    var campo = (raiz.closest && raiz.closest(".heroi")) || raiz;

    campo.addEventListener("pointerenter", function () {
      alvoAtivo = 1; acordar();
    });
    campo.addEventListener("pointerleave", function () {
      if (arrastando) return;
      alvoAtivo = 0; acordar();
    });
    campo.addEventListener("pointermove", function (e) {
      if (arrastando) return;   /* durante o arrasto quem manda é o listener da peça */
      situar(e);
      alvoAtivo = 1;
      acordar();
    });
    raiz.addEventListener("pointerdown", function (e) {
      arrastando = true;
      ultimoX = e.clientX; ultimoY = e.clientY;
      situar(e);
      alvoAtivo = 1;
      if (raiz.setPointerCapture) raiz.setPointerCapture(e.pointerId);
      acordar();
    });
    raiz.addEventListener("pointermove", function (e) {
      situar(e);
      alvoAtivo = 1;
      if (arrastando) {
        var dx = e.clientX - ultimoX, dy = e.clientY - ultimoY;
        ultimoX = e.clientX; ultimoY = e.clientY;
        giro -= dx * 0.007;
        giroVel = -dx * 0.14;
        /* trava a inclinação: abaixo de -0,25 o visitante olha o flange por
           baixo, acima de 0,95 vê a peça de cima e ela deixa de ser um braço */
        inclinacao = Math.max(-0.25, Math.min(0.95, inclinacao + dy * 0.004));
      }
      acordar();
    });
    function soltar(e) {
      if (!arrastando) return;
      arrastando = false;
      if (e && e.pointerId != null && raiz.hasPointerCapture &&
          raiz.hasPointerCapture(e.pointerId)) raiz.releasePointerCapture(e.pointerId);
      /* No toque não há hover: a lente fica acesa enquanto o dedo está na
         peça e apaga ao soltar, senão ficaria presa para sempre. */
      if (window.matchMedia("(hover: none)").matches) alvoAtivo = 0;
      acordar();
    }
    raiz.addEventListener("pointerup", soltar);
    raiz.addEventListener("pointercancel", soltar);

    /* Teclado: a peça é conteúdo, e conteúdo se navega sem ponteiro. As setas
       orbitam e a lente vai para o centro, senão quem usa teclado nunca veria
       o dourado acontecer. */
    raiz.addEventListener("keydown", function (e) {
      var passo = 0.18;
      if (e.key === "ArrowLeft") giro -= passo;
      else if (e.key === "ArrowRight") giro += passo;
      else if (e.key === "ArrowUp") inclinacao = Math.min(0.95, inclinacao + 0.08);
      else if (e.key === "ArrowDown") inclinacao = Math.max(-0.25, inclinacao - 0.08);
      else return;
      e.preventDefault();
      pontX = 0.5; pontY = 0.46; alvoAtivo = 1;
      acordar();
    });
    raiz.addEventListener("focus", function () {
      pontX = 0.5; pontY = 0.46; alvoAtivo = 1; acordar();
    });
    raiz.addEventListener("blur", function () { alvoAtivo = 0; acordar(); });

    /* `lerTema` roda UMA vez. Ele reagia a `temachange` e ao esquema do
       sistema enquanto havia dois temas; com tema único não há o que reler. */
    lerTema();
    medir();
    window.addEventListener("resize", function () { medir(); acordar(); });

    /* A peça é conteúdo navegável, então entra na ordem de tabulação — mas
       só depois de o WebGL2 ter dado certo. Focar um PNG estático não leva
       a lugar nenhum, e um ponto de parada morto é pior que nenhum. */
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
    var els = document.querySelectorAll("[data-braco]");
    for (var i = 0; i < els.length; i++) montar(els[i]);
  }

  if (document.readyState === "loading") {
    document.addEventListener("DOMContentLoaded", iniciar);
  } else {
    iniciar();
  }
})();
