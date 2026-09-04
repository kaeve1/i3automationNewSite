// Fotografa a janela com um seletor no topo — para inspecionar um componente.
import { abrirChrome, fecharChrome, Sessao, pagina, avaliar } from "./cdp.mjs";
import { pathToFileURL } from "node:url";
import { resolve } from "node:path";
import { writeFileSync, mkdirSync } from "node:fs";

const [,, nomePag, seletor, larguraS = "375", alturaS = "667", desloc = "0", rotulo = "foto"] = process.argv;
const L = Number(larguraS), A = Number(alturaS);
mkdirSync(resolve("ferramentas/movel/tiras"), { recursive: true });
const ch = await abrirChrome(9380);
const br = await Sessao.conectar(ch.browserWs);
const { s, targetId } = await pagina(br, { url: pathToFileURL(resolve("site", nomePag + ".html")).href, largura: L, altura: A, dpr: 2, movel: true });
await avaliar(s, `(()=>{document.documentElement.classList.remove('intro-ativa');const i=document.querySelector('.intro');if(i)i.remove();document.documentElement.style.scrollBehavior='auto';return 1})()`);
await new Promise(r => setTimeout(r, 500));
const y = await avaliar(s, `(()=>{const e=document.querySelector(${JSON.stringify(seletor)}); if(!e) return -1; const b=e.getBoundingClientRect(); return Math.max(0, Math.round(b.top + window.scrollY + ${Number(desloc)}));})()`);
if (y < 0) { console.log("seletor não achado: " + seletor); }
else {
  await avaliar(s, `window.scrollTo(0, ${y}); 1`);
  await new Promise(r => setTimeout(r, 800));
  const { data } = await s("Page.captureScreenshot", { format: "png" });
  const arq = resolve("ferramentas/movel/tiras", `${rotulo}-${L}.png`);
  writeFileSync(arq, Buffer.from(data, "base64"));
  console.log("y=" + y + " → " + arq);
}
await br.enviar("Target.closeTarget", { targetId });
br.fechar(); fecharChrome(ch);
