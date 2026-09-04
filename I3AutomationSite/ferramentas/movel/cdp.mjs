// Driver CDP mínimo — Chrome headless sem puppeteer.
// Node 24 já traz WebSocket global, então não há dependência nenhuma.
import { spawn } from "node:child_process";
import { mkdtempSync, rmSync } from "node:fs";
import { tmpdir } from "node:os";
import { join } from "node:path";

const CHROME = process.env.CHROME_BIN || "C:/Program Files/Google/Chrome/Application/chrome.exe";

export async function abrirChrome(porta = 9333) {
  const perfil = mkdtempSync(join(tmpdir(), "i3cdp-"));
  const proc = spawn(CHROME, [
    "--headless=new",
    `--remote-debugging-port=${porta}`,
    `--user-data-dir=${perfil}`,
    "--no-first-run", "--no-default-browser-check",
    "--disable-extensions", "--disable-gpu",
    "--hide-scrollbars",
    "--force-device-scale-factor=1",
    "--allow-file-access-from-files",
    // So para teste local com certificado autoassinado (o Apache em container
    // de ferramentas/velocidade). Sem isto o Chrome bloqueia o handshake e a
    // medicao devolve 0 byte e ~3 s uniformes em toda pagina -- numero que
    // parece medida e nao e. Fica atras de variavel de ambiente porque
    // ignorar certificado por padrao e o tipo de atalho que sobrevive ate
    // alguem apontar a ferramenta para a internet.
    ...(process.env.CDP_TLS_INSEGURO === "1"
        ? ["--ignore-certificate-errors"] : []),
    "about:blank",
  ], { stdio: "ignore", detached: false });

  // espera a porta responder
  let alvo = null;
  for (let i = 0; i < 100; i++) {
    try {
      const r = await fetch(`http://127.0.0.1:${porta}/json/version`);
      if (r.ok) { alvo = (await r.json()).webSocketDebuggerUrl; break; }
    } catch {}
    await new Promise(r => setTimeout(r, 150));
  }
  if (!alvo) { proc.kill(); throw new Error("Chrome não subiu"); }
  return { proc, perfil, browserWs: alvo, porta };
}

export function fecharChrome(ch) {
  try { ch.proc.kill(); } catch {}
  try { rmSync(ch.perfil, { recursive: true, force: true }); } catch {}
}

export class Sessao {
  constructor(ws) { this.ws = ws; this.id = 0; this.pend = new Map(); this.eventos = new Map(); }

  static async conectar(url) {
    const ws = new WebSocket(url);
    await new Promise((ok, err) => { ws.onopen = ok; ws.onerror = err; });
    const s = new Sessao(ws);
    ws.onmessage = (m) => {
      const msg = JSON.parse(m.data);
      if (msg.id != null && s.pend.has(msg.id)) {
        const { ok, err } = s.pend.get(msg.id); s.pend.delete(msg.id);
        msg.error ? err(new Error(JSON.stringify(msg.error))) : ok(msg.result);
      } else if (msg.method) {
        (s.eventos.get(msg.method) || []).forEach(f => f(msg.params));
      }
    };
    return s;
  }

  on(metodo, fn) {
    if (!this.eventos.has(metodo)) this.eventos.set(metodo, []);
    this.eventos.get(metodo).push(fn);
  }

  enviar(method, params = {}, sessionId) {
    const id = ++this.id;
    return new Promise((ok, err) => {
      this.pend.set(id, { ok, err });
      this.ws.send(JSON.stringify(sessionId ? { id, method, params, sessionId } : { id, method, params }));
      setTimeout(() => { if (this.pend.has(id)) { this.pend.delete(id); err(new Error("timeout " + method)); } }, 30000);
    });
  }

  fechar() { try { this.ws.close(); } catch {} }
}

// Abre uma aba nova já emulando um aparelho, navega e espera assentar.
export async function pagina(browser, { url, largura, altura, dpr = 2, movel = true }) {
  const { targetId } = await browser.enviar("Target.createTarget", { url: "about:blank" });
  const { sessionId } = await browser.enviar("Target.attachToTarget", { targetId, flatten: true });
  const s = (m, p) => browser.enviar(m, p, sessionId);

  await s("Page.enable");
  await s("Runtime.enable");
  await s("Emulation.setDeviceMetricsOverride", {
    width: largura, height: altura, deviceScaleFactor: dpr, mobile: movel,
    screenWidth: largura, screenHeight: altura,
  });
  if (movel) await s("Emulation.setTouchEmulationEnabled", { enabled: true, maxTouchPoints: 5 });
  await s("Emulation.setEmulatedMedia", { features: [{ name: "prefers-reduced-motion", value: "no-preference" }] });

  const carregou = new Promise(ok => {
    const h = () => ok();
    browser.on("Page.loadEventFired", h);
    setTimeout(ok, 12000);
  });
  await s("Page.navigate", { url });
  await carregou;
  await new Promise(r => setTimeout(r, 900));
  return { sessionId, s, targetId };
}

export async function avaliar(s, expr) {
  const r = await s("Runtime.evaluate", { expression: expr, returnByValue: true, awaitPromise: true });
  if (r.exceptionDetails) throw new Error(r.exceptionDetails.exception?.description || JSON.stringify(r.exceptionDetails));
  return r.result.value;
}
