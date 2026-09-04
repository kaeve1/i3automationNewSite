# plano — especificação de construção

Fecha o trio: **`design.md`** diz *como o sistema se comporta*, **`doit.md`** diz
*em que ordem executar*, este diz **o que vai em cada página**. O registro de
medições e decisões está em `memorianew.md`.

Escopo: **as 9 páginas**, redesenho completo. Data de fechamento: 2026-08-25.

---

## 1. "Clean" — a definição operacional

O pedido foi *"precisamos deixar o site clean"*. Adjetivo não se verifica, então
vira regra com número. **Toda seção precisa passar nestas dez.** Se uma falhar, a
seção está errada, não a régua.

| # | Regra | Verificação |
|---|---|---|
| 1 | **Uma ideia por dobra.** Se a seção precisa de "e também", ela é duas seções. | Conte as afirmações. >1 = quebrar. |
| 2 | **Um CTA por seção**, no máximo. Zero é permitido e frequente. | Conte `.cta` e `.botao`. |
| 3 | **No máximo 3 superfícies visíveis ao mesmo tempo.** Branco, quente e uma escura — nunca as quatro. | Screenshot da dobra, conte fundos. |
| 4 | **Um movimento por dobra.** O reveal do texto **ou** o parallax da imagem, nunca os dois na mesma tela. | Conte animações disparando. |
| 5 | **Separação por espaço, nunca por linha.** Filete só onde carrega informação (a aresta do rodapé revelado, `design.md` §6.1). | `grep border` no CSS de seção. |
| 6 | **No máximo 2 pesos tipográficos por tela.** 300 para título, 400 para corpo. O 500 é só UI (nav, botão, eyebrow). | Inspecionar. |
| 7 | **Uma imagem por seção.** Grade de miniaturas só existe em `gallery.html`. | Conte `<img>` fora da galeria. |
| 8 | **`--sec-y` intocável.** 160px no desktop. Comprimir respiro para caber mais conteúdo é a definição de não-clean. | Medir. |
| 9 | **Nada pisca, nada pula, nada aparece sozinho** fora do reveal de entrada. Sem carrossel automático, sem contador animado, sem tooltip que abre no hover. | Ver a página parada por 30s. |
| 10 | **Se um elemento precisa de legenda explicando como usá-lo, ele sai.** | A linha `"Drag the arm to orbit"` do herói publicado é o exemplo do que não fazer. |

> **A regra que engloba as dez:** o site que o cliente chamou de perfeito é calmo.
> Cada coisa que a gente acrescentar tem que ser paga tirando outra.

---

## 2. Decisões desta rodada — referência rápida

| | Decisão |
|---|---|
| Herói | **Vídeo full-bleed**, `heroi.mp4` 4K, espelhado (`hflip`), véu 25% |
| Accent | **Azul médio `#4D8ECB`**, derivado do navy da marca (H209 · S55 · L55) |
| Dourado | **Só dentro do logo.** Zero ocorrências no CSS de página |
| Escuro | **Alternância suavizada** — `--azul-bloco #0D4477` substitui `#001D3D`/`#000814` |
| Tema | **Único, claro.** O alternador sai |
| Tipografia | **Travada.** `--fs-display` reaberto pelo herói em vídeo — conferir na tela (§3.5) |
| Logo | **Arte real** (`logo/logonova.png`), marca isolada no nav, lockup na intro/rodapé/OG |
| Momentos | **Um filme + duas variações**, mecanismo diferente em cada |
| Lottie | **Fora.** SVG com `stroke-dashoffset` no lugar |
| Movimento | Inércia da roda **e** rodapé revelado, os dois ficam |
| Peças | Ficam `mimico.js`, `malha.js`, `carta.js`. `braco.js` → 404. Saem `clp.js`, `planta.js`, `marca.js` |
| Legendas | **Descritivas do assunto, nunca afirmação de autoria** |

---

