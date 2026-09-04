// uso: node ferramentas/movel/estilos-todas.mjs <sufixo> [larg] [alt]
// Despeja o estilo computado das dez paginas de uma vez. Ver estilos.mjs.
import { abrirChrome, fecharChrome, Sessao, pagina, avaliar } from "./cdp.mjs";
import { pathToFileURL } from "node:url";
import { resolve } from "node:path";
import { writeFileSync } from "node:fs";

const PAGS = ["index","who-we-are","capabilities","past-performance","services",
              "gallery","contact","404","privacy-policy","terms-and-conditions"];
const [, , suf = "x", LS = "1440", AS = "900"] = process.argv;
const PROPS = ["display","position","width","height","margin","padding","color",
  "background-color","background-image","border","font-size","font-weight",
  "line-height","letter-spacing","opacity","transform","grid-template-columns",
  "gap","flex-direction","align-items","justify-content","z-index",
  "aspect-ratio","clip-path","overflow","max-width","min-height"];

const ch = await abrirChrome(9406);
const br = await Sessao.conectar(ch.browserWs);
const tudo = {};
for (const p of PAGS) {
  const { s } = await pagina(br, { url: pathToFileURL(resolve("site", p + ".html")).href,
    largura: Number(LS), altura: Number(AS), dpr: 1, movel: Number(LS) < 900 });
  await new Promise((r) => setTimeout(r, 1300));
  await avaliar(s, `(()=>{document.documentElement.classList.remove('intro-ativa');
    const i=document.querySelector('.intro'); if(i) i.remove(); return 1})()`);
  await new Promise((r) => setTimeout(r, 350));
  tudo[p] = JSON.parse(await avaliar(s, `(()=>{
    const P=${JSON.stringify(PROPS)}, o={}; let n=0;
    document.querySelectorAll('body *').forEach(e=>{
      const cs=getComputedStyle(e), r=e.getBoundingClientRect();
      o[(e.tagName+'.'+(e.className.baseVal||e.className||'')+'#'+(n++)).slice(0,90)]=
        P.map(x=>cs.getPropertyValue(x)).join('|')+'||'+Math.round(r.width)+'x'+Math.round(r.height);
    });
    return JSON.stringify(o)})()`));
  process.stdout.write(".");
}
writeFileSync(resolve("ferramentas/movel", "_est-" + suf + "-" + LS + ".json"), JSON.stringify(tudo));
console.log(`\n${suf}@${LS}: ${Object.values(tudo).reduce((a,o)=>a+Object.keys(o).length,0)} elementos`);
await fecharChrome(ch);
