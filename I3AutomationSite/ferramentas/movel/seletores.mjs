// uso: node ferramentas/movel/seletores.mjs
//
// Seletor de CLASSE que existe no CSS e nao casa com NADA em nenhuma das dez
// paginas. E o inverso de `varredura.py`: la sao arquivos sem consumidor, aqui
// e regra sem consumidor.
//
// POR QUE NO NAVEGADOR e nao por regex: `querySelectorAll` responde a pergunta
// de verdade -- "isto casa?" --, incluindo combinadores, `:has()`, pseudo e
// atributo. Um regex sobre o CSS acha o nome da classe; nao acha se a regra
// inteira alcanca alguem.
//
// O QUE ELE NAO ACUSA, de proposito: seletor que so casa em ESTADO (`:hover`,
// `[open]`, `.is-*`, `[data-*]`) e seletor de pseudo-elemento. O estado nao
// existe no DOM em repouso, e marcar isso como morto mandaria apagar
// exatamente as regras de interacao.
import { abrirChrome, fecharChrome, Sessao, pagina, avaliar } from "./cdp.mjs";
import { pathToFileURL } from "node:url";
import { resolve } from "node:path";
import { readFileSync } from "node:fs";

const PAGS = ["index", "who-we-are", "capabilities", "past-performance",
              "services", "gallery", "contact", "404",
              "privacy-policy", "terms-and-conditions"];

const css = readFileSync(resolve("site/css/style.css"), "utf8")
  .replace(/\/\*[\s\S]*?\*\//g, "");

// so as regras de classe; nada de @media/@keyframes/@supports
const sels = new Set();
for (const m of css.matchAll(/(^|[}])\s*([^@{}][^{}]*)\{/g)) {
  for (let s of m[2].split(",")) {
    s = s.trim().replace(/\s+/g, " ");
    if (!s.startsWith(".")) continue;
    if (/:hover|:focus|:active|:target|\[open\]|\.is-|\[data-|::/.test(s)) continue;
    if (s.includes("%")) continue;
    sels.add(s);
  }
}

const ch = await abrirChrome(9394);
const br = await Sessao.conectar(ch.browserWs);
const lista = [...sels];
const usado = new Set();
for (const p of PAGS) {
  const { s } = await pagina(br, {
    url: pathToFileURL(resolve("site", p + ".html")).href,
    largura: 1440, altura: 900, dpr: 1, movel: false,
  });
  await new Promise((r) => setTimeout(r, 500));
  const hit = JSON.parse(await avaliar(s, `(()=>{const L=${JSON.stringify(lista)};
    const o=[]; for(const s of L){ try{ if(document.querySelector(s)) o.push(s);}catch(e){o.push(s);} }
    return JSON.stringify(o)})()`));
  hit.forEach((h) => usado.add(h));
}
const mortos = lista.filter((s) => !usado.has(s));
console.log(`${lista.length} seletores de classe · ${usado.size} vivos · ${mortos.length} sem consumidor\n`);
mortos.sort().forEach((s) => console.log("   " + s));
await fecharChrome(ch);
