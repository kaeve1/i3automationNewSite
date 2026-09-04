/* Previa da MARCA EXTRUDADA fora do navegador.

   Por que existe: `site/js/marca.js` le a geometria do DOM e a extruda, e a
   unica pergunta que importa -- "isto se parece com a marca i3 em tres
   dimensoes?" -- nao se responde lendo o arquivo. A extensao do Chrome nao
   conecta neste ambiente, entao a alternativa era entregar sem ver.

   ONDE ESTA A FRONTEIRA, e ela e a parte importante deste harness.

   O que e ESTUBADO aqui e a PLATAFORMA, nunca a logica do site:
     - o DOM minimo (querySelector, getAttribute, closest)
     - `getTotalLength` / `getPointAtLength`, que no navegador sao o mecanismo
       de SVG andando sobre o caminho

   O que roda de verdade, do arquivo de producao, e TUDO o mais: `construir()`,
   `amostrar()` com a preservacao de canto, `prisma()`, a tabela PAPEL com os
   pesos e as profundidades, FOV, MIRA, AR e o enquadramento de gl.js. Se a
   geometria mudar em marca.js, esta previa muda junto -- que e o ponto, e e a
   licao que a copia de `pose()` em previa_braco.js ensinou: previa que diverge
   do original mede um site que nao existe.

   E OS CAMINHOS SAEM DO SITE CONSTRUIDO, nao de uma copia. O `<svg>` e lido de
   `site/who-we-are.html`, ou seja, do que `icone_marca()` realmente emitiu.

   Uso: node ferramentas/previa_marca.js <giro> <incl> <larg> <alt> > saida.json
*/
"use strict";
const fs = require("fs");
const path = require("path");
const vm = require("vm");

const RAIZ = path.join(__dirname, "..");

/* ===================== 1. os caminhos, do site construido ===================== */
const HTML = fs.readFileSync(path.join(RAIZ, "site", "who-we-are.html"), "utf8");
const bloco = HTML.match(/<svg class="marca3d__plano"[\s\S]*?<\/svg>/);
if (!bloco) throw new Error("nao achei o <svg class=marca3d__plano> em who-we-are.html");
const SVG = bloco[0];

const vbm = SVG.match(/viewBox="([\d.\s-]+)"/);
const VB = vbm ? vbm[1].trim().split(/\s+/).map(Number) : [0, 0, 410, 258];

const ELEMENTOS = [];
const re = /<(path|rect)\b([^>]*)\/?>/g;
let m;
while ((m = re.exec(SVG))) {
  const tag = m[1], attrs = m[2];
  const pega = (n) => {
    const a = attrs.match(new RegExp(n + '="([^"]*)"'));
    return a ? a[1] : null;
  };
  /* as chaves tem de ser os nomes REAIS dos atributos: marca.js le por
     `getAttribute("class")`, e um apelido aqui devolveria contorno vazio */
  ELEMENTOS.push({ tag, "class": pega("class") || "", d: pega("d"),
                   x: pega("x"), y: pega("y"),
                   width: pega("width"), height: pega("height") });
}

/* ============ 2. o stub de plataforma: andar sobre o caminho SVG ============
   Achata M/m L/l H/h V/v C/c Z/z numa polilinha densa e devolve pontos por
   comprimento de arco. E o que o mecanismo de SVG faz; nao ha nada de i3 aqui.
   Cubicas em 64 passos: bem acima do passo de amostragem de marca.js (~1,2
   unidade num "3" de ~90 de altura), entao o achatamento nao e o gargalo. */
