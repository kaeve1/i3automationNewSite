// uso: node ferramentas/movel/intro.mjs <larg> <alt> [rotulo]
//
// Fotografa a intro em instantes fixos da linha do tempo.
//
// DUAS ARMADILHAS, e as duas custaram uma captura em branco:
//
//   1. `getAnimations()` NAO LISTA animacao terminada sem `forwards`. A
//      abertura da tampa dura de 0,15s a 1,05s e tem `backwards` so -- meio
//      segundo depois da carga ela ja acabou, o objeto sumiu e o `transform`
//      voltou a `none`. Parecia defeito e era o contrario: era o fim correto
//      do gesto. Por isso as animacoes sao PAUSADAS por CSS injetado ANTES da
//      carga, e nao pausadas depois.
//   2. O modulo 5 do main.js remove a intro do DOM em 3,25s. Com o relogio
//      congelado o tempo real continua andando, e a peca sumia no meio da
//      sessao. O `setTimeout` longo e neutralizado no mesmo script.
//
// Com as duas resolvidas, `Animation.currentTime` da quadros deterministicos:
// a mesma execucao devolve as mesmas imagens, que e o que serve para comparar
// antes e depois.
import { abrirChrome, fecharChrome, Sessao, pagina, avaliar } from "./cdp.mjs";
import { pathToFileURL } from "node:url";
import { resolve } from "node:path";
import { writeFileSync, mkdirSync } from "node:fs";

const [, , LS = "1440", AS = "900", rotulo = "intro"] = process.argv;
const L = Number(LS), A = Number(AS);
const saida = resolve("ferramentas/movel/tiras");
mkdirSync(saida, { recursive: true });

const MARCOS = [0, 500, 1050, 1400, 1560, 2000, 2740, 3100, 3500, 3950];

const PRE = `
  (function () {
    var st = window.setTimeout;
    window.setTimeout = function (f, ms) { return st(f, ms > 400 ? 9e6 : ms); };
    document.addEventListener('DOMContentLoaded', function () {
      var s = document.createElement('style');
      s.textContent = '.intro, .intro * { animation-play-state: paused !important; }';
      document.head.appendChild(s);
    });
  })();
`;

const ch = await abrirChrome(9376);
const br = await Sessao.conectar(ch.browserWs);
const { s } = await pagina(br, { url: "about:blank", largura: L, altura: A, dpr: 1, movel: L < 900 });
await s("Page.addScriptToEvaluateOnNewDocument", { source: PRE });
await s("Page.navigate", { url: pathToFileURL(resolve("site", "index.html")).href });
await s("Page.bringToFront");
await new Promise((r) => setTimeout(r, 1400));

const n = await avaliar(s, `(()=>{
  const i=document.querySelector('.intro');
  if(!i) return 0;
  window.__anim=[...document.getAnimations()].filter(a=>{
    const t=a.effect&&a.effect.target; return t&&(t===i||i.contains(t));
  });
  return window.__anim.length})()`);
console.log(`${rotulo} @ ${L}x${A} — ${n} animacoes congeladas`);
if (!n) { console.log("  a intro nao esta presente"); await fecharChrome(ch); process.exit(1); }

for (const t of MARCOS) {
  await avaliar(s, `(()=>{window.__anim.forEach(a=>{try{a.currentTime=${t}}catch(e){}});return 1})()`);
  await new Promise((r) => setTimeout(r, 140));
  const d = JSON.parse(await avaliar(s, `(()=>{
    const q=x=>document.querySelector(x), cs=e=>e?getComputedStyle(e):null;
    const tp=cs(q('.intro__tampa')), ch=cs(q('.intro__chao'));
    const pt=cs(q('.intro__painel--topo')), nb=cs(q('.intro__nb'));
    const mat=x=>{const m=(x||'').match(/matrix3?d?\\(([^)]*)\\)/); return m?m[1].split(',').slice(0,6).map(v=>(+v).toFixed(2)).join(','):x;};
    return JSON.stringify({
      chao: ch?(+ch.opacity).toFixed(2):'-',
      nb: nb?(+nb.opacity).toFixed(2):'-',
      tampa: tp?mat(tp.transform):'-',
      painel: pt?mat(pt.transform):'-'})})()`));
  console.log(`  t=${String(t).padStart(4)}ms  chao ${d.chao}  nb ${d.nb}  painel[${d.painel}]  tampa[${d.tampa}]`);
  const { data } = await s("Page.captureScreenshot", { format: "png" });
  writeFileSync(resolve(saida, `${rotulo}-${String(t).padStart(4, "0")}.png`),
                Buffer.from(data, "base64"));
}
await fecharChrome(ch);
