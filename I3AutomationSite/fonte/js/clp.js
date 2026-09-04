/* ============================================================================
   clp.js — o CLP explodido
   i3Automations

   O QUE ELA É. Um controlador lógico programável em axonometria explodida:
   trilho DIN e barramento, fonte, CPU, dois cartões de E/S e os bornes
   frontais. Em repouso os módulos estão levemente separados; ao apontar a
   lista de capacidades eles se DESPLUGAM do barramento, na ordem em que
   qualquer um os tiraria com a mão.

   POR QUE UM CLP, E NÃO O ARMÁRIO INTEIRO. A primeira versão era um painel
   completo -- placa, trilhos, disjuntores, canaleta, porta -- e o usuário não
   entendeu: com tanta peça e a porta cobrindo tudo pela frente, a leitura era
   "uma caixa". O CLP tem seis módulos numa fileira só, e a fileira SE EXPLICA:
   dá para contar as partes e ver o barramento por trás.

   E é o assunto certo desta página: "PLC Programming" é a segunda das oito
   disciplinas, e o rack é o objeto que a i3 realmente especifica, monta e
   programa.

   COMO ELA SE ENCAIXA. Mesma família de `braco.js`: segmentos em lista,
   expansão em quad no vertex shader, instâncias, atenuação por profundidade e
   a lente dourada sob o ponteiro. O que muda é a cinemática -- lá são nove
   matrizes de rotação, aqui são seis TRANSLAÇÕES ao longo da profundidade.
   ============================================================================ */
