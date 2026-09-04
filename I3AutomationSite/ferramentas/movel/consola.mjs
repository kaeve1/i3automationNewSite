// uso: node ferramentas/movel/consola.mjs [larg] [alt]
//
// Erro de console e requisicao falhada nas dez paginas. `varredura.py` confere
// referencia por TEXTO no HTML; isto confere o que o navegador de fato tentou
// buscar e o que o JS de fato fez -- um `src` montado em runtime, uma fonte
// que nao existe no disco, uma excecao dentro de um modulo. Sao dois erros
// diferentes e nenhum dos dois pega o do outro.
import { abrirChrome, fecharChrome, Sessao, pagina, avaliar } from "./cdp.mjs";
import { pathToFileURL } from "node:url";
import { resolve } from "node:path";

const PAGS = ["index", "who-we-are", "capabilities", "past-performance",
              "services", "gallery", "contact", "404",
              "privacy-policy", "terms-and-conditions"];
const L = Number(process.argv[2] || 1440), A = Number(process.argv[3] || 900);

const ch = await abrirChrome(9392);
const br = await Sessao.conectar(ch.browserWs);
console.log(`CONSOLA @ ${L}x${A}\n`);
let total = 0;

for (const p of PAGS) {
  const { s } = await pagina(br, { url: "about:blank", largura: L, altura: A, dpr: 1, movel: L < 900 });
  // captura ANTES da navegacao, senao os erros da carga se perdem
  await s("Page.addScriptToEvaluateOnNewDocument", {
    source: `window.__err = [];
      addEventListener('error', function (e) {
        window.__err.push((e.target && e.target.src)
          ? ('recurso falhou: ' + String(e.target.src).split('/').slice(-2).join('/'))
          : ('js: ' + (e.message || '')));
      }, true);
      addEventListener('unhandledrejection', function (e) {
        window.__err.push('promessa: ' + e.reason);
      });`,
  });
  await s("Page.navigate", { url: pathToFileURL(resolve("site", p + ".html")).href });
  await new Promise((r) => setTimeout(r, 2200));
  // rola a pagina inteira: lazy-load e IntersectionObserver so falham depois
  await avaliar(s, `(async()=>{const h=document.documentElement.scrollHeight;
    for(let y=0;y<h;y+=600){window.scrollTo(0,y);await new Promise(r=>setTimeout(r,45));}
    window.scrollTo(0,0); return 1})()`);
  await new Promise((r) => setTimeout(r, 900));
  const err = JSON.parse(await avaliar(s, `JSON.stringify(window.__err || [])`));
  const unicos = [...new Set(err)];
  total += unicos.length;
  console.log(`${p.padEnd(22)} ${unicos.length ? "" : "ok"}`);
  unicos.forEach((e) => console.log(`   ${e}`));
}
console.log(`\n${total} erro(s)`);
await fecharChrome(ch);
