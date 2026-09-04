// Mede a geometria de seletores escolhidos, num aparelho.
import { abrirChrome, fecharChrome, Sessao, pagina, avaliar } from "./cdp.mjs";
import { pathToFileURL } from "node:url";
import { resolve } from "node:path";

const [,, nomePag = "index", larguraS = "375", alturaS = "667", ...sel] = process.argv;
const L = Number(larguraS), A = Number(alturaS);
const ch = await abrirChrome(9360);
const br = await Sessao.conectar(ch.browserWs);
const url = pathToFileURL(resolve("site", nomePag + ".html")).href;
const { s, targetId } = await pagina(br, { url, largura: L, altura: A, dpr: 2, movel: true });
await avaliar(s, `(()=>{document.documentElement.classList.remove('intro-ativa'); const i=document.querySelector('.intro'); if(i) i.remove(); return 1})()`);
await new Promise(r => setTimeout(r, 500));

const seletores = sel.length ? sel : [".heroi", ".heroi__peca", ".braco", ".braco__tela", ".heroi__container", ".heroi__texto", ".heroi__rodape"];
const r = await avaliar(s, `(() => {
  const out = [];
  for (const q of ${JSON.stringify(seletores)}) {
    document.querySelectorAll(q).forEach((el, i) => {
      const b = el.getBoundingClientRect();
      const cs = getComputedStyle(el);
      out.push({ q: q + (i?"["+i+"]":""), x: Math.round(b.x), y: Math.round(b.y + window.scrollY), w: Math.round(b.width), h: Math.round(b.height),
        disp: cs.display, pos: cs.position, op: cs.opacity, vis: cs.visibility, ar: cs.aspectRatio, cls: el.className });
    });
  }
  return out;
})()`);
console.table(r);
console.log("scrollHeight", await avaliar(s, "document.documentElement.scrollHeight"));
await br.enviar("Target.closeTarget", { targetId });
br.fechar(); fecharChrome(ch);
