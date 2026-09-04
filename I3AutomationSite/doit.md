# doit — plano de execução da revisão de 2026-08-25

> ## Começar aqui
>
> **Sessão nova:** leia nesta ordem — `memorianew.md` (o que já foi medido e
> decidido, e os becos sem saída), `design.md` (o sistema), `plano.md` (o que vai
> em cada página, incluindo a definição de "clean" em 10 regras e os redlines),
> e então este arquivo.
>
> **A Fase 0 está concluída.** O trabalho começa na **Fase 1 — Tokens**, que
> bloqueia todo o resto.
>
> **Não existe decisão pendente que bloqueie a execução.** O único item aberto
> (`--fs-display` sobre o vídeo) é verificação de tela na Fase 5, e entra com o
> valor herdado.

Ordem importa. Cada fase assume as anteriores prontas. As decisões que
justificam cada item estão em `design.md` e `plano.md`; as medições e becos sem
saída, em `memorianew.md`.

**Escopo desta rodada: as 9 páginas, redesenho completo.**

---

## Fase 0 — Preparação

**Esta fase está concluída.**

- [x] ~~Destino das skills do `uipro init`.~~ `.gitignore` criado — as sete pastas
      (CC-BY-NC-4.0, trabalho comercial pago) ficam fora do versionamento.
- [x] ~~Marcar `specs/design.md` como superado.~~ Bloco de aviso no topo do arquivo.
- [x] ~~Atualizar `CLAUDE.md`.~~ Regras críticas 4 e 5 reescritas, regra 6 (tema
      único) acrescentada, e os ponteiros agora apontam para os quatro documentos
      correntes.

---

## Fase 1 — Tokens (bloqueia todo o resto)

- [x] **Reescrever `fonte/css/tokens.css`** com a paleta de `design.md` §1.2.
      Entram: `--azul #4D8ECB`, `--azul-txt #2C6396`, `--azul-luz #88B4DD`,
      `--azul-bloco #0D4477`, `--azul-chip #DCE9F5`, `--quente #F7F3EC`.
      Saem: `--dourado`, `--dourado-txt`, `--navy-fundo`, `--navy-tinta`,
      `--navy-chip`, `--navy-luz`, `--accent-txt`.
- [x] **Remover o bloco de tema escuro inteiro** — o `@media (prefers-color-scheme: dark)`
      e o `[data-tema="escuro"]`. Tema único, claro.
- [x] **Varredura de `#FDC500` no CSS de página.** O alvo é **zero ocorrências**
      fora dos assets de logo. Mesma varredura para `#001D3D`, `#000814`,
      `#6B5000`, `#D7E3F0`, `#8FB4DC`.
- [x] **Recalcular todo contraste que dependia dos tokens mortos** e registrar
      em `memorianew.md`. Regra do projeto: número no CSS tem conta atrás.

## Fase 2 — Remoção do alternador de tema

- [x] Remover o botão `.tema` do nav (`build_paginas.py` / `build_site.py`).
- [x] Remover o script inline de `localStorage` do `<head>` das 9 páginas.
- [x] Remover a lógica de alternância de `fonte/js/main.js`.
- [x] Remover as duas `<meta name="theme-color">` por esquema; deixar uma só.
- [x] Conferir as peças que ficam (`mimico`, `malha`, `carta`): as três reagem a
      troca de tema via `tela.js`/`gl.js`. Esse caminho vira código morto —
      remover, não deixar pendurado.

## Fase 3 — Logo

- [x] ~~Mover os PNGs de marca para o repositório.~~ **Feito** —
      `referencia/marca/`, 13 arquivos: `logo-original.png` mais lockup e marca
      isolada, navy e knockout, em 96/192/288px. O build publica em `site/brand/`.
- [x] **Script de geração do logo** em `ferramentas/`, com o método de
      `design.md` §3.4: quantizar para as 7 cores exatas → flood fill da borda
      atravessando não-dourado → knockout do que for alcançado → downsample
      LANCZOS. Nunca bounding box.
- [x] **Reescrever `ferramentas/build_icones.py`.** Hoje ele deriva favicon e
      ícones do SVG redesenhado (linhas 28, 93, 116–118). A fonte de verdade
      passa a ser `logo/logonova.png`. É troca de fonte, não patch.
- [x] **Nav: marca isolada + nome em Outfit** (`design.md` §3.3). O lockup
      completo não entra no nav — medido, o wordmark fica em 8,8–11px.
- [x] **Lockup completo** na intro, no rodapé e na imagem OG.
- [x] **Reescrever a intro**: de encaixe glifo a glifo para animação do logo
      inteiro (translate/scale/clip). Some `data-intro-destino` e `data-encaixe`.
