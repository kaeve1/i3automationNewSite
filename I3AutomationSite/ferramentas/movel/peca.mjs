// Captura UMA peça de canvas depois de deixá-la animar de verdade.
//
// POR QUE ELE EXISTE. `tirar.mjs` abre a aba em segundo plano, e nesse estado
// o Chrome não entrega `requestAnimationFrame`: a peça desenha a grade no
// primeiro quadro e para. O histórico das penas nunca se forma, e o screenshot
// mostra uma caixa vazia que parece defeito e não é. É a mesma limitação que
// `doit.md` registra na Fase 8.
//
// A saída é `Emulation.setVirtualTimePolicy`: o relógio da página avança sob
// controle, `rAF` dispara, e a peça acumula os quadros que precisa antes da
// captura. Sem isso não há como conferir uma peça animada fora do navegador.
//
// uso: node ferramentas/movel/peca.mjs services .malha 4000 malha
import { abrirChrome, fecharChrome, Sessao, pagina, avaliar } from "./cdp.mjs";
import { pathToFileURL } from "node:url";
import { resolve } from "node:path";
import { writeFileSync, mkdirSync } from "node:fs";

const [, , nomePag = "services", seletor = ".malha", msS = "4000", rotulo = "peca"] = process.argv;
const ms = Number(msS);
const saida = resolve("ferramentas/movel/tiras");
mkdirSync(saida, { recursive: true });

const ch = await abrirChrome(9352);
const br = await Sessao.conectar(ch.browserWs);
const url = pathToFileURL(resolve("site", nomePag + ".html")).href;
const { s } = await pagina(br, { url, largura: 1440, altura: 900, dpr: 2, movel: false });

await avaliar(s, `(()=>{document.documentElement.classList.remove('intro-ativa');
  const i=document.querySelector('.intro'); if(i) i.remove();
  document.documentElement.style.scrollBehavior='auto'; return 1})()`);

// leva a peça para o meio da janela, senão o IntersectionObserver não a liga
await avaliar(s, `(()=>{const e=document.querySelector('${seletor}');
  if(!e) return 'AUSENTE';
  e.scrollIntoView({block:'center'}); return e.className})()`).then(r => console.log("alvo:", r));

// `Page.bringToFront` tira a aba de `visibilityState: "hidden"`. Sem ela o
// Chrome não entrega `requestAnimationFrame` e a peça desenha um quadro só --
// grade e eixo, sem histórico, que é a caixa "vazia" que `doit.md` registra
// como limitação da Fase 8.
//
// Tempo REAL e não `setVirtualTimePolicy`: o relógio virtual entrega o
// orçamento inteiro como poucos saltos enormes, e as penas precisam de MUITOS
// quadros pequenos para acumular histórico -- `avancar()` integra a passo
// fixo e limita quantos passos faz por quadro.
await s("Page.bringToFront");
await avaliar(s, `document.visibilityState`).then(v => console.log("visibilidade:", v));
await new Promise(r => setTimeout(r, ms));

const viva = await avaliar(s, `document.querySelector('${seletor}')?.classList.contains('is-viva')`);
console.log("is-viva:", viva);

// `clip` do CDP é em coordenadas de DOCUMENTO, e `getBoundingClientRect` é em
// coordenadas de VIEWPORT. Sem somar a rolagem o recorte sai de outro pedaço
// da página -- foi o que devolveu um retângulo branco na primeira tentativa.
const caixa = await avaliar(s, `(()=>{const r=document.querySelector('${seletor}').getBoundingClientRect();
  return JSON.stringify({x:Math.round(r.x+scrollX),y:Math.round(r.y+scrollY),
                         w:Math.round(r.width),h:Math.round(r.height)})})()`);
const c = JSON.parse(caixa);
console.log("caixa:", caixa);

const { data } = await s("Page.captureScreenshot", {
  format: "png",
  clip: { x: c.x, y: c.y, width: c.w, height: c.h, scale: 2 },
});
const arq = resolve(saida, `${rotulo}.png`);
writeFileSync(arq, Buffer.from(data, "base64"));
console.log("->", arq);

await fecharChrome(ch);
