
import { abrirChrome, fecharChrome, Sessao } from "../movel/cdp.mjs";
import { readFileSync } from "node:fs";
const TAMANHOS = [16, 32, 48, 180, 192, 512];
const svg = readFileSync(process.argv[2], "utf8");
const ch = await abrirChrome(9406);
const b = await Sessao.conectar(ch.browserWs);
const { targetId } = await b.enviar("Target.createTarget", { url: "about:blank" });
const { sessionId } = await b.enviar("Target.attachToTarget", { targetId, flatten: true });
const s = (m, p) => b.enviar(m, p, sessionId);
await s("Page.enable"); await s("Runtime.enable");
const saida = {};
for (const t of TAMANHOS) {
  await s("Emulation.setDeviceMetricsOverride", { width: t, height: t, deviceScaleFactor: 1, mobile: false });
  // O SVG vai INLINE no documento, sem margem e sem fundo do navegador: um
  // <img src=...> herdaria o branco da pagina nas bordas antisserrilhadas.
  const doc = `<!doctype html><meta charset=utf-8><style>
    html,body{margin:0;padding:0;width:${t}px;height:${t}px;overflow:hidden;background:transparent}
    svg{display:block;width:${t}px;height:${t}px}</style>` + svg;
  await s("Page.navigate", { url: "data:text/html;charset=utf-8," + encodeURIComponent(doc) });
  await new Promise(r => setTimeout(r, 250));
  const { data } = await s("Page.captureScreenshot", { format: "png", captureBeyondViewport: false });
  saida[t] = data;
}
console.log(JSON.stringify(saida));
b.fechar(); fecharChrome(ch);
