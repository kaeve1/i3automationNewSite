# Design — i3Automations & Controls (revisão de 2026-08-25)

**Este documento substitui `specs/design.md`.** O anterior continua no repositório
como registro histórico, mas onde os dois divergirem, vale este. O §10 lista
exatamente o que morreu e por quê.

A revisão nasceu de um feedback do cliente que rejeitava três coisas do site
publicado: a cor amarela, o braço robótico do herói, e a distância de clima em
relação ao Universo do CLP — que ele chamou de perfeito e não quis mudar em nada.

---

## 0. O diagnóstico que organiza o resto

O cliente disse "não gostei do amarelo". O `#FDC500` é a cor do logo dele,
medida em pixel. Ninguém odeia a própria marca — o que incomodava era o **uso**.

Comparando os dois `tokens.css`:

| | UnidoCLP | i3 (publicado) |
|---|---|---|
| cor dominante | `#628AD1` — azul médio, claro | `#003566` / `#001D3D` — navy de fundo |
| neutro quente | `#FCEEE1` creme | **não existia** |
| accent | `#F2891F` laranja | `#FDC500` amarelo saturado |
| faixa média | o site inteiro vive nela | saltava de `#D7E3F0` para `#003566` |

O site não tinha faixa média e não tinha nada quente. Saltava de quase-branco a
quase-preto, e o `#FDC500` entrava como a única coisa quente num campo escuro e
saturado. **Navy com amarelo saturado é a paleta de placa de sinalização** — cone,
cavalete, fita de perigo. Lia como alerta, não como marca.

No UnidoCLP o laranja funciona porque vive num ambiente arejado azul-claro e
creme. A cor não é melhor; **o ar em volta dela é**.

Quando o cliente pediu "a tonalidade do universo do clp", ele não estava pedindo
o laranja. Estava pedindo **luz**. E o `specs/design.md` §1.4 tinha decidido o
oposto — *"sem gradiente creme, o cliente é industrial pesado"*. Essa linha é a
causa raiz do feedback, e é a primeira coisa que este documento revoga.

---

## 1. Paleta

### 1.1 O que é medido e o que é derivado

`#003566` e `#FDC500` continuam sendo os dois únicos valores **medidos** —
amostrados por contagem de cor em `logo/logonova.png` (1024×387): 44.534 px de
navy, 23.370 px de dourado. Todo o resto abaixo é **derivado deles por conta**,
com contraste conferido pela fórmula WCAG. Nenhum valor foi escolhido no olho.

O navy da marca em HSL é **H209 · S100 · L20**. Toda a família azul nova é o
**mesmo matiz 209**, variando saturação e luminosidade — é o que faz o site ler
como uma marca só em vez de uma coleção de azuis.

### 1.2 A tabela

| Token | Cor | Papel | Contraste medido |
|---|---|---|---|
| `--navy` | `#003566` | Estrutural: botão primário, títulos, nav sólido | 12,34:1 sobre branco |
| `--azul` | `#4D8ECB` | **Accent.** Régua do nav, barras, sublinhados, estado ativo | 3,47:1 sobre branco |
| `--azul-txt` | `#2C6396` | A forma de **escrever** em accent sobre claro | 6,30:1 branco · 5,70:1 quente |
| `--azul-luz` | `#88B4DD` | O accent **sobre bloco escuro** | 4,56:1 sobre bloco · 5,65:1 sobre navy |
| `--azul-bloco` | `#0D4477` | Fundo do bloco escuro — substitui `#001D3D` | branco por cima = 9,95:1 |
| `--azul-chip` | `#DCE9F5` | Fundo do chip de seta do CTA | navy por cima = 10,00:1 |
| `--quente` | `#F7F3EC` | **O neutro quente que faltava** | 1,11 vs branco · texto = 15,74:1 |
| `--off-white` | `#F2F5F8` | Seção clara alternada, fria | — |
| `--branco` | `#FFFFFF` | Fundo padrão | — |
| `--txt` | `#1A1A1A` | Corpo sobre claro | 17,40:1 branco · 15,74:1 quente |
| `--txt-2` | `#40607F` | Eyebrow e texto secundário | 6,57:1 sobre branco |
| `--txt-suave` | `#5A5A5A` | Legendas e rótulos | 6,90:1 |
| `--txt-inv` | `#FFFFFF` | Texto sobre escuro | 9,95:1 sobre bloco |
| `--dourado` | `#FDC500` | **Existe SÓ dentro do logo.** Zero ocorrências no CSS de página | — |

