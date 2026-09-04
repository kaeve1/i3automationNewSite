# memorianew — estado, decisões e medições

Arquivo de recuperação de contexto da revisão iniciada em **2026-08-25**.
Substitui `memoria.md` como registro corrente; o antigo continua válido para
tudo anterior a esta data, **com uma correção de fato registrada em §6**.

---

## 1. O que provocou a revisão

Feedback do cliente sobre o site publicado em `https://i3automations.pages.dev/`,
recebido junto com elogio sem ressalva ao `https://universodoclp.pages.dev/`
("está perfeito, nada realmente para mudar"):

1. Não gostou das cores — **"esse amarelo não me pegou mesmo"**.
2. O braço robótico do herói é bonito mas **fora de assunto**: "não vendo robôs".
   Sugeriu CLP, peça de arduino, placa solar.
3. Quer algo parecido com a seção de vídeo do UnidoCLP ("Construa seu futuro hoje").
4. **"O mais parecido que você conseguir chegar do nível do universo do clp
   melhor — eu digo a tonalidade de cor e decoração."**

E a moldura comercial: *"não vamos fazer negócio se não me der o que eu quero."*

---

## 2. O diagnóstico

O `#FDC500` **é a cor do logo do próprio cliente**, medida em pixel. Ele não
odiava a marca dele; odiava o uso.

O que faltava no i3 e existia no UnidoCLP: **a faixa média de luminosidade e
qualquer coisa quente**. O i3 saltava de `#D7E3F0` direto para `#003566`, e o
dourado entrava como a única coisa quente num campo escuro e saturado.

**Navy com amarelo saturado é a paleta de sinalização** — cone, cavalete, fita de
perigo. Lia como alerta.

`specs/design.md` §1.4 tinha decidido explicitamente *"sem gradiente creme, o
cliente é industrial pesado"*. **Essa linha é a causa raiz do feedback.** Quando o
cliente pediu "a tonalidade do universo do clp", estava pedindo **luz**, não o
laranja.

---

## 3. Medições — logo

### 3.1 `logonova.png` não é um logo novo

| arquivo | dimensões | `#003566` | `#FDC500` | `#F7CA3C` |
|---|---|---|---|---|
| `logo/logonova.png` | 1024×387 | 44.534 px | 23.370 px | 17.099 px |
| `referencia/i3automations/logo-i3.png` | 1024×387 | 44.534 px | 23.370 px | 17.099 px |

**Histograma idêntico.** O md5 difere só por metadado. O cliente mandou o logo
dele **de volta** — a reclamação "mudei a logo" era sobre o redesenho em SVG que
o site publicava.

Diferenças do redesenho para a arte real: notebook virou monitor; cantos
arredondados viraram retos; tela facetada em 5 tons virou chapada; o "i3" em
geométrica de terminais redondos virou `<rect>` mais um "3" de lados retos; o
wordmark (uma terceira face tipográfica) sumiu.

### 3.2 O knockout — um beco sem saída registrado

**Bounding box não funciona.** Primeira tentativa: preservar o navy dentro da
caixa da tela dourada. Resultado — a caixa englobava parte da moldura, então
metade dela virou branca e a outra metade ficou navy. Visível na prancha de
conferência.

**O método correto é flood fill a partir da borda da imagem atravessando tudo
que não é dourado.** O anel dourado da tela é a única fronteira fechada do
desenho; o que sobra inalcançável é exatamente o glifo "i3".

Medido: **4.988 px preservados** (o i3, que fica navy porque branco sobre
`#FDC500` daria 1,6:1) e **46.433 px em knockout** (moldura, base, wordmark).

**Quantizar antes de recolorir.** Snap para as 7 cores exatas do arquivo mata os
pixels de anti-aliasing que produziam franja clara na fronteira navy/dourado. O
anti-aliasing volta correto no downsample com LANCZOS.

### 3.3 O lockup não sobrevive no nav

| altura | largura | cada linha do wordmark |
|---|---|---|
| 32px | 116px | **8,8px** |
| 40px | 145px | **11,0px** |
| 48px | 174px | **13,2px** |

Wordmark de duas linhas ocupando ~55% da altura, dividido por dois. Abaixo do
piso de 12px e visualmente borrão. **Nav usa a marca isolada** (1,58:1) mais o
nome em Outfit; o lockup completo vai para intro, rodapé e OG.

### 3.4 Assets gerados

12 PNGs em `…/scratchpad/marca/`: `logo-completo` e `logo-marca`, versão navy e
knockout, em 96/192/288px. **Ainda não movidos para o repositório.**

---

## 4. Medições — paleta

### 4.1 Por que não existe um dourado que sirva

| cor | /branco | /off-white | /navy | /navy-fundo |
|---|---:|---:|---:|---:|
| `#FDC500` publicado | **1,60** | **1,46** | 7,74 | 10,59 |
| `#F7CA3C` faceta do logo | 1,56 | 1,42 | 7,92 | 10,83 |
| `#D89B2C` latão | 2,43 | 2,22 | 5,08 | 6,95 |
| `#F2891F` laranja do UnidoCLP | 2,51 | 2,29 | 4,92 | 6,74 |
| `#B45309` | 5,02 | 4,59 | **2,46** | **3,36** |
| `#A16207` | 4,92 | 4,50 | **2,51** | **3,43** |
| `#6B5000` `--dourado-txt` | 7,57 | 6,92 | **1,63** | **2,23** |

**Nenhum dourado funciona nos dois lados.** O `#FDC500` brilha no navy e some no
branco; os âmbares de croma baixo fazem o inverso e reprovam até o piso de 3:1
sobre navy.

`#A16207` e `#B45309` vieram da busca de cor da skill `ui-ux-pro-max` para
perfis institucionais (Research Lab, Legal Services). Eles funcionam **naqueles
produtos** porque são sites claro-dominantes — `background: #F8FAFC`, navy só em
botão e cabeçalho, sem campo escuro full-bleed. **A skill não sugeria outra cor;
sugeria outra estrutura.**

### 4.2 A família azul nova — derivada, não escolhida

`#003566` em HSL é **H209 · S100 · L20**. Toda a família nova mantém o matiz 209.

| Token | Cor | HSL | Contraste |
|---|---|---|---|
| `--azul` | `#4D8ECB` | H209 S55 L55 | 3,47:1 sobre branco |
| `--azul-txt` | `#2C6396` | H209 S55 L38 | 6,30:1 branco · 5,70:1 quente |
| `--azul-luz` | `#88B4DD` | H209 S55 L70 | 4,56:1 sobre bloco · 5,65:1 sobre navy |
| `--azul-bloco` | `#0D4477` | H209 S80 L26 | branco por cima = 9,95:1 |
| `--azul-chip` | `#DCE9F5` | H209 S55 L91 | navy por cima = 10,00:1 |
| `--quente` | `#F7F3EC` | — | 1,11 vs branco · texto = 15,74:1 |

**Nota de método:** clarear `#003566` misturando com branco produz azuis
acinzentados (`#6686A3` e família) porque a mistura linear derruba a saturação.
A derivação correta é em **HSL preservando o matiz e fixando a saturação** — é
como se chega a um azul que ainda lê como azul.

### 4.3 A coincidência

`--azul` = H209 · S55 · L60 → 3,47:1
`--azul` do UnidoCLP (`#628AD1`) = H218 · S55 · L60 → 3,46:1

**Mesma saturação, mesma luminosidade, mesmo contraste até a segunda casa.** Nove
graus de matiz separam os dois. Partindo do logo do cliente chegamos praticamente
no accent do site que ele chamou de perfeito.

### 4.4 A falha que criou um token

`--azul` sobre `--azul-bloco` = **2,87:1**, reprova o piso de 3:1 do WCAG 1.4.11.
Por isso `--azul-luz #88B4DD` existe: sobre bloco escuro o accent **troca de
token**, não de cor.

### 4.5 Conferência final

```
OK    corpo #1A1A1A sobre branco          17,40:1   (piso 4,5)
OK    corpo #1A1A1A sobre quente          15,74:1   (piso 4,5)
OK    link --azul-txt sobre branco         6,30:1   (piso 4,5)
OK    link --azul-txt sobre quente         5,70:1   (piso 4,5)
OK    --azul como régua sobre branco       3,47:1   (piso 3,0)
OK    branco sobre --azul-bloco            9,95:1   (piso 4,5)
OK    branco sobre --navy                 12,34:1   (piso 4,5)
OK    navy sobre --azul-chip              10,00:1   (piso 4,5)
FALHA --azul sobre --azul-bloco            2,87:1   (piso 3,0)  → usar --azul-luz
```

---

## 5. Inventário de vídeo

`Videos/` — 8 arquivos, **441 MB**, quase todos 4K:

| arquivo | duração | assunto |
|---|---|---|
| `estacaoagua.mp4` | 13,9s | **aérea de estação de tratamento de água** |
| `elemnetotecnologicodeesteira.mp4` | 9,6s | **células solares em esteira de produção** |
| `14129726_…25fps.mp4` | 14,2s | fileiras aéreas de solar |
| `15267987_…30fps.mp4` | 22,2s | arranjo solar circular, aéreo |
| `placasSolares.mp4` | 26,3s | solar sobre grama |
| `placassolares2.mp4` | 33,0s | solar aéreo sobre areia |
| `placasSolares3.mp4` | 13,2s | close diagonal de placa |
| `placassolares4.mp4` | 13,0s | close da superfície azul |

**1 água, 1 esteira, 6 solar.** O acervo é solar-pesado e não tem nada de
Oil & Gas — que é provavelmente o maior vertical da empresa. É a razão de o
momento 3 ser fotografia e não vídeo.

Três arquivos carregam faixa AAC a 253 kb/s. **Remover sempre** — desperdício, e
autoplay com áudio apanha de política de navegador.

---

## 6. Correção de fato ao `memoria.md`

O `memoria.md` registra **duas vezes** (19/08 e 20/08) que vídeo estava parado
porque *"não há ffmpeg neste ambiente"*, e lista os vídeos como pendência aberta.

**Isso é falso a partir de 2026-08-25.** O pacote `imageio_ffmpeg` está instalado
e traz o binário:

```
C:\Users\kegit\AppData\Roaming\Python\Python314\site-packages\
  imageio_ffmpeg\binaries\ffmpeg-win-x86_64-v7.1.exe
7.1-essentials — libx264, libx265, libvpx-vp9, libaom-av1
```

Acesso por `imageio_ffmpeg.get_ffmpeg_exe()`.

**Encode medido**, 8s de `estacaoagua`, 1920×1080, sem áudio, CRF 26, preset slow:

```
2.504.432 bytes (2,5 MB) — 5,0s de encode  →  ~313 KB/s a 1080p
```

Portanto: loop de 10s ≈ 3 MB; três momentos ≈ 9 MB mais alternativas AV1/VP9;
teto do Cloudflare Pages é 25 MB por arquivo. **441 MB de 4K viram ~10 MB
publicados.** A pendência de vídeo está encerrada.

---

## 7. Decisões desta sessão

Todas do usuário, em três rodadas.

| # | Decisão |
|---|---|
| 1 | **Herói: fotografia única tratada.** Full-bleed, véu navy, tipo por cima. |
| 2 | **Dourado sai do site**, vive só dentro do logo. |
| 3 | **Alternância suavizada**: `#001D3D`/`#000814` saem, bloco escuro vira azul. |
| 4 | **Escopo: as 9 páginas**, redesenho completo. |
| 5 | **Accent: azul médio**, paralelo direto do `--azul` do UnidoCLP. |
| 6 | **Tema único claro** — o alternador sai. |
| 7 | **Peças que ficam:** `mimico.js` (IHM/SCADA), `malha.js`, `carta.js` (mapa). |
| 8 | **`braco.js` vira easter egg do 404.** |
| 9 | **Saem:** `clp.js`, `planta.js`, `marca.js` — guardados, não apagados. |
| 10 | **Fotografia:** todo o acervo do repositório, **fechando com o assunto**. |
| 11 | **Legendas descritivas, nunca afirmação de autoria.** |
| 12 | **Tipografia travada**, exceto `--fs-display`, reaberto para medir sobre foto. |
| 13 | **Movimento: os dois ficam** — inércia da roda (LERP 0.11) e rodapé revelado. |
| 14 | **Lottie fora**, SVG com `stroke-dashoffset` no lugar. |
| 15 | **Herói: aérea de usina solar em construção**, entre quatro candidatas. |
| 16 | ~~Herói contido~~ — **revertido**: chegou vídeo 4K e a restrição de resolução sumiu. |
| 17 | **Herói é `Videos/heroi/heroi.mp4`**, full-bleed, espelhado (`hflip`), véu 25%. |
| 18 | **Hover: um gesto, dois tokens** por superfície. `--navy-hover` morreu na medição. |
| 19 | **Momento 3 = macro do módulo de relés** com traço. |
| 20 | **Assets de marca em `referencia/marca/`**, 13 arquivos. |

`marca.js` sai por uma razão específica que vale registrar: **ela extruda o
RE-DESENHO da marca, não a arte real.** Mantê-la reintroduziria exatamente o erro
que o cliente reclamou.

---

## 8. Ferramental que entrou

`npm install -g ui-ux-pro-max-cli@2.15.0`, depois `uipro init --ai claude` dentro
de `I3AutomationSite/`.

Criou **7 pastas** em `.claude/skills/`, não uma: `banner-design`, `brand`,
`design`, `design-system`, `slides`, `ui-styling`, `ui-ux-pro-max` — ~4,5 MB,
untracked.

**Licença do conteúdo é CC-BY-NC-4.0** (o CLI é MIT). Isto é trabalho comercial
pago. Usar como referência de decisão é uma coisa; embutir tabelas ou derivados
no entregável é outra. Recomendação: `.gitignore`.

O `stacks/` não cobre a stack do projeto — tem react, next, vue, svelte, shadcn,
flutter, threejs, `html-tailwind`, e nenhum HTML+CSS+JS puro. A parte útil é a
agnóstica: `colors.csv`, `typography.csv`, `motion.csv`, `landing.csv`.

Contribuição real: a busca de cor corroborou de forma independente a família
âmbar, e ao fazer isso revelou que o problema era **estrutural, não cromático**
(§4.1).

---

## 8.5 O herói contido — REVERTIDO, mas o raciocínio fica

> **Esta decisão foi revertida em §8.6**, quando chegou o vídeo 4K e a restrição
> de resolução que a motivava deixou de existir. Fica registrada porque a
> medição continua válida: é a referência de quanto um arquivo cobre em cada
> largura de coluna, e vale para qualquer foto futura.

A foto escolhida (`fotosproduto/solar.png`) é **1280×720**. Full-bleed em retina
pede ~2400px, e ampliar aérea de drone com fileiras finas repetidas serrilha.

Cobertura do arquivo de 1280px contra o grid de 12 num container de 1376:

| colunas | CSS px | pede @2x | cobertura |
|---:|---:|---:|---:|
| **5/12** | **573** | 1146 | **112%** |
| 6/12 | 688 | 1376 | 93% |
| 7/12 | 803 | 1606 | 80% |
| 8/12 | 917 | 1834 | 70% |
| 12/12 | 1376 | 2752 | 47% |

Mobile, onde a coluna empilha: 390 CSS × 3x = 1170px → **109%**. Passa.

**Daí a especificação 7/5** — tipo em `1 / 8`, foto em `8 / -1`.

**Duas consequências que não eram óbvias:**

1. **O véu navy do herói deixa de existir.** Ele só servia para o texto
   sobreviver sobre a imagem. Sem sobreposição, sem véu — uma camada a menos, e a
   fotografia com a cor que ela tem.
2. **`--fs-display` fechou sem precisar de medição nova.** Ele tinha sido
   reaberto porque tipo sobre fotografia pede outra coisa. O tipo agora está
   sobre campo chapado, que é o caso para o qual a escala foi desenhada. **A
   tipografia volta a ser 100% travada, sem exceção nenhuma.**

Registro de acervo: as quatro candidatas vieram de
`referencia/universodoclp-assets/.../fotosproduto/` — são as fotos de produto do
UnidoCLP. A pasta tem 24 arquivos, sete deles acima de 3.000px, mapeados em
`plano.md` §7.2. O maior é `pexels-valentin-ilas` (9504×6336); o mais estratégico
é **`gas.jpg` (7900×5266)**, único material de alta resolução de Oil & Gas.

Uma das candidatas era um **módulo de 4 relés SRD-05VDC-SL-C** — acessório de
Arduino, não um CLP. Descartada como herói por credibilidade: a i3 programa
ControlLogix e S7 e é fornecedora federal. Realocada para Capabilities, onde é
excelente, e como candidata do traço do momento 3 (é toda aresta dura com fios
em curva).

---

## 8.6 O herói em vídeo — a medição que salvou o enquadramento

`Videos/heroi/heroi.mp4`: **3840×2160 · 34,1s · 29,97fps · 18,7 Mbps.** Painel
solar em contra-plongée, céu refletido, nuvens correndo, sem corte.

**Luminância das zonas candidatas ao H1, pior caso ao longo dos 34s**, contra
branco puro (percentil 90 da zona, quadro a quadro):

| zona | branco por cima | |
|---|---:|---|
| esquerda-inferior (lugar clássico do H1) | **1,34:1** | reprova |
| esquerda-meio | **1,10:1** | reprova |
| faixa inferior inteira | 2,94:1 | reprova |
| direita-inferior | 5,99:1 | OK |

**O céu fica à esquerda, o painel escuro à direita** — e o split 4/8 do site põe
título à esquerda. O tipo morreria exatamente onde precisa estar. Véu de **62%**
salvaria (4,80:1), mas enlameia o vídeo.

**A correção custa uma flag: `-vf hflip`.** Espelhado, medido no clipe inteiro:

| véu navy | branco por cima |
|---:|---:|
| **0%** | **5,28:1** |
| **25%** | **6,63:1** ← alvo |
| 45% | 7,95:1 |

Passa AA **sem véu nenhum**. Espelhar é inócuo: não há texto, rosto nem marca no
quadro, só painel e céu.

**Consequência de bitrate, contraintuitiva:** véu leve esconde MENOS artefato. O
CRF 30 orçado para os momentos vale porque lá o véu é de 62%. O herói, com 25%,
precisa de CRF mais baixo — **medir, não herdar**.

**O que isso reverteu:** o herói contido (7/5) existia só porque a foto era
1280×720. Com 4K a restrição sumiu. E `--fs-display`, que tinha fechado por não
haver imagem sob o tipo, volta a ficar **em observação** — mas o painel espelhado
é quase uniforme a 6,63:1, então a escala herdada provavelmente aguenta.

---

## 8.7 O hover — nenhuma cor única serve

| preenchimento | rótulo | branco | quente | off-white | bloco |
|---|---:|---:|---:|---:|---:|
| `--navy #003566` | 12,34 | 12,34 | 11,16 | 11,28 | **1,24** |
| `--azul-txt #2C6396` | 6,30 | 6,30 | 5,70 | 5,76 | **1,58** |
| `--azul #4D8ECB` | **3,55** | 3,47 | 3,14 | 3,17 | **2,87** |
| `--azul-luz #88B4DD` | 5,65 | **2,18** | **1,97** | **2,00** | 4,56 |

Mesma estrutura do accent: claro e escuro pedem tokens diferentes. Spec em
`plano.md` §6.

**`--navy-hover #002647` morreu aqui:** 1,24× de delta contra `--navy` é
imperceptível. O botão primário parecia não reagir ao ponteiro. Quem ocupa o
papel é `--azul-txt`, a 1,96×.

---

## 9. Aberto

1. ~~**`--fs-display` sobre o vídeo do herói**~~ — **FECHADO em 2026-08-26, e
   por um caminho que ninguém previu: o herói nunca usou esse token.** Ver
   §11.1. A tipografia volta a ser 100% travada, sem exceção nenhuma.
2. ~~**Material extra de vídeo** — painel/MCC, operador na tela de SCADA,
   oil & gas.~~ **FECHADO em 2026-08-26, e sem pedir nada ao cliente: o
   material já estava no disco.** O acervo tem 14 arquivos e não 8. Ver §23.
3. ~~**A regra 7 de clean na dobra de setores**~~ — **FECHADO em 2026-08-26**:
   a grade saiu da home. Ver §25.2.

---

## 10. Risco em aberto

A home vai carregar simultaneamente: inércia sequestrando o `wheel`, três
momentos lendo progresso de rolagem, parallax e um rodapé sticky. **Nada disso
foi medido junto ainda**, e é a única coisa que nenhuma medição fora do navegador
responde.

Saída já decidida em `design.md` §6.1: se ficar pesado, **a inércia é a primeira
coisa a cair**, não os momentos.

---

# PARTE II — a execução, 2026-08-26

As fases 1 a 8 do `doit.md` foram executadas. O que segue são as medições
NOVAS, as decisões que a execução forçou, e — mais importante — **os quatro
pontos em que a tela contrariou o plano**. O plano não estava errado; ele
estava incompleto em lugares que só o render revela.

---

## 11. Os quatro lugares onde a medição contrariou o plano

### 11.1 O herói nunca usou `--fs-display` — e isso fecha o único item aberto

O `doit.md` carregava um item aberto desde o início: *"`--fs-display` sobre o
vídeo — entra como está; conferir na tela e só mexer se falhar."*

Na primeira montagem eu apliquei `--fs-display` ao H1 do herói e **ele falhou
espetacularmente**: 200px contra 1.280px úteis, cada uma das três linhas
quebrando em duas, seis linhas transbordando a dobra.

Só que a falha era minha, não do token. O herói ANTERIOR nunca usou
`--fs-display`. Ele usava `clamp(2.25rem, 5.2vw, 4.75rem)`, com um comentário
que já explicava tudo:

> *"O display de 200px é para uma palavra só. Aqui a headline tem oito, e por
> isso ela vive um degrau abaixo — a escala não mudou, o uso mudou."*

**Portanto o item aberto fecha sem que um valor da escala mude.**
`--fs-display` continua `clamp(2.75rem, 10.4vw, 12.5rem)`, intocado. A
tipografia volta a ser 100% travada, sem exceção nenhuma.

O que mudou foi só a largura disponível para a headline: o herói era contido em
6 de 12 colunas (~640px) e virou full-bleed (1.280px úteis). Por isso o degrau
dela sobe de 4,75rem para **7,5rem**, e o teto tem conta:

| | |
|---|---|
| linha mais larga, "Good control strategy", em Outfit 300 | **9,741em** |
| largura útil dentro de `--container` | **1.280px** |
| teto para caber numa linha só | **1280 / 9,741 = 131px** |
| escolhido | **7,5rem = 120px** (91% da largura) |

`clamp(2.25rem, 8.4vw, 7.5rem)`, e o coeficiente fluido fica abaixo do teto em
toda a faixa: 1376→115 (teto 131), 1200→101 (teto 113), 1024→86 (teto 98),
768→64 (teto 72).

> **Beco sem saída registrado:** `max-width: 62ch` no bloco do herói. `ch` é
> relativo ao font-size do PRÓPRIO elemento, que ali é o do corpo — 62ch
> resolviam em ~560px e estrangulavam uma headline de 120px. Quem limita a
> headline é o container, não uma medida em `ch` herdada do texto.

### 11.2 O nav reprova sobre o herói — o plano só mediu a zona do H1

`plano.md` §3.2 mediu a zona do H1 com cuidado e não mediu mais nada. Mas o nav
é **transparente** sobre o herói (`.nav--sobre-heroi`), em texto branco, e a
faixa do topo deste clipe é céu.

Medido no pôster já velado a 25%, branco por cima da faixa do nav:

| | |
|---|---:|
| sem scrim | **2,76:1** — reprova |
| sem scrim, metade direita (onde ficam os links) | **2,92:1** — reprova |
| scrim a .25 | 4,22:1 — reprova por pouco |
| **scrim a .32** | **4,79:1** — passa, e é o mínimo que passa |
| scrim a .45 | 6,14:1 |

Entrou um gradiente de topo a `.32` morrendo em 22% da altura — acima do H1,
que continua nos 8,81:1 medidos. É a mesma técnica que `design.md` §5.1 já
torna obrigatória no momento 1: escurecer **onde o texto vive**, em vez de
velar a imagem inteira até o pior quadro sobreviver.

### 11.3 A frase do filme caía no buraco do próprio scrim

O scrim do `.filme` é de dois gradientes por decisão: topo e pé escurecem, o
**meio fica intocado** para a fotografia não morrer. E a frase estava centrada
verticalmente — ou seja, exatamente no meio.

Branco sobre o pôster do momento 1, percentil 90 por faixa:

| faixa | sem scrim | com scrim |
|---|---:|---:|
| topo 0–20% | 2,77:1 | 5,51:1 |
| **meio 40–60%** | 2,31:1 | **2,45:1** — reprova |
| pé 72–92% | 2,07:1 | **6,17:1** |

`place-items: end stretch` em vez de `center`. A frase desce para onde o campo
é escuro — a mesma decisão que o herói tomou por outra medição.

### 11.4 O CRF do herói: a previsão estava metade certa

`plano.md` §5.4 previa que o herói precisaria de CRF bem mais baixo que os
momentos, porque véu leve esconde menos artefato. A regra geral está certa. A
consequência prevista, não.

Medido a 1920px, espelhado, contra referência em CRF 12. O véu de 25% é uma
transformação **afim idêntica nos dois lados** da comparação, então soma
exatamente `20·log₁₀(1/0,75) = 2,50 dB` ao PSNR — não precisa medir duas vezes:

| CRF | MB em 12s | PSNR-Y | sob véu 25% | SSIM |
|---:|---:|---:|---:|---:|
| 20 | 7,31 | 47,74 dB | 50,24 dB | 0,98999 |
| 23 | 4,62 | 46,36 dB | 48,86 dB | 0,98737 |
| **26** | **3,05** | 44,83 dB | **47,33 dB** | 0,98378 |
| 30 | 1,86 | 42,52 dB | 45,02 dB | 0,97652 |

