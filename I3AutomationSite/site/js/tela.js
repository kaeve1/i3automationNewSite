(function () {
"use strict";
var TETO = 4096;
function token(el, nome, reserva) {
var v = window.getComputedStyle(el).getPropertyValue(nome).trim();
return v || reserva;
}
function alfa(cor, a) {
var c = cor.trim();
if (c.charAt(0) === "#") {
var h = c.slice(1);
if (h.length === 3) h = h[0] + h[0] + h[1] + h[1] + h[2] + h[2];
var n = parseInt(h, 16);
return "rgba(" + ((n >> 16) & 255) + "," + ((n >> 8) & 255) + "," +
(n & 255) + "," + a + ")";
}
var m = c.match(/rgba?\(([^)]+)\)/);
if (!m) return c;
var p = m[1].split(",");
return "rgba(" + p[0] + "," + p[1] + "," + p[2] + "," + a + ")";
}
var TIPO_PX = 12, TIPO_TRACK = 0.14;
function tipo(ctx, el, escala) {
var e = escala || 1;
var px = TIPO_PX * e;
ctx.font = px.toFixed(3) + "px " +
token(el, "--font-mono", "ui-monospace, monospace");
if ("letterSpacing" in ctx) {
ctx.letterSpacing = (TIPO_PX * TIPO_TRACK * e).toFixed(3) + "px";
}
return px;
}
function montar(raiz, opcoes) {
var canvas = raiz.querySelector("canvas");
if (!canvas || !canvas.getContext) return null;
var ctx = canvas.getContext("2d");
if (!ctx) return null;
var reduzido = window.matchMedia("(prefers-reduced-motion: reduce)").matches;
var larg = 1, alt = 1, dpr = 1;
var visivel = false, rodando = false, anterior = 0, t = 0;
function medir() {
var c = raiz.getBoundingClientRect();
if (c.width < 2 || c.height < 2) return false;
dpr = Math.min(window.devicePixelRatio || 1, 2);
larg = Math.min(c.width, TETO / dpr);
alt = Math.min(c.height, TETO / dpr);
var w = Math.round(larg * dpr), h = Math.round(alt * dpr);
if (canvas.width !== w || canvas.height !== h) {
canvas.width = w;
canvas.height = h;
}
return true;
}
function pintar(dt) {
ctx.setTransform(dpr, 0, 0, dpr, 0, 0);
ctx.clearRect(0, 0, larg, alt);
opcoes.desenhar(ctx, larg, alt, t, dt);
}
function quadro(agora) {
rodando = false;
var dt = anterior ? Math.min((agora - anterior) / 1000, 0.064) : 0.016;
anterior = agora;
t += dt;
pintar(dt);
if (visivel && !reduzido) acordar();
}
function acordar() {
if (rodando) return;
rodando = true;
window.requestAnimationFrame(quadro);
}
function refazer() {
if (!medir()) return;
if (opcoes.medida) opcoes.medida(larg, alt);
anterior = 0;
if (reduzido) pintar(0); else acordar();
}
window.addEventListener("resize", refazer);
if (window.IntersectionObserver) {
new IntersectionObserver(function (ent) {
visivel = ent[0].isIntersecting;
if (visivel) { anterior = 0; if (reduzido) pintar(0); else acordar(); }
}, { rootMargin: "120px" }).observe(raiz);
} else {
visivel = true;
}
if (!medir()) return null;
if (opcoes.medida) opcoes.medida(larg, alt);
pintar(0);
return {
raiz: raiz, canvas: canvas, ctx: ctx, reduzido: reduzido,
acordar: acordar, refazer: refazer, redesenhar: function () { pintar(0); },
dim: function () { return [larg, alt]; }
};
}
window.I3Tela = { montar: montar, token: token, alfa: alfa, tipo: tipo };
})();