function achatar(d) {
  const num = d.match(/-?\d*\.?\d+(?:e[-+]?\d+)?|[a-zA-Z]/g) || [];
  const pts = [];
  let i = 0, cx = 0, cy = 0, sx = 0, sy = 0, cmd = "";
  const n = () => parseFloat(num[i++]);
  const push = (x, y) => pts.push([x, y]);
  const cubica = (x1, y1, x2, y2, x3, y3) => {
    const PASSOS = 64;
    for (let k = 1; k <= PASSOS; k++) {
      const t = k / PASSOS, u = 1 - t;
      push(u * u * u * cx + 3 * u * u * t * x1 + 3 * u * t * t * x2 + t * t * t * x3,
           u * u * u * cy + 3 * u * u * t * y1 + 3 * u * t * t * y2 + t * t * t * y3);
    }
    cx = x3; cy = y3;
  };
  while (i < num.length) {
    if (/[a-zA-Z]/.test(num[i])) cmd = num[i++];
    const rel = cmd === cmd.toLowerCase();
    const bx = rel ? cx : 0, by = rel ? cy : 0;
    switch (cmd.toUpperCase()) {
      case "M":
        cx = bx + n(); cy = by + n(); sx = cx; sy = cy; push(cx, cy);
        cmd = rel ? "l" : "L";          /* pares seguintes de M sao lineto */
        break;
      case "L": cx = bx + n(); cy = by + n(); push(cx, cy); break;
      case "H": cx = bx + n(); push(cx, cy); break;
      case "V": cy = by + n(); push(cx, cy); break;
      case "C": {
        const x1 = bx + n(), y1 = by + n(), x2 = bx + n(), y2 = by + n();
        cubica(x1, y1, x2, y2, bx + n(), by + n());
        break;
      }
      case "Z": cx = sx; cy = sy; push(cx, cy); break;
      default: throw new Error("comando de caminho nao suportado: " + cmd);
    }
  }
  return pts;
}

function fazerElemento(e) {
  const el = {
    tagName: e.tag,
    getAttribute: (k) => e[k],
    closest: () => null            /* nao ha `.marca__contorno` neste SVG */
  };
  if (e.tag === "path" && e.d) {
    const pts = achatar(e.d);
    const acc = [0];
    for (let k = 1; k < pts.length; k++) {
      acc.push(acc[k - 1] + Math.hypot(pts[k][0] - pts[k - 1][0],
                                       pts[k][1] - pts[k - 1][1]));
    }
    const total = acc[acc.length - 1];
    el.getTotalLength = () => total;
    el.getPointAtLength = (s) => {
      s = Math.max(0, Math.min(total, s));
      let lo = 0, hi = acc.length - 1;
      while (lo < hi - 1) {
        const mid = (lo + hi) >> 1;
        if (acc[mid] <= s) lo = mid; else hi = mid;
      }
      const span = acc[hi] - acc[lo] || 1;
      const t = (s - acc[lo]) / span;
      return { x: pts[lo][0] + (pts[hi][0] - pts[lo][0]) * t,
               y: pts[lo][1] + (pts[hi][1] - pts[lo][1]) * t };
    };
  }
  return el;
}

const NOS = ELEMENTOS.map(fazerElemento);
const svgFalso = {
  viewBox: { baseVal: { width: VB[2], height: VB[3] } },
  querySelectorAll: () => NOS,
  querySelector: () => null
};

/* ============ 3. os modulos de PRODUCAO, avaliados sem alteracao ============ */
const NUCLEO = fs.readFileSync(path.join(RAIZ, "site", "js", "gl.js"), "utf8");
let fonte = fs.readFileSync(path.join(RAIZ, "site", "js", "marca.js"), "utf8");

/* Expoe os internos SEM tocar no arquivo de producao: o modulo e uma IIFE,
   entao basta injetar a exportacao imediatamente antes do fecho dela. */
const FECHO = "})();";
const corte = fonte.lastIndexOf(FECHO);
if (corte < 0) throw new Error("nao achei o fecho da IIFE em marca.js");
fonte = fonte.slice(0, corte) +
  "globalThis.__marca = { construir, PAPEL, FOV, MIRA, AR, " +
  "Z_FUNDO, Z_FRENTE, Z_TELA, Z_GLIFO, ESCALA };\n" +
  fonte.slice(corte);

