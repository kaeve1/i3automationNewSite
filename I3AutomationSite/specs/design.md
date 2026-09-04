> # ⚠ SUPERADO EM 2026-08-25
>
> **Este documento não vale mais como fonte de decisão.** Ele foi substituído por
> **`design.md`** na raiz do projeto, que lista no §10 exatamente o que morreu daqui
> e por quê. Fica preservado como registro histórico.
>
> O que morreu: a paleta (o dourado saiu do site), o §1.4 "sem gradiente creme"
> (causa raiz do feedback do cliente), o alternador de tema, o herói com peça 3D,
> e a regra de cantos retos sem exceção (o logo agora é isento).
>
> O que sobreviveu inteiro: tipografia, espaçamento, grid de 12, tom de voz,
> o CTA de chip com seta, e a disciplina de medir em vez de estimar.
>
> Ver também: `plano.md` (o que vai em cada página), `doit.md` (ordem de execução),
> `memorianew.md` (medições e decisões).

# Design — i3Automations & Controls

Variação do sistema de design construído para o **Universo do CLP** (github.com/kaeve1/UnidoCLP, no ar em https://universodoclp.pages.dev/), que por sua vez tem direção de estrutura e clima extraída de [zetta-joule.com](https://zetta-joule.com/).

**O que é herdado sem discussão:** a **tipografia inteira** (família, escala, pesos, entrelinhas, tracking), a gramática de layout (grid de 12, split 4/8, ritmo claro/escuro), o padrão de seção (eyebrow → título → parágrafo → CTA), os componentes (chip de seta, botão de borda fina) e a gramática de movimento (uma só: entra com desfoque e sobe).

**O que muda:** a **paleta**, que deixa de ser o azul da referência e passa a ser a marca real do cliente (navy + dourado, medidos no logo deles); o **idioma** (EN-US); o **conteúdo** (indústria americana de Oil & Gas, água/esgoto, automotivo, solar); e o **peso institucional** — o UnidoCLP vende treinamento a pessoas, o i3Automations vende integração e contrato a empresas e ao governo dos EUA.

O conteúdo e a identidade vêm do site atual do cliente (https://i3automations.com/, recorte salvo em `referencia/i3automations/`), que é a verdade absoluta sobre o que a empresa oferece.

---

## 1. Paleta

### 1.1 Cores de marca (medidas em pixel no logo real)

Extraídas de `referencia/i3automations/logo-i3.png` (1024×387, baixado do site do cliente) por contagem de cores. **São valores medidos, não estimados.**

| Papel | Cor | Onde aparece no logo |
|---|---|---|
| **Navy de marca** | **`#003566`** | Contorno do monitor, wordmark "Automations & Controls" — 44.534 px |
| **Dourado de marca** | **`#FDC500`** | Tela do monitor / campo do "i3" — 23.370 px |

As facetas do gradiente da tela (`#F7CA3C`, `#EAB306`, `#E0AC0B`, `#FFDC6E`) são efeito do arquivo original, não cores de sistema — **não entram no site**.

### 1.2 Paleta completa do site

Só as duas primeiras são medidas. As demais são **derivadas** delas, com contraste calculado (não escolhido no olho) — todos os valores abaixo foram conferidos pela fórmula WCAG.

| Token | Cor | Papel | Contraste medido |
|---|---|---|---|
| `--navy` | `#003566` | Cor estrutural: fundos de faixa, títulos sobre claro, botão primário | 12,34:1 sobre branco |
| `--navy-fundo` | `#001D3D` | Seção escura profunda / rodapé | branco por cima = 16,89:1 |
| `--navy-tinta` | `#000814` | Rodapé, quando quiser o fecho mais fundo que o resto | branco por cima = 20,1:1 |
| `--navy-hover` | `#002647` | Estado hover do botão primário | 15,35:1 sobre branco |
| `--navy-chip` | `#D7E3F0` | Fundo do chip de seta do CTA (o `--azul-claro` do UnidoCLP) | navy por cima = 9,49:1 |
| `--navy-luz` | `#8FB4DC` | Links e accents **sobre fundo escuro** | 7,83:1 sobre `#001D3D` |
| `--dourado` | `#FDC500` | Accent de marca: barras, sublinhados, ícones, números de destaque | 7,74:1 sobre navy · 10,59:1 sobre `#001D3D` |
| `--dourado-txt` | `#6B5000` | A **única** forma de escrever em dourado sobre fundo claro | 7,57:1 sobre branco |
| `--off-white` | `#F2F5F8` | Seção clara alternada | — |
| `--branco` | `#FFFFFF` | Fundo padrão | — |
| `--txt` | `#1A1A1A` | Corpo sobre claro | 17,4:1 |
| `--txt-2` | `#40607F` | Eyebrow e texto secundário (steel-blue derivado do navy) | 6,57:1 sobre branco · 6,0:1 sobre off-white |
| `--txt-suave` | `#5A5A5A` | Legendas, rótulos de números | 6,9:1 |
| `--txt-inv` | `#FFFFFF` | Texto sobre escuro | — |
| `--txt-inv-2` | `rgba(255,255,255,.72)` | Parágrafo sobre escuro | — |

### 1.3 Regras de uso — leia antes de pintar qualquer coisa

1. **O navy é a cor estrutural, o dourado é o accent.** Mesma lógica do UnidoCLP (azul estrutural + laranja escasso), com os papéis herdados da marca real. O dourado **nunca** é fundo de seção inteira e **nunca** é fundo de botão **em repouso** — ele é a linha, a barra, o ícone, o número, o sublinhado, o estado ativo. **Exceção medida e confirmada:** o *hover* de todo botão preenche em dourado com tinta navy (7,74:1) — transitório, um de cada vez, sob o ponteiro. Ver §6.3.
2. **Teto de dourado: no máximo 2 ocorrências por dobra.** Regra que veio do UnidoCLP e vale ainda mais aqui, porque `#FDC500` é muito mais saturado que o laranja de lá. Três manchas douradas numa tela viram "site de construtora".
3. **`#FDC500` não é cor de texto sobre claro** — 1,6:1 contra branco, ilegível. Sobre claro, dourado só como preenchimento de forma. Para escrever em dourado sobre claro, use `--dourado-txt` (`#6B5000`).
4. **Sobre navy, o dourado brilha** (7,74:1) — é ali que ele deve viver: números de credibilidade, barras de dado, ícones do rodapé, o estado ativo do nav sólido escuro.
5. **Ritmo vertical alternado**, como no UnidoCLP: bloco branco → bloco off-white → bloco navy → bloco branco. A alternância é o que cria cadência de leitura numa página longa; blocos escuros seguidos matam o ritmo.
6. **Fotografia sempre full-bleed dentro do bloco**, com overlay de navy (`rgba(0,29,61,.6→.85)`) quando houver texto por cima. Nunca moldura decorativa, nunca sombra de caixa.

   **Duas seções conectadas dividem UMA fotografia** (`.dupla`). Quando duas
   seções escuras seguidas se leem como um bloco só, a foto sobe para um
   invólucro e as seções ficam transparentes — senão a imagem de cima termina
   e outra começa no meio do bloco. O véu abre só na faixa vertical sem texto
   entre as duas, e essa faixa é a INTERSECÇÃO das páginas que usam o
   componente (home 27–52%, services 30–57% → abre em 34–42%, fechado em 48%).
   Está em `ferramentas/previa_dupla.py`.

### 1.4 O que muda em relação ao UnidoCLP

| UnidoCLP | i3Automations | Motivo |
|---|---|---|
| `--azul #628AD1` (da referência zetta-joule) | `--navy #003566` (do logo do cliente) | O cliente já tem marca. Não se importa um azul emprestado por cima dela. |
| `--laranja #F2891F` (accent escasso do logo) | `--dourado #FDC500` (accent escasso do logo) | Mesmo papel, cor diferente — e a regra do "máximo 2 por dobra" viaja junto. |
| `--navy #002D4D`, `--carvao #1B1B1B`, `--preto` | `--navy-fundo #001D3D`, `--navy-tinta #000814` | A escala escura passa a ser toda em família navy, para o site ler como uma marca só. |
| Gradiente de herói azul→cinza→creme | **Sem gradiente creme** | O creme era transição para o clima leve/otimista do UnidoCLP. Aqui o herói é navy sólido ou foto com overlay navy — o cliente é industrial pesado e vende para o governo. |

---

## 2. Tipografia — **herdada na íntegra, sem alteração**

Esta é a parte que o cliente pediu como referência absoluta. **Nada aqui é para ser reinterpretado.** Os valores abaixo são os que estão hoje em `site/css/tokens.css` e `site/css/style.css` do UnidoCLP, em produção.

### 2.1 Família

**Outfit** — sans-serif geométrica arredondada, fonte variável cobrindo os pesos **300–500** num arquivo só.

```css
--font: "Outfit", system-ui, -apple-system, "Segoe UI", Roboto, sans-serif;
```

**Servida localmente, nunca por CDN.** Dois arquivos `.woff2` (latin e latin-ext) em `site/fonts/`, com `font-display: swap` e `unicode-range` para o navegador só baixar o que precisa:

```css
@font-face {
  font-family: "Outfit";
  font-style: normal;
  font-weight: 300 500;   /* variável: um arquivo, três pesos */
  font-display: swap;
  src: url("/fonts/outfit-latin.woff2") format("woff2");
  unicode-range: U+0000-00FF, U+0131, U+0152-0153, U+02BB-02BC, U+02C6, U+02DA,
                 U+02DC, U+0304, U+0308, U+0329, U+2000-206F, U+20AC, U+2122,
                 U+2191, U+2193, U+2212, U+2215, U+FEFF, U+FFFD;
}
/* + o mesmo bloco para outfit-latin-ext.woff2 com o range estendido */
```

> **Nota de EN-US:** o site é em inglês, então o `latin-ext` cobre praticamente nada do conteúdo. Manter o arquivo mesmo assim (nomes próprios, "Mercedes-Benz", eventual PT no rodapé), mas ele quase nunca será baixado — que é exatamente o objetivo do `unicode-range`.

**Uma família só para tudo.** Sem fonte de display separada, sem serifa, sem "fonte industrial pesada". A única exceção é `ui-monospace, SFMono-Regular, Menlo, Consolas, monospace`, usada em dados técnicos pontuais (códigos, tags, identificadores — aqui: UEI, CAGE, NAICS).

### 2.2 Escala — fluida, 9 degraus

Todos com `clamp()`, sem media query. A escala base é **14 · 15 · 16 · 17 · 20 · 28 · 38 · 44 · 200 px**.

```css
--fs-display: clamp(2.75rem, 10.4vw, 12.5rem);  /*  44px → 200px  — H1 do herói */
--fs-h2:      clamp(1.75rem, 2.3vw,  2.75rem);  /*  28px →  44px  */
--fs-h3:      clamp(1.5rem,  2vw,    2.375rem); /*  24px →  38px  */
--fs-lead:    clamp(1.25rem, 1.46vw, 1.75rem);  /*  20px →  28px  */
--fs-body:    clamp(1rem,    1.04vw, 1.25rem);  /*  16px →  20px  */
--fs-small:   1.0625rem;                        /*  17px          */
--fs-ui:      1rem;                             /*  16px  — nav, botões, CTA */
--fs-eyebrow: .9375rem;                         /*  15px          */
--fs-legal:   .875rem;                          /*  14px          */
```

### 2.3 Pesos, entrelinha e tracking — valores exatos

| Elemento | Tamanho | Peso | `line-height` | `letter-spacing` |
|---|---|---|---|---|
| `body` | `--fs-body` | **400** | **1.45** | — |
| `h1` | `--fs-display` | **300** | **.98** | **-.02em** |
| `h2` | `--fs-h2` | **300** | **1.05** | **-.01em** |
| `h3` | `--fs-h3` | **400** | **1.08** | **-.01em** |
| `.eyebrow` | `--fs-eyebrow` | **500** | — | **.01em** |
| `.lead` | `--fs-lead` | 400 | **1.36** | — |
| Nav / botão / CTA | `--fs-ui` | **500** | — | — |
| Número de credibilidade | `clamp(2.25rem, 3.4vw, 3.5rem)` | **300** | **1** | **-.02em** |
| Título de card | `1.25rem` | **500** | 1.2 | -.01em |
| Rodapé / legal | `--fs-legal` | 500 | — | .01em |
| `strong` | — | **500** (nunca 700) | — | — |
| Dado monoespaçado | `13px` / `1.5rem` | 500 | — | `.02em` / `.12em` |

**A regra que governa tudo isso: título grande = peso leve.** H1 e H2 são **300**. Quanto maior o tipo, mais leve ele fica; quanto menor, mais peso ganha (UI em 500). É o inverso do reflexo comum e é a assinatura visual do sistema — se um título grande aparecer em 600, o sistema quebrou.

**Nunca use peso acima de 500 em lugar nenhum.** O arquivo variável nem carrega 600/700; pedir isso força o navegador a sintetizar um falso-negrito.

### 2.4 Contenção de texto

```css
p        { hyphens: auto; -webkit-hyphens: auto; text-wrap: pretty; }
h1,h2,h3,h4 { hyphens: none; text-wrap: balance; }
.tabular { font-variant-numeric: tabular-nums; }
```

- `.lead` e `.cabecalho__lead`: `max-width: 46ch`
- `.corpo`: `max-width: 62ch`
- `h1` de página interna: `max-width: 18ch`
- Rótulo de número (`dd`): `max-width: 22ch`

> **Adaptação EN-US:** o `hyphens: auto` existia por causa de palavras longas do PT-BR ("desenvolvimento", "instrumentação"). Em inglês ele quase nunca dispara — **manter mesmo assim**, sem custo, e porque termos técnicos longos aparecem ("instrumentation", "commissioning"). O `text-wrap: balance` nos títulos é o que realmente importa e vale igual nos dois idiomas.

### 2.5 Links em texto corrido

```css
p a, li a.link {
  text-decoration: underline;
  text-decoration-thickness: 1px;
  text-underline-offset: 3px;
  transition: color .18s ease;
}
p a:hover { color: var(--navy-hover); }
```

Sublinhado **só** em link dentro de parágrafo. Link de navegação, de card e de CTA nunca é sublinhado — tem outro sinal (régua que cresce, chip que desliza).

---

## 3. Espaçamento e layout — herdados

```css
/* escala base 8px */
--s-1: 4px;   --s-2: 8px;   --s-3: 16px;  --s-4: 24px;
--s-5: 32px;  --s-6: 48px;  --s-7: 64px;  --s-8: 96px;
--s-9: 128px; --s-10: 160px; --s-11: 200px;

--container:    1376px;
--pad-lateral:  48px;    /* 32px < 1024 · 20px < 768 */
--nav-altura:   96px;    /* 80px < 1024 · 64px < 768 */
--sec-y:        var(--s-10);   /* --s-8 < 1024 · --s-7 < 768 */
--gap-bloco:    var(--s-7);    /* --s-6 < 1024 · --s-5 < 768 */
--gap-card:     16px;
```

**Os dois vãos descem juntos, e a razão entre eles é o que importa.** `--sec-y`
separa ASSUNTO (uma seção da outra) e `--gap-bloco` separa GRUPO (o cabeçalho
de uma seção do componente dela). Enquanto `--gap-bloco` era fixo em 64, a
razão caía de 2,5× no desktop para **1,0× no celular** — e a hierarquia
simplesmente sumia, com o vão entre duas seções inteiras igual ao vão interno
de uma. Agora a razão fica em 2,5× / 2,0× / 2,0×.


**Grid de 12 colunas**, `gap: 0` (o respiro vem do span, não do gap). O split dominante é **4/8**: `.bloco__esq { grid-column: span 4 }` para o eyebrow+título, `.bloco__dir { grid-column: 5 / -1 }` para o texto e o CTA. Abaixo de 1024px, os dois viram `1 / -1` e ganham `row-gap: var(--s-4)`.

---

## 4. Tom de voz

O UnidoCLP fala com estudantes e técnicos brasileiros. O i3Automations fala com **engenheiros de planta, gerentes de manutenção e compradores públicos americanos**. O registro sobe.

### 4.1 Regras

- **Autoridade técnica sem adjetivo.** Frases curtas, declarativas, primeira pessoa do plural. "We commission the panel and hand you the drawings" > "We are passionate about delivering world-class automation excellence."
- **Prova antes de promessa.** O site atual já entrega os números; use-os literalmente: **279+ projetos no mundo, 158+ nos EUA, 78+ na Flórida, mais de 150.000 tags historiados em PI System, desde 2000**. Número concreto vale mais que superlativo.
- **Toda seção segue o padrão:** eyebrow pequeno → título grande (1–2 linhas, peso 300) → parágrafo curto → CTA discreto (chip de seta + texto). Nunca um botão gritante no meio do texto.
- **A frase do cliente é boa e deve sobreviver:** *"Good control strategy beats more expensive instrumentation."* É a tese da empresa em oito palavras — merece ser dita grande, sozinha, num bloco navy. E o par dela: *"Senior control experts know things they do not teach in school."*
- **O tagline atual** — "DEDICATED TO EXCEEDING YOUR NEEDS WITH UNWAVERING COMMITMENT" — é genérico e está em caixa alta. Reescrever mantendo a promessa, ou aposentá-lo em favor da frase de controle acima. **Decisão a confirmar com o usuário.**
- **Sem jargão de marketing:** nada de "synergy", "cutting-edge", "revolutionize", "world-class", "passionate". Se a frase serviria para uma agência de publicidade, ela não serve aqui.
- **Nada de caixa alta em bloco.** Caixa alta só em rótulos de ≤ 3 palavras. O sistema tipográfico não tem tracking positivo suficiente para caixa alta longa ser legível.

### 4.2 Vocabulário de credibilidade que o público-alvo reconhece

Deve aparecer literalmente, porque é o que o comprador procura no Ctrl+F: **Rockwell, Siemens, Schneider, Ignition, VTScada, Canary, PI System, SCADA, HMI, PLC, MCC, commissioning, instrumentation**. Certificações (**Ignition Certified, VTScada Certified, Canary Certified**) e credenciais de fornecedor federal (**UEI XUZ4WKEZLS67, CAGE 9ZJM6, NAICS 541511** + secundários 238210, 334513, 335313, 518210, 541330, 541512) têm bloco próprio — para o comprador público, isso é o conteúdo mais importante da página inteira.

---

## 5. Estrutura de página

Padrão a seguir, não a copiar literalmente. Ordem herdada do UnidoCLP, conteúdo remapeado para o i3.

1. **Nav fixo** — logo à esquerda, links à direita, CTA de contato no canto. Transparente sobre o herói, sólido branco ao rolar (ver §6.1).
2. **Herói** — full-bleed navy ou foto com overlay navy. H1 gigante em peso 300, duas linhas, entrando linha a linha. Apoio curto embaixo à esquerda com régua vertical que se desenha. Sem CTA grande dentro do herói.
3. **Números de credibilidade** — faixa logo abaixo da dobra: `279+ projects worldwide · 158+ in the U.S. · 78+ in Florida · 150,000+ historized tags · since 2000`. Números em peso 300, dourado sobre navy ou navy sobre claro.
4. **Capabilities** — bloco alternado claro/escuro com as 8 competências: Control Panels, PLC Programming, SCADA Programming, Commissioning, Instrumentation, Network, Motor Controls, Software Development.
5. **Platforms** — Rockwell / Siemens / Schneider + Ignition / VTScada / Canary / PI System. Grid de marcas ou barra de plataformas; **não** um carrossel de logos genérico.
6. **Industries served** — Oil & Gas (Houston), Water & Wastewater (Flórida), Automotive (Mercedes-Benz/Daimler, BMW), Paper mills, Solar & renewables. Cada um com foto de contexto real, não banco de imagem quando houver alternativa.
7. **Past performance** — grid de cases. É o equivalente ao "Trabalhos Realizados" do UnidoCLP e é o que fecha contrato B2B.
8. **Government / capability statement** — bloco escuro dedicado: UEI, CAGE, NAICS, certificações, e o PDF de Capabilities Statement para download.
9. **CTA final escuro** → **rodapé** (`--navy-tinta`): headline curta, colunas de navegação, dois telefones (Sales +1 407 820-0299 · Support +1 941 666-1880), e-mail, WhatsApp, redes (LinkedIn, Facebook, YouTube, Instagram @i3automations.plc), logo, copyright, Privacy Policy, Terms and Conditions.

**Páginas:** Home · Who We Are · Capabilities · Past Performance · Services · Gallery · Contact (espelhando o menu atual, para não perder nada na migração) + Privacy Policy e Terms and Conditions no rodapé.

---

## 6. Componentes

### 6.1 Nav

- `position: fixed`, altura `--nav-altura`, `border-bottom: 1px solid transparent`.
- Sobre o herói: fundo transparente, texto branco, logo em versão clara, CTA de borda `rgba(255,255,255,.6)`.
- Ao rolar (`.is-rolado`) ou em página interna (`.nav--solido`): fundo branco, texto `--txt`, logo escuro, `box-shadow: 0 1px 20px rgba(0,53,102,.06)`, borda inferior visível. Transição de `.25s ease` em `background-color, box-shadow, border-color`.
- Link do nav: 16px/500, com régua de 2px em `--dourado` que cresce da esquerda (`transform: scaleX(0→1)`, `.22s ease`) no hover e fica fixa em `[aria-current="page"]`.
  > **Mudança em relação ao UnidoCLP:** lá a régua era azul (a cor estrutural). Aqui ela é **dourada** — é o lugar mais barato de colocar a marca e não conta para o teto de 2 por dobra, porque o nav não é dobra.
- Hambúrguer < 768px: três traços de 22×1px em `currentColor`, viram X com `transform` em `.25s ease`.

### 6.2 CTA discreto (o componente principal do sistema)

Chip quadrado de 32×32 com seta + texto ao lado. **É o CTA padrão** — botão preenchido é exceção.

```css
/* tipografia: declarada UMA vez, no grupo `.nav__cta, .cta, .botao` */
.nav__cta, .cta, .botao { font-family: var(--font); font-size: var(--fs-ui);
                          font-weight: 500; letter-spacing: normal; }

.cta { display: inline-flex; align-items: center; gap: 12px;
       min-height: 44px; transition: color .18s ease; }
.cta__chip { width: 32px; height: 32px; display: inline-flex;
             align-items: center; justify-content: center; flex-shrink: 0;
             background: var(--navy-chip); color: var(--navy);
             transition: background-color .2s ease, transform .2s ease, color .2s ease; }
.cta__chip svg { width: 13px; height: 13px; }

/* o chip acende DOURADO em qualquer superfície — ver §6.3 */
.cta:hover .cta__chip { background: var(--dourado); color: var(--navy);
                        transform: translateX(3px); }
.cta:hover            { color: var(--accent-txt); }
```

Sobre fundo escuro: chip em `rgba(255,255,255,.12)` com seta branca. O **hover é o mesmo em toda superfície** (§6.3).

O rótulo é a única peça não preenchida do componente, então é a única que precisa de token por superfície: `--accent-txt` dá `#6B5000` no claro (7,57:1 sobre branco) e `#FDC500` no escuro (12,35:1). Nas superfícies navy — `.heroi`, `.cabecalho`, `.faixa`, `.rodape`, `.secao--escura` — o token é reapontado para `--dourado`, porque `#6B5000` sobre navy dá **2,23:1** e o rótulo sumiria.

`margin-top: var(--s-6)` quando o CTA vem depois de `p`, `.corpo` ou `.lead`.

### 6.3 Botões

Retângulo **sem raio de canto**, borda de 1px, altura mínima 48px, padding lateral 24px, texto 16px/500, ícone opcional de 18px.

```css
/* REPOUSO — navy ou borda fina, nunca dourado */
.botao            { min-height: 48px; padding: 0 24px; gap: 10px;
                    border: 1px solid var(--borda-ui);
                    background: var(--sup-1); color: var(--tinta);
                    transition: background-color .18s ease, color .18s ease,
                                border-color .18s ease; }
.botao--principal { background: var(--navy); color: #fff; border-color: var(--navy); }
.botao--claro     { background: transparent; color: #fff;
                    border-color: rgba(255,255,255,.45); }
```

**O acender é dourado, e é um só (revisto em 2026-08-19 — ver abaixo):**

```css
.botao:hover, .botao--principal:hover, .botao--claro:hover,
.nav__cta:hover, .nav--sobre-heroi .nav__cta:hover,
.nav.is-rolado .nav__cta:hover, .nav--solido .nav__cta:hover {
  background: var(--dourado); color: var(--navy); border-color: var(--dourado);
}
```

**O rodapé é descoberto, não rolado (2026-08-20).** O fecho fica preso ao pé da
janela desde a carga, escondido atrás do `<main>`, que rola por cima dele como
a folha de um livro virando. **É layout puro** — `position: sticky` mais um
`z-index`; nenhuma animação, nenhum JavaScript no caminho da rolagem, nada que
possa engasgar.

Duas condições, e as duas são consequência desta paleta e desta estrutura:

**A guarda de tamanho.** Um sticky mais alto que a janela não revela nada: ele
é puxado para cima até o pé encostar no pé da tela, e o topo — que é onde a
frase de fecho mora — fica fora da tela o tempo todo. O rodapé mede **732px**
com as quatro colunas numa linha, 1053 em duas e 1694 em uma. Por isso a
revelação só liga em `min-width: 900px and min-height: 780px`; fora disso o
rodapé é estático e a frase entra rolando, como antes.

**A aresta da folha.** Sete das nove páginas terminam em `--sup-3` e o rodapé é
`--sup-3-fundo`: medido, **1,19:1 no claro e 1,66:1 no escuro** — a folha
subiria e nada mudaria na tela. A borda de 1px em `rgba(255,255,255,.55)` é o
que torna a subida legível. É **borda e não sombra** porque este documento
decide isso duas vezes (§6 item 6 e §6.3); e é `.55` e não o `.3` de
`--filete-forte` porque um filete é divisória decorativa (que o WCAG 1.4.11
isenta) enquanto esta aresta CARREGA o efeito — o vizinho mais claro
(`#003566`, tema escuro) obriga a `.55` para passar 3:1.

**A roda ganhou inércia (2026-08-20), e isto REVERTE uma decisão deste
documento.** Até aqui a rolagem era estritamente nativa e o `memoria.md`
registrava "nada sequestra a roda" desde 19/08. O usuário pediu o
desaceleramento e confirmou a via depois de ver os custos — registro aqui para
que a reversão não pareça esquecimento.

**A página rola de verdade.** `window.scrollTo` por quadro, nunca `transform`
num wrapper. É o que mantém `position: sticky` vivo — e o rodapé revelado da
linha acima é sticky, então a via do wrapper teria matado o item anterior desta
mesma tabela. Mantém junto a barra nativa, o "localizar na página", as âncoras
e o leitor de tela.

**Três coisas que a implementação NÃO faz, e cada uma é uma decisão:**

1. **Não toca em trackpad.** O sistema já aplica momentum próprio nele; somar o
   nosso dá o "duplo momentum" que faz a página parecer atrasada. Eventos com
   `|deltaY| < 50px` passam direto — roda de mouse manda ~100px por dente,
   trackpad manda muitos e pequenos.
2. **Não toca em teclado nem em barra de rolagem.** Continuam nativos; o alvo
   apenas se reancora quando a página se move sem nós.
3. **Não roda com `prefers-reduced-motion`.** Rolagem animada é das poucas
   coisas que provocam enjoo de verdade (regra dura nº3), e aqui não há
   meia-medida: desliga inteiro.

A força mora numa constante só, `LERP = 0.11` em `main.js §11`: 90% da
distância em ~330ms. A suavização é **por tempo e não por quadro** — `k` fixo
rodaria o dobro de rápido num monitor de 120Hz; com `dt` na conta, 60/90/120/144Hz
entregam os mesmos 100/333/667ms para 50/90/99%.

**Regras duras:**
- **Sem `border-radius` em lugar nenhum do site.** O sistema é de cantos retos — um botão arredondado destrói a coerência.
- **Sem sombra em botão.** A elevação do sistema vem de fundo e borda, não de sombra.
- **Nenhum botão em REPOUSO tem fundo `--dourado`.** Um botão dourado parado vira o elemento mais alto da página e rouba o navy. Em repouso o dourado só entra como borda ou como ícone.
- **No HOVER, todo botão preenche em `--dourado` com tinta `--navy`.** Um gesto, uma cor, em qualquer seção e nos dois temas.
- Alvo de toque mínimo: 44px (CTA) / 48px (botão).

#### Por que o hover dourado (revisão de 2026-08-19)

A versão anterior desta seção dizia *"Nunca um botão com fundo `--dourado`"*, sem separar repouso de hover. O resultado foi **quatro acenderes diferentes para um gesto só**: `.nav__cta` preenchia branco sobre o herói e navy depois de rolar; `.cta` acendia navy em seção clara e dourado em seção escura; `.botao` preenchia navy sempre. O mesmo controle mudava de cor conforme a seção sob ele.

As alternativas foram **medidas** com `ferramentas/contraste.py`, não escolhidas:

| via | tema claro | tema escuro | serve? |
|---|---|---|---|
| dourado como **borda** | 1,60:1 sobre branco · 1,46:1 sobre off-white | 12,35:1 | **não** — reprova o piso de 3:1 do WCAG 1.4.11 e some no claro |
| dourado como **tinta** | 1,60:1 sobre branco | 12,35:1 | **não** — é a regra crítica nº4 do `CLAUDE.md` |
| `--accent-txt` como tinta | 7,57:1 sobre branco · **2,23:1 sobre navy** | 12,35:1 | **não** — muda de cor por superfície, que é o defeito a corrigir |
| **preenchimento dourado + tinta navy** | **7,74:1** | **7,74:1** | **sim** |

Só o preenchimento é o mesmo amarelo em todo lugar, e a razão é estrutural: **quando o campo vira dourado, a superfície de baixo deixa de importar.** Borda e tinta dependem dela; preenchimento não.

O par `#003566` sobre `#FDC500` não é arbitrário — é **o logo do cliente**: glifo navy dentro do campo dourado da tela do monitor. É a mesma dupla que o realce da headline do herói já usa.

A regra antiga continua valendo para o **repouso**, que não mudou. O hover é transitório, existe um de cada vez e vive sob o ponteiro — a mesma isenção que o §6.5 já concede à lente. **Confirmado explicitamente com o usuário em 2026-08-19** (`CLAUDE.md` regra crítica nº1).

### 6.4 Números de credibilidade

`<dl>` em grid de 4 colunas (2 colunas < 768px), separado do bloco acima por `border-top: 1px solid` e `padding-top: var(--s-6)`. `dt` em `clamp(2.25rem, 3.4vw, 3.5rem)`/300/`tabular-nums`, cor `--navy` (ou `--dourado` sobre escuro). `dd` em `--fs-small`/400/`--txt-suave`, `max-width: 22ch`.

### 6.5 Ícones e fotografia

- Ícones **lineares, monocromáticos, 1px de traço**. Branco sobre escuro, navy sobre claro. Sem ícone colorido, sem ilustração 3D.
- Fotografia full-bleed dentro do bloco, `object-fit: cover`, sem moldura. Overlay navy quando houver texto por cima.
- **Preferência absoluta por foto real de campo** (painel montado, comissionamento, sala de controle do cliente) sobre banco de imagem. Aprendizado direto do UnidoCLP: foto de banco ao lado de foto real denuncia a si mesma. Se só houver banco de imagem para um tema, é melhor não ter a foto.

### 6.6 Desenho gerado (planta e braço)

Dois componentes do site não são imagem: são **geometria gerada por código e desenhada em aresta**, em WebGL2 escrito à mão (§9 continua valendo — nenhuma dependência de terceiros).

- **`.planta`** (`js/planta.js`) — a topologia de uma instalação inteira: ativos de campo, supervisão no centro, telemetria correndo pelos enlaces. Vive sobre papel claro.
- **`.braco`** (`js/braco.js`) — a peça do herói: um robô de 6 eixos com cinemática direta na GPU, orbitável por arrasto, com um ciclo de trabalho de 13 s. Vive sobre o navy do herói.

Regras dos dois:

1. **Aresta, nunca face.** O assunto do site é o desenho técnico por baixo da fotografia; preencher face quebraria isso.
2. **Peso de aresta é hierarquia, não decoração.** 1 é contorno estrutural, abaixo de .5 é sombreado. A peça tem de se ler inteira **só com o contorno estrutural** — e é ele que responde pelo 3:1 do WCAG 1.4.11.
3. **Atenuação por profundidade é o único mecanismo de forma.** Sem face não há remoção de linha oculta: o que separa a frente do fundo é só isso. Piso alto demais e a peça vira gaiola transparente.
4. **Cor sempre de token, lida por parser hexadecimal próprio.** `getComputedStyle` devolve o hexadecimal literal — ver a armadilha no `memoria.md`.
5. **O enquadramento se resolve sozinho** quando a silhueta muda de proporção com o ângulo, e a distância depende do ÂNGULO, nunca do quadro — senão a peça pulsa de tamanho.
6. **`prefers-reduced-motion`** congela o ciclo numa pose e mantém a interação por ponteiro, que carrega significado.

O dourado destes componentes é **transitório e sob o ponteiro**. Não conta para o teto de 2 dourados por dobra do `CLAUDE.md`, porque não é mancha permanente.

---

## 7. Movimento

**Uma gramática só, herdada sem alteração: entra com desfoque e sobe, com saída exponencial.** Curva única em todo o site: `cubic-bezier(.16, 1, .3, 1)`.

```css
.reveal {
  opacity: 0;
  transform: translate3d(0, 22px, 0);
  filter: blur(6px);
  transition: opacity   .85s cubic-bezier(.16,1,.3,1),
              transform .85s cubic-bezier(.16,1,.3,1),
              filter    .85s cubic-bezier(.16,1,.3,1);
  transition-delay: calc(var(--i, 0) * 70ms);   /* cascata pelo índice */
}
.reveal.is-visivel { opacity: 1; transform: none; filter: blur(0); }
```

O atraso em cascata vem de `--i` no elemento, **não** de uma classe por item. Um `IntersectionObserver` só, que adiciona `.is-visivel` e para de observar.

**Vocabulário completo de movimento:**

| Movimento | Onde | Duração / curva |
|---|---|---|
| `.reveal` | Tudo que entra na tela ao rolar | `.85s` + `--i × 70ms` |
| `.entra-linha` | H1 do herói, linha a linha, **uma vez só** | `.95s` + `--i × 90ms` |
| Régua que se desenha (`scaleY 0→1`) | Barra vertical do apoio do herói | `1.1s`, delay `.9s`, `backwards` |
| `.rodape__headline` — palavras plotadas por `clip-path` | Frase de fecho, nas nove páginas | `.72s` + `--i × 55ms` |
| Régua do fecho (`scaleX 0→1`) | Sob a frase de fecho, após a última palavra | `1.05s`, delay `--n × 55ms + 140ms` |
| Chip que desliza (`translateX(3px)`) | Hover do CTA | `.2s ease` |
| Sublinhado que cresce (`background-size 0%→100% 1px`) | Links do rodapé | `.4s` |
| Régua do nav (`scaleX 0→1`) | Hover / página atual | `.22s ease` |
| Troca de estado do nav | Fundo, sombra, borda ao rolar | `.25s ease` |
| Hover de cor (texto, botão, borda) | Todo o site | `.18s`–`.2s ease` |
| **Junta de corte** — linha de eixo traçada por `clip-path` | Emenda onde a SUPERFÍCIE muda, nas 9 páginas | `1.15s` |
| **Junta interna** — tique de 120px na origem do container | Emenda entre duas seções da MESMA superfície | `1.15s` |
| **Rodapé revelado** — `position: sticky` sob o `<main>` | O fecho das 9 páginas, descoberto ao fim da rolagem | sem duração: é layout |
| **Inércia da roda** — lerp sobre `window.scrollY` | Roda de mouse, no site inteiro | ~330ms para 90% |

**A junta entre seções (2026-08-20).** O site se lê como um conjunto encadernado
de desenho técnico, e faltava a marca que um conjunto usa para dizer que o
desenho CONTINUA. Quando uma planta não cabe numa folha ela é cortada por uma
**linha de eixo** e cada folha recebe a referência da seguinte. A regra é
literal, e é ela que produz a variedade sem inventar nada:

| o que acontece na borda | leitura | o que aparece |
|---|---|---|
| a superfície MUDA | é outra folha | linha de eixo + `SHEET 04 OF 07` |
| a superfície é a MESMA | é a mesma folha | só o tique de construção |
| `.faixa` full-bleed | não é folha, é chapa inserida | nada — ela já tem entrada própria |

Duas seções navy seguidas **não** ganham linha: não há corte entre elas. Quem
decide não é quem escreve o HTML — é `juntar()`, em `ferramentas/build_paginas.py`,
que lê a superfície de cada seção e escreve a classe. O rótulo mora sempre na
ponta em que o traço TERMINA, então o mesmo `clip-path` que desenha a linha o
plota por último: linha de construção primeiro, anotação depois.

**Linha tracejada não se anima por escala.** `scaleX(0→1)` encolhe o PADRÃO
junto: a 8% do percurso o traço de 26px desenha com 2px e o que está na tela é
uma linha pontilhada — outra convenção de desenho. `clip-path` revela o padrão
no tamanho verdadeiro desde o primeiro quadro. Medido em
`ferramentas/previa_junta.py`, que lê a geometria do próprio `style.css`.

**A junta não usa dourado**, e não é economia: ela cai exatamente na dobra
entre duas seções, e a regra crítica nº5 admite duas manchas por dobra. Uma
junta dourada estouraria a conta de toda seção que já usa as duas.

**Regras duras:**

1. **Nenhuma transição sem estado inverso definido.** Se entra, sabe voltar.
2. **`animation-fill-mode: backwards` é obrigatório em qualquer animação com `animation-delay` longo.** Sem ele, o elemento fica com o estilo base visível durante o atraso — no UnidoCLP isso deixou tocos de linha parados na tela por 6,5 segundos antes de a animação começar. É a pegadinha mais cara do sistema.
3. **`prefers-reduced-motion: reduce` não é opcional.** `.reveal` e `.entra-linha` viram estado final imediato, sem `transition`; animações contínuas somem; o que carrega significado (uma topologia que se desenha, por exemplo) aparece com um fade só, sem viagem.
4. **`will-change` só com teto.** Só em elemento efetivamente animando, e removido quando ele sai da dobra — senão a camada promovida fica na GPU pela página inteira.
5. **Sem parallax de rolagem como efeito decorativo.** Movimento por ponteiro (deriva suave, amplitude ≤ 18px) é aceito; movimento por rolagem só quando comunica algo.
6. **Nada pisca, nada pula, nada rebate.** Sem `bounce`, sem `elastic`, sem `spin`.

---

## 8. Logo

Arquivo real em `referencia/i3automations/logo-i3.png` (1024×387). Duas partes:

1. **Ícone** — um monitor/laptop de contorno navy com a tela dourada e o "i3" vazado em navy. A tela tem facetas de gradiente (raios saindo do centro), que são tratamento do arquivo original.
2. **Wordmark** — "Automations & Controls" em sans-serif humanista navy, peso semibold, duas linhas.

**Direção para o site novo:**

- **Ícone:** achatar — remover as facetas de gradiente da tela e deixar `#FDC500` chapado com o contorno `#003566`. Ele fica ótimo pequeno: favicon, marca d'água, marcador de lista, estado de carregamento. As facetas somem em qualquer tamanho abaixo de ~64px de qualquer jeito, então mantê-las só custa peso de arquivo.
- **Wordmark:** **re-tipografar em Outfit 500**, em duas linhas, alinhado à esquerda do ícone. A fonte atual do logo não é Outfit e, no meio de um site inteiro em Outfit, a diferença aparece. Re-tipografar unifica; manter o PNG deixa a marca parecendo colada.
- **Nome:** "i3Automations" (uma palavra, i minúsculo) é como o site atual se chama; "i3 Automations & Controls" é a marca completa do logo. **Usar "i3Automations" na copy e no nav; "i3 Automations & Controls" no rodapé, na assinatura e nos documentos formais.**
- **Duas versões no nav:** clara (para o nav transparente sobre o herói) e escura (para o nav sólido), trocadas por CSS, como no UnidoCLP.
- O ícone dourado sobre navy é a combinação mais forte da marca — é o favicon e é o emblema de fecho de seção.

---

## 9. Stack

Igual ao UnidoCLP, e por escolha, não por inércia: **HTML + CSS + JS puro, sem framework e sem build step.** Deploy é publicar arquivos estáticos.

- Fonte servida localmente (`site/fonts/`), sem CDN.
- Sem dependência de terceiros no runtime.
- Imagens em AVIF + WebP + JPEG com `<picture>` e `sizes` corretos.
- **Cuidado com caminhos absolutos:** o UnidoCLP tem 204 `href="/css/..."` e por isso **só funciona servido na raiz de um domínio** — o que eliminou GitHub Pages de projeto. Decidir cedo: ou o host serve na raiz, ou os caminhos são relativos desde o primeiro arquivo.

---

## 10. Decisões em aberto

| # | Questão | Recomendação | Estado |
|---|---|---|---|
| 1 | Idioma do site | **EN-US** — cliente e público são americanos | **Confirmado (2026-08-18)** |
| 2 | Paleta | Navy `#003566` + dourado `#FDC500` do logo real, no lugar do azul da referência | **Confirmado (2026-08-18)** |
| 3 | Tagline "DEDICATED TO EXCEEDING YOUR NEEDS…" | Aposentar em favor de "Good control strategy beats more expensive instrumentation" | **Confirmar** |
| 4 | Fotografia | Pedir ao cliente fotos reais de painel, comissionamento e sala de controle | **Pendente com o cliente** |
| 5 | Capabilities Statement (PDF) | Manter como download no bloco de governo | Provável; confirmar se há versão atualizada |
| 6 | Domínio / hospedagem | Cloudflare Pages, servindo na raiz | A definir |
| 7 | Formulário de contato | Sem back-end no plano atual; precisa de serviço externo ou `mailto:` | A definir |
| 8 | Gallery | O menu atual tem "Gallery"; decidir se vira seção de Past Performance ou página própria | A definir |
