/* ============================================================================
   malha.js — a malha de controle que responde
   i3Automations

   A TESE DA EMPRESA, DESENHADA EM VEZ DE REPETIDA. A manchete da home diz
   "Good control strategy beats more expensive instrumentation". Esta peça é
   essa frase virando experimento: a MESMA planta e o MESMO instrumento, duas
   sintonias, e a resposta muda completamente. O visitante arrasta o setpoint e
   vê a variável de processo perseguir.

   POR QUE ELA MORA EM SERVICES. É a página em que o comprador decide como
   contratar, e o argumento de venda inteiro da i3 é que a inteligência está na
   ESTRATÉGIA, não no equipamento. Aqui ele testa isso com a mão.

   O QUE É SIMULADO, E É SIMULAÇÃO DE VERDADE:

     planta ... primeira ordem com tempo morto (FOPDT), que é o modelo com que
                um integrador realmente identifica um processo térmico ou de
                nível: ganho, constante de tempo e atraso de transporte;
     malha .... PID de velocidade com anti-windup por clamp e derivada sobre a
                MEDIÇÃO, não sobre o erro -- que é o que evita o chute de
                derivada quando alguém mexe no setpoint. É exatamente o
                detalhe que separa uma malha ajustada de uma malha "que
                funciona".

   NENHUM NÚMERO DE PROCESSO É AFIRMADO. Os eixos não têm escala e as unidades
   não aparecem: isto é um diagrama de comportamento, não a leitura de uma
   planta real. A distinção importa neste site, que já tirou uma afirmação de
   autoria da galeria pelo mesmo motivo.

   Sem WebGL: é canvas 2D sobre `tela.js`.
   ============================================================================ */
