// Quem esta bloqueando a thread principal, e por quanto tempo.
// TBT alto sem esta resposta vira palpite -- e o palpite caro aqui seria
// "e o WebGL", quando pode ser o parser, a fonte ou o observador de rolagem.
import { abrirChrome, fecharChrome, Sessao } from "../movel/cdp.mjs";
const [ , , URL, CPU ] = process.argv;
const ch = await abrirChrome(9403);
const b = await Sessao.conectar(ch.browserWs);
const { targetId } = await b.enviar("Target.createTarget", { url: "about:blank" });
const { sessionId } = await b.enviar("Target.attachToTarget", { targetId, flatten: true });
const s = (m, p) => b.enviar(m, p, sessionId);
await s("Page.enable"); await s("Runtime.enable"); await s("Profiler.enable");
await s("Emulation.setDeviceMetricsOverride", { width: 390, height: 844, deviceScaleFactor: 3, mobile: true, screenWidth: 390, screenHeight: 844 });
await s("Emulation.setCPUThrottlingRate", { rate: +(CPU || 4) });
await s("Page.addScriptToEvaluateOnNewDocument", { source: `
window.__lt = [];
try { new PerformanceObserver(l => { for (const e of l.getEntries())
  window.__lt.push({ t: Math.round(e.startTime), d: Math.round(e.duration), a: (e.attribution||[]).map(x => x.name + ":" + (x.containerName||x.containerSrc||x.containerId||"")).join(",") });
}).observe({ type: "longtask", buffered: true }); } catch (e) {}
` });
await s("Profiler.setSamplingInterval", { interval: 200 });
await s("Profiler.start");
const carregou = new Promise(ok => { b.on("Page.loadEventFired", ok); setTimeout(ok, 30000); });
await s("Page.navigate", { url: URL }); await carregou;
await new Promise(r => setTimeout(r, 3500));
const { profile } = await s("Profiler.stop");
const r = await s("Runtime.evaluate", { expression: "JSON.stringify(window.__lt)", returnByValue: true });
console.log("TAREFAS LONGAS (>50ms):");
let tbt = 0;
for (const t of JSON.parse(r.result.value)) { tbt += Math.max(0, t.d - 50); console.log(`  em ${String(t.t).padStart(5)}ms  dura ${String(t.d).padStart(4)}ms  ${t.a}`); }
console.log(`  TBT = ${Math.round(tbt)}ms\n`);

// Auto-tempo por funcao, agregado do profile de amostragem.
const porNo = new Map(profile.nodes.map(n => [n.id, n]));
const conta = new Map();
for (let i = 0; i < profile.samples.length; i++) {
  const n = porNo.get(profile.samples[i]); if (!n) continue;
  const dt = (profile.timeDeltas[i] || 0) / 1000;
  const f = n.callFrame;
  const chave = `${f.functionName || "(anonima)"}  ${(f.url || "").replace(/^https?:\/\/[^/]+/, "")}:${f.lineNumber + 1}`;
  conta.set(chave, (conta.get(chave) || 0) + dt);
}
console.log("AUTO-TEMPO POR FUNCAO (ms):");
[...conta.entries()].sort((a, c) => c[1] - a[1]).slice(0, 16)
  .forEach(([k, v]) => console.log(`  ${v.toFixed(1).padStart(7)}  ${k}`));
b.fechar(); fecharChrome(ch);
