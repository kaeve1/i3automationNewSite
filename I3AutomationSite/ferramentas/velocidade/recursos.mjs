// Lista, por peso, o que UMA pagina realmente baixa. A pergunta que ele
// responde e a que a soma nao responde: QUAL arquivo esta pesando.
import { abrirChrome, fecharChrome, Sessao } from "../movel/cdp.mjs";
const [ , , URL, L, A, DPR ] = process.argv;
const ch = await abrirChrome(9402);
const b = await Sessao.conectar(ch.browserWs);
const porId = new Map(); const rec = [];
b.on("Network.responseReceived", p => porId.set(p.requestId, { url: p.response.url, tipo: p.type }));
b.on("Network.loadingFinished", p => { const r = porId.get(p.requestId); if (r) rec.push({ ...r, rede: p.encodedDataLength }); });
const { targetId } = await b.enviar("Target.createTarget", { url: "about:blank" });
const { sessionId } = await b.enviar("Target.attachToTarget", { targetId, flatten: true });
const s = (m, p) => b.enviar(m, p, sessionId);
await s("Page.enable"); await s("Network.enable"); await s("Network.setCacheDisabled", { cacheDisabled: process.env.SEM_CACHE === "1" });
await s("Emulation.setDeviceMetricsOverride", { width: +L, height: +A, deviceScaleFactor: +DPR, mobile: +DPR > 1, screenWidth: +L, screenHeight: +A });
const carregou = new Promise(ok => { b.on("Page.loadEventFired", ok); setTimeout(ok, 30000); });
await s("Page.navigate", { url: URL }); await carregou;
await new Promise(r => setTimeout(r, 2500));
rec.sort((x, y) => y.rede - x.rede);
let t = 0; for (const r of rec) t += r.rede;
console.log(`TOTAL ${(t/1024).toFixed(1)} KB em ${rec.length} pedidos\n`);
for (const r of rec.slice(0, 22)) console.log(`${(r.rede/1024).toFixed(1).padStart(8)} KB  ${r.tipo.padEnd(10)} ${r.url.replace(/^https?:\/\/[^/]+/, "")}`);
b.fechar(); fecharChrome(ch);