**A curva não tem joelho.** Nem a 30 a qualidade desaba. A razão é o assunto —
céu e painel quase uniforme, quase nada de alta frequência —, que é o **mesmo
motivo** pelo qual o clipe passa AA sem véu nenhum: a zona é homogênea.

A escolha deixou de ser de qualidade e virou de orçamento. **CRF 26**: 3,05 MB,
o mesmo ~3 MB por clipe que `design.md` §5.4 orçou, com 47 dB de folga.

---

## 12. VP9: o deslocamento de CRF é +12, não +3

Primeira passada do `build_video.py` usou `crf + 3` para o VP9. **O WebM saiu
MAIOR que o mp4 em dois dos três clipes** (2.519 KB contra 1.283 KB no momento
1). Servir isso seria pior que não servir nada: o navegador fica com o primeiro
`<source>` que sabe tocar e baixaria o arquivo mais pesado achando que economiza.

A escala de CRF do VP9 não é a do x264, e comparar "crf 30 contra crf 33" não
diz nada. O que decide é **SSIM casada**: com a mesma qualidade percebida, quem
gasta menos bytes. Medido em 5s do momento 1, a 1600px:

| codec | KB | SSIM |
|---|---:|---:|
| h264 crf 30 | 688 | 0,95967 |
| vp9 crf 33 | 1271 | 0,97590 |
| vp9 crf 38 | 790 | 0,96855 |
| **vp9 crf 42** | **549** | **0,96018** ← casa a SSIM, gasta 20% menos |
| vp9 crf 46 | 384 | 0,94894 |

Com `+12` o VP9 finalmente faz o que se esperava dele. Total publicado: **9,5
MB**, contra os ~10 MB previstos, e todo WebM menor que o mp4 (o do herói é 51%
menor: 1.503 KB contra 3.080 KB).

---

## 13. A regressão silenciosa das bordas com alfa

**Todas** as bordas brancas com alfa do site foram medidas sobre `#001D3D`. Com
o bloco escuro clareando para `--azul-bloco #0D4477`, o **mesmo alfa passou a
dar menos contraste** — superfície mais clara pede MAIS alfa, não menos.

O feixe a `.38` caiu de 3,47:1 para **2,79:1** e passou a reprovar o piso de
3:1 do WCAG 1.4.11 sem que nada acusasse. Corrigido para `.45` (3,31:1, e é o
mínimo que passa).

Branco com alfa sobre as superfícies novas:

| alfa | sobre `--azul-bloco` | sobre `--sup-3-fundo` |
|---:|---:|---:|
| .30 | 2,27:1 | 2,60:1 |
| .38 | 2,79:1 | 3,33:1 |
| .45 | **3,31:1** | 4,10:1 |
| .55 | 4,18:1 | **5,39:1** |

`--borda-ui-esc` a `.45` sobrevive (3,31:1). A aresta do rodapé revelado a
`.55` sobre `--sup-3-fundo` dá 5,39:1.

É por isso que `contraste.py` agora tem uma seção de **LÁPIDES**: oito linhas
que DEVEM reprovar, cada uma um token que alguém vai propor de novo. Se uma
delas passar, a paleta mudou embaixo do sistema.

---

## 14. `--sup-3-fundo`: o rodapé precisava de um valor novo

`#000814` morreu com a alternância suavizada, e o rodapé revelado precisa ser
mais fundo que o bloco para a subida ler. Derivado em H209 S80, o mesmo matiz:

| L | cor | branco por cima | contra o bloco |
|---:|---|---:|---:|
| 12 | `#061F37` | 16,68:1 | 1,68:1 |
| **16** | **`#082A49`** | **14,61:1** | **1,47:1** |
| 20 | `#0A345C` | 12,66:1 | 1,27:1 |

L16. Passo visível contra o bloco sem voltar ao quase-preto — que é exatamente
o que `#000814` fazia de errado.

---

## 15. O logo: o método reproduziu a medição pixel a pixel

`ferramentas/build_marca.py` implementa o método de `design.md` §3.4 —
quantizar para as 7 cores exatas, flood fill da borda atravessando não-dourado,
knockout do alcançado, downsample LANCZOS. Rodado sobre a arte real:

```
navy   #003566    4.988 preservados   46.433 em knockout
branco #FFFFFF        0 preservados   20.066 em knockout
ouro (5 faces)   64.827 preservados        0 em knockout
```

**4.988 e 46.433 batem exatamente com o §3.2**, medido numa sessão anterior por
outro caminho. O método está certo, e agora é reproduzível.

Recortes medidos, achados por componente conexo e não por coordenada escrita à
mão: **marca isolada 421×268 (1,571:1)**, **lockup 946×268 (3,530:1)**, e a
**tela 330×215 (1,535:1)**, que é a maior região dourada conexa.

### 15.1 O ícone precisa de dois recortes, não de um

Renderizado nos tamanhos reais: a marca inteira num quadrado de 16px ocupa
16×10, a moldura vira uma barra de 1px e o "i3" fica com 4px e some.

| tamanho | marca inteira | só a tela |
|---|---|---|
| 16px | borrão | campo dourado + glifo, lê |
| 32px | limite | lê |
| 48px+ | lê bem | perde a moldura, que é o desenho |

Então 16/32/48 usam a **tela** e 180/192/512 usam a **marca inteira em
knockout**. Não é inconsistência: é a mesma decisão que o SVG antigo já tomava
("no favicon a moldura vira só a base"), tomada agora sobre a arte certa.

`favicon.svg` e `logo-icone.svg` foram **removidos**. Eram o redesenho; mantê-los
no diretório significava que o próximo deploy os publicaria e a marca errada
voltaria pela porta dos fundos.

---

## 16. O traço do momento 3 é extraído da própria fotografia

`ferramentas/build_traco.py`: cinza → desfoque 1,4 → Sobel por convolução 3×3
→ limiar por **percentil** (5,5% dos pixels, e não valor absoluto, que acerta
numa foto e erra na seguinte) → afinamento por máximo local → caminhada
8-conectada → Douglas-Peucker.

Sobre a macro do módulo de relés: **110 caminhos, 454 pontos, 8,8 KB**. Vai
INLINE na página — não por `<img>`, porque um SVG referenciado vive num
documento separado e o CSS da página não alcança os `<path>` dele. Este traço
precisa de duas coisas que só o CSS da página dá: herdar `currentColor` e
receber `stroke-dashoffset` atado a `--p`.

`pathLength="100"` em todo caminho: um par dasharray/dashoffset serve para os
110, e nenhuma medição acontece em JS. Medido sobre a foto velada a 62%: o
traço a `.85` dá **6,71:1**, e o texto branco no pé, **6,34:1**.

---

## 17. WCAG 2.2.2 — o que o plano não cobria

O herói é um loop de 12s que começa sozinho e divide a tela com a headline.
Isso encaixa nas três condições do critério 2.2.2 (movimento automático, mais
de 5 segundos, em paralelo com outro conteúdo) e **exige um mecanismo de
pausa**.

`plano.md` §3.4 especifica o herói como "mudo, em loop" e §5.4 cobre
`prefers-reduced-motion` — que é outro critério (2.3.3) e não substitui este:
2.2.2 vale para quem **não** pediu movimento reduzido e mesmo assim quer parar
a imagem.

Entrou um botão de pausa de 44px, escrito no HTML e não injetado por JS (injetar
deixaria quem está sem JavaScript com um vídeo que não para — exatamente o caso
que o critério cobre).

**Não viola a regra 10 de clean.** O exemplo que a regra usa é a linha "Drag the
arm to orbit" — uma FRASE ensinando um gesto inventado. Um botão de pausa é o
oposto: símbolo universal, sem legenda.

---

## 18. A rede de segurança do `.reveal`

Havia saída para dois casos — `prefers-reduced-motion` e navegador sem
`IntersectionObserver` — e **nenhuma para o terceiro: o IO existe e nunca
dispara**.

Não é hipotético; foi observado. Numa aba de segundo plano o Chrome não entrega
callback de IO. A página PINTA — uma captura de tela mostra — mas nada recebe
`is-visivel`, e o estado base de `.reveal` é `opacity: 0` com desfoque. O que se
encontra é uma página em branco com o logo em cima.

É a MESMA armadilha que o código já registrava duas vezes para a intro: estado
inicial de animação que **esconde conteúdo**. Lá o conserto foi por CSS; aqui
tem de ser por tempo, porque quem esconde é uma classe que só o JS põe.
Timer de 6s, bem depois de qualquer revelação legítima (a mais lenta é .85s
mais 70ms por item).

---

## 19. Higiene: o que a varredura pegou

`varredura.py` **não lia `poster=`**, então acusava os três pôsteres de vídeo
como órfãos — sugerindo apagar arquivos que são obrigatórios por spec e que são
o que o visitante vê com `prefers-reduced-motion`. Uma varredura que chama de
órfão o que é obrigatório convida a apagar o arquivo certo. Corrigido.

Depois disso, órfãos reais removidos do deploy (não do repositório):

- `js/clp.js`, `js/planta.js`, `js/marca.js` — 31 KB de JS que nenhuma página
  carregava. O `design.md` §8 diz "nada do que sai é apagado do repositório";
  o que a regra protege é a **fonte**, e ela continua em `fonte/js/`. Publicar
  é outra coisa.
- `img/dupla/clp-*` e `img/faixa/robotica-*` — ~2 MB, a dupla e a faixa que
  saíram da home.
- dez PNGs de marca — `site/brand/` agora recebe só os seis que alguma página
  referencia; `referencia/marca/` guarda os 17.
- `img/cabecalho/capacidades-*` — nunca vestiu capabilities (1024×331 seria
  ampliada 1,87× e sairia borrada; a página usa `faixa/refinaria`). O único
  consumidor era o cabeçalho de terms.

**Estado final: 0 quebradas, 0 órfãos, 0 conflitos de seletor, 0 fotos
repetidas, 0 falhas na matriz de contraste.**

### 19.1 As duas páginas legais perderam a fotografia de cabeçalho

`repetidas.py` acusou: privacy usava `cabecalho/quem-somos` e terms usava
`cabecalho/capacidades` — as duas vestindo a foto de uma página de conteúdo.

A colisão era invisível até esta rodada porque who-we-are era a única página
SEM foto (a marca 3D ocupava a direita). Com `marca.js` fora, who-we-are
recebeu a foto que leva o nome dela e a duplicata apareceu.

Não há uma sétima foto de cabeçalho no acervo — as seis pertencem, por assunto
e por nome, às seis páginas de conteúdo. E inventar uma para uma política de
privacidade resolveria o problema errado: **uma página legal é um documento, e
não tem hero.**

---

## 20. A faixa de armazenamento estava mentindo

Ela dizia que o único valor guardado no navegador era a escolha de tema
claro/escuro. **O alternador saiu** (design.md §1.4 regra 6), então a frase
virou falsa no instante em que o botão saiu do nav.

Isso é exatamente o defeito que a faixa existe para evitar: o texto dela foi
escrito com cuidado justamente porque "we use cookies to improve your
experience" numa página sem cookie é afirmação falsa, e a política de
privacidade a poucos cliques diz o contrário.

O que sobrou guardado é a dispensa DA PRÓPRIA FAIXA — ela guarda um registro de
si mesma. Agora é isso que ela diz, e a política de privacidade foi corrigida
nos três lugares em que citava o tema.

---

## 21. Tensão em aberto: a regra 7 de clean na dobra de setores

`plano.md` §1 regra 7 é literal: *"Uma imagem por seção. Grade de miniaturas só
existe em `gallery.html`. Verificação: conte `<img>` fora da galeria."*

A dobra 10 da home — Setores — tem **cinco** imagens: os cinco cards de
vertical, cada um com a fotografia e a lente de revelação.

As duas coisas estão no mesmo documento e se contradizem: §4 lista "Setores"
como dobra com os cinco verticais nomeados, e `design.md` §8 preserva a lente
sem ressalva. **Não mexi.** Gutar um componente de conteúdo que o cliente vê,
por leitura minha de uma tensão interna da spec, é decisão do usuário e não
minha. Fica registrado para decisão.

---

## 22. O que a verificação em navegador alcançou, e o que não

A aba de automação abre em **segundo plano** (`visibilityState: "hidden"`), e
nesse estado o Chrome não entrega `requestAnimationFrame` nem carrega mídia.
Consequência: `--p` não avança, os momentos não animam, nenhum vídeo decodifica.

Dois becos sem saída de diagnóstico, registrados para não serem refeitos:

1. **`http.server` do Python não implementa `Range`.** O `<video>` do Chrome
   manda `Range: bytes=0-` e espera 206; o handler devolve 200 com o corpo
   inteiro. O `curl` fica feliz, o `<video>` trava em `networkState 2 /
   readyState 0` **para sempre, sem erro nenhum**. Corrigido com um servidor de
   teste próprio — mas não era a causa raiz.
2. **A causa raiz era a aba oculta**, e ela também congela `rAF`. Qualquer
   `await` sobre `requestAnimationFrame` trava a avaliação por 45s e derruba a
   conexão com o renderer.

**Verificado:** layout das treze dobras, tamanho medido do H1, estado inicial
dos momentos (janela fechada, traço por desenhar), contraste faixa a faixa,
nav sólido ao rolar, a rede de segurança do `.reveal`, e o build limpo.

**Não verificado:** os três momentos a 60 quadros convivendo com a inércia da
roda, o parallax e o rodapé sticky. É o risco principal que `design.md` §6.1
registra, e continua aberto. A saída, se ficar pesado, já está decidida: **a
inércia cai primeiro**, não os momentos.

---

# PARTE III — a ampliação da home, 2026-08-26

Pedido do usuário, depois de ver a home: *"o herói está perfeito mas ainda
usamos imagens repetidas. Adicione mais vídeos ao rolar a home, com animações
de rolagem. Preciso de uma home impecável, mas não mexa no herói."*

**O herói não foi tocado.** Nem o vídeo, nem o véu, nem o `hflip`, nem o H1,
nem o scrim do nav, nem o botão de pausa.

---

## 23. O acervo de vídeo era quase o dobro do que a memória registrava

`memorianew.md` §5 lista **8 arquivos, 441 MB**. O disco tem **14 arquivos,
645 MB** — e entre os seis que ninguém tinha aberto estavam justamente os dois
que o §9 listava como material AUSENTE, a pedir ao cliente:

| arquivo | duração | assunto |
|---|---:|---|
| `automacaorobo.mp4` | 11,3s | célula com robô SCARA e passa-cabo azul |
| `automacaorobo2.mp4` | 7,4s | **fileira de atuadores pneumáticos** |
| `automacaorobo3.mp4` | 9,5s | dispositivos azuis em máquina, foco raso |
| `ihm.mp4` | 18,8s | **operador na tela de uma máquina** |
| `pc.mp4` | 10,7s | engenheiro na estação de trabalho |

> **A lição de método:** o §9 tinha uma pendência aberta pedindo material que
> já estava na pasta. Inventário por memória não substitui inventário por
> `os.walk`. A tabela do §5 agora está desatualizada e fica como está — este
> parágrafo é a correção.

---

## 24. A home passou a ter QUATRO momentos, cada um com mecanismo próprio

A regra que protege a calma não é "poucos momentos", é **"nenhum mecanismo se
repete"**. Repetir o filme quatro vezes transformaria um momento em padrão e um
padrão em tique.

| | mecanismo | assunto | vertical |
|---|---|---|---|
| M1 | o **filme** — a janela abre de faixa a full-bleed | estação de água | água e esgoto |
| M2 | **variação A** — a janela é fixa; quem anda é o texto | atuadores pneumáticos | produção |
| M3 | **variação C** — duas portas correm e descobrem o vídeo | operador na tela | **controle** |
| M4 | **variação B** — parallax com o traço se desenhando | tanque, tocha, tubulação | **oil & gas** |

Com o herói (solar), a home cobre **os cinco verticais**. Antes desta rodada,
oil & gas — provavelmente o maior deles — não tinha uma única peça de mídia em
lugar nenhum do site.

### 24.1 A variação C, e por que o gesto tem assunto

Duas portas opacas em `--sup-3` correm para os lados por `transform`, atadas a
`--p`. Nunca `width`: largura causa layout a cada quadro.

**50,5% de largura em cada uma, e não 50%.** Com 50% exatos um arredondamento
sub-pixel abre um fio de vídeo no meio antes da hora. Meio ponto percentual de
sobreposição custa nada e fecha a costura.

O gesto significa: o clipe é alguém operando uma máquina, e a máquina se
abrindo é a leitura literal do que a empresa faz — dar acesso ao processo. Um
mecanismo que só serve de variação é decoração.

### 24.2 A esteira saiu, e a troca corrige o assunto onde ele mais importava

`plano.md` §5.5 pedia o momento 2 *"cortado fechado nos bicos e atuadores"*. O
clipe da esteira **não tem bico nem atuador** — tem uma polia e uma correia,
com células solares passando. Cortar fechado escondia o solar mas não produzia
o assunto pedido; era o compromisso possível com o acervo que se conhecia.

`automacaorobo2.mp4` **é** o assunto pedido, e sem recorte nenhum.

### 24.3 A variação A não estava acontecendo

Defeito encontrado na tela: a coluna de texto cabia numa tela, então o
`position: sticky` do vídeo **nunca engatava** — os dois subiam juntos e a
dobra era um vídeo ao lado de um texto, que é o que qualquer página faz.

A variação inteira é "o vídeo fica, o texto anda". Sem trilho, não há variação.
Corrigido com `--s-8` (96px) entre blocos e respiro vertical: a seção passou de
77vh para 126vh e o mecanismo passou a existir. 128px chegaram a ser testados
e a coluna virou fragmento solto — **o vão precisa ser maior que o respiro de
parágrafo e menor que o de seção**, ou o texto deixa de ler como coluna.

---

## 25. `gas.jpg` estava em CINCO lugares — e a ferramenta não via

O usuário disse "ainda usamos imagens repetidas". Estava certo, e o defeito era
sistêmico.

`gas.jpg` (7900×5266) é a **única** fotografia de oil & gas do acervo inteiro.
Ela tinha sido recortada e exportada cinco vezes, com cinco nomes:

| nome | onde |
|---|---|
| `momento/refinaria` | momento 4 da home |
| `setores/oil-gas` | card de setor, **na mesma página**, uma dobra abaixo |
| `setor/oil-gas` | card de setor de past-performance |
| `faixa/refinaria` | cabeçalho de capabilities |
| `galeria/refinaria` | galeria |

`repetidas.py` agrupava por **caminho**, então cinco arquivos distintos davam
zero alarme — enquanto a home mostrava o mesmo tanque com a mesma tocha duas
vezes em duas dobras seguidas.

### 25.1 A ferramenta agora compara pixel

dHash de 8×9 (64 bits) sobre cada arquivo. Invariante a escala, formato e
compressão — que são as três coisas que o pipeline de imagens faz — e sensível
a recorte só o suficiente: dois recortes do mesmo negativo caem a poucos bits,
duas fotos diferentes ficam longe. Limiar de Hamming ≤ 12, generoso de
propósito: falso positivo custa olhar duas imagens; falso negativo vai ao ar.

Duas isenções, as duas de **papel**: `galeria/` (a galeria É o acervo — toda
foto do site sai de lá por definição) e `brand/` (o logo deve estar em todas as
nove páginas). **Nenhuma isenção cobre duas ocorrências na mesma página.**

### 25.2 O que mudou de lugar

- **A grade de setores saiu da home.** Dois motivos que apontam para o mesmo
  lado: cinco imagens numa seção contra a regra 7 de clean, e o card de oil &
  gas era a mesma fotografia do momento 4 uma dobra acima. A home já cobre os
  cinco verticais pelo herói e pelos quatro momentos. A taxonomia continua em
  past-performance, que é a página do assunto, com o conjunto próprio dela em
  `img/setor/`. *(Isto também fecha a tensão registrada no §21.)*
- **Capabilities trocou de cabeçalho** para `faixa/britagem-planta`
  (`pexels-valentin-ilas`, 9504×6336). Resolve de quebra o problema que
  `cabecalho/capacidades` tinha: 1024×331 seria AMPLIADA 1,87× num cabeçalho
  de 620px.
- **`gas.jpg` aparece uma vez**, no momento 4, full-bleed com o traço. Quando
  só há um exemplar de um assunto, usá-lo bem uma vez vale mais do que
  espalhá-lo.

> **Descartada:** `pexels-shvetsa` (6240×4160). `plano.md` §8.2 a descreve como
> "mão em tela HMI colorida" e sugere Services. Vista de perto, é um **moedor
> de café** com alguém de avental listrado. Não é industrial.

---

## 26. O tcheco do `ihm.mp4`, e por que o trecho mudou duas vezes

A tela do clipe está em **tcheco** — é banco de imagem, não um sistema da i3.
Numa dobra full-bleed isso vira um documento legível em outro idioma na home de
uma fornecedora do governo federal americano.

1. **Primeira tentativa:** cortar fechado na mão (2400×1350) para diminuir o
   texto. Mas o momento é full-bleed atrás de duas portas, e `object-fit: cover`
   num palco de 100vh corta de novo por cima do corte — o resultado lia como
   **macro de uma mão**, que não conta história nenhuma.
2. **Segunda:** reabrir para 3200×1800. O quadro voltou a ler como estação, e o
   texto ficou **mais** legível, não menos.
3. **A solução não era de enquadramento, era de TRECHO.** A partir de ~13s a
   mesma tela vira outra coisa: leitura numérica **ao vivo** (1009.770 →
   892.237 → 872.760 → 140.270), vista 3D da peça, indicador de eixos, barra de
   avanço a 90%. Quase nenhuma prosa — e **número é neutro de idioma**.

5,6s de loop, e cabe: a câmera é praticamente estática, então o ponto de emenda
não tem evento para denunciar. A legenda descreve o que se vê e nunca afirma
que o sistema é da casa.

---

## 27. O deslocamento de CRF do VP9 não é uma lei

O `+12` do §12 economizava 20% no clipe da água. No clipe dos atuadores — uma
fileira de hastes metálicas finas, alta frequência em todo quadro — o VP9
**perdeu**: 2.644 KB contra 2.122 KB do h264, com o mesmo `+12`.

O ganho do VP9 depende do **assunto**, e nenhuma constante acerta em todos.
Então a garantia deixou de ser um número calibrado e virou **estrutural**: o
build compara os dois arquivos e **descarta o WebM quando ele não ganha**. Uma
constante bem escolhida envelhece no dia em que entra um clipe novo; a
verificação não envelhece.

Total publicado: **9,3 MB de vídeo**, quatro clipes.

---

## 28. Dois defeitos de CSS que não davam erro nenhum

### 28.1 O traço saía com a classe do gerador

`build_traco.py` escreve `class="traco__svg"` no `<svg>`. A home pedia
`.momento-b__traco`. O CSS nunca alcançava o elemento — e o sintoma era
traiçoeiro: os `<path>` continuavam desenhando, só que herdando a tinta do
**corpo** (`#1A1A1A`) em vez da cor da seção. Num campo navy isso dá linhas
escuras sobre escuro, que leem como sujeira de compressão e não como defeito.

`traco()` agora recebe a classe de quem chama.

### 28.2 A frase do momento C caía no degrau do próprio scrim

Uma tela de IHM é interface **clara**: branco sobre ela, sem scrim, dá
**1,47:1** — o pior caso de todo o site. O scrim inicial morria em 46% da
altura, o que entregava alfa efetivo de só **.35** no TOPO da faixa de texto: a
primeira linha da frase reprovava a ~3,3:1 enquanto a última passava.

**Um scrim que salva o pé e perde a cabeça do parágrafo é pior que nenhum,
porque nada acusa.** Medido:

| alfa | branco por cima |
|---:|---:|
| sem scrim | 1,47:1 |
| .48 | 4,23:1 — ainda reprova |
| **.62** | **6,18:1** — passa |
| .78 | 9,78:1 |

Agora `.82` no pé, `.62` em 30% e morrendo em 60%: a faixa inteira do texto
fica entre 6,18:1 e ~9,9:1, e os 40% de cima da imagem continuam limpos.

---

## 29. `contraste.py` ganhou a tabela dos momentos

Os quatro momentos têm quatro superfícies diferentes sob o mesmo texto branco,
e a diferença entre elas é grande: o bloco chapado da variação A dá 9,95:1 de
graça; a tela de IHM da variação C dá 1,47:1 e precisa do scrim mais forte do
site. Agora as quatro entram na matriz a cada rodada, e duas lápides novas
guardam os casos que não podem voltar.

---

## 30. O que a aba oculta impediu de ver — e o que a substituiu

Confirmado por medição: a aba de automação abre com `visibilityState:
"hidden"`, e nesse estado o Chrome **(a)** não entrega `requestAnimationFrame`,
**(b)** não carrega `loading="lazy"`, e **(c)** não re-rasteriza camadas
promovidas por `will-change`.

Consequência prática: uma captura de tela do momento 4 mostra o campo navy sem
a fotografia, e uma do momento 3 mostra as portas numa posição que não é a
atual — **mesmo com o layout computado correto**. Duas horas de diagnóstico
foram gastas nisto; fica registrado para não se repetir.

Três becos sem saída, os três descartados:

1. `http.server` do Python não implementa `Range` — o `<video>` do Chrome trava
   em `networkState 2 / readyState 0` para sempre, sem erro. Corrigido com
   servidor próprio, mas não era a causa.
2. `scroll-behavior: smooth` no `html` — rolagem programática vira animação, e
   animação precisa de `rAF`. `scrollTop` não avançava um pixel.
3. `will-change` nas portas e na foto do momento 4 — camada de compositor presa.

**O que substituiu a captura:** medição de geometria computada
(`getBoundingClientRect` responde certo mesmo sem pintura — as portas dão 0,
−486 e −972 para `--p` 0, 0,5 e 1) e **composição offline em PIL** do
poster + véu + scrim + traço. As duas juntas cobrem o que a captura cobriria,
e a matriz de contraste cobre o resto.

