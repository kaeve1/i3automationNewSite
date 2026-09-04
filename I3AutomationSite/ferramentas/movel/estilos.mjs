// uso: node ferramentas/movel/estilos.mjs <pagina> <arquivo-de-saida> [larg] [alt]
//
// Despeja o estilo COMPUTADO de cada elemento da pagina. Comparar dois
// despejos diz exatamente qual elemento mudou e em qual propriedade -- o que
// um diff de imagem nao diz, e o que um screenshot nem sempre consegue tirar
// (a cena da cobertura estoura o timeout de captura neste ambiente).
import { abrirChrome, fecharChrome, Sessao, pagina, avaliar } from "./cdp.mjs";
import { pathToFileURL } from "node:url";
import { resolve } from "node:path";
import { writeFileSync } from "node:fs";

const [, , pag = "capabilities", saida = "_estilos.json",
       LS = "1440", AS = "900"] = process.argv;

const PROPS = ["display", "position", "width", "height", "margin", "padding",
               "color", "background-color", "background-image", "border",
               "font-size", "font-weight", "line-height", "letter-spacing",
               "opacity", "transform", "grid-template-columns", "gap",
               "flex-direction", "align-items", "justify-content", "z-index",
               "aspect-ratio", "clip-path", "overflow", "max-width", "min-height"];

const ch = await abrirChrome(9404);
const br = await Sessao.conectar(ch.browserWs);
const { s } = await pagina(br, {
  url: pathToFileURL(resolve("site", pag + ".html")).href,
  largura: Number(LS), altura: Number(AS), dpr: 1, movel: Number(LS) < 900,
});
await new Promise((r) => setTimeout(r, 1400));
await avaliar(s, `(()=>{document.documentElement.classList.remove('intro-ativa');
  const i=document.querySelector('.intro'); if(i) i.remove(); return 1})()`);
await new Promise((r) => setTimeout(r, 400));

const dump = await avaliar(s, `(()=>{
  const P=${JSON.stringify(PROPS)}, o={};
  let n=0;
  document.querySelectorAll('body *').forEach(e=>{
    const cs=getComputedStyle(e);
    const r=e.getBoundingClientRect();
    const chave=(e.tagName+'.'+(e.className.baseVal||e.className||'')+'#'+(n++)).slice(0,90);
    o[chave]=P.map(p=>cs.getPropertyValue(p)).join('|')
      +'||'+[r.width,r.height].map(v=>Math.round(v)).join('x');
  });
  return JSON.stringify(o)})()`);
writeFileSync(resolve("ferramentas/movel", saida), dump);
console.log(`${pag}: ${Object.keys(JSON.parse(dump)).length} elementos -> ${saida}`);
await fecharChrome(ch);
