(function () {
"use strict";
var TAU = Math.PI * 2;
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
function enquadrarCaixas(cantos, matrizes, giro, inclinacao, prop, mira, fov, ar) {
var tv = Math.tan(fov / 2) * ar;
var th = tv * prop;
var ci = Math.cos(inclinacao);
var dx = Math.sin(giro) * ci, dy = Math.sin(inclinacao), dz = Math.cos(giro) * ci;
var rl = Math.hypot(dz, dx) || 1;
var rx = dz / rl, rz = -dx / rl;
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
function cantosDaCaixa(c) {
var p = [];
for (var i = 0; i < 8; i++) {
p.push([c[(i & 1) ? 3 : 0], c[(i & 2) ? 4 : 1], c[(i & 4) ? 5 : 2]]);
}
return p;
}
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
(typeof globalThis !== "undefined" ? globalThis : window).I3GL = API;
})();
