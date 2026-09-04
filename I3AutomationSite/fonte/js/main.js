/* ============================================================================
   i3Automations — comportamento
   HTML + CSS + JS puro, sem framework e sem build (design.md §9).

   2. nav ao rolar            3. menu no toque
   4. revelação ao rolar      5. intro: o notebook abre  6. deriva por ponteiro
   6b. lente sobre o texto    7. progresso de rolagem  8. dominó da lista
   9. ano corrente           10. rodapé revelado    11. inércia da roda
   12. aviso de armazenamento  13. vídeo dos momentos  14. pausa do herói

   O módulo 1 era o alternador de tema. Saiu em 2026-08-25 junto com o tema
   escuro inteiro (design.md §1.4 regra 6) — e com ele saiu o evento
   `temachange`, que era o único jeito de as peças em canvas saberem que os
   tokens de cor tinham mudado. A numeração começa em 2 de propósito: ela é
   a mesma do UnidoCLP, e renumerar tornaria as duas ilegíveis lado a lado.
   ============================================================================ */
(function () {
  "use strict";

  var reduzido = window.matchMedia("(prefers-reduced-motion: reduce)").matches;

  /* ---------- 2. Nav ao rolar ---------- */
  (function () {
    var nav = document.querySelector(".nav");
    if (!nav || !nav.classList.contains("nav--sobre-heroi")) return;

    var limite = Math.max(120, window.innerHeight * 0.62);
    var ticando = false;

    var avaliar = function () {
      nav.classList.toggle("is-rolado", window.scrollY > limite);
      ticando = false;
    };
    window.addEventListener("scroll", function () {
      if (ticando) return;
      ticando = true;
      window.requestAnimationFrame(avaliar);
    }, { passive: true });
    window.addEventListener("resize", function () {
      limite = Math.max(120, window.innerHeight * 0.62);
      avaliar();
    });
    avaliar();
  })();

  /* ---------- 3. Menu no toque ---------- */
  (function () {
    var botao = document.querySelector(".nav__hamburguer");
    var painel = document.getElementById("menu-mobile");
    if (!botao || !painel) return;

    var fechar = function () {
      botao.setAttribute("aria-expanded", "false");
      painel.classList.remove("is-aberto");
    };

    botao.addEventListener("click", function () {
      var aberto = botao.getAttribute("aria-expanded") === "true";
      botao.setAttribute("aria-expanded", aberto ? "false" : "true");
      painel.classList.toggle("is-aberto", !aberto);
    });
    painel.addEventListener("click", function (e) {
      if (e.target.tagName === "A") fechar();
    });
    document.addEventListener("keydown", function (e) {
      if (e.key === "Escape") fechar();
    });
    window.addEventListener("resize", function () {
      if (window.innerWidth > 1100) fechar();
    });
  })();

  /* ---------- 4. Revelação ao rolar ----------
     Um observador só, que marca e para de observar. O atraso em cascata vem
     de --i no elemento, nunca de uma classe por item (design.md §7). */
  (function () {
    var alvos = Array.prototype.slice.call(document.querySelectorAll(".reveal"));

    /* O RODAPÉ PRESO JÁ ESTÁ DENTRO DA JANELA desde a carga -- escondido atrás
       do <main>, mas o IntersectionObserver não enxerga oclusão, só geometria.
       Deixar a frase de fecho aqui faria ela se plotar inteira no primeiro
       quadro, atrás do conteúdo: o visitante chegaria ao fim do site com a
       animação já gasta. Quem a revela nesse modo é o §10. */
    var rodape = document.querySelector(".rodape");
    if (rodape && window.getComputedStyle(rodape).position === "sticky") {
      alvos = alvos.filter(function (el) {
        return !el.classList.contains("rodape__headline");
      });
    }
    if (!alvos.length) return;
    if (reduzido || !window.IntersectionObserver) {
      for (var i = 0; i < alvos.length; i++) alvos[i].classList.add("is-visivel");
      return;
    }
    var io = new IntersectionObserver(function (entradas) {
      entradas.forEach(function (e) {
        if (!e.isIntersecting) return;
        e.target.classList.add("is-visivel");
        io.unobserve(e.target);
      });
    }, { rootMargin: "0px 0px -12% 0px", threshold: 0.08 });
    for (var j = 0; j < alvos.length; j++) io.observe(alvos[j]);

    /* REDE DE SEGURANCA, e ela fecha um buraco real.
       Havia saida para dois casos -- `prefers-reduced-motion` e navegador sem
       IntersectionObserver -- e nenhuma para o terceiro: o IO EXISTE e nunca
       dispara.

       Nao e hipotetico. Numa aba de segundo plano o navegador nao entrega
       callback de IO; a pagina PINTA (uma captura de tela a mostra) mas nada
       recebe `is-visivel`. O estado base de `.reveal` e `opacity: 0` com
       desfoque, entao o que o visitante encontra e uma pagina em branco com o
       logo em cima. Ao voltar para a aba o IO acorda e conserta sozinho -- mas
       "conserta sozinho na maioria das vezes" nao e a mesma coisa que
       "conteudo sempre aparece".

       E a MESMA armadilha que este arquivo ja registra duas vezes para a intro
       e para a frase dela: estado inicial de animacao que ESCONDE conteudo. A
       diferenca e que la o conserto foi por CSS, e aqui tem de ser por tempo,
       porque quem esconde e uma classe que so o JS poe.

       6 segundos: bem depois de qualquer revelacao legitima (a mais lenta e
       .85s mais 70ms por item), e bem antes de alguem desistir da pagina. */
    window.setTimeout(function () {
      for (var k = 0; k < alvos.length; k++) alvos[k].classList.add("is-visivel");
      io.disconnect();
    }, 6000);
  })();

  /* ---------- 5. Intro: o notebook da marca abre ----------
     TERCEIRA INTRO DO PROJETO, reescrita em 2026-08-27 a pedido do usuário:
     *"o computador (logo do i3) está fechado no plano start, e se abre e
     preenche a tela, como se o site fosse a tela do notebook."*

     A v1 — o lockup revelado da esquerda para a direita — está salva inteira
     em `melhorias/intro-v1/`, com o procedimento de volta. Foi a primeira
     coisa desta rodada, antes de qualquer alteração.

     O MECANISMO INTEIRO É CSS, e é de propósito. `style.css` §5 gira a tampa
     na dobradiça, escreve a frase e recolhe os quatro painéis que revelam a
     página. Nada disso passa por aqui: são `transform` e `clip-path` em
     keyframes, que rodam na composição.

     O QUE SOBRA PARA O JS são as três coisas que o CSS não alcança:

       1. medir a frase em pixels, porque o cursor caminha por `translateX` e
          `ch` mente em tipo proporcional;
       2. tirar a intro do caminho na hora certa;
       3. garantir que ela termine mesmo quando o navegador congela a aba —
          uma aba em segundo plano não recebe `requestAnimationFrame` nem
          roda animações, e sem a rede de segurança a intro ficaria pendurada
          cobrindo o site.

     Linha do tempo, 4,1s (a v1 levava 5,6):
       0,15 → 1,05s  a tampa gira de −92° a 0
       0,95 → 1,55s  a frase se escreve
       1,55 → 2,75s  a pausa em que ela é lida
       2,75 → 3,95s  os painéis recuam: a tela do notebook vira a página
       4,10s         este módulo remove a intro */
  (function () {
    var intro = document.querySelector(".intro");
    if (!intro) return;

    var encerrado = false;

    var encerrar = function () {
      if (encerrado) return;
      encerrado = true;
      document.documentElement.classList.remove("intro-ativa");
      if (intro.parentNode) intro.parentNode.removeChild(intro);
    };

    /* O numero tem de casar com a linha do tempo de style.css §5: ali o
       ultimo painel termina em 3,95s, e o JS remove a peca 150ms depois.
       Subiu de 3250 para 4100 em 2026-08-27, quando a frase ganhou 1,2s de
       PAUSA para ser lida -- antes ela ficava inteira na tela por 0,15s. */
    var TOTAL = 4100;

    /* O VEU NAO E MAIS ANIMADO AQUI. Na v1 o JS levantava a opacidade da
       intro inteira por WAAPI, e o `onfinish` dela era o gatilho do fim.
       Na v3 quem revela a pagina sao os quatro paineis, em CSS, por
       `transform` -- entao o JS so precisa saber A HORA de tirar o elemento
       do caminho. Menos uma animacao concorrendo com as outras cinco. */
    var animar = function () {
      window.setTimeout(encerrar, reduzido ? 600 : TOTAL);
    };

    /* O cursor da frase caminha por transform, então precisa da largura real
       do texto em pixels — a única medida que o CSS sozinho não alcança. */
    var texto = intro.querySelector(".intro__texto");
    if (texto) {
      /* Abaixo de 440px a frase quebra em duas linhas (CSS §5) e o cursor
         passa a percorrer uma de cada vez, então ali quem importa é a largura
         de CADA linha e não a da frase. As tres medidas saem juntas: custa um
         `getBoundingClientRect` a mais e evita um segundo caminho de codigo
         que so roda no celular -- ou seja, o caminho que ninguem testa.

         `--largura-frase` continua sendo escrita como sempre: no desktop as
         duas linhas sao `display: inline` e a caixa do `.intro__texto` e a
         reta unica de sempre. */
      var linhas = texto.querySelectorAll(".intro__linha");
      var medirFrase = function () {
        intro.style.setProperty("--largura-frase",
          Math.round(texto.getBoundingClientRect().width) + "px");
        for (var i = 0; i < linhas.length && i < 2; i++) {
          intro.style.setProperty("--l" + (i + 1),
            Math.round(linhas[i].getBoundingClientRect().width) + "px");
        }
      };
      medirFrase();
      if (document.fonts && document.fonts.ready) document.fonts.ready.then(medirFrase);
    }

    /* Rede de segurança que não depende de requestAnimationFrame: numa aba em
       segundo plano o navegador congela rAF e as animações, e sem isto a
       intro ficaria presa cobrindo o site. */
    window.setTimeout(encerrar, 5600);

    /* Quem abre o site numa aba de fundo não deve encontrar uma abertura de
       cinco segundos ao voltar: nesse caso a intro simplesmente não acontece. */
    if (document.visibilityState !== "visible") { encerrar(); return; }

    var iniciado = false;
    var iniciar = function () {
      if (iniciado) return;
      iniciado = true;
      window.requestAnimationFrame(animar);
    };
    /* Esperar o "load" da página inteira atrasaria a intro por segundos sem
       necessidade: as duas peças somam 13 KB e já estão no HTML. */
    if (document.fonts && document.fonts.ready) document.fonts.ready.then(iniciar);
    window.setTimeout(iniciar, 900);

    /* quem já conhece o site pula: clique, tecla ou rolagem encerram na hora */
    intro.addEventListener("click", encerrar);
    window.addEventListener("keydown", encerrar, { once: true });
    window.addEventListener("wheel", encerrar, { once: true, passive: true });
    window.addEventListener("touchstart", encerrar, { once: true, passive: true });
  })();

  /* ---------- 6. Deriva por ponteiro ----------
     Movimento por ponteiro é aceito; por rolagem, não (design.md §7 regra 5).
     Amplitude máxima de 18px, e o alvo é interpolado — sem isso a peça gruda
     no cursor e perde a inércia que a faz parecer massa. */
  (function () {
    if (reduzido) return;
    var alvos = document.querySelectorAll("[data-deriva]");
    if (!alvos.length || window.matchMedia("(hover: none)").matches) return;

    var mx = 0, my = 0, ax = 0, ay = 0, rodando = false;
    var AMPLITUDE = 18;

    var passo = function () {
      ax += (mx - ax) * 0.06;
      ay += (my - ay) * 0.06;
      for (var i = 0; i < alvos.length; i++) {
        var f = parseFloat(alvos[i].getAttribute("data-deriva")) || 1;
        alvos[i].style.transform =
          "translate3d(" + (ax * AMPLITUDE * f).toFixed(2) + "px," +
          (ay * AMPLITUDE * f).toFixed(2) + "px,0)";
      }
      if (Math.abs(mx - ax) > 0.001 || Math.abs(my - ay) > 0.001) {
        window.requestAnimationFrame(passo);
      } else {
        rodando = false;
      }
    };

    window.addEventListener("pointermove", function (e) {
      mx = (e.clientX / window.innerWidth - 0.5) * 2;
      my = (e.clientY / window.innerHeight - 0.5) * 2;
      if (!rodando) { rodando = true; window.requestAnimationFrame(passo); }
    }, { passive: true });
  })();

  /* ---------- 6b. Lente sobre o texto do herói ----------
     O braço acende sob o ponteiro; sem isto o texto ficaria inerte ao lado, e
     o herói teria dois comportamentos em vez de um instrumento só.

     O JS só publica a POSIÇÃO — a aparência inteira é do CSS. E publica em
     coordenadas locais de cada alvo, porque `background-clip: text` recorta o
     fundo de CADA elemento: um gradiente em coordenada de página apareceria
     deslocado em cada linha da headline.

     Um `requestAnimationFrame` por movimento, não um por evento: o ponteiro
     dispara dezenas de eventos por quadro e cada um custa um
     `getBoundingClientRect` por alvo — que é leitura de layout. */
  (function () {
    var heroi = document.querySelector(".heroi");
    if (!heroi || window.matchMedia("(hover: none)").matches) return;
    var alvos = heroi.querySelectorAll("[data-lente-texto]");
    if (!alvos.length) return;

    var x = 0, y = 0, pendente = false;

    var pintar = function () {
      pendente = false;
      for (var i = 0; i < alvos.length; i++) {
        var r = alvos[i].getBoundingClientRect();
        alvos[i].style.setProperty("--lente-x", (x - r.left).toFixed(1) + "px");
        alvos[i].style.setProperty("--lente-y", (y - r.top).toFixed(1) + "px");
      }
    };

    heroi.addEventListener("pointermove", function (e) {
      x = e.clientX; y = e.clientY;
      if (!pendente) { pendente = true; window.requestAnimationFrame(pintar); }
    });

    heroi.addEventListener("pointerleave", function () {
      for (var i = 0; i < alvos.length; i++) {
        alvos[i].style.setProperty("--lente-x", "-9999px");
      }
    });
  })();

  /* ---------- 7. Progresso de rolagem ----------
     Publica `--p` (0..1) em `[data-progresso]` conforme o elemento atravessa a
     janela. É o motor das três coisas que reagem à rolagem no site: a prancha
     da home, o painel de setores de past-performance e a galeria.

     A ROLAGEM CONTINUA NATIVA, e isto não é detalhe de implementação. O
     `memoria.md` registra a decisão: não sequestramos a roda com JavaScript,
     porque isso quebra o gesto de quem usa trackpad, teclado ou leitor de
     tela — e `scroll-behavior: smooth` do site depende de a roda ser do
     navegador. Aqui só LEMOS a posição; ninguém chama `preventDefault`, e
     `passive: true` garante que não dá nem para tentar.

     Duas leituras, escolhidas pela altura do próprio elemento:

       CENA PRESA (bem mais alta que a janela) — o caso da seção com painel
         `sticky`. O curso é `altura - janela`: 0 quando o topo encosta no topo
         da janela, 1 quando o fundo encosta no fundo dela. É exatamente o
         trecho em que o painel fica preso.

       TRAVESSIA (todo o resto) — o caso da prancha e o de cada figura da
         galeria. O curso é a travessia inteira, de entrar pelo pé da janela a
         sair pelo topo.

     O LIMIAR DE 0,5 JANELA ENTROU EM 2026-08-27, CONSERTANDO UM DEFEITO REAL.
     A condição era `curso > 0` — qualquer elemento um pixel mais alto que a
     janela caía na leitura de cena presa. Uma figura da galeria não é uma cena
     presa; ela só é alta. Medida a figura 13 (`fiacao`, a mais retrato do
     acervo, proporção 0,6604) numa janela de 1440x700:

       scrollY   topo   visível    --p    opacity
          2556    263      62%   0,0000     0,00
          2730     85      87%   0,0000     0,00
          2788     26      95%   0,0000     0,00   <- quase inteira na tela
          2846    -65      91%   1,0000     1,00   <- e ESTALA para 1

     `curso` valia 708 − 700 = **8px**: a animação inteira acontecia em oito
     pixels de rolagem, e só depois de o topo da figura já ter saído por cima.
     O visitante via um buraco branco durante toda a entrada e um estalo no
     fim — nunca a revelação.

     0,5 É FOLGADO DOS DOIS LADOS, e os números são medidos, não estimados.
     Levantados todos os consumidores de `[data-progresso]` do site a 1440x700,
     em cursos por janela:

       cena presa mais CURTA .......... 1,500  (`.unidade`, `.secao--presa`)
       `.filme` ....................... 1,600
       `.cobertura` ................... 2,000
       `.galeria__mosaico` ............ 6,300
       ---------------------------------------- limiar 0,5
       figura 13 ...................... 0,011
       figura 28 ...................... 0,003

     Três vezes abaixo da menor cena legítima e trinta vezes acima da maior
     figura quebrada. Não há nada perto do limiar.

     Ler layout dentro do próprio evento de rolagem é o que causa engasgo; por
     isso a medição é adiada para o quadro seguinte com `requestAnimationFrame`
     e coalescida por `pendente`. */
  (function () {
    var alvos = document.querySelectorAll("[data-progresso]");
    if (!alvos.length) return;

    /* Com movimento reduzido não há progresso: tudo nasce no estado final.
       Uma animação atada à rolagem é das que mais provocam enjoo. */
    if (reduzido) {
      for (var i = 0; i < alvos.length; i++) {
        alvos[i].style.setProperty("--p", "1");
        alvos[i].classList.add("is-estatico");
      }
      return;
    }

    var pendente = false;
    /* Alocado uma vez: o laco roda por quadro de rolagem e nao pode gerar lixo. */
    var caixas = new Array(alvos.length);

    /* DUAS PASSAGENS, E A SEPARACAO E O PONTO. A primeira versao lia
       `getBoundingClientRect()` e escrevia `--p` no MESMO laco: a escrita suja
       o estilo, e a leitura do elemento seguinte forca o navegador a
       recalcular estilo e layout ali mesmo, de forma sincrona. Na galeria sao
       30 alvos, entao eram 30 layouts forcados por quadro -- e justamente na
       pagina mais pesada, no aparelho mais fraco.

       Separadas, o navegador faz UM layout para as 30 leituras e depois
       recebe as 30 escritas sem nada entre elas. E o descarte do que esta fora
       da tela passou para a segunda passagem: adiantar o `continue` nao
       poupava nada, porque o retangulo ja tinha sido lido para decidir. */
    var medir = function () {
      pendente = false;
      var vh = window.innerHeight || 1;
      var k;

      /* passagem 1 - so LEITURA */
      for (k = 0; k < alvos.length; k++) {
        caixas[k] = alvos[k].getBoundingClientRect();
      }

      /* passagem 2 - so ESCRITA */
      for (k = 0; k < alvos.length; k++) {
        var el = alvos[k];
        var c = caixas[k];
        /* fora da janela com folga: nada a atualizar, e nada a pagar */
        if (c.bottom < -vh || c.top > vh * 2) continue;
        /* `curso > vh * .5` e nao `curso > 0`: so e cena presa quem tem curso
           de verdade. Ver a conta no cabecalho deste bloco -- a 0 uma figura
           8px mais alta que a janela animava em 8px de rolagem, depois de ja
           ter saido de vista. */
        var curso = c.height - vh;
        var p = curso > vh * 0.5
          ? -c.top / curso
          : (vh - c.top) / (vh + c.height);
        p = p < 0 ? 0 : (p > 1 ? 1 : p);
        el.style.setProperty("--p", p.toFixed(4));

        /* `data-abriu-em` marca o ponto do curso em que o mecanismo terminou
           de abrir, e a classe que ele liga serve para uma coisa só:
           VISIBILIDADE, no sentido de teste de acerto.

           `opacity: 0` esconde da vista e não esconde de mais nada — o
           elemento continua capturando clique e continua na ordem de
           tabulação. Numa unidade isso significa que o rodapé, invisível
           durante toda a primeira metade do curso, ainda assim receberia o
           clique de quem mirasse a legenda do vídeo atrás dele; e a coluna
           de texto, já apagada, continuaria roubando o foco do teclado.

           Uma classe, dois efeitos opostos: quando a caixa abriu, a coluna
           sai do alcance e o rodapé entra. */
        var abriu = el.getAttribute("data-abriu-em");
        if (abriu) el.classList.toggle("is-aberta", p >= parseFloat(abriu));

        /* `data-passos` transforma o progresso contínuo num índice discreto,
           publicado em `--n`. É o que faz o painel de setores trocar de foto:
           o CSS não precisa saber contar, e o JS não precisa saber desenhar. */
        var passos = parseInt(el.getAttribute("data-passos"), 10);
        if (passos > 1) {
          var n = Math.min(passos - 1, Math.floor(p * passos));
          if (el.getAttribute("data-n") !== String(n)) {
            el.setAttribute("data-n", n);
            el.style.setProperty("--n", n);
            el.dispatchEvent(new CustomEvent("passo", { detail: { n: n } }));
          }
        }
      }
    };

    var pedir = function () {
      if (pendente) return;
      pendente = true;
      window.requestAnimationFrame(medir);
    };

    /* `passive: true` é a promessa de que este ouvinte NÃO cancela o gesto —
       o navegador pode rolar sem esperar o JavaScript responder. */
    window.addEventListener("scroll", pedir, { passive: true });
    window.addEventListener("resize", pedir);
    medir();
  })();

  /* ---------- 8. Dominó da lista de capacidades ----------
     Publica em cada item a DISTÂNCIA até o item apontado (`--d`), e o CSS
     converte isso em atraso e em intensidade. O item sob o ponteiro reage
     primeiro, os vizinhos logo atrás, e a onda morre nas pontas.

     POR QUE JS E NÃO `:has()`. Distância exige contar, e contar em CSS puro
     seriam 64 regras (8 itens x 8 origens) que ninguém consegue manter. Aqui
     são duas linhas de aritmética e o CSS continua declarativo.

     E POR QUE A ONDA NÃO PODE MEXER NO LAYOUT — esta é a parte cara, já paga
     uma vez. A primeira versão da lista encolhia as irmãs com `:has()`: as de
     cima encolhiam, a apontada subia, o ponteiro escapava, o hover desligava,
     ela voltava ao tamanho e o ponteiro entrava de novo. Piscava em laço e a
     lista ficava impossível de usar.

     Por isso o dominó daqui move só `transform` e `color`, que não entram no
     layout: a caixa de cada item fica exatamente onde estava e o alvo nunca
     foge do ponteiro. Quem cresce continua sendo só o item apontado, e só
     para BAIXO, que é o gesto já provado estável. */
  (function () {
    var listas = document.querySelectorAll("[data-domino]");
    if (!listas.length || reduzido) return;

    for (var i = 0; i < listas.length; i++) {
      (function (lista) {
        var itens = lista.children;

        var espalhar = function (origem) {
          for (var j = 0; j < itens.length; j++) {
            itens[j].style.setProperty(
              "--d", origem < 0 ? 99 : Math.abs(j - origem));
          }
        };

        /* `pointerover` e não `pointerenter` em cada item: um ouvinte só na
           lista, que continua certo se a lista crescer. */
        lista.addEventListener("pointerover", function (e) {
          var alvo = e.target.closest ? e.target.closest("[data-i]") : null;
          if (!alvo || alvo.parentNode !== lista) return;
          espalhar(+alvo.getAttribute("data-i"));
        });
        lista.addEventListener("pointerleave", function () { espalhar(-1); });
        /* teclado: quem tabula pela lista vê a mesma onda */
        lista.addEventListener("focusin", function (e) {
          var alvo = e.target.closest ? e.target.closest("[data-i]") : null;
          if (alvo && alvo.parentNode === lista) {
            espalhar(+alvo.getAttribute("data-i"));
          }
        });
        lista.addEventListener("focusout", function (e) {
          if (!lista.contains(e.relatedTarget)) espalhar(-1);
        });
        espalhar(-1);
      })(listas[i]);
    }
  })();

  /* ---------- 10. Rodapé revelado: gatilho e foco ----------
     Duas consequências de o rodapé ficar preso ao pé da janela, e as duas são
     invisíveis até alguém tropeçar nelas.

     O GATILHO. Ele está na janela desde a carga, então observá-LO não diz nada
     sobre ele estar VISÍVEL. Quem diz é o fim do <main>: quando a última linha
     do conteúdo sobe até o pé da tela, o que está aparecendo é o rodapé. Por
     isso o observador olha um marcador no fim do main, e não o rodapé.

     O FOCO. Pela mesma razão, focar um link do rodapé pelo teclado NÃO provoca
     rolagem -- para o navegador ele já está na tela. O anel de foco ficaria
     atrás do conteúdo, invisível, e quem navega por teclado se perderia. O
     primeiro foco que entra no rodapé leva a página até o fim.

     O módulo inteiro só existe quando a revelação está ligada: fora da guarda
     de tamanho o rodapé é estático e o §4 cuida da frase como sempre cuidou. */
  (function () {
    var rodape = document.querySelector(".rodape");
    if (!rodape || window.getComputedStyle(rodape).position !== "sticky") return;

    var frase = rodape.querySelector(".rodape__headline");
    var marca = document.querySelector("[data-fim-conteudo]");

    if (frase) {
      if (reduzido || !window.IntersectionObserver || !marca) {
        frase.classList.add("is-visivel");
      } else {
        var io = new IntersectionObserver(function (ent) {
          ent.forEach(function (e) {
            if (!e.isIntersecting) return;
            frase.classList.add("is-visivel");
            io.disconnect();
          });
        }, { rootMargin: "0px 0px -8% 0px" });
        io.observe(marca);
      }
    }

    rodape.addEventListener("focusin", function () {
      var main = document.querySelector("main");
      if (!main) return;
      var coberto = main.getBoundingClientRect().bottom
                  > rodape.getBoundingClientRect().top + 4;
      if (coberto) {
        window.scrollTo({
          top: document.documentElement.scrollHeight,
          behavior: reduzido ? "auto" : "smooth"
        });
      }
    });
  })();

  /* ---------- 11. Inércia da roda ----------
     A roda deixa de mover a página e passa a mover um ALVO; a página persegue
     esse alvo por quadro. O gesto ganha o desaceleramento que a rolagem nativa
     do Windows não tem.

     ESTA É UMA REVERSÃO DELIBERADA, e ela está registrada. Este arquivo dizia
     "nada sequestra a roda" desde 19/08, por três motivos: biblioteca no
     runtime, trackpad e acessibilidade. Os três foram endereçados abaixo, e a
     escolha foi confirmada com o usuário em 20/08 (CLAUDE.md regra nº1).

     A PÁGINA ROLA DE VERDADE. `window.scrollTo` por quadro, não `transform`
     num wrapper. É o que mantém `position: sticky` vivo — e o rodapé revelado
     é sticky, então a via do wrapper teria matado a entrega anterior. Mantém
     junto a barra nativa, o "localizar na página" e o leitor de tela.

     QUATRO COISAS QUE PARECEM DETALHE E NÃO SÃO:

     1. `scroll-behavior` TEM DE SER DESLIGADO durante o laço. O `html` o
        declara `smooth` para as âncoras, e sem desligar, cada `scrollTo` deste
        laço seria ele mesmo animado pelo navegador — duas interpolações
        brigando, e o resultado é mingau, não maciez. Feito por atributo de
        estilo em vez de `behavior: "instant"` na chamada, porque o atributo
        funciona em todo navegador que tem `scroll-behavior`, e o valor
        "instant" é recente.

     2. Trackpad não entra. O sistema já aplica momentum próprio nele, e somar
        o nosso é o "duplo momentum" que faz a página parecer atrasada. Roda de
        mouse manda poucos eventos e GRANDES (~100px por dente); trackpad manda
        muitos e pequenos. Abaixo do piso o evento passa direto, sem
        `preventDefault`, e o SO cuida.

     3. A suavização é por TEMPO, não por quadro. `k` fixo em 60 Hz roda o
        dobro de rápido num monitor de 120 Hz. A conta com `dt` deixa o gesto
        idêntico nos dois. Em .11 por quadro de 60 Hz, 90% da distância é
        coberta em ~20 quadros = ~330 ms.

     4. Elemento rolável por baixo do ponteiro tem precedência. O painel do
        menu (`overflow-y: auto`) e a matriz de services (`overflow-x: auto`)
        precisam receber a roda quando ainda têm curso — senão o menu aberto
        no celular fica preso.

     E o alvo se RESSINCRONIZA a cada rolagem que não veio da roda: teclado,
     barra, âncora, `scrollIntoView`. Sem isso o primeiro giro depois de um
     salto de âncora puxaria a página de volta para onde ela estava. */
  (function () {
    /* Rolagem animada é das poucas coisas que provocam enjoo de verdade
       (design.md §7 regra 3). Aqui não há meia-medida: desliga. */
    if (reduzido) return;

    var LERP = 0.11;          /* ~330 ms para 90% da distância a 60 Hz */
    var PISO_RODA = 50;       /* abaixo disso é trackpad: não é nosso */
    var QUADRO = 1000 / 60;

    var alvo = window.scrollY;
    var rodando = false;
    /* A posição que ESTE laço mandou o navegador assumir no quadro anterior.
       Se a leitura do quadro seguinte não bate com ela, alguém mais mexeu na
       rolagem — teclado, barra, âncora — e o alvo tem de se reancorar ali. É
       mais confiável que um sinalizador booleano, porque o evento `scroll`
       pode ser coalescido pelo navegador e o sinalizador ficaria presos. */
    var previsto = -1;

    var teto = function () {
      return Math.max(0, document.documentElement.scrollHeight - window.innerHeight);
    };

    /* deltaMode: 0 pixels, 1 linhas, 2 páginas */
    var pixels = function (e) {
      if (e.deltaMode === 1) return e.deltaY * 16;
      if (e.deltaMode === 2) return e.deltaY * window.innerHeight;
      return e.deltaY;
    };

    /* Alguém sob o ponteiro ainda tem curso para rolar? Então a roda é dele. */
    var temDono = function (no, dir) {
      while (no && no !== document.body && no !== document.documentElement) {
        if (no.scrollHeight > no.clientHeight + 1) {
          var ov = window.getComputedStyle(no).overflowY;
          if (ov === "auto" || ov === "scroll") {
            var max = no.scrollHeight - no.clientHeight;
            if ((dir < 0 && no.scrollTop > 0) ||
                (dir > 0 && no.scrollTop < max - 1)) return true;
          }
        }
        no = no.parentElement;
      }
      return false;
    };

    /* O `html` tem `scroll-behavior: smooth` para as âncoras. Sem desligá-lo,
       CADA `scrollTo` deste laço seria ele mesmo animado pelo navegador: duas
       interpolações brigando, e o resultado é mingau em vez de maciez.
       Desligar por atributo de estilo (e não passar `behavior: "instant"` na
       chamada) funciona em todo navegador que tem `scroll-behavior`, inclusive
       nos que ainda não conhecem o valor "instant". */
    var raiz = document.documentElement;
    var parar = function () {
      rodando = false;
      ultimo = 0;
      previsto = -1;
      raiz.style.scrollBehavior = "";
    };

    var ultimo = 0;
    var passo = function (agora) {
      var dt = ultimo ? Math.min(agora - ultimo, 64) : QUADRO;
      ultimo = agora;

      /* suavização exponencial INDEPENDENTE do refresh: em 120 Hz o dt é
         metade, então k é menor, e o gesto dura o mesmo tempo */
      var k = 1 - Math.pow(1 - LERP, dt / QUADRO);
      var atual = window.scrollY;

      /* alguém mais moveu a página no meio do gesto: reancora e segue */
      if (previsto >= 0 && Math.abs(atual - previsto) > 4) alvo = atual;

      if (Math.abs(alvo - atual) < 0.5) { parar(); return; }

      var y = atual + (alvo - atual) * k;
      previsto = Math.round(y);
      window.scrollTo(0, y);
      window.requestAnimationFrame(passo);
    };

    window.addEventListener("wheel", function (e) {
      if (e.ctrlKey) return;                    /* pinça de zoom */
      var d = pixels(e);
      if (!d || Math.abs(d) < PISO_RODA) return;   /* trackpad: do SO */
      if (temDono(e.target, d)) return;            /* painel, tabela */

      e.preventDefault();
      if (!rodando) alvo = window.scrollY;
      alvo = Math.max(0, Math.min(teto(), alvo + d));
      if (!rodando) {
        rodando = true;
        ultimo = 0;
        previsto = -1;
        raiz.style.scrollBehavior = "auto";
        window.requestAnimationFrame(passo);
      }
    }, { passive: false });

    /* Teclado, barra, âncora e o pular-conteúdo continuam NATIVOS. Só é
       preciso avisar o alvo de que a página se moveu sem nós. */
    window.addEventListener("scroll", function () {
      if (!rodando) alvo = window.scrollY;
    }, { passive: true });

    window.addEventListener("resize", function () {
      alvo = Math.max(0, Math.min(teto(), window.scrollY));
    });
  })();

  /* ---------- 9. Ano corrente ---------- */
  (function () {
    var els = document.querySelectorAll("[data-ano]");
    var ano = String(new Date().getFullYear());
    for (var i = 0; i < els.length; i++) els[i].textContent = ano;
  })();

  /* ---------- 12. Aviso de armazenamento ----------
     A faixa nasce `hidden` no HTML e é este módulo que decide mostrá-la. A
     ordem importa e é a razão de ela não nascer visível: sem JavaScript
     ninguém consegue dispensá-la, e faixa que não se dispensa é pior que
     faixa nenhuma.

     A ironia é declarada: a única coisa que este site guarda no navegador é
     a preferência de tema, e agora também a marca de que o aviso foi lido —
     ou seja, o aviso guarda um registro de si mesmo. É `localStorage`, não
     cookie: ele não viaja em requisição nenhuma, que é justamente o que a
     faixa afirma.

     TODO acesso vai dentro de try/catch. Em janela anônima com dados de site
     bloqueados o próprio acessor LEVANTA, e uma exceção aqui derrubaria o
     resto do módulo. Falhando, a faixa aparece — que é o lado seguro: mostrar
     de novo é chato, esconder sem consentimento é o defeito. */
  (function () {
    var faixa = document.getElementById("aviso-armazenamento");
    if (!faixa) return;

    var CHAVE = "i3-aviso";
    var lido = false;
    try { lido = window.localStorage.getItem(CHAVE) === "1"; } catch (e) {}
    if (lido) return;

    var botao = faixa.querySelector("[data-aviso-ok]");

    /* A rede de segurança de 7 s e o observador podem chamar `mostrar` os
       DOIS. Sem esta trava, quem dispensasse a faixa nos primeiros segundos a
       veria voltar sozinha aos 7 s — e o defeito só apareceria na home, que é
       a única página com intro. */
    var mostrado = false;
    var mostrar = function () {
      if (mostrado) return;
      mostrado = true;
      faixa.hidden = false;
      /* Dois quadros antes de acender a classe: no mesmo quadro em que
         `hidden` sai, o elemento ainda não tem estilo calculado e a
         transição não dispara — a faixa apareceria de estalo. */
      window.requestAnimationFrame(function () {
        window.requestAnimationFrame(function () { faixa.classList.add("is-visivel"); });
      });
    };

    var fechar = function () {
      try { window.localStorage.setItem(CHAVE, "1"); } catch (e) {}
      faixa.classList.remove("is-visivel");
      if (reduzido) { faixa.hidden = true; return; }
      /* Espera a transição de saída. O tempo é o mesmo do CSS (.5s), com
         folga — e o `hidden` no fim tira a faixa da árvore de acessibilidade,
         que `opacity: 0` sozinho não faz. */
      window.setTimeout(function () { faixa.hidden = true; }, 560);
    };

    if (botao) botao.addEventListener("click", fechar);

    /* Na home a faixa espera a intro terminar: ela ocupa a base da tela
       exatamente enquanto a marca voa até o herói, e as duas competiriam. A
       intro remove `intro-ativa` do <html> ao encerrar (módulo 5), então é
       essa remoção que se observa — não um tempo fixo, que dessincronizaria
       no dia em que a duração da intro mudar. */
    var raiz = document.documentElement;
    if (!raiz.classList.contains("intro-ativa") || !window.MutationObserver) {
      mostrar();
      return;
    }
    var obs = new MutationObserver(function () {
      if (!raiz.classList.contains("intro-ativa")) { obs.disconnect(); mostrar(); }
    });
    obs.observe(raiz, { attributes: true, attributeFilter: ["class"] });
    /* Rede de segurança: se a intro falhar em encerrar, a faixa aparece
       mesmo assim. A intro inteira dura 5,6 s. */
    window.setTimeout(function () { obs.disconnect(); mostrar(); }, 7000);
  })();

  /* ---------- 13. Vídeo: um decodificando por vez ----------
     REGRA DURA DE MÍDIA (design.md §5.4): `preload="none"` mais
     IntersectionObserver dando play e pause, e pôster obrigatório em todos.

     POR QUE ISSO IMPORTA MAIS AQUI DO QUE NO SITE MÉDIO. A home carrega, ao
     mesmo tempo: a inércia da roda sequestrando o `wheel`, dois momentos
     lendo progresso de rolagem, um parallax e um rodapé sticky. Três vídeos
     decodificando junto disso é o quadro que estoura — e decodificação de
     vídeo não roda na main thread, mas disputa memória e barramento com o
     compositor, que roda.

     O HERÓI FICA DE FORA deste módulo. Ele é a única mídia autorizada a
     carregar adiantado, porque ele É a primeira dobra; quem o controla é o
     botão de pausa do módulo 14.

     `play()` DEVOLVE UMA PROMESSA QUE REJEITA, e ignorá-la é como se ganha um
     "Uncaught (in promise)" no console de produção. Rejeita legitimamente: a
     aba perdeu o foco entre o observador disparar e o quadro seguinte, ou a
     política de autoplay do navegador recusou. Nenhum dos dois é erro nosso,
     e nenhum dos dois deve virar ruído. */
  (function () {
    var videos = document.querySelectorAll("[data-momento-video]");
    if (!videos.length) return;

    /* Com movimento reduzido os três momentos desligam INTEIROS: a janela
       nasce aberta, o texto entra sem transformação e o vídeo NÃO TOCA. O que
       o visitante vê é o pôster, que por isso é obrigatório e não opcional. */
    if (reduzido || !window.IntersectionObserver) return;

    var tocando = null;

    var parar = function (v) {
      if (!v) return;
      try { v.pause(); } catch (e) { /* já removido do DOM */ }
    };

    var obs = new IntersectionObserver(function (entradas) {
      for (var i = 0; i < entradas.length; i++) {
        var e = entradas[i];
        var v = e.target;
        if (e.isIntersecting) {
          /* QUEM PEDIU PAUSA CONTINUA PAUSADO. `data-parado` é escrito pelo
             botão do módulo 14, e sem esta guarda o observador desfaria a
             decisão do visitante na primeira vez que ele rolasse para fora e
             voltasse — o que esvazia o mecanismo que o WCAG 2.2.2 exige. */
          if (v.hasAttribute("data-parado")) continue;
          /* UM DE CADA VEZ, e a ordem importa: pausa o anterior ANTES de
             pedir o próximo, senão existe uma janela de um quadro com dois
             decodificadores vivos — que é justamente o instante em que a
             rolagem está mais rápida. */
          if (tocando && tocando !== v) parar(tocando);
          tocando = v;
          var p = v.play();
          if (p && p.catch) p.catch(function () { /* autoplay recusado, tudo bem */ });
        } else if (v === tocando) {
          parar(v);
          tocando = null;
        } else {
          parar(v);
        }
      }
    }, {
      /* 25% do elemento na tela para começar. Com `0` o vídeo daria play com
         uma tira de dois pixels visível, no meio de uma rolagem rápida que
         nem vai parar ali. */
      threshold: 0.25
    });

    for (var i = 0; i < videos.length; i++) obs.observe(videos[i]);

    /* Aba em segundo plano: o navegador já congela `rAF`, mas não pausa vídeo.
       Sem isto o visitante que troca de aba deixa um decodificador rodando. */
    document.addEventListener("visibilitychange", function () {
      if (document.hidden) parar(tocando);
      else if (tocando && !tocando.hasAttribute("data-parado")) {
        var p = tocando.play();
        if (p && p.catch) p.catch(function () {});
      }
    });
  })();

  /* ---------- 14. Pausa do herói — WCAG 2.2.2 ----------
     O critério é objetivo e não interpretativo: conteúdo em movimento que
     começa AUTOMATICAMENTE, dura mais de CINCO segundos e é apresentado em
     PARALELO com outro conteúdo precisa de um mecanismo para pausar, parar
     ou esconder. O herói é um loop de 12 s rodando debaixo da headline —
     encaixa nas três condições.

     ISTO NÃO ESTAVA NO PLANO. `plano.md` §3.4 especifica o herói como "mudo,
     em loop", e §5.4 cobre `prefers-reduced-motion`, que é outro critério
     (2.3.3) e não substitui este: 2.2.2 vale para quem NÃO pediu movimento
     reduzido e mesmo assim quer parar a imagem.

     E NÃO VIOLA A REGRA 10 DE CLEAN ("se um elemento precisa de legenda
     explicando como usá-lo, ele sai"). O exemplo que a regra usa é a linha
     "Drag the arm to orbit" do herói publicado — uma FRASE ensinando um gesto
     inventado. Um botão de pausa é o oposto: símbolo universal, sem legenda,
     e o `aria-label` existe para leitor de tela, não para a tela.

     O botão é escrito no HTML e não injetado por JS: injetar deixaria quem
     está sem JavaScript com um vídeo que não para, que é exatamente o caso
     que o critério cobre. Aqui o JS só liga o comportamento. */
  /* PLURAL DESDE 2026-08-26, e não por generalidade preventiva: who-we-are
     ganhou um FUNDO EM VÍDEO na dobra do argumento, e ele encaixa nas mesmas
     três condições do 2.2.2 que o herói. `querySelector` no singular teria
     funcionado por acidente — as duas páginas têm um vídeo de fundo cada —, e
     teria quebrado em silêncio no dia em que uma tivesse dois.

     O PAR É DECLARADO POR `data-pausa`, e não por proximidade no DOM: o botão
     aponta para o `id` do vídeo que ele controla. Amarrar por "o vídeo mais
     próximo" é o tipo de acoplamento que sobrevive à primeira remontagem do
     HTML e morre na segunda. */
  (function () {
    var botoes = document.querySelectorAll("[data-pausa]");
    if (!botoes.length) return;

    for (var i = 0; i < botoes.length; i++) (function (botao) {
      var video = document.getElementById(botao.getAttribute("data-pausa"));
      if (!video) return;

      /* Com movimento reduzido o vídeo nem toca e o botão está escondido em
         CSS — não há o que pausar, e um controle invisível na ordem de
         tabulação é um ponto de parada morto. */
      if (reduzido) { botao.setAttribute("hidden", ""); return; }

      var rotular = function (pausado) {
        botao.setAttribute("aria-pressed", pausado ? "true" : "false");
        botao.setAttribute("aria-label",
          pausado ? "Play background video" : "Pause background video");
      };

      botao.addEventListener("click", function () {
        if (video.paused) {
          /* `data-parado` é a MEMÓRIA DA DECISÃO, e ela existe por causa do
             módulo 13. Um fundo de seção é `[data-momento-video]`: sai da
             tela, o observador pausa; volta, o observador dá play. Sem esta
             marca, quem apertou pausa e rolou até o rodapé encontraria o
             vídeo tocando de novo na volta — ou seja, o mecanismo que o 2.2.2
             exige duraria até a próxima rolagem. */
          video.removeAttribute("data-parado");
          var p = video.play();
          if (p && p.catch) p.catch(function () {});
          rotular(false);
        } else {
          video.setAttribute("data-parado", "");
          video.pause();
          rotular(true);
        }
      });

      /* O estado pode mudar sem passar pelo botão: economia de bateria do
         sistema, política de autoplay, aba em segundo plano. O rótulo segue o
         VÍDEO, e não o último clique — senão ele mente. */
      video.addEventListener("pause", function () { rotular(true); });
      video.addEventListener("play", function () { rotular(false); });
      rotular(video.paused);
    })(botoes[i]);
  })();

})();
