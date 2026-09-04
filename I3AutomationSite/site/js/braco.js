(function () {
"use strict";
var TAU = Math.PI * 2;
var reduzido = window.matchMedia("(prefers-reduced-motion: reduce)").matches;
var G = (typeof globalThis !== "undefined" ? globalThis : window).I3GL;
var mult = G.mult, transladar = G.transladar, giroY = G.giroY, giroZ = G.giroZ;
var perspectiva = G.perspectiva, normal = G.normal, cruz = G.cruz, olhar = G.olhar;
var rgb = G.rgb, programa = G.programa;
function aresta(L, elo, a, b, p) {
L.push(a[0], a[1], a[2], b[0], b[1], b[2], p, elo);
var c = CAIXAS[elo] || (CAIXAS[elo] = [1e9, 1e9, 1e9, -1e9, -1e9, -1e9]);
for (var i = 0; i < 3; i++) {
c[i] = Math.min(c[i], a[i], b[i]);
c[i + 3] = Math.max(c[i + 3], a[i], b[i]);
}
}
var CAIXAS = [];
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
var XY = function (u, v, w) { return [u, v, w]; };
var XZ = function (u, v, w) { return [u, w, v]; };
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
var PIVO = [
null,
[0, 1.72, 0],
[0, 1.05, 0],
[0, 3.45, 0],
[0, 2.95, 0],
[0, 0.62, 0],
[0, 0.78, 0]
];
var PIVO_DEDO = 0.92;
function construir() {
var L = [];
CAIXAS = [];
var f = 1.42;
chapa(L, 0, [[-f, -f, 0.30], [f, -f, 0.30], [f, f, 0.30], [-f, f, 0.30]],
0, 0.26, 0.95, { plano: XZ, n: 40, nervura: 5 });
[[-f, -f], [f, -f], [f, f], [-f, f]].forEach(function (c) {
traco(L, 0, [[c[0], c[1], 0.155]], 0.27, 0.5, { plano: XZ, n: 14 });
});
coluna(L, 0, 0, 0.26, 0, 1.06, 0.96, 1.30, 30, 0.9);
traco(L, 0, [[0, 0, 0.99]], 1.30, 0.45, { plano: XZ, n: 30 });
coluna(L, 1, 0, -0.14, 0, 0.99, 1.02, 0.42, 30, 0.85);
[-1, 1].forEach(function (s) {
chapa(L, 1, [[0, 0.30, 0.86], [0, 1.05, 1.02]],
s * 0.62, s * 0.96, 0.8, { n: 34, nervura: 8 });
});
chapa(L, 2, [[0, 0, 1.04], [0, 3.45, 0.82]], -0.70, 0.70, 1, { nervura: 5 });
[-0.70, 0.70].forEach(function (z) {
traco(L, 2, [[0, 0.92, 0.52], [0, 2.62, 0.40]], z, 0.48, { n: 30 });
});
[-1, 1].forEach(function (s) {
chapa(L, 2, [[0, 0, 0.74]], s * 0.70, s * 0.80, 0.7, { n: 30, nervura: 9 });
});
chapa(L, 3, [[0, 0, 0.80], [0, 2.95, 0.50]], -0.54, 0.54, 1, { nervura: 5 });
[-0.54, 0.54].forEach(function (z) {
traco(L, 3, [[0, 0.62, 0.34], [0, 1.95, 0.26]], z, 0.42, { n: 26 });
});
[-0.545, 0.545].forEach(function (z) {
aresta(L, 3, [-0.30, 1.10, z], [0.30, 1.16, z], 0.34);
aresta(L, 3, [-0.30, 0.94, z], [0.30, 1.00, z], 0.34);
});
coluna(L, 3, 0, 2.62, 0, 0.46, 0.44, 0.36, 22, 0.75);
coluna(L, 4, 0, -0.06, 0, 0.43, 0.41, 0.60, 22, 0.8);
traco(L, 4, [[0, 0, 0.30]], 0.55, 0.4, { plano: XZ, n: 18 });
chapa(L, 5, [[0, 0, 0.42], [0, 0.62, 0.36]], -0.34, 0.34, 0.9, { n: 34, nervura: 7 });
coluna(L, 5, 0, 0.60, 0, 0.34, 0.32, 0.20, 20, 0.7);
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
[7, 8].forEach(function (elo) {
var s = elo === 7 ? -1 : 1;
chapa(L, elo, [[0, 0, 0.19], [-s * 0.05, 0.50, 0.15], [-s * 0.17, 0.98, 0.11]],
-0.14, 0.14, 0.95, { n: 30, nervura: 9 });
for (var g = 0; g < 4; g++) {
var t = g / 3;
var x = -s * (0.06 + t * 0.13), y = 0.60 + t * 0.30;
aresta(L, elo, [x, y, -0.14], [x, y, 0.14], 0.32);
}
});
var cantos = CAIXAS.map(function (c) {
var p = [];
for (var i = 0; i < 8; i++) {
p.push([c[(i & 1) ? 3 : 0], c[(i & 2) ? 4 : 1], c[(i & 4) ? 5 : 2]]);
}
return p;
});
return { segmentos: new Float32Array(L), cantos: cantos };
}
var CICLO = 13;
function pose(t) {
var f = reduzido ? 0.22 : (t / CICLO) % 1;
var w = f * TAU;
var s1 = Math.sin(w), s2 = Math.sin(w + 0.85), s3 = Math.sin(w + 1.5);
var a1 = s1 * 0.20;
var a2 = -0.12 + s2 * 0.10;
var a3 = -2.30 + s3 * 0.16;
var a4 = s1 * 0.22;
var a5 = -0.20 - s3 * 0.14;
var a6 = s2 * 0.34;
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
m[7] = mult(mult(m[6], transladar(-PIVO_DEDO * 0.42, PIVO_DEDO, 0)), giroZ(abertura));
m[8] = mult(mult(m[6], transladar(PIVO_DEDO * 0.42, PIVO_DEDO, 0)), giroZ(-abertura));
return m;
}
var FOV = 0.52;
var MIRA = 3.3;
var AR = 0.98;
function enquadrar(cantos, matrizes, giro, inclinacao, prop) {
return G.enquadrarCaixas(cantos, matrizes, giro, inclinacao, prop, MIRA, FOV, AR);
}
var VS = [
"#version 300 es",
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
"  vProf = clamp(1.0 - (c.w - (uDist - uRaioPeca)) / (2.0 * uRaioPeca), 0.55, 1.0);",
"  vPeso = peso;",
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
G.RUIDO_GLSL,
"void main() {",
"  float lado = smoothstep(uCorte - 0.004, uCorte + 0.004, vTela.y);",
"  vec3  cTinta = mix(uTintaB, uTinta, lado);",
"  vec3  cAceso = mix(uAcesoB, uAceso, lado);",
"  float ganho  = mix(uGanhoB, uGanhoA, lado);",
"  float d = length((vTela - uPonteiro) * vec2(uProp, 1.0)) / max(uRaio, 1e-4);",
"  float n = (fbm(vTela * 9.0 + uTempo * 0.05) - 0.5) * 0.17;",
"  float rev = (1.0 - smoothstep(0.80, 1.04, d + n)) * uAtivo;",
"  float a = (0.55 + 0.45 * vPeso) * ganho * vProf * uEntrada",
"          * (1.0 + rev * 0.42);",
"  vec3 c = mix(cTinta, cAceso, rev);",
"  float t = (d + n - 0.94) * 20.0;",
"  float banda = exp(-t * t) * uAtivo * uEntrada;",
"  c = mix(c, cAceso, clamp(banda * 0.85, 0.0, 1.0));",
"  a = max(a, banda * vPeso * 0.75);",
"  a *= 1.0 - smoothstep(vMeia - 0.5, vMeia + 0.5, abs(vBorda));",
"  cor = vec4(c, clamp(a, 0.0, 1.0));",
"}"
].join("\n");
function montar(raiz) {
var canvas = raiz.querySelector(".braco__tela");
if (!canvas || !window.WebGL2RenderingContext) {
raiz.classList.add("is-indisponivel");
return;
}
var gl = canvas.getContext("webgl2", {
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
[["pa", 3, 0], ["pb", 3, 12], ["peso", 1, 24], ["elo", 1, 28]]
.forEach(function (a) {
var loc = gl.getAttribLocation(prog, a[0]);
gl.enableVertexAttribArray(loc);
gl.vertexAttribPointer(loc, a[1], gl.FLOAT, false, 32, a[2]);
gl.vertexAttribDivisor(loc, 1);
});
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
var giro = 2.40, giroVel = 0, inclinacao = 0.16;
var arrastando = false, ultimoX = 0, ultimoY = 0;
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
fina = parseFloat(cs.getPropertyValue("--braco-linha-fina")) || 0.9;
grossa = parseFloat(cs.getPropertyValue("--braco-linha-grossa")) || 1.8;
}
function medirCorte() {
if (!heroi) { corte = -1; return; }
var c = canvas.getBoundingClientRect();
if (!c.height) { corte = -1; return; }
var fim = heroi.getBoundingClientRect().bottom;
corte = 1 - (fim - c.top) / c.height;
}
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
if (Math.abs(giroVel) < 0.02 && !reduzido) giro += 0.035 * dt;
}
entrada += ((visivel ? 1 : 0) - entrada) * (1 - Math.pow(0.02, dt));
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
function situar(e) {
var c = raiz.getBoundingClientRect();
pontX = (e.clientX - c.left) / Math.max(1, c.width);
pontY = 1 - (e.clientY - c.top) / Math.max(1, c.height);
}
var campo = (raiz.closest && raiz.closest(".heroi")) || raiz;
campo.addEventListener("pointerenter", function () {
alvoAtivo = 1; acordar();
});
campo.addEventListener("pointerleave", function () {
if (arrastando) return;
alvoAtivo = 0; acordar();
});
campo.addEventListener("pointermove", function (e) {
if (arrastando) return;
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
inclinacao = Math.max(-0.25, Math.min(0.95, inclinacao + dy * 0.004));
}
acordar();
});
function soltar(e) {
if (!arrastando) return;
arrastando = false;
if (e && e.pointerId != null && raiz.hasPointerCapture &&
raiz.hasPointerCapture(e.pointerId)) raiz.releasePointerCapture(e.pointerId);
if (window.matchMedia("(hover: none)").matches) alvoAtivo = 0;
acordar();
}
raiz.addEventListener("pointerup", soltar);
raiz.addEventListener("pointercancel", soltar);
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
lerTema();
medir();
window.addEventListener("resize", function () { medir(); acordar(); });
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