### 1.3 A coincidência que justifica a escolha

`--azul` derivado do navy da marca é **H209 · S55 · L60**, que arredonda para
`#4D8ECB` a 3,47:1 sobre branco.

O `--azul` do UnidoCLP é `#628AD1` — **H218 · S55 · L60**, a 3,46:1.

Mesma saturação, mesma luminosidade, mesmo contraste até a segunda casa. Nove
graus de matiz separam os dois. **Partindo do logo do próprio cliente, chegamos
praticamente no accent do site que ele chamou de perfeito.** Não é imitação: é o
mesmo lugar do espaço de cor, alcançado pela marca dele.

### 1.4 Regras de uso

1. **O dourado saiu do site.** Ele vive dentro do logo, facetado, como sempre
   foi. Nenhuma régua, barra, ícone, número ou hover usa `#FDC500`. A marca ecoa
   pelo **matiz 209 compartilhado**, não por repetir a cor do accent.
2. **`--azul` é preenchimento de forma, nunca texto sobre claro** (3,47:1
   reprova o piso de 4,5:1). Para escrever em accent sobre claro existe
   `--azul-txt`. É a mesma disciplina de dois tokens que o UnidoCLP aplica ao
   laranja (`--laranja` + `--laranja-esc`).
3. **Sobre bloco escuro o accent troca de token**, não de cor: `--azul-luz`.
   `--azul` sobre `--azul-bloco` dá 2,87:1 e reprova o piso de 3:1 do WCAG
   1.4.11 — foi medido e falhou, por isso o token existe.
4. **Alternância suavizada.** O ritmo vertical continua: branco → off-white →
   quente → bloco escuro → branco. O que muda é a profundidade do escuro:
   `#001D3D` e `#000814` saem, `--azul-bloco #0D4477` entra. O bloco escuro
   agora é **azul**, não quase-preto.
5. **O neutro quente é escasso e estrutural.** `--quente` não é decoração: é a
   faixa de luminosidade que faltava. Uma ou duas seções por página, nunca
   coladas.
6. **Tema único: claro.** O alternador claro/escuro (`data-tema`, localStorage,
   botão no nav) sai. Nenhuma das referências que o cliente citou tem alternador,
   e ele dobra a matriz de verificação em 9 páginas sem ganho para este público.

### 1.5 O hover

O sistema antigo preenchia todo controle de dourado no hover — um gesto, uma cor,
qualquer superfície. Com o dourado fora do site isso precisou ser refeito, e a
medição mostrou que **nenhum preenchimento único serve nas quatro superfícies**:
navy morre no bloco escuro (1,24:1), `--azul-luz` morre no claro (1,97:1),
`--azul` reprova o próprio rótulo (3,55:1).

A saída é a mesma da regra 3 acima — **um gesto, dois tokens por superfície**:

- **Superfície clara:** botão de borda preenche `--navy` com rótulo branco;
  o `.botao--principal`, que já repousa em navy, **clareia** para `--azul-txt`.
- **Bloco escuro:** os dois preenchem `--azul-luz` com tinta `--navy`.

Tabela completa e medida em **`plano.md` §6**.

`--navy-hover #002647` **morreu na medição**: 1,24× de delta contra `--navy` é
imperceptível, e o botão primário parecia não reagir. Sai da paleta.

---

## 2. Tipografia — travada

**Família, escala, pesos, entrelinhas e tracking continuam herdados exatos do
UnidoCLP.** É o único ponto em que o site já é idêntico ao que o cliente elogiou
sem ressalva, e agora carrega mais peso do que antes: com o dourado saindo e o
herói virando tipo sobre campo claro, **o tipo é o ativo mais forte do sistema**.