**Continua sem verificação:** os quatro momentos a 60 quadros convivendo com a
inércia da roda, o parallax e o rodapé sticky. É o risco principal do
`design.md` §6.1, e agora há **quatro** trilhos em vez de três. A saída, se
ficar pesado, continua decidida: **a inércia cai primeiro**, não os momentos.

---

# PARTE IV — sustentação e montagem, 2026-08-26 (segunda rodada)

Sete pedidos do usuário. **O herói não foi tocado**, de novo.

---

## 31. A sustentação — o defeito era de aritmética, não de gosto

*"Os vídeos precisam ficar em foco por um pequeno tempo antes de poderem ser
scrollados, tipo o max size, quando ele entra em tela inteira."*

Todo mecanismo interpolava de `--p` 0 a 1. Ou seja: a janela terminava de abrir
**exatamente** no instante em que o trilho acabava e a seção começava a sair da
tela. O vídeo existia em tamanho cheio por um quadro. **Todo o percurso era
abertura, e nada era permanência.**

A correção separa o curso em duas fases com `--fim-abre`:

| | trilho | abrindo | **parado em tela cheia** |
|---|---:|---:|---:|
| M1 filme | 260vh | 61vh | **99vh** |
| M2 variação A | 250vh | 69vh | **81vh** |
| M3 variação C | 240vh | 59vh | **81vh** |
| M4 variação B | 180vh | — | 80vh (parallax contínuo) |

`--abre: clamp(0, calc(var(--p) / var(--fim-abre)), 1)` é **derivado**, não
publicado pelo JS: o módulo 7 continua escrevendo só `--p`, e cada mecanismo
decide sozinho quanto do curso usa para acontecer.

---

## 32. A segunda seção: ela nunca chegava a tela cheia

*"A segunda seção com vídeo não me agradou muito."*

Diagnóstico: era a única das quatro que **nunca ocupava a janela**. As outras
três tomam a tela e prendem; esta era um retângulo de sete colunas parado ao
lado de uma coluna de texto. Como composição está correta; como **momento**,
não é um — faltava-lhe a única coisa que os outros três têm.

Agora tem duas fases, e a segunda é a que faltava:

1. `--abre` 0 → 1: a caixa vive à esquerda em ~52% da largura e a coluna de
   texto entra ao lado, linha a linha. **É o que o usuário pediu para
   replicar** na rodada anterior.
2. o resto do curso: a caixa cresce até tela cheia, o texto sai, e o vídeo fica
   sozinho e parado.

`clip-path` e não `width`/`grid`: o vídeo é full-bleed o tempo todo, o que muda
é o **recorte**. Sem layout por quadro, e o enquadramento não salta quando a
caixa muda de proporção.

**Por que não repete o momento 1:** lá a janela é uma faixa CENTRADA que abre
simetricamente, como um letterbox cedendo. Aqui é uma caixa DESCENTRADA que se
expande para os quatro lados enquanto entrega a coluna ao lado — o gesto é de
tomar a tela, não de revelar uma faixa.

A coluna sai em `--abre` .62, e a borda direita do vídeo só passa dos 56% da
tela depois disso: se as duas se cruzassem, o texto ficaria ilegível sobre a
imagem por um instante.

---

## 33. O momento 1 virou montagem de quatro cortes

*"O vídeo da água é legal, mas precisamos fazer um compilado."*

É a decisão certa **pela frase que a dobra carrega** — *"Senior control experts
know things they do not teach in school."* Ela não fala de um processo, fala de
**repertório**. Um plano único de estação de água ilustra água; quatro planos
que mudam ilustram a amplitude que a frase afirma.

| corte | clipe | assunto |
|---|---|---|
| 1 | `estacaoagua` | aérea da estação de tratamento |
| 2 | `automacaorobo` | célula com robô colaborativo |
| 3 | `pc` (recortado no monitor) | engenheiro na estação de trabalho |
| 4 | `automacaorobo3` (recortado à direita) | detalhe de dispositivo em máquina |

**4,5s por corte, 18s no total.** Abaixo de 4s o olho não termina de ler o
plano e a sequência vira videoclipe; acima de 8s deixa de ser montagem e volta
a ser uma sucessão de clipes. A água abre e fecha o ciclo porque é o plano mais
amplo dos quatro — sair de uma aérea e voltar para ela faz a emenda do loop ler
como respiro.

**Corte seco, sem fundido.** Fundido entre assuntos diferentes lê como vídeo
institucional; corte seco lê como observação. E o corte é o único que sobrevive
a um `<video>` em loop: um fundido na emenda exigiria que o último quadro
casasse com o primeiro.

> **A armadilha técnica da montagem:** os clipes vêm a 23,98, 25, 29,97, 50 e
> 100 fps, e o `concat` do ffmpeg recusa entradas que diferem em formato,
> resolução ou SAR. `fps`, `scale`, `setsar=1` e `format=yuv420p` em cada
> trecho **antes** do concat — e `setpts=PTS-STARTPTS` em cada um, senão o
> segundo trecho herda o timestamp do primeiro e o arquivo sai com 40s
> declarados e 18s de imagem.

---

## 34. O traço saiu do momento 4, e o barramento saiu de who-we-are

**O traço** era o traçado de aresta da própria refinaria, desenhado por
`stroke-dashoffset`. Tecnicamente correto e, **sobre esta foto**, ruído: a
refinaria já é toda aresta dura — tanque, escada helicoidal, torre de tocha —,
e sobrepor linhas brancas a isso duplica o desenho que a fotografia já tem. O
traço nasceu para a macro dos relés, que é superfície lisa com fio em curva, e
é lá que ele tem o que revelar.

**O barramento** de who-we-are era uma TRAMA — linha fina correndo por trás do
texto, organizando a página por grafismo. A regra 5 de clean diz o contrário:
*separação por espaço, nunca por linha*. Era o único lugar do site onde uma
linha decorativa ainda organizava uma página.

`build_traco.py`, os SVGs e `feixe()` continuam no repositório. Nada do que sai
é apagado.

---

## 35. O que entrou no lugar: movimento nas internas

Três peças, todas de custo zero em bytes, e nenhuma desenha nada — todas movem
o que já existe:

| peça | onde |
|---|---|
| parallax do cabeçalho (8% de curso) | as 6 páginas com foto de cabeçalho |
| parallax do fundo fotográfico | seções `.secao--foto` |
| números entrando um a um | onde a faixa aparece |

`data-progresso` **só** onde há fotografia: num cabeçalho liso o parallax não
teria o que mover, e o atributo custaria um `getBoundingClientRect` por quadro
em troca de nada — o módulo 7 mede todo elemento marcado, tenha ele o que
animar ou não.

**Os números não são contador animado.** O redline 8 proíbe "número que sobe
sozinho", e com razão: um número que corre é ilegível enquanto corre e sugere
precisão que não tem. O que se move é a **entrada** de cada bloco; o valor já
está escrito quando aparece.

Elementos atados à rolagem por página: home 5 · who-we-are 3 ·
past-performance 2 · capabilities/services/contact 1 · gallery 35.

---

## 36. `html.js` — a armadilha que o movimento novo abriu

Derivar `opacity` de `--p` tem um custo que não é óbvio: **sem JavaScript,
`--p` nunca é escrito e `clamp(0, ..., 1)` resolve em 0.** A faixa de números,
as colunas dos momentos e as legendas ficariam **invisíveis** — não degradadas,
invisíveis.

É a terceira vez que este projeto encontra a mesma armadilha (a intro e a frase
dela foram as duas primeiras, ambas registradas em style.css §5): **estado
inicial de animação que esconde conteúdo.**

A correção é o padrão `html.js`: uma linha inline no `<head>`, depois do CSS,
e **12 regras** passam a esconder só quando o JS existe para mostrar de novo.
Sem ele tudo nasce no estado final — a janela cheia, as portas fora de cena, o
texto visível.

> **Duas regras foram auditadas e NÃO precisavam de guarda:**
> `.galeria__figura` e `.prancha__item` já usavam `var(--p, 1)` — padrão **1**,
> não 0. Quem escreveu aquilo já tinha visto o problema. A guarda que eu tinha
> posto ali foi revertida.

---

## 37. `transition` numa propriedade atada à rolagem é sempre errado

`.filme__janela` tinha `transition: clip-path .05s linear`. Errado por duas
razões:

1. **De princípio:** a rolagem já É a linha do tempo do recorte — `--p` é
   reescrito a cada quadro. Uma transição por cima acrescenta 50ms entre o dedo
   e a imagem, que é exatamente a sensação elástica que um mecanismo atado à
   rolagem não pode ter.
2. **Prática:** numa aba que não recebe `requestAnimationFrame` a transição
   nunca avança, e o recorte fica congelado no valor inicial **mesmo com `--p`
   já em 0,70**. Foi assim que ela apareceu: `--abre` computava certo, a regra
   casava, e o `clip-path` continuava fechado.

Removida. Medido depois: `--p` 0 → `inset(21.3% 8%)`, 0,19 → `inset(10.65% 4%)`,
**0,38 → `inset(0%)`**, e assim fica até 1.

---

## 38. Estado

Quatro clipes, **10 MB de vídeo**. Home com 1664vh — quatro momentos de ~250vh
cada é o preço da sustentação que foi pedida.

0 quebradas · 0 órfãos · 0 fotografias repetidas · 0 conflitos de seletor ·
0 falhas na matriz de contraste · 0 regras que escondem conteúdo sem JS.

---

# PARTE V — a home virou um sistema, 2026-08-26 (terceira rodada)

Pedido do usuário depois de ver a dobra dos atuadores no ar: *"'The line does
not care how clever the code is' ficou perfeito, quero que você faça essa
seção se expandir com o vídeo do IHM no mesmo formato, e mais um vídeo
substituindo a seção que tem o gás. Você vai pôr as informações do site nesse
sistema — vídeo pequeno + um texto, vídeo grande + outro texto — três vezes."*

**O herói não foi tocado.**

---

## 39. A regra que mudou, e ela é do `design.md`

`design.md` §5 diz, com todas as letras:

> *"O mecanismo muda a cada volta. Repetir o filme três vezes transforma um
> momento em padrão e um padrão em tique — e o que o cliente elogiou foi a
> calma."*

O pedido é o oposto: **o mesmo mecanismo, três vezes.** A regra foi escrita
antes de existir uma dobra desse tipo no ar. O usuário viu a dobra pronta,
aprovou o formato e pediu a repetição — decisão dele, e ele é quem olha o site
com os olhos do cliente. Fica registrado que a regra foi revogada por decisão,
e não por esquecimento.

**O que a repetição custa, para poder decidir de novo:** a versão anterior
tinha quatro gestos (janela que abre, caixa que cresce, portas que correm,
parallax). Agora há **dois** — o filme, uma vez, e a unidade, três vezes. O que
impede o tique de se instalar é o **assunto**, que muda a cada volta, e o
texto, que carrega informação diferente em cada uma.

---

## 40. A unidade, e o que ela absorveu

Uma função só, `unidade()`, e as três saem dela. Cada uma tem **dois textos
que não dizem a mesma coisa**:

| | conteúdo | quando aparece |
|---|---|---|
| coluna | eyebrow → H2 → parágrafo → **CTA** | com a caixa pequena, ao lado |
| rodapé | a frase cinematográfica + a legenda | quando o vídeo tomou a tela |

| | vídeo | eyebrow | frase | leva a |
|---|---|---|---|---|
| 1 | atuadores | Eight disciplines | *The line does not care how clever the code is.* | capabilities |
| 2 | operador na tela | Method | *Screens an operator can read at three in the morning.* | services |
| 3 | engenheiro | Industries | *Oil and gas does not forgive a drawing that lies.* | past-performance |

**Os blocos de texto soltos entre os momentos saíram**, e não por economia: a
coluna de cada unidade **é** o bloco de texto, no mesmo formato de sempre e com
o mesmo destino. Manter os dois daria **dez** blocos de texto numa home cuja
regra número 1 é "uma ideia por dobra". Sobrou um solto, o de abertura, que
existe porque precede o primeiro vídeo e leva a who-we-are.

A home foi de 1664vh para **1365vh** com mais conteúdo dentro dos vídeos.

---

## 41. O que saiu, e para onde

- **A montagem perdeu `pc.mp4`** (3 cortes, 13,5s): ele virou o vídeo da
  unidade 3, e usar o mesmo clipe nos dois lugares seria a repetição que o
  usuário já reclamou uma vez.
- **A dobra da refinaria saiu.** Oil & gas não perde representação: `setor/
  oil-gas` continua em past-performance e é um recorte da mesma `gas.jpg`. A
  home passa a falar do vertical **por texto** — na coluna da unidade 3 e no
  bloco de governo. `momento/refinaria` saiu da geração.
- **`lente.js` parou de ser publicado.** A grade de setores foi para
  past-performance na rodada anterior e a lente ficou sem consumidor;
  `varredura.py` a acusou. O CSS e a função continuam no repositório.

---

## 42. Dois bugs de celular, e o segundo é o mais instrutivo

### 42.1 O vídeo cobria o texto

No celular eu tinha posto `.unidade__coluna { position: static }` mas deixado o
palco `sticky` com `height: 100vh` e o vídeo `absolute; inset: 0` dentro dele.
Resultado: o vídeo cobria a viewport inteira e a coluna renderizava **por
baixo**.

Em coluna única o mecanismo não existe, e forçá-lo é pior que perdê-lo: "ao
lado" não é uma posição possível numa tela de 528px. A dobra virou o que ela é
sem o gesto — texto, vídeo, frase, nessa ordem.

**E a frase ficou.** A primeira versão escondia `.unidade__rodape` no celular,
e com ela ia embora *"The line does not care how clever the code is"* — a
manchete da dobra. Esconder o gesto é uma coisa; esconder o texto é outra.

### 42.2 `:where()` — a guarda `html.js` estava vencendo demais

A guarda de §36 tinha um efeito colateral que só apareceu no celular:
`html.js .unidade__coluna` tem especificidade **(0,2,1)**, e o reset
`.unidade__coluna { opacity: 1 }` dentro de `@media (max-width: 900px)` tem
**(0,1,0)** — porque **media query não acrescenta especificidade**.

A guarda ganhava, e a coluna de texto do celular simplesmente não aparecia. E
nenhuma ferramenta acusa isso: a regra está escrita e está correta; ela só
perde.

A correção é `:where(html.js)`, que tem especificidade **zero**. A guarda volta
a (0,1,0), igual à regra base, e vence apenas **por ordem no arquivo** — que é
o comportamento que se espera dela. Doze guardas convertidas.

> **A lição generalizável:** uma guarda que sobe a especificidade não guarda,
> ela sequestra. Toda regra escrita depois passa a precisar da guarda também,
> e quem escrever a próxima media query não vai saber disso.

### 42.3 A ordem do documento é a ordem do celular

No desktop os três blocos são absolutos dentro do palco e a ordem no HTML não
importa. No celular tudo volta ao fluxo, e a ordem do documento vira a ordem da
leitura — então o HTML foi reescrito na ordem do celular: **coluna, janela,
rodapé**.

Reordenar por `order:` no flex resolveria o visual e **quebraria o teclado**:
`order` não muda a ordem de tabulação, então o foco continuaria percorrendo o
vídeo antes do texto.

---

## 43. Estado

Cinco vídeos (herói + montagem + três unidades), **11 MB**. Home com 1365vh.

0 quebradas · 0 órfãos · 0 fotografias repetidas · 0 conflitos de seletor ·
0 falhas na matriz de contraste · 0 regras que escondem conteúdo sem JS ·
redlines limpos.

**Continua sem verificação:** os quatro trilhos a 60 quadros com a inércia da
roda e o rodapé sticky, e o layout de DESKTOP desta rodada — a janela do
navegador de automação está em 528px e o `resize` é recusado pelo ambiente,
então tudo o que foi visto nesta rodada foi o ramo do celular. O desktop foi
verificado por geometria computada e pelas rodadas anteriores.

---

# PARTE VI — revisão de layout com a skill `impeccable`, 2026-08-26 (quarta rodada)

Pedido: *"utilize a skill impeccable; adicione uma seção entre o vídeo
principal, o .filme e os vídeos, com texto para adicionar mais espaço; intercale
vídeos à direita e à esquerda; revise a página home."*

A skill vive em `.claude/skills/impeccable/` e **não está registrada no
harness** — foi lida do repositório. `context.mjs` classificou o pedido como
refinamento estreito (`SCOPED_EXISTING_ALLOWED`) e apontou `design.md` como
autoridade incumbente. Playbook carregado: `reference/layout.md`, mais
`reference/craft-floor.md` antes de editar.

> **O detector mecânico rodou DEGRADADO** (`htmlparser2`, `css-select`,
> `css-tree`, `domutils` ausentes) e caiu para regex, devolvendo `[]`. Ele
> mesmo avisa que isso é subcontagem, não atestado de limpeza. A avaliação de
> layout foi feita à mão, como o playbook manda quando não há sub-agente.

---

## 44. A regressão que a revisão encontrou: o neutro quente havia sumido

Varredura de superfície na home antes desta rodada:

```
navy > BRANCO > BRANCO > escuro > escuro > escuro > escuro > off-white > escuro > escuro
```

Quatro dobras escuras seguidas — **1.010vh de campo escuro contínuo** — e, pior:

```
--quente usado na home?           False
--quente usado em alguma pagina?  []
```

**`--sup-q` não era usado em lugar nenhum do site.** Quando consolidei os
blocos de texto dentro das unidades na rodada anterior, levei junto a única
seção que o usava.

Isso não é um detalhe de paleta. `design.md` §0 identifica o neutro quente
como a **correção da causa raiz** do feedback do cliente:

> *"O site não tinha faixa média e não tinha nada quente... Quando o cliente
> pediu 'a tonalidade do universo do clp', ele não estava pedindo o laranja.
> Estava pedindo **luz**."*

Uma home sem a faixa quente devolve exatamente o problema que a revisão inteira
existe para resolver. Ritmo depois:

```
navy > BRANCO > BRANCO > QUENTE > escuro > BRANCO > escuro > escuro > escuro > off-white > escuro > escuro
```

---

## 45. As duas seções novas, e por que a copy não foi inventada

| | superfície | copy | de onde vem |
|---|---|---|---|
| entre a abertura e o filme | **`--sup-q`** | *"A better transmitter will not rescue a loop that was tuned wrong"* | who-we-are, "Strategy first, hardware second" |
| entre o filme e as unidades | branco | *"What changes between a refinery and a body shop is the process"* | past-performance, "Six sectors, one discipline" |

As duas frases já estavam escritas e verificadas no site. O redline 11 proíbe
afirmação não verificável, e a saída para isso não é escrever com cuidado — é
**não escrever**: reusar o que já passou pela verificação.

A segunda seção tem trabalho além de respirar: as três unidades são o mesmo
mecanismo três vezes, e quem não sabe que são três percebe repetição, não
sistema. Ela diz que são três e do que cada uma trata.

---

## 46. A alternância esquerda/direita, e o teste que a justifica

O **teste de meio-fechar os olhos** (squint test) é o primeiro item do playbook
de layout: *"com o detalhe borrado, ainda dá para identificar o elemento
primário, o secundário e os grupos principais, em ordem?"*

Com a caixa sempre do mesmo lado, as três unidades são **três dobras escuras
com a mesma silhueta** — o teste não distingue a 1 da 2 nem da 3. Elas
partilham mecanismo, superfície e altura de propósito (sistema se reconhece por
repetição), mas precisavam de um eixo de diferença.

`--lado-caixa` / `--lado-vazio` são a única coisa que o modificador inverte;
toda a aritmética de abertura continua uma só. Medido no render a 1920px:

```
unidade 1 (esq)  inset(21,13% 34,43% 21,13%  3,13%)   coluna em left: 1450px
unidade 2 (dir)  inset(21,13%  3,13% 21,13% 34,43%)   coluna em left:    0px
unidade 3 (esq)  inset(21,13% 34,43% 21,13%  3,13%)   coluna em left: 1450px
```

Espelhamento exato.

---

## 47. `ch` estava mentindo — e o defeito era de todo o site

O craft floor pede medida de corpo entre 65 e 75 caracteres. Medindo o render
real em vez de confiar no valor escrito:

| | escrito no CSS | caracteres reais por linha |
|---|---|---:|
| `.bloco__dir > p` | sem teto | **100** |
| `.corpo` | `62ch` | **104** |

`ch` é a largura do glifo **"0"**, e em Outfit ele mede 13,09px num tipo de
19,97px — enquanto o caractere **médio** do texto real da página mede 8,52px.
**A unidade é 54% mais larga que o caractere que ela deveria representar.**

A intenção de quem escreveu `62ch` estava certa; a unidade traía. E nada
acusa, porque o número no CSS parece perfeitamente razoável.

`em` é previsível: 8,52 / 19,97 = **0,4267em por caractere**.

| | novo valor | medido depois |
|---|---|---:|
| `.corpo` | `26em` (≈62 caracteres, a intenção original) | **73–74** |
| `.bloco__dir > p` | `30em` (≈70 caracteres) | **70–74** |

> **Nota de proporção:** os outros `ch` do arquivo foram conferidos e ficam
> **dentro** da faixa por coincidência — `.lead` a 46ch dá ~71 caracteres,
> `.bloco--centro` a 48ch dá ~74. Os medidores de manchete (20ch, 22ch, 24ch)
> continuam sendo quebras curtas de propósito. Só os dois fora de faixa foram
> mexidos.

Primeira tentativa desta correção usou `66ch`, que resolveu em **864px** — mais
largo que a própria coluna de 853px, ou seja, não limitou nada. O erro só
apareceu porque a verificação mediu o render em vez de conferir se a regra
tinha sido escrita.

---

## 48. O vão entre título e corpo era ZERO

Medido em quatro blocos: `margin-bottom` do h2 = 0, `margin-top` do parágrafo
= 0, distância real entre a base do título e o topo do texto = **0px**. O único
respiro era a entrelinha do parágrafo — sobra, não decisão, e num h2 de
entrelinha 1,05 sobra pouco.

`--s-4` (24px) entra como o degrau que separa DENTRO de um grupo. O que separa o
bloco da seção seguinte continua sendo `--sec-y` (160px): a razão entre os dois
é ~6,7x, e é ela que faz o título ler como parte do parágrafo e o bloco ler como
separado do resto.

---

## 49. As superfícies que o navegador desenha

O craft floor chama isto de *"o sinal mais barato de que uma página foi
construída em vez de montada, e o que os modelos pulam com mais confiabilidade"*.
Auditado: `::selection` ✓, foco ✓, `text-underline-offset` ✓,
`tabular-nums` ✓ — e **faltavam** barra de rolagem, cursor de texto e
`accent-color`.

Numa página que rola 1.400vh a barra é um elemento permanente da composição.
Entraram `scrollbar-color` (padrão) mais o par `::-webkit-` (Safari), pintando
os mesmos tokens; `caret-color` nos campos de contact.html, com variante para
superfície escura; e `accent-color` para caixa de seleção e rádio, que o §9 do
design.md prefere nativos a recriados.

---

## 50. Uma regra do craft floor NÃO foi aplicada, de propósito

O piso bane eyebrow acima de heading — *"this one is a ban, not a default: no
brief earns it back"*. Mas a regra de precedência da própria skill diz:

> *"The brief wins. Honor pinned aesthetics... Redirecting a clear brief toward
> your taste is failure."*
> *"Preserve the established visual world. A layout command changes structure
> inside it."*

`eyebrow → H2 → parágrafo → CTA` é a gramática de `design.md`, usada nas nove
páginas. O mundo visual incumbente vence o padrão da skill. Não mexido.

---

## 51. Estado

0 quebradas · 0 órfãos · 0 fotografias repetidas · 0 conflitos de seletor ·
0 falhas na matriz de contraste · 0 regras que escondem conteúdo sem JS ·
redlines limpos.

**Verificado no desktop desta vez** (a janela abriu em 1920px): a alternância,
o ritmo de superfície, a faixa quente, a medida de corpo e o vão de título.

**Continua sem verificação:** os quatro trilhos a 60 quadros com a inércia da
roda e o rodapé sticky. E fica registrado um incidente do próprio teste que
vale como evidência: forçar `preload="auto"` e `load()` nos quatro vídeos ao
mesmo tempo — anulando o `IntersectionObserver` — **congelou o renderer**. É a
demonstração involuntária de por que a regra de "um vídeo decodificando por
vez" existe.

---

# PARTE VII — vídeos, creme e reestruturação do topo, 2026-08-26 (quinta rodada)

Sete pedidos numa mensagem. **O herói não foi tocado.**

---

## 52. O bug que o usuário achou, e ele era meu

> *"O primeiro texto que aparece antes das fotos se integrarem completamente à
> tela não é clicável, então os botões que tem nela não funcionam."*

Causa, uma linha: `.unidade__coluna { pointer-events: none }`. Ela existe por
um bom motivo — a coluna é uma camada de texto **por cima** de um vídeo que vai
tomar a tela, e um link que desaparece mas continua capturando clique é uma
armadilha. Só que apliquei a regra à coluna **inteira** em vez de apenas ao
estado apagado, e levei o CTA junto.

**A correção não foi "ligar o `pointer-events`".** Mesmo clicável, o CTA na
coluna só existiria durante uma janela estreita de rolagem: o visitante teria
de parar no momento certo. Isso é pior que um botão que não funciona, porque
*parece* funcionar.

O CTA foi para o **rodapé da unidade**, que fica visível durante a
SUSTENTAÇÃO inteira — 81vh de rolagem com o vídeo parado, a fase mais longa e
mais estável. A coluna ficou só com texto, que foi exatamente o que o usuário
propôs.

### 52.1 `opacity: 0` não esconde de ninguém além do olho

