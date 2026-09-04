/* ============================================================================
   mimico.js — a tela de supervisão que roda no campo
   i3Automations

   O QUE ESTA PEÇA É. Um sinóptico de SCADA: dois tanques com nível, uma bomba
   girando, válvulas, linhas de processo com o fluxo correndo e os tags em
   mono. É literalmente o ARTEFATO QUE A EMPRESA ENTREGA -- a tela que o
   operador olha o turno inteiro depois que a i3 vai embora.

   POR QUE EM PAST PERFORMANCE. A página se chama "What already runs in the
   field". Todas as outras provas dela são fotografia e número; esta é a única
   que mostra a COISA em si.

   POR QUE NÃO É OUTRA PLANTA. `planta.js` é o SÍTIO em isométrico, desenhado
   em aresta, com telemetria correndo pelos enlaces. Esta é a TELA: ortogonal,
   chapada, com símbolo de instrumento e leitura numérica. Um é o lugar, o
   outro é o que se vê do lugar -- e é por isso que as duas cabem no mesmo site
   sem competir.

   A HONESTIDADE DA PEÇA, e ela é declarada na própria tela. Os valores são
   simulados e os tags são genéricos (`LIT-201`, `FIC-101`), com a nota
   "DEMONSTRATION MIMIC" no rodapé do sinóptico. Este projeto já tirou uma
   afirmação de autoria da galeria por mostrar uma coisa e afirmar outra; um
   sinóptico sem essa nota afirmaria ser a planta de um cliente.

   Sem WebGL: canvas 2D sobre `tela.js`.
   ============================================================================ */
