(function () {
"use strict";
if (!window.I3Tela) return;
var T = window.I3Tela;
function montar(raiz) {
var cor = {};
function lerTema() {
cor.traco = T.token(raiz, "--mimico-traco", "#9FBEE0");
cor.vivo = T.token(raiz, "--mimico-vivo", "#FDC500");
cor.tinta = T.token(raiz, "--mimico-tinta", "#FFFFFF");
cor.grade = T.alfa(cor.traco, 0.14);
cor.fraco = T.alfa(cor.traco, 0.55);
cor.cheio = T.alfa(cor.traco, 0.22);
}
lerTema();
var n1 = 0.42, n2 = 0.58, vazao = 0.0, giro = 0, bomba = true;
var alarme = 0;
var TIPO = 12;
function processo(dt) {
var alvo = bomba ? 0.78 : 0.15;
vazao += ((bomba ? 0.62 : 0.02) - vazao) * dt * 1.4;
n1 += (alvo - n1) * dt * 0.16;
n2 += (0.5 + 0.28 * Math.sin(giro * 0.11) - n2) * dt * 0.22;
giro += dt * (bomba ? 3.4 : 0.2);
if (bomba && n1 > 0.76) bomba = false;
if (!bomba && n1 < 0.22) bomba = true;
alarme = n1 > 0.74 ? Math.min(1, alarme + dt * 3) : Math.max(0, alarme - dt * 2);
}
function caixa(ctx, x, y, w, h) {
ctx.strokeStyle = cor.fraco;
ctx.lineWidth = 1;
ctx.strokeRect(Math.round(x) + 0.5, Math.round(y) + 0.5,
Math.round(w), Math.round(h));
}
function tanque(ctx, x, y, w, h, nivel, tag, u) {
caixa(ctx, x, y, w, h);
var alt = Math.max(0, Math.min(1, nivel)) * (h - 4);
ctx.fillStyle = cor.cheio;
ctx.fillRect(Math.round(x) + 2, Math.round(y + h - 2 - alt),
Math.round(w) - 3, Math.round(alt));
ctx.strokeStyle = cor.vivo;
ctx.lineWidth = 1.5;
ctx.beginPath();
ctx.moveTo(x + 2, Math.round(y + h - 2 - alt) + 0.5);
ctx.lineTo(x + w - 2, Math.round(y + h - 2 - alt) + 0.5);
ctx.stroke();
ctx.strokeStyle = cor.fraco;
ctx.lineWidth = 1;
ctx.beginPath();
for (var i = 1; i < 4; i++) {
var yy = Math.round(y + h - 2 - (h - 4) * (i / 4)) + 0.5;
ctx.moveTo(x + w - 6, yy); ctx.lineTo(x + w - 1, yy);
}
ctx.stroke();
ctx.fillStyle = cor.fraco;
ctx.textAlign = "center";
ctx.fillText(tag, x + w / 2, y + h + TIPO * 1.15);
ctx.fillStyle = cor.tinta;
ctx.fillText(Math.round(nivel * 100) + u, x + w / 2, y - TIPO * 0.45);
ctx.textAlign = "left";
}
function linha(ctx, pts, corrida) {
ctx.strokeStyle = cor.fraco;
ctx.lineWidth = 1;
ctx.beginPath();
for (var i = 0; i < pts.length; i += 2) {
var x = Math.round(pts[i]) + 0.5, y = Math.round(pts[i + 1]) + 0.5;
if (i === 0) ctx.moveTo(x, y); else ctx.lineTo(x, y);
}
ctx.stroke();
if (corrida === null) return;
ctx.save();
ctx.strokeStyle = cor.vivo;
ctx.lineWidth = 2;
ctx.setLineDash([5, 11]);
ctx.lineDashOffset = -corrida;
ctx.stroke();
ctx.restore();
}
function valvula(ctx, x, y, aberta) {
var s = 5;
ctx.strokeStyle = aberta ? cor.vivo : cor.fraco;
ctx.lineWidth = 1.4;
ctx.beginPath();
ctx.moveTo(x - s, y - s); ctx.lineTo(x + s, y + s);
ctx.lineTo(x + s, y - s); ctx.lineTo(x - s, y + s);
ctx.closePath();
ctx.stroke();
}
function bombaSimbolo(ctx, x, y, r, ang, ligada) {
ctx.strokeStyle = ligada ? cor.vivo : cor.fraco;
ctx.lineWidth = 1.4;
ctx.beginPath();
ctx.arc(x, y, r, 0, Math.PI * 2);
ctx.stroke();
ctx.beginPath();
for (var k = 0; k < 2; k++) {
var a = ang + k * Math.PI;
ctx.moveTo(x, y);
ctx.lineTo(x + Math.cos(a) * (r - 2), y + Math.sin(a) * (r - 2));
}
ctx.stroke();
}
function desenhar(ctx, larg, alt, t, dt) {
if (dt) processo(dt);
ctx.textBaseline = "alphabetic";
ctx.strokeStyle = cor.grade;
ctx.lineWidth = 1;
ctx.beginPath();
for (var gx = 24; gx < larg; gx += 24) {
ctx.moveTo(Math.round(gx) + 0.5, 0); ctx.lineTo(Math.round(gx) + 0.5, alt);
}
for (var gy = 24; gy < alt; gy += 24) {
ctx.moveTo(0, Math.round(gy) + 0.5); ctx.lineTo(larg, Math.round(gy) + 0.5);
}
ctx.stroke();
var m = Math.min(larg / 520, alt / 260);
ctx.save();
ctx.translate((larg - 520 * m) / 2, (alt - 260 * m) / 2);
ctx.scale(m, m);
TIPO = T.tipo(ctx, raiz, 1 / m);
var corrida = t * 46;
tanque(ctx, 36, 58, 74, 132, n1, "LIT-201", "%");
tanque(ctx, 404, 58, 74, 132, n2, "LIT-204", "%");
linha(ctx, [110, 168, 168, 168], bomba ? corrida : null);
bombaSimbolo(ctx, 186, 168, 15, giro, bomba);
linha(ctx, [204, 168, 250, 168, 250, 96, 404, 96], bomba ? corrida : null);
valvula(ctx, 300, 96, bomba);
linha(ctx, [404, 168, 330, 168, 330, 214, 74, 214, 74, 190], null);
valvula(ctx, 200, 214, true);
function bolha(x, y, tag) {
ctx.strokeStyle = cor.fraco;
ctx.lineWidth = 1;
var r = 13 / m;
ctx.beginPath(); ctx.arc(x, y, r, 0, Math.PI * 2); ctx.stroke();
ctx.fillStyle = cor.fraco;
ctx.textAlign = "center";
ctx.fillText(tag.slice(0, 3), x, y - TIPO * 0.1);
ctx.fillText(tag.slice(4), x, y + TIPO * 0.85);
ctx.textAlign = "left";
}
bolha(250, 40, "FIC-101");
ctx.strokeStyle = cor.fraco;
ctx.setLineDash([2, 3]);
ctx.beginPath(); ctx.moveTo(250, 53); ctx.lineTo(250, 88); ctx.stroke();
ctx.setLineDash([]);
ctx.fillStyle = cor.tinta;
ctx.fillText((vazao * 180).toFixed(0) + " m3/h", 214, 148);
ctx.fillStyle = bomba ? cor.vivo : cor.fraco;
ctx.fillText(bomba ? "P-101  RUN" : "P-101  STOP", 158, 200);
if (alarme > 0.02) {
ctx.globalAlpha = alarme;
ctx.strokeStyle = cor.vivo;
ctx.lineWidth = 1;
var hf = TIPO * 1.7;
ctx.strokeRect(28.5, 8.5, 463, hf);
ctx.fillStyle = cor.vivo;
ctx.fillText("LAH-201   TK-201 LEVEL HIGH", 38, 8.5 + hf * 0.72);
ctx.globalAlpha = 1;
}
ctx.fillStyle = cor.fraco;
ctx.fillText("DEMONSTRATION MIMIC · SIMULATED VALUES", 28, 260 - TIPO * 0.4);
ctx.restore();
}
var peca = T.montar(raiz, { desenhar: desenhar });
if (peca) raiz.classList.add("is-viva");
}
function iniciar() {
var els = document.querySelectorAll("[data-mimico]");
for (var i = 0; i < els.length; i++) montar(els[i]);
}
if (document.readyState === "loading") {
document.addEventListener("DOMContentLoaded", iniciar);
} else {
iniciar();
}
})();
