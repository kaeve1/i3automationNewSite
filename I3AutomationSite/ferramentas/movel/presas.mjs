// uso: node ferramentas/movel/presas.mjs
//
// As cenas presas continuam varrendo 0->1 depois do limiar? Este e o teste de
// nao-regressao do conserto de 2026-08-27 em main.js.
import { abrirChrome, fecharChrome, Sessao, pagina, avaliar } from "./cdp.mjs";
import { pathToFileURL } from "node:url";
import { resolve } from "node:path";

const ALVOS = [
  ["index", ".filme"],
  ["index", ".unidade"],
  ["who-we-are", ".secao--presa"],
  ["capabilities", ".cobertura"],
  ["gallery", ".galeria__mosaico"],
];
const L = 1440, A = 700;

const ch = await abrirChrome(9362);
const br = await Sessao.conectar(ch.browserWs);
console.log(`janela ${L}x${A}\n`);
console.log("pagina           seletor              altura  curso/vh   p min   p max   veredito");
for (const [pag, sel] of ALVOS) {
  const url = pathToFileURL(resolve("site", pag + ".html")).href;
  const { s } = await pagina(br, { url, largura: L, altura: A, dpr: 1, movel: false });
  await s("Page.bringToFront");
  await avaliar(s, `(()=>{document.documentElement.classList.remove('intro-ativa');
    const i=document.querySelector('.intro'); if(i) i.remove();
    const a=document.getElementById('aviso-armazenamento'); if(a) a.remove();
    document.documentElement.style.scrollBehavior='auto'; return 1})()`);
  await new Promise((r) => setTimeout(r, 500));

  const info = JSON.parse(await avaliar(s, `(()=>{const e=document.querySelector('${sel}');
    if(!e) return 'null';
    const r=e.getBoundingClientRect();
    return JSON.stringify({h:Math.round(r.height), y:Math.round(r.top+scrollY)})})()`));
  if (!info) { console.log(`${pag.padEnd(16)} ${sel.padEnd(20)} AUSENTE`); continue; }

  let min = 9, max = -9;
  for (let y = info.y - A; y <= info.y + info.h + A; y += Math.round(A / 8)) {
    await avaliar(s, `window.scrollTo(0, ${Math.max(0, y)}); 1`);
    await new Promise((r) => setTimeout(r, 40));
    const p = parseFloat(await avaliar(s,
      `parseFloat(getComputedStyle(document.querySelector('${sel}')).getPropertyValue('--p'))`));
    if (!isNaN(p)) { min = Math.min(min, p); max = Math.max(max, p); }
  }
  const curso = (info.h - A) / A;
  const ok = min <= 0.02 && max >= 0.98;
  console.log(`${pag.padEnd(16)} ${sel.padEnd(20)} ${String(info.h).padStart(6)} ${curso.toFixed(3).padStart(9)}  ${min.toFixed(3).padStart(6)}  ${max.toFixed(3).padStart(6)}   ${ok ? "ok" : "<<< REGREDIU"}`);
}
await fecharChrome(ch);
