/* ============================================================================
   gl.js — o núcleo comum dos desenhos em WebGL2
   i3Automations

   POR QUE ESTE ARQUIVO EXISTE.
   Três componentes do site desenham em aresta com WebGL2 escrito à mão:
   `planta.js` (a instalação isométrica), `braco.js` (o robô de 6 eixos do
   herói) e `marca.js` (a marca i3 extrudada, no cabeçalho de who-we-are).
   Os três precisam exatamente da mesma base: multiplicação de matriz,
   perspectiva, lookAt, o parser hexadecimal de token e a compilação de shader.

   Quando o terceiro chegou, a escolha era duplicar essa base ou extraí-la.
   Este projeto já pagou por duplicar: a cópia de `pose()` em
   ferramentas/previa_braco.js divergiu da original em meia hora — a amplitude
   da cintura mudou no site e não na cópia, e a prévia passou a medir um site
   que não existia. Uma matriz que diverge não avisa: ela devolve um desenho
   plausível e errado.

   O QUE ENTRA AQUI e o que não entra. Entra só o que é genuinamente comum e
   PURO — função que depende apenas dos argumentos. Não entra nada que precise
   conhecer o assunto do desenho: a cinemática do braço, a geometria da planta
   e o perfil da marca ficam cada um no seu arquivo. `enquadrarCaixas()` é o
   caso limite e entrou porque a conta é geométrica, não de assunto: os três
   têm caixas envolventes e os três precisam saber de quanto a câmera recua.

   COMO É CONSUMIDO. Um objeto global, `window.I3GL`. Sem módulos ES: o site é
   HTML estático servido de qualquer lugar, inclusive de `file://`, e `import`
   exige CORS. Cada consumidor faz o alias local no topo da própria IIFE, então
   os call sites continuam lendo `mult(a, b)` e não `I3GL.mult(a, b)`.

   ORDEM DE CARGA. Este arquivo tem de vir ANTES dos consumidores. Todos usam
   `defer`, e scripts com `defer` executam na ORDEM DO DOCUMENTO — então basta
   a tag de gl.js aparecer primeiro no HTML, o que build_paginas.py garante.
   ============================================================================ */
