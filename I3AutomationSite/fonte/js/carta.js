/* ============================================================================
   carta.js — a chapa de navegação das duas operações
   i3Automations

   A PÁGINA DE CONTATO ERA A ÚNICA SEM PEÇA PRÓPRIA. Esta é a informação de
   contato DESENHADA: Lakewood Ranch, FL e Houston, TX -- as duas operações que
   o texto já cita -- plotadas sobre uma retícula de latitude e longitude, com
   a geodésica entre elas e a distância medida.

   O LITORAL É DADO, NÃO MEMÓRIA. A primeira versão não tinha contorno nenhum:
   eu me recusei a desenhar uma costa de cabeça, porque seria inventar
   geografia -- o tipo de afirmação que este site já removeu da galeria. Mas o
   usuário não entendeu a peça, e ele tem razão: retícula com duas cruzes não
   lê como mapa.

   A saída honesta não era desenhar de memória, era ir BUSCAR O DADO. O
   contorno vem de `referencia/us-states.geojson` (fronteiras estaduais dos
   EUA, domínio público, derivadas do TIGER do US Census), recortado à janela e
   simplificado por Douglas-Peucker em `ferramentas/extrair_costa.py`: 10
   anéis, 246 pontos, duas casas decimais (~1 km, muito abaixo do que esta
   escala mostra).

   REGRA QUE FICA: quando a alternativa honesta a inventar é não desenhar, a
   terceira saída costuma ser ir buscar o dado.

   A PROJEÇÃO É MERCATOR, e ela importa aqui: numa faixa de latitude de 26 a
   31 graus a diferença para uma projeção plana é pequena, mas a geodésica
   entre Houston e Lakewood Ranch fica visivelmente ARQUEADA -- e é esse arco
   que diz que são 1.289 km e não um traço de régua. (O valor é calculado por
   haversine no próprio arquivo; conferido contra a lei esférica dos cossenos
   e Vincenty esférico, as três dão 1.289,2 km.)

   Sem WebGL: canvas 2D sobre `tela.js`.
   ============================================================================ */