O rodapé e a coluna trocam de estado por `opacity`, e opacidade zero **continua
capturando clique e continua na ordem de tabulação**. Sem guarda, o rodapé
receberia o clique de quem mirasse a legenda do vídeo atrás dele durante toda a
primeira metade do curso, e a coluna apagada roubaria o foco do teclado.

`data-abriu-em="0.32"` no HTML, o módulo 7 liga `is-aberta`, e uma classe faz
dois efeitos opostos: a coluna sai do alcance, o rodapé entra. Verificado por
teste de acerto real:

```
fechada  rodapé visibility: hidden   tabulável: false
aberta   rodapé visibility: visible  tabulável: true
         elementsFromPoint no centro do CTA -> ["A.cta", ...]   147x44px
```

---

## 53. Os dois vídeos trocados

**Method → `ihm` de verdade.** O corte anterior pegava 13,0→18,6s, que é a
parte em que a tela mostra *só* leitura numérica. Escolhi aquele trecho para
fugir da prosa em tcheco, e a conta de credibilidade continua valendo — mas o
efeito colateral foi que a dobra deixou de **parecer** o clipe do ihm: sem mão,
sem contexto, só números mudando. O usuário olhou e não reconheceu.

4,0→14,0s cobre a interface inteira: lista de programas, mão do operador,
diálogo, entrada na tela numérica. O tcheco volta junto, e o que o mantém
aceitável é o recorte não centralizar a tabela de texto, o scrim cobrir a faixa
mais densa, e a legenda dizer "machine HMI" sem afirmar autoria.

**Unidade 3 → `placassolares4`.** Travelling lento sobre a superfície da placa.
Ela fecha a sequência num vertical real e **muda o registro**: as duas unidades
antes dela são máquina e interface, em interior; esta é campo, em luz natural.
Depois de dois interiores seguidos, sair para fora é o que impede a sequência
de fechar abafada.

A frase mudou junto: *"Oil and gas does not forgive a drawing that lies"* era
do tanque e da tocha, e sobre uma placa solar seria legenda errada. Entrou
copy verificada de past-performance sobre geração e camada de supervisão.

---

## 54. O creme saiu

> *"A cor creme não funcionou no layout, apenas troque por branco ou um tom de
> branco."*