const contexto = {
  console,
  globalThis: null,
  window: {
    matchMedia: () => ({ matches: false, addEventListener() {} }),
    requestAnimationFrame() {},
    WebGL2RenderingContext: null
  },
  document: { readyState: "complete", querySelectorAll: () => [], addEventListener() {} }
};
contexto.globalThis = contexto;
vm.createContext(contexto);
vm.runInContext(NUCLEO, contexto);
vm.runInContext(fonte, contexto);
const M = contexto.__marca;
const G = contexto.I3GL;

/* ============================ 4. camera e projecao ============================ */
const giro = parseFloat(process.argv[2] ?? "-0.62");
const incl = parseFloat(process.argv[3] ?? "0.18");
const LARG = parseFloat(process.argv[4] ?? "340");
const ALT = parseFloat(process.argv[5] ?? "364");
/* AR e MIRA entram por argv para permitir VARREDURA de enquadramento sem
   editar o arquivo de producao; sem argumento sao os valores que estao em
   marca.js, entao rodar limpo mede o que o navegador faz. */
const AR = parseFloat(process.argv[6] ?? "0") || null;
const MIRA = process.argv[7] !== undefined ? parseFloat(process.argv[7]) : null;

const cena = M.construir(svgFalso);
if (!cena) throw new Error("construir() devolveu vazio -- nenhum contorno foi lido");
const dados = cena.segmentos;

const CANTOS = [G.cantosDaCaixa(cena.caixa)];
const IDENT = [G.identidade()];
const ar = AR || M.AR;
const mira = MIRA === null ? M.MIRA : MIRA;
const d = G.enquadrarCaixas(CANTOS, IDENT, giro, incl, LARG / ALT,
                            mira, M.FOV, ar);

let RAIO = 0.5;
for (const p of CANTOS[0]) RAIO = Math.max(RAIO, Math.hypot(p[0], p[1] - mira, p[2]));

const olho = [
  Math.sin(giro) * Math.cos(incl) * d,
  mira + Math.sin(incl) * d,
  Math.cos(giro) * Math.cos(incl) * d
];
const mvp = G.mult(G.perspectiva(M.FOV, LARG / ALT, 1, 120),
                   G.olhar(olho, [0, mira, 0], [0, 1, 0]));

function aplicar(Mx, v) {
  const o = [0, 0, 0, 0];
  for (let r = 0; r < 4; r++) {
    o[r] = Mx[0 * 4 + r] * v[0] + Mx[1 * 4 + r] * v[1] +
           Mx[2 * 4 + r] * v[2] + Mx[3 * 4 + r] * v[3];
  }
  return o;
}

/* Larguras iguais as dos tokens do CSS (--marca-linha-fina/-grossa). Entram
   por argv para permitir VARREDURA de espessura sem editar producao. */
const FINA = parseFloat(process.argv[8] ?? "0") || 1.4;
const GROSSA = parseFloat(process.argv[9] ?? "0") || 2.8;
const GANHO = 0.92;

const segs = [];
for (let k = 0; k < dados.length; k += 8) {
  const peso = dados[k + 6], tinta = dados[k + 7];
  const pontos = [];
  let prof = 1;
  for (const t of [[dados[k], dados[k + 1], dados[k + 2]],
                   [dados[k + 3], dados[k + 4], dados[k + 5]]]) {
    const p = aplicar(mvp, [t[0], t[1], t[2], 1]);
    prof = Math.min(prof, Math.max(0.55, 1 - (p[3] - (d - RAIO)) / (2 * RAIO)));
    pontos.push([(p[0] / p[3] * 0.5 + 0.5) * LARG,
                 (1 - (p[1] / p[3] * 0.5 + 0.5)) * ALT]);
  }
  /* mesma curva do fragment shader, e a mesma largura do vertex shader */
  segs.push([pontos[0][0], pontos[0][1], pontos[1][0], pontos[1][1],
             (0.55 + 0.45 * peso) * GANHO * prof,
             FINA + (GROSSA - FINA) * Math.max(0, Math.min(1, peso)),
             tinta]);
}

process.stdout.write(JSON.stringify({
  larg: LARG, alt: ALT, segmentos: segs.length, raio: RAIO, dist: d,
  elementos: ELEMENTOS.map((e) => e["class"]), segs
}));