## 3. O herói

### 3.1 A escolha: vídeo

**`Videos/heroi/heroi.mp4`** — painel solar em contra-plongée com o céu refletido
na superfície, nuvens correndo. **3840×2160 · 34,1s · 29,97fps · 18,7 Mbps.**

Por que ele:

- **Resolução resolvida.** 4K, contra os 1280×720 da foto que estava escolhida.
  A restrição que obrigava ao herói contido deixou de existir.
- **A paleta já é a do sistema.** Céu azul frio, painel azul-quase-preto, nuvem
  branca. É `--azul` e `--navy` filmados.
- **Movimento conquistado.** Nuvem refletida, sem corte, sem câmera nervosa.
  É o movimento lento e ambiente que um herói institucional aguenta.
- **Tem zona escura de verdade** para o tipo — medida abaixo.

### 3.2 A medição que mudou o enquadramento

Luminância das zonas candidatas ao H1, **pior caso ao longo dos 34 segundos**,
contra branco puro:

| zona | branco por cima | |
|---|---:|---|
| esquerda-inferior (lugar clássico do H1) | **1,34:1** | reprova |
| esquerda-meio | **1,10:1** | reprova |
| faixa inferior inteira | 2,94:1 | reprova |
| direita-inferior | 5,99:1 | OK |

**O céu fica à esquerda e o painel escuro à direita** na maior parte do clipe — e
a gramática do site põe eyebrow e título à esquerda (o split 4/8). O tipo morreria
exatamente onde precisa estar. Salvar na posição original exigiria **62% de véu**
para chegar a 4,80:1, o que enlameia justamente o que torna o vídeo bom.

### 3.3 A correção: `-vf hflip`

Espelhar horizontalmente joga o painel escuro para a esquerda. Medido no clipe
inteiro, espelhado:

| véu navy | branco por cima | |
|---:|---:|---|
| **0%** | **5,28:1** | OK |
| **25%** | **6,63:1** | **OK — o alvo** |
| 45% | 7,95:1 | OK |

**Passa AA sem véu nenhum.** Espelhar é inócuo aqui: não há texto, rosto nem
marca no quadro, só painel e céu.

### 3.4 Especificação

- **Full-bleed**, altura de herói. O vídeo é o fundo, o tipo vive por cima.
- **`-vf hflip` obrigatório no encode.** Sem ele o herói reprova contraste.
- **Véu navy a 25%** — 6,63:1, e o vídeo aparece quase limpo.
- **H1 em peso 300**, branco, entrando linha a linha:
  *"Good control strategy / beats more expensive / instrumentation."*
- Apoio curto com **régua vertical que se desenha** (`stroke-dashoffset`).
- **Sem CTA grande. Sem objeto 3D. Sem legenda de instrução.**
- Mudo, em loop, `preload="none"` não se aplica aqui — **o herói é a única mídia
  autorizada a carregar adiantado**. Poster obrigatório, com `fetchpriority="high"`.
- `alt` / `aria-label`: *"Solar panel surface reflecting moving clouds."*
  **Nunca afirma autoria.**

> **Custo de bitrate, e é contraintuitivo:** véu leve **esconde menos artefato**.
> O CRF 30 orçado para os momentos vale porque lá o véu é de 62%. Com 0–25% de
> véu o herói precisa de CRF mais baixo. **Medir no encode real**, não herdar o
> número dos momentos.

### 3.5 O que isso reabriu

O herói contido (tipo em 7 col, foto em 5) existia **porque a foto era 1280px**.
Com 4K, a restrição sumiu e a decisão voltou para full-bleed.

**`--fs-display` reabre junto.** Ele tinha fechado porque o tipo ficaria sobre
campo chapado. Voltou a ficar sobre imagem — mas sobre um painel quase uniforme
a 6,63:1, então a escala herdada provavelmente aguenta. **Conferir na tela antes
de mexer**, e só mexer se falhar.