(function () {
  "use strict";
  var G = (typeof globalThis !== "undefined" ? globalThis : window).I3GL;
  if (!G) return;

  var mult = G.mult, transladar = G.transladar;
  var perspectiva = G.perspectiva, olhar = G.olhar, rgb = G.rgb;
  var programa = G.programa, enquadrarCaixas = G.enquadrarCaixas;
  var cantosDaCaixa = G.cantosDaCaixa;

  /* ============================== geometria ==============================
     `S` é a lista de SEGMENTOS, 8 floats cada:
        ax, ay, az, bx, by, bz, peso, camada
     `peso` 1 = contorno estrutural, .45 = detalhe. `camada` é o índice da
     matriz de explosão. Mesma convenção de braco.js, de propósito. */
  var S = [];

  function seg(a, b, peso, cam) {
    S.push(a[0], a[1], a[2], b[0], b[1], b[2], peso, cam);
  }

  /* Arestas de uma caixa alinhada aos eixos: centro e meia-extensão. */
  function caixa(cx, cy, cz, hx, hy, hz, peso, cam) {
    var x0 = cx - hx, x1 = cx + hx, y0 = cy - hy, y1 = cy + hy;
    var z0 = cz - hz, z1 = cz + hz;
    var v = [[x0, y0, z0], [x1, y0, z0], [x1, y1, z0], [x0, y1, z0],
             [x0, y0, z1], [x1, y0, z1], [x1, y1, z1], [x0, y1, z1]];
    var e = [0, 1, 1, 2, 2, 3, 3, 0, 4, 5, 5, 6, 6, 7, 7, 4, 0, 4, 1, 5, 2, 6, 3, 7];
    for (var i = 0; i < e.length; i += 2) seg(v[e[i]], v[e[i + 1]], peso, cam);
  }

  /* --- 0. trilho DIN e barramento: a base, que não se move ------------- */
  var X0 = -2.55, X1 = 2.55;
  caixa(0, -1.02, 0, (X1 - X0) / 2, .10, .09, 1, 0);      /* trilho DIN */
  caixa(0, .10, -.02, (X1 - X0) / 2, .92, .06, 1, 0);     /* placa de fundo */
  /* o barramento: a fileira de contatos em que cada módulo pluga */
  for (var i = 0; i < 26; i++) {
    var bx = X0 + .22 + i * ((X1 - X0 - .44) / 25);
    seg([bx, .74, .05], [bx, .92, .05], .45, 0);
  }
  seg([X0 + .18, .83, .05], [X1 - .18, .83, .05], .45, 0);

  /* --- os cinco módulos, numa fileira ---------------------------------- */
  var MOD = [
    /* x centro, meia-largura, camada, rótulo interno */
    [-2.06, .44, 1],   /* fonte */
    [-1.02, .56, 2],   /* CPU, mais larga */
    [ 0.10, .34, 3],   /* cartão de entradas */
    [ 0.86, .34, 4],   /* cartão de saídas */
    [ 1.62, .34, 4]    /* segundo cartão de saídas, mesma camada */
  ];

  for (i = 0; i < MOD.length; i++) {
    var mx = MOD[i][0], hw = MOD[i][1], cam = MOD[i][2];
    caixa(mx, .06, .30, hw, .82, .26, 1, cam);            /* corpo do módulo */
    /* a lingueta de encaixe no trilho, embaixo */
    caixa(mx, -.86, .26, hw * .5, .12, .16, .45, cam);
    /* ranhuras de ventilação na frente: é o que faz o bloco LER como módulo
       e não como caixa, e são a única textura da peça */
    for (var k = 0; k < 5; k++) {
      var vy = .48 - k * .17;
      seg([mx - hw * .62, vy, .56], [mx + hw * .62, vy, .56], .3, cam);
    }
  }

  /* CPU: display e LEDs de estado, que é o que distingue a CPU dos cartões */
  caixa(-1.02, .48, .57, .34, .22, .02, .45, 2);
  for (i = 0; i < 4; i++) {
    seg([-1.30 + i * .19, .04, .57], [-1.30 + i * .19, .12, .57], .45, 2);
  }
  /* a porta serial/ethernet, embaixo da CPU */
  caixa(-1.02, -.42, .57, .16, .12, .02, .45, 2);

  /* fonte: os bornes de alimentação, maiores */
  for (i = 0; i < 3; i++) {
    seg([-2.34 + i * .28, -.30, .57], [-2.34 + i * .28, -.06, .57], .45, 1);
  }

  /* --- 5. bornes frontais: saem por último, e mais longe ---------------- */
  for (i = 2; i < MOD.length; i++) {
    var tx = MOD[i][0], tw = MOD[i][1];
    caixa(tx, .10, .62, tw * .88, .70, .07, 1, 5);
    for (k = 0; k < 8; k++) {
      var ty = .70 - k * .18;
      seg([tx - tw * .80, ty, .70], [tx + tw * .80, ty, .70], .3, 5);
    }
  }

  var N_CAM = 6;
  /* Deslocamento de explosão por camada. Os bornes vão MAIS LONGE porque são
     a primeira coisa que sai quando alguém troca um cartão -- a ordem da
     separação é a ordem real de desmontagem, não um escalonamento decorativo. */
  var AFASTA = [0, 1.05, 1.35, 1.65, 1.95, 3.20];

  var VS = [
    "#version 300 es",
    "layout(location=0) in vec2 aQuad;",
    "layout(location=1) in vec3 aA;",
    "layout(location=2) in vec3 aB;",
    "layout(location=3) in float aPeso;",
    "layout(location=4) in float aCam;",
    "uniform mat4 uMVP;",
    "uniform mat4 uCam[6];",
    "uniform vec2 uTela;",
    "uniform float uFina, uGrossa, uDist, uRaioPeca;",
    "out float vPeso, vProf, vBorda;",
    "out vec2 vNdc;",
    "void main(){",
    "  int c = int(aCam + 0.5);",
    "  vec4 pa = uMVP * uCam[c] * vec4(aA, 1.0);",
    "  vec4 pb = uMVP * uCam[c] * vec4(aB, 1.0);",
    /* Expansão em QUAD, e não gl.LINES: `lineWidth > 1` é ignorado no Chrome,
       então a linha sairia com 1 pixel de DISPOSITIVO -- meio pixel de CSS
       numa tela 2x, que é o defeito de "peça fantasma" já pago em braco.js. */
    "  vec2 sa = pa.xy / pa.w * uTela * 0.5;",
    "  vec2 sb = pb.xy / pb.w * uTela * 0.5;",
    "  vec2 dir = sb - sa;",
    "  float L = max(length(dir), 1e-4);",
    "  vec2 n = vec2(-dir.y, dir.x) / L;",
    "  float larg = mix(uFina, uGrossa, aPeso) * 0.5 + 0.8;",
    "  vec4 p = mix(pa, pb, aQuad.x);",
    "  vec2 s = mix(sa, sb, aQuad.x) + n * aQuad.y * larg;",
    "  gl_Position = vec4(s / (uTela * 0.5) * p.w, p.z, p.w);",
    "  vPeso = aPeso;",
    "  vBorda = aQuad.y * larg;",
    /* NDC 0..1 para a lente. `+1` é o TOPO aqui, e o ponteiro do DOM cresce
       para BAIXO -- o espelho do eixo Y é feito ao publicar `uPonteiro`, e
       não aqui. Foi o bug que custou uma sessão no herói. */
    "  vNdc = gl_Position.xy / gl_Position.w * 0.5 + 0.5;",
    "  vProf = clamp((p.w - (uDist - uRaioPeca)) / (2.0 * uRaioPeca), 0.0, 1.0);",
    "}"
  ].join("\n");

  var FS = [
    "#version 300 es",
    "precision highp float;",
    "in float vPeso, vProf, vBorda;",
    "in vec2 vNdc;",
    "uniform vec3 uTinta, uAceso;",
    "uniform vec2 uPonteiro;",
    "uniform float uFina, uGrossa, uGanho, uRaio, uAtivo, uProp, uTempo;",
    "out vec4 cor;",
    /* MESMO RUÍDO da lente do herói, da marca e da planta. As revelações do
       site têm de ter a MESMA aresta, senão a página parece ter vários
       instrumentos diferentes apontados para ela. Fonte única em gl.js. */
    G.RUIDO_GLSL,
    "void main(){",
    "  float larg = mix(uFina, uGrossa, vPeso) * 0.5;",
    /* rampa própria de antisserrilhado: permite desligar o MSAA, que em linha
       fina resolve mal e come justamente a intensidade que falta */
    "  float a = 1.0 - smoothstep(larg - 0.5, larg + 0.5, abs(vBorda));",
    /* profundidade ancorada na CÂMERA e não em distância absoluta: o
       enquadramento é automático e a distância varia com a moldura */
    "  float p = mix(1.0, 0.55, vProf);",
    /* A LENTE. Mesmo raio e mesma curva do braço -- se um dia o uRaio de lá
       mudar, este muda junto, senão a página passa a ter dois instrumentos de
       tamanhos diferentes apontados para ela. */
    "  float d = length((vNdc - uPonteiro) * vec2(uProp, 1.0)) / max(uRaio, 1e-4);",
    "  float n = (fbm(vNdc * 9.0 + uTempo * 0.05) - 0.5) * 0.17;",
    "  float rev = (1.0 - smoothstep(0.80, 1.04, d + n)) * uAtivo;",
    "  vec3 c = mix(uTinta, uAceso, rev);",
    "  cor = vec4(c, a * p * mix(0.55, 1.0, vPeso) * uGanho * (1.0 + rev * 0.42));",
    "}"
  ].join("\n");

  function montar(raiz) {
    var canvas = raiz.querySelector("canvas");
    if (!canvas) return;
    var gl = canvas.getContext("webgl2", { antialias: false, alpha: true });
    if (!gl) return;                       /* sem WebGL2: fica a reserva do CSS */

    var pp = programa(gl, VS, FS, "clp");
    if (!pp) return;
    raiz.classList.add("is-gl");

    var quad = new Float32Array([0, -1, 1, -1, 1, 1, 0, -1, 1, 1, 0, 1]);
    var vao = gl.createVertexArray();
    gl.bindVertexArray(vao);
    var bq = gl.createBuffer();
    gl.bindBuffer(gl.ARRAY_BUFFER, bq);
    gl.bufferData(gl.ARRAY_BUFFER, quad, gl.STATIC_DRAW);
    gl.enableVertexAttribArray(0);
    gl.vertexAttribPointer(0, 2, gl.FLOAT, false, 0, 0);

    var dados = new Float32Array(S);
    var bs = gl.createBuffer();
    gl.bindBuffer(gl.ARRAY_BUFFER, bs);
    gl.bufferData(gl.ARRAY_BUFFER, dados, gl.STATIC_DRAW);
    var passo = 8 * 4;
    [[1, 3, 0], [2, 3, 12], [3, 1, 24], [4, 1, 28]].forEach(function (a) {
      gl.enableVertexAttribArray(a[0]);
      gl.vertexAttribPointer(a[0], a[1], gl.FLOAT, false, passo, a[2]);
      gl.vertexAttribDivisor(a[0], 1);
    });
    var N = S.length / 8;

    var uP = {};
    ["uMVP", "uCam", "uTela", "uFina", "uGrossa", "uDist", "uRaioPeca",
     "uTinta", "uAceso", "uGanho", "uPonteiro", "uRaio", "uAtivo", "uProp",
     "uTempo"].forEach(function (n) { uP[n] = gl.getUniformLocation(pp, n); });

    var tinta = [0.62, 0.75, 0.88], aceso = [0.99, 0.77, 0], ganho = 0.95;
    function lerTema() {
      var cs = window.getComputedStyle(raiz);
      tinta = rgb(cs.getPropertyValue("--clp-traco"), [0.62, 0.75, 0.88]);
      aceso = rgb(cs.getPropertyValue("--clp-aceso"), [0.99, 0.77, 0]);
      ganho = parseFloat(cs.getPropertyValue("--clp-ganho")) || 0.95;
    }
    lerTema();

    var reduzido = window.matchMedia("(prefers-reduced-motion: reduce)").matches;
    /* REPOUSO PARCIALMENTE ABERTO, e isso é conserto de LEITURA. Com repouso
       em 0 a porta cobre tudo pela frente e a peça lia como uma caixa fechada
       -- o usuário perguntou "é uma porta?". Em .34 as camadas aparecem desde
       o primeiro quadro e o objeto se explica sozinho; o ponteiro leva a 1. */
    var REPOUSO = 0.34;
    var abertoAlvo = REPOUSO, aberto = REPOUSO;
    var giro = 0.52, giroVel = 0, inclinacao = -0.26, deriva = 1;
    var ativo = 0, alvoAtivo = 0, pontX = -9, pontY = -9;
    var visivel = false, rodando = false, anterior = 0, relogio = 0;
    var arrastando = false, ultimoX = 0, ultimoY = 0;
    var dpr = 1, larg = 1, alt = 1;
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

    var mats = new Float32Array(16 * N_CAM);

    /* CAIXA ENVOLVENTE POR CAMADA, medida da geometria de verdade -- e não uma
       caixa generosa igual para as seis. Com uma caixa única o enquadramento
       superestima e a peça encolhe sem motivo. */
    var cantos = (function () {
      var lim = [];
      for (var k = 0; k < N_CAM; k++) lim.push([1e9, 1e9, 1e9, -1e9, -1e9, -1e9]);
      for (var i = 0; i < S.length; i += 8) {
        var c = lim[S[i + 7] | 0];
        for (var e = 0; e < 2; e++) {
          for (var a = 0; a < 3; a++) {
            var v = S[i + e * 3 + a];
            if (v < c[a]) c[a] = v;
            if (v > c[a + 3]) c[a + 3] = v;
          }
        }
      }
      return lim.map(cantosDaCaixa);
    })();

    /* RAIO DA PEÇA: metade da diagonal do conjunto. Ancora a rampa de
       profundidade na CÂMERA, e não numa distância absoluta. */
    var RAIO = (function () {
      var g = [1e9, 1e9, 1e9, -1e9, -1e9, -1e9];
      for (var k = 0; k < N_CAM; k++) {
        var c = cantos[k];
        for (var j = 0; j < c.length; j++) {
          for (var a = 0; a < 3; a++) {
            g[a] = Math.min(g[a], c[j][a]);
            g[a + 3] = Math.max(g[a + 3], c[j][a]);
          }
        }
      }
      return 0.5 * Math.sqrt((g[3] - g[0]) * (g[3] - g[0]) +
                             (g[4] - g[1]) * (g[4] - g[1]) +
                             (g[5] - g[2]) * (g[5] - g[2]));
    })();

    var MIRA = 0, FOV = 0.72, AR = 0.94;

    function matrizes(f, gravar) {
      var lista = [];
      for (var k = 0; k < N_CAM; k++) {
        var m = transladar(0, 0, AFASTA[k] * f);
        lista.push(m);
        if (gravar) mats.set(m, k * 16);
      }
      return lista;
    }

    /* A DISTÂNCIA É O MÁXIMO ENTRE MONTADO E SEPARADO, não a do instante.
       Medindo só a pose atual, a peça ENCOLHE enquanto explode e cresce
       enquanto remonta -- lê como zoom involuntário, que é exatamente o
       defeito que braco.js pagou com as seis fases do ciclo. */
    var enqGiro = null, enqIncl = null, enqProp = null, dAlvo = 0, dSuave = 0;
    function distancia(prop) {
      if (enqGiro !== null && Math.abs(giro - enqGiro) < 0.05 &&
          Math.abs(inclinacao - enqIncl) < 0.05 && prop === enqProp) return dAlvo;
      enqGiro = giro; enqIncl = inclinacao; enqProp = prop;
      dAlvo = Math.max(
        enquadrarCaixas(cantos, matrizes(0, false), giro, inclinacao, prop, MIRA, FOV, AR),
        enquadrarCaixas(cantos, matrizes(1, false), giro, inclinacao, prop, MIRA, FOV, AR));
      return dAlvo;
    }

    function quadro(agora) {
      rodando = false;
      var dt = anterior ? Math.min((agora - anterior) / 1000, 0.064) : 0.016;
      anterior = agora;
      relogio += dt;

      if (!reduzido) {
        aberto += (abertoAlvo - aberto) * (1 - Math.pow(0.006, dt));
        if (!arrastando) {
          giro += giroVel * dt;
          giroVel *= Math.pow(0.02, dt);
          /* DERIVA DE REPOUSO QUE VAI E VOLTA. De sentido único a peça
             encostaria no limite e ficaria parada lá -- exatamente o que a
             deriva existe para evitar. Mesma decisão da marca 3D, e o limite
             existe pelo mesmo motivo: de perfil um armário vira uma tira
             vertical e para de comunicar. */
          if (Math.abs(giroVel) < 0.02) {
            giro += deriva * 0.055 * dt;
            if (giro > 0.95) deriva = -1;
            if (giro < -0.20) deriva = 1;
          }
        }
        /* subir é rápido (o ponteiro chegou), descer é lento (a peça esfria) */
        ativo += (alvoAtivo - ativo) *
                 (1 - Math.pow(alvoAtivo > ativo ? 0.001 : 0.15, dt));
      } else {
        aberto = abertoAlvo; ativo = alvoAtivo;
      }

      matrizes(aberto, true);
      var prop = larg / Math.max(1, alt);
      var alvoD = distancia(prop);
      dSuave = dSuave ? dSuave + (alvoD - dSuave) * 0.10 : alvoD;

      gl.clearColor(0, 0, 0, 0);
      gl.clear(gl.COLOR_BUFFER_BIT);
      gl.enable(gl.BLEND);
      gl.blendFunc(gl.SRC_ALPHA, gl.ONE_MINUS_SRC_ALPHA);
      gl.useProgram(pp);
      gl.bindVertexArray(vao);

      var d = dSuave;
      var olho = [Math.sin(giro) * Math.cos(inclinacao) * d,
                  MIRA + Math.sin(inclinacao) * d,
                  Math.cos(giro) * Math.cos(inclinacao) * d];
      var proj = perspectiva(FOV, prop, 1, 120);
      gl.uniformMatrix4fv(uP.uMVP, false,
                          mult(proj, olhar(olho, [0, MIRA, 0], [0, 1, 0])));
      gl.uniformMatrix4fv(uP.uCam, false, mats);
      gl.uniform2f(uP.uTela, larg * dpr, alt * dpr);
      gl.uniform1f(uP.uFina, 1.1 * dpr);
      gl.uniform1f(uP.uGrossa, 2.2 * dpr);
      gl.uniform1f(uP.uDist, d);
      gl.uniform1f(uP.uRaioPeca, RAIO);
      gl.uniform3fv(uP.uTinta, tinta);
      gl.uniform3fv(uP.uAceso, aceso);
      gl.uniform1f(uP.uGanho, ganho);
      gl.uniform2f(uP.uPonteiro, pontX, pontY);
      gl.uniform1f(uP.uRaio, 0.30);
      gl.uniform1f(uP.uAtivo, ativo);
      gl.uniform1f(uP.uProp, prop);
      gl.uniform1f(uP.uTempo, relogio);
      gl.drawArraysInstanced(gl.TRIANGLES, 0, 6, N);

      if ((visivel || ativo > 0.01) && !reduzido) acordar();
    }

    function acordar() {
      if (rodando) return;
      rodando = true;
      anterior = 0;
      window.requestAnimationFrame(quadro);
    }

    /* ---------------------------- interação ----------------------------
       O mesmo ponteiro faz as duas coisas: acende a lente onde está e, com o
       botão apertado, orbita. Não há modo -- é a peça que responde. Mesma
       gramática do braço e da marca. */
    function situar(e) {
      var c = canvas.getBoundingClientRect();
      pontX = (e.clientX - c.left) / Math.max(1, c.width);
      /* O ESPELHO DO EIXO Y. `vNdc` sai de NDC, onde +1 é o TOPO; o ponteiro
         do DOM cresce para BAIXO. Sem inverter, a lente aparece espelhada na
         vertical -- ponteiro em cima, dourado embaixo. Custou uma sessão no
         herói em 19/08, e aqui já nasce certo. */
      pontY = 1 - (e.clientY - c.top) / Math.max(1, c.height);
    }

    raiz.addEventListener("pointerenter", function () { alvoAtivo = 1; acordar(); });
    raiz.addEventListener("pointerleave", function () {
      if (arrastando) return;
      alvoAtivo = 0; abertoAlvo = REPOUSO; acordar();
    });
    raiz.addEventListener("pointerdown", function (e) {
      arrastando = true;
      ultimoX = e.clientX; ultimoY = e.clientY;
      situar(e);
      alvoAtivo = 1;
      if (raiz.setPointerCapture) raiz.setPointerCapture(e.pointerId);
      acordar();
      e.preventDefault();
    });
    raiz.addEventListener("pointermove", function (e) {
      situar(e);
      alvoAtivo = 1;
      abertoAlvo = 1;
      if (arrastando) {
        var dx = e.clientX - ultimoX, dy = e.clientY - ultimoY;
        ultimoX = e.clientX; ultimoY = e.clientY;
        giro = Math.max(-1.15, Math.min(1.15, giro - dx * 0.007));
        giroVel = -dx * 0.14;
        /* trava a inclinação: acima o visitante olha a placa por cima e o
           armário deixa de ser um armário; abaixo vê o fundo da caixa */
        inclinacao = Math.max(-0.85, Math.min(0.30, inclinacao + dy * 0.004));
      }
      acordar();
    });
    function soltar(e) {
      if (!arrastando) return;
      arrastando = false;
      if (e && e.pointerId != null && raiz.hasPointerCapture &&
          raiz.hasPointerCapture(e.pointerId)) raiz.releasePointerCapture(e.pointerId);
      /* No toque não há hover: a lente apaga ao soltar, senão ficaria presa. */
      if (window.matchMedia("(hover: none)").matches) {
        alvoAtivo = 0; abertoAlvo = REPOUSO;
      }
      acordar();
    }
    raiz.addEventListener("pointerup", soltar);
    raiz.addEventListener("pointercancel", soltar);

    /* A LISTA TAMBÉM COMANDA. Nenhum gesto novo: é o mesmo `pointerover` que
       o dominó já escuta (main.js §8). Apontar qualquer capacidade separa o
       armário. "Eight disciplines, ONE contractor", performado. */
    var lista = document.querySelector("[data-domino]");
    if (lista) {
      lista.addEventListener("pointerover", function () { abertoAlvo = 1; acordar(); });
      lista.addEventListener("pointerleave", function () { abertoAlvo = REPOUSO; acordar(); });
      lista.addEventListener("focusin", function () { abertoAlvo = 1; acordar(); });
      lista.addEventListener("focusout", function () { abertoAlvo = REPOUSO; acordar(); });
    }

    document.addEventListener("temachange", function () { lerTema(); acordar(); });
    window.addEventListener("resize", function () {
      medir(); enqProp = null; acordar();
    });

    if (window.IntersectionObserver) {
      new IntersectionObserver(function (ent) {
        visivel = ent[0].isIntersecting;
        if (visivel) acordar();
      }, { rootMargin: "120px" }).observe(raiz);
    } else {
      visivel = true;
    }
    medir();
    acordar();
  }

  function iniciar() {
    var els = document.querySelectorAll("[data-clp]");
    for (var i = 0; i < els.length; i++) montar(els[i]);
  }
  if (document.readyState === "loading") {
    document.addEventListener("DOMContentLoaded", iniciar);
  } else {
    iniciar();
  }
})();