- [x] **Escrever a isenção** de cantos retos e família única no `CLAUDE.md`.

## Fase 4 — Pipeline de vídeo

- [x] **`ferramentas/build_video.py`.** Lê `Videos/`, corta, escala para 1080p,
      **remove a faixa de áudio**, encoda h264 (CRF 26, preset slow,
      `+faststart`) mais alternativa AV1/VP9, e gera poster de cada um.
      Binário: `imageio_ffmpeg.get_ffmpeg_exe()` → ffmpeg 7.1.
- [x] **Escolher o trecho de cada clipe.** `estacaoagua.mp4` (momento 1) e
      `elemnetotecnologicodeesteira.mp4` (momento 2, **cortado fechado nos bicos e
      atuadores** — se abrir na célula solar, a home vira monotemática, `plano.md`
      §5.5). Loop de ~10s, sem corte.
- [x] **Conferir o orçamento**: ~3 MB por loop, ~9 MB no total, teto de 25 MB
      por arquivo do Cloudflare Pages.

## Fase 5 — Home

- [x] **Herói em vídeo full-bleed** (`plano.md` §3): `Videos/heroi/heroi.mp4`,
      3840×2160. **`-vf hflip` obrigatório** — sem ele o H1 reprova a 1,34:1.
      Véu navy de 25% (6,63:1). H1 branco peso 300, entrada linha a linha.
- [x] **Encodar o herói com CRF próprio, medido.** Véu de 25% esconde muito menos
      artefato que os 62% dos momentos — não herdar o CRF 30 deles.
- [x] **O herói é a única mídia que carrega adiantado**: poster com
      `fetchpriority="high"`, `preload` liberado. Os momentos ficam em `none`.
- [x] **Conferir `--fs-display` na tela** sobre o vídeo. Entra como está; só mexer
      se falhar.
- [x] **Remover `data-braco` e `data-planta`** da home.
- [x] **Componente `.filme`** — porte do UnidoCLP: trilho de 220vh (180vh no
      mobile), palco sticky de 100vh, `clip-path: inset()` por `--p`,
      texto por `--t`. **Scrim de dois gradientes obrigatório.**
- [x] **Variação A** — janela fixa que não abre, coluna de texto rolando ao
      lado com reveal linha a linha.
- [x] **Variação B** — parallax de camadas com fotografia, sem vídeo.
- [x] **Blocos de texto** antes de cada momento: eyebrow → H2 → parágrafo → CTA.
- [x] **IntersectionObserver** dando play/pause, `preload="none"`, poster em
      todos. Um vídeo decodificando por vez.
- [x] **`prefers-reduced-motion`** desligando os três momentos inteiros.

## Fase 6 — As outras 8 páginas

- [x] `who-we-are.html` — remover `data-marca`; cabeçalho novo.
- [x] `capabilities.html` — remover `data-clp`; cabeçalho novo.
- [x] `past-performance.html` — **mantém `data-mimico`**, repaginado para o
      vocabulário claro.
- [x] `services.html` — **mantém `data-malha`**, repaginado.
- [x] `gallery.html` — mantém `data-mosaico`; aplicar a regra de legenda.
- [x] `contact.html` — **mantém `data-carta`**, repaginado.
- [x] `404.html` — **recebe o braço** (`braco.js`) como easter egg.
- [x] `privacy-policy.html` e `terms-and-conditions.html` — só tokens.

## Fase 7 — Fotografia

- [x] **Curar o acervo por assunto.** 33 de galeria, 6 de setor, 6 de cabeçalho,
      4 do componente duplo. Cada página recebe o que **fecha com o assunto**.
- [x] **Reescrever todo `alt` e toda legenda** conforme `design.md` §7.1:
      descreve o que a imagem mostra, **nunca afirma autoria**. O cliente é
      fornecedor federal — legenda que afirma obra não verificável é risco real.

## Fase 8 — Verificação

- [x] `ferramentas/varredura.py` — referências quebradas e órfãos. Alvo: 0 e 0.
- [x] `ferramentas/contraste.py` — a matriz inteira da paleta nova. **Agora com
      metade do tamanho**, porque só há um tema.
- [x] `ferramentas/conflitos.py` e `repetidas.py` no CSS reescrito.
- [ ] **Verificar no navegador de verdade**: os três momentos a 60 quadros
      convivendo com a inércia da roda e com o rodapé sticky. É o único item que
      nenhuma medição fora do navegador responde.
      **PARCIAL — falta a parte que só uma aba em PRIMEIRO PLANO responde.**
      A aba de automação abre em segundo plano (`visibilityState: "hidden"`), e
      nesse estado o Chrome não entrega `requestAnimationFrame` nem carrega
      mídia. Ou seja: `--p` não avança, os momentos não animam e nenhum vídeo
      decodifica. **Verificado assim mesmo:** layout das treze dobras, estado
      inicial dos momentos (janela fechada, traço por desenhar), contraste de
      cada faixa, e o build limpo. **Falta medir:** os três momentos a 60
      quadros junto com a inércia da roda, o parallax e o rodapé sticky —
      exatamente o risco que `design.md` §6.1 registra. A saída, se ficar
      pesado, já está decidida: **a inércia cai primeiro**, não os momentos.