> **Guardado:** `fotosproduto/gas.jpg`, em **7900×5266** — tanque, tocha,
> refinaria. Único material de alta resolução de Oil & Gas. Destino no §8.2.

---

## 4. A home, dobra a dobra

| # | Dobra | Superfície | Conteúdo | Movimento |
|---|---|---|---|---|
| 1 | **Herói** | vídeo full-bleed + véu 25% | H1 300 branco por cima | loop lento + entrada linha a linha |
| 2 | **Números** | branco | 279+ projetos · 158+ EUA · 78+ FL · 150.000+ tags · desde 2000 | reveal |
| 3 | **Texto** | branco | eyebrow → H2 → parágrafo → CTA | reveal |
| 4 | **Momento 1 — o Filme** | vídeo | frase estática por cima | janela abre (§5.1) |
| 5 | **Texto** | quente | eyebrow → H2 → parágrafo → CTA | reveal |
| 6 | **Momento 2 — variação A** | vídeo | texto correndo ao lado | janela fixa (§5.2) |
| 7 | **Texto** | branco | eyebrow → H2 → parágrafo → CTA | reveal |
| 8 | **Momento 3 — variação B** | foto | traço se desenhando sobre a foto | parallax (§5.3) |
| 9 | **Plataformas** | off-white | Rockwell, Siemens, Schneider · Ignition, VTScada, Canary, PI System | reveal |
| 10 | **Setores** | branco | Oil & Gas · água · automotivo · papel · solar | reveal |
| 11 | **Governo** | `--azul-bloco` | UEI `XUZ4WKEZLS67` · CAGE `9ZJM6` · NAICS `541511` · certificações · Capability Statement | reveal |
| 12 | **CTA final** | `--azul-bloco` | headline curta + contato | reveal |
| 13 | **Rodapé** | `--sup-3-fundo` | 4 colunas, 2 telefones, e-mail, redes, legal | **revelado por sticky** |

**Regra 3 de clean conferida:** as superfícies visíveis simultaneamente nunca
passam de três, porque as dobras 11 e 12 são o mesmo bloco escuro contínuo.

---

## 5. Os três momentos, especificados

### 5.1 Momento 1 — o Filme

Porte direto do `.filme` do UnidoCLP, verificado em produção.

```
.filme          height: 220vh   (180vh < 768px)
.filme__palco   position: sticky · top: 0 · height: 100vh
.filme__janela  clip-path: inset(...) interpolado por --p (0 → 1)
.filme__texto   opacity e translateY por --t
```

- **Assunto:** a estação de tratamento de água (`estacaoagua.mp4`, 4K).
- **Frase, estática:** *"Senior control experts know things they do not teach in school."*
- **Scrim obrigatório** de dois gradientes — sem ele, branco sobre vídeo claro
  cai muito abaixo de 4,5:1 em vários quadros.
- Sem áudio. `preload="none"`. Poster obrigatório.

### 5.2 Momento 2 — variação A

O vídeo fica em janela menor e **não abre**. Quem se move é a coluna de texto ao
lado, com reveal linha a linha.

- **Assunto:** `elemnetotecnologicodeesteira.mp4` — **enquadrado nos bicos e atuadores, não na célula solar**. Assim lê como linha de produção automatizada em vez de mais um plano de solar (ver §5.5).
- Mesmo orçamento e mesmas regras de mídia do 5.1.

### 5.3 Momento 3 — variação B

**Sem vídeo.** É o que impede a home de virar três telas de vídeo seguidas.

Fotografia em parallax lento com o **traço técnico sobreposto se desenhando**
(`stroke-dasharray` / `stroke-dashoffset`). O projeto já tem esse vocabulário
construído: `site/img/setores/*-traco-*.png` são o traçado de aresta da própria
fotografia, em branco sobre transparente.

