// Mede desempenho real em Chrome headless, sem Lighthouse e sem instalar nada.
//
// Por que nao "rodar o PageSpeed": o PageSpeed Insights e um servico que
// precisa de URL PUBLICA. O site ainda nao esta no ar, entao o que da para
// fazer -- e o que importa -- e medir as MESMAS metricas que ele reporta,
// com o mesmo estrangulamento que o Lighthouse movel usa por padrao.
//
// LCP, CLS e TBT sao coletados por PerformanceObserver injetado ANTES de
// qualquer script da pagina (Page.addScriptToEvaluateOnNewDocument), senao o
// observador perde as entradas que ocorrem antes de ele existir.
import { abrirChrome, fecharChrome, Sessao } from "../movel/cdp.mjs";

const BASE = process.argv[2] || "http://127.0.0.1:8765";
// A lista de paginas vem por ambiente quando existe, para o medidor servir
// qualquer site e nao so este. `PAGINAS="/,/quem-somos/" node medir.mjs <url>`
const PAGINAS = process.env.PAGINAS
  ? process.env.PAGINAS.split(",").map(s => s.trim()).filter(Boolean)
  : ["/", "/who-we-are.html", "/capabilities.html", "/services.html",
     "/past-performance.html", "/gallery.html", "/contact.html"];

// Lighthouse movel: 4x de CPU, Slow 4G (1,6 Mbps / 750 kbps / 150 ms).
const PERFIS = {
  movel:   { largura: 390, altura: 844, dpr: 3, movel: true,  cpu: 4, rede: { down: 1.6e6/8, up: 750e3/8, rtt: 150 } },
  desktop: { largura: 1440, altura: 900, dpr: 1, movel: false, cpu: 1, rede: null },
};

const SONDA = `
window.__perf = { lcp: 0, cls: 0, tbt: 0, fcp: 0, longas: 0 };
try {
  new PerformanceObserver(l => { for (const e of l.getEntries()) window.__perf.lcp = e.startTime; })
    .observe({ type: "largest-contentful-paint", buffered: true });
  new PerformanceObserver(l => {
    for (const e of l.getEntries()) if (!e.hadRecentInput) window.__perf.cls += e.value;
  }).observe({ type: "layout-shift", buffered: true });
  new PerformanceObserver(l => {
    for (const e of l.getEntries()) {
      window.__perf.longas++;
      if (e.duration > 50) window.__perf.tbt += e.duration - 50;
    }
  }).observe({ type: "longtask", buffered: true });
  new PerformanceObserver(l => {
    for (const e of l.getEntries()) if (e.name === "first-contentful-paint") window.__perf.fcp = e.startTime;
  }).observe({ type: "paint", buffered: true });
} catch (e) {}
`;

let COLETOR;
async function medirPagina(browser, caminho, perfil) {
  const { targetId } = await browser.enviar("Target.createTarget", { url: "about:blank" });
  const { sessionId } = await browser.enviar("Target.attachToTarget", { targetId, flatten: true });
  const s = (m, p) => browser.enviar(m, p, sessionId);

  const rec = [];
  COLETOR.rec = rec;
  COLETOR.porId = new Map();

  await s("Page.enable");
  await s("Runtime.enable");
  await s("Network.enable");
  // O CACHE FICA LIGADO, e a limpeza acontece ENTRE paginas.
  // `setCacheDisabled` parece o jeito certo de medir visita fria e nao e: ele
  // tambem impede a reutilizacao DENTRO da pagina. As mascaras de setor tem
  // dois consumidores cada (o `mask-image` do CSS e o `new Image()` da lente),
  // e sem cache as cinco eram baixadas DUAS vezes -- 720 KB de defeito que so
  // existia na medicao. `clearBrowserCache` da a visita fria de verdade sem
  // inventar esse custo.
  await s("Network.clearBrowserCache");
  await s("Page.addScriptToEvaluateOnNewDocument", { source: SONDA });
  await s("Emulation.setDeviceMetricsOverride", {
    width: perfil.largura, height: perfil.altura, deviceScaleFactor: perfil.dpr,
    mobile: perfil.movel, screenWidth: perfil.largura, screenHeight: perfil.altura,
  });
  if (perfil.cpu > 1) await s("Emulation.setCPUThrottlingRate", { rate: perfil.cpu });
  if (perfil.rede) await s("Network.emulateNetworkConditions", {
    offline: false, latency: perfil.rede.rtt,
    downloadThroughput: perfil.rede.down, uploadThroughput: perfil.rede.up,
  });

  const carregou = new Promise(ok => {
    const h = (p) => { if (p.sessionId === sessionId || p.sessionId === undefined) ok(); };
    browser.on("Page.loadEventFired", h);
    setTimeout(ok, 40000);
  });
  await s("Page.navigate", { url: BASE + caminho });
  await carregou;
  // A janela de LCP/TBT que o Lighthouse considera vai bem alem do load.
  await new Promise(r => setTimeout(r, 3500));

  const r = await s("Runtime.evaluate", { expression: "JSON.stringify(window.__perf)", returnByValue: true });
  const perf = JSON.parse(r.result.value);
  await browser.enviar("Target.closeTarget", { targetId });
  return { perf, rec };
}

const ch = await abrirChrome(9401);
const browser = await Sessao.conectar(ch.browserWs);

// Ouvintes registrados UMA vez. cdp.mjs nao remove ouvinte, entao registrar por
// pagina acumularia e a pagina 7 contaria os recursos das 6 anteriores.
COLETOR = { rec: [], porId: new Map() };
browser.on("Network.responseReceived", (p) => {
  COLETOR.porId.set(p.requestId, { url: p.response.url, tipo: p.type, mime: p.response.mimeType });
});
browser.on("Network.loadingFinished", (p) => {
  const r = COLETOR.porId.get(p.requestId);
  if (r) COLETOR.rec.push({ ...r, rede: p.encodedDataLength });
});
const saida = {};
for (const nome of Object.keys(PERFIS)) {
  saida[nome] = {};
  for (const p of PAGINAS) {
    const { perf, rec } = await medirPagina(browser, p, PERFIS[nome]);
    const soma = (f) => rec.filter(f).reduce((t, x) => t + x.rede, 0);
    saida[nome][p] = {
      lcp: Math.round(perf.lcp), fcp: Math.round(perf.fcp),
      cls: +perf.cls.toFixed(4), tbt: Math.round(perf.tbt), longas: perf.longas,
      pedidos: rec.length,
      total: soma(() => true),
      img: soma(x => x.tipo === "Image"),
      script: soma(x => x.tipo === "Script"),
      css: soma(x => x.tipo === "Stylesheet"),
      fonte: soma(x => x.tipo === "Font"),
      doc: soma(x => x.tipo === "Document"),
    };
    console.error(`  ${nome} ${p} ok`);
  }
}
browser.fechar(); fecharChrome(ch);
console.log(JSON.stringify(saida, null, 1));
