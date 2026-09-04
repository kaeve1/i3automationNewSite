/* ============================================================================
   mosaico.js — reempilha as colunas da galeria quando a largura muda
   ============================================================================

   POR QUE ISTO EXISTE. A galeria deixou de usar `columns` do CSS e passou a
   ter três COLUNAS DE VERDADE, cada uma um elemento. O motivo é um só: coluna
   que é elemento pode ter deriva própria na rolagem, e é a deriva que dá
   profundidade ao acervo. Com `columns` não há o que animar — é uma caixa só.

   O preço é este arquivo. `columns` redistribui sozinho quando a largura muda;
   três elementos não. Então a distribuição vira responsabilidade nossa, e é
   ela que este módulo faz — e SÓ ela.

   O QUE ELE NÃO FAZ, e isso é o desenho: ele não monta a galeria. O gerador
   (`_empilhar()` em ferramentas/build_site.py) já entrega as três colunas
   empilhadas e equilibradas no HTML. Sem JavaScript, ou antes de ele rodar, a
   página já está certa em três colunas — este módulo só entra quando o
   visitante está abaixo de 1100 px, ou quando ele redimensiona a janela.

   O CRITÉRIO É O MESMO DOS DOIS LADOS. Guloso pela coluna mais curta até
   então, com a altura de cada peça estimada em unidades de LARGURA DE COLUNA:
   `1 / proporção` mais a legenda. Round-robin (`i % n`) seria uma linha e
   estaria errado — com proporções de 0,66 a 1,60 as colunas terminariam com
   centenas de pixels de diferença.

   A proporção vem de `data-ar`, que o gerador MEDIU no arquivo em disco. Não
   se lê `naturalWidth` aqui de propósito: isso obrigaria a esperar 29 imagens
   carregarem para poder empilhar, que é justamente o rearranjo tardio que o
   `aspect-ratio` do CSS existe para evitar.

   As figuras são reordenadas por `data-ordem`, que é a ordem CURADA do acervo
   em build_site.py — não a ordem em que elas por acaso ficaram no DOM depois
   de um empilhamento anterior. Sem isso, dois redimensionamentos seguidos
   embaralhariam a galeria.
   ============================================================================ */
(function () {
  "use strict";

  var mosaico = document.querySelector("[data-mosaico]");
  if (!mosaico) return;

  var colunas = [].slice.call(mosaico.children);
  if (!colunas.length) return;

  var figuras = [].slice.call(mosaico.querySelectorAll(".galeria__figura"))
    .sort(function (a, b) {
      return (a.getAttribute("data-ordem") | 0) - (b.getAttribute("data-ordem") | 0);
    });
  if (!figuras.length) return;

  /* Legenda + goteira, em larguras de coluna. É o mesmo valor de
     `_empilhar()`: se os dois divergirem, a página muda de arranjo ao
     redimensionar de volta para a largura em que ela nasceu. */
  var LEGENDA = 0.18;

  /* Os mesmos dois pontos de quebra do CSS (§21.4). Ficam aqui como números e
     não como `matchMedia` porque são três estados de UMA grandeza, e ler a
     largura uma vez é mais barato que manter três listeners de media query. */
  var quantas = function () {
    var w = window.innerWidth || document.documentElement.clientWidth;
    return w <= 700 ? 1 : (w <= 1100 ? 2 : 3);
  };

  /* O estado inicial é o que o GERADOR escreveu, e ele diz quantas colunas
     usou. Começar em 0 obrigaria um reempilhamento no carregamento de toda
     visita em desktop — um refluxo de 29 figuras para chegar exatamente ao
     arranjo que já estava na tela. */
  var atual = parseInt(mosaico.getAttribute("data-colunas"), 10) || colunas.length;

  var montar = function (n) {
    if (n === atual) return;
    atual = n;
    mosaico.setAttribute("data-colunas", n);

    var alturas = [];
    var i;
    for (i = 0; i < colunas.length; i++) {
      /* A coluna que sobra sai do fluxo. Vazia e visível ela ainda ocuparia
         uma célula da grade, e as duas em uso encolheriam para dois terços. */
      colunas[i].style.display = i < n ? "" : "none";
      if (i < n) {
        /* As figuras estão referenciadas em `figuras`: esvaziar a coluna as
           desanexa, não as destrói. */
        while (colunas[i].firstChild) colunas[i].removeChild(colunas[i].firstChild);
        alturas.push(0);
      }
    }

    for (i = 0; i < figuras.length; i++) {
      var k = 0;
      var j;
      for (j = 1; j < alturas.length; j++) if (alturas[j] < alturas[k]) k = j;
      colunas[k].appendChild(figuras[i]);
      var ar = parseFloat(figuras[i].getAttribute("data-ar")) || 1;
      alturas[k] += 1 / ar + LEGENDA;
    }
  };

  /* Coalescido no quadro: um arrasto de borda de janela dispara `resize`
     dezenas de vezes por segundo, e reempilhar 29 figuras em cada um trava a
     aba. `montar()` sai na primeira linha quando o número não mudou, então o
     custo real é uma leitura de largura por quadro. */
  var pendente = false;
  var pedir = function () {
    if (pendente) return;
    pendente = true;
    window.requestAnimationFrame(function () {
      pendente = false;
      montar(quantas());
    });
  };

  window.addEventListener("resize", pedir);
  window.addEventListener("orientationchange", pedir);
  montar(quantas());
})();