Vale integralmente o §2 do `specs/design.md`: Outfit variável 300–500 servida
localmente, escala fluida de 9 degraus, e a regra que governa tudo —
**título grande = peso leve** (H1 e H2 em 300), nada acima de 500 em lugar nenhum.

**`--fs-display` é o único ponto em observação.** Ele foi posto em revisão
porque tipo sobre imagem tem exigência diferente de tipo sobre campo chapado, e o
herói virou vídeo (`plano.md` §3). Mas o painel espelhado é quase uniforme e
entrega 6,63:1 sob véu de 25% — **a escala herdada provavelmente aguenta**.

Regra: `clamp(2.75rem, 10.4vw, 12.5rem)` entra como está. **Conferir na tela e só
mexer se falhar.** Não é permissão para redesenhar a escala; é uma verificação.

---

## 3. Logo

### 3.1 O que aconteceu

`logo/logonova.png` é **pixel-idêntico** a `referencia/i3automations/logo-i3.png`
— mesmas dimensões, mesmo histograma. O cliente não mandou um logo novo; mandou
o logo dele **de volta**. O que o site publicou era um redesenho em SVG.

O que o redesenho tinha jogado fora:

| logo real | o SVG publicado |
|---|---|
| **notebook** — tampa mais base com entalhe do trackpad | monitor: retângulo e barra lisa |
| **cantos arredondados** na moldura, na tela e na base | cantos retos |
| tela **facetada em 5 tons** (`#FDC500 #F7CA3C #EAB306 #E0AC0B #FFDC6E`) | chapado `#FDC500` |
| "i3" em geométrica de terminais redondos, ponto circular | `<rect>` quadrado e um "3" de lados retos |
| wordmark em uma terceira face, humanista | — |

Ele reparou porque **era um logo diferente**.

### 3.2 A isenção, escrita

Repor a arte real faz do logo **o único objeto arredondado, com degradê e em
tipografia estrangeira do site inteiro**. Isso não é acidente, é isenção:

> **O logo é a única exceção à regra de cantos retos e à regra de família
> tipográfica única.** Nenhum outro elemento do site herda arredondamento,
> faceta ou tipo de fora do sistema por proximidade com ele.

Sem essa linha escrita, o site briga com a própria marca.

### 3.3 Como o nav usa

O lockup completo **não sobrevive em tamanho de navegação**. Medido:

| altura do lockup | largura | cada linha do wordmark |
|---|---|---|
| 32px | 116px | **8,8px** |
| 40px | 145px | **11,0px** |
| 48px | 174px | **13,2px** |

O wordmark tem duas linhas e ocupa ~55% da altura, dividido por dois. Entre 8,8 e
11px é borrão, e fica abaixo do piso de 12px.

**Portanto:** o nav usa a **marca isolada** (proporção 1,58:1, muito mais
eficiente em largura) mais o nome composto em Outfit — que é o que o `nav__nome`
já faz estruturalmente. O **lockup completo** vai para a intro, o rodapé e a
imagem OG, onde há altura.

### 3.4 O knockout — o método importa

Para fundo escuro, moldura, base e wordmark viram branco; **o "i3" continua
navy**, porque ele fica sobre o dourado e branco sobre `#FDC500` daria 1,6:1.

Bounding box **não funciona** — foi tentado e metade da moldura virou branca. O
método correto é **flood fill a partir da borda da imagem atravessando tudo que
não é dourado**: o anel dourado da tela é a única fronteira fechada do desenho,
então o que sobra inalcançável é exatamente o glifo. Medido: 4.988 px preservados,
46.433 px em knockout.

Antes de recolorir, **quantizar para as 7 cores exatas do arquivo** (nearest de
paleta). Isso elimina os pixels de anti-aliasing que produziam franja clara na
fronteira navy/dourado; o anti-aliasing volta correto no downsample com LANCZOS.

### 3.5 A intro

A intro atual encaixa **glifo por glifo** (`data-intro-destino`, `data-encaixe`).
Com a arte real isso vira animação do **logo inteiro** — translate, scale e clip.
Mais simples, mais barato, e sobrevive a qualquer refinamento futuro do vetor.

### 3.6 Vetorização

