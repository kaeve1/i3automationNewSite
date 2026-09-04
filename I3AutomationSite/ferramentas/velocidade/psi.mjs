// PageSpeed Insights de verdade, no dominio publicado.
//
// Por que ele nao pode rodar agora: o PSI e um servico do Google que precisa
// buscar a URL pela internet. Enquanto o site nao estiver no ar, o que da para
// medir e o que `medir.mjs` mede -- as MESMAS metricas, no mesmo Chrome, com o
// mesmo estrangulamento (Slow 4G + CPU 4x, o perfil movel do Lighthouse).
//
// No dia em que i3automations.com apontar para o site novo:
//   node ferramentas/velocidade/psi.mjs https://i3automations.com/
//
// Sem chave a API aceita algumas consultas por minuto, que basta para conferir
// as sete paginas. Com cota estourada ela devolve 429 -- espere e repita.
const URL_ALVO = process.argv[2];
if (!URL_ALVO) { console.error("uso: node psi.mjs <url> [movel|desktop]"); process.exit(1); }
const ESTRATEGIA = (process.argv[3] || "movel") === "desktop" ? "desktop" : "mobile";

const api = "https://www.googleapis.com/pagespeedonline/v5/runPagespeed"
  + `?url=${encodeURIComponent(URL_ALVO)}&strategy=${ESTRATEGIA}`
  + "&category=performance&category=seo&category=accessibility&category=best-practices";

const r = await fetch(api);
if (!r.ok) { console.error(`PSI devolveu ${r.status}: ${await r.text()}`); process.exit(1); }
const d = await r.json();
const lh = d.lighthouseResult;
console.log(`${URL_ALVO}  (${ESTRATEGIA})\n`);
for (const [k, c] of Object.entries(lh.categories)) {
  console.log(`  ${String(Math.round(c.score * 100)).padStart(3)}  ${c.title}`);
}
console.log();
for (const id of ["largest-contentful-paint", "total-blocking-time",
                  "cumulative-layout-shift", "first-contentful-paint", "speed-index"]) {
  const a = lh.audits[id];
  if (a) console.log(`  ${a.title.padEnd(28)} ${a.displayValue}`);
}