**Assunto decidido:** a macro do módulo de relés (`pexels-maltelu-5276099.jpg`,
5184×3456). Ela é toda aresta dura com fios em curva — traça excepcionalmente
bem — e é o único momento da home que fala de **controle**, que é o que a empresa
vende. Nota: o objeto é um módulo de 4 relés, não um CLP; a legenda descreve
"relay module and field wiring", nunca "PLC".

### 5.4 Orçamento de mídia — medido

| encode | tamanho |
|---|---|
| 1080p, CRF 26, 8s | 2.504.432 B (2,4 MB) |
| 1600px, CRF 26, 7s | 1.713.887 B (1,6 MB) |
| 1600px, CRF 30, 7s | **924.108 B (0,9 MB)** |
| 1600px, CRF 34, 7s | 525.440 B (0,5 MB) |

**O véu navy permite comprimir mais que o normal** — ele esconde artefato de
bloco. CRF 30 a 1600px é o alvo: **~900 KB por momento**.

**O herói é a exceção.** Lá o véu é de 25%, então esconde muito menos — CRF 30
vai aparecer. O herói precisa de CRF mais baixo e vai custar mais por segundo
que os momentos. **Medir no encode real, não herdar este número.**

Binário: `imageio_ffmpeg.get_ffmpeg_exe()` → ffmpeg 7.1 com x264/x265/vp9/aom.
Teto do Cloudflare Pages: 25 MB por arquivo.

**Regras duras de mídia:**
- Faixa de áudio **removida sempre** (3 dos 8 arquivos carregam AAC a 253 kb/s).
- **Um vídeo decodificando por vez** — IntersectionObserver dá play e pause.
- `prefers-reduced-motion` desliga os três momentos inteiros: janela nasce
  aberta, vídeo não toca, texto entra sem transformação.

### 5.5 O equilíbrio de assunto — a correção que o herói exige

O acervo é solar-pesado: **6 dos 8 vídeos** são placa solar, e o herói agora
também é. Solar é **um de cinco verticais**, e o menor deles. Sem correção, o
site inteiro diz "empresa de energia solar".

**A sequência que corrige, sem abrir mão do vídeo do herói:**

| | assunto | lê como |
|---|---|---|
| Herói | painel solar e nuvem refletida | solar |
| Momento 1 — filme | estação de tratamento de água | infraestrutura de processo |
| Momento 2 — variação A | a esteira, **enquadrada nos bicos e atuadores** | linha de produção automatizada |
| Momento 3 — variação B | macro do módulo de relés, com traço | **controle** |

Solar → água → produção → controle. Cobre a empresa em vez de repetir um vertical.

> **O enquadramento do momento 2 é o que carrega essa correção.** Se a câmera
> abrir na célula solar, volta a ser solar e a sequência perde o efeito. Cortar
> fechado na máquina.

`gas.jpg` (7900×5266) merece posição de destaque numa interna — é o único
material de Oil & Gas que existe no projeto.

Vale pedir ao cliente, nem que sejam 10 segundos de cada: **interior de
painel/MCC, operador na tela de SCADA, e qualquer coisa de oil & gas.**

---

## 6. O hover — um gesto, dois tokens

O sistema antigo preenchia tudo de dourado no hover (7,74:1 em qualquer
superfície). Com o dourado fora do site, o gesto precisava ser refeito.

**Medido: nenhum preenchimento único serve nas quatro superfícies.**

| preenchimento | rótulo | branco | quente | off-white | bloco |
|---|---:|---:|---:|---:|---:|
| `--navy #003566` | 12,34 | 12,34 | 11,16 | 11,28 | **1,24** |
| `--azul-txt #2C6396` | 6,30 | 6,30 | 5,70 | 5,76 | **1,58** |
| `--azul #4D8ECB` | **3,55** | 3,47 | 3,14 | 3,17 | **2,87** |
| `--azul-luz #88B4DD` | 5,65 | **2,18** | **1,97** | **2,00** | 4,56 |

