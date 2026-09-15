(function () {
"use strict";
if (!window.I3Tela) return;
var T = window.I3Tela;
var K = 1.0, TAU = 2.6, L = 0.55;
var SINTONIA = { kp: 2.20, ki: 0.85, kd: 0.30 };
var JANELA = 22;
var PASSO = 1 / 60;
function montar(raiz) {
var canvas = raiz.querySelector("canvas");
if (!canvas) return;
var sp = 0.62;
var pv = 0.30, integral = 0, medAnterior = 0.30, u = 0;
var atraso = [];
var hist = [];
var relogio = 0, acumulado = 0;
var cor = {};
function lerTema() {
cor.traco = T.token(raiz, "--malha-traco", "#9FBEE0");
cor.pv = T.token(raiz, "--malha-pv", "#FFFFFF");
cor.sp = T.token(raiz, "--malha-sp", "#B9D2EA");
cor.grade = T.alfa(cor.traco, 0.16);
cor.fraco = T.alfa(cor.traco, 0.55);
}
lerTema();
function integrar(dt) {
var s = SINTONIA;
var erro = sp - pv;
var dMed = (pv - medAnterior) / Math.max(dt, 1e-6);
medAnterior = pv;
var termoI = integral + s.ki * erro * dt;
var bruto = s.kp * erro + termoI - s.kd * dMed;
var sat = Math.max(0, Math.min(1, bruto));
if (bruto === sat || erro * (sat - bruto) > 0) integral = termoI;
u = sat;
atraso.push(u);
var n = Math.max(1, Math.round(L / dt));
while (atraso.length > n) atraso.shift();
var uAtrasado = atraso.length >= n ? atraso[0] : 0;
pv += (K * uAtrasado - pv) * (dt / TAU);
}
function avancar(dt) {
acumulado += dt;
var voltas = 0;
while (acumulado >= PASSO && voltas < 240) {
integrar(PASSO);
relogio += PASSO;
acumulado -= PASSO;
voltas++;
hist.push([relogio, sp, pv]);
}
while (hist.length && hist[0][0] < relogio - JANELA) hist.shift();
}
var PAD = { e: 46, d: 14, c: 18, b: 26 };
function xy(larg, alt, tempo, v) {
var x = PAD.e + (larg - PAD.e - PAD.d) *
(1 - (relogio - tempo) / JANELA);
var y = alt - PAD.b - (alt - PAD.c - PAD.b) * v;
return [x, y];
}
function pena(ctx, larg, alt, idx, c, larguraLinha, tracejada) {
if (hist.length < 2) return;
ctx.beginPath();
for (var i = 0; i < hist.length; i++) {
var p = xy(larg, alt, hist[i][0], hist[i][idx]);
if (i === 0) ctx.moveTo(p[0], p[1]); else ctx.lineTo(p[0], p[1]);
}
ctx.strokeStyle = c;
ctx.lineWidth = larguraLinha;
ctx.lineJoin = "round";
if (tracejada) ctx.setLineDash([6, 5]); else ctx.setLineDash([]);
ctx.stroke();
ctx.setLineDash([]);
}
function desenhar(ctx, larg, alt, tempoTotal, dt) {
if (dt) avancar(dt);
var x0 = PAD.e, x1 = larg - PAD.d;
var y0 = PAD.c, y1 = alt - PAD.b;
ctx.strokeStyle = cor.grade;
ctx.lineWidth = 1;
ctx.beginPath();
for (var i = 0; i <= 4; i++) {
var y = y0 + (y1 - y0) * (i / 4);
ctx.moveTo(x0, Math.round(y) + 0.5);
ctx.lineTo(x1, Math.round(y) + 0.5);
}
for (var j = 0; j <= 5; j++) {
var x = x0 + (x1 - x0) * (j / 5);
ctx.moveTo(Math.round(x) + 0.5, y0);
ctx.lineTo(Math.round(x) + 0.5, y1);
}
ctx.stroke();
ctx.strokeStyle = cor.fraco;
ctx.beginPath();
ctx.moveTo(Math.round(x0) + 0.5, y0);
ctx.lineTo(Math.round(x0) + 0.5, y1);
ctx.lineTo(x1, Math.round(y1) + 0.5);
ctx.stroke();
pena(ctx, larg, alt, 1, cor.sp, 1, true);
pena(ctx, larg, alt, 2, cor.pv, 2);
var pSp = xy(larg, alt, relogio, sp);
ctx.fillStyle = cor.sp;
ctx.fillRect(x1 - 7, Math.round(pSp[1]) - 1, 7, 2);
ctx.strokeStyle = cor.sp;
ctx.lineWidth = 1;
ctx.strokeRect(x1 - 6.5, Math.round(pSp[1]) - 5.5, 5, 11);
T.tipo(ctx, raiz);
ctx.textBaseline = "middle";
var ySp = xy(larg, alt, relogio, sp)[1];
var yPv = xy(larg, alt, relogio, pv)[1];
var SEPARA = 13;
if (Math.abs(ySp - yPv) < SEPARA) {
ySp = yPv + (ySp <= yPv ? -SEPARA : SEPARA);
}
ctx.fillStyle = cor.sp;
ctx.fillText("SP", 8, ySp);
ctx.fillStyle = cor.pv;
ctx.fillText("PV", 8, yPv);
ctx.fillStyle = cor.fraco;
ctx.textBaseline = "top";
ctx.fillText("MV " + Math.round(u * 100) + "%", x0 + 6, y0 + 4);
}
var peca = T.montar(raiz, { desenhar: desenhar });
if (!peca) return;
raiz.classList.add("is-viva");
function daPonteiro(e) {
var c = canvas.getBoundingClientRect();
var v = 1 - (e.clientY - c.top - PAD.c) / Math.max(1, c.height - PAD.c - PAD.b);
sp = Math.max(0.05, Math.min(0.95, v));
peca.acordar();
}
var arrastando = false;
canvas.addEventListener("pointerdown", function (e) {
arrastando = true;
canvas.setPointerCapture(e.pointerId);
daPonteiro(e);
e.preventDefault();
});
canvas.addEventListener("pointermove", function (e) {
if (arrastando) daPonteiro(e);
});
canvas.addEventListener("pointerup", function () { arrastando = false; });
canvas.addEventListener("pointercancel", function () { arrastando = false; });
canvas.addEventListener("keydown", function (e) {
var d = (e.key === "ArrowUp" || e.key === "ArrowRight") ? 0.05
: (e.key === "ArrowDown" || e.key === "ArrowLeft") ? -0.05 : 0;
if (!d) return;
sp = Math.max(0.05, Math.min(0.95, sp + d));
canvas.setAttribute("aria-valuenow", Math.round(sp * 100));
peca.acordar();
e.preventDefault();
});
if (peca.reduzido) {
for (var k = 0; k < Math.round(JANELA / PASSO); k++) {
integrar(PASSO); relogio += PASSO; hist.push([relogio, sp, pv]);
}
while (hist.length && hist[0][0] < relogio - JANELA) hist.shift();
peca.redesenhar();
}
}
function iniciar() {
var els = document.querySelectorAll("[data-malha]");
for (var i = 0; i < els.length; i++) montar(els[i]);
}
if (document.readyState === "loading") {
document.addEventListener("DOMContentLoaded", iniciar);
} else {
iniciar();
}
})();
