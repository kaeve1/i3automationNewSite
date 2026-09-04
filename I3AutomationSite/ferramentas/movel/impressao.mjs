// uso: node ferramentas/movel/impressao.mjs <antes|depois>
//
// Impressao digital de RENDER das dez paginas, em duas larguras. Serve para
// provar que uma mudanca de CSS nao mexeu em pixel nenhum -- que e a unica
// forma honesta de mover regra morta sem apostar.
//
// Nao e screenshot da janela: e a pagina INTEIRA (`captureBeyondViewport`),
// senao a comparacao cobre so a primeira dobra.
import { abrirChrome, fecharChrome, Sessao, pagina, avaliar } from "./cdp.mjs";
import { pathToFileURL } from "node:url";
import { resolve } from "node:path";
import { writeFileSync, readFileSync, existsSync } from "node:fs";
import { createHash } from "node:crypto";

const PAGS = ["index", "who-we-are", "capabilities", "past-performance",
              "services", "gallery", "contact", "404",
              "privacy-policy", "terms-and-conditions"];
const fase = process.argv[2] || "antes";
const arq = resolve("ferramentas/movel/_impressao-" + fase + ".json");

const ch = await abrirChrome(9398);
const br = await Sessao.conectar(ch.browserWs);
const out = {};

for (const [larg, alt] of [[1440, 900], [390, 844]]) {
  for (const p of PAGS) {
    const { s } = await pagina(br, {
      url: pathToFileURL(resolve("site", p + ".html")).href,
      largura: larg, altura: alt, dpr: 1, movel: larg < 900,
    });
    await new Promise((r) => setTimeout(r, 1200));
    // a intro e as pecas animadas mudam a cada quadro: fora da comparacao
    await avaliar(s, `(()=>{document.documentElement.classList.remove('intro-ativa');
      const i=document.querySelector('.intro'); if(i) i.remove();
      document.querySelectorAll('canvas, video').forEach(e=>e.style.visibility='hidden');
      document.getAnimations().forEach(a=>{try{a.finish()}catch(e){}});
      return 1})()`);
    await new Promise((r) => setTimeout(r, 500));
    const { data } = await s("Page.captureScreenshot", {
      format: "png", captureBeyondViewport: true,
    });
    out[`${p}@${larg}`] = createHash("sha1").update(data).digest("hex").slice(0, 16);
  }
}
writeFileSync(arq, JSON.stringify(out, null, 1));
console.log(`${fase}: ${Object.keys(out).length} renders`);

const outro = resolve("ferramentas/movel/_impressao-" +
                      (fase === "antes" ? "depois" : "antes") + ".json");
if (existsSync(outro)) {
  const o = JSON.parse(readFileSync(outro, "utf8"));
  const dif = Object.keys(out).filter((k) => o[k] && o[k] !== out[k]);
  console.log(dif.length ? "\nDIFEREM:\n   " + dif.join("\n   ")
                         : "\nIDENTICAS em todas as dez paginas, nas duas larguras.");
}
await fecharChrome(ch);