A arte é vetor chapado de 7 cores, então um trace fiel é **exato**, não
aproximado. Mas **não é bloqueante**: PNG em 1x/2x/3x é pixel-fiel por definição,
e o UnidoCLP já serve marca em PNG. O trace entra como polimento, depois.

---

## 4. Estrutura da home

1. **Nav** — marca isolada e nome em Outfit; transparente sobre o herói, sólido
   ao rolar. Régua do link em `--azul`.
2. **Herói — vídeo full-bleed.** `heroi.mp4` (3840×2160), **espelhado com
   `-vf hflip`** e véu navy de 25%. O espelhamento não é estético: sem ele o
   painel escuro fica à direita e o H1 à esquerda reprova a 1,34:1; espelhado,
   passa a 6,63:1. H1 em peso 300 branco entrando linha a linha, apoio curto com
   régua vertical. Sem CTA grande. **Sem objeto 3D.** Detalhe em `plano.md` §3.
3. **Números de credibilidade** — 279+ projetos, 158+ nos EUA, 78+ na Flórida,
   150.000+ tags historiados, desde 2000. Peso 300.
4. **Bloco de texto** → **Momento 1: o Filme**
5. **Bloco de texto** → **Momento 2: variação A**
6. **Bloco de texto** → **Momento 3: variação B**
7. **Plataformas** — Rockwell, Siemens, Schneider, Ignition, VTScada, Canary, PI System.
8. **Setores** — Oil & Gas, água e esgoto, automotivo, papel e celulose, solar.
9. **Governo** — UEI, CAGE, NAICS, certificações, Capability Statement.
10. **CTA final** → **rodapé**.

---

## 5. Os três momentos

A unidade que se repete:

```
[ bloco de texto ]            eyebrow → H2 → parágrafo → CTA    (estático, respira)
[ momento cinematográfico ]   rola, uma frase por cima
```

**O mecanismo muda a cada volta.** Repetir o filme três vezes transforma um
momento em padrão e um padrão em tique — e o que o cliente elogiou foi a calma.

> **REVOGADO EM 2026-08-26, por decisão do usuário.** Depois de ver a dobra
> "The line does not care how clever the code is" no ar, ele pediu o **mesmo
> mecanismo três vezes** — vídeo pequeno com um texto ao lado, vídeo em tela
> cheia com outro texto. A home passou a ter dois gestos (o filme, uma vez; a
> unidade, três) em vez de quatro. O que impede o tique é o assunto e o texto,
> que mudam a cada volta. O custo está registrado em `memorianew.md` §39, para
> que a decisão possa ser revista com o que se sabe agora.

### 5.1 Momento 1 — o Filme

Porte direto do `.filme` do UnidoCLP, verificado em produção:

```
.filme          height: 220vh    (180vh < 768px)   trilho que alimenta o progresso
.filme__palco   position: sticky · top: 0 · height: 100vh
.filme__janela  clip-path: inset(...) interpolado por --p de 0 a 1
.filme__texto   opacity e translateY por --t
```

A janela abre de faixa 2,9:1 até full-bleed conforme rola. Frase **estática** por
cima. Scrim obrigatório de dois gradientes — sem ele, branco sobre vídeo claro cai
muito abaixo de 4,5:1 em vários quadros.

**Assunto: a estação de água.** É o melhor material do acervo e bate com um
vertical real da empresa.

**A frase:** *"Senior control experts know things they do not teach in school."*
Já aprovada no tom de voz, e é a irmã da manchete do herói. **Não** pode ser
tradução de "Construa seu futuro hoje".

### 5.2 Momento 2 — variação A: janela fixa, texto ao lado

O vídeo fica numa janela menor e **não abre**. Quem se move é a coluna de texto
ao lado, com reveal linha a linha. Assunto: **a esteira de produção**.

### 5.3 Momento 3 — variação B: parallax de camadas, sem vídeo

Fotografia autoral em parallax lento com o desenho técnico sobreposto, revelado
camada a camada. **Sem vídeo** — é o que impede a home de virar três telas de
vídeo seguidas.

### 5.4 Orçamento de vídeo