- [x] `ferramentas/build_ativos.py` e `build_site.py` — build limpo das 9.

---

## Abertos — precisam de decisão antes das fases que dependem deles

| # | Aberto | Bloqueia |
|---|---|---|
| 1 | ~~Qual mídia vira o herói~~ | **fechado** — vídeo 4K full-bleed, `hflip`, véu 25% (`plano.md` §3) |
| 2 | **`--fs-display` sobre o vídeo** — entra como está; conferir na tela e só mexer se falhar | Fase 5, não bloqueia |
| 3 | ~~Assunto do momento 3~~ | **fechado** — macro do módulo de relés com traço |
| 4 | ~~Onde moram os assets de marca~~ | **fechado** — `referencia/marca/` |
| 5 | ~~O hover dos botões~~ | **fechado** — `plano.md` §6, medido |
| 6 | **Material extra de vídeo** — painel/MCC, operador em HMI, oil & gas. Não bloqueia; o momento 3 é foto justamente por isso | — |

---

## Ampliação de 2026-08-26 — a home passou a ter quatro momentos

Pedido do usuário depois de ver a home publicada: mais vídeo ao rolar, animação
de rolagem, e o fim das imagens repetidas. **O herói não foi tocado.**

- [x] **Inventário real do acervo de vídeo.** 14 arquivos e 645 MB, não os 8 e
      441 MB que `memorianew.md` §5 registrava. Entre os que ninguém tinha
      aberto estavam `ihm.mp4` (operador na tela) e `automacaorobo2.mp4`
      (atuadores) — o material que o §9 pedia ao cliente.
- [x] **Quarto momento e terceiro mecanismo.** `variação C`: duas portas
      correm e descobrem o vídeo, atadas a `--p`, só por `transform`.
- [x] **A esteira saiu, os atuadores entraram.** O clipe da esteira não tinha
      bico nem atuador — tinha polia e correia com solar passando.
- [x] **Oil & gas ganhou o momento 4**, com o traço extraído da própria foto.
      Era o único vertical sem nenhuma peça de mídia no site inteiro.
- [x] **`repetidas.py` passou a comparar PIXEL** (dHash), e não nome de
      arquivo. `gas.jpg` estava em cinco lugares, duas vezes na mesma página.
- [x] **A grade de setores saiu da home** — fecha a tensão da regra 7 e a
      duplicata de oil & gas na mesma dobra.
- [x] **A variação A ganhou trilho.** O `sticky` não engatava: a coluna cabia
      numa tela e o mecanismo simplesmente não acontecia.
- [x] **`.rolagem`** — revelação atada à posição de rolagem, não a um gatilho
      de entrada: subir a página desfaz o avanço.
- [x] **O WebM é descartado quando não ganha.** O deslocamento de CRF do VP9
      depende do assunto; a garantia virou estrutural em vez de calibrada.

## Segunda rodada de 2026-08-26 — sustentação e montagem

Sete pedidos do usuário. **O herói não foi tocado.**

- [x] **Sustentação nos momentos.** `--fim-abre` separa o curso em abrir e
      PERMANECER: 99vh de filme parado em tela cheia, 81vh nos momentos 2 e 3.
      Antes o vídeo existia em tamanho cheio por um quadro.
- [x] **A segunda seção cresce até tela cheia.** Era a única que nunca ocupava
      a janela — daí não agradar. Coluna de texto ao lado na fase 1, tela cheia
      e parada na fase 2.
- [x] **O momento 1 virou montagem** de quatro cortes de 4,5s: água, célula
      com robô, engenheiro, detalhe de máquina. 18s, corte seco.
- [x] **Traços removidos** do momento 4 (a refinaria já é toda aresta).
- [x] **Barramento removido** de who-we-are (regra 5: separação por espaço).
- [x] **Movimento nas internas** — parallax de cabeçalho e de fundo
      fotográfico, números entrando um a um. Custo zero em bytes.
- [x] **`html.js`** — 12 regras deixaram de esconder conteúdo quando não há JS.
- [x] **`transition` removida** da máscara atada à rolagem: a rolagem já é a
      linha do tempo, e a transição só acrescentava atraso elástico.

## Terceira rodada de 2026-08-26 — a home virou um sistema

