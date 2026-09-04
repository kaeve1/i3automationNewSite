/* ============================================================================
   tela.js — o núcleo das peças em CANVAS 2D
   i3Automations

   POR QUE ISTO EXISTE. Três peças nasceram juntas em 20/08 — a malha de
   controle de services, o sinóptico de past-performance e a carta de
   contact — e todas as três precisam exatamente da mesma caldeira: medir a
   caixa, resolver o `devicePixelRatio`, parar de desenhar fora da tela,
   respeitar movimento reduzido e reagir à troca de tema.

   Repetir isso três vezes é como as três divergem. É a mesma decisão que
   `gl.js` já registrou para as peças em WebGL, tomada agora no começo em vez
   de depois da segunda cópia.

   O QUE ELE NÃO FAZ: não desenha. Cada peça recebe o contexto já dimensionado
   e a largura/altura em pixels de CSS, e o resto é dela.

   DUAS ARMADILHAS JÁ PAGAS POR ESTE PROJETO, e as duas moram aqui:

     o canvas NÃO PODE PARTICIPAR DO LAYOUT. Ele tem tamanho intrínseco vindo
       dos atributos `width`/`height`; se `medir()` lê o retângulo e escreve de
       volta nos atributos, e a caixa depende do canvas, a página cresce sem
       parar. Custou uma sessão em 19/08. Por isso a tela é sempre `position:
       absolute` e o CSS dá a caixa;

     o TETO de 4096 px não é otimização. É a trava para que a próxima
       regressão desse tipo seja um desenho feio, e não um site travado.
   ============================================================================ */