`ffmpeg 7.1` está disponível via `imageio_ffmpeg` (ver `memorianew.md`), com
libx264, libx265, libvpx-vp9 e libaom-av1. Medido: 8s de 1080p, sem áudio,
CRF 26, preset slow = **2.504.432 bytes**, encodado em 5,0s. Ou seja
**~313 KB/s a 1080p**.

- um loop de 10s ≈ **3 MB** em h264
- três momentos ≈ **9 MB** mais as alternativas AV1/VP9
- limite do Cloudflare Pages é 25 MB por arquivo — folgado
- **441 MB de 4K viram ~10 MB publicados**

**Faixa de áudio removida sempre.** Três dos arquivos carregam AAC a 253 kb/s,
que é desperdício e faz autoplay apanhar de política de navegador.

**Um vídeo decodificando por vez:** `preload="none"` mais IntersectionObserver
dando play e pause, poster obrigatório em todos.

### 5.5 O buraco do acervo

Dos 8 vídeos: **1 estação de água, 1 esteira de produção, 6 placa solar.** Se os
três momentos saírem só desse poço, o site lê como empresa de energia solar —
que é **um** de cinco verticais, e Oil & Gas, provavelmente o maior deles, tem
zero material.

**E o herói também virou solar**, o que agrava. A correção é a sequência de
assunto — solar → água → produção → controle — especificada em `plano.md` §5.5.
O enquadramento do momento 2 é o que a carrega: cortado fechado na máquina, lê
como linha de produção; aberto na célula, vira mais solar.

Vale pedir ao cliente, nem que sejam 10 segundos de cada: **interior de
painel/MCC, operador na tela de SCADA, e qualquer coisa de oil & gas.**

---

## 6. Movimento

### 6.1 O que fica

**A inércia da roda fica** (`LERP = 0.11` em `main.js §11`: 90% da distância em
~330ms, suavização por tempo e não por quadro). Continuam valendo as três coisas
que ela deliberadamente não faz: não toca em trackpad (`|deltaY| < 50px` passa
direto), não toca em teclado nem em barra de rolagem, e **não roda com
`prefers-reduced-motion`**.

**O rodapé revelado fica.** É layout puro — `position: sticky` mais `z-index`,
nenhum JS no caminho da rolagem. Guarda de tamanho em `min-width: 900px and
min-height: 780px`, e a aresta de 1px em `rgba(255,255,255,.55)` que torna a
subida legível.

> **Custo assumido, registrado:** a inércia disputa a roda com o `clip-path` dos
> três momentos e com o parallax. O que torna isso viável é que **a página rola
> de verdade** (`window.scrollTo` por quadro, nunca `transform` num wrapper) —
> então `position: sticky` continua vivo e o progresso dos momentos é lido da
> posição real de rolagem. Se em teste real ficar pesado, **a inércia é a
> primeira coisa a cair**, não os momentos.

### 6.2 Reveals e parallax

Só `transform` e `opacity`. Progresso lido da rolagem real. Onde houver suporte,
**`animation-timeline: view()`** — animação por rolagem nativa roda fora da main
thread, e isso importa porque a página já carrega inércia e WebGL. JS como
fallback.

Desligamento em `prefers-reduced-motion` em tudo, sem meia-medida.

### 6.3 Lottie: não

Lottie significa `lottie-web` (~250 KB gzip) mais os JSON, e é dependência de
runtime que quebra a regra de sem framework e sem build step.

Tudo que Lottie faria aqui — traço que se desenha sozinho, ícone que anima no
reveal — sai de **SVG inline com `stroke-dasharray` e `stroke-dashoffset`**, que
o site **já faz** na régua do herói. Zero KB, sem dependência, e herda os tokens
de cor automaticamente, coisa que um JSON de Lottie não faz.

---

## 7. Fotografia

O acervo do repositório é maior do que parecia: **33 fotos de galeria** (painel,
SCADA, sala de controle, comissionamento, fiação, bornes, solar, água,
clarificador, refinaria, automotivo, prensas, AGV), mais 6 de setor, 6 de
cabeçalho de página e 4 do componente duplo. Dá para vestir as 9 páginas sem
pedir nada novo.