(function () {
  "use strict";
  if (!window.I3Tela) return;

  var T = window.I3Tela;
  var RAD = Math.PI / 180;

  /* Coordenadas públicas das duas operações que o site declara. */
  var SITIOS = [
    { nome: "LAKEWOOD RANCH, FL", curto: "HQ", lat: 27.418, lon: -82.430 },
    { nome: "HOUSTON, TX", curto: "OIL & GAS", lat: 29.760, lon: -95.370 }
  ];

/* Contorno do Golfo/Sudeste, extraido de referencia/us-states.geojson
   por ferramentas/extrair_costa.py (Douglas-Peucker, eps 0.10).
   10 aneis, 246 pontos. Fonte de dominio publico (US Census TIGER).
   Duas casas decimais = ~1 km, muito abaixo do que esta escala mostra. */
  var COSTA = [
    [-87.36,35.00,-85.61,34.98,-85.18,32.86,-84.89,32.26,-85.14,31.84,-85.00,31.00,-87.60,31.00,-87.37,30.43,-87.66,30.25,-88.01,30.69,-88.14,30.32,-88.39,30.37,-88.47,31.90,-88.10,34.89,-88.20,35.00,-87.36,35.00],
    [-94.47,36.50,-90.15,36.50,-90.06,36.30,-90.38,36.00,-89.73,36.00,-89.76,35.81,-90.13,35.44,-90.11,35.20,-90.59,34.62,-90.57,34.42,-90.95,34.14,-90.89,34.03,-91.23,33.56,-91.06,33.43,-91.17,33.00,-94.04,33.02,-94.04,33.55,-94.48,33.64,-94.43,35.40,-94.62,36.50,-94.47,36.50],
    [-85.50,31.00,-85.00,31.00,-84.87,30.71,-82.22,30.57,-82.17,30.36,-82.05,30.36,-81.95,30.83,-81.44,30.71,-81.26,29.79,-80.52,28.46,-80.57,28.09,-80.03,26.80,-80.15,25.74,-80.50,25.20,-81.08,25.12,-81.35,25.82,-81.68,25.84,-82.04,26.52,-82.06,26.88,-82.25,26.76,-82.69,27.44,-82.39,27.84,-82.72,27.69,-82.85,27.89,-82.64,28.89,-83.64,29.89,-84.02,30.10,-85.31,29.70,-85.40,29.94,-86.30,30.36,-87.52,30.28,-87.37,30.43,-87.60,31.00,-85.50,31.00],
    [-83.11,35.00,-83.34,34.68,-82.90,34.49,-82.56,33.94,-81.49,33.01,-81.12,32.12,-80.89,32.03,-81.40,31.13,-81.44,30.71,-81.95,30.83,-82.05,30.36,-82.22,30.57,-84.87,30.71,-85.11,31.28,-85.14,31.84,-84.89,32.26,-85.18,32.86,-85.61,34.98,-83.11,35.00],
    [-93.61,33.02,-91.17,33.00,-90.99,32.22,-91.50,31.64,-91.64,31.00,-89.75,31.00,-89.85,30.67,-89.52,30.18,-89.84,29.95,-89.60,29.88,-89.50,30.04,-89.29,29.88,-89.42,29.70,-89.65,29.75,-89.70,29.51,-89.00,29.18,-89.34,29.04,-89.85,29.31,-89.85,29.48,-90.03,29.43,-90.10,29.15,-90.56,29.28,-90.80,29.09,-91.53,29.53,-91.62,29.74,-91.88,29.71,-91.89,29.84,-92.31,29.54,-93.23,29.78,-93.84,29.69,-93.73,30.58,-93.53,30.94,-93.82,31.78,-94.04,31.99,-94.04,33.02,-93.61,33.02],
    [-88.47,35.00,-88.10,34.89,-88.47,31.90,-88.39,30.37,-88.84,30.41,-89.52,30.18,-89.85,30.67,-89.75,31.00,-91.64,31.00,-91.50,31.64,-90.99,32.22,-91.15,32.64,-91.06,33.43,-91.23,33.56,-90.31,35.00,-88.47,35.00],
    [-100.09,37.00,-94.62,37.00,-94.43,35.40,-94.48,33.64,-95.22,33.96,-96.15,33.84,-96.35,33.69,-96.92,33.96,-97.17,33.74,-97.69,33.98,-97.87,33.85,-98.17,34.11,-99.19,34.21,-99.26,34.40,-99.70,34.38,-100.00,34.56,-100.00,36.50,-103.00,36.50,-103.00,37.00,-100.09,37.00],
    [-82.76,35.07,-82.28,35.20,-81.04,35.15,-80.80,34.82,-79.68,34.80,-78.54,33.85,-78.94,33.64,-79.36,33.01,-79.58,33.01,-80.89,32.03,-81.12,32.12,-81.49,33.01,-82.56,33.94,-82.90,34.49,-83.34,34.68,-83.11,35.00,-82.76,35.07],
    [-88.05,36.50,-88.07,36.68,-81.68,36.59,-81.72,36.35,-82.04,36.12,-82.61,35.97,-82.64,36.06,-82.99,35.77,-83.77,35.56,-84.29,35.23,-84.32,34.99,-90.31,35.00,-89.53,36.25,-89.54,36.50,-88.05,36.50],
    [-101.81,36.50,-100.00,36.50,-100.00,34.56,-99.70,34.38,-99.26,34.40,-99.19,34.21,-98.17,34.11,-97.87,33.85,-97.69,33.98,-97.17,33.74,-96.92,33.96,-96.35,33.69,-96.15,33.84,-95.22,33.96,-94.38,33.54,-94.04,33.55,-94.04,31.99,-93.82,31.78,-93.53,30.94,-93.73,30.58,-93.84,29.69,-94.52,29.55,-94.74,29.79,-95.02,29.56,-94.90,29.31,-95.38,28.87,-95.99,28.60,-96.66,28.70,-96.40,28.44,-96.77,28.41,-97.54,27.23,-97.43,27.26,-97.56,26.84,-97.22,25.99,-97.52,25.89,-98.20,26.06,-99.17,26.54,-99.45,27.02,-99.48,27.48,-100.30,28.28,-100.67,29.10,-101.41,29.75,-102.34,29.87,-102.63,29.73,-103.12,28.99,-103.28,28.98,-104.51,29.64,-104.90,30.57,-106.64,31.90,-103.07,32.00,-103.04,36.50,-101.81,36.50],
  ];

  /* Janela da carta, em graus. Sobra deliberada em volta dos dois pontos para
     a retícula ter meridianos suficientes para ler como carta. */
  var O = -101, L = -76, S = 23.5, N = 33.5;

  function merc(lat) { return Math.log(Math.tan(Math.PI / 4 + lat * RAD / 2)); }

  /* Distância de círculo máximo, em quilômetros -- haversine. */
  function haversine(a, b) {
    var dLat = (b.lat - a.lat) * RAD, dLon = (b.lon - a.lon) * RAD;
    var h = Math.sin(dLat / 2) * Math.sin(dLat / 2) +
            Math.cos(a.lat * RAD) * Math.cos(b.lat * RAD) *
            Math.sin(dLon / 2) * Math.sin(dLon / 2);
    return 6371 * 2 * Math.asin(Math.sqrt(h));
  }

  /* Ponto intermediário da geodésica, para o arco não ser uma reta. */
  function meio(a, b, f) {
    var d = haversine(a, b) / 6371;
    var A = Math.sin((1 - f) * d) / Math.sin(d), B = Math.sin(f * d) / Math.sin(d);
    var x = A * Math.cos(a.lat * RAD) * Math.cos(a.lon * RAD) +
            B * Math.cos(b.lat * RAD) * Math.cos(b.lon * RAD);
    var y = A * Math.cos(a.lat * RAD) * Math.sin(a.lon * RAD) +
            B * Math.cos(b.lat * RAD) * Math.sin(b.lon * RAD);
    var z = A * Math.sin(a.lat * RAD) + B * Math.sin(b.lat * RAD);
    return { lat: Math.atan2(z, Math.sqrt(x * x + y * y)) / RAD,
             lon: Math.atan2(y, x) / RAD };
  }

  function montar(raiz) {
    var cor = {};
    function lerTema() {
      cor.traco = T.token(raiz, "--carta-traco", "#9FBEE0");
      cor.vivo = T.token(raiz, "--carta-vivo", "#FDC500");
      cor.tinta = T.token(raiz, "--carta-tinta", "#FFFFFF");
      cor.grade = T.alfa(cor.traco, 0.16);
      cor.fraco = T.alfa(cor.traco, 0.58);
    }
    lerTema();

    var km = haversine(SITIOS[0], SITIOS[1]);

    function desenhar(ctx, larg, alt, t) {
      var pad = 26;
      var yS = merc(S), yN = merc(N);
      function px(lon) { return pad + (larg - pad * 2) * (lon - O) / (L - O); }
      function py(lat) { return alt - pad - (alt - pad * 2) * (merc(lat) - yS) / (yN - yS); }

      T.tipo(ctx, raiz);
      ctx.textBaseline = "middle";

      /* --- o contorno, primeiro: é o fundo sobre o qual tudo se lê ------
         Em filete fraco e não cheio: a carta é desenho técnico, e o assunto
         são os dois sítios, não a geografia. Ela existe para o visitante
         RECONHECER onde está, e recua assim que cumpre isso.

         RECORTADO NA MOLDURA. Os anéis vêm inteiros do dado -- o Texas chega a
         106°W e vários sobem até 37°N, bem além da janela de 101..76 e
         23,5..33,5. Sem o recorte o traço vaza para fora da chapa e a peça
         deixa de ser uma carta emoldurada para virar um desenho solto. */
      ctx.save();
      ctx.beginPath();
      ctx.rect(pad, pad, larg - pad * 2, alt - pad * 2);
      ctx.clip();
      ctx.strokeStyle = cor.grade;
      ctx.lineWidth = 1;
      ctx.beginPath();
      for (var a = 0; a < COSTA.length; a++) {
        var an = COSTA[a];
        for (var q = 0; q < an.length; q += 2) {
          var cx = px(an[q]), cy = py(an[q + 1]);
          if (q === 0) ctx.moveTo(cx, cy); else ctx.lineTo(cx, cy);
        }
        ctx.closePath();
      }
      ctx.stroke();
      ctx.restore();

      /* --- retícula: meridianos de 5 em 5, paralelos de 2 em 2 ---------- */
      ctx.strokeStyle = cor.grade;
      ctx.lineWidth = 1;
      ctx.beginPath();
      var lon, lat;
      for (lon = -100; lon <= L; lon += 5) {
        ctx.moveTo(Math.round(px(lon)) + 0.5, pad);
        ctx.lineTo(Math.round(px(lon)) + 0.5, alt - pad);
      }
      for (lat = 24; lat <= N; lat += 2) {
        ctx.moveTo(pad, Math.round(py(lat)) + 0.5);
        ctx.lineTo(larg - pad, Math.round(py(lat)) + 0.5);
      }
      ctx.stroke();

      /* moldura da chapa */
      ctx.strokeStyle = cor.fraco;
      ctx.strokeRect(Math.round(pad) + 0.5, Math.round(pad) + 0.5,
                     Math.round(larg - pad * 2), Math.round(alt - pad * 2));

      /* rótulos da retícula, fora da moldura, como numa carta de verdade */
      ctx.fillStyle = cor.fraco;
      ctx.textAlign = "center";
      for (lon = -100; lon <= L; lon += 10) {
        ctx.fillText(Math.abs(lon) + "°W", px(lon), alt - pad + 12);
      }
      ctx.textAlign = "right";
      for (lat = 24; lat <= N; lat += 4) {
        ctx.fillText(lat + "°N", pad - 6, py(lat));
      }

      /* --- a geodésica ---------------------------------------------------
         Desenhada em 48 passos porque a curva de círculo máximo NÃO é uma
         reta em Mercator: o arco é a diferença entre "duas cidades" e "1.500
         km de distância", e é ele que dá a escala da operação. */
      var pts = [];
      for (var i = 0; i <= 48; i++) {
        var p = meio(SITIOS[0], SITIOS[1], i / 48);
        pts.push([px(p.lon), py(p.lat)]);
      }
      ctx.strokeStyle = cor.fraco;
      ctx.lineWidth = 1;
      ctx.beginPath();
      for (i = 0; i < pts.length; i++) {
        if (i === 0) ctx.moveTo(pts[i][0], pts[i][1]);
        else ctx.lineTo(pts[i][0], pts[i][1]);
      }
      ctx.stroke();

      /* o pulso percorrendo a rota: o mesmo gesto do barramento de
         who-we-are, na única peça do site que tem distância de verdade */
      var f = (t * 0.18) % 1;
      var seg = Math.min(pts.length - 2, Math.floor(f * (pts.length - 1)));
      var fr = f * (pts.length - 1) - seg;
      var hx = pts[seg][0] + (pts[seg + 1][0] - pts[seg][0]) * fr;
      var hy = pts[seg][1] + (pts[seg + 1][1] - pts[seg][1]) * fr;
      ctx.fillStyle = cor.vivo;
      ctx.fillRect(Math.round(hx) - 1, Math.round(hy) - 1, 3, 3);

      /* --- os dois sítios ------------------------------------------------ */
      ctx.textAlign = "left";
      for (i = 0; i < SITIOS.length; i++) {
        var s = SITIOS[i];
        var x = px(s.lon), y = py(s.lat);
        /* cruz de marcação, não pino: convenção de carta, e canto reto */
        ctx.strokeStyle = cor.vivo;
        ctx.lineWidth = 1;
        ctx.beginPath();
        ctx.moveTo(Math.round(x) + 0.5, y - 7); ctx.lineTo(Math.round(x) + 0.5, y + 7);
        ctx.moveTo(x - 7, Math.round(y) + 0.5); ctx.lineTo(x + 7, Math.round(y) + 0.5);
        ctx.stroke();
        ctx.strokeRect(Math.round(x) - 3.5, Math.round(y) - 3.5, 7, 7);

        var dir = s.lon > -88 ? -1 : 1;      /* rótulo para o lado com espaço */
        ctx.fillStyle = cor.tinta;
        ctx.textAlign = dir > 0 ? "left" : "right";
        ctx.fillText(s.nome, x + dir * 13, y - 6);
        ctx.fillStyle = cor.fraco;
        ctx.fillText(s.curto, x + dir * 13, y + 7);
      }

      /* --- bloco de dados, canto inferior direito ----------------------- */
      ctx.textAlign = "right";
      ctx.fillStyle = cor.fraco;
      ctx.fillText(Math.round(km) + " km · " + Math.round(km / 1.609) + " mi",
                   larg - pad - 6, alt - pad - 18);
      ctx.fillText("MERCATOR · WGS 84", larg - pad - 6, alt - pad - 6);
      ctx.textAlign = "left";
    }

    var peca = T.montar(raiz, { desenhar: desenhar });
    if (peca) raiz.classList.add("is-viva");
  }

  function iniciar() {
    var els = document.querySelectorAll("[data-carta]");
    for (var i = 0; i < els.length; i++) montar(els[i]);
  }
  if (document.readyState === "loading") {
    document.addEventListener("DOMContentLoaded", iniciar);
  } else {
    iniciar();
  }
})();
