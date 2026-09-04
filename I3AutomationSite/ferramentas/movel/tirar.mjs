// Captura a página inteira num aparelho, fatiada em tiras legíveis.
import { abrirChrome, fecharChrome, Sessao, pagina, avaliar } from "./cdp.mjs";
import { pathToFileURL } from "node:url";
import { resolve } from "node:path";
import { writeFileSync, mkdirSync } from "node:fs";

const [,, nomePag = "index", larguraS = "375", alturaS = "667", rotulo = ""] = process.argv;
const L = Number(larguraS), A = Number(alturaS);
const saida = resolve("ferramentas/movel/tiras");
mkdirSync(saida, { recursive: true });

const ch = await abrirChrome(9350);
const br = await Sessao.conectar(ch.browserWs);
const url = pathToFileURL(resolve("site", nomePag + ".html")).href;
const { s, targetId } = await pagina(br, { url, largura: L, altura: A, dpr: 2, movel: true });

// mata a intro para não cobrir a home
await avaliar(s, `(()=>{document.documentElement.classList.remove('intro-ativa'); const i=document.querySelector('.intro'); if(i) i.remove(); document.documentElement.style.scrollBehavior='auto'; return 1})()`);
await new Promise(r => setTimeout(r, 400));

const alturaTotal = await avaliar(s, `document.documentElement.scrollHeight`);
const tiras = Math.min(14, Math.ceil(alturaTotal / A));
console.log(`${nomePag} @${L}x${A} — altura total ${alturaTotal}px, ${tiras} tiras`);

for (let i = 0; i < tiras; i++) {
  const y = i * A;
  await avaliar(s, `window.scrollTo(0, ${y}); 1`);
  await new Promise(r => setTimeout(r, 650));
  const { data } = await s("Page.captureScreenshot", { format: "png", captureBeyondViewport: false });
  const arq = resolve(saida, `${rotulo || nomePag}-${L}-${String(i).padStart(2,"0")}.png`);
  writeFileSync(arq, Buffer.from(data, "base64"));
}
await br.enviar("Target.closeTarget", { targetId });
br.fechar(); fecharChrome(ch);
console.log("ok");