(function () {
  "use strict";
  if (!window.I3Tela) return;

  var T = window.I3Tela;

  function montar(raiz) {
    var cor = {};
    function lerTema() {
      cor.traco = T.token(raiz, "--mimico-traco", "#9FBEE0");
      cor.vivo = T.token(raiz, "--mimico-vivo", "#FDC500");
      cor.tinta = T.token(raiz, "--mimico-tinta", "#FFFFFF");
      cor.grade = T.alfa(cor.traco, 0.14);
      cor.fraco = T.alfa(cor.traco, 0.55);
      cor.cheio = T.alfa(cor.traco, 0.22);
    }
    lerTema();

    /* --- o processo simulado ---------------------------------------------
       Um tanque enche por uma bomba e esvazia por uma válvula de saída; o
       segundo recebe o transbordo. Nada aqui pretende ser um modelo: é o
       suficiente para os números se moverem de forma coerente entre si, que
       é o que faz um sinóptico parecer vivo em vez de parecer um desenho. */
    var n1 = 0.42, n2 = 0.58, vazao = 0.0, giro = 0, bomba = true;
    var alarme = 0;
    /* Altura do tipo em UNIDADES LOCAIS. Vale 12/m e é recalculada a cada
       quadro; tudo que fica ao lado de uma letra se mede por ela, e não por
       constante fixa -- senão o rótulo encolhe e o vão em volta não. */
    var TIPO = 12;

    function processo(dt) {
      var alvo = bomba ? 0.78 : 0.15;
      vazao += ((bomba ? 0.62 : 0.02) - vazao) * dt * 1.4;
      n1 += (alvo - n1) * dt * 0.16;
      n2 += (0.5 + 0.28 * Math.sin(giro * 0.11) - n2) * dt * 0.22;
      giro += dt * (bomba ? 3.4 : 0.2);
      /* a bomba alterna sozinha, como um controle de nível por histerese */
      if (bomba && n1 > 0.76) bomba = false;
      if (!bomba && n1 < 0.22) bomba = true;
      alarme = n1 > 0.74 ? Math.min(1, alarme + dt * 3) : Math.max(0, alarme - dt * 2);
    }

    /* --- primitivas do sinóptico ------------------------------------------ */
    function caixa(ctx, x, y, w, h) {
      ctx.strokeStyle = cor.fraco;
      ctx.lineWidth = 1;
      ctx.strokeRect(Math.round(x) + 0.5, Math.round(y) + 0.5,
                     Math.round(w), Math.round(h));
    }

    function tanque(ctx, x, y, w, h, nivel, tag, u) {
      caixa(ctx, x, y, w, h);
      var alt = Math.max(0, Math.min(1, nivel)) * (h - 4);
      ctx.fillStyle = cor.cheio;
      ctx.fillRect(Math.round(x) + 2, Math.round(y + h - 2 - alt),
                   Math.round(w) - 3, Math.round(alt));
      /* a linha do nível, que é o que o operador de fato lê */
      ctx.strokeStyle = cor.vivo;
      ctx.lineWidth = 1.5;
      ctx.beginPath();
      ctx.moveTo(x + 2, Math.round(y + h - 2 - alt) + 0.5);
      ctx.lineTo(x + w - 2, Math.round(y + h - 2 - alt) + 0.5);
      ctx.stroke();
      /* marcas de escala a cada 25% */
      ctx.strokeStyle = cor.fraco;
      ctx.lineWidth = 1;
      ctx.beginPath();
      for (var i = 1; i < 4; i++) {
        var yy = Math.round(y + h - 2 - (h - 4) * (i / 4)) + 0.5;
        ctx.moveTo(x + w - 6, yy); ctx.lineTo(x + w - 1, yy);
      }
      ctx.stroke();
      ctx.fillStyle = cor.fraco;
      ctx.textAlign = "center";
      /* uma linha abaixo da base e meia linha acima do topo -- medidos EM
         TIPO, para o rótulo não descolar do tanque quando a caixa muda */
      ctx.fillText(tag, x + w / 2, y + h + TIPO * 1.15);
      ctx.fillStyle = cor.tinta;
      ctx.fillText(Math.round(nivel * 100) + u, x + w / 2, y - TIPO * 0.45);
      ctx.textAlign = "left";
    }

    function linha(ctx, pts, corrida) {
      ctx.strokeStyle = cor.fraco;
      ctx.lineWidth = 1;
      ctx.beginPath();
      for (var i = 0; i < pts.length; i += 2) {
        var x = Math.round(pts[i]) + 0.5, y = Math.round(pts[i + 1]) + 0.5;
        if (i === 0) ctx.moveTo(x, y); else ctx.lineTo(x, y);
      }
      ctx.stroke();
      if (corrida === null) return;
      /* O FLUXO. Tracejado deslocando ao longo da tubulação -- a convenção
         que todo sinóptico usa para dizer "tem produto passando aqui". A
         velocidade é a vazão, então parar a bomba PARA o tracejado. */
      ctx.save();
      ctx.strokeStyle = cor.vivo;
      ctx.lineWidth = 2;
      ctx.setLineDash([5, 11]);
      ctx.lineDashOffset = -corrida;
      ctx.stroke();
      ctx.restore();
    }

    function valvula(ctx, x, y, aberta) {
      var s = 5;
      ctx.strokeStyle = aberta ? cor.vivo : cor.fraco;
      ctx.lineWidth = 1.4;
      ctx.beginPath();
      ctx.moveTo(x - s, y - s); ctx.lineTo(x + s, y + s);
      ctx.lineTo(x + s, y - s); ctx.lineTo(x - s, y + s);
      ctx.closePath();
      ctx.stroke();
    }

    function bombaSimbolo(ctx, x, y, r, ang, ligada) {
      ctx.strokeStyle = ligada ? cor.vivo : cor.fraco;
      ctx.lineWidth = 1.4;
      ctx.beginPath();
      ctx.arc(x, y, r, 0, Math.PI * 2);
      ctx.stroke();
      /* o rotor: duas pás girando. É o único elemento redondo do site, e é
         convenção de P&ID -- não decoração. */
      ctx.beginPath();
      for (var k = 0; k < 2; k++) {
        var a = ang + k * Math.PI;
        ctx.moveTo(x, y);
        ctx.lineTo(x + Math.cos(a) * (r - 2), y + Math.sin(a) * (r - 2));
      }
      ctx.stroke();
    }

    function desenhar(ctx, larg, alt, t, dt) {
      if (dt) processo(dt);
      ctx.textBaseline = "alphabetic";

      /* retícula de fundo, como a tela de um supervisório */
      ctx.strokeStyle = cor.grade;
      ctx.lineWidth = 1;
      ctx.beginPath();
      for (var gx = 24; gx < larg; gx += 24) {
        ctx.moveTo(Math.round(gx) + 0.5, 0); ctx.lineTo(Math.round(gx) + 0.5, alt);
      }
      for (var gy = 24; gy < alt; gy += 24) {
        ctx.moveTo(0, Math.round(gy) + 0.5); ctx.lineTo(larg, Math.round(gy) + 0.5);
      }
      ctx.stroke();

      /* a composição escala com a caixa, mas mantém proporções fixas */
      var m = Math.min(larg / 520, alt / 260);
      ctx.save();
      ctx.translate((larg - 520 * m) / 2, (alt - 260 * m) / 2);
      ctx.scale(m, m);

      /* A TIPOGRAFIA NÃO ESCALA COM O DESENHO, e este é o conserto de 20/08.
         A composição inteira vive num espaço local de 520x260 e é ampliada
         para caber na caixa -- a 1440 o fator é 2,46. Com a fonte declarada em
         `11px` DENTRO desse espaço, o rótulo saía na tela com **27,1 px**:
         mais que o dobro do maior mono do site, que vai de 11 a 13.

         Pior que o tamanho era a instabilidade: `m` muda com a janela, então a
         tipografia da peça não tinha relação nenhuma com a escala do site --
         crescia e encolhia sozinha enquanto todo o resto obedece a um clamp.

         Dividir por `m` cancela a ampliação: o texto é posicionado no espaço
         local, junto do desenho, e RENDERIZA no tamanho de tela declarado.

         12 px com .14em é o registro da linha de cota da prancha
         (`.prancha__cota`) -- que é exatamente o que um rótulo de sinóptico é:
         anotação sobre um desenho, não corpo de texto. */
      TIPO = T.tipo(ctx, raiz, 1 / m);

      var corrida = t * 46;
      tanque(ctx, 36, 58, 74, 132, n1, "LIT-201", "%");
      tanque(ctx, 404, 58, 74, 132, n2, "LIT-204", "%");

      /* sucção → bomba → recalque → segundo tanque */
      linha(ctx, [110, 168, 168, 168], bomba ? corrida : null);
      bombaSimbolo(ctx, 186, 168, 15, giro, bomba);
      linha(ctx, [204, 168, 250, 168, 250, 96, 404, 96], bomba ? corrida : null);
      valvula(ctx, 300, 96, bomba);

      /* retorno por gravidade */
      linha(ctx, [404, 168, 330, 168, 330, 214, 74, 214, 74, 190], null);
      valvula(ctx, 200, 214, true);

      /* instrumentos: o círculo com o tag é a bolha de ISA-5.1 */
      function bolha(x, y, tag) {
        ctx.strokeStyle = cor.fraco;
        ctx.lineWidth = 1;
        /* raio em unidades LOCAIS que correspondem a ~26 px de tela: a bolha
           acompanha o texto, senão fica um círculo grande com duas letrinhas
           perdidas no meio. */
        var r = 13 / m;
        ctx.beginPath(); ctx.arc(x, y, r, 0, Math.PI * 2); ctx.stroke();
        ctx.fillStyle = cor.fraco;
        ctx.textAlign = "center";
        ctx.fillText(tag.slice(0, 3), x, y - TIPO * 0.1);
        ctx.fillText(tag.slice(4), x, y + TIPO * 0.85);
        ctx.textAlign = "left";
      }
      bolha(250, 40, "FIC-101");
      ctx.strokeStyle = cor.fraco;
      ctx.setLineDash([2, 3]);
      ctx.beginPath(); ctx.moveTo(250, 53); ctx.lineTo(250, 88); ctx.stroke();
      ctx.setLineDash([]);

      /* leitura de vazão e estado da bomba */
      ctx.fillStyle = cor.tinta;
      ctx.fillText((vazao * 180).toFixed(0) + " m3/h", 214, 148);
      ctx.fillStyle = bomba ? cor.vivo : cor.fraco;
      ctx.fillText(bomba ? "P-101  RUN" : "P-101  STOP", 158, 200);

      /* faixa de alarme: só acende quando o nível alto é atingido */
      if (alarme > 0.02) {
        ctx.globalAlpha = alarme;
        ctx.strokeStyle = cor.vivo;
        ctx.lineWidth = 1;
        var hf = TIPO * 1.7;
        ctx.strokeRect(28.5, 8.5, 463, hf);
        ctx.fillStyle = cor.vivo;
        ctx.fillText("LAH-201   TK-201 LEVEL HIGH", 38, 8.5 + hf * 0.72);
        ctx.globalAlpha = 1;
      }

      /* A NOTA QUE MANTÉM A PEÇA HONESTA. Sem ela o sinóptico afirma ser a
         planta de um cliente, e não é: os valores são simulados. */
      ctx.fillStyle = cor.fraco;
      ctx.fillText("DEMONSTRATION MIMIC · SIMULATED VALUES", 28, 260 - TIPO * 0.4);
      ctx.restore();
    }

    var peca = T.montar(raiz, { desenhar: desenhar });
    if (peca) raiz.classList.add("is-viva");
  }

  function iniciar() {
    var els = document.querySelectorAll("[data-mimico]");
    for (var i = 0; i < els.length; i++) montar(els[i]);
  }
  if (document.readyState === "loading") {
    document.addEventListener("DOMContentLoaded", iniciar);
  } else {
    iniciar();
  }
})();
