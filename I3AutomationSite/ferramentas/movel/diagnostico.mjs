// Varredura de defeitos de layout móvel, medida no Chrome de verdade.
import { abrirChrome, fecharChrome, Sessao, pagina, avaliar } from "./cdp.mjs";
import { pathToFileURL } from "node:url";
import { resolve } from "node:path";

const PAGINAS = ["index","who-we-are","capabilities","past-performance","services","gallery","contact","privacy-policy","terms-and-conditions","404"];

const APARELHOS = [
  { nome: "iPhone SE",       l: 375, a: 667, dpr: 2 },
  { nome: "iPhone 14 Pro",   l: 393, a: 852, dpr: 3 },
  { nome: "Galaxy S20",      l: 360, a: 800, dpr: 3 },
  { nome: "pequeno 320",     l: 320, a: 568, dpr: 2 },
  { nome: "iPhone paisagem", l: 667, a: 375, dpr: 2 },
  { nome: "iPad retrato",    l: 768, a: 1024, dpr: 2 },
];

const SONDA = `(() => {
  document.documentElement.classList.remove("intro-ativa");
  const _i = document.querySelector(".intro"); if (_i) _i.remove();
  const vw = window.innerWidth;
  const doc = document.documentElement;
  const out = { vw, vh: window.innerHeight, scrollW: doc.scrollWidth, bodyW: document.body.scrollWidth, transborda: [], alvos: [], sobreposicao: [], tipoPequeno: [] };

  const desc = (el) => {
    const c = typeof el.className === "string" ? el.className.trim().split(/\s+/).slice(0,3).join(".") : "";
    return el.tagName.toLowerCase() + (el.id ? "#" + el.id : "") + (c ? "." + c : "");
  };

  // 1) quem passa da borda direita da janela
  const vistos = new Set();
  for (const el of document.querySelectorAll("body *")) {
    const cs = getComputedStyle(el);
    if (cs.display === "none" || cs.visibility === "hidden" || cs.opacity === "0") continue;
    const r = el.getBoundingClientRect();
    if (r.width === 0 && r.height === 0) continue;
    if (cs.position === "fixed" && r.width <= vw + 1) continue;
    const excedeD = r.right - vw;
    const excedeE = -r.left;
    if (excedeD > 1 || excedeE > 1) {
      // só reporta se nenhum ancestral já corta (overflow hidden/clip)
      let cortado = false;
      for (let p = el.parentElement; p && p !== document.body; p = p.parentElement) {
        const pc = getComputedStyle(p);
        if (/hidden|clip|auto|scroll/.test(pc.overflowX)) { cortado = true; break; }
      }
      if (cortado) continue;
      if (el.classList.contains('pular-conteudo')) continue;
      const k = desc(el);
      if (vistos.has(k)) continue; vistos.add(k);
      out.transborda.push({ el: k, right: Math.round(r.right), left: Math.round(r.left), w: Math.round(r.width), excede: Math.round(Math.max(excedeD, excedeE)) });
    }
  }

  // 2) alvos de toque pequenos
  const cliqueveis = document.querySelectorAll("a[href], button, input, select, textarea, [role=button], [tabindex]:not([tabindex='-1'])");
  const vistosA = new Set();
  for (const el of cliqueveis) {
    const cs = getComputedStyle(el);
    if (cs.display === "none" || cs.visibility === "hidden") continue;
    const r = el.getBoundingClientRect();
    if (r.width === 0 || r.height === 0) continue;
    if (r.width < 44 || r.height < 44) {
      const k = desc(el);
      if (vistosA.has(k)) continue; vistosA.add(k);
      out.alvos.push({ el: k, w: Math.round(r.width), h: Math.round(r.height), txt: (el.textContent||"").trim().slice(0,28) });
    }
  }

  // 3) tipo abaixo de 14px em conteúdo
  const vistosT = new Set();
  for (const el of document.querySelectorAll("p, li, dd, dt, span, a, small, td, th, figcaption")) {
    if (!el.textContent.trim()) continue;
    const cs = getComputedStyle(el);
    if (cs.display === "none") continue;
    const fs = parseFloat(cs.fontSize);
    if (fs < 13) {
      const k = desc(el) + "@" + fs;
      if (vistosT.has(k)) continue; vistosT.add(k);
      out.tipoPequeno.push({ el: desc(el), fs: fs.toFixed(1), txt: el.textContent.trim().slice(0,24) });
    }
  }
  return out;
})()`;

const raiz = resolve("site");
const ch = await abrirChrome(9333 + (Number(process.env.PORTA_OFF)||0));
const br = await Sessao.conectar(ch.browserWs);
const filtroPag = process.argv[2] ? process.argv[2].split(",") : PAGINAS;
const filtroApp = process.argv[3] ? APARELHOS.filter(a => process.argv[3].split(",").includes(a.nome)) : APARELHOS;

const relatorio = [];
for (const ap of filtroApp) {
  for (const p of filtroPag) {
    const url = pathToFileURL(resolve(raiz, p + ".html")).href;
    const { s, targetId } = await pagina(br, { url, largura: ap.l, altura: ap.a, dpr: ap.dpr, movel: ap.l < 900 });
    let r;
    try { r = await avaliar(s, SONDA); } catch (e) { r = { erro: String(e) }; }
    await br.enviar("Target.closeTarget", { targetId });
    relatorio.push({ aparelho: ap.nome, pagina: p, ...r });
  }
}
br.fechar(); fecharChrome(ch);

// ---- saída legível ----
let rolagemH = 0, totalAlvos = 0, totalTrans = 0;
for (const r of relatorio) {
  const temRolagem = r.scrollW > r.vw + 1;
  if (temRolagem) rolagemH++;
  const linhas = [];
  if (temRolagem) linhas.push(`  ROLAGEM HORIZONTAL: scrollWidth ${r.scrollW} > viewport ${r.vw}  (+${r.scrollW - r.vw}px)`);
  if (r.transborda?.length) { totalTrans += r.transborda.length; linhas.push("  transborda: " + r.transborda.map(t => `${t.el} +${t.excede}px`).join(", ")); }
  if (r.alvos?.length) { totalAlvos += r.alvos.length; linhas.push("  alvos <44px: " + r.alvos.map(t => `${t.el} ${t.w}x${t.h}`).join(", ")); }
  if (r.tipoPequeno?.length) linhas.push("  tipo <13px: " + r.tipoPequeno.map(t => `${t.el} ${t.fs}px`).join(", "));
  if (r.erro) linhas.push("  ERRO " + r.erro);
  if (linhas.length) console.log(`\n[${r.aparelho}] ${r.pagina}\n` + linhas.join("\n"));
}
console.log(`\n===== ${relatorio.length} combinações · ${rolagemH} com rolagem horizontal · ${totalTrans} elementos transbordando · ${totalAlvos} alvos pequenos =====`);
