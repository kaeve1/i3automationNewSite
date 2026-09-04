// Servidor local que imita a hospedagem: comprime texto e devolve 404 de
// verdade quando o caminho nao existe. Sem isso a medicao mente para os dois
// lados -- CSS/JS sairiam sem gzip (peso inflado) e caminho errado devolveria
// a home com 200, que e justamente o defeito que a 404.html conserta.
import { createServer } from "node:http";
import { createServer as createServerTLS } from "node:https";
import { readFile, stat } from "node:fs/promises";
import { gzipSync } from "node:zlib";
import { join, extname } from "node:path";

const RAIZ = process.argv[2];
const PORTA = +(process.argv[3] || 8765);
const TIPO = {
  ".html": "text/html; charset=utf-8", ".css": "text/css; charset=utf-8",
  ".js": "text/javascript; charset=utf-8", ".json": "application/json",
  ".svg": "image/svg+xml", ".xml": "application/xml", ".txt": "text/plain",
  ".jpg": "image/jpeg", ".png": "image/png", ".webp": "image/webp",
  ".avif": "image/avif", ".woff2": "font/woff2", ".ico": "image/x-icon",
  ".webmanifest": "application/manifest+json",
};
const COMPRIME = new Set([".html", ".css", ".js", ".svg", ".xml", ".txt", ".json", ".webmanifest"]);

const atender = async (req, res) => {
  let p = decodeURIComponent(req.url.split("?")[0]);
  if (p.endsWith("/")) p += "index.html";
  const arq = join(RAIZ, p);
  const ext = extname(arq).toLowerCase();
  try {
    if (!(await stat(arq)).isFile()) throw new Error("dir");
    let corpo = await readFile(arq);
    // O _headers de producao faz parte da medicao: sem Cache-Control o Chrome
    // trata o recurso como nao-cacheavel e um mesmo arquivo pedido por dois
    // consumidores (mask-image no CSS e new Image() no JS) vira DOIS downloads.
    // Medir sem os cabecalhos do host inventa um defeito que o ar nao tem.
    const cab = { "Content-Type": TIPO[ext] || "application/octet-stream" };
    if (/^\/(img|fonts)\//.test(p)) cab["Cache-Control"] = "public, max-age=31536000, immutable";
    else if (/^\/brand\//.test(p) || p === "/favicon.ico" || p === "/site.webmanifest")
      cab["Cache-Control"] = "public, max-age=604800";
    else if (ext === ".css" || ext === ".js") cab["Cache-Control"] = "public, max-age=3600";
    cab["X-Content-Type-Options"] = "nosniff";
    if (COMPRIME.has(ext) && /gzip/.test(req.headers["accept-encoding"] || "")) {
      corpo = gzipSync(corpo, { level: 9 });
      cab["Content-Encoding"] = "gzip";
    }
    cab["Content-Length"] = corpo.length;
    res.writeHead(200, cab); res.end(corpo);
  } catch {
    try {
      const c = await readFile(join(RAIZ, "404.html"));
      res.writeHead(404, { "Content-Type": "text/html; charset=utf-8" }); res.end(c);
    } catch { res.writeHead(404).end("404"); }
  }
};

// TLS opcional, e ele existe por um motivo de medicao: o Chrome NAO GUARDA EM
// CACHE resposta vinda de origem com certificado invalido. Medir o site atras
// de um certificado autoassinado devolve, portanto, downloads duplicados que
// nao existem em producao. Com o mesmo servidor servindo http e https da para
// isolar a variavel em vez de adivinhar.
const cert = process.env.CERT, chave = process.env.CHAVE;
if (cert && chave) {
  const { readFileSync } = await import("node:fs");
  createServerTLS({ cert: readFileSync(cert), key: readFileSync(chave) }, atender)
    .listen(PORTA, "127.0.0.1", () => console.error("servindo TLS em " + PORTA));
} else {
  createServer(atender).listen(PORTA, "127.0.0.1",
    () => console.error("servindo " + RAIZ + " em " + PORTA));
}