(function () {
  "use strict";

  var TAU = Math.PI * 2;

  /* ================================ matriz ================================
     Convenção COLUNA-MAIOR, a mesma de todo o projeto e a mesma que
     `gl.uniformMatrix4fv(..., false, m)` espera. `mult(a, b)` devolve a·b. */
  function mult(a, b) {
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

  function identidade() {
    return new Float32Array([1, 0, 0, 0, 0, 1, 0, 0, 0, 0, 1, 0, 0, 0, 0, 1]);
  }
  function transladar(x, y, z) {
    return new Float32Array([1, 0, 0, 0, 0, 1, 0, 0, 0, 0, 1, 0, x, y, z, 1]);
  }
  function giroY(a) {
    var c = Math.cos(a), s = Math.sin(a);
    return new Float32Array([c, 0, -s, 0, 0, 1, 0, 0, s, 0, c, 0, 0, 0, 0, 1]);
  }
  function giroZ(a) {
    var c = Math.cos(a), s = Math.sin(a);
    return new Float32Array([c, s, 0, 0, -s, c, 0, 0, 0, 0, 1, 0, 0, 0, 0, 1]);
  }

  function perspectiva(fov, prop, perto, longe) {
    var f = 1 / Math.tan(fov / 2), nf = 1 / (perto - longe);
    var o = new Float32Array(16);
    o[0] = f / prop; o[5] = f; o[10] = (longe + perto) * nf;
    o[11] = -1; o[14] = 2 * longe * perto * nf;
    return o;
  }

  function normal(v) {
    var m = Math.hypot(v[0], v[1], v[2]) || 1;
    return [v[0] / m, v[1] / m, v[2] / m];
  }
  function cruz(a, b) {
    return [a[1] * b[2] - a[2] * b[1], a[2] * b[0] - a[0] * b[2],
            a[0] * b[1] - a[1] * b[0]];
  }
  function olhar(olho, alvo, cima) {
    var z = normal([olho[0] - alvo[0], olho[1] - alvo[1], olho[2] - alvo[2]]);
    var x = normal(cruz(cima, z));
    var y = cruz(z, x);
    return new Float32Array([
      x[0], y[0], z[0], 0,
      x[1], y[1], z[1], 0,
      x[2], y[2], z[2], 0,
      -(x[0] * olho[0] + x[1] * olho[1] + x[2] * olho[2]),
      -(y[0] * olho[0] + y[1] * olho[1] + y[2] * olho[2]),
      -(z[0] * olho[0] + z[1] * olho[1] + z[2] * olho[2]), 1
    ]);
  }

  /* =========================== enquadramento ===========================
     De quanto a câmera precisa recuar para que TODA a peça caiba no tronco.

     Um ponto a `z` de profundidade e `x` de afastamento lateral só cabe se
     `d >= z + |x| / tan(meio campo)`; a resposta é o maior valor entre todos
     os cantos e os dois eixos. `cantos[e]` são os 8 cantos da caixa do elo
     `e`, em espaço LOCAL, e `matrizes[e]` é a matriz que o põe no mundo —
     então quem tem cinemática entrega a pose do instante e quem é rígido
     entrega a identidade.

     `ar` é a folga de respiro. Não é gosto: a caixa envolvente SUPERESTIMA a
     silhueta (canto de caixa cai fora de peça arredondada), então parte da
     margem já vem de graça — por isso os valores usados no site passam de 1
     em vez de ficarem em 0,8.

     É função PURA de propósito, e é a mesma que ferramentas/previa_braco.js
     roda para medir enquadramento fora do navegador. Medida que vale para o
     site tem de sair do código do site. */
  function enquadrarCaixas(cantos, matrizes, giro, inclinacao, prop, mira, fov, ar) {
    var tv = Math.tan(fov / 2) * ar;
    var th = tv * prop;
    var ci = Math.cos(inclinacao);
    /* `dir` aponta do centro para o olho — é o eixo Z da câmera */
    var dx = Math.sin(giro) * ci, dy = Math.sin(inclinacao), dz = Math.cos(giro) * ci;
    /* direita = normalizar(cima x dir), com cima = (0,1,0) */
    var rl = Math.hypot(dz, dx) || 1;
    var rx = dz / rl, rz = -dx / rl;
    /* cima da câmera = dir x direita */
    var ux = dy * rz, uy = dz * rx - dx * rz, uz = -dy * rx;
    var precisa = 6;
    for (var e = 0; e < cantos.length; e++) {
      var pts = cantos[e], M = matrizes[e];
      if (!pts || !M) continue;
      for (var i = 0; i < 8; i++) {
        var q = pts[i];
        var wx = M[0] * q[0] + M[4] * q[1] + M[8] * q[2] + M[12];
        var wy = M[1] * q[0] + M[5] * q[1] + M[9] * q[2] + M[13] - mira;
        var wz = M[2] * q[0] + M[6] * q[1] + M[10] * q[2] + M[14];
        var z = wx * dx + wy * dy + wz * dz;
        var x = wx * rx + wz * rz;
        var y = wx * ux + wy * uy + wz * uz;
        precisa = Math.max(precisa, z + Math.abs(x) / th, z + Math.abs(y) / tv);
      }
    }
    return precisa;
  }

  /* Os 8 cantos de uma caixa [minx, miny, minz, maxx, maxy, maxz]. */
  function cantosDaCaixa(c) {
    var p = [];
    for (var i = 0; i < 8; i++) {
      p.push([c[(i & 1) ? 3 : 0], c[(i & 2) ? 4 : 1], c[(i & 4) ? 5 : 2]]);
    }
    return p;
  }

  /* ================================ token ================================
     ARMADILHA CARA, e ela custou uma sessão: `getComputedStyle(el)
     .getPropertyValue('--traco')` NÃO resolve para `rgb()`. Devolve a string
     `"#003566"` crua. Ler isso com uma regex de dígitos casa o token inteiro
     como UM número — o uniform vira `[14, NaN, NaN]`.

     E o NaN não morre na máscara: em IEEE 754 `NaN x 0 = NaN`, então a camada
     multiplicada por zero continua contaminando a saída. É um bug de cor que
     sobrevive à própria máscara que deveria desligá-lo, e por isso não aparece
     ao reler o shader. Todo leitor de token para GL precisa deste parser. */
  function rgb(css, padrao) {
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
    return padrao;
  }

  /* =============================== shader =============================== */
  function compilar(gl, tipo, fonte, rotulo) {
    var s = gl.createShader(tipo);
    gl.shaderSource(s, fonte); gl.compileShader(s);
    if (!gl.getShaderParameter(s, gl.COMPILE_STATUS)) {
      console.warn("[" + (rotulo || "gl") + "] shader:", gl.getShaderInfoLog(s));
      return null;
    }
    return s;
  }

  function programa(gl, vs, fs, rotulo) {
    var v = compilar(gl, gl.VERTEX_SHADER, vs, rotulo);
    var f = compilar(gl, gl.FRAGMENT_SHADER, fs, rotulo);
    if (!v || !f) return null;
    var p = gl.createProgram();
    gl.attachShader(p, v); gl.attachShader(p, f); gl.linkProgram(p);
    if (!gl.getProgramParameter(p, gl.LINK_STATUS)) {
      console.warn("[" + (rotulo || "gl") + "] link:", gl.getProgramInfoLog(p));
      return null;
    }
    return p;
  }

  /* O RUÍDO DA LENTE, em GLSL, escrito uma vez.
     A borda da revelação é dissolvida por este fBm em `lente.js`, `braco.js` e
     `marca.js`. Se cada um tivesse o seu, os componentes leriam como
     instrumentos DIFERENTES apontados para a mesma página — e o site inteiro
     se apoia em serem o mesmo. */
  var RUIDO_GLSL = [
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
    "}"
  ].join("\n");

  var API = {
    TAU: TAU,
    mult: mult, identidade: identidade, transladar: transladar,
    giroY: giroY, giroZ: giroZ, perspectiva: perspectiva,
    normal: normal, cruz: cruz, olhar: olhar,
    enquadrarCaixas: enquadrarCaixas, cantosDaCaixa: cantosDaCaixa,
    rgb: rgb, compilar: compilar, programa: programa,
    RUIDO_GLSL: RUIDO_GLSL
  };

  /* `globalThis` e não `window`: ferramentas/previa_braco.js avalia este
     arquivo num contexto de `vm` do Node, onde `window` é um esboço mínimo. */
  (typeof globalThis !== "undefined" ? globalThis : window).I3GL = API;
})();