Navy morre no bloco escuro; `--azul-luz` morre no claro; `--azul` reprova o
próprio rótulo. **É a mesma estrutura do accent** (`design.md` §1.4 regra 3):
claro e escuro pedem tokens diferentes.

### 6.1 A especificação

**Um gesto — o hover preenche, e o preenchimento anda para o azul.**

| superfície | controle | repouso | hover | medição |
|---|---|---|---|---|
| clara | `.botao` | transparente, borda `--borda-ui` | preenche **`--navy`**, rótulo branco | fundo 11,16–12,34:1 · rótulo 12,34:1 |
| clara | `.botao--principal` | `--navy`, branco | clareia para **`--azul-txt #2C6396`**, branco | delta **1,96×** · rótulo 6,30:1 |
| bloco escuro | ambos | borda `--borda-ui-esc` | preenche **`--azul-luz #88B4DD`**, rótulo `--navy` | fundo 4,56:1 · rótulo 5,65:1 |
| clara | `.cta__chip` | `--azul-chip` | preenche **`--azul #4D8ECB`**, seta `--navy` | 3,55:1 — **seta é ícone**, piso 3:1 |
| escura | `.cta__chip` | `rgba(255,255,255,.12)` | preenche **`--azul-luz`**, seta `--navy` | 5,65:1 |

O chip também desliza `translateX(3px)`, como já fazia.

### 6.2 O token que morreu na medição

`--navy-hover #002647` dá **delta de 1,24×** contra `--navy`. É imperceptível —
o botão primário parecia não reagir. Ele sai da paleta; quem ocupa esse papel é
`--azul-txt`, a 1,96×.

---

## 7. As 8 páginas internas

| Página | Peça | Cabeçalho | Notas |
|---|---|---|---|
| `who-we-are.html` | **remover `data-marca`** | foto + véu | `marca.js` sai: ela extruda o RE-DESENHO da marca |
| `capabilities.html` | **remover `data-clp`** | foto + véu | A macro do relé mora aqui — é onde ela é ótima |
| `past-performance.html` | **mantém `data-mimico`** | foto + véu | A tela de SCADA é o artefato que a empresa entrega |
| `services.html` | **mantém `data-malha`** | foto + véu | A tese da empresa virando experimento |
| `gallery.html` | mantém `data-mosaico` | foto + véu | **Única página com grade de imagens** (exceção à regra 7) |
| `contact.html` | **mantém `data-carta`** | foto + véu | Litoral real do TIGER/US Census |
| `404.html` | **recebe `braco.js`** | — | Easter egg. Sem nav pesado, sem seção |
| `privacy-policy.html` · `terms-and-conditions.html` | — | — | Só tokens novos |

Todas herdam: logo real, paleta nova, tema único, tipografia travada, e as dez
regras de clean.

---

## 8. Fotografia — inventário e atribuição

### 8.1 O que existe

| origem | quantidade | resolução |
|---|---|---|
| `site/img/galeria/` | 33 assuntos | 400–800px |
| `site/img/setores/` | 6 + 6 traços | 336–900px |
| `site/img/dupla/` | 4 | **2560px** |
| `site/img/cabecalho/` | 6 | — |
| `melhorias/gallery/` | 9 autorais | **600×600** |
| `referencia/…/fotosproduto/` | 24 | até **9504×6336** |

**Só as de `dupla/` e as de `fotosproduto/` têm resolução de cabeçalho.** As
autorais de `melhorias/gallery` são quadradas e pequenas — servem para grade, não
para faixa.

### 8.2 Candidatas de alta resolução ainda não usadas

