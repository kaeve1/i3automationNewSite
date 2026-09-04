// uso: node ferramentas/movel/progresso.mjs <num> <larg> <alt>
//
// Onde a animacao acontece EM RELACAO ao que o visitante ve.
//
// Uma revelacao so e revelacao se ela roda enquanto a figura esta na tela. Se
// `--p` ainda vale 0 quando metade da figura ja apareceu, o visitante ve um
// buraco branco; se ele ja vale 1 antes de a figura entrar, nao ha animacao
// nenhuma. Esta sonda cruza as duas grandezas.
import { abrirChrome, fecharChrome, Sessao, pagina, avaliar } from "./cdp.mjs";
import { pathToFileURL } from "node:url";
import { resolve } from "node:path";

const [, , num = "13", LS = "1440", AS = "700"] = process.argv;
const L = Number(LS), A = Number(AS);

const ch = await abrirChrome(9358);
const br = await Sessao.conectar(ch.browserWs);
const url = pathToFileURL(resolve("site", "gallery.html")).href;
const { s } = await pagina(br, { url, largura: L, altura: A, dpr: 1, movel: false });
await s("Page.bringToFront");
await avaliar(s, `(()=>{const a=document.getElementById('aviso-armazenamento'); if(a) a.remove();
  document.documentElement.style.scrollBehavior='auto'; return 1})()`);
await new Promise((r) => setTimeout(r, 500));

const topo = await avaliar(s, `(()=>{const f=[...document.querySelectorAll('.galeria__figura')]
  .find(e=>e.querySelector('.galeria__num').textContent.trim()==='${num}');
  return Math.round(f.getBoundingClientRect().top + scrollY)})()`);

console.log(`figura #${num} @ ${L}x${A} — topo do documento em ${topo}px\n`);
console.log("scrollY   top    altura  visivel   --p     opacity  clip-top");
for (let y = topo - A; y <= topo + A * 1.4; y += Math.round(A / 12)) {
  await avaliar(s, `window.scrollTo(0, ${Math.max(0, y)}); 1`);
  await new Promise((r) => setTimeout(r, 45));
  const j = await avaliar(s, `(()=>{
    const f=[...document.querySelectorAll('.galeria__figura')]
      .find(e=>e.querySelector('.galeria__num').textContent.trim()==='${num}');
    const r=f.getBoundingClientRect(), vh=innerHeight;
    const vis=Math.max(0, Math.min(r.bottom,vh)-Math.max(r.top,0));
    const cs=getComputedStyle(f);
    return JSON.stringify({top:Math.round(r.top),h:Math.round(r.height),
      vis:Math.round(100*vis/r.height), p:cs.getPropertyValue('--p').trim(),
      op:(+cs.opacity).toFixed(2),
      clip:getComputedStyle(f.querySelector('.galeria__item')).clipPath})})()`);
  const d = JSON.parse(j);
  const marca = d.vis > 15 && (+d.op) < 0.15 ? "  <-- visivel e APAGADA" : "";
  console.log(
    `${String(Math.max(0, y)).padStart(7)} ${String(d.top).padStart(6)} ${String(d.h).padStart(7)} ` +
    `${String(d.vis).padStart(6)}% ${d.p.padStart(7)} ${d.op.padStart(8)}  ${d.clip}${marca}`
  );
}
await fecharChrome(ch);