(function () {
  "use strict";

  var TETO = 4096;

  /* Cor de token resolvida para o canvas. Ao contrário do WebGL, aqui NÃO é
     preciso parser hexadecimal: `fillStyle`/`strokeStyle` aceitam a string
     como ela sai do `getComputedStyle`. A nota longa em lente.js explica por
     que no shader é o contrário — e é o bug mais caro já registrado aqui. */
  function token(el, nome, reserva) {
    var v = window.getComputedStyle(el).getPropertyValue(nome).trim();
    return v || reserva;
  }

  /* Alfa sobre uma cor de token, para peças que precisam de meia-tinta sem
     inventar um token novo. Aceita #rgb, #rrggbb e rgb()/rgba(). */
  function alfa(cor, a) {
    var c = cor.trim();
    if (c.charAt(0) === "#") {
      var h = c.slice(1);
      if (h.length === 3) h = h[0] + h[0] + h[1] + h[1] + h[2] + h[2];
      var n = parseInt(h, 16);
      return "rgba(" + ((n >> 16) & 255) + "," + ((n >> 8) & 255) + "," +
             (n & 255) + "," + a + ")";
    }
    var m = c.match(/rgba?\(([^)]+)\)/);
    if (!m) return c;
    var p = m[1].split(",");
    return "rgba(" + p[0] + "," + p[1] + "," + p[2] + "," + a + ")";
  }

  /* O REGISTRO TIPOGRÁFICO DAS PEÇAS EM CANVAS, num lugar só.
     12 px com .14em é o registro da linha de cota da prancha
     (`.prancha__cota` no CSS) -- e é exatamente o que um rótulo de peça é:
     ANOTAÇÃO sobre um desenho, não corpo de texto.

     Existe aqui porque as três peças divergiram sozinhas em um dia: o
     sinóptico saía a 27 px (a fonte era declarada dentro de um espaço
     escalado 2,46x e ninguém tinha reparado), a malha a 11 px sem tracking e
     a carta a 10 px -- abaixo do piso de 11 do site. Três peças irmãs, três
     tipografias diferentes, nenhuma delas escolhida.

     `escala` é para quem desenha num espaço transformado: passando 1/m, a
     fonte é declarada em unidades locais e RENDERIZA no tamanho de tela
     certo. `letterSpacing` do canvas é recente (Chrome 99, Safari 16.4);
     onde não existe, a atribuição é ignorada e some o acabamento, não a
     informação. */
  var TIPO_PX = 12, TIPO_TRACK = 0.14;

  function tipo(ctx, el, escala) {
    var e = escala || 1;
    var px = TIPO_PX * e;
    ctx.font = px.toFixed(3) + "px " +
               token(el, "--font-mono", "ui-monospace, monospace");
    if ("letterSpacing" in ctx) {
      ctx.letterSpacing = (TIPO_PX * TIPO_TRACK * e).toFixed(3) + "px";
    }
    return px;
  }

  /* `desenhar(ctx, larg, alt, t, dt)` recebe pixels de CSS -- a escala do dpr
     já está aplicada no contexto, então a peça pensa em unidades de layout e
     nunca em pixels de dispositivo. */
  function montar(raiz, opcoes) {
    var canvas = raiz.querySelector("canvas");
    if (!canvas || !canvas.getContext) return null;
    var ctx = canvas.getContext("2d");
    if (!ctx) return null;

    var reduzido = window.matchMedia("(prefers-reduced-motion: reduce)").matches;
    var larg = 1, alt = 1, dpr = 1;
    var visivel = false, rodando = false, anterior = 0, t = 0;

    function medir() {
      var c = raiz.getBoundingClientRect();
      if (c.width < 2 || c.height < 2) return false;
      dpr = Math.min(window.devicePixelRatio || 1, 2);
      larg = Math.min(c.width, TETO / dpr);
      alt = Math.min(c.height, TETO / dpr);
      var w = Math.round(larg * dpr), h = Math.round(alt * dpr);
      if (canvas.width !== w || canvas.height !== h) {
        canvas.width = w;
        canvas.height = h;
      }
      return true;
    }

    function pintar(dt) {
      ctx.setTransform(dpr, 0, 0, dpr, 0, 0);
      ctx.clearRect(0, 0, larg, alt);
      opcoes.desenhar(ctx, larg, alt, t, dt);
    }

    function quadro(agora) {
      rodando = false;
      var dt = anterior ? Math.min((agora - anterior) / 1000, 0.064) : 0.016;
      anterior = agora;
      t += dt;
      pintar(dt);
      /* Movimento reduzido desenha UMA VEZ e para: a peça continua legível,
         só não anima (design.md §7 regra 3). */
      if (visivel && !reduzido) acordar();
    }

    function acordar() {
      if (rodando) return;
      rodando = true;
      window.requestAnimationFrame(quadro);
    }

    function refazer() {
      if (!medir()) return;
      if (opcoes.medida) opcoes.medida(larg, alt);
      anterior = 0;
      if (reduzido) pintar(0); else acordar();
    }

    /* Havia aqui um ouvinte de `temachange` que rechamava `opcoes.tema` para
       a peça reler os tokens de cor. Com tema único (2026-08-25) o evento
       nunca mais é disparado, então o ouvinte e a opção `tema` saíram: cada
       peça lê os tokens uma vez, na montagem, e pronto. */
    window.addEventListener("resize", refazer);

    if (window.IntersectionObserver) {
      new IntersectionObserver(function (ent) {
        visivel = ent[0].isIntersecting;
        if (visivel) { anterior = 0; if (reduzido) pintar(0); else acordar(); }
      }, { rootMargin: "120px" }).observe(raiz);
    } else {
      visivel = true;
    }

    if (!medir()) return null;
    if (opcoes.medida) opcoes.medida(larg, alt);
    pintar(0);
    return {
      raiz: raiz, canvas: canvas, ctx: ctx, reduzido: reduzido,
      acordar: acordar, refazer: refazer, redesenhar: function () { pintar(0); },
      dim: function () { return [larg, alt]; }
    };
  }

  window.I3Tela = { montar: montar, token: token, alfa: alfa, tipo: tipo };
})();