| arquivo | tamanho | assunto | destino sugerido |
|---|---|---|---|
| `gas.jpg` | 7900×5266 | tanque, tocha, refinaria | **Oil & Gas** — preenche o vertical vazio |
| `pexels-valentin-ilas` | 9504×6336 | britagem, esteira, silo | Setores / past-performance |
| `pexels-shvetsa` | 6240×4160 | mão em tela HMI colorida | **Services** ou o bloco de SCADA |
| `pexels-peter-xie` | 5715×3810 | manipulador verde em armazém | Automotivo / logística |
| `pexels-maltelu` | 5184×3456 | macro do módulo de relés | **Capabilities** + traço do momento 3 |
| `pexels-pixabay-159298` | 5655×3775 | engrenagens em preto e branco | Papel e celulose |
| `pexels-mazhar-ulazhar` | 3195×1799 | fileira de prensas, perspectiva | **Automotivo** |

### 8.3 A regra de legenda — não negociável

**Descritiva do assunto, nunca afirmação de autoria.**

- **Certo:** *"Control panel wiring and terminal blocks"* · *"Aerial view of a water treatment clarifier"*
- **Errado:** *"Painel entregue pela i3 em Houston, 2021"* — a menos que verificável.

O acervo mistura autoral com banco de imagem, e **o cliente é fornecedor federal**.
Legenda que afirma obra não verificável é risco real, não preciosismo. O `alt`
descreve o que a imagem mostra; nada além disso.

---

## 9. Redlines — o que é proibido

1. **`#FDC500` em qualquer lugar que não seja dentro do logo.** Zero ocorrências
   no CSS de página. Vale para régua, barra, ícone, número, hover e foco.
2. **`border-radius` em qualquer elemento que não seja o logo.** A isenção é do
   logo e só dele (`design.md` §3.2).
3. **Peso tipográfico acima de 500.** O arquivo variável não carrega — pedir
   força falso-negrito.
4. **Sombra em botão.** Elevação vem de fundo e borda.
5. **Framework, biblioteca de animação ou build step no deploy.** Publicar a
   pasta `site/` é o deploy inteiro.
6. **Editar `site/css`, `site/js` ou o HTML de `site/` à mão.** Tudo ali é
   gerado; o próximo build sobrescreve.
7. **Fonte por CDN.** Sempre local.
8. **Carrossel automático, contador animado, número que sobe sozinho.**
9. **Caixa alta em bloco.** Só em rótulos de até 3 palavras.
10. **Jargão de marketing** — *synergy, cutting-edge, world-class, passionate*.
    Se a frase serviria para uma agência de publicidade, não serve aqui.
11. **Legenda que afirma autoria não verificável** (§8.3).
12. **Número no CSS sem a conta que o produziu** registrada em `memorianew.md`.

---

## 10. Abertos

| # | Aberto | Bloqueia |
|---|---|---|
| 1 | ~~Resolução do herói~~ | **fechado** — vídeo 4K full-bleed, `hflip`, véu 25% (§3) |
| 2 | ~~Assunto do momento 3~~ | **fechado** — macro do módulo de relés com traço (§5.3) |
| 3 | ~~Onde moram os assets de marca~~ | **fechado** — `referencia/marca/`, 13 arquivos |
| 4 | ~~O hover dos botões~~ | **fechado** — §6 deste documento |
| 5 | **`--fs-display` sobre o vídeo** — conferir na tela; só mexer se falhar | Fase 5, não bloqueia |
| 6 | **Material extra de vídeo** — painel/MCC, operador em HMI, oil & gas. Não bloqueia | — |

---

## 11. O risco que sobra

A home vai carregar ao mesmo tempo: inércia sequestrando o `wheel`, três momentos
lendo progresso de rolagem, parallax e rodapé sticky. **Nada disso foi medido
junto**, e é a única coisa que nenhuma medição fora do navegador responde.

Saída já decidida em `design.md` §6.1: se ficar pesado, **a inércia cai primeiro**,
não os momentos. Ela é a única peça que sequestra a roda e a que menos o cliente
pediu — e a regra 4 de clean (§1) já limita movimento a um por dobra, o que
ajuda a manter o orçamento de quadro.
