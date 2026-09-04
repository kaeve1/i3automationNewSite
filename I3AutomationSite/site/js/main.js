(function () {
"use strict";
var reduzido = window.matchMedia("(prefers-reduced-motion: reduce)").matches;
(function () {
var nav = document.querySelector(".nav");
if (!nav || !nav.classList.contains("nav--sobre-heroi")) return;
var limite = Math.max(120, window.innerHeight * 0.62);
var ticando = false;
var avaliar = function () {
nav.classList.toggle("is-rolado", window.scrollY > limite);
ticando = false;
};
window.addEventListener("scroll", function () {
if (ticando) return;
ticando = true;
window.requestAnimationFrame(avaliar);
}, { passive: true });
window.addEventListener("resize", function () {
limite = Math.max(120, window.innerHeight * 0.62);
avaliar();
});
avaliar();
})();
(function () {
var botao = document.querySelector(".nav__hamburguer");
var painel = document.getElementById("menu-mobile");
if (!botao || !painel) return;
var fechar = function () {
botao.setAttribute("aria-expanded", "false");
painel.classList.remove("is-aberto");
};
botao.addEventListener("click", function () {
var aberto = botao.getAttribute("aria-expanded") === "true";
botao.setAttribute("aria-expanded", aberto ? "false" : "true");
painel.classList.toggle("is-aberto", !aberto);
});
painel.addEventListener("click", function (e) {
if (e.target.tagName === "A") fechar();
});
document.addEventListener("keydown", function (e) {
if (e.key === "Escape") fechar();
});
window.addEventListener("resize", function () {
if (window.innerWidth > 1100) fechar();
});
})();
(function () {
var alvos = Array.prototype.slice.call(document.querySelectorAll(".reveal"));
var rodape = document.querySelector(".rodape");
if (rodape && window.getComputedStyle(rodape).position === "sticky") {
alvos = alvos.filter(function (el) {
return !el.classList.contains("rodape__headline");
});
}
if (!alvos.length) return;
if (reduzido || !window.IntersectionObserver) {
for (var i = 0; i < alvos.length; i++) alvos[i].classList.add("is-visivel");
return;
}
var io = new IntersectionObserver(function (entradas) {
entradas.forEach(function (e) {
if (!e.isIntersecting) return;
e.target.classList.add("is-visivel");
io.unobserve(e.target);
});
}, { rootMargin: "0px 0px -12% 0px", threshold: 0.08 });
for (var j = 0; j < alvos.length; j++) io.observe(alvos[j]);
window.setTimeout(function () {
for (var k = 0; k < alvos.length; k++) alvos[k].classList.add("is-visivel");
io.disconnect();
}, 6000);
})();
(function () {
var intro = document.querySelector(".intro");
if (!intro) return;
var encerrado = false;
var encerrar = function () {
if (encerrado) return;
encerrado = true;
document.documentElement.classList.remove("intro-ativa");
if (intro.parentNode) intro.parentNode.removeChild(intro);
};
var TOTAL = 4100;
var animar = function () {
window.setTimeout(encerrar, reduzido ? 600 : TOTAL);
};
var texto = intro.querySelector(".intro__texto");
if (texto) {
var linhas = texto.querySelectorAll(".intro__linha");
var medirFrase = function () {
intro.style.setProperty("--largura-frase",
Math.round(texto.getBoundingClientRect().width) + "px");
for (var i = 0; i < linhas.length && i < 2; i++) {
intro.style.setProperty("--l" + (i + 1),
Math.round(linhas[i].getBoundingClientRect().width) + "px");
}
};
medirFrase();
if (document.fonts && document.fonts.ready) document.fonts.ready.then(medirFrase);
}
window.setTimeout(encerrar, 5600);
if (document.visibilityState !== "visible") { encerrar(); return; }
var iniciado = false;
var iniciar = function () {
if (iniciado) return;
iniciado = true;
window.requestAnimationFrame(animar);
};
if (document.fonts && document.fonts.ready) document.fonts.ready.then(iniciar);
window.setTimeout(iniciar, 900);
intro.addEventListener("click", encerrar);
window.addEventListener("keydown", encerrar, { once: true });
window.addEventListener("wheel", encerrar, { once: true, passive: true });
window.addEventListener("touchstart", encerrar, { once: true, passive: true });
})();
(function () {
if (reduzido) return;
var alvos = document.querySelectorAll("[data-deriva]");
if (!alvos.length || window.matchMedia("(hover: none)").matches) return;
var mx = 0, my = 0, ax = 0, ay = 0, rodando = false;
var AMPLITUDE = 18;
var passo = function () {
ax += (mx - ax) * 0.06;
ay += (my - ay) * 0.06;
for (var i = 0; i < alvos.length; i++) {
var f = parseFloat(alvos[i].getAttribute("data-deriva")) || 1;
alvos[i].style.transform =
"translate3d(" + (ax * AMPLITUDE * f).toFixed(2) + "px," +
(ay * AMPLITUDE * f).toFixed(2) + "px,0)";
}
if (Math.abs(mx - ax) > 0.001 || Math.abs(my - ay) > 0.001) {
window.requestAnimationFrame(passo);
} else {
rodando = false;
}
};
window.addEventListener("pointermove", function (e) {
mx = (e.clientX / window.innerWidth - 0.5) * 2;
my = (e.clientY / window.innerHeight - 0.5) * 2;
if (!rodando) { rodando = true; window.requestAnimationFrame(passo); }
}, { passive: true });
})();
(function () {
var heroi = document.querySelector(".heroi");
if (!heroi || window.matchMedia("(hover: none)").matches) return;
var alvos = heroi.querySelectorAll("[data-lente-texto]");
if (!alvos.length) return;
var x = 0, y = 0, pendente = false;
var pintar = function () {
pendente = false;
for (var i = 0; i < alvos.length; i++) {
var r = alvos[i].getBoundingClientRect();
alvos[i].style.setProperty("--lente-x", (x - r.left).toFixed(1) + "px");
alvos[i].style.setProperty("--lente-y", (y - r.top).toFixed(1) + "px");
}
};
heroi.addEventListener("pointermove", function (e) {
x = e.clientX; y = e.clientY;
if (!pendente) { pendente = true; window.requestAnimationFrame(pintar); }
});
heroi.addEventListener("pointerleave", function () {
for (var i = 0; i < alvos.length; i++) {
alvos[i].style.setProperty("--lente-x", "-9999px");
}
});
})();
(function () {
var alvos = document.querySelectorAll("[data-progresso]");
if (!alvos.length) return;
if (reduzido) {
for (var i = 0; i < alvos.length; i++) {
alvos[i].style.setProperty("--p", "1");
alvos[i].classList.add("is-estatico");
}
return;
}
var pendente = false;
var caixas = new Array(alvos.length);
var medir = function () {
pendente = false;
var vh = window.innerHeight || 1;
var k;
for (k = 0; k < alvos.length; k++) {
caixas[k] = alvos[k].getBoundingClientRect();
}
for (k = 0; k < alvos.length; k++) {
var el = alvos[k];
var c = caixas[k];
if (c.bottom < -vh || c.top > vh * 2) continue;
var curso = c.height - vh;
var p = curso > vh * 0.5
? -c.top / curso
: (vh - c.top) / (vh + c.height);
p = p < 0 ? 0 : (p > 1 ? 1 : p);
el.style.setProperty("--p", p.toFixed(4));
var abriu = el.getAttribute("data-abriu-em");
if (abriu) el.classList.toggle("is-aberta", p >= parseFloat(abriu));
var passos = parseInt(el.getAttribute("data-passos"), 10);
if (passos > 1) {
var n = Math.min(passos - 1, Math.floor(p * passos));
if (el.getAttribute("data-n") !== String(n)) {
el.setAttribute("data-n", n);
el.style.setProperty("--n", n);
el.dispatchEvent(new CustomEvent("passo", { detail: { n: n } }));
}
}
}
};
var pedir = function () {
if (pendente) return;
pendente = true;
window.requestAnimationFrame(medir);
};
window.addEventListener("scroll", pedir, { passive: true });
window.addEventListener("resize", pedir);
medir();
})();
(function () {
var listas = document.querySelectorAll("[data-domino]");
if (!listas.length || reduzido) return;
for (var i = 0; i < listas.length; i++) {
(function (lista) {
var itens = lista.children;
var espalhar = function (origem) {
for (var j = 0; j < itens.length; j++) {
itens[j].style.setProperty(
"--d", origem < 0 ? 99 : Math.abs(j - origem));
}
};
lista.addEventListener("pointerover", function (e) {
var alvo = e.target.closest ? e.target.closest("[data-i]") : null;
if (!alvo || alvo.parentNode !== lista) return;
espalhar(+alvo.getAttribute("data-i"));
});
lista.addEventListener("pointerleave", function () { espalhar(-1); });
lista.addEventListener("focusin", function (e) {
var alvo = e.target.closest ? e.target.closest("[data-i]") : null;
if (alvo && alvo.parentNode === lista) {
espalhar(+alvo.getAttribute("data-i"));
}
});
lista.addEventListener("focusout", function (e) {
if (!lista.contains(e.relatedTarget)) espalhar(-1);
});
espalhar(-1);
})(listas[i]);
}
})();
(function () {
var rodape = document.querySelector(".rodape");
if (!rodape || window.getComputedStyle(rodape).position !== "sticky") return;
var frase = rodape.querySelector(".rodape__headline");
var marca = document.querySelector("[data-fim-conteudo]");
if (frase) {
if (reduzido || !window.IntersectionObserver || !marca) {
frase.classList.add("is-visivel");
} else {
var io = new IntersectionObserver(function (ent) {
ent.forEach(function (e) {
if (!e.isIntersecting) return;
frase.classList.add("is-visivel");
io.disconnect();
});
}, { rootMargin: "0px 0px -8% 0px" });
io.observe(marca);
}
}
rodape.addEventListener("focusin", function () {
var main = document.querySelector("main");
if (!main) return;
var coberto = main.getBoundingClientRect().bottom
> rodape.getBoundingClientRect().top + 4;
if (coberto) {
window.scrollTo({
top: document.documentElement.scrollHeight,
behavior: reduzido ? "auto" : "smooth"
});
}
});
})();
(function () {
if (reduzido) return;
var LERP = 0.11;
var PISO_RODA = 50;
var QUADRO = 1000 / 60;
var alvo = window.scrollY;
var rodando = false;
var previsto = -1;
var teto = function () {
return Math.max(0, document.documentElement.scrollHeight - window.innerHeight);
};
var pixels = function (e) {
if (e.deltaMode === 1) return e.deltaY * 16;
if (e.deltaMode === 2) return e.deltaY * window.innerHeight;
return e.deltaY;
};
var temDono = function (no, dir) {
while (no && no !== document.body && no !== document.documentElement) {
if (no.scrollHeight > no.clientHeight + 1) {
var ov = window.getComputedStyle(no).overflowY;
if (ov === "auto" || ov === "scroll") {
var max = no.scrollHeight - no.clientHeight;
if ((dir < 0 && no.scrollTop > 0) ||
(dir > 0 && no.scrollTop < max - 1)) return true;
}
}
no = no.parentElement;
}
return false;
};
var raiz = document.documentElement;
var parar = function () {
rodando = false;
ultimo = 0;
previsto = -1;
raiz.style.scrollBehavior = "";
};
var ultimo = 0;
var passo = function (agora) {
var dt = ultimo ? Math.min(agora - ultimo, 64) : QUADRO;
ultimo = agora;
var k = 1 - Math.pow(1 - LERP, dt / QUADRO);
var atual = window.scrollY;
if (previsto >= 0 && Math.abs(atual - previsto) > 4) alvo = atual;
if (Math.abs(alvo - atual) < 0.5) { parar(); return; }
var y = atual + (alvo - atual) * k;
previsto = Math.round(y);
window.scrollTo(0, y);
window.requestAnimationFrame(passo);
};
window.addEventListener("wheel", function (e) {
if (e.ctrlKey) return;
var d = pixels(e);
if (!d || Math.abs(d) < PISO_RODA) return;
if (temDono(e.target, d)) return;
e.preventDefault();
if (!rodando) alvo = window.scrollY;
alvo = Math.max(0, Math.min(teto(), alvo + d));
if (!rodando) {
rodando = true;
ultimo = 0;
previsto = -1;
raiz.style.scrollBehavior = "auto";
window.requestAnimationFrame(passo);
}
}, { passive: false });
window.addEventListener("scroll", function () {
if (!rodando) alvo = window.scrollY;
}, { passive: true });
window.addEventListener("resize", function () {
alvo = Math.max(0, Math.min(teto(), window.scrollY));
});
})();
(function () {
var els = document.querySelectorAll("[data-ano]");
var ano = String(new Date().getFullYear());
for (var i = 0; i < els.length; i++) els[i].textContent = ano;
})();
(function () {
var faixa = document.getElementById("aviso-armazenamento");
if (!faixa) return;
var CHAVE = "i3-aviso";
var lido = false;
try { lido = window.localStorage.getItem(CHAVE) === "1"; } catch (e) {}
if (lido) return;
var botao = faixa.querySelector("[data-aviso-ok]");
var mostrado = false;
var mostrar = function () {
if (mostrado) return;
mostrado = true;
faixa.hidden = false;
window.requestAnimationFrame(function () {
window.requestAnimationFrame(function () { faixa.classList.add("is-visivel"); });
});
};
var fechar = function () {
try { window.localStorage.setItem(CHAVE, "1"); } catch (e) {}
faixa.classList.remove("is-visivel");
if (reduzido) { faixa.hidden = true; return; }
window.setTimeout(function () { faixa.hidden = true; }, 560);
};
if (botao) botao.addEventListener("click", fechar);
var raiz = document.documentElement;
if (!raiz.classList.contains("intro-ativa") || !window.MutationObserver) {
mostrar();
return;
}
var obs = new MutationObserver(function () {
if (!raiz.classList.contains("intro-ativa")) { obs.disconnect(); mostrar(); }
});
obs.observe(raiz, { attributes: true, attributeFilter: ["class"] });
window.setTimeout(function () { obs.disconnect(); mostrar(); }, 7000);
})();
(function () {
var videos = document.querySelectorAll("[data-momento-video]");
if (!videos.length) return;
if (reduzido || !window.IntersectionObserver) return;
var tocando = null;
var parar = function (v) {
if (!v) return;
try { v.pause(); } catch (e) {   }
};
var obs = new IntersectionObserver(function (entradas) {
for (var i = 0; i < entradas.length; i++) {
var e = entradas[i];
var v = e.target;
if (e.isIntersecting) {
if (v.hasAttribute("data-parado")) continue;
if (tocando && tocando !== v) parar(tocando);
tocando = v;
var p = v.play();
if (p && p.catch) p.catch(function () {   });
} else if (v === tocando) {
parar(v);
tocando = null;
} else {
parar(v);
}
}
}, {
threshold: 0.25
});
for (var i = 0; i < videos.length; i++) obs.observe(videos[i]);
document.addEventListener("visibilitychange", function () {
if (document.hidden) parar(tocando);
else if (tocando && !tocando.hasAttribute("data-parado")) {
var p = tocando.play();
if (p && p.catch) p.catch(function () {});
}
});
})();
(function () {
var botoes = document.querySelectorAll("[data-pausa]");
if (!botoes.length) return;
for (var i = 0; i < botoes.length; i++) (function (botao) {
var video = document.getElementById(botao.getAttribute("data-pausa"));
if (!video) return;
if (reduzido) { botao.setAttribute("hidden", ""); return; }
var rotular = function (pausado) {
botao.setAttribute("aria-pressed", pausado ? "true" : "false");
botao.setAttribute("aria-label",
pausado ? "Play background video" : "Pause background video");
};
botao.addEventListener("click", function () {
if (video.paused) {
video.removeAttribute("data-parado");
var p = video.play();
if (p && p.catch) p.catch(function () {});
rotular(false);
} else {
video.setAttribute("data-parado", "");
video.pause();
rotular(true);
}
});
video.addEventListener("pause", function () { rotular(true); });
video.addEventListener("play", function () { rotular(false); });
rotular(video.paused);
})(botoes[i]);
})();
})();