*"Vídeo pequeno + um texto, vídeo grande + outro texto — três vezes."*
**O herói não foi tocado.**

- [x] **Três unidades no mesmo formato**, saindo de uma função só: atuadores
      (a linha), operador na tela (o controle), engenheiro (o projeto).
- [x] **A informação do site foi para dentro do sistema.** A coluna de cada
      unidade É o bloco de texto — eyebrow, H2, parágrafo e CTA. Os blocos
      soltos entre os momentos saíram; sobrou o de abertura.
- [x] **A dobra da refinaria virou vídeo.** Oil & gas continua no site por
      `setor/oil-gas`, em past-performance.
- [x] **A montagem perdeu `pc.mp4`** (3 cortes, 13,5s): ele virou a unidade 3.
- [x] **`:where(html.js)`** — a guarda subia a especificidade e vencia todo
      reset escrito depois, inclusive dentro de media query. A coluna de texto
      do celular não aparecia.
- [x] **O ramo de celular da unidade foi refeito**: o vídeo `absolute` cobria
      o texto, e a frase da dobra estava escondida.
- [x] **A ordem do HTML virou a do celular** (coluna, janela, rodapé) porque
      `order:` no flex não muda a ordem de tabulação.

> **Contradiz `design.md` §5** ("o mecanismo muda a cada volta"). A regra foi
> escrita antes de existir uma dobra deste tipo no ar; o usuário viu a dobra
> pronta e pediu a repetição. Revogada por decisão, não por esquecimento —
> ver `memorianew.md` §39 para o que a repetição custa.

## Quarta rodada de 2026-08-26 — revisão de layout (skill `impeccable`)

- [x] **Duas seções de texto novas**, uma delas sobre o neutro quente. A copy
      vem de who-we-are e past-performance, já verificada — não foi escrita.
- [x] **O neutro quente voltou ao site.** Ele tinha sumido de TODAS as páginas
      quando consolidei os blocos de texto, e ele é a correção da causa raiz do
      feedback do cliente (`design.md` §0).
- [x] **Unidades alternam esquerda/direita.** Sem isso o teste de meio-fechar
      os olhos não distinguia a unidade 1 da 2 nem da 3.
- [x] **`ch` estava mentindo.** Em Outfit o glifo "0" mede 13,09px contra
      8,52px do caractere médio: `62ch` entregava 104 caracteres por linha.
      Trocado por `em` medido — agora 70–74.
- [x] **O vão entre título e corpo era zero px** em todo bloco do site.
- [x] **Barra de rolagem, cursor e `accent-color`** entraram na paleta.

> A skill não está registrada no harness; foi lida de `.claude/skills/`. O
> detector dela roda DEGRADADO (faltam `htmlparser2`, `css-select`,
> `css-tree`, `domutils`) e devolve `[]` por regex — subcontagem, não
> atestado. A avaliação foi feita à mão.

## Quinta rodada de 2026-08-26 — vídeos, creme e o topo

- [x] **BUG CORRIGIDO: o CTA da unidade não era clicável.**
      `.unidade__coluna { pointer-events: none }` matava o botão dentro dela.
      O CTA foi para o rodapé, que fica visível durante a sustentação inteira,
      e ganhou guarda de `visibility` — `opacity: 0` não tira nada do teste de
      acerto nem da ordem de tabulação. Verificado por `elementsFromPoint`.
- [x] **Method voltou ao `ihm` reconhecível** (4,0→14,0s, com a interface e a
      mão do operador). O corte anterior mostrava só números.
- [x] **Unidade 3 → `placassolares4`.** Muda o registro: depois de dois
      interiores, sair para o campo. A frase mudou junto, porque a antiga era
      do tanque e da tocha.
- [x] **O creme saiu.** `.secao--quente` pinta `--sup-2`; o token fica.
- [x] **O topo virou o texto do site original** — sem a caixa alta, que o
      redline 9 proíbe em bloco.
- [x] **Dobra fundida**: "what we actually do" + números + "what follows".
- [x] **Plataformas → as oito disciplinas** de capabilities.
- [x] **Uma imagem para governo + CTA**, no componente `.dupla`, como
      who-we-are. Contraste medido antes de entrar (5,15:1 no véu aberto).

## Risco principal

**Fase 8, item do navegador.** A home vai carregar, ao mesmo tempo: inércia de
roda sequestrando o `wheel`, três momentos lendo progresso de rolagem, parallax,
um rodapé sticky e — nas internas — WebGL. Nada disso foi medido junto ainda.

`design.md` §6.1 já registra a saída se ficar pesado: **a inércia é a primeira
coisa a cair**, não os momentos. Ela é a única peça do conjunto que sequestra a
roda, e é a que menos o cliente pediu.
