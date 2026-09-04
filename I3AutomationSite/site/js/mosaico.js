(function () {
"use strict";
var mosaico = document.querySelector("[data-mosaico]");
if (!mosaico) return;
var colunas = [].slice.call(mosaico.children);
if (!colunas.length) return;
var figuras = [].slice.call(mosaico.querySelectorAll(".galeria__figura"))
.sort(function (a, b) {
return (a.getAttribute("data-ordem") | 0) - (b.getAttribute("data-ordem") | 0);
});
if (!figuras.length) return;
var LEGENDA = 0.18;
var quantas = function () {
var w = window.innerWidth || document.documentElement.clientWidth;
return w <= 700 ? 1 : (w <= 1100 ? 2 : 3);
};
var atual = parseInt(mosaico.getAttribute("data-colunas"), 10) || colunas.length;
var montar = function (n) {
if (n === atual) return;
atual = n;
mosaico.setAttribute("data-colunas", n);
var alturas = [];
var i;
for (i = 0; i < colunas.length; i++) {
colunas[i].style.display = i < n ? "" : "none";
if (i < n) {
while (colunas[i].firstChild) colunas[i].removeChild(colunas[i].firstChild);
alturas.push(0);
}
}
for (i = 0; i < figuras.length; i++) {
var k = 0;
var j;
for (j = 1; j < alturas.length; j++) if (alturas[j] < alturas[k]) k = j;
colunas[k].appendChild(figuras[i]);
var ar = parseFloat(figuras[i].getAttribute("data-ar")) || 1;
alturas[k] += 1 / ar + LEGENDA;
}
};
var pendente = false;
var pedir = function () {
if (pendente) return;
pendente = true;
window.requestAnimationFrame(function () {
pendente = false;
montar(quantas());
});
};
window.addEventListener("resize", pedir);
window.addEventListener("orientationchange", pedir);
montar(quantas());
})();