### 7.1 A regra de legenda

**Legenda descritiva do assunto, nunca afirmação de autoria.**

- **Certo:** "Control panel wiring and terminal blocks", "Aerial view of a water
  treatment clarifier".
- **Errado:** "Painel entregue pela i3 em Houston, 2021" — a menos que seja
  verificável.

O acervo mistura material autoral com banco de imagem, e **o cliente é fornecedor
federal**. Uma legenda que afirma obra que não é dele é exatamente a classe de
afirmação que este projeto já removeu uma vez da galeria. O `alt` descreve o que
a imagem mostra; nada mais.

### 7.2 Tratamento

Full-bleed dentro do bloco, véu navy quando houver texto por cima. Nunca moldura
decorativa, nunca sombra de caixa. O componente `.dupla` — duas seções conectadas
dividindo UMA fotografia — continua válido.

---

## 8. As peças desenhadas

| Peça | Onde | Situação |
|---|---|---|
| `mimico.js` — a tela de SCADA | past-performance | **Fica.** É literalmente o artefato que a empresa entrega. |
| `malha.js` — a malha de controle | services | **Fica.** É a tese da empresa virando experimento. |
| `carta.js` — a chapa de navegação | contact | **Fica.** Litoral real do TIGER/US Census, não desenhado de memória. |
| `braco.js` — o robô de 6 eixos | ~~herói~~ → **404** | **Vira easter egg.** Sai do herói, ganha a página de erro. |
| `clp.js` — o CLP explodido | capabilities | **Sai.** Guardado para reaproveitar depois. |
| `planta.js` — a planta isométrica | home | **Sai.** A home vira foto e três momentos. |
| `marca.js` — a marca extrudada | who-we-are | **Sai.** Ela extruda o RE-DESENHO da marca — manter reintroduziria exatamente o erro que o cliente reclamou. |

`gl.js` e `tela.js` continuam como núcleo comum das peças que ficam. Nada do que
sai é apagado do repositório — sai da página, fica no `fonte/js/`.

---

## 9. O que não muda

- **Stack: HTML, CSS e JS puro.** Sem framework, sem build step no deploy.
- **`fonte/` edita, `site/` publica.** Tudo em `site/` é gerado.
- **Cantos retos em tudo** — com a isenção do logo escrita em §3.2.
- **Sem sombra em botão.** Elevação vem de fundo e borda.
- **Fonte servida localmente**, nunca por CDN.
- **Idioma do site EN-US**, documentação interna em PT-BR.
- **Medir, não estimar.** Todo número no CSS tem uma conta atrás, e a conta vai
  para `memorianew.md`.
- **Todo o conteúdo do site atual sobrevive à migração** — serviços, capacidades,
  plataformas, certificações, UEI/CAGE/NAICS, números, contatos, páginas legais.

---

## 10. O que morreu do `specs/design.md`

| morreu | por quê |
|---|---|
| §1.4 "sem gradiente creme, o cliente é industrial pesado" | **É a causa raiz do feedback.** Era a decisão que tirava a luz do site. |
| §1 dourado como accent do site | Dourado agora existe só dentro do logo. |
| §1.2 `--dourado-txt #6B5000` | Não há mais texto em accent dourado. |
| §6.3 "no hover, todo botão preenche em `--dourado`" | O hover passa a ser navy/azul, a definir na implementação. |
| §1.2 `--navy-fundo #001D3D`, `--navy-tinta #000814` | Substituídos por `--azul-bloco #0D4477`. |
| Alternador de tema claro/escuro | Tema único. |
| §5 item 2, herói navy sólido com peça 3D | Herói é fotografia tratada. |
| §1.1 "as facetas do gradiente não entram no site" | Elas **são** o logo. Entram, dentro dele. |
| "cantos retos em tudo", sem exceção | Ganhou a isenção explícita do logo. |

**O que sobreviveu inteiro:** a tipografia (§2), a gramática de espaçamento e o
grid de 12 (§3), o tom de voz (§4), o CTA de chip com seta (§6.2), e a disciplina
de medir em vez de estimar.