`.secao--quente` passa a pintar `--sup-2` (#F2F5F8). O token `--sup-q` fica em
`tokens.css` e a classe fica apontando para outro valor **em vez de ser
apagada**: o dia em que a faixa morna for testada de novo custa uma linha, e
não uma arqueologia.

**O que isso custa, registrado.** `--sup-q` era a resposta ao diagnóstico de
`design.md` §0 — o site saltava de quase-branco a quase-preto sem faixa média,
e o cliente, ao pedir "a tonalidade do universo do clp", estava pedindo **luz**.
`--sup-2` também é faixa média, só que **fria**: resolve a luminosidade e não a
temperatura. O ar entre branco e navy volta; o calor, não.

Contraste sobre `--sup-2` conferido, e é um fio melhor que sobre o quente em
todos os pares: corpo 15,91:1, eyebrow 6,00:1, título navy 11,28:1,
`--borda-ui` 3,71:1.

---

## 55. O topo virou o texto do site original

A abertura passou a ser a copy institucional que o usuário forneceu, na ordem
que ele pediu:

| dobra | | |
|---|---|---|
| 2 | branco | *Controls, automation and software* → a assinatura → o parágrafo |
| 3 | off-white | *Our mission* |

> **A LINHA DE ASSINATURA NÃO ENTROU EM CAIXA ALTA.** No original ela é
> "DEDICATED TO EXCEEDING YOUR NEEDS WITH UNWAVERING COMMITMENT", e o redline 9
> é explícito: caixa alta em bloco só em rótulos de até 3 palavras. Sete
> palavras em versal viram grito, e o tom de voz do §4 é declarativo. **O texto
> é o mesmo; a caixa muda.**

---

## 56. A dobra fundida

> *"What we actually do e os números vão para cima da seção what follows,
> mescle e refaça o layout para essa parte."*

Três seções viraram uma, e a fusão tem lógica de leitura: **o que fazemos →
em que escala → o que vem a seguir**. As duas primeiras se sustentam
mutuamente (a afirmação e a prova dela); a terceira abre as três unidades.

O que mantém as três legíveis como **três tempos de uma dobra**, e não como
três dobras coladas, é a razão entre o respiro interno e o externo:

```
entre as partes ..... --s-8   96px
entre as seções ..... --sec-y 160px      razão 1,67x
```

Abaixo de ~1,5x as três leem como massa só; acima de ~2x leem como seções
separadas e a fusão perde o sentido.

---

## 57. Plataformas → as oito disciplinas

A troca melhora a dobra por um motivo que vale registrar: a grade de
plataformas listava **ferramentas** (Rockwell, Siemens, Ignition), e ferramenta
é o que qualquer integrador tem. As oito disciplinas listam o que a empresa
**entrega**, que é a única coisa que a diferencia — e é a resposta direta ao
"what follows" três dobras acima.

As plataformas não se perdem: a grade continua inteira em capabilities.html.

Efeito colateral pego na verificação: a unidade 1 abria com "Eight
disciplines", que virou o título desta dobra. Duas dobras da mesma página
abrindo com a mesma frase leem como erro de montagem. A unidade 1 passou a
"Motor controls / From a single skid to a full lineup" — copy de capabilities,
já verificada, e que fala do clipe dela (atuadores).

---

## 58. Uma imagem para as duas seções de fecho

> *"Adicione uma única imagem para Federal contracting e Talk to an engineer
> assim como é em who we are."*

**"Uma única imagem" para as duas** é literalmente o componente `.dupla` —
duas seções escuras conectadas partilhando UMA fotografia, com o véu abrindo na
faixa livre entre os dois blocos de texto. who-we-are e past-performance já o
usam com este mesmo par de seções.

`--d-abre/--d-fecha` em 56–64%, os mesmos de who-we-are, porque a caixa contém
exatamente o mesmo par.

**A foto passou por medição antes de entrar**, e essa caixa tem histórico: a
nota de who-we-are registra que `baterias` foi a única do acervo a passar AA
nela. Medido na caixa da home (1440×1700):

| | véu .78 (fechado) | véu .50 (aberto) |
|---|---:|---:|
| `fiacao` (a nova) | 10,47:1 | **5,15:1** |
| `baterias` (referência) | 11,61:1 | 6,47:1 |

Passa nos dois. Um degrau abaixo da referência, e acima do piso de 4,5.

> **Nota de acervo:** o original é `pexels-salim-serdar-bali`, 2080×3120,
> **retrato** — e retrato é o formato de que uma caixa empilhada precisa. Sem a
> proporção por entrada em `DUPLAS` ele sairia recortado em 3:2 e jogaria fora
> metade da altura. É o mesmo negativo de `galeria/fiacao-textil`, e isso é o
> padrão e não exceção: `dupla/baterias` também é `galeria/baterias`, porque a
> galeria **é** o acervo de onde toda foto de seção sai.

---

## 59. Uma armadilha do próprio pipeline

`dupla/clp` voltou ao deploy sem ninguém pedir. Ele tinha sido removido numa
rodada anterior (a home deixou de ter dupla quando virou vídeo e momentos), mas
gerar `fiacao` chamou `duplas()`, que **regenera a lista inteira** — e os
arquivos apagados voltaram.

`varredura.py` pegou. Ficam duas lições: gerar um item de uma lista regenera
todos, e um arquivo apagado de `site/` sem ser desligado na receita volta na
próxima geração. A entrada foi comentada, não apagada.

---

## 60. Estado

```
0 quebradas · 0 órfãos · 0 fotografias repetidas · 0 conflitos de seletor
0 falhas na matriz de contraste · 0 caixa alta em bloco · redlines limpos
5 vídeos, 11 MB
```

**Verificado:** o teste de acerto do CTA (o bug reportado), a troca de
visibilidade coluna/rodapé, a ordem de tabulação, o contraste da foto da dupla,
a estrutura e o ritmo de superfície, e a dobra fundida no celular.

**Não verificado:** o layout de DESKTOP desta rodada — a janela do navegador de
automação abriu em 545px e o `resize` é recusado pelo ambiente. E os quatro
trilhos a 60 quadros com a inércia da roda, que continua sendo o item que só
uma sessão de rolagem real responde.

---

# PARTE VIII — o clipe do ihm, inteiro, 2026-08-26 (sexta rodada)

Pedido: *"'Screens an operator can read at three in the morning' — o vídeo aqui
precisa ser o `Videos/ihm.mp4`."*

A seção **já** apontava para `ihm.mp4`. Verifiquei os arquivos no ar antes de
mexer: nada estava desatualizado, os dois derivavam da fonte certa. A diferença
era outra — eu publicava **10s recortados** (`crop=3000:1688:420:180`) de um
original de **18,76s**.

Publicado agora: **18,70s, quadro cheio**, só o `scale` para 1600. 887 KB em
h264, 741 KB em VP9.

## 61. As três tentativas, e o que cada uma trocava

| trecho | o que ganhava | o que perdia |
|---|---|---|
| 13,0→18,6s | só a leitura numérica; número é neutro de idioma | a dobra deixava de **parecer** o ihm — sem mão, sem contexto |
| 4,0→14,0s | a interface e a mão, o reconhecimento de volta | trazia o diálogo modal junto |
| **0→18,7s** | **o clipe como ele é**, que foi o pedido | idem, e mais os 8s que eu havia cortado |

**O que a decisão aceita, registrado com a evidência na frente:** entre ~7s e
~11s o clipe mostra um diálogo modal em tcheco — *"Vývoj / Přenos souboru /
23 %"* e *"Náhled není možný!"*. Em tela cheia numa home de fornecedor federal
americano isso pode ler como uma máquina estrangeira com uma transferência
travada. A janela **2,2→6,8s** tem a interface e a mão **sem** o diálogo, e
continua disponível: trocar `ini` e `dur` na peça é a volta atrás inteira.

A decisão é do usuário, tomada depois de ver a crítica que levantou o ponto.

## 62. A legenda mudou junto com o clipe

Ela dizia *"Machine HMI showing live axis positions and feed rate"*. Os eixos e
a barra de avanço só aparecem a partir dos ~13s — com o clipe completo no ar, a
legenda prometia o que os primeiros treze segundos não mostram.

Passou a *"Operator at a machine HMI touchscreen, selecting a program"*, que é
verdade do início ao fim. A regra de legenda (design.md §7.1) vale para vídeo:
descreve o que se vê, e nada além — e nunca afirma que o sistema é da casa.

## 63. Estado

0 quebradas · 0 órfãos · 0 fotografias repetidas · 0 conflitos ·
0 falhas na matriz de contraste. Vídeo total: 12 MB.

---

# PARTE IX — a abertura, integrada, 2026-08-26 (sétima rodada)

Pedido com print (`mudanca/image.png`): *"essas duas seções ficaram estranhas,
precisamos mudar o layout delas para se integrarem; colocar alguma informação
como número no meio talvez já dê uma impressão mais clean; adicione
elementos."*

## 64. O que o print mostrava — três defeitos somados

As duas dobras de abertura tinham a **mesma estrutura em sequência** — eyebrow
à esquerda, título e parágrafo à direita — e a única diferença entre elas era o
tom do fundo. Liam como o mesmo bloco duas vezes.

| | |
|---|---|
| coluna esquerda | ~430px **vazios** sob um eyebrow de três palavras |
| vão morto | 65vh e 55vh de seção para ~40vh e ~35vh de conteúdo |
| diferenciação | duas estruturas idênticas coladas, nada para o olho separar |

A causa do primeiro: o split 4/8 do `.bloco` **supõe uma coluna direita alta**.
Funciona em toda página onde ela é; aqui ela tinha só título e um parágrafo, e a
esquerda ficou órfã.

## 65. O que integra as duas é o alinhamento, não uma moldura

Uma seção só, três movimentos, e no meio uma **faixa de plataformas no MESMO
grid 4/8**:

```
[ Controls, automation and software ]  [ título + parágrafo ]
[ Certified on                      ]  [ ● Ignition ● VTScada ● Canary
                                          Rockwell · Siemens · Schneider ]
[ Our mission                       ]  [ título + parágrafo ]
```

O rótulo da faixa cai na mesma linha de base dos dois eyebrows e os chips
alinham com os dois títulos. **Três rótulos à esquerda passam a ler como uma
coluna**, e não como dois blocos com um enfeite entre eles. A coluna esquerda
ganhou trabalho, que era o defeito raiz.

Altura: de 120vh em duas seções para **104vh numa**, com mais conteúdo.

### 65.1 Chips e não uma segunda faixa de números

O pedido sugeria "informação como número". Fui de **chips de plataforma** por
duas razões:

1. A home já tem uma faixa numérica (279+ / 158+ / 78+ / 150.000+ / 2000) na
   dobra fundida. Uma segunda faixa de números seria o *hero-metric template*
   duas vezes na mesma página — que o craft floor lista como padrão a recusar.
2. Os chips não são componente novo: `.marca` e `.marca--certificada` já
   existem e já carregam **estado** — ponto cheio = somos certificados aqui,
   chip liso = operamos aqui. É a mesma distinção que a escada de plataformas
   faz em capabilities, na versão compacta.

E eles **devolvem conteúdo que a home tinha perdido**: as certificações saíram
daqui quando a grade de plataformas foi substituída pelas oito disciplinas.

**Seis chips e não os oito de `PLATAFORMAS`.** AVEVA PI System e SQL Server
ficam de fora: são a camada de historiador, não "plataforma em que somos
certificados ou que operamos" no mesmo sentido — e o historiador já tem número
próprio na faixa de credibilidade. Seis leem como dois grupos de três; oito
leem como uma lista.

Contraste conferido: borda `--azul` sobre `--sup-2` = 3,17:1 (piso 3:1 para
elemento não-textual); tinta do chip = 15,91:1.

## 66. O respiro interno é diferente do da dobra fundida, e de propósito

| | vão entre partes | razão contra `--sec-y` |
|---|---:|---:|
| `.secao--fundida` | `--s-8` 96px | 1,67x |
| `.secao--intro` | `--s-7` 64px | 2,5x |

A diferença é de **assunto**. Na dobra fundida as três partes são coisas
distintas (o que fazemos, em que escala, o que vem a seguir) e pedem mais ar.
Aqui as três são a **mesma declaração em três tempos** — um vão maior as
separaria de novo, que é exatamente o defeito que a mudança conserta.

## 67. `.secao--quente` foi renomeada, porque o nome mentia

Ela pintava `--sup-2`, o off-white **frio**, desde que o creme saiu. Uma classe
chamada "quente" pintando frio é a espécie de pegadinha que custa meia hora a
quem ler o arquivo daqui a um ano. Quem pinta agora é `.secao--intro`, que diz
o **papel** e não a temperatura. O token `--sup-q` fica em `tokens.css` sem
consumidor, para a volta atrás custar uma linha.

## 68. Estado

Ritmo de superfície: `navy → off-white → escuro → branco → escuro ×3 →
off-white → escuro ×2`.

0 quebradas · 0 órfãos · 0 conflitos de seletor · 0 falhas na matriz de
contraste.

---

# PARTE X — as juntas, a aba dobrada, o logo e who-we-are, 2026-08-26 (oitava rodada)

Quatro pedidos numa mensagem só:

> *"Retire todos os sheet n / n do site. Existem duas abas de contact, contact e
> contact us, deixe apenas contact us (com retângulo em volta). É possível
> melhorar a qualidade do logo e deixar exatamente do jeito original? (melhorar
> na animação principalmente, está embaçado). A página home está pronta com
> essas alterações. A página who we are: precisamos refazer completamente."*

---

## 69. As juntas saíram inteiras, e a linha saiu junto com o rótulo

O pedido nomeia o **rótulo** — "SHEET 03 OF 05", em mono, na dobra entre duas
superfícies. A `.junta` era duas coisas coladas: uma **linha de eixo ISO 128**
desenhada por `clip-path`, e o rótulo na ponta em que o traço termina.

**Tirei as duas, e a regra é do próprio projeto.** `plano.md` §1 regra 5:
*"separação por espaço, nunca por linha — filete só onde carrega informação"*.
Quem carregava informação ali era o rótulo. Sem ele, uma linha tracejada na
emenda entre duas seções é ornamento — que é exatamente o que a regra 5 recusa.
Deixar a linha seria manter metade de um componente que perdeu a razão de ser.

O que saiu de onde:

| arquivo | o que mudou |
|---|---|
| `build_paginas.py` | `pagina()` não chama mais `juntar()` |
| `build_paginas.py` | `juntar()` e `_superficie()` ficam no arquivo, sem consumidor, com a nota de aposentadoria |
| `build_site.py` | os três `data-junta="inversa"` escritos à mão saíram |
| `fonte/css/style.css` | 130 linhas de `.junta` viraram uma lápide de 14 |

**A `.junta` também fazia uma coisa útil que agora não faz falta:** ela
acrescentava `reveal reveal--limpo` à seção, para o observador enxergá-la. Isso
existia *só* para o `clip-path` da linha poder disparar. Sem linha, a marca não
tem consumidor — e cada `.bloco` já traz o seu próprio `reveal`.

> **Nota de método:** `ferramentas/previa_junta.py` continua no repositório. É
> a prancha que mediu a receita da linha (26-8-3-8, período 45) e o histórico
> de por que a primeira, 22-5-2-5, lia como tracejado comum. Nada se apaga.

---

## 70. A aba de contato estava duas vezes no mesmo cabeçalho

O cabeçalho carregava **"Contact"** entre os sete links e **"Contact Us"** com
moldura à direita. Os dois apontam para `contact.html`, a ~5 cm um do outro.

Ficou o **botão**, e não a aba, porque ele é o único item do cabeçalho com
moldura: trocar o botão pela aba rebaixaria o CTA da barra a um link igual aos
outros seis. Foi o que o usuário pediu, e é o que o desenho quer.

**`MENU` não mudou.** Ele alimenta também a navegação do rodapé, onde
`contact.html` é um link de página como outro qualquer — e lá não há duplicata,
porque a coluna "Contact" ao lado carrega telefone e e-mail, não a página.
**Quem filtra é a barra**, dentro de `nav()`:

```python
abas = [(h, t) for h, t in MENU if h != 'contact.html']
```

**O `aria-current` foi para o botão.** Sem isso, em `contact.html` nenhum item
do cabeçalho seria a página corrente, e a barra deixaria de anunciar onde o
visitante está. Vale para o painel do celular também, que tem o mesmo par.

---

## 71. O logo embaçado: um erro de 1,65x que aparecia em TODO monitor

Este é o achado da rodada, e não era o que parecia. Não era compressão, não era
a arte, e não era o DPR do avaliador.

**O `srcset` do lockup era por DENSIDADE, dimensionado para o slot errado.**
`marca_lockup()` emitia `1x/2x/3x` calculado sobre `width="339"` — que é a
largura com que o **rodapé** rende o lockup. A **intro** rende
`min(72vw, 560px)`. Descritor de densidade não sabe disso: ele troca de arquivo
quando o DPR troca, nunca quando o slot muda.

Medido no navegador, a 1440 px de viewport:

| DPR | arquivo escolhido | px de tela | ampliação |
|---:|---|---:|---:|
| 1 | 339×96 | 560 | **1,65x** |
| 2 | 678×192 | 1120 | **1,65x** |
| 3 | 1017×288 | 1680 | **1,65x** |

**A mesma ampliação em todos os três.** Era um erro fixo — todo mundo via o
mesmo borrão, em qualquer tela.

### 71.1 E o arquivo "3x" era resolução falsa

O recorte do lockup na arte do cliente tem **946×268**. Pedir altura 288 fazia
`gravar()` **ampliar 1,07x** com LANCZOS e gravar 1017×288 de pixel inventado.
Um arquivo que se anuncia como 3x sem ter a informação de 3x é pior que não
existir: o navegador o escolhe e paga a banda por nada.

`gravar()` agora **recusa** qualquer altura acima da nativa e grita no build.
Foi o guarda que revelou que `logo-marca-288.png` era falso pelo mesmo motivo —
a marca isolada também tem 268 px de altura nativa.

### 71.2 A correção não foi consertar o srcset: foi apagá-lo

Medido no build, os três knockouts:

| arquivo | dimensão | peso |
|---|---:|---:|
| `logo-completo-branco-96.png` | 339×96 | 17,4 KB |
| `logo-completo-branco-192.png` | 678×192 | 39,7 KB |
| **`logo-completo-branco-268.png`** | **946×268** | **25,3 KB** |

**A nativa tem 7,8x mais pixel que a de 96 e pesa 1,5x — e pesa MENOS que a
intermediária.** Não é anomalia: a arte é chapada em 7 cores (`build_marca.py`
quantiza para elas antes do flood fill), e PNG comprime região chapada quase de
graça. Quem engorda os derivados é o anti-aliasing que o LANCZOS introduz ao
reduzir.

Ou seja: **o srcset gastava banda para entregar menos resolução.**

Com um arquivo só não há descritor para errar. O rodapé (141 px de largura)
recebe uma redução limpa em qualquer DPR, e a intro sai de 1,65x de ampliação
para **0,60x de redução** em DPR 1 e **1,18x** no pior caso (DPR 2). 946 px é o
teto real da arte — não existe versão vetorial, e `logo/logonova.png` é
pixel-idêntico ao `logo-original.png` que já estava no acervo (conferido por
`ImageChops.difference`: bbox `None`).

### 71.3 O que a limpeza levou junto

`build_marca.py` ganhou uma **varredura de órfãos** em `site/brand/`: tirar um
nome de `PUBLICADOS` não tirava o arquivo do deploy, e os três PNGs do srcset
morto teriam ficado lá — **125 KB que nenhum `<img>` pedia**. Agora o publicador
remove o que ele mesmo produziu e deixou de publicar. Não toca em
`apple-touch-icon` nem nos `icon-*`, que saem de outro script.

Saldo: o logo ficou nítido **e** o deploy de marca caiu de 95,7 KB para 38,6 KB.

---

## 72. Who We Are, refeita do zero

O pedido era refazer a página com a informação do site antigo. O diagnóstico
achou três defeitos, e só um era de copy.

**1. Ela repetia `services.html` inteira.** A dobra *"How we work / Strategy
first, hardware second"* mais `diagrama()` com os quatro passos era, palavra por
palavra, a dobra *"How the work runs / Strategy first, hardware second"* de
services. Duas páginas do mesmo site com o mesmo título e o mesmo componente. O
método pertence a services, que descreve o **engajamento**; who-we-are descreve
a **casa**. O diagrama saiu daqui.

**2. Ela não vendia nada.** Havia o que a empresa é (desde 2000, certificada,
federal) e a missão. No meio não havia **um argumento** — nenhuma razão para
preferir esta casa a outra com as mesmas certificações.

**3. O melhor argumento do cliente estava fora do site.** O site antigo tem uma
seção inteira — *"Senior control experts know things they do not teach in
school"*, o transmissor de $45.000, o loop que se retuna por anos sem sucesso —
e a migração tinha ficado só com a **manchete**, no filme da home. O
raciocínio, que é a parte que convence, não estava em lugar nenhum.

### 72.1 A estrutura nova

| dobra | superfície | afirmação |
|---|---|---|
| cabeçalho | navy | "We are problem solvers" |
| o histórico | branco | 26 anos + os cinco números |
| **o argumento** | **escuro + foto** | **o transmissor de $45.000** |
| o retorno | off-white | os cinco ganhos, em `.dados` |
| a missão | branco | citação + os setores em chips |
| dupla | escuro ×2 | governo + CTA, inalterada |

Ritmo: `navy → branco → escuro → off-white → branco → escuro ×2`. Alterna em
toda emenda — que é o que substitui a junta como marcador de folha.

**Nenhum componente novo e nenhuma classe nova.** Tudo o que a página usa já
existia: `.bloco`, `.pilha`, `.citacao`, `.numeros`, `.dados` (de services),
`.marca` (dos chips da home) e `.dupla`. O sistema já tinha as peças — o que
faltava era o argumento.

### 72.2 O que entrou do texto do cliente, e o que eu escrevi

O parágrafo do transmissor entra **quase inteiro**, e as duas mudanças são de
forma:

- *"This statement may upset some"* saiu. É hedge, e o tom do site pede
  declarativo — a frase seguinte já assume o desconforto sem anunciá-lo.
- **O fecho é novo, e é a única coisa ali que o cliente não escreveu.** O
  original termina no **diagnóstico** ("por que o loop não se deixa tunar") e
  nunca diz o que se faz no lugar — ou seja, para o comprador ele para uma frase
  antes de vender. Feedforward, controle por razão e cascata são as três
  respostas de livro para as três perturbações que o próprio texto enumera, na
  mesma ordem em que ele as enumera. Não há invenção: é o nome das estratégias.

**A cifra fica em $45.000** porque é a do cliente. Arredondar para "um
transmissor caro" perderia o que faz o parágrafo morder.

Os cinco ganhos vêm do site antigo — *"revenue growth, cost reduction, market
expansion, enhanced partner collaboration, streamlined production cycles"* —,
que é a lista certa escrita na língua errada: são os cinco substantivos de
qualquer folheto de consultoria, e o **redline 10** recusa exatamente esse
registro. Cada um foi reescrito para o que ele **é na planta**. "Revenue growth"
não diz nada; *"more product through the same asset, because the loop holds
setpoint instead of hunting around it"* diz a mesma coisa e pode ser conferido.

`.dados` e não `diagrama()`: os cinco são **paralelos**, não uma sequência.
Numerá-los treinaria o olho a procurar uma ordem que não existe — a mesma razão
que tirou os cards 01/02/03 de `oferta()`.

### 72.3 O cabeçalho continua com o véu FECHADO, e é decisão

As outras cinco páginas de conteúdo passam `classe='cabecalho--foto'`, que abre
o véu de `.72/.92` para `.52/.86` e põe a fotografia como **assunto**. Aqui não
dá: `cabecalho/quem-somos` sai de `foto.png`, a foto autoral do cliente, que tem
**1127 px de largura** — num cabeçalho de 1440 px ela é **ampliada 1,28x**.

Ela é o **assunto certo** (dois engenheiros lendo a tela de uma máquina; é
literalmente "who we are") e a **resolução errada** para ficar exposta. Sob o
véu fechado ela é textura, e textura ampliada 1,28x ninguém vê. Trocar por uma
foto de banco de 5.000 px resolveria a nitidez e perderia o assunto — numa
página chamada "Who We Are", uma engrenagem genérica é pior que uma foto macia
da própria equipe.

---

## 73. Dois vãos que eram ZERO, e agora são regra

O mesmo defeito que a quarta rodada registrou entre título e corpo estava em
mais dois pares, e os dois apareceram nesta página assim que ela foi montada:

| par | vão medido | vão agora | por quê esse degrau |
|---|---:|---:|---|
| `.lead + .pilha` | 0px | `--s-5` 40px | o lead se fecha, a pilha desenvolve: dois movimentos |
| `.citacao + .pilha` | 0px | `--s-5` 40px | idem |
| `.pilha + .cta` | 0px | `--s-6` | entrou na regra que já governa `p + .cta` |

`--s-5` e não os `--s-4` da regra de título: acima, o par é título e corpo —
duas partes da mesma frase. Aqui são duas afirmações, e o degrau seguinte da
escala é o que as separa sem soltar uma da outra.

**A causa raiz era inline.** who-we-are vinha resolvendo o primeiro par com
`style="margin-top: var(--s-5)"` escrito na marcação. Inline não é regra: a
próxima página que usasse o par nasceria com o defeito de volta, e ninguém
saberia por quê. E os três parágrafos do argumento, escritos como `.corpo`
soltos, saíram como **um bloco de texto só** — `.corpo` só declara medida, não
vão. Quem tem vão é `.pilha`, que é o componente que existe para isso.

---

## 74. Um chip liso mede 1,78:1 na borda, e passa

Os seis setores entram como `.marca` liso, sem o ponto de `.marca--certificada`.
Medido sobre branco:

| | valor |
|---|---:|
| rótulo `--tinta` #1A1A1A | **17,40:1** |
| borda `--filete-forte` rgba(0,0,0,.24) → #C2C2C2 | **1,78:1** |
| borda `--azul` (só em `.marca--certificada`) | **3,47:1** |

O 1,78 está abaixo do piso de 3:1 do WCAG 1.4.11 **de propósito**: aquele piso
vale para o que **identifica** um controle ou o estado dele. O chip liso não é
controle e não tem estado — o nome do setor está escrito dentro, em 17,40:1, e a
moldura só agrupa. É o mesmo chip liso que a dobra de abertura da home já usa.
Quem carrega estado é `.marca--certificada`, e essa tem borda `--azul`, acima do
piso — que é por que a distinção entre as duas se enxerga.

---

## 75. Estado

```
0 quebradas · 0 órfãos · 0 fotografias repetidas · 0 conflitos de seletor
0 falhas na matriz de contraste · 289 referências, 294 arquivos
marca no deploy: 95,7 KB -> 38,6 KB
```

**Verificado no navegador:** a barra com uma aba de contato só (e o painel do
celular), o rodapé com a arte nativa, o lockup a 0,60x de redução em vez de
1,65x de ampliação, as sete dobras de who-we-are com o `reveal` forçado, o ritmo
de superfície da página inteira e a ausência de qualquer junta nas nove páginas.

**Não verificado:** who-we-are com o `reveal` REAL disparando — a aba de
automação abre em segundo plano (`visibilityState: "hidden"`) e o Chrome congela
`requestAnimationFrame` e o `IntersectionObserver` ali. É a mesma limitação que
`doit.md` Fase 8 já registra, e é por isso que a intro também não roda na
automação: `main.js` §5 encerra na hora quando a aba não está visível.

---

# PARTE XI — o argumento em vídeo, os cinco momentos e o "why us", 2026-08-26 (nona rodada)

Três pedidos, todos em who-we-are:

> *"Adicione uma animação de aparição paralaxe na seção 'Why it matters who
> does the work' e mude a foto de fundo, talvez coloque um vídeo. Na seção
> 'What the work returns' refatore o layout com uma forma mais interativa em
> momentos de cada um dos five things. Adicione uma seção mesclada a our
> mission para dizer a quem está olhando 'why us' — crie um novo segmento para
> esse elemento."*

---

## 76. O fundo virou vídeo, e o clipe já estava no disco

`pc.mp4` — o engenheiro na estação — estava no acervo **sem consumidor** desde
a segunda rodada: era um dos quatro cortes da montagem da home, saiu de lá para
virar a unidade 3, e a unidade 3 virou solar. Ficou parado.

E ele é o assunto **exato** desta dobra, que é a razão de ter sido o escolhido
e não um clipe bonito qualquer. A seção se chama *"Why it matters **who does
the work**"* e argumenta que a estratégia de controle vale mais que o
instrumento — ou seja, que o trabalho é de **engenharia** e não de compra. Todo
o resto do acervo mostra **equipamento**; este mostra alguém projetando.
`faixa/ferramental`, a foto que ele substitui, mostrava ferramental sob uma
prensa: processo industrial genérico, não quem o pensa.

### 76.1 Contraste medido nos DEZ quadros, não no pôster

Um fundo em movimento tem de passar em **todo** quadro, não no que a gente
escolheu para a medição. Um quadro por segundo dos 9,7s publicados, compostos
sob o véu `.55/.35` de `.secao--foto`, caixa 1400×1050, média local 12×12:

| | pior quadro (q02) | melhor (q09) |
|---|---:|---:|
| fundo mais claro do miolo | #40556C | #3F5369 |
| branco — título e citação | **7,68:1** | 7,92:1 |
| corpo `--sobre-3-2` | **4,78:1** | 4,93:1 |
| eyebrow #B9D2EA | **4,93:1** | 5,08:1 |

Passa AA em todos os dez, e a **variação é de 0,15** no corpo. Isso não é sorte:
o plano é contínuo e a luz não muda, que é precisamente o que torna este clipe
utilizável como fundo. Um clipe com corte ou com mudança de exposição
reprovaria em algum quadro e passaria no pôster — que é a medição que quase
todo mundo faz.

### 76.2 O custo, e o que ele pagou

549 KB (h264) / 279 KB (VP9), contra ~180 KB dos três AVIF de
`faixa/ferramental`. Numa página interna com `preload="none"`: só quem chega na
dobra baixa. `faixa/ferramental` saiu da geração — 7 arquivos e 1,0 MB que
`varredura.py` acusou na primeira passagem depois da troca.

---

## 77. Paralaxe é diferença de velocidade, não uma entrada bonita

O que a dobra tinha era um `reveal` único: eyebrow, título, citação, três
parágrafos e CTA apareciam **todos no mesmo instante e com o mesmo
deslocamento**. Isso é um fade, e um fade não tem profundidade — nada nele diz
que uma coisa está mais perto do olho que outra.

Agora cada camada tem curso próprio, e o curso **cresce com a proximidade**:

| camada | curso | entra em |
|---|---:|---:|
| vídeo de fundo | 5% de cada lado do centro | sempre |
| rótulo + título | 34px | p = .00 |
| citação | 46px | p = .06 |
| pilha de parágrafos | 58px | p = .12 |
| CTA | 70px | p = .18 |

O vídeo anda em **porcentagem** (é a caixa inteira) e o texto em **pixel** (são
linhas): porcentagem numa linha de texto muda de curso conforme a tipografia
quebra. É a mesma escolha que `.cabecalho__foto` e `.numeros` já faziam.

### 77.1 A armadilha do `data-progresso`, e ela é de altura

O módulo 7 tem **duas leituras**, escolhidas pela altura do alvo: elemento mais
alto que a janela mede o curso do `sticky` (`--p` só começa a andar quando o
topo dele encosta no topo da janela); mais baixo, mede a **travessia inteira**.

A seção tem ~1006px. Numa janela de 950 ela cai no primeiro caso — e a aparição
aconteceria com a dobra **já lida**. Por isso quem carrega o atributo é o
`.bloco` (~600px), e a seção mantém o dela só para o vídeo. **Dois
`[data-progresso]` aninhados**, cada um medindo o que precisa.

E o `.bloco` perdeu o `reveal`: os dois juntos dariam dois mecanismos
disputando a mesma `opacity`.

### 77.2 A borda que estava escondida por sorte de gradiente

`.secao--foto[data-progresso] .secao__foto` deriva 3,5% para cada lado com
`inset: 0` — ou seja, **descobre a borda**. Não aparece porque o degradê do véu
termina em `--sup-3` chapado nos 22% de cima e de baixo, justo ali.

Com 10% de curso a sorte acaba. `.secao--video .secao__fundo` declara a folga:
`inset: -6% 0` com `height: 112%` — 6% de cobertura contra 5% de curso, 1% de
margem. A regra antiga fica como está: mexer nela sem medir as outras cinco
páginas que a usam seria trocar um defeito invisível por um visível.

---

## 78. Os cinco ganhos viraram cinco momentos

`.dados` é o componente certo para "o que sai com você" em services — uma lista
de entregáveis que se lê de cima a baixo — e é o **errado** para cinco
afirmações que pedem para ser lidas uma a uma.

### 78.1 Duas coisas que NÃO foram feitas, e as duas têm histórico

**Não é um painel `sticky`.** Era a resposta óbvia, e ela já existiu neste site,
em past-performance, e **saiu a pedido**: *"esse estilo não combinou com o
site"* — carrossel de tela cheia é vocabulário de apresentação de produto, e o
resto do site se lê como documentação técnica. Repetir o padrão aqui seria
reintroduzir o defeito com outro nome.

**Nada é apagado.** É a forma mais fácil de fazer um item "ser o momento", e ela
custa contraste: texto a 60% de opacidade sobre o off-white cai abaixo de
4,5:1, e um dos cinco ficaria legível enquanto quatro não. Aqui **nada fica
menos legível** — o item do momento *ganha* ênfase, os outros continuam em
tinta cheia. É a diferença entre destacar e esconder.

### 78.2 O que o item do momento ganha, e as três coisas já eram vocabulário

| gesto | de onde vem |
|---|---|
| régua de 2px que se **desenha** na borda de cima | `.diagrama__passo` |
| número passa a `--azul-txt` | o acender de `.capacidade` |
| campo levanta para `--sup-1` | elevação por fundo, §8.1 |

### 78.3 Duas fontes decidem o momento, e a segunda vence

- **rolagem** — `data-passos="5"` faz o módulo 7 publicar `data-n` de 0 a 4
- **ponteiro** — `:hover` e `:focus-within` no item

O ponteiro vencer é o que torna a peça interativa de fato: quem só rola vê os
cinco momentos na ordem; quem aponta assume o controle.

**`data-passos` existia desde a primeira versão do módulo 7 e nunca teve
consumidor** — foi escrito para o painel de setores, que saiu. Esta é a primeira
peça a usá-lo, e usa exatamente como o comentário dele previa: *"o CSS não
precisa saber contar, e o JS não precisa saber desenhar"*.

**Cinco regras explícitas, sem `abs()`.** `abs()` em CSS só chegou ao Chrome 133
e ao Safari 15.4, e uma peça de conteúdo não é lugar de apostar em suporte
recente. `data-n` + `:nth-child` resolve sem aritmética de custom property.

---

## 79. "Why us" — mesclado, e não seguinte

A diferença é estrutural. As duas partes moram numa seção só (`.secao--fundida`),
no **mesmo grid 4/8**, com os dois rótulos caindo na coluna da esquerda um sob
o outro. Dois blocos de mesma estrutura em sequência leem como o mesmo bloco
duas vezes — e a coluna esquerda ficaria vazia sob um eyebrow de duas palavras.
É o mesmo conserto que a dobra de abertura da home levou na sétima rodada.

`--s-8` (96px) entre a missão e o porquê, e não os `--s-7` de `.secao--intro`:
lá as três partes são a mesma declaração em três tempos; aqui são duas coisas
distintas — o que a casa persegue, e por que contratá-la.

### 79.1 O formato é pergunta e resposta, e a razão é de repetição

A página já tem **duas** listas rotuladas — `.retorno` acima e `.credencial` no
bloco de governo. Uma terceira leria como a mesma peça pela terceira vez. Aqui
o rótulo é a **objeção** que o comprador já tem na cabeça, em mono como toda
anotação deste site, e o texto é a resposta.

### 79.2 As quatro respostas são verificáveis no próprio site

Requisito e não capricho: o cliente é fornecedor federal, e o `plano.md` §8.3
proíbe afirmação não verificável.

| objeção | onde a resposta se confere |
|---|---|
| "Support ends when the job ends" | Arcadia e os três anos, em past-performance |
| "The code belongs to the integrator" | o bloco de entregáveis de services |
| "You will write it your way" | Daimler e BMW, em past-performance |
| "You will sell us what we don't need" | o argumento e os cinco ganhos, acima |

A quarta amarra na própria página — que é o que faz ela **fechar** em vez de
terminar.

---

## 80. O botão de pausa virou plural, e ganhou memória

O fundo em vídeo encaixa nas mesmas três condições do **WCAG 2.2.2** que o
herói: movimento que começa sozinho, dura mais de 5 s e divide a tela com outro
conteúdo. Duas mudanças no módulo 14:

**Plural.** `querySelector` no singular teria funcionado por acidente — as duas
páginas têm um vídeo de fundo cada — e teria quebrado em silêncio no dia em que
uma tivesse dois. O par agora é declarado por `data-pausa="<id>"`, e não por
proximidade no DOM: amarrar por "o vídeo mais próximo" é o tipo de acoplamento
que sobrevive à primeira remontagem do HTML e morre na segunda.

**`data-parado`, e este é o defeito que quase passou.** Um fundo de seção é
`[data-momento-video]`: sai da tela, o módulo 13 pausa; volta, o módulo 13 dá
play. Sem uma marca de decisão, **quem apertou pausa e rolou até o rodapé
encontraria o vídeo tocando de novo na volta** — ou seja, o mecanismo que o
2.2.2 exige duraria até a próxima rolagem. O módulo 13 agora respeita a marca,
na entrada em tela e na volta da aba.

`data-heroi-video` saiu do herói junto: com o gancho da pausa apontando para um
`id`, ele ficou sem leitor nenhum. Gancho morto no HTML é o que faz o próximo
leitor procurar o código que o consome durante dez minutos.

---

## 81. Estado

```
0 quebradas · 0 órfãos · 0 fotografias repetidas · 0 conflitos de seletor
0 falhas na matriz de contraste · 285 referências, 290 arquivos
vídeo total: 13,1 MB  ·  #FDC500 fora do logo: 0  ·  border-radius: 0
```

**Verificado no navegador:** as sete dobras da página, a aparição em camadas com
`--p` real, o item do momento em `.retorno` (por `data-n` e por ponteiro), o
segmento "why us" no grid fundido, o botão de pausa nas duas páginas — incluindo
a memória de `data-parado` — e o herói da home depois da troca de gancho.

**Não verificado, e é a mesma limitação de sempre:** o vídeo *tocando*. A aba de
automação abre em segundo plano (`visibilityState: "hidden"`), e ali o Chrome
congela `rAF` e o `IntersectionObserver` e não decodifica mídia. O que se vê nas
capturas é o pôster sob o véu — que é justamente o estado que a medição de
contraste cobriu quadro a quadro. **E o layout de celular**: o `resize` da janela
continua sendo recusado por este ambiente (`innerWidth` fica em 1920 depois do
pedido), então as duas media queries novas — `.retorno` em 1023px e `.porque` em
767px — estão escritas e não medidas na tela.

---

# PARTE XII — o vazamento, a cena presa e a cobertura, 2026-08-26 (décima rodada)

Cinco pedidos. Os quatro primeiros fecham who-we-are; o quinto abre capabilities.

---

## 82. O vídeo vazava, e a causa era a folga que eu tinha acabado de criar

> *"O vídeo precisa ser do mesmo tamanho do filtro azul, atualmente está
> vazando."*

Estava. E a causa é a correção da rodada anterior: para o parallax não
descobrir a borda, `.secao--video .secao__fundo` ficou **12% mais alto que a
seção** (`inset: -6% 0`). O véu `::before` é `inset: 0` e cobre só a seção.
Sobravam **6% de vídeo cru** para fora do azul, em cima e embaixo.

**Cortar, e não encolher.** Sem a folga o parallax volta a descobrir o canto —
que era o defeito anterior. `overflow: clip` na seção faz a caixa pintada ser
exatamente a da seção, e o véu e o vídeo passam a ter o mesmo tamanho.

`clip` e não `hidden`, com `hidden` antes como reserva: é a mesma lição que o
`<body>` já paga na §1 — `overflow: hidden` num eixo faz o outro computar para
`auto` e transforma o elemento em contêiner de rolagem, que é o assassino de
`position: sticky`. Não há sticky nesta seção hoje; `clip` garante que pôr um
amanhã não vire meia hora de investigação.

Verificado na tela: a caixa de layout do vídeo continua 117px acima e 4px
abaixo da seção (a folga), e `overflow` computa `clip/clip` — ou seja, nada
disso pinta.

---

## 83. O clipe virou `placasSolares.mp4`, e ele é o mais caro do acervo

Troca pedida direto. `pc.mp4` (o engenheiro na estação) volta a ficar sem
consumidor, e a nota da nona rodada — que explicava por que ele era o assunto
exato daquela dobra — fica como registro do que se trocou.

**12s de 26,26s, começando em 2,0.** O fim do clipe **funde para preto**: o
quadro em 25s é preto chapado, e num fundo em loop isso apagaria a dobra por
dois segundos a cada volta.

### 83.1 A conta que mudou o orçamento do encode

Uma travelling aérea sobre uma grade regular e fina de células fotovoltaicas é
o **pior caso de um codec**: alta frequência espacial em movimento constante,
sem uma área chapada para o compressor economizar.

| | h264 |
|---|---:|
| 1600px CRF 30 (o padrão dos momentos) | **2.959 KB** |
| 1440px CRF 32 | 1.890 KB |
| **1280px CRF 34** | **1.176 KB** |
| 1280px CRF 36 | 919 KB |

1600/30 daria **3 MB num fundo de seção** — mais que o herói, que é a primeira
dobra do site inteiro. E o véu paga a diferença: aqui ele fecha em .55 no miolo
e compõe .71 na lateral. Artefato de CRF 34 não sobrevive a isso.

> É `plano.md` §3.4 na direção contrária. Lá está escrito que *"véu leve
> esconde MENOS artefato"*, e foi por isso que o herói precisou de CRF baixo.
> Aqui o véu é pesado, então o CRF pode subir. A regra é a mesma; o sinal é que
> inverte.

**O VP9 foi descartado pelo build** (4.781 KB contra 2.959 do h264), e o
`<source>` do WebM saiu do HTML junto — um WebM maior não é neutro: o navegador
fica com a primeira `<source>` que sabe tocar, então Chrome e Firefox baixariam
mais que o Safari.

**O pôster ganhou qualidade própria** (`q_poster`). `-q:v 3` é quase sem perda e
é o certo para o herói, que é o LCP e aparece sem véu. Um fundo de seção vive
sob 55–71% de navy e só aparece nos milissegundos antes do vídeo chegar: 208 KB
para entregar detalhe que a camada por cima apaga. Em `-q:v 7`, **121 KB**.

Contraste re-medido no encode **final**, quadro a quadro (12 quadros): pior
caso `#41556E` — branco 7,64:1, corpo **4,76:1**, eyebrow 4,90:1. Passa.

---

## 84. A cena presa — e eu tinha argumentado contra ela

> *"'What the work returns' precisa ficar antiscroll até o scroll ir de output
> a cycle time; ele precisa passar por todos e só depois pode mudar de seção."*

**Na nona rodada eu recusei o painel preso aqui**, citando past-performance,
onde ele existiu e saiu a pedido (*"esse estilo não combinou com o site"*). O
usuário viu a versão sem prisão e pediu a prisão. Decisão dele, com a
alternativa na frente — e fica registrada assim.

**O que a de past-performance tinha de errado e esta não tem:** lá o painel
**trocava a fotografia inteira** a cada passo, e era isso que lia como
apresentação de produto. Aqui a cena é uma lista de documentação parada, e o que
muda é qual linha está acesa.

### 84.1 A conta do trilho

```
altura = 100vh + 5 x 55vh = 375vh      medido: 3544px numa janela de 945
curso  = altura - 100vh   = 275vh      medido: 2599px -> 520px por passo
```

55vh por item: a 100 o visitante rola uma tela inteira para trocar uma linha de
uma lista que já leu, e a peça vira pedágio; a 30 os cinco passam num gesto só
e a prisão não se justifica.

**A rolagem continua nativa.** Não há `wheel` sequestrado nem biblioteca — é um
trilho alto com um palco `sticky`. Teclado, `End`, barra e âncora seguem
funcionando, e é isso que faz "antiscroll" aqui não custar acessibilidade.

### 84.2 Três defeitos que a prisão criou, e os três consertados

**1. Dois `data-progresso` medindo a mesma coisa.** A `.retorno` tinha o dela
de quando a seção era de altura normal. Presa, ela não atravessa mais nada: o
retângulo fica parado e o `--p` que ela mediria é uma **constante** — o item
aceso travaria no primeiro. Quem mede agora é a seção; a lista não mede nada. Um
alvo, uma medida.

**2. A especificidade virou de lado, em silêncio.** Com as regras de rolagem
lendo o `data-n` da seção elas subiram para (0,4,0), e o `:hover` de (0,3,0)
passou a **perder** — o efeito continua existindo, só nunca acontece quando
importa. `.secao--presa[data-n]` na frente devolve (0,5,0). É a mesma armadilha
que `.contato__valor` custou uma vez neste arquivo.

**3. O eyebrow ficava atrás do nav.** `top: 0` põe as primeiras linhas da cena
sob a barra fixa e opaca — durante os cinco passos inteiros. O herói e a
cobertura podem colar em 0 porque o que passa por baixo do nav ali é
**fotografia**; aqui é texto. `top: var(--nav-altura)` com
`height: calc(100svh - var(--nav-altura))`.

### 84.3 A prisão tem de se explicar sem legenda

Regra 10 de clean: se um elemento precisa de uma frase ensinando a usá-lo, ele
sai. Quem fica preso sem saber por quanto tempo **rola mais forte**. O contador
`03 / 05` e os cinco segmentos, três acesos, dizem quanto falta — e é isso que
torna a prisão legível em vez de irritante. Ambos com `aria-hidden`: o leitor de
tela recebe a lista inteira de uma vez e a encenação, para ele, não acontece.

**E a entrada escalonada saiu.** Ela existia para os cinco chegarem em ordem
enquanto a seção atravessava a janela — e a seção deixou de atravessar. Numa
cena parada os cinco precisam estar legíveis no primeiro quadro. O
escalonamento não se perdeu: mudou de eixo, de tempo de entrada para `data-n`.

`prefers-reduced-motion` desliga a prisão inteira. É o único gesto do site que o
visitante **não consegue interromper rolando** — prender a tela de quem pediu
menos movimento é o pior caso possível.

---

## 85. A foto da dupla desenterrou um defeito que a anterior escondia

> *"Troque a imagem de fundo das últimas duas seções."*

A troca é de uma linha. O que ela revelou não: **a faixa livre do véu estava no
lugar errado**, e estava havia rodadas.

`--d-abre: 56%` / `--d-fecha: 64%` era número herdado de uma versão anterior
desta página. Medido agora **no navegador**, sobre a página como ela é (dupla de
1431px):

| zona | posição |
|---|---|
| texto do bloco de governo | 11,2% – 39,3% |
| **faixa livre de verdade** | **39,3% – 61,6%** |
| texto do CTA | 61,6% – 88,8% |

O véu abria em 56% e a rampa de fechamento ia até 70% — **em cima do eyebrow e
do título do CTA**, que começam em 61,6%. A fotografia aparecia debaixo de
letra, e só ali.

`baterias` era escura e chapada, então ninguém via. `prototipagem` tem uma
protoboard **branca**: o defeito virou ilegível na hora, e apareceu na primeira
captura.

**44% e 54% são os números certos.** A rampa de abertura começa em 40 (o governo
terminou em 39,3) e a de fechamento termina em 60 (o CTA só começa em 61,6).
Nenhuma letra sob véu aberto, dos dois lados.

### 85.1 O override que eu quase deixei no arquivo

A primeira tentativa foi `--veu-d-meio: .88`, para compensar o branco da
protoboard. Ele funcionava — 4,83:1 — e estava **compensando a faixa mal posta,
não a foto**. Com a faixa no lugar, medido nas zonas de texto reais:

| véu | pior fundo | branco | corpo | rótulo | |
|---|---|---:|---:|---:|---|
| .72 | #455C73 | 6,93 | 4,31 | 4,44 | reprova |
| **.78 (o padrão)** | #364E67 | 8,60 | **5,35** | 5,51 | passa |
| .88 | #1D3854 | 12,03 | 7,49 | 7,71 | escuro sem precisar |

Fica o padrão: **menos um override**, mais contraste do que a versão com .88
entregava, e a fotografia visível. É o lembrete de sempre — quando um valor de
sistema precisa de exceção, vale conferir se o problema não é outro parâmetro
fora do lugar.

### 85.2 E o enquadramento entrou junto

Sem ele a protoboard cai a ~49% da altura da fonte, e a faixa livre pegava só
fundo preto: a foto pagava contraste **e** não aparecia. `duplas()` ganhou uma
**janela** opcional `(fração, âncora)` — um recorte vertical feito antes do
recorte de cobertura. Com `(.75, .16)` o objeto vai para ~60% da fonte, que cai
dentro de 44–54% na caixa. Amplitude na faixa livre: **157**.

> **Nota de assunto, e ela fica aqui de propósito:** o objeto é uma montagem de
> bancada em protoboard, não equipamento industrial instalado. Sob o bloco de
> credenciais federais isso pede a regra de sempre com mais rigor — o `alt`
> descreve o que se vê e para aí, e nenhuma legenda visível acompanha, porque a
> foto é fundo de seção e não figura.

---

## 86. A cobertura por quadrados, em capabilities

> *"Sobre ela vamos adicionar uma animação de quadrados que cobrem gradualmente
> a foto ao scrollar; a tela fica fixa e avança até estar totalmente coberta, lá
> então a seção seguinte aparecerá."*

**A peça é uma transição de seção que acontece NA TELA em vez de na emenda.** A
fotografia não sai rolando: é apagada em blocos, e o que sobra quando o último
cai já é a superfície da seção seguinte.

**Por isso os quadrados pintam `--sup-2`** — o off-white de "Platforms and
certifications", logo abaixo. Quando fecha, a tela inteira já é aquela seção, e
o `sticky` solta sem troca de cor visível. Branco, cinza ou navy fariam a cena
fechar numa cor que some no quadro seguinte, e a costura apareceria.

### 86.1 A conta de cada quadrado

```
--t: clamp(0, (p - o * .72) * 8, 1)

o = 0    abre em p .000, fecha em .125
o = 1    abre em p .720, fecha em .845
```

A cobertura **fecha em ~85% do curso**, e os 15% que sobram são sustentação com
a tela cheia. Não é folga desperdiçada: é a garantia do pedido. Sem ela o último
quadrado cairia no mesmo quadro em que o `sticky` solta, e quem rolasse rápido
veria a foto aparecendo na saída.

`* 8` é a inclinação: mais rápido e os quadrados **piscam**; mais lento e a
cobertura vira um fade cinza em vez de blocos.

**`scale` e não `opacity`**, e é o que faz ler como bloco: nas quatro
referências os quadrados são chapados desde o primeiro quadro em que existem.
`opacity` entregaria 84 retângulos cinzentos a 40%, que é névoa.

### 86.2 A ordem é calculada no build, e o padrão é de baixo para cima

`Math.random()` no cliente daria uma trama diferente a cada carga — e um efeito
que nunca é o mesmo **não pode ser conferido**. E sortear no cliente exigiria JS
escrevendo 84 estilos; assim o JS do site continua publicando `--p` e nada mais.

```
peso = (1 - linha_normalizada) * 0.55  +  ruido * 0.45
```

A parcela de posição garante a direção (as referências crescem do rodapé); a de
ruído garante que a fronteira nunca seja uma linha reta subindo — que faria a
peça ler como persiana e não como quadrados.

**84 = 12×7 no desktop e 14×6 no celular.** Os dois fatoram 84, então a mesma
marcação cobre as duas grades sem um único quadrado órfão.

### 86.3 Dois defeitos pegos na tela

**A foto era `lazy`.** Numa cena `sticky` a fotografia é o primeiro pixel que o
visitante vê ao chegar — e `loading="lazy"` só a pede quando ela entra na
janela, ou seja no mesmo quadro em que a cena prende. Medido: em `--p = 0` o
palco estava **branco**, com a legenda boiando sozinha. `ansioso=True`.

**A legenda era branca com sombra**, como legenda de vídeo — e esta fotografia é
um painel **claro**. Branco sobre ela não se lê em canto nenhum, e sombra não
salva texto claro sobre fundo claro; só suja. Virou **placa**: pinta `--sup-2`
(a mesma cor dos quadrados) e escreve em `--tinta`, **15,91:1**, sem depender de
nada da fotografia. E ganha sentido de peça — sendo do tom dos quadrados, lê
como o primeiro quadrado já colocado.

---

## 87. Platforms and certifications, refeita

> *"Esta seção precisa ser refeita de acordo com o design do nosso site e nossas
> mudanças."*

**O defeito não era a escada.** Ela é a única peça do site que usa notação de
engenharia de controle para carregar informação — contato energizado =
certificados, contato aberto = operamos. O problema é que ela punha as **oito**
plataformas num rail só, e o visitante tinha de **deduzir** o que o contato
cheio significa. A regra 10 não deixa consertar isso com uma legenda.

**O conserto é estrutural: dois rails rotulados.**

| rótulo | degraus | |
|---|---|---|
| Certified on | 3 energizados | Ignition, VTScada, Canary |
| Fluent in | 5 abertos | Rockwell, Siemens, Schneider, PI System, SQL Server |

O rótulo do grupo **é** a tradução da notação. A escada para de precisar de
legenda porque o título já diz o que o estado quer dizer.

E o bloco cai no padrão de **três rótulos empilhados** na coluna esquerda, que é
o mesmo conserto de coluna órfã que a abertura da home e o "why us" de
who-we-are já levaram.

`.bloco__dir > .escada { margin-top: 0 }`: `--gap-bloco` existe para separar a
escada do bloco de texto acima dela. Dentro da coluna, ao lado do próprio
rótulo, ele vira buraco — medido, o rótulo ficava ~90px acima do primeiro
degrau, e a coluna esquerda voltava a parecer órfã, que é o defeito que partir a
escada tinha ido consertar.

**A foto da cena mudou junto, e era hora.** A anterior era a macro de um módulo
de 4 relés SRD-05VDC-SL-C — acessório de Arduino, com "4 Relay Module"
serigrafado na placa — e tinha uma legenda escrita para **não** chamar aquilo de
CLP. Uma página chamada "Eight disciplines, one contractor" ilustrada por um
módulo de bancada. A nova (`quadrados/final.jpg`, 7008×4672) é o produto:
interior de painel montado, CLPs Siemens em trilho, disjuntores, réguas de
bornes e chicote.

---

## 88. Estado

```
0 quebradas · 0 órfãos · 0 fotografias repetidas · 0 conflitos de seletor
0 falhas na matriz de contraste · 284 referências, 289 arquivos
#FDC500 fora do logo: 0 · border-radius: 0
fundo-solar: 1.204 KB (era 3.030) · pôster 121 KB (era 208)
```

Saíram do deploy: `momento/rele` (9 arquivos), `dupla/baterias` (2 que
sobravam), `fundo-projeto` (mp4, webm e pôster).

**Verificado no navegador:** o corte do vídeo (`overflow: clip/clip`, com a
folga de 117px do parallax confirmada em layout e nenhuma pintura fora), o clipe
solar sob o véu, a cena presa passo a passo (contador 01→05, régua, item aceso
em cada passo, e a soltura só depois do quinto), a cobertura em p≈0,3 e p≈0,9, a
placa da legenda legível sobre a foto e sobre o off-white, e os dois rails de
plataformas.

**Não verificado, e é a limitação de sempre:** vídeo tocando (aba em segundo
plano) e **layout de celular** — o `resize` continua sendo recusado por este
ambiente. As media queries novas (`.retorno` em 1023px, `.porque` em 767px,
`.cobertura__grade` em 14×6 e `--presa-passo` em 42vh) estão escritas e não
medidas na tela. Nesta rodada o Chrome de automação também passou a estourar o
timeout de captura com frequência nas duas páginas com vídeo — as capturas que
saíram foram tiradas entre estouros.

---

# PARTE XIII — o fecho da cobertura, 2026-08-26 (décima rodada, adendo)

> *"Está foda. Após os quadrados brancos aparecerem, precisamos inserir algo na
> tela no espaço preenchido, para criar movimento, pode ser um texto curto mas
> profundo."*

## 89. Os últimos 15% do curso eram tela vazia

E eram vazios **de propósito**: a sustentação existe para garantir que a
cobertura fechou antes de o `sticky` soltar (§86.1). Mas sustentar uma tela
off-white chapada é pedir ao visitante que role no escuro. O espaço estava lá;
faltava o que pôr nele.

A cena passou de **250vh para 300vh** — os 50vh a mais são exatamente o tempo da
frase. Encurtar a cobertura para caber não servia: são 84 quadrados, e abaixo de
~120vh a formação da trama vira um piscar.

## 90. A frase é o que acabou de acontecer na tela

```
You can see the hardware.
You are paying for the judgement.
```

O painel — a coisa que dá para apontar — **acaba de ser apagado na frente do
visitante**. A primeira oração chega em cima desse apagamento; a segunda nomeia
o que ficou. O mecanismo e a copy dizem a mesma coisa: a peça não ilustra o
argumento, ela o executa. É a razão de a frase morar aqui e não servir em
nenhuma outra dobra do site.

Ela é irmã das outras duas — *"Good control strategy beats more expensive
instrumentation"* (herói) e *"Senior control experts know things they do not
teach in school"* (o filme, e o argumento de who-we-are). Mesma família, uma por
página. E **não repete** a abertura de "Platforms and certifications" logo
abaixo, que fala de software de terceiros: aqui o assunto é hardware contra
julgamento.

## 91. O movimento são dois tempos, e a legenda entrega o lugar

| | curso |
|---|---|
| legenda da foto apaga | .62 → .78 |
| *"You can see the hardware."* | .78 → .88 |
| *"You are paying for the judgement."* | .86 → .96 |
| as duas paradas, e a cena solta | .96 → 1.0 |

**A sobreposição de dois centésimos é de propósito:** sem ela a segunda oração
parte depois de a primeira assentar, e as duas leem como dois eventos. Com ela,
a frase **se escreve**.

**Começa em .78 e não antes, e a razão é de contraste.** A cobertura fecha em
~.845; antes disso ainda há fotografia na tela, e esta é uma foto CLARA. Entrando
em .78 a frase assenta sobre campo praticamente fechado, e a partir de .845 é
chapado — `--tinta` sobre `--sup-2`, 15,91:1.

**A legenda sai porque a fotografia saiu.** Ela descreve o painel; passados ~80%
do curso não há painel nenhum, e uma legenda de uma foto que não existe é ruído
— ruído que disputa a atenção com o dístico que acaba de chegar no centro. O
curso dela é o espelho do da frase, e o cruzamento em .78 faz disso **uma
entrega, e não dois eventos**.

Verificado no navegador: em `--p .32` a legenda está em 1 e as duas orações em 0;
em `--p .99` a legenda está em 0 e as duas em 1.

## 92. Dois detalhes de tipografia

**36ch e não 22:** cada oração cabe numa linha só e a frase lê como um **dístico**
— duas linhas de peso igual. A 22 a segunda quebrava em duas e a primeira ficava
em uma, o que dá uma estrofe torta de três linhas. `text-wrap: balance` saiu
junto: não há o que balancear quando cada linha é uma oração inteira.

**Dois `<span>` e não uma frase só:** elas chegam em tempos diferentes, e o que
se anima é cada uma. `display: block` num `<span>` dentro do mesmo parágrafo
mantém a frase **inteira** para quem lê com leitor de tela e **separada** para
quem anima. Mesma solução do `.rodape__headline`, que quebra o fecho do site em
palavras pela mesma razão. Sem `aria-hidden`: é conteúdo de verdade.

## 93. Estado

```
0 quebradas · 0 órfãos · 0 fotografias repetidas · 0 conflitos de seletor
0 falhas na matriz de contraste
```

**Não verificado:** o celular (`resize` continua recusado — a frase cai para
`--fs-h3` em 18ch, escrito e não visto) e a cena a 60 quadros com o vídeo da
outra página, que continua estourando o timeout de captura deste ambiente.

---

# PARTE XIV — o paralaxe fora, o scroll mais rápido, e o celular medido enfim, 2026-08-26

> *"Mudei a frase, agora sim. Preciso que volte na tela de who we are: não quero
> o paralax na seção 'Why it matters who does the work', deixe como estava
> (mantenha o vídeo atual). Na seção seguinte, What the work returns, deixe o
> scroll mais rápido — estamos perdendo tempo no site com o scroll travado."*

## 94. A frase estava num arquivo gerado, e o próximo build a apagaria

O usuário reescreveu o fecho da cobertura **direto em `site/capabilities.html`**.
Aquela pasta é saída de `build_site.py`: o build seguinte teria sobrescrito o
arquivo inteiro, e a frase sumiria sem nada acusar.

Portada para `ferramentas/build_site.py` antes de qualquer outra coisa desta
rodada. A dele:

```
Anyone can see the panel.
We understand what's behind it.
```

É melhor que a minha (*"You can see the hardware. / You are paying for the
judgement."*): nomeia **quem entende**, e não só o que se paga. O apóstrofo
virou `&rsquo;`, que é a convenção tipográfica do site.

> **A lição é do processo, não do texto:** `CLAUDE.md` já avisa que `site/` é
> gerado, e mesmo assim foi ali que a edição aconteceu — porque é ali que se vê
> o resultado. Vale conferir `site/` contra a fonte sempre que o usuário disser
> que mexeu em alguma coisa.

## 95. O paralaxe saiu inteiro, e levou junto um defeito que tinha criado

A dobra do argumento teve, entre a nona e a décima rodada, uma aparição em
paralaxe: cada camada com curso próprio (34/46/58/70px) mais 10% de deriva no
vídeo. Saiu tudo — a seção perdeu o `data-progresso`, então o fundo também
parou de derivar. Era a leitura literal do pedido: *"não quero o paralax na
seção"*, não "na metade de cima dela".

**E isso desfaz o vazamento pela raiz.** A deriva exigia o vídeo 12% mais alto
que a caixa para não descobrir a borda — e foi essa folga que vazou para fora
do véu na décima rodada, consertada com `overflow: clip`. Sem curso não há
folga: o vídeo volta a `inset: 0`, e não há o que vazar nem o que cortar. O
`clip` fica como garantia barata, não como conserto.

O vídeo fica, como pedido. O bloco volta ao `reveal` simples — como era antes da
nona rodada. 118 linhas de CSS viraram 63.

## 96. O scroll travado custava quase três telas

| | antes | agora | |
|---|---:|---:|---|
| passo por item (desktop) | 55vh | **30vh** | |
| curso travado (desktop) | 275vh | **150vh** | −45% |
| curso travado (≤1023px) | 210vh | **115vh** | −45% |

A queixa era justa e a conta explica: a 55vh a cena custava **275vh de rolagem**
— quase três telas para ler cinco linhas que já estão todas visíveis.

O raciocínio de antes continua valendo nas duas pontas, só com o meio
deslocado: a 100vh o visitante rola uma tela inteira para trocar UMA linha e a
peça vira pedágio; abaixo de ~20vh os cinco passam num gesto só e a prisão
deixa de se justificar. **30 é onde o item ainda tem batida sem cobrar por
ela.**

## 97. O celular, medido pela primeira vez — e três defeitos nele

A janela de automação abriu em **360×740** por conta própria. É a primeira vez
neste projeto que dá para ver o layout móvel, e as três media queries que eu
vinha registrando como "escritas e não medidas" foram conferidas de uma vez.
Duas estavam erradas.

### 97.1 A cena presa não cabia — e escondia o próprio conteúdo

```
conteúdo do palco ....... 1437px
altura disponível ....... 676px   (740 menos o nav)
sobra ................... -761px
```

O palco é `overflow: clip`: o que não cabe **desaparece**. O que não cabia era o
cabeçalho, o contador e dois dos cinco itens. **Uma cena presa que esconde o
próprio conteúdo é pior que não ter cena** — o visitante fica travado rolando
uma tela que não mostra o que ele está travado para ver.

Abaixo de 1024 a seção volta a ser seção: altura automática, palco em fluxo,
respiro normal. O item aceso **continua acendendo** conforme a rolagem —
`data-n` não depende do `sticky`, só do progresso —, então o gesto sobrevive sem
a prisão. Contador e régua saem, porque medem uma prisão que não está mais lá.

1024 e não 768: é o mesmo ponto em que `.retorno` empilha, e é ali que o item
engorda o suficiente para a lista estourar a tela.

### 97.2 A grade da cobertura estava com os fatores trocados

`14 x 6` dava célula de **26x123px** — barras verticais, numa peça que se chama
"quadrados". A conta de qual par usar: célula quadrada quando `larg/c = alt/r`
com `c * r = 84`; a 360x740 isso dá `r = 2,06c` e `c² = 40,9`, ou seja **c ≈ 6**.
Com `6 x 14` a célula fica **60x53** — a mesma leitura do desktop (120x136).

### 97.3 O que já estava certo

`.porque` em uma coluna (310px), os chips de setor quebrando em três linhas, a
placa da legenda legível sobre a foto, e o `.retorno` empilhado com o número à
esquerda e nome/frase na segunda coluna.

## 98. Estado

```
0 quebradas · 0 órfãos · 0 fotografias repetidas · 0 conflitos de seletor
0 falhas na matriz de contraste
```

**Verificado a 360x740:** a dobra do argumento sem paralaxe e com o vídeo, a
lista de retorno sem prisão, o "why us" em coluna única, a cobertura em
quadrados, e a placa da legenda.

**Continua sem medição:** o desktop desta rodada — a janela abriu em 360 e o
`resize` segue sendo recusado. O que mudou no desktop é a remoção de regras
(paralaxe) e um número (`--presa-passo`), os dois conferidos por computed style
e pela conta; nenhum layout novo entrou.

---

# PARTE XV — services vira uma página, 2026-08-27

> *"a pagina services precisa começar com um video, tipo o heroi da home. a
> proxima sessao Engagements, precisa ser refeita(layout) para se adequar ao
> site, verifique as informações que esta seçao diz e veja se faz sentido. a
> proxima sessao In every scope esta boa, mas precisa de uma foto de fundo e
> animaç~eos de hover no texto. How the work runs e platformns precisam ser
> mesclado em uma unica sessão. Your design or ours esta boa e nao vejo
> ajustes pra agora, vale voce checar. use a skill impeccable para fazer o
> trabalho. Adicione imagens e videos que ainda não foram usados no site e
> estao disponiveis aqui no repo."*

## 99. O diagnóstico que abriu a rodada

Antes de qualquer pedido, o levantamento de services contra as outras cinco:

| | imagens no corpo | cena | peça |
|---|---:|---|---|
| past-performance | 6 | `obras` | mímico |
| capabilities | 2 | `cobertura` (84 quadrados) | — |
| who-we-are | 1 + vídeo | cena presa | — |
| index | 0 + 5 vídeos | 3 unidades + filme | — |
| **services** | **1** | **nenhuma** | malha, no rodapé de um CTA |

Seis seções, seis `.bloco` idênticos, zero movimento. Era a única interna sem
um momento em que a página faz alguma coisa — e é a página em que o comprador
decide.

## 100. O acervo de vídeo não usado tinha seis clipes, e cinco eram solar

Levantado contra `build_video.py`: sobravam `pc.mp4`, quatro aéreas de fazenda
solar e `elemnetotecnologicodeesteira.mp4`.

**`pc.mp4` foi descartado, e é a perda que dói.** As notas da nona rodada o
chamam de *"o projeto antes da máquina"*, que é literalmente a tese de "How you
buy the work" — o melhor casamento de assunto do acervo inteiro. Mas **todos os
quadros mostram um diálogo do Autodesk Inventor avisando que a licença
expirou**, e o cliente é fornecedor federal. Existe recorte que esconde o
diálogo — `crop=3840:1215:0:945`, medido e conferido em contato-folha —, só que
ele custa a metade de cima do quadro e o assunto continua errado: CAD mecânico
não é controle.

Entrou `elemnetotecnologicodeesteira.mp4` — módulo fotovoltaico numa esteira
sob lâmpadas de teste. É o sexto assunto solar do site, o risco que `design.md`
§5.5 registra, e a compensação é a **cor**: sob véu navy é o único clipe do
acervo com luz quente. Lê como inspeção de linha, não como mais uma fazenda.

**O corte 0,6s → 6,6s é medido.** A esteira anda sem parar, então não há par de
emenda perfeito. Medida a diferença média absoluta entre quadro de entrada e de
saída para todo par com 5s ou mais, **todos** os melhores pares dão exatamente
6,0s de distância — é o passo entre um módulo e o próximo. 0,6 → 6,6 é o melhor
deles: 7,57 de diferença média contra 50,19 do pior par.

## 101. A simulação errou o véu do herói, e o render corrigiu

Este é o registro mais útil da rodada, e a lição é do método.

Compondo o véu sobre quadros amostrados na mão, a zona do H1 dava
rgb(84,108,130) e `.55` parecia bastar. Medido no screenshot do Chrome — véu
real, escala real, o quadro que o navegador de fato parou — o fundo é
rgb(82,120,152), e a conta desaba:

| elemento | simulado | RENDER |
|---|---|---|
| H1 (grande) | 5,39:1 | 4,73:1 passa (piso 3:1) |
| apoio | 4,68:1 | **4,03:1 REPROVA** |
| trilha | ~4,75:1 | **4,14:1 REPROVA** |

> **Quando os dois discordam, quem vale é o render.** A amostragem na mão pegou
> o pior quadro de uma grade de sete; o vídeo tem 180.

E a saída não foi fechar o véu inteiro: chapar tudo em .68 apagaria os módulos e
as lâmpadas no alto do quadro, que já estavam confortáveis. Entrou um **segundo
gradiente embaixo** (.30 sobre .55, compondo .685 no pé), que é o gesto que
`.heroi__veu` já faz no topo com o scrim do nav, espelhado. Reconferido no
render: H1 11,51 · apoio 5,25 · trilha 5,94.

**Sem eyebrow no herói**, e também por medição: nenhum dos dois azuis de accent
serve como texto pequeno ali — `--azul-luz` 2,50:1, `#B9D2EA` 3,50:1, branco
5,45:1. Branco é a única cor que passa, e poria uma segunda coisa branca a
competir com o H1. A trilha logo abaixo já diz "Home / Services".

## 102. Engagements: a auditoria de conteúdo achou uma coluna sem lastro

O pedido incluía *"verifique as informações que esta seçao diz e veja se faz
sentido"*. Cruzadas as três colunas com o site antigo, past-performance e
capabilities:

| coluna | lastro |
|---|---|
| New system | documentado — Daimler, BMW, solar, Houston |
| **Retrofit & migration** | **nenhum, em lugar nenhum do acervo** |
| Annual support | documentado — Arcadia FL, Houston |

E `"tested in our shop"`, no passo 03 do método, também não aparece em lugar
nenhum: nada no site afirma que a i3 tem galpão próprio.

Faltava ainda o inverso: **"Control panel services and process
troubleshooting"** é o que a ficha da WestRock registra em past-performance, e
não estava nesta página.

**Decisão do usuário: quatro colunas.** Retrofit fica, afirmado pelo cliente e
não pelo acervo — registrado aqui como tal, pela mesma razão que `design.md`
§7.1 proíbe legenda que afirma obra não verificável. Panel services entra, com
texto tirado da ficha da WestRock em vez de escrito do zero.

## 103. A matriz virou quatro derivações de um barramento

A queixa não era da matriz — ela é o formato certo, e o comprador lê uma linha
para comparar ou uma coluna para entender uma oferta. A queixa era que ela não
se parecia com o site. Então mudou a **gramática**, não a estrutura: barramento
horizontal no topo, um ramo caindo em cada coluna, terminal aberto no pé do
ramo. Mesma família da `.escada`, sem ser a mesma peça — lá é série entre dois
rails, aqui é paralelo pendurado num barramento. A forma passa a dizer o que o
texto já dizia e a tabela não mostrava.

**Dois defeitos que só o render mostrou:**

1. **Layout automático mentia sobre as larguras.** Os `width` em porcentagem
   viram sugestão, e as quatro colunas de texto longo engoliam a coluna de
   critério: ~400px de vão entre o rótulo em mono e a primeira célula, com o
   rótulo órfão do próprio dado. `table-layout: fixed` resolve, e de quebra
   deixa as quatro rigorosamente da mesma largura — que é o que "paralelas"
   tem de parecer.
2. **`vertical-align: bottom` serrilhava a fileira de nomes.** Cada nome
   flutuava conforme quebrasse em uma ou duas linhas, logo abaixo de quatro
   terminais perfeitamente alinhados. Pelo topo eles nascem na mesma linha,
   colados no próprio terminal.

`min-width: 928px` **não foi escolhido**: a peça empilha a 1023 (breakpoint do
sistema), o último viewport que mostra a matriz é 1024, e ali o container útil
vale 1024 − 2×48 = 928.

## 104. "In every scope": a fotografia decidiu a superfície da seção

O pedido era foto de fundo numa dobra off-white. Medido sobre
`faixa/gabinete` (média local 12x12, p2 dos blocos — o **mínimo absoluto não
discrimina**: toda fotografia tem um bloco estourado, e três fotos diferentes
davam o mesmo número):

| véu | corpo | secundário | accent | amplitude |
|---|---|---|---|---|
| navy .55/.35 | 7,18:1 | **4,61:1** | 4,61:1 | **46,5** |
| off-white .72 | 8,28:1 | 3,28:1 | 3,00:1 | 44,9 |
| off-white .80 | 10,15:1 | 4,02:1 | 3,68:1 | 32,1 |
| quente .78 | 9,59:1 | 3,80:1 | 3,47:1 | 35,3 |

**Nenhum véu claro serve.** O secundário reprova em toda linha, e fechá-lo até
passar apaga a fotografia. A seção vira escura. O ritmo continua alternando:
herói escuro → engagements branco → esta escura → método off-white → fecho
escuro.

`faixa/gabinete` sai de `raymond-sime-KDkU44ikiko-unsplash.jpg`, 7008×4672 — a
foto existia desde 20/08 como `galeria/painel-clp`, **num mosaico de 400-800px**.
É a primeira vez que ela sai em tamanho de seção. O assunto é o argumento: os
quatro entregáveis descrevem exatamente este gabinete, e a lista fica por cima
da coisa que ela documenta.

## 105. E o rótulo teve de mudar de família, não de claridade

O desktop passava e o **celular não** — `object-fit: cover` recorta outro pedaço
da foto e ali o chicote claro cai atrás da lista. Medido a 390:

| tinta | p98 | máximo |
|---|---|---|
| branco | 4,77:1 | 4,29:1 |
| `--tinta-2` #B9D2EA (o rótulo) | **3,06:1** | **2,75:1** |

**Fechar o véu sozinho não resolvia:** para o #B9D2EA passar no p98 seria
preciso alfa composto ~.80, e a essa altura não há mais fotografia.

Então o rótulo deixou de se distinguir por claridade e passou a se distinguir
por **família**: mono, caixa alta e tracking, em branco. É como todo rótulo
deste sistema se marca onde o fundo é exigente (`.oferta tbody th`,
`.contratos__rotulo`, `.peca__cota`), e de quebra amarra a lista à matriz de
Engagements logo acima. Véu fecha um degrau só (.55 → .62) para dar margem.
Reconferido no render a 390: **5,42:1 no pior bloco absoluto.**

O hover **não troca a cor do rótulo** — ele já é branco, e o accent sobre esta
foto dá 3,06:1: acender nele seria apagar. O gesto fica com o filete que se
desenha (`scaleX`, `transform-origin: left`), o chão que acende e o
deslocamento de 4px: três leituras do mesmo evento, nenhuma dependente de cor.

## 106. Método e plataformas: a costura já estava no texto

O passo 02 é "Choose the strategy", e o parágrafo das plataformas dizia, sozinho
numa seção separada, que a escolha *"is a decision about the process and about
who maintains it after we leave"*. Não era outro assunto — era o passo 02
contado por outro lado. Separadas, a página fazia duas vezes a mesma pergunta.

Nasceu `.bloco--continua` para o segundo bloco de texto dentro de uma seção. O
número sai da razão que já existe: `--s-4` (24) dentro de um grupo,
`--gap-bloco` (64) entre bloco e componente, `--sec-y` (160) entre seções.
**`--s-9` (128) é o degrau entre os dois últimos** — mais que bloco/componente,
menos que seção/seção. Menos que isso e ele gruda no diagrama; mais e a seção
mesclada se lê como as duas que ela veio substituir.

A seção passou a **off-white**: com uma seção a menos a página perdia a única
faixa de meio-tom, e o salto de quase-branco a quase-preto é a causa raiz do
feedback que originou a revisão inteira (`design.md` §0).

## 107. "Your design or ours" estava boa — e a peça dentro dela, não

O pedido era *"vale voce checar"*. A peça tinha um defeito de verdade.

O comentário em `style.css` ainda dizia *"o PV é dourado porque ele é O DADO —
a única linha que o visitante segue"*. Quando o `#FDC500` saiu do site (regra
crítica 4, 25/08), o PV foi colado no **mesmo token do chrome** e a conta nunca
foi refeita:

| | antes | agora |
|---|---|---|
| PV (a resposta) | #B9D2EA sólido 2px — 6,38:1 | **branco sólido 2px — 9,95:1** |
| SP (a referência) | branco 85% 1px — 7,68:1 | **#B9D2EA tracejado 1px — 6,38:1** |
| PV contra SP | **1,20:1** | 1,56:1 **mais o padrão** |

**1,20:1 entre as duas linhas de que a peça inteira trata**, separadas só por
espessura — e com a hierarquia invertida: o setpoint, que é só a referência que
o visitante arrasta, era a coisa mais clara da tela.

1,56:1 ainda não separa sozinho, e por isso o SP passou a ser **tracejado**:
cor mais padrão separam, e o padrão continua separando para quem não distingue
as duas cores. Nenhuma cor nova entrou.

**Uma armadilha junto:** `malha.js` tinha `#FDC500` como reserva de
`--malha-pv`. Nunca disparou, mas era o único `#FDC500` do código de página —
**num canvas**, onde o grep de redline (que varre CSS) nunca teria achado.

> **`carta.js` e `mimico.js` têm a MESMA armadilha** (`--carta-vivo` e
> `--mimico-vivo` caem em `#FDC500`), e continuam com ela: são contact e
> past-performance, fora do escopo desta rodada. Os dois tokens existem em
> `style.css`, então as reservas também não disparam hoje.

## 108. A peça animada, medida pela primeira vez fora do navegador

`doit.md` registra na Fase 8 que a aba de automação abre em segundo plano e o
Chrome não entrega `requestAnimationFrame` — as peças de canvas desenhavam a
grade e paravam, e o screenshot mostrava uma caixa vazia que parecia defeito.

Resolvido: **`Page.bringToFront`** tira a aba de `visibilityState: "hidden"`.
`ferramentas/movel/peca.mjs` faz isso, espera tempo REAL e recorta a peça.

Duas armadilhas do caminho, para quem repetir:

- **`setVirtualTimePolicy` não serve aqui.** O relógio virtual entrega o
  orçamento como poucos saltos enormes, e as penas precisam de muitos quadros
  pequenos: `avancar()` integra a passo fixo e limita passos por quadro.
- **`clip` do CDP é em coordenadas de DOCUMENTO**, `getBoundingClientRect` é em
  coordenadas de VIEWPORT. Sem somar a rolagem o recorte sai branco.

E a captura achou um defeito que nenhuma leitura de código acharia: **no regime
permanente os rótulos "SP" e "PV" caíam no mesmo pixel** — que é justamente o
estado final da peça, então ficavam ilegíveis para sempre. Separação mínima de
13px, e quem cede é o SP: o PV marca o dado, então a referência é que se
desloca.

## 109. Estado

```
0 quebradas · 0 conflitos de seletor · 0 fotografias repetidas
0 falhas na matriz viva de contraste · 0 #FDC500 no CSS de página
```

**Medido no render, a 1440 e a 390:** o herói (H1, apoio, trilha), a matriz de
quatro colunas nas duas formas (matriz e empilhada), a seção do gabinete
(rótulo e valor, nos dois tamanhos), a escada e a peça da malha animada.

**Órfão que sobra, e não é desta rodada:** `img/dupla/baterias-*` — 7 arquivos,
5,4 MB de deploy. `build_imagens.py` o mantém de propósito desde 26/08 ("o nome
continua servindo a quem quiser a caixa alta"), mas ele não tem consumidor
desde que who-we-are trocou o fundo. Vale decidir.

**Não verificado:** as outras cinco páginas não foram recapturadas — todas as
mudanças de CSS desta rodada são de classe nova (`.heroi--servicos`,
`.bloco--continua`, `.dados--entrega`) ou de componente que só services usa
(`.oferta`, `.malha`), conferido por grep em `site/*.html`.

---

# PARTE XVI — a figura 13 da galeria, 2026-08-27

> *"a foto 13 em galleey esta com animação quebrada"*

## 110. Não era a foto, era o motor de progresso — e valia para o site inteiro

A figura 13 (`fiacao`, proporção **0,6604** — a mais retrato do acervo) não
animava: aparecia como um buraco branco durante a entrada inteira e **estalava**
para o estado final quando o topo dela já tinha saído por cima da tela.

O arquivo estava íntegro (422×639, avif/webp/jpg), o HTML era idêntico ao das
outras 32, e a matemática do CSS também — congelando `--p` em 0,15 / 0,35 / 1,00
a figura 13 e a 20 produziam exatamente o mesmo `--avanco`, a mesma `opacity` e
o mesmo `clip-path`. **A peça estava certa; quem estava errado era o valor que
chegava nela.**

## 111. A conta que quebrava, e por que só nesta figura

`main.js` publica `--p` com duas leituras, escolhidas pela altura do elemento:

```js
var curso = c.height - vh;
var p = curso > 0 ? -c.top / curso : (vh - c.top) / (vh + c.height);
```

O ramo de cima é o da **cena presa** — a seção com painel `sticky`, em que o
curso é justamente o trecho em que o painel fica preso. Mas a condição era
`curso > 0`: **qualquer** elemento um pixel mais alto que a janela caía nele.

Uma figura de galeria não é uma cena presa. Ela só é alta.

Medida a figura 13 numa janela de 1440×700 (altura da figura: 708px, então
`curso` = **8 pixels**):

| scrollY | topo | visível | `--p` | opacity |
|---:|---:|---:|---:|---:|
| 2556 | 263 | 62% | 0,0000 | 0,00 |
| 2730 | 85 | 87% | 0,0000 | 0,00 |
| 2788 | 26 | **95%** | 0,0000 | **0,00** |
| 2846 | −65 | 91% | **1,0000** | **1,00** |

A animação inteira acontecia em **oito pixels de rolagem**, e só depois de o
topo já ter passado. O visitante via um vão branco durante toda a entrada e um
estalo no fim — nunca a revelação.

**Por que só a 13.** Ela é a mais retrato do acervo, então é a primeira a ficar
mais alta que a janela. A 1440×700, em três colunas de 432px:

| figura | proporção | altura | mais alta que a janela? |
|---|---:|---:|---|
| **13** `fiacao` | 0,6604 | 708 | **sim** |
| **28** `fiacao-textil` | 0,6667 | 702 | **sim** |
| 29 `baterias` | 0,7498 | 630 | não |
| todas as outras | ≥ 0,80 | ≤ 594 | não |

A 1440×900 nenhuma quebra — por isso a rodada anterior não pegou. É um defeito
de **janela baixa**, e a 13 é quem o expõe primeiro. A 28 vinha logo atrás, com
6px de folga.

## 112. O limiar, e ele é medido

A condição virou `curso > vh * 0.5`: só é cena presa quem tem curso de verdade.
Levantados **todos** os consumidores de `[data-progresso]` do site a 1440×700,
em cursos por janela:

```
cena presa mais CURTA ......... 1,500   (.unidade, .secao--presa)
.filme ........................ 1,600
.cobertura .................... 2,000
.galeria__mosaico ............. 6,300
------------------------------------- limiar 0,5
figura 13 ..................... 0,011
figura 28 ..................... 0,003
```

**Três vezes abaixo da menor cena legítima e trinta vezes acima da maior figura
quebrada.** Não há nada perto do limiar — não é um número escolhido para caber,
é um vale vazio entre dois grupos.

Depois do conserto, a mesma figura 13 na mesma janela:

```
visível  29%  38%  46%  55%  64%  73%  82%  91%  99%
opacity  .10  .20  .31  .42  .52  .63  .73  .84  .94
clip     90%  80%  69%  58%  47%  37%  27%  16%   6%
```

A revelação passou a acontecer **enquanto a figura está na tela**, que é a
definição de revelação.

## 113. Não-regressão, e as ferramentas que ficaram

As cinco cenas presas do site continuam varrendo 0 → 1 depois do limiar:
`.filme`, `.unidade`, `.secao--presa`, `.cobertura` e `.galeria__mosaico` —
todas `ok`.

Três diagnósticos ficaram em `ferramentas/movel/`, e os três nasceram desta
caçada:

- **`peca.mjs`** — congela e fotografa uma peça de canvas **animada**.
  `Page.bringToFront` tira a aba de `visibilityState: "hidden"`, que é o que
  fazia `rAF` não disparar e as peças saírem vazias no screenshot.
- **`progresso.mjs`** — cruza, quadro a quadro, **quanto da figura está
  visível** contra o `--p` que ela recebe. É a tabela do §111, e é a única
  forma de ver este defeito: `--p` ia de 0 a 1 normalmente, então qualquer
  sonda que só olhasse mínimo e máximo daria "saudável".
- **`presas.mjs`** — o teste de não-regressão do limiar.

> **A lição é da sonda, não do bug.** A primeira varredura mediu `p mínimo` e
> `p máximo` das 33 figuras e devolveu 0,000 → 1,000 em todas, inclusive na
> quebrada. O defeito não estava na FAIXA que `--p` percorre, estava em QUANDO
> ele a percorre. Medir a amplitude de uma animação não diz se ela é visível.

## 114. Estado

```
0 quebradas · 0 conflitos de seletor · 0 fotografias repetidas
0 falhas na matriz viva de contraste
```

**Verificado a 1440×700 e 1440×900:** as 33 figuras da galeria e as cinco cenas
presas. A figura foi **consertada, não removida** — o usuário abriu a
possibilidade ("se for muito dificil apenas retire a foto"), mas o conserto é
uma condição em `main.js`, e tirar a foto teria deixado a 28 quebrada e o
defeito de pé para qualquer janela mais baixa.

---

# PARTE XVII — a escada sai de services, 2026-08-27

> *"Inside step 02 na aba services, faz sentido existir isso e a tabela de
> tecnologias ali? se sim melhore o layout (as tecnologias o layout foi
> atualizado no site)"*

## 115. Faz sentido a pergunta; não fazia sentido o catálogo

A resposta é dividida, e as duas metades têm razão diferente.

**Fica a decisão de plataforma.** O comprador em services tem duas perguntas
legítimas — *"vocês trabalham com a minha?"* e *"quem mantém isso depois que
vocês saem?"* — e a segunda é argumento de venda, não catálogo.

**Sai a escada de oito degraus.** Quatro razões, nenhuma de gosto:

1. **Era duplicata literal da âncora de capabilities.** As mesmas oito
   plataformas, com os mesmos sub-rótulos. Capabilities é a página chamada
   *"Certified where it matters"* — a escada é o argumento dela.
2. **E era a versão VELHA.** Capabilities partiu a escada em dois rails
   rotulados ("Certified on" / "Fluent in") em 26/08, porque num rail só o
   visitante tinha de DEDUZIR que contato cheio significa certificação, e
   `plano.md` §1 regra 10 não deixa explicar isso em legenda. Services tinha
   ficado com o rail único — era o que o usuário quis dizer com *"o layout foi
   atualizado no site"*.
3. **As plataformas já aparecem duas vezes em capabilities** — na lista das
   oito disciplinas ("Rockwell, Siemens and Schneider" em PLC Programming;
   "Ignition, VTScada and Canary" em SCADA Programming) e na escada. Com
   services eram **quatro** aparições da mesma lista no site.
4. **O próprio parágrafo entregava o jogo:** terminava em *"The certifications
   themselves are on Capabilities"*. Mostrar uma cópia logo acima do link que
   aponta para o original é redundância assumida.

> Este era o achado nº 4 da auditoria que abriu a PARTE XV, e ele tinha ficado
> sem resolução: o pedido daquela rodada foi MESCLAR método e plataformas, o
> que manteve a escada na página. A pergunta do usuário fecha o item.

## 116. O que entrou no lugar: nenhum componente novo

`marcas_certificacao()` já existia — a faixa de chips que a home usa como
ponte entre duas dobras. Ela carrega **a mesma notação da escada na forma
compacta**: ponto cheio é certificação, chip liso é operação. Responde "a minha
está aí?" numa olhada, sem copiar o componente-âncora de capabilities.

**Oito chips e não os seis da home.** Lá `AVEVA PI System` e `SQL Server` ficam
de fora por serem camada de historiador e não plataforma de controle — a
exceção está documentada na própria função. Aqui entram, e a razão é a pergunta
desta página: quem compra quer saber **quem mantém o dado depois**, e o
historiador é exatamente essa parte da resposta. O parâmetro `nomes` existe
para isso.

**O eyebrow deixou de apontar para o diagrama.** *"Inside step 02"* só
funcionava para quem tinha acabado de ler os quatro passos — era navegação, não
rótulo. *"What it runs on"* nomeia o assunto.

## 117. Duas regras de CSS, e a segunda saiu do render

`.bloco__dir > .corpo + .marcas` não existia: a faixa nasceu na home entre dois
blocos, no grid 4/8, onde o espaçamento vem do próprio bloco. Dentro da coluna
direita, depois de um parágrafo, ela nascia colada no texto. `--s-5`, o mesmo
degrau que separa parágrafo de componente em toda a coluna direita do site.

E **`max-width: 26em`, que a captura pediu.** Solto, o strip de oito chips
esticava para ~1075px debaixo de um parágrafo de 494 (`.corpo` é 26em): duas
larguras diferentes em blocos que se leem como um só, com o texto virando uma
tira estreita ao lado de uma faixa larga.

> A distinção que a regra registra: **componente que ocupa a coluna inteira** (a
> escada, o diagrama) é IRMÃO do bloco de texto e nasce depois dele;
> **continuação de parágrafo** herda a medida do parágrafo. Os chips são o
> segundo caso.

Em 26em os oito caem em quatro fileiras (3 / 2 / 2 / 1) — e a primeira fileira
é exatamente **os três certificados**, que é o agrupamento que interessa. Não
foi planejado; foi conferido e mantido.

`.corpo--nota` para a frase de remissão: um degrau abaixo do corpo e em tinta
secundária, porque no mesmo tamanho ela competiria com o argumento que acabou
de ser feito. O link segue em accent — é ele que tem de ser visto.

## 118. Estado

```
0 quebradas · 0 conflitos de seletor · 0 falhas na matriz viva de contraste
```

| | antes | agora |
|---|---:|---:|
| `services.html` | 25,4 KB | **23,1 KB** |
| altura a 1440x900 | 7367 px | **6947 px** |
| páginas com `.escada` | 2 | **1** (só capabilities) |

**Verificado no render a 1440x900 e 390x844:** a dobra inteira, o rag dos chips
nas duas larguras e a nota de remissão.

---

# PARTE XVIII — o mecanismo no celular, e o ar de who-we-are, 2026-08-27

> *"apos o filme principal na pagina home, temos os outros 3 menores, existe um
> problema na aplicação mobile, os videos nao tem animação nenhuma, de crescer
> e diminuir, e os textos (primeira e segunda fase simplesmente some a aparecem
> do nada). no pc esta perfeito. (…) a pagina who we are esta com muito texto, e
> isso tira o ar que a pagina precisa ter, principalmente no mobile, quero que
> voce refaça os textos de since 2000 e why it matters who does the work."*

## 119. As duas queixas eram o mesmo bloco de CSS

Medido a 390x844, rolando a unidade 1 de ponta a ponta:

```
scrollY   --p    is-aberta   coluna     rodapé     clip da janela
   4586  0.2905     nao      1.00/vis   1.00/hid   none
   4707  0.3631     SIM      1.00/hid   1.00/vis   none
```

Duas coisas nesse par de linhas, e são exatamente as duas que o usuário viu:

1. **`clip: none` do começo ao fim.** O ramo de celular desligava o
   `clip-path` da janela e **nada tomava o lugar dele**. Não era um mecanismo
   fraco — era mecanismo nenhum.
2. **A coluna e o rodapé trocavam por `visibility`, num único quadro**, com a
   opacidade travada em 1. `visibility` não interpola: é o estalo descrito como
   "some e aparece do nada".

O `visibility` vinha de `.unidade.is-aberta`, que o **desktop** usa para tirar
a coluna do teste de acerto quando o vídeo vem tomar a tela. No celular não
existe essa disputa — coluna, vídeo e frase são três blocos em sequência no
fluxo, nenhum passa por cima de nenhum. **A regra estava vazando de um layout
para o outro**, e o ramo de celular nunca a desfez.

## 120. O conserto, e a linha que eu quase cruzei

`animation-timeline: view()` resolveria a janela numa linha e rodaria fora da
main thread. **Não usei, e o motivo já estava escrito neste projeto** (§21 do
`style.css`): não há no Safari, e o efeito sumiria inteiro para metade dos
visitantes de iPhone. Num ramo que **só existe no celular** esse argumento é o
mais forte que fica. Tudo aqui sai de `--p`.

**A janela lê a travessia dela mesma.** `data-progresso` foi para
`.unidade__janela` no gerador. Não dá para recortar uma faixa do `--p` da
seção: no celular a altura da seção depende do tamanho do texto da coluna, e as
três unidades têm alturas diferentes — **823, 904 e 855px**. Qualquer faixa fixa
acertaria numa e erraria nas outras duas. Lendo a própria travessia, a janela
acerta nas três:

| | unidade 1 | unidade 2 | unidade 3 |
|---|---|---|---|
| altura da seção | 823 | 904 | 855 |
| clip no início | 13% / 9% | 13% / 9% | 13% / 9% |
| clip no fim | 0% | 0% | 0% |
| rodapé entra em `--p` | .58 | .58 | .58 |

**A geometria muda de propósito.** No desktop a caixa nasce encostada num dos
lados, porque ali existe um lado para a coluna de texto ocupar, e o lado
alterna a cada unidade. Numa coluna só não há o que revelar do outro lado:
a caixa nasce **centrada** e menor (13% em cima e embaixo, 9% dos lados) e vai
a zero. O `--lado-caixa`/`--lado-vazio` alternado não tem função aqui.

O vídeo cede 4% de escala junto com a máscara: sem isso o recorte lê como um
retângulo menor da MESMA imagem, e não como uma imagem que cresce.

**A faixa é .18 → .62 da travessia**, e não 0 → 1. A janela é 16:9 numa tela de
844px: ocupa ~26% dela, então a travessia dura ~1,26 telas. Abrindo em .18 o
gesto começa com a caixa já dentro do campo de visão e termina em .62, bem
antes de ela sair. Fora dessa faixa a animação aconteceria onde ninguém está
olhando — **que é literalmente o defeito da figura 13 da galeria** (§111). A
lição daquela caçada foi aplicada antes de virar defeito.

O texto passou a entrar em vez de piscar, escalonado por `--i`, lendo o `--p` da
seção — e aqui isso é o certo, porque coluna e rodapé são as **pontas** dela.
Medido depois:

```
--p      0.07  0.15  0.22  0.29  0.36  0.51  0.58  0.65  0.73  0.80
coluna   .20   .66   1.00  1.00  1.00  1.00  1.00  1.00  1.00  1.00
         .00   .38   .83   1.00  ...
         .00   .10   .55   1.00  ...
clip     13%   13%   13%   13%   10%   3%    0%    0%    0%    0%
rodapé   .00   .00   .00   .00   .00   .00   .01   .41   .81   1.00
```

Sem sobreposição, sem estalo. **E um bloco novo de `prefers-reduced-motion` só
para o celular**: o 6c.5 foi escrito quando ali não havia mecanismo nenhum para
desligar, e sem a regra nova quem pede menos movimento passaria a receber
**mais** do que antes desta rodada.

## 121. who-we-are: o texto que a própria página já dizia

**"Since 2000": 190 → 88 palavras de prosa (−54%).** O que saiu, e cada coisa
por um motivo:

- **A lista de verticais** (água, papel, óleo e gás, solar) — os chips de setor
  mais abaixo **nesta mesma página** já a mostram, e past-performance dá uma
  ficha por setor. Era a terceira vez.
- **"certified on the leading supervisory platforms"** — é a afirmação-âncora
  de capabilities, com a escada inteira por baixo. Aqui era só a afirmação,
  sem a prova.
- **O parágrafo do "wrong partner is expensive twice"** — versão abstrata e
  mais fraca do argumento do transmissor de $45.000, que vem na dobra
  **seguinte** com número e mecanismo. Ele gastava o soco 200 palavras antes de
  o soco acontecer.
- **"twenty-six years" e "five industries" em prosa** — o bloco `NUMEROS`, logo
  abaixo, diz 279 projetos, 158 nos EUA, 78 na Flórida, 150.000 tags e desde
  2000. Prosa repetindo número é a prosa perdendo.

Fica o que só esta dobra diz: o que a casa **é** (consultora e integradora, não
linha de produto) e o que ela **vende** (julgamento e documentação). O resto da
dobra são os números, e agora eles têm espaço.

**"Why it matters who does the work": 183 → 143 palavras (−22%), e o corte foi
cirúrgico.** É a única dobra do site que mostra COMO um especialista em
controle pensa, em vez de afirmar que a casa tem especialistas — é a razão de a
página ter sido refeita.

> **Nada de fato saiu.** Continuam inteiros: a cifra de $45.000, que é do
> cliente; as três perturbações na ordem em que ele as enumera; as três
> estratégias que respondem a elas uma a uma (feedforward, razão, cascata); e o
> fecho de 2000.

O que saiu foi **fôlego de frase**. A enumeração das perturbações eram três
orações completas — *"An inlet temperature change arrives… A header pressure
change moves… A production rate change demands…"* — e virou uma lista pontuada
dentro de uma oração só. O argumento é o mesmo; muda quanto ar ele ocupa numa
tela de 390px, por cima de um vídeo.

## 122. Estado

```
0 quebradas · 0 conflitos de seletor · 0 falhas na matriz viva de contraste
```

**Verificado:** as três unidades a 390x844 (progresso, clip, escalonamento do
texto, rodapé) e a unidade 1 a 1440x900 para não-regressão — o desktop abre de
`inset(27% 44% 27% 4%)` a zero exatamente como antes. who-we-are relido a
390x844 nas duas dobras.

**Ferramenta nova:** `ferramentas/movel/unidade.mjs` — despeja progresso,
`is-aberta`, opacidade de cada filho da coluna, do rodapé e o clip da janela ao
longo da rolagem. Foi ela que mostrou que `--p` ia bem e o problema era o
`visibility`.

**Não tocado, e vale decidir:** *"Our mission"* é a seção **mais longa** de
who-we-are — **251 palavras**, contra as 88 de "Since 2000" agora. O pedido
nomeava duas dobras e eu fiquei nelas, mas se o assunto é ar, essa é a próxima.

---

# PARTE XIX — o notebook abre, e Engagements emagrece, 2026-08-27

Três pedidos numa rodada: simplificar Engagements, trocar a intro pelo
notebook da marca abrindo (**com ponto de retorno salvo antes**), e um "see
more" no argumento de who-we-are só no celular.

## 123. O ponto de retorno, primeiro

> *"salve o estado atual da animação, caso eu nao goste do resultado
> conseguimos voltar no tempo."*

`melhorias/intro-v1/` guarda os quatro pedaços da intro anterior — a seção 5
do `style.css`, o módulo 5 do `main.js`, o `intro_html` e `marca_lockup()` —
mais `COMO-VOLTAR.md` com o procedimento. **Os assets de marca não mudam entre
as versões**, então voltar é só CSS, JS e HTML gerado: nenhuma imagem precisa
ser reconstruída.

## 124. A intro nova, e a regra que governou a implementação

> *"O computador (logo do i3) esta fechado no plano start, e se abre e preenche
> a tela, como se o site fosse a tela do notebook."*

**NÃO REDESENHAR A MARCA.** A primeira intro do projeto morreu por isso
(`design.md` §3.5): desenhava o REDESENHO em SVG, e o cliente reparou. Abrir um
notebook pede duas peças que giram uma contra a outra, e a saída óbvia é
desenhá-las — seria o mesmo erro pela terceira vez.

`ferramentas/corte_marca.py` **corta a arte real na dobradiça** e grava
`logo-tampa.png` (12 KB) e `logo-base.png` (1,4 KB). Não há um pixel desenhado:
há a arte do cliente, partida onde ela já se parte. Medido no arquivo:

```
notebook (marca isolada) ... x  40..460   y  65..333
aresta de cima da tampa .... y  65..68
DOBRADIÇA .................. y 298..300
entalhe do trackpad ........ y 306..308
aresta de baixo da base .... y 329..332
```

Duas tentativas erradas antes de acertar o cortador, e as duas viram
comentário no arquivo: procurar a dobradiça pelo **pico** de pixels brancos
achou a aresta de BAIXO (a base saiu com 5px); e delimitar o notebook pelas
colunas com tinta no topo cortou 21px de cada lado da base — **a base é mais
larga que a tampa**, e é esse ressalto que faz a peça ler como laptop.

### A tela vira o site sem ampliar um pixel

O caminho ingênuo é crescer o notebook até encher a janela. Não serve: a tampa
tem 420px nativos, e encher 1440 pediria ampliar 3,5x uma arte já em 1,2x — a
marca borraria justamente quando é o assunto.

**Quem se move é o véu.** Quatro painéis navy emolduram a tela dourada e recuam
para fora dos quatro cantos; o buraco que se abre entre eles É a página. A
marca fica no tamanho em que é nítida e sai por opacidade. O gesto lido é o
mesmo e nada é ampliado. Os quatro andam só por `scaleX/scaleY` com origem na
borda de fora — a abertura inteira roda na composição.

O retângulo é **exato por construção**: as frações da tela dourada saem do
mesmo `corte_marca.py`, e tanto o notebook quanto os painéis são posicionados a
partir delas. Uma conta só, usada dos dois lados. Mais `--folga: 2px` de
sobreposição, para nenhum arredondamento de subpixel deixar passar um fio da
página antes da hora.

**No celular não entra aparelho novo**, e é a mesma regra. Desenhar um telefone
seria inventar um objeto de marca que não existe na arte. E não é preciso: o
buraco abre até a janela, e a janela ali é retrato — a tela do notebook virando
a tela do visitante é o gesto pedido, sem silhueta nova. Só `--nb` muda (74vw
→ 86vw).

### Dois defeitos achados na captura

**`backwards forwards` não existe.** Escrevi `animation: … .95s backwards
forwards` em quatro lugares. `animation-fill-mode` é UMA palavra: o par
invalida o shorthand inteiro, e sem animação a frase ficava presa em
`clip-path: inset(0 100% 0 0)` — **invisível**. O correto é `both`. A captura
mostrou 9 animações onde deviam ser 12.

**E uma que parecia defeito e não era.** `getAnimations()` não lista animação
terminada sem `forwards`. A abertura da tampa acaba em 1,05s e tem `backwards`
só: meio segundo depois da carga o objeto sumiu e o `transform` voltou a
`none`. Era o fim correto do gesto. Por isso `ferramentas/movel/intro.mjs`
pausa as animações por **CSS injetado antes da carga**, e neutraliza o
`setTimeout` que remove a intro em 3,25s — sem as duas coisas a captura vinha
vazia.

Linha do tempo: 3,4s contra os 5,6s da v1.

## 125. Engagements: a matriz saiu

> *"esta muito complexa e nao funciona bem no celular, preciso que voce resuma
> e escolha bem as informações."*

A matriz não era um formato errado — ela deixava comparar quatro ofertas num
critério lendo uma linha. Mas cobrava caro: com a quarta coluna virou **4×4 =
16 células**, `table-layout: fixed`, `min-width: 928px` e um ramo de celular
que desmontava a tabela inteira. Dois layouts para manter, e o pior dos dois
era o do celular — que é onde se lê.

**E o que foi cortado era repetição.** Dos quatro critérios, `Starts when` e
`Typical trigger` descreviam a mesma coisa: a situação em que o comprador se
reconhece. Viraram um.

Agora são quatro fichas, três campos cada: a situação em corpo cheio (é a
frase em que o leitor se reconhece, e tem de vir antes), depois `WE DO` e
`YOU GET` em rótulo mono. Grade 2×2 no desktop, uma coluna no celular — **o
mesmo layout, contagem de colunas diferente**. Some a rolagem horizontal, some
a largura mínima, some o ramo separado.

O terminal aberto fica: as quatro formas continuam sendo derivações paralelas,
não uma sequência. O que sai é o barramento horizontal — com as fichas em duas
fileiras ele teria de dobrar, e barramento que dobra não lê como barramento.

`services.html`: 23,1 → **21,6 KB**.

## 126. "Read why", e só no celular

Um `<details>` de verdade, e não uma classe com `max-height`. O conteúdo
continua no DOM e achável pelo Ctrl+F; o `<summary>` já é botão para teclado e
leitor de tela; e **sem JS ele ainda abre** — a página não tem script próprio,
e um acordeão dependente de JS seria o único ponto do site em que texto some se
um arquivo falhar.

O primeiro parágrafo fica **fora** do `details`: ele carrega a cifra de $45.000
e o "muito simples e muito errado". Esconder o gancho seria esconder o
argumento.

**No desktop o componente não existe:** o `summary` sai do fluxo e o corpo é
revelado por `display`, então o que resta é a `.pilha` de sempre — verificado,
163px de altura antes e depois.

> **E o navegador não fecha mais o `details` sozinho.** Medido no Chrome: sem
> `open`, o corpo continuava com **349px** de altura. O esconder padrão migrou
> para `::details-content` com `content-visibility`, e um filho com `display`
> próprio escapa dele. `.mais:not([open]) .mais__corpo { display: none }`
> resolve, e vale em todo navegador. Confiar no UA aqui daria uma dobra que
> "às vezes" abre fechada.

Verificado: 390px fecha em 0 e abre em 349 ao toque; 1440px ignora o
componente.

## 127. Estado

```
0 conflitos de seletor · 0 falhas na matriz viva de contraste · 0 quebradas
```

**Ferramenta nova:** `ferramentas/movel/intro.mjs` — congela o relógio das
animações da intro e fotografa marcos fixos. Determinística: a mesma execução
devolve as mesmas imagens, que é o que serve para comparar v1 e v3.

**Verificado no render:** a intro a 1440x900 e 390x844 nos dez marcos (tampa
fechada a −92°, abertura, frase escrita, painéis recuando, revelação), o
Engagements novo nas duas larguras, e o `details` nos dois estados.

**Não medido:** a intro em Safari. O giro usa `perspective` + `rotateX`, que é
suporte antigo e universal, mas o projeto não tem Safari neste ambiente.

## 128. O pedaço de texto ao lado do notebook, 2026-08-27

> *"ficou um pedaço do texto na animação da intro a direita do notebook"*

Um risco branco de **3x18px** flutuando ao lado da tampa. Localizado no render
em x 977..979, y 444..462, com pico em rgb(244,247,249) — desvio de **540** do
campo navy. Rastreado de volta ao pixel de origem: `logo-original.png`, x=459,
y≈238. **Era a primeira letra do wordmark.**

A BASE DO NOTEBOOK E O WORDMARK SE SOBREPÕEM. Medido, contando qualquer alfa:

```
x=457   base 27 linhas   wordmark  0
x=458   base 26 linhas   wordmark 12   alfa até  73  (a franja)
x=459   base 24 linhas   wordmark 24   alfa até 244  (a letra)
x=460   base 22 linhas   wordmark 31   alfa    255
```

`corte_marca.py` fechava a caixa na borda da **base** (x1=460), e levava junto
as dez linhas de letra da coluna 459.

**Duas correções, e a segunda só apareceu porque a primeira foi conferida.**
Cortar no primeiro pixel OPACO do wordmark (x1=459) derrubou o risco de 540
para **76** — a franja anti-serrilhada da coluna 458, mais fraca e ainda
visível. O corte tem de cair antes de QUALQUER tinta do wordmark, alfa > 0.

E o detector precisou de mais duas voltas até acertar:

- partir de um `x` fixo (439) caiu dentro da franja da própria tampa e cortou
  a marca em 439 — 40px a menos de notebook;
- procurar o vão a partir de `x0` contou as ~20 colunas em que a base existe e
  a tampa ainda não, e cortou em 61, dentro da tampa.

A regra que ficou: na faixa de altura do wordmark (y 114..263) só existem duas
coisas — a tampa à esquerda e o wordmark à direita, com um vão vazio entre
elas. A varredura **começa na tampa** e corta no fim do vão. Nenhum número
chutado.

Resultado: x 40..458. O notebook perde duas colunas da ponta anti-serrilhada do
canto da base — invisível. Conferido no render: a faixa à direita da tampa tem
desvio **0** do campo nos estados assentados.

As seis frações do CSS foram refeitas junto (`--nb-alt`, `--nb-tampa` e as
quatro da tela dourada): elas saem da mesma medição, e deixá-las velhas
desalinharia os painéis da tela por ~1px.

---

# PARTE XX — o tempo de leitura da intro, e contact repensada, 2026-08-27

## 129. A intro não estava rápida demais: estava sem tempo de leitura

> *"a animação está desaparecendo muito rápido, desaparecer mais lentamente
> para que consigamos ler o que está escrito, ou escreva mais rápido."*

A conta explica a queixa exatamente. A frase terminava de se escrever em
**1,75s** e os painéis começavam a recuar em **1,90s**: sete palavras com
**0,15s** de tela. Não era pouco tempo de animação — era animação sem pausa.

O conserto faz as duas coisas oferecidas, cada uma pela metade:

| | antes | agora |
|---|---:|---:|
| escrita da frase | 0,80s | **0,60s** |
| frase inteira na tela | **0,15s** | **1,20s** |
| início da saída | 1,90s | 2,75s |
| total | 3,25s | 4,10s |

Ainda abaixo dos 5,6s da v1. A pausa é uma fase de verdade agora — entre
1,55s e 2,75s nada se move, que é o que faltava.

## 130. Contact: o mapa estava a três seções da legenda dele

> *"repense o layout de contact us (…) deixe o mapa e redes sociais e
> contatos."*

O diagnóstico é de **agrupamento** antes de ser de estilo. Três defeitos:

1. **O endereço aparecia em duas dobras distantes.** O bloco "Offices —
   Lakewood Ranch, FL / Houston, TX" vivia na seção 2; a **carta** que desenha
   exatamente esses dois pontos vivia no fim da seção 4. O mapa e a legenda
   dele separados por toda a página.
2. **Uma seção respondia duas perguntas sob um título que só cobria uma.**
   "Where else we show up" fala de redes sociais, e embaixo dela estava o mapa,
   que fala de geografia.
3. **A página se justificava antes de servir.** A seção 2 abria com dois
   parágrafos sobre por que não há formulário — no ponto de maior atenção,
   antes de qualquer telefone.

**A estrutura nova, três dobras em vez de quatro:**

```
branco ..... "Reach us"                 os três canais, primeiro
escuro ..... "Where to find us"         o mapa + as redes — as duas formas
                                        de ACHAR a empresa, física e online
off-white .. "For contracting officers" as credenciais
```

O bloco "Offices" sai de `.contato`: a cota da carta já nomeia as duas
cidades, e `HOUSTON, TX / OIL & GAS` contra `LAKEWOOD RANCH, FL / HQ` diz mais
que a linha de texto dizia. `.contato` é `auto-fit`, então três blocos
preenchem a linha sem um ajuste de CSS.

**As redes ficam na dobra escura**, e a razão é dupla: `.canais` foi desenhado
para superfície escura (régua em `--filete`, hover em `#fff`), e "onde nos
achar" é a mesma pergunta que o mapa responde — uma no espaço, outra na rede.

A decisão de não ter formulário continua dita, agora em **uma frase depois dos
telefones** em vez de dois parágrafos antes deles.

## 131. Duas afirmações que não se sustentavam, escritas por mim

O primeiro rascunho desta dobra tinha o título *"Lakewood Ranch, and a bench
in Houston"* e a frase *"close enough to be on site the same day when a plant
calls"*. **As duas prometiam o que o acervo não sustenta:**

- nada no site diz que há oficina ou pessoal fixo em Houston. O que
  past-performance registra é a CARTEIRA — *"our oil and gas client base sits
  in Houston, Texas"* —, e o site antigo diz o mesmo. "Bench" promete bancada.
- "on site the same day" promete tempo de resposta a **1.289 km** de distância,
  que é o número que a própria carta imprime.

Trocado por *"An office in Florida, a client base in Texas"* e por uma frase
que só diz o que o mapa desenha. É a mesma regra de `design.md` §7.1 que
governa legenda de fotografia, aplicada a copy: o cliente é fornecedor
federal, e afirmação não verificável é risco real.

> Vale o registro de que o erro foi meu e não herdado — escrevi as duas na
> mesma rodada em que as removi. A regra pega copy nova tanto quanto copy
> velha.

## 132. Estado

```
0 conflitos de seletor · 0 falhas na matriz viva · 0 referências quebradas
```

**Verificado no render:** a linha do tempo da intro nos dez marcos (a pausa de
1,2s existe e nada se move nela), e contact a 1440x900 e 390x844 — os três
canais, o mapa com as duas cidades legíveis, e as redes empilhadas no celular.

**Órfão que continua:** `img/dupla/baterias-*`, 5,4 MB, mantido de propósito
por `build_imagens.py` desde 26/08 e sem consumidor desde então.

## 133. As fotos de past-performance cinzentas no celular, 2026-08-27

> *"no celular os elementos da pagina past performance nao ficam com a cor
> adequada, apenas quando eles sao clicados (…) ou todos ficam com cor total,
> ou mudam automaticamente como foco."*

**A causa é uma linha só:** `.obra__placa img` repousa em
`filter: saturate(.2) contrast(1.05)` e só sobe a cor em `:hover`. A decisão
está documentada e continua certa no desktop — *"a fotografia é PROVA, não
decoração, e só sobe de tom quando o visitante repara nela"*.

**Num aparelho de toque não há ponteiro.** As seis fotografias ficam cinzentas
até alguém tocar numa — e aí o `:hover` GRUDA nela e não sai. O visitante de
celular vê ou a página inteira em cinza, ou uma foto colorida no meio de cinco
cinzentas. Os dois estados são acidente; nenhum é o desenho.

E é pior que uma afordância perdida: **a foto é prova de obra entregue.**
Dessaturada, ela lê como imagem quebrada ou marca d'água, não como contenção.

**O conserto: onde não há ponteiro, o estado de hover É o estado de repouso.**

```css
@media (hover: hover) { /* as três regras de :hover ficam aqui */ }
@media (hover: none)  {
  .obra__placa img { filter: none; }
  .obra__regua     { transform: scaleX(1); }
  .obra__idx       { color: var(--accent-txt); }
}
```

`(hover: none)` **e não `max-width`**, e a distinção importa: o que decide não é
o tamanho da tela, é a existência de ponteiro. Um notebook de 390px continua
tendo hover; um tablet de 1024px não tem. Largura acertaria o telefone e
erraria o tablet — que é onde uma página de obras é mais lida.

**Das três coisas que o ponteiro acende, duas entram no repouso e uma não.** A
cor da foto e o acento (régua e índice) são ESTADO e passam a valer sempre; o
`scale(1.03)` é GESTO e fica de fora — permanente, ele só recortaria a
fotografia em 3% sem dizer nada.

Medido nos dois modos:

| | filtro da foto | régua | índice |
|---|---|---|---|
| `hover: hover` | `saturate(.2)` | `scaleX(0)` | `--tinta-2` |
| `hover: none` | `none` | `scaleX(1)` | `--azul-txt` |

O desktop ficou intacto.

> **A varredura que fecha o assunto:** `saturate(` aparece **uma vez** em todo
> o `style.css`. Nenhuma outra página tem fotografia dessaturada em repouso, e
> nenhuma outra regra de `:hover` esconde conteúdo — as demais (fundo do
> degrau, borda do passo, seta de `.canais` em `opacity: .5`) realçam um estado
> que já está legível. O defeito era exclusivo de `.obra`.

**Nota de ferramenta:** `cdp.mjs` já reportava `hover: none` e
`pointer: coarse` com `movel: true` — o Chrome deriva os dois de
`setTouchEmulationEnabled`. As capturas de celular sempre foram fiéis nesse
ponto; o que faltava era eu ter olhado para o estado de repouso delas.

---

# PARTE XXI — vistoria de acabamento (`/impeccable polish`), 2026-08-27

O playbook pede "quality bar e shipping constraints". Este projeto já os
declara: `plano.md` §1 define "clean" em dez regras verificáveis, §8 lista os
redlines, e `contraste.py` é a matriz viva. Não perguntei — usei os documentos.

## 134. O que a vistoria mediu, e o que ela achou

Três sondas novas, nas **dez** páginas, em três larguras:

| sonda | o que responde | achado |
|---|---|---|
| `movel/vistoria.mjs` | transbordo lateral, id repetido, img sem alt, link sem nome, ordem de título, alvo de toque | **1** |
| `movel/consola.mjs` | erro de JS e recurso que falhou, depois de rolar a página inteira | **0** |
| `movel/seletores.mjs` | regra de CSS sem consumidor | 102 famílias |

Contraste, conflito de seletor, referência quebrada e foto repetida: **0** nos
quatro, como já estavam.

**O único defeito funcional: a 404 não tinha `h1`.** As outras nove recebem o
h1 de `cabecalho()`; a 404 não usa cabeçalho e abria em `h2`. Sem h1 a página
não tem raiz de estrutura — leitor de tela não acha o começo e o indexador não
sabe do que ela trata. Virou `h1` com a escala de `h2` (`.secao--erro h1`), que
é o que `.cabecalho h1` já faz: **o nível muda, o tipo não** — a tipografia
travada de `CLAUDE.md` regra 2 fica intacta.

Os outros quatro apontamentos de alvo de toque são **links em linha dentro de
frase** (`WhatsApp`, o e-mail nas páginas legais, a remissão de services), que
o WCAG 2.5.8 isenta explicitamente. Não são defeito.

## 135. 18% do CSS publicado não casava com nada

`seletores.mjs` achou 102 seletores de classe sem consumidor. Medido por
família: **16.776 bytes, 18,3% do `style.css` publicado.**

E a causa é uma **regra cumprida pela metade**. `design.md` §8 manda guardar a
peça que sai: *"Nada do que sai é apagado do repositório — sai da página, fica
no `fonte/js/`."* O JS obedecia — `planta.js`, `clp.js`, `lente.js` e
`marca.js` estão em `GUARDADAS` e não vão ao deploy. **O CSS dessas mesmas
peças continuava viajando dentro de `style.css` até o navegador do visitante.**

CSS é render-blocking: é o arquivo que segura a primeira pintura. 18% dele
morto custa em toda visita.

As 116 regras foram para `fonte/css/aposentado.css`, que entrou em
`GUARDADAS`. **Nada foi apagado** — a política é honrada, e o deploy encolhe:

```
style.css publicado   89,5 KB -> 78,3 KB   (gzip 13,8 KB)
CSS + JS do deploy   402,7 KB -> 138,9 KB minificado
```

## 136. Como a separação foi provada, e o controle que salvou a conclusão

Mover regra morta é uma aposta a menos que se prove. Três provas, em ordem de
força:

1. **Divisão sem perda.** 704 regras entram, 588 + 116 saem, zero perdidas e
   zero alteradas (comparação por multiconjunto do texto normalizado).
2. **Nenhum seletor movido casa.** Testados os 112 seletores de
   `aposentado.css` — inclusive os de dentro de `@media`, que a primeira
   extração **não alcançava** — contra as dez páginas: zero casamentos.
3. **Estilo computado, elemento a elemento.** 5.948 elementos nas dez páginas,
   em duas larguras, 27 propriedades mais a caixa.

A prova 3 acusou **5 diferenças**, e por um momento pareceram regressão — uma
delas era `past-performance DIV.container` perdendo `margin: 0 32px`.

> **O CONTROLE DESMENTIU AS CINCO.** Rodando o MESMO CSS duas vezes, o
> comparador acusa **4 diferenças** — inclusive o mesmo `DIV.container#56` e o
> mesmo `IMG.cabecalho__foto`. O teste velho-contra-novo deu **3**: menos que o
> controle.
>
> As três fontes de ruído, todas de tempo e nenhuma de CSS: a classe
> `is-visivel` que o aviso de armazenamento ganha por temporizador; o
> `transform` do paralaxe do cabeçalho, que depende do quadro em que se mede; e
> o `auto` da margem do container, cuja resolução muda enquanto a página ainda
> carrega.

Sem o controle eu teria "consertado" um defeito que não existia. **Comparador
sem grupo de controle mede o próprio ruído e chama de resultado.**

Uma tentativa anterior por hash de screenshot (`movel/impressao.mjs`) apontou
`capabilities@1440`; o despejo de estilo computado da mesma página deu **0
diferenças em 365 elementos**. Screenshot da página inteira não é
determinístico aqui — e a captura de `capabilities` ainda estoura o timeout,
como `doit.md` já registrava.

## 137. O que NÃO foi mexido, e por quê

- **As peças aposentadas não foram apagadas.** `design.md` §8 é explícito, e
  polir não é decidir de novo. Elas mudaram de arquivo, não de existência.
- **`img/dupla/baterias-*`** — 7 arquivos, 5,4 MB, sem consumidor desde 26/08.
  `build_imagens.py` o mantém **de propósito**, com a razão escrita. É deploy
  morto e é decisão registrada: fica para o usuário decidir, não para a
  vistoria desfazer. **Terceira vez que aparece nestas notas.**
- **Os quatro links em linha** abaixo de 44px: isentos por norma.

## 138. Estado

```
0 erro de console · 0 recurso falhado · 0 transbordo lateral · 0 id repetido
0 img sem alt · 0 link sem nome · 0 conflito de seletor · 0 foto repetida
0 falha na matriz viva de contraste · 0 referência quebrada
```

Dez páginas, três larguras (1440, 1024, 390). Ferramentas novas em
`ferramentas/movel/`: `vistoria.mjs`, `consola.mjs`, `seletores.mjs`,
`estilos.mjs`, `estilos-todas.mjs`, `impressao.mjs`.

## 139. Comentário no que vai ao ar: zero, 2026-08-27

> *"Elimine todo resquício de comentário desse repositório."*

**Perguntei o escopo antes de apagar**, e a razão está em `CLAUDE.md` regra 1:
parar e avisar quando um pedido contradiz o que está escrito. O que está
escrito é *"CSS e JS moram COMENTADOS em `fonte/`; `build_ativos.py` publica em
`site/` sem comentário"*, mais a regra 3 — todo número no CSS tem a conta ao
lado. Medido antes de perguntar:

| | bytes | comentário | % |
|---|---:|---:|---:|
| `fonte/css/*.css` | 306.452 | 204.388 | **67%** |
| `fonte/js/*.js` | 249.899 | 109.952 | 44% |
| `ferramentas/*.py` | 495.380 | 193.573 | 39% |
| **total da fonte** | **1.131.827** | **519.757** | **46%** |

E não havia ponto de retorno: o último commit é `ec4c7c8` e tudo desde então
está sem commit — um `git checkout` levaria junto o trabalho inteiro.

**O usuário escolheu o escopo do deploy.** A fonte fica intacta.

### O que estava sobrando, e não era o que parecia

`site/*.html` já tinha **zero** comentários (`limpar()` os tira). O que sobrava:

```
site/css/*.css + site/js/*.js ... 11 banners  /* GERADO por ... */
site/.htaccess .................. 36 linhas em PT-BR
site/_redirects .................  5 linhas
site/_headers ...................  1 linha
```

Os três arquivos de deploy tinham **escapado da divisão** que o resto do
projeto faz: `build_ativos.py` limpa CSS e JS desde sempre, mas
`_headers`, `_redirects` e `.htaccess` iam ao ar comentados — 42 linhas de
decisão interna em português num site EN-US. `sem_comentario_config()` fecha
isso, com a mesma regra dos três formatos: `#` no INÍCIO da linha é
comentário, `#` no meio não é (um valor de cabeçalho pode contê-lo, e um
`split('#')` quebraria a diretiva sem erro nenhum).

Conferido: `.htaccess` com blocos balanceados e aninhamento correto, e as
**75 diretivas idênticas** às da fonte. Só comentário saiu.

### O banner tinha função, e ela não foi jogada fora

O `/* GERADO por ferramentas/build_ativos.py — edite fonte/… */` existia para
impedir um acidente que **já aconteceu**: `memorianew.md` §94 registra o
usuário reescrevendo uma frase direto em `site/capabilities.html`, que o build
seguinte teria apagado sem dizer nada.

Apagar o banner sem substituir a guarda seria trocar 660 bytes por uma tarde
perdida. Entrou `conferir_mao()`: um manifesto de sha1 do que o último build
escreveu, comparado antes de sobrescrever.

> **A guarda passou de passiva a ativa.** O banner só servia se a pessoa
> abrisse o arquivo E lesse a primeira linha; a conferência **pega** a edição e
> avisa antes de sobrescrever. Zero byte no deploy, e mais eficaz.

Ela **avisa e não aborta**, de propósito: abortar transformaria um arquivo
editado por engano numa parede — o build inteiro pararia, e o jeito de sair
seria apagar exatamente o trabalho que se queria salvar.

Testado: editei `site/css/style.css` à mão, rodei o build, e ele avisou
nomeando o arquivo e a fonte.

`ferramentas/_publicado.json` é estado de build e entrou no `.gitignore`.

### Estado

```
27 arquivos publicados · 0 comentários
75/75 diretivas do .htaccess preservadas · blocos balanceados
0 erro de console nas dez páginas · 0 conflito · 0 falha de contraste
```