(function () {
  "use strict";
  if (!window.I3Tela) return;

  var T = window.I3Tela;

  /* --- planta: primeira ordem + tempo morto ------------------------------
     K = ganho, TAU = constante de tempo, L = tempo morto (segundos). Os três
     descrevem um processo lento o bastante para a resposta ser LEGÍVEL numa
     tela: com TAU muito curto o overshoot acontece antes de o olho acompanhar,
     e a peça deixa de ensinar o que veio ensinar. */
  var K = 1.0, TAU = 2.6, L = 0.55;

  /* --- as duas sintonias -------------------------------------------------
     A frouxa não é "errada por acaso": é o ganho alto com integral rápida
     demais para o tempo morto, que é o erro clássico de quem sintoniza no
     olho. A ajustada segue a regra prática de IMC/lambda para FOPDT. */
  /* OS TRÊS NÚMEROS SÃO MEDIDOS, não escolhidos, e a medição derrubou a
     primeira tentativa. Portado o laço para Python e medida a resposta ao
     degrau, os valores que eu tinha posto (kp 1,15 / ki 0,42) levavam
     12,5 s para assentar -- lentos a ponto de a peça parecer travada.

     Estes assentam em 8,0 s com 0% de ultrapassagem e nenhum cruzamento do
     setpoint, que é perto do mínimo teórico desta planta (~3·TAU): não dá
     para ser mais rápido sem ultrapassar.

     Para registro, a contraprova: com kp 8,0 / ki 6,0 -- ganho alto com
     integral rápida demais para o tempo morto, que é o erro clássico de quem
     sintoniza no olho -- a malha ultrapassa 13,5% e NUNCA assenta, cruzando o
     setpoint 36 vezes em 40 s. Esse par chegou a ser um botão na página e
     saiu a pedido do usuário: a alternância não acrescentava ao argumento. */
  var SINTONIA = { kp: 2.20, ki: 0.85, kd: 0.30 };

  var JANELA = 22;          /* segundos de histórico visíveis */
  var PASSO = 1 / 60;       /* passo fixo de integração */

  function montar(raiz) {
    var canvas = raiz.querySelector("canvas");
    if (!canvas) return;

    var sp = 0.62;                 /* setpoint, 0..1 */
    var pv = 0.30, integral = 0, medAnterior = 0.30, u = 0;
    var atraso = [];               /* fila do tempo morto */
    var hist = [];                 /* [t, sp, pv] */
    var relogio = 0, acumulado = 0;
    var cor = {};

    function lerTema() {
      cor.traco = T.token(raiz, "--malha-traco", "#9FBEE0");
      /* AS RESERVAS ERAM UMA ARMADILHA: `--malha-pv` caia em #FDC500, que e a
         UNICA cor proibida fora do logo (CLAUDE.md, regra critica 4). Ela
         nunca disparou -- o token existe em style.css desde sempre --, mas
         era o unico #FDC500 do codigo de pagina, e num canvas: o grep de
         redline varre CSS e nunca teria achado. Trocadas pelos valores que
         os tokens de fato resolvem. */
      cor.pv = T.token(raiz, "--malha-pv", "#FFFFFF");
      cor.sp = T.token(raiz, "--malha-sp", "#B9D2EA");
      cor.grade = T.alfa(cor.traco, 0.16);
      cor.fraco = T.alfa(cor.traco, 0.55);
    }
    lerTema();

    /* --- um passo da malha ---------------------------------------------- */
    function integrar(dt) {
      var s = SINTONIA;
      var erro = sp - pv;

      /* DERIVADA SOBRE A MEDIÇÃO e com sinal invertido: sobre o erro, cada
         arrasto do setpoint daria um degrau na derivada e a saída saltaria --
         o "derivative kick". Sobre a medição, o termo só reage ao processo. */
      var dMed = (pv - medAnterior) / Math.max(dt, 1e-6);
      medAnterior = pv;

      var termoI = integral + s.ki * erro * dt;
      var bruto = s.kp * erro + termoI - s.kd * dMed;
      var sat = Math.max(0, Math.min(1, bruto));
      /* ANTI-WINDUP por clamp: a integral só acumula se a saída não estiver
         saturada, ou se o erro empurra para DENTRO da faixa. Sem isto a malha
         frouxa gruda no batente e volta com um atraso que não é do processo. */
      if (bruto === sat || erro * (sat - bruto) > 0) integral = termoI;
      u = sat;

      /* tempo morto: a planta recebe o que a malha mandou L segundos atrás */
      atraso.push(u);
      var n = Math.max(1, Math.round(L / dt));
      while (atraso.length > n) atraso.shift();
      var uAtrasado = atraso.length >= n ? atraso[0] : 0;

      /* primeira ordem */
      pv += (K * uAtrasado - pv) * (dt / TAU);
    }

    function avancar(dt) {
      acumulado += dt;
      var voltas = 0;
      while (acumulado >= PASSO && voltas < 240) {
        integrar(PASSO);
        relogio += PASSO;
        acumulado -= PASSO;
        voltas++;
        hist.push([relogio, sp, pv]);
      }
      while (hist.length && hist[0][0] < relogio - JANELA) hist.shift();
    }

    /* --- desenho --------------------------------------------------------- */
    var PAD = { e: 46, d: 14, c: 18, b: 26 };

    function xy(larg, alt, tempo, v) {
      var x = PAD.e + (larg - PAD.e - PAD.d) *
              (1 - (relogio - tempo) / JANELA);
      var y = alt - PAD.b - (alt - PAD.c - PAD.b) * v;
      return [x, y];
    }

    function pena(ctx, larg, alt, idx, c, larguraLinha, tracejada) {
      if (hist.length < 2) return;
      ctx.beginPath();
      for (var i = 0; i < hist.length; i++) {
        var p = xy(larg, alt, hist[i][0], hist[i][idx]);
        if (i === 0) ctx.moveTo(p[0], p[1]); else ctx.lineTo(p[0], p[1]);
      }
      ctx.strokeStyle = c;
      ctx.lineWidth = larguraLinha;
      ctx.lineJoin = "round";
      /* O SETPOINT E TRACEJADO E O PV E SOLIDO, que e como um registrador de
         verdade desenha os dois -- e aqui isso nao e citacao de estilo, e a
         segunda metade de um conserto de contraste. Ver a nota em style.css,
         em `.malha`: as duas linhas estavam na mesma cor a 1,20:1, e cor
         sozinha nao separa duas penas finas com seguranca. Cor MAIS padrao
         separa, e o padrao ainda funciona para quem nao distingue as duas
         cores -- que e a razao pela qual ele nao e opcional. */
      if (tracejada) ctx.setLineDash([6, 5]); else ctx.setLineDash([]);
      ctx.stroke();
      ctx.setLineDash([]);
    }

    function desenhar(ctx, larg, alt, tempoTotal, dt) {
      if (dt) avancar(dt);

      var x0 = PAD.e, x1 = larg - PAD.d;
      var y0 = PAD.c, y1 = alt - PAD.b;

      /* grade: cinco divisões, como um registrador de papel */
      ctx.strokeStyle = cor.grade;
      ctx.lineWidth = 1;
      ctx.beginPath();
      for (var i = 0; i <= 4; i++) {
        var y = y0 + (y1 - y0) * (i / 4);
        ctx.moveTo(x0, Math.round(y) + 0.5);
        ctx.lineTo(x1, Math.round(y) + 0.5);
      }
      for (var j = 0; j <= 5; j++) {
        var x = x0 + (x1 - x0) * (j / 5);
        ctx.moveTo(Math.round(x) + 0.5, y0);
        ctx.lineTo(Math.round(x) + 0.5, y1);
      }
      ctx.stroke();

      /* eixo, em filete forte */
      ctx.strokeStyle = cor.fraco;
      ctx.beginPath();
      ctx.moveTo(Math.round(x0) + 0.5, y0);
      ctx.lineTo(Math.round(x0) + 0.5, y1);
      ctx.lineTo(x1, Math.round(y1) + 0.5);
      ctx.stroke();

      /* O PV VEM DEPOIS E POR CIMA: onde as duas se encontram -- que e o
         momento inteiro da peca, a variavel alcancando a referencia -- quem
         tem de continuar visivel e o dado, nao a referencia. */
      pena(ctx, larg, alt, 1, cor.sp, 1, true);            /* setpoint */
      pena(ctx, larg, alt, 2, cor.pv, 2);                  /* PV */

      /* a alça do setpoint, na borda direita */
      var pSp = xy(larg, alt, relogio, sp);
      ctx.fillStyle = cor.sp;
      ctx.fillRect(x1 - 7, Math.round(pSp[1]) - 1, 7, 2);
      ctx.strokeStyle = cor.sp;
      ctx.lineWidth = 1;
      ctx.strokeRect(x1 - 6.5, Math.round(pSp[1]) - 5.5, 5, 11);

      /* rótulos em mono, sem escala: é diagrama, não leitura */
      /* CADA ROTULO NA COR DA PROPRIA PENA. O "SP" saia em `cor.fraco` --
         um terceiro tom, que nao era o da linha que ele nomeia.

         E OS DOIS SE AFASTAM QUANDO A MALHA ASSENTA. O regime permanente
         desta peca -- que e justamente o que ela existe para mostrar -- tem
         PV EM CIMA de SP, e os dois rotulos caiam no mesmo pixel: "SP" e "PV"
         impressos um sobre o outro viravam um borrao ilegivel, e ficavam
         assim para sempre, porque assentado e o estado final. Defeito
         encontrado na captura da peca animada, nao no codigo.

         SEPARACAO MINIMA DE 13px (a altura da linha do mono a 12px): abaixo
         disso eles se tocam. Quem cede e o SP, e nao o PV: o PV marca o dado,
         entao ele fica onde o dado esta e a referencia e que se desloca. Fora
         do regime permanente nada se move -- so entra quando encostam. */
      T.tipo(ctx, raiz);
      ctx.textBaseline = "middle";
      var ySp = xy(larg, alt, relogio, sp)[1];
      var yPv = xy(larg, alt, relogio, pv)[1];
      var SEPARA = 13;
      if (Math.abs(ySp - yPv) < SEPARA) {
        /* empurra o SP para o lado de onde ele ja estava; se estiverem
           exatamente juntos, para cima -- o setpoint e a referencia, e ela
           lê melhor acima da variavel que a persegue. */
        ySp = yPv + (ySp <= yPv ? -SEPARA : SEPARA);
      }
      ctx.fillStyle = cor.sp;
      ctx.fillText("SP", 8, ySp);
      ctx.fillStyle = cor.pv;
      ctx.fillText("PV", 8, yPv);
      ctx.fillStyle = cor.fraco;
      ctx.textBaseline = "top";
      ctx.fillText("MV " + Math.round(u * 100) + "%", x0 + 6, y0 + 4);
    }

    var peca = T.montar(raiz, { desenhar: desenhar });
    if (!peca) return;
    raiz.classList.add("is-viva");

    /* --- o setpoint é arrastável ---------------------------------------- */
    function daPonteiro(e) {
      var c = canvas.getBoundingClientRect();
      var v = 1 - (e.clientY - c.top - PAD.c) / Math.max(1, c.height - PAD.c - PAD.b);
      sp = Math.max(0.05, Math.min(0.95, v));
      peca.acordar();
    }
    var arrastando = false;
    canvas.addEventListener("pointerdown", function (e) {
      arrastando = true;
      canvas.setPointerCapture(e.pointerId);
      daPonteiro(e);
      e.preventDefault();
    });
    canvas.addEventListener("pointermove", function (e) {
      if (arrastando) daPonteiro(e);
    });
    canvas.addEventListener("pointerup", function () { arrastando = false; });
    canvas.addEventListener("pointercancel", function () { arrastando = false; });

    /* Teclado: a peça carrega informação, então tem de ser operável sem
       ponteiro. As setas movem o setpoint em degraus de 5%. */
    canvas.addEventListener("keydown", function (e) {
      var d = (e.key === "ArrowUp" || e.key === "ArrowRight") ? 0.05
            : (e.key === "ArrowDown" || e.key === "ArrowLeft") ? -0.05 : 0;
      if (!d) return;
      sp = Math.max(0.05, Math.min(0.95, sp + d));
      canvas.setAttribute("aria-valuenow", Math.round(sp * 100));
      peca.acordar();
      e.preventDefault();
    });


    /* Com movimento reduzido a malha não corre sozinha, mas o desenho tem de
       existir: roda um transitório de uma vez e mostra o resultado parado. */
    if (peca.reduzido) {
      for (var k = 0; k < Math.round(JANELA / PASSO); k++) {
        integrar(PASSO); relogio += PASSO; hist.push([relogio, sp, pv]);
      }
      while (hist.length && hist[0][0] < relogio - JANELA) hist.shift();
      peca.redesenhar();
    }
  }

  function iniciar() {
    var els = document.querySelectorAll("[data-malha]");
    for (var i = 0; i < els.length; i++) montar(els[i]);
  }
  if (document.readyState === "loading") {
    document.addEventListener("DOMContentLoaded", iniciar);
  } else {
    iniciar();
  }
})();
