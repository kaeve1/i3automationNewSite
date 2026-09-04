/* Prévia do braço FORA do navegador.

   Por que existe: a geometria de js/braco.js é gerada por código, e a única
   pergunta que importa — "isto se parece com um braço de 6 eixos?" — não se
   responde lendo o arquivo. Este harness carrega o MESMO módulo, roda a MESMA
   cinemática e a MESMA matriz MVP, e cospe os segmentos já projetados em JSON;
   ferramentas/previa_braco.py desenha o PNG.

   Não duplica nada: o código de produção é lido do disco e avaliado. Se a
   geometria mudar, a prévia muda junto — que é o ponto.

   Uso:  node ferramentas/previa_braco.js <giro> <inclinacao> <fase> > saida.json
*/
"use strict";
const fs = require("fs");
const path = require("path");
const vm = require("vm");

const ARQ = path.join(__dirname, "..", "site", "js", "braco.js");
/* gl.js tem de ser avaliado ANTES: desde a extracao do nucleo, braco.js pega
   matriz, parser de token e compilacao de shader de globalThis.I3GL. No
   navegador quem garante a ordem e o `defer` na ordem do documento; aqui e
   esta concatenacao. Sem ela o modulo lanca no primeiro alias e a previa
   morre calada. */
const NUCLEO = fs.readFileSync(
  path.join(__dirname, "..", "site", "js", "gl.js"), "utf8");
let fonte = fs.readFileSync(ARQ, "utf8");

/* Expõe os internos SEM tocar no arquivo de produção: o módulo é uma IIFE,
   então basta injetar a exportação imediatamente antes do fecho dela. */
const FECHO = "})();";
const i = fonte.lastIndexOf(FECHO);
if (i < 0) throw new Error("não achei o fecho da IIFE em braco.js");
fonte = fonte.slice(0, i) +
  "globalThis.__braco = { construir, mult, transladar, giroY, giroZ, " +
  "perspectiva, olhar, PIVO, PIVO_DEDO, enquadrar, MIRA, FOV, pose, CICLO };\n" +
  fonte.slice(i);

/* Stubs mínimos: o módulo só toca em matchMedia e no DOM depois de iniciar,
   e iniciar() não acha nenhum [data-braco] aqui. */
const contexto = {
  console,
  globalThis: null,
  window: {
    matchMedia: () => ({ matches: false, addEventListener() {} }),
    requestAnimationFrame() {},
    WebGL2RenderingContext: null
  },
  document: {
    readyState: "complete",
    querySelectorAll: () => [],
    addEventListener() {}
  }
};
contexto.globalThis = contexto;
vm.createContext(contexto);
vm.runInContext(NUCLEO, contexto);   /* publica contexto.I3GL */
vm.runInContext(fonte, contexto);
const B = contexto.__braco;

/* ---- mesma pose e mesma câmera do quadro real ---- */
const TAU = Math.PI * 2;
const giro = parseFloat(process.argv[2] ?? "2.40");
const incl = parseFloat(process.argv[3] ?? "0.16");
const fase = parseFloat(process.argv[4] ?? "0.22");
const LARG = parseFloat(process.argv[5] ?? "430");
const ALT = parseFloat(process.argv[6] ?? "584");
/* distancia e altura do alvo entram por argv para permitir varredura de
   enquadramento sem editar o arquivo de producao; os padroes sao os valores
   que estao em braco.js, entao rodar sem argumento mede o que o site faz. */
const DIST = parseFloat(process.argv[7] ?? "0") || null;
const ALVO_Y = parseFloat(process.argv[8] ?? "0") || null;

/* pose() NAO e reimplementada aqui: e a de site/js/braco.js, exposta acima.
   A copia que existia neste arquivo ja tinha divergido da original em uma
   sessao -- previa que diverge do original mede um site que nao existe.
   `fase` entra como fracao de 0..1 e vira tempo pelo ciclo real. */
const pose = (f) => B.pose(f * B.CICLO);

const cena = B.construir();
const dados = cena.segmentos;
const M = pose(fase);

/* A distancia sai da MESMA funcao que o site usa. DIST so existe para
   comparar contra um valor fixo; sem ele, isto mede o que o navegador faz. */
const mira = ALVO_Y || B.MIRA;
/* mesmo criterio do site: o maior de SEIS fases, para a distancia depender
   so do angulo e a peca nao pulsar de tamanho durante o ciclo */
let dAuto = 0;
for (let k = 0; k < 6; k++) {
  dAuto = Math.max(dAuto, B.enquadrar(cena.cantos, pose(k / 6), giro, incl, LARG / ALT));
}
const d = DIST || dAuto;
const olho = [
  Math.sin(giro) * Math.cos(incl) * d,
  mira + Math.sin(incl) * d,
  Math.cos(giro) * Math.cos(incl) * d
];
const mvp = B.mult(B.perspectiva(B.FOV, LARG / ALT, 1, 120),
                   B.olhar(olho, [0, mira, 0], [0, 1, 0]));

function aplicar(M, v) {
  const o = [0, 0, 0, 0];
  for (let r = 0; r < 4; r++) {
    o[r] = M[0 * 4 + r] * v[0] + M[1 * 4 + r] * v[1] +
           M[2 * 4 + r] * v[2] + M[3 * 4 + r] * v[3];
  }
  return o;
}

/* Raio da peca em torno do ponto visado -- mesma conta do site, e o que
   ancora a rampa de profundidade na distancia da camera. */
let RAIO = 1;
for (let e = 0; e < cena.cantos.length; e++) {
  const pts = cena.cantos[e], Me = M[e];
  if (!pts || !Me) continue;
  for (let i = 0; i < 8; i++) {
    const q = pts[i];
    const x = Me[0] * q[0] + Me[4] * q[1] + Me[8] * q[2] + Me[12];
    const y = Me[1] * q[0] + Me[5] * q[1] + Me[9] * q[2] + Me[13] - mira;
    const z = Me[2] * q[0] + Me[6] * q[1] + Me[10] * q[2] + Me[14];
    RAIO = Math.max(RAIO, Math.hypot(x, y, z));
  }
}

/* Larguras iguais as dos tokens do CSS (--braco-linha-fina/-grossa). */
const FINA = 0.9, GROSSA = 1.8;

const segs = [];
for (let k = 0; k < dados.length; k += 8) {
  const elo = Math.round(dados[k + 7]);
  const peso = dados[k + 6];
  const pontos = [];
  let prof = 1;
  for (const t of [[dados[k], dados[k + 1], dados[k + 2]],
                   [dados[k + 3], dados[k + 4], dados[k + 5]]]) {
    const mundo = aplicar(M[elo], [t[0], t[1], t[2], 1]);
    const p = aplicar(mvp, mundo);
    prof = Math.min(prof, Math.max(0.55, 1 - (p[3] - (d - RAIO)) / (2 * RAIO)));
    pontos.push([(p[0] / p[3] * 0.5 + 0.5) * LARG,
                 (1 - (p[1] / p[3] * 0.5 + 0.5)) * ALT]);
  }
  /* mesma curva do fragment shader, e a mesma largura do vertex shader */
  segs.push([pontos[0][0], pontos[0][1], pontos[1][0], pontos[1][1],
             (0.55 + 0.45 * peso) * 0.92 * prof,
             FINA + (GROSSA - FINA) * Math.max(0, Math.min(1, peso))]);
}
process.stdout.write(JSON.stringify({
  larg: LARG, alt: ALT, segmentos: segs.length, raio: RAIO,
  dist: d, segs
}));
