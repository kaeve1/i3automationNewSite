/* ============================================================================
   Planta — gêmeo digital isométrico em WebGL2 escrito à mão
   i3Automations

   Sem Three.js. A geometria não vem de arquivo: é GERADA por código a partir
   de primitivas (caixa, cilindro, torre, arranjo solar, bacia), e desenhada em
   ARESTA, não em face — o que a mantém coerente com o resto do site, onde o
   assunto é sempre o desenho técnico por baixo da fotografia.

   O que existe aqui e por quê:
     · ~60 linhas de matemática de matriz (perspectiva, lookAt, multiplicação);
     · um programa de LINHAS com atenuação por profundidade, para o fundo da
       planta recuar sem precisar de névoa nem de luz;
     · um programa de PONTOS para a telemetria que corre pelos enlaces — é o
       dado saindo do campo para a supervisão, que é literalmente o que a
       empresa vende;
     · órbita por arrasto, com inércia, e rotação lenta enquanto ninguém toca.

   Custo total: este arquivo. Nenhuma dependência de terceiros (design.md §9).
   ============================================================================ */
(function () {
  "use strict";

  var reduzido = window.matchMedia("(prefers-reduced-motion: reduce)").matches;

  /* ================================ matriz ================================ */
  function identidade() {
    return new Float32Array([1, 0, 0, 0, 0, 1, 0, 0, 0, 0, 1, 0, 0, 0, 0, 1]);
  }

  function multiplicar(a, b) {
    var o = new Float32Array(16);
    for (var i = 0; i < 4; i++) {
      for (var j = 0; j < 4; j++) {
        var s = 0;
        for (var k = 0; k < 4; k++) s += a[k * 4 + j] * b[i * 4 + k];
        o[i * 4 + j] = s;
      }
    }
    return o;
  }

  function perspectiva(fov, prop, perto, longe) {
    var f = 1 / Math.tan(fov / 2), nf = 1 / (perto - longe);
    var o = new Float32Array(16);
    o[0] = f / prop; o[5] = f; o[10] = (longe + perto) * nf;
    o[11] = -1; o[14] = 2 * longe * perto * nf;
    return o;
  }

  function normalizar(v) {
    var m = Math.hypot(v[0], v[1], v[2]) || 1;
    return [v[0] / m, v[1] / m, v[2] / m];
  }
  function cruzar(a, b) {
    return [a[1] * b[2] - a[2] * b[1], a[2] * b[0] - a[0] * b[2], a[0] * b[1] - a[1] * b[0]];
  }

  function olhar(olho, alvo, cima) {
    var z = normalizar([olho[0] - alvo[0], olho[1] - alvo[1], olho[2] - alvo[2]]);
    var x = normalizar(cruzar(cima, z));
    var y = cruzar(z, x);
    return new Float32Array([
      x[0], y[0], z[0], 0,
      x[1], y[1], z[1], 0,
      x[2], y[2], z[2], 0,
      -(x[0] * olho[0] + x[1] * olho[1] + x[2] * olho[2]),
      -(y[0] * olho[0] + y[1] * olho[1] + y[2] * olho[2]),
      -(z[0] * olho[0] + z[1] * olho[1] + z[2] * olho[2]), 1
    ]);
  }

  /* ============================== geometria ==============================
     Cada função empurra pares de vértices em `L` (lista de linhas) e devolve
     nada — a lista é a única estrutura. `p` é a "prioridade" da aresta: 1 é
     contorno estrutural, .45 é detalhe. O shader usa isso como peso de linha
     falso (não há lineWidth confiável em WebGL) modulando a opacidade.
     ============================================================================ */
  function aresta(L, a, b, p) {
    L.push(a[0], a[1], a[2], p, b[0], b[1], b[2], p);
  }

  function caixa(L, x, y, z, w, h, d, p) {
    var x0 = x - w / 2, x1 = x + w / 2, z0 = z - d / 2, z1 = z + d / 2, y1 = y + h;
    var b = [[x0, y, z0], [x1, y, z0], [x1, y, z1], [x0, y, z1]];
    var t = [[x0, y1, z0], [x1, y1, z0], [x1, y1, z1], [x0, y1, z1]];
    for (var i = 0; i < 4; i++) {
      aresta(L, b[i], b[(i + 1) % 4], p);
      aresta(L, t[i], t[(i + 1) % 4], p);
      aresta(L, b[i], t[i], p);
    }
  }

  function cilindro(L, x, y, z, r, h, seg, p) {
    var i, a0, a1, ant = null;
    for (i = 0; i <= seg; i++) {
      var a = (i / seg) * Math.PI * 2;
      var px = x + Math.cos(a) * r, pz = z + Math.sin(a) * r;
      if (ant) {
        aresta(L, [ant[0], y, ant[1]], [px, y, pz], p);
        aresta(L, [ant[0], y + h, ant[1]], [px, y + h, pz], p);
      }
      if (i % Math.max(1, Math.round(seg / 8)) === 0) {
        aresta(L, [px, y, pz], [px, y + h, pz], p * 0.6);
      }
      ant = [px, pz];
    }
    /* cinta de inspeção a 2/3 da altura: detalhe que denuncia escala */
    ant = null;
    for (i = 0; i <= seg; i++) {
      a0 = (i / seg) * Math.PI * 2;
      var qx = x + Math.cos(a0) * r * 1.03, qz = z + Math.sin(a0) * r * 1.03;
      if (ant) aresta(L, [ant[0], y + h * 0.66, ant[1]], [qx, y + h * 0.66, qz], p * 0.45);
      ant = [qx, qz];
    }
  }

  function torre(L, x, y, z, base, topo, h, andares, p) {
    for (var i = 0; i < andares; i++) {
      var t0 = i / andares, t1 = (i + 1) / andares;
      var r0 = base + (topo - base) * t0, r1 = base + (topo - base) * t1;
      var y0 = y + h * t0, y1 = y + h * t1;
      var c0 = [[-r0, -r0], [r0, -r0], [r0, r0], [-r0, r0]];
      var c1 = [[-r1, -r1], [r1, -r1], [r1, r1], [-r1, r1]];
      for (var k = 0; k < 4; k++) {
        var n = (k + 1) % 4;
        aresta(L, [x + c0[k][0], y0, z + c0[k][1]], [x + c0[n][0], y0, z + c0[n][1]], p);
        aresta(L, [x + c0[k][0], y0, z + c0[k][1]], [x + c1[k][0], y1, z + c1[k][1]], p);
        /* diagonal de contraventamento — é o que faz ler como estrutura */
        aresta(L, [x + c0[k][0], y0, z + c0[k][1]], [x + c1[n][0], y1, z + c1[n][1]], p * 0.4);
      }
    }
    var rt = topo;
    var ct = [[-rt, -rt], [rt, -rt], [rt, rt], [-rt, rt]];
    for (var j = 0; j < 4; j++) {
      aresta(L, [x + ct[j][0], y + h, z + ct[j][1]],
                [x + ct[(j + 1) % 4][0], y + h, z + ct[(j + 1) % 4][1]], p);
    }
  }

  function solar(L, x, y, z, fileiras, colunas, p) {
    var pw = 1.5, pd = 0.9, gap = 0.55, incl = 0.42;
    for (var i = 0; i < fileiras; i++) {
      for (var j = 0; j < colunas; j++) {
        var cx = x + j * (pw + 0.25) - (colunas - 1) * (pw + 0.25) / 2;
        var cz = z + i * (pd + gap) - (fileiras - 1) * (pd + gap) / 2;
        var dy = Math.sin(incl) * pd, dz = Math.cos(incl) * pd;
        var a = [cx - pw / 2, y + 0.18, cz - dz / 2];
        var b = [cx + pw / 2, y + 0.18, cz - dz / 2];
        var c = [cx + pw / 2, y + 0.18 + dy, cz + dz / 2];
        var d = [cx - pw / 2, y + 0.18 + dy, cz + dz / 2];
        aresta(L, a, b, p); aresta(L, b, c, p); aresta(L, c, d, p); aresta(L, d, a, p);
        aresta(L, [a[0], y, a[2]], a, p * 0.5);
        aresta(L, [b[0], y, b[2]], b, p * 0.5);
      }
    }
  }

  function bacia(L, x, y, z, w, d, p) {
    caixa(L, x, y - 0.35, z, w, 0.35, d, p);
    /* defletores: as paredes internas do decantador */
    for (var i = 1; i < 4; i++) {
      var zz = z - d / 2 + (d * i) / 4;
      aresta(L, [x - w / 2, y, zz], [x + w / 2, y, zz], p * 0.45);
    }
  }

  /* ============================ a planta ============================
     Os nós são os setores que a empresa declara atender. A supervisão fica no
     centro e todo enlace nasce nela: é a topologia real de um SCADA, não uma
     composição decorativa. */
  var NOS = [
    { id: "scada",  rotulo: "Control room · SCADA",   x: 0,    z: 0 },
    { id: "oleo",   rotulo: "Oil & Gas · Houston",    x: -9,   z: -4.5 },
    { id: "agua",   rotulo: "Water & wastewater",     x: 8.5,  z: -5 },
    { id: "auto",   rotulo: "Automotive body shop",   x: -8,   z: 5.5 },
    { id: "papel",  rotulo: "Paper mill",             x: 2,    z: -8.5 },
    { id: "solar",  rotulo: "Solar & renewables",     x: 9,    z: 5 },
    { id: "mcc",    rotulo: "Motor control center",   x: -1.5, z: 8 }
  ];

  function construir() {
    var L = [];
    var no = {};
    NOS.forEach(function (n) { no[n.id] = n; });

    /* chão: grade de referência, leve */
    var R = 13, passo = 2.5;
    for (var g = -R; g <= R; g += passo) {
      aresta(L, [-R, 0, g], [R, 0, g], 0.13);
      aresta(L, [g, 0, -R], [g, 0, R], 0.13);
    }

    /* supervisão: o prédio central, o único com massa */
    caixa(L, 0, 0, 0, 3.4, 2.2, 3.4, 1);
    caixa(L, 0, 2.2, 0, 2.4, 0.5, 2.4, 0.8);
    caixa(L, 0, 2.7, 0, 0.24, 1.9, 0.24, 0.7);
    aresta(L, [0, 4.6, 0], [0, 5.2, 0], 0.5);

    /* Oil & Gas: torre de destilação + dois tanques */
    torre(L, no.oleo.x, 0, no.oleo.z, 0.85, 0.5, 5.2, 5, 0.95);
    cilindro(L, no.oleo.x - 2.6, 0, no.oleo.z + 1.6, 1.15, 1.5, 18, 0.85);
    cilindro(L, no.oleo.x + 2.3, 0, no.oleo.z + 2.1, 0.9, 1.2, 16, 0.85);

    /* Água: bacias de decantação + casa de bombas */
    bacia(L, no.agua.x, 0.35, no.agua.z, 5.2, 3.2, 0.9);
    caixa(L, no.agua.x + 3.6, 0, no.agua.z - 1.4, 1.6, 1.3, 1.6, 0.85);
    cilindro(L, no.agua.x - 3.2, 0, no.agua.z + 1.2, 0.8, 1.9, 16, 0.8);

    /* Automotivo: galpão longo com pórticos */
    caixa(L, no.auto.x, 0, no.auto.z, 6.4, 2.4, 3.6, 0.95);
    for (var i = -2; i <= 2; i++) {
      aresta(L, [no.auto.x + i * 1.3, 2.4, no.auto.z - 1.8],
                [no.auto.x + i * 1.3, 3.1, no.auto.z], 0.45);
      aresta(L, [no.auto.x + i * 1.3, 3.1, no.auto.z],
                [no.auto.x + i * 1.3, 2.4, no.auto.z + 1.8], 0.45);
    }

    /* Papel: máquina longa + rolo */
    caixa(L, no.papel.x, 0, no.papel.z, 7.2, 1.6, 2.2, 0.9);
    cilindro(L, no.papel.x + 4.4, 0, no.papel.z, 1.1, 1.1, 16, 0.8);

    /* Solar: arranjo fotovoltaico + inversor */
    solar(L, no.solar.x, 0, no.solar.z, 3, 4, 0.75);
    caixa(L, no.solar.x + 4.4, 0, no.solar.z, 0.9, 1.4, 0.7, 0.8);

    /* MCC: fileira de painéis — o produto da casa */
    for (var c = 0; c < 6; c++) {
      caixa(L, no.mcc.x + c * 0.95 - 2.4, 0, no.mcc.z, 0.9, 2.0, 1.0, 0.85);
    }

    /* enlaces: nascem na supervisão e vão a cada ativo, com um cotovelo em
       ângulo reto — roteamento de eletrocalha, não linha reta de gráfico */
    var enlaces = [];
    NOS.slice(1).forEach(function (n) {
      var meio = [n.x * 0.55, 0.06, 0];
      var pts = [[0, 0.06, 0], meio, [n.x * 0.55, 0.06, n.z], [n.x, 0.06, n.z]];
      for (var k = 0; k < pts.length - 1; k++) aresta(L, pts[k], pts[k + 1], 0.55);
      enlaces.push(pts);
      /* haste do rótulo: sobe do ativo até onde o texto vai flutuar */
      aresta(L, [n.x, 0, n.z], [n.x, 5.6, n.z], 0.22);
    });

    return { linhas: new Float32Array(L), enlaces: enlaces };
  }

  /* ============================== shaders ============================== */
  var VS_LINHA = [
    "#version 300 es",
    "in vec3 pos;",
    "in float peso;",
    "uniform mat4 uMVP;",
    "out float vPeso;",
    "out float vProfundidade;",
    "out vec2  vTela;",
    "void main() {",
    "  vec4 p = uMVP * vec4(pos, 1.0);",
    "  gl_Position = p;",
    /* posição em espaço de tela, 0..1 — é onde a lente do ponteiro vive */
    "  vTela = p.xy / p.w * 0.5 + 0.5;",
    /* atenuação por profundidade: o fundo da planta recua sem névoa nem luz */
    "  vProfundidade = clamp(1.0 - (p.w - 26.0) / 62.0, 0.42, 1.0);",
    "  vPeso = peso;",
    "}"
  ].join("\n");

  var FS_LINHA = [
    "#version 300 es",
    /* highp e não mediump: o fBm da borda da lente banda visivelmente em
       mediump, e o degradê fica em degraus em vez de dissolver. */
    "precision highp float;",
    "in float vPeso;",
    "in float vProfundidade;",
    "in vec2  vTela;",
    "uniform vec3 uCor;",
    "uniform vec3 uAceso;",
    "uniform vec2 uPonteiro;",
    "uniform float uRaio;",
    "uniform float uAtivo;",
    "uniform float uTempo;",
    "uniform float uEntrada;",
    "uniform float uProp;",
    "out vec4 cor;",

    /* Mesmo ruído da lente do herói (js/braco.js e js/lente.js): as três
       revelações do site têm de ter a MESMA aresta, senão o visitante encontra
       três instrumentos diferentes em vez de um. */
    "float hash(vec2 p) {",
    "  return fract(sin(dot(p, vec2(127.1, 311.7))) * 43758.5453123);",
    "}",
    "float ruido(vec2 p) {",
    "  vec2 i = floor(p), f = fract(p);",
    "  vec2 u = f * f * (3.0 - 2.0 * f);",
    "  return mix(mix(hash(i), hash(i + vec2(1.0, 0.0)), u.x),",
    "             mix(hash(i + vec2(0.0, 1.0)), hash(i + vec2(1.0, 1.0)), u.x), u.y);",
    "}",
    "float fbm(vec2 p) {",
    "  float v = 0.0, a = 0.5;",
    "  for (int i = 0; i < 4; i++) { v += a * ruido(p); p *= 2.03; a *= 0.5; }",
    "  return v;",
    "}",
    "void main() {",
    // O 1.35 e o ganho de linha: com peso x profundidade cru o desenho saia
    // em ~0,45 de alfa e mal se lia sobre o papel. O clamp segura o estouro.
    /* A LENTE: sob o ponteiro o desenho acende, como no herói. A cor acesa NÃO
       é o dourado puro — a planta vive sobre papel claro, e ali #FDC500 dá
       1,46:1 e sumiria. O uniform recebe `--accent-txt`, que é #6B5000 no tema
       claro (6,92:1) e #FDC500 no escuro (11,66:1). */
    "  float d = length((vTela - uPonteiro) * vec2(uProp, 1.0)) / max(uRaio, 1e-4);",
    "  float n = (fbm(vTela * 9.0 + uTempo * 0.05) - 0.5) * 0.17;",
    "  float rev = (1.0 - smoothstep(0.80, 1.04, d + n)) * uAtivo;",
    "  float a = vPeso * vProfundidade * uEntrada * 1.35 * (1.0 + rev * 0.55);",
    "  vec3 c = mix(uCor, uAceso, rev);",
    /* a banda dourada no limite, pelo QUADRADO: pow(x, y) é indefinido para
       x < 0 em GLSL, e dentro da lente o argumento é negativo o tempo todo */
    "  float t = (d + n - 0.94) * 20.0;",
    "  float banda = exp(-t * t) * uAtivo * uEntrada;",
    "  c = mix(c, uAceso, clamp(banda * 0.85, 0.0, 1.0));",
    "  a = max(a, banda * vPeso * 0.75);",
    "  cor = vec4(c, clamp(a, 0.0, 1.0));",
    "}"
  ].join("\n");

  var VS_PULSO = [
    "#version 300 es",
    "in vec3 pos;",
    "in float vida;",
    "uniform mat4 uMVP;",
    "uniform float uDpr;",
    "out float vVida;",
    "void main() {",
    "  vec4 p = uMVP * vec4(pos, 1.0);",
    "  gl_Position = p;",
    "  gl_PointSize = (4.5 + 3.0 * vida) * uDpr;",
    "  vVida = vida;",
    "}"
  ].join("\n");

  var FS_PULSO = [
    "#version 300 es",
    "precision mediump float;",
    "in float vVida;",
    "uniform vec3 uCor;",
    "uniform float uEntrada;",
    "out vec4 cor;",
    "void main() {",
    "  float d = length(gl_PointCoord - 0.5);",
    "  float a = (1.0 - smoothstep(0.28, 0.5, d)) * vVida * uEntrada;",
    "  cor = vec4(uCor, a);",
    "}"
  ].join("\n");

  function compilar(gl, tipo, fonte) {
    var s = gl.createShader(tipo);
    gl.shaderSource(s, fonte); gl.compileShader(s);
    if (!gl.getShaderParameter(s, gl.COMPILE_STATUS)) {
      console.warn("[planta] shader:", gl.getShaderInfoLog(s));
      return null;
    }
    return s;
  }

  function programa(gl, vs, fs) {
    var v = compilar(gl, gl.VERTEX_SHADER, vs);
    var f = compilar(gl, gl.FRAGMENT_SHADER, fs);
    if (!v || !f) return null;
    var p = gl.createProgram();
    gl.attachShader(p, v); gl.attachShader(p, f); gl.linkProgram(p);
    if (!gl.getProgramParameter(p, gl.LINK_STATUS)) {
      console.warn("[planta] link:", gl.getProgramInfoLog(p));
      return null;
    }
    return p;
  }

  /* Ver a nota longa em lente.js: custom property devolve o hexadecimal
     literal, e ler isso com /[\d.]+/ captura o token inteiro como um numero so. */
  function rgb(css) {
    css = (css || "").trim();
    if (css.charAt(0) === "#") {
      var h = css.slice(1);
      if (h.length === 3) h = h[0] + h[0] + h[1] + h[1] + h[2] + h[2];
      if (h.length >= 6) {
        return [parseInt(h.substr(0, 2), 16) / 255,
                parseInt(h.substr(2, 2), 16) / 255,
                parseInt(h.substr(4, 2), 16) / 255];
      }
    }
    var m = css.match(/-?[\d.]+/g);
    if (m && m.length >= 3) return [+m[0] / 255, +m[1] / 255, +m[2] / 255];
    return [0, 0.21, 0.4];
  }

  /* =============================== montagem =============================== */
  function montar(raiz) {
    var canvas = raiz.querySelector(".planta__tela");
    if (!canvas || !window.WebGL2RenderingContext) {
      raiz.classList.add("is-indisponivel");
      return;
    }
    var gl = canvas.getContext("webgl2", {
      alpha: true, premultipliedAlpha: false, antialias: true,
      depth: true, powerPreference: "low-power"
    });
    if (!gl) { raiz.classList.add("is-indisponivel"); return; }

    var pl = programa(gl, VS_LINHA, FS_LINHA);
    var pp = programa(gl, VS_PULSO, FS_PULSO);
    if (!pl || !pp) { raiz.classList.add("is-indisponivel"); return; }

    var cena = construir();

    var vaoL = gl.createVertexArray();
    gl.bindVertexArray(vaoL);
    var bufL = gl.createBuffer();
    gl.bindBuffer(gl.ARRAY_BUFFER, bufL);
    gl.bufferData(gl.ARRAY_BUFFER, cena.linhas, gl.STATIC_DRAW);
    var aPos = gl.getAttribLocation(pl, "pos");
    var aPeso = gl.getAttribLocation(pl, "peso");
    gl.enableVertexAttribArray(aPos);
    gl.vertexAttribPointer(aPos, 3, gl.FLOAT, false, 16, 0);
    gl.enableVertexAttribArray(aPeso);
    gl.vertexAttribPointer(aPeso, 1, gl.FLOAT, false, 16, 12);
    var nLinhas = cena.linhas.length / 4;

    /* pulsos: 3 por enlace, posição recalculada por quadro na CPU. São
       poucas dezenas de vértices — não vale um transform feedback. */
    var POR_ENLACE = 3;
    var nPulsos = cena.enlaces.length * POR_ENLACE;
    var dadosPulso = new Float32Array(nPulsos * 4);
    var vaoP = gl.createVertexArray();
    gl.bindVertexArray(vaoP);
    var bufP = gl.createBuffer();
    gl.bindBuffer(gl.ARRAY_BUFFER, bufP);
    gl.bufferData(gl.ARRAY_BUFFER, dadosPulso, gl.DYNAMIC_DRAW);
    var pPos = gl.getAttribLocation(pp, "pos");
    var pVida = gl.getAttribLocation(pp, "vida");
    gl.enableVertexAttribArray(pPos);
    gl.vertexAttribPointer(pPos, 3, gl.FLOAT, false, 16, 0);
    gl.enableVertexAttribArray(pVida);
    gl.vertexAttribPointer(pVida, 1, gl.FLOAT, false, 16, 12);

    /* comprimento acumulado de cada enlace, para o pulso andar em velocidade
       constante em vez de acelerar nos trechos curtos */
    var trilhas = cena.enlaces.map(function (pts) {
      var segs = [], total = 0;
      for (var i = 0; i < pts.length - 1; i++) {
        var a = pts[i], b = pts[i + 1];
        var c = Math.hypot(b[0] - a[0], b[1] - a[1], b[2] - a[2]);
        segs.push({ a: a, b: b, c: c, i0: total });
        total += c;
      }
      return { segs: segs, total: total };
    });

    gl.enable(gl.BLEND);
    gl.blendFuncSeparate(gl.SRC_ALPHA, gl.ONE_MINUS_SRC_ALPHA, gl.ONE, gl.ONE_MINUS_SRC_ALPHA);
    gl.clearColor(0, 0, 0, 0);

    var uL = {
      mvp: gl.getUniformLocation(pl, "uMVP"),
      cor: gl.getUniformLocation(pl, "uCor"),
      aceso: gl.getUniformLocation(pl, "uAceso"),
      ponteiro: gl.getUniformLocation(pl, "uPonteiro"),
      raio: gl.getUniformLocation(pl, "uRaio"),
      ativo: gl.getUniformLocation(pl, "uAtivo"),
      prop: gl.getUniformLocation(pl, "uProp"),
      tempo: gl.getUniformLocation(pl, "uTempo"),
      entrada: gl.getUniformLocation(pl, "uEntrada")
    };
    var uP = {
      mvp: gl.getUniformLocation(pp, "uMVP"),
      cor: gl.getUniformLocation(pp, "uCor"),
      dpr: gl.getUniformLocation(pp, "uDpr"),
      entrada: gl.getUniformLocation(pp, "uEntrada")
    };

    /* ---------------------------- estado ---------------------------- */
    var giro = -0.62, giroVel = 0, inclinacao = 0.72;
    var arrastando = false, ultimoX = 0, ultimoY = 0;
    var entrada = 0, dpr = 1, larg = 1, alt = 1;
    var corLinha, corPulso, corAceso;
    var pontX = 0.5, pontY = 0.5, ativo = 0, alvoAtivo = 0, relogio = 0;
    var visivel = false, rodando = false, anterior = 0;

    function lerTema() {
      var cs = getComputedStyle(raiz);
      corLinha = rgb(cs.getPropertyValue("--traco"));
      corPulso = rgb(cs.getPropertyValue("--dourado") || "#FDC500");
      /* `--accent-txt`, não `--dourado`: a planta vive sobre papel claro, e o
         dourado puro daria 1,46:1 ali. O token já vira #6B5000 no tema claro
         e #FDC500 no escuro, que é exatamente a troca que a lente precisa. */
      corAceso = rgb(cs.getPropertyValue("--accent-txt") || "#6B5000");
    }

    /* Mesma trava de js/braco.js, e pelo mesmo motivo: esta funcao LE o
       retangulo e ESCREVE os atributos do canvas, que sao o tamanho
       intrinseco dele. Hoje a .planta tem `aspect-ratio`, entao a altura e
       definida e o ciclo nao fecha — a trava existe para o dia em que nao
       for. Ver a nota longa em braco.js. */
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

    function mvp() {
      /* distância pela largura: numa janela estreita a planta recua sozinha
         em vez de sair pelas bordas */
      // Medido a 30: a torre de destilacao e a fileira de MCC saiam pelas
      // bordas da moldura. A cena tem 30 unidades de vao e o campo horizontal
      // e ~60 graus, entao 42 deixa uma margem de respiro em vez de corte.
      var d = 42 + Math.max(0, (900 - larg) / 900) * 14;
      var olho = [
        Math.sin(giro) * Math.cos(inclinacao) * d,
        Math.sin(inclinacao) * d,
        Math.cos(giro) * Math.cos(inclinacao) * d
      ];
      var proj = perspectiva(0.62, larg / alt, 1, 120);
      return multiplicar(proj, olhar(olho, [0, 1.6, 0], [0, 1, 0]));
    }

    function atualizarPulsos(t) {
      var k = 0;
      for (var e = 0; e < trilhas.length; e++) {
        var tr = trilhas[e];
        for (var j = 0; j < POR_ENLACE; j++) {
          var fase = (t * 0.17 + j / POR_ENLACE + e * 0.31) % 1;
          var s = fase * tr.total;
          var seg = tr.segs[tr.segs.length - 1];
          for (var i = 0; i < tr.segs.length; i++) {
            if (s <= tr.segs[i].i0 + tr.segs[i].c) { seg = tr.segs[i]; break; }
          }
          var u = seg.c > 0 ? (s - seg.i0) / seg.c : 0;
          u = Math.max(0, Math.min(1, u));
          dadosPulso[k * 4] = seg.a[0] + (seg.b[0] - seg.a[0]) * u;
          dadosPulso[k * 4 + 1] = seg.a[1] + (seg.b[1] - seg.a[1]) * u + 0.05;
          dadosPulso[k * 4 + 2] = seg.a[2] + (seg.b[2] - seg.a[2]) * u;
          /* acende no meio do percurso e apaga nas pontas: o dado chega, não
             pisca eternamente no mesmo lugar */
          dadosPulso[k * 4 + 3] = Math.sin(fase * Math.PI);
          k++;
        }
      }
      gl.bindBuffer(gl.ARRAY_BUFFER, bufP);
      gl.bufferSubData(gl.ARRAY_BUFFER, 0, dadosPulso);
    }

    function quadro(agora) {
      var dt = Math.min((agora - anterior) / 1000, 0.05);
      anterior = agora;
      relogio += dt;
      /* sobe rápido (o ponteiro chegou), desce devagar (o desenho esfria) */
      ativo += (alvoAtivo - ativo) *
               (1 - Math.pow(alvoAtivo > ativo ? 0.002 : 0.06, dt));

      if (!arrastando) {
        giro += giroVel * dt;
        giroVel *= Math.pow(0.02, dt);
        if (Math.abs(giroVel) < 0.02 && !reduzido) giro += 0.045 * dt;
      }
      entrada += ((visivel ? 1 : 0) - entrada) * (1 - Math.pow(0.02, dt));

      medir();
      var m = mvp();
      gl.clear(gl.COLOR_BUFFER_BIT | gl.DEPTH_BUFFER_BIT);

      gl.useProgram(pl);
      gl.bindVertexArray(vaoL);
      gl.uniformMatrix4fv(uL.mvp, false, m);
      gl.uniform3fv(uL.cor, corLinha);
      gl.uniform3fv(uL.aceso, corAceso);
      gl.uniform2f(uL.ponteiro, pontX, pontY);
      gl.uniform1f(uL.raio, 0.30);
      gl.uniform1f(uL.ativo, ativo);
      gl.uniform1f(uL.prop, larg / alt);
      gl.uniform1f(uL.tempo, relogio);
      gl.uniform1f(uL.entrada, entrada);
      gl.drawArrays(gl.LINES, 0, nLinhas);

      if (!reduzido) {
        atualizarPulsos(agora / 1000);
        gl.useProgram(pp);
        gl.bindVertexArray(vaoP);
        gl.uniformMatrix4fv(uP.mvp, false, m);
        gl.uniform3fv(uP.cor, corPulso);
        gl.uniform1f(uP.dpr, dpr);
        gl.uniform1f(uP.entrada, entrada);
        gl.drawArrays(gl.POINTS, 0, nPulsos);
      }

      if (visivel || entrada > 0.01) window.requestAnimationFrame(quadro);
      else rodando = false;
    }

    function acordar() {
      if (rodando) return;
      rodando = true; anterior = performance.now();
      window.requestAnimationFrame(quadro);
    }

    /* ---------------------------- interação ----------------------------
       O Y é INVERTIDO: `vTela` sai de NDC, onde +1 é o topo, enquanto clientY
       cresce para baixo. Sem o espelho a lente aparece invertida na vertical —
       ponteiro em cima, aceso embaixo. Foi exatamente o bug do herói. */
    function situar(e) {
      var c = raiz.getBoundingClientRect();
      pontX = (e.clientX - c.left) / Math.max(1, c.width);
      pontY = 1 - (e.clientY - c.top) / Math.max(1, c.height);
    }

    raiz.addEventListener("pointerenter", function () { alvoAtivo = 1; acordar(); });
    raiz.addEventListener("pointerleave", function () {
      if (arrastando) return;
      alvoAtivo = 0; acordar();
    });

    raiz.addEventListener("pointerdown", function (e) {
      arrastando = true; ultimoX = e.clientX; ultimoY = e.clientY;
      raiz.classList.add("is-tocada");
      situar(e);
      alvoAtivo = 1;
      raiz.setPointerCapture(e.pointerId);
      acordar();
    });
    raiz.addEventListener("pointermove", function (e) {
      situar(e);
      alvoAtivo = 1;
      if (!arrastando) { acordar(); return; }
      var dx = e.clientX - ultimoX, dy = e.clientY - ultimoY;
      ultimoX = e.clientX; ultimoY = e.clientY;
      giro -= dx * 0.006;
      giroVel = -dx * 0.12;
      /* trava a inclinação: abaixo de .18 rad a planta vira uma linha e
         acima de 1.15 o visitante olha o chão */
      inclinacao = Math.max(0.18, Math.min(1.15, inclinacao + dy * 0.004));
      acordar();
    });
    function soltar(e) {
      if (!arrastando) return;
      arrastando = false;
      if (e && e.pointerId != null && raiz.hasPointerCapture &&
          raiz.hasPointerCapture(e.pointerId)) raiz.releasePointerCapture(e.pointerId);
    }
    raiz.addEventListener("pointerup", soltar);
    raiz.addEventListener("pointercancel", soltar);

    /* Teclado: a planta é conteúdo, e conteúdo se navega sem mouse. */
    raiz.setAttribute("tabindex", "0");
    raiz.addEventListener("keydown", function (e) {
      var passo = 0.16;
      if (e.key === "ArrowLeft") giro -= passo;
      else if (e.key === "ArrowRight") giro += passo;
      else if (e.key === "ArrowUp") inclinacao = Math.min(1.15, inclinacao + 0.08);
      else if (e.key === "ArrowDown") inclinacao = Math.max(0.18, inclinacao - 0.08);
      else return;
      e.preventDefault();
      raiz.classList.add("is-tocada");
      pontX = 0.5; pontY = 0.5; alvoAtivo = 1;
      acordar();
    });

    lerTema();
    medir();
    var mm = window.matchMedia("(prefers-color-scheme: dark)");
    if (mm.addEventListener) mm.addEventListener("change", function () { lerTema(); acordar(); });
    document.addEventListener("temachange", function () { lerTema(); acordar(); });
    window.addEventListener("resize", function () { medir(); acordar(); });

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
    var els = document.querySelectorAll("[data-planta]");
    for (var i = 0; i < els.length; i++) montar(els[i]);
  }

  if (document.readyState === "loading") {
    document.addEventListener("DOMContentLoaded", iniciar);
  } else {
    iniciar();
  }
})();
