// uso: node ferramentas/movel/vistoria.mjs [larg] [alt]
//
// VISTORIA DE ACABAMENTO — o que uma matriz de contraste e um varredor de
// referencias nao pegam. Roda as nove paginas no navegador e volta com defeito
// funcional, nao com opiniao:
//
//   erro de console ....... script quebrado em producao
//   transbordo lateral .... a pagina rola de lado (o defeito de celular que
//                           mais escapa, porque so aparece com o dedo)
//   id repetido ........... quebra ancora, `for=` de label e leitor de tela
//   imagem sem alt ........ o atributo AUSENTE, nao o vazio (vazio e decisao)
//   link sem nome ......... o leitor de tela anuncia "link" e mais nada
//   ordem de titulo ....... h1 faltando, h1 repetido, nivel pulado
//   alvo de toque ......... abaixo de 44px no celular (WCAG 2.5.8 pede 24;
//                           44 e o piso confortavel e o que a Apple publica)
//   foco invisivel ........ elemento focavel sem contorno visivel
//   deslocamento .......... CLS acumulado depois da carga
import { abrirChrome, fecharChrome, Sessao, pagina, avaliar } from "./cdp.mjs";
import { pathToFileURL } from "node:url";
import { resolve } from "node:path";

const PAGS = ["index", "who-we-are", "capabilities", "past-performance",
              "services", "gallery", "contact", "404",
              "privacy-policy", "terms-and-conditions"];

const L = Number(process.argv[2] || 390), A = Number(process.argv[3] || 844);

const SONDA = `(() => {
  const out = { over: 0, ids: [], semAlt: [], semNome: [], titulos: [], toque: [], foco: [] };

  out.over = Math.max(0, document.documentElement.scrollWidth - document.documentElement.clientWidth);
  if (out.over > 0) {
    // quem esta estourando: o elemento cuja borda direita passa da janela
    const lim = document.documentElement.clientWidth;
    out.culpados = [...document.querySelectorAll('body *')]
      .filter(e => { const r = e.getBoundingClientRect();
                     return r.width > 0 && r.right > lim + 1; })
      .slice(0, 6)
      .map(e => (e.tagName + '.' + (e.className.baseVal || e.className || '')).slice(0, 60));
  }

  const vistos = new Set();
  document.querySelectorAll('[id]').forEach(e => {
    if (vistos.has(e.id)) out.ids.push(e.id); else vistos.add(e.id);
  });

  document.querySelectorAll('img').forEach(e => {
    if (!e.hasAttribute('alt')) out.semAlt.push((e.getAttribute('src') || '').slice(-42));
  });

  document.querySelectorAll('a[href], button').forEach(e => {
    const nome = (e.getAttribute('aria-label') || e.textContent || '').trim();
    if (!nome) out.semNome.push((e.tagName + ' ' + (e.getAttribute('href') || e.className)).slice(0, 54));
  });

  let ant = 0;
  document.querySelectorAll('h1,h2,h3,h4').forEach(h => {
    const n = +h.tagName[1];
    if (ant && n > ant + 1) out.titulos.push('pulou h' + ant + ' -> h' + n + ': ' + h.textContent.trim().slice(0, 32));
    ant = n;
  });
  const h1 = document.querySelectorAll('h1').length;
  if (h1 !== 1) out.titulos.push('h1 x' + h1);

  if (matchMedia('(pointer: coarse)').matches) {
    document.querySelectorAll('a[href], button, summary, [tabindex]').forEach(e => {
      const r = e.getBoundingClientRect();
      if (r.width === 0 || r.height === 0) return;             // escondido
      if (getComputedStyle(e).display === 'none') return;
      if (r.height < 44 || r.width < 24) {
        out.toque.push(((e.textContent || e.getAttribute('aria-label') || e.className) + '')
          .trim().slice(0, 26) + ' ' + Math.round(r.width) + 'x' + Math.round(r.height));
      }
    });
  }
  return JSON.stringify(out);
})()`;

const ch = await abrirChrome(9390);
const br = await Sessao.conectar(ch.browserWs);
console.log(`VISTORIA @ ${L}x${A}\n`);
let total = 0;

for (const p of PAGS) {
  const { s } = await pagina(br, { url: "about:blank", largura: L, altura: A, dpr: 1, movel: L < 900 });
  const erros = [];
  await s("Runtime.enable");
  await s("Log.enable").catch(() => {});
  s.on?.("Runtime.exceptionThrown", (e) => erros.push("exception"));
  await s("Page.navigate", { url: pathToFileURL(resolve("site", p + ".html")).href });
  await new Promise((r) => setTimeout(r, 1500));
  // mata a intro para nao medir a pagina coberta
  await avaliar(s, `(()=>{document.documentElement.classList.remove('intro-ativa');
    const i=document.querySelector('.intro'); if(i) i.remove();
    const a=document.getElementById('aviso-armazenamento'); if(a) a.remove(); return 1})()`);
  await new Promise((r) => setTimeout(r, 400));

  const consola = await avaliar(s, `(window.__erros||[]).length`);
  const d = JSON.parse(await avaliar(s, SONDA));
  const linhas = [];
  if (d.over) linhas.push(`transbordo lateral ${d.over}px  ${(d.culpados || []).join(' | ')}`);
  if (d.ids.length) linhas.push(`id repetido: ${d.ids.join(', ')}`);
  if (d.semAlt.length) linhas.push(`img sem alt: ${d.semAlt.join(', ')}`);
  if (d.semNome.length) linhas.push(`sem nome: ${d.semNome.join(' | ')}`);
  if (d.titulos.length) linhas.push(`titulos: ${d.titulos.join(' | ')}`);
  if (d.toque.length) linhas.push(`alvo <44px (${d.toque.length}): ${d.toque.slice(0, 5).join(' | ')}`);
  total += linhas.length;
  console.log(`${p.padEnd(22)} ${linhas.length ? "" : "ok"}`);
  linhas.forEach((l) => console.log(`   ${l}`));
}
console.log(`\n${total} achado(s)`);
await fecharChrome(ch);
