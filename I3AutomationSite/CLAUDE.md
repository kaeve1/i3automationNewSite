# i3Automations — Projeto do Site

Site institucional da **i3Automations & Controls** (Lakewood Ranch, Flórida, EUA): integração de automação industrial — painéis de controle, programação de CLP/PLC, SCADA, comissionamento, instrumentação. Atende Oil & Gas, água e esgoto, automotivo, papel e celulose, solar/renováveis, e é fornecedora do governo federal americano. Empresa em operação desde 2000.

Este projeto é uma **variação do sistema de design do Universo do CLP** (github.com/kaeve1/UnidoCLP), feito para o mesmo cliente no Brasil.

## Regras críticas

1. **Se algum pedido contradisser o que já está em `design.md` (paleta, tipografia, tom, estrutura, movimento), pare e avise antes de mudar qualquer coisa.** Não sobrescreva decisão de design em silêncio — confirme explicitamente primeiro.
2. **A tipografia é intocável.** Família, escala, pesos, entrelinhas e tracking foram herdados **exatos** do UnidoCLP a pedido do usuário. Nenhum valor de tipo se altera sem confirmação explícita. Em especial: **título grande = peso leve** (H1 e H2 em 300) e **nada acima de peso 500 em lugar nenhum**.
3. **Medir, não estimar.** Cor vem de amostragem de pixel; contraste, da fórmula WCAG; espaçamento, de valor medido. Se um número entrar no CSS, tem que existir a conta que o produziu — e ela vai para `memorianew.md`.
4. **`#FDC500` só existe dentro do logo.** Zero ocorrências no CSS de página — nem régua, nem barra, nem ícone, nem número, nem hover, nem foco. O accent do site é `--azul #4D8ECB`, derivado do navy da marca. *(Revisto em 2026-08-25; a regra anterior tratava o dourado como accent de página.)*
5. **O logo é a única exceção à regra de cantos retos e à regra de família tipográfica única.** A arte real é arredondada, facetada e usa duas faces de fora do sistema. Nenhum outro elemento herda isso por proximidade. *(Revisto em 2026-08-25.)*
6. **Tema único, claro.** Não existe mais alternador claro/escuro.

## Regras gerais

- **Idioma do site: EN-US** (confirmado com o usuário em 2026-08-18). A **documentação interna** — este arquivo, `design.md`, `plano.md`, `doit.md`, `memorianew.md` — fica em **PT-BR**, porque quem lê é o usuário.
- **Stack: HTML + CSS + JS puro.** Sem framework (nada de React/Vue/Astro), sem build step **no deploy** — publicar a pasta `site/` é o deploy inteiro. Manter isso ao propor qualquer estrutura de pastas, componentização ou ferramenta.
- **`fonte/` é onde se edita; `site/` é o que se publica.** CSS e JS moram comentados em `fonte/css/` e `fonte/js/`; `ferramentas/build_ativos.py` publica em `site/` sem comentário (−54%: 402 → 184 KB). **Editar `site/css` ou `site/js` direto é trabalho perdido** — o próximo build sobrescreve. Cada arquivo publicado abre com um banner dizendo isso.
- **O HTML de `site/` também é gerado** (`ferramentas/build_site.py`), junto com `sitemap.xml` e `robots.txt`. Nada em `site/` se edita à mão.
- **Fonte servida localmente** (`site/fonts/`), nunca por CDN.
- **Todo o conteúdo relevante do site atual** (https://i3automations.com/) deve aparecer no site novo: serviços, capacidades, plataformas, certificações, credenciais federais (UEI/CAGE/NAICS), números, contatos, redes sociais, páginas legais. Nada se perde na migração — só muda a forma.
- **Cantos retos em tudo, exceto o logo** (regra crítica 5). Sem `border-radius`, sem sombra em botão.
- **Decidir cedo se os caminhos do HTML são absolutos ou relativos** — no UnidoCLP os caminhos absolutos amarraram o site à raiz de um domínio e eliminaram opções de hospedagem.
- Antes de decidir algo que `design.md` e `plano.md` não resolvem sozinhos, **pergunte ao usuário em vez de assumir**.
- **Registre em `memorianew.md` toda decisão, medição e beco sem saída** — é o arquivo de recuperação de contexto do projeto, e o que sustenta a continuidade entre sessões.
- **`plano.md` §1 define "clean" em 10 regras verificáveis.** Toda seção precisa passar nas dez. `plano.md` §8 lista os redlines.

## Onde estão as decisões

**Revisão de 2026-08-25 — estes quatro são a fonte de verdade corrente:**

- @design.md — o sistema: paleta medida, tipografia, logo, movimento, o que morreu do spec antigo.
- @plano.md — o que vai em cada página, a definição operacional de "clean" (10 regras) e os redlines.
- @doit.md — ordem de execução em 8 fases, com dependências.
- @memorianew.md — medições, decisões e becos sem saída. **Ler primeiro ao entrar no projeto.**

**Histórico, não use para decidir:**

- `specs/design.md` — **superado**; o que sobreviveu está citado em `design.md`.
- `memoria.md` — válido até 24/08. Contém um erro de fato corrigido em `memorianew.md` §6: ffmpeg **existe** neste ambiente.

## Onde estão os arquivos

- `referencia/marca/` — **os assets de marca em uso**: `logo-original.png` (a arte do cliente), mais lockup e marca isolada, versão navy e knockout. Alturas: marca em 32/64/96/192/268, lockup em 96/192/268. **268 é a altura NATIVA do recorte** — `build_marca.py` recusa qualquer pedido acima dela, porque foi assim que os arquivos `-288` viraram resolução falsa (ampliação LANCZOS de 1,07x gravada como se fosse 3x).
- `referencia/i3automations/` — logo real do cliente (`logo-i3.png`, idêntico ao `logo-original.png`) e captura da home atual (`home-atual.html`).
- `Videos/` — 8 clipes 4K (441 MB) para os três momentos. ffmpeg vem de `imageio_ffmpeg.get_ffmpeg_exe()`.
- `referencia/goal/` — referências de estilo e capturas medidas.
- `ferramentas/` — scripts Python de análise (amostragem de cor, cálculo de contraste, build de imagens). Exigem `Pillow`, que está disponível no ambiente.
- `fonte/` — **o CSS e o JS que você edita**, comentados. É aqui que se trabalha.
- `site/` — o que será publicado, **inteiramente gerado**: HTML, CSS e JS enxutos, `sitemap.xml`, `robots.txt`. Não editar.

## Referência de origem

O sistema herdado está em github.com/kaeve1/UnidoCLP, no ar em https://universodoclp.pages.dev/. Os arquivos que definem o que foi herdado: `specs/design.md`, `site/css/tokens.css`, `site/css/style.css`. **Ao consultar, use os arquivos do repositório — não o site renderizado**, que dá valores aproximados.
