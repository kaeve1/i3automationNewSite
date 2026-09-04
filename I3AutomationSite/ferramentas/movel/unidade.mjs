// uso: node ferramentas/movel/unidade.mjs <indice> <larg> <alt>
//
// O estado de UMA unidade da home ao longo da rolagem: progresso, abertura,
// a classe `is-aberta`, e o que cada camada esta de fato mostrando. Serve
// para ver o mecanismo onde ele nao aparece no screenshot -- no celular, em
// que tudo e estatico e a unica coisa que se move e um `visibility` que
// estala.
import { abrirChrome, fecharChrome, Sessao, pagina, avaliar } from "./cdp.mjs";
import { pathToFileURL } from "node:url";
import { resolve } from "node:path";

const [, , idxS = "0", LS = "390", AS = "844"] = process.argv;
const idx = Number(idxS), L = Number(LS), A = Number(AS);

const ch = await abrirChrome(9372);
const br = await Sessao.conectar(ch.browserWs);
const { s } = await pagina(br, {
  url: pathToFileURL(resolve("site", "index.html")).href,
  largura: L, altura: A, dpr: 1, movel: L < 900,
});
await s("Page.bringToFront");
await avaliar(s, `(()=>{document.documentElement.classList.remove('intro-ativa');
  const i=document.querySelector('.intro'); if(i) i.remove();
  const a=document.getElementById('aviso-armazenamento'); if(a) a.remove();
  document.documentElement.style.scrollBehavior='auto'; return 1})()`);
await new Promise((r) => setTimeout(r, 700));

const info = JSON.parse(await avaliar(s, `(()=>{
  const u=document.querySelectorAll('.unidade')[${idx}];
  const r=u.getBoundingClientRect();
  return JSON.stringify({y:Math.round(r.top+scrollY), h:Math.round(r.height)})})()`));
console.log(`unidade[${idx}] @ ${L}x${A} — topo ${info.y}, altura ${info.h}\n`);
console.log("scrollY   --p   aberta  rodape   janela clip                    filhos da coluna");

for (let y = info.y - A; y <= info.y + info.h + A * 0.3; y += Math.round(A / 7)) {
  await avaliar(s, `window.scrollTo(0, ${Math.max(0, y)}); 1`);
  await new Promise((r) => setTimeout(r, 60));
  const j = await avaliar(s, `(()=>{
    const u=document.querySelectorAll('.unidade')[${idx}];
    const cs=getComputedStyle(u);
    const col=u.querySelector('.unidade__coluna');
    const rod=u.querySelector('.unidade__rodape');
    const jan=u.querySelector('.unidade__janela');
    const g=e=>{const c=getComputedStyle(e); return (+c.opacity).toFixed(2)+'/'+c.visibility.slice(0,3)};
    return JSON.stringify({
      p:cs.getPropertyValue('--p').trim()||'-',
      abre:(+cs.getPropertyValue('--abre')||0).toFixed(3),
      ab:u.classList.contains('is-aberta')?'SIM':'nao',
      col:g(col), rod:g(rod),
      filhos:[...col.children].map(e=>(+getComputedStyle(e).opacity).toFixed(2)).join(' '),
      clip:getComputedStyle(jan).clipPath.replace(/px/g,'').slice(0,34)})})()`);
  const d = JSON.parse(j);
  console.log(`${String(Math.max(0, y)).padStart(7)} ${d.p.padStart(6)}  ${d.ab.padStart(5)}  ${d.rod.padStart(9)}  ${d.clip.padEnd(30)} ${d.filhos}`);
}
await fecharChrome(ch);
