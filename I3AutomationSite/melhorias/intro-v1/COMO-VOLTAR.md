# intro v1 — o estado salvo em 2026-08-27, antes do notebook

Snapshot pedido pelo usuário antes de trocar a intro:

> *"salve o estado atual da animação, caso eu nao goste do resultado
> conseguimos voltar no tempo."*

## O que a v1 era

O **lockup completo** (marca + wordmark, 3,530:1) revelado da esquerda para a
direita por `clip-path`, sobre campo `--sup-3`, e a frase se escrevendo com
cursor logo abaixo. Linha do tempo de 5,6 s:

```
0    -> 1,0s   o lockup é revelado da esquerda para a direita
1,0s -> 2,6s   a frase se escreve com o cursor
4,0s -> 5,6s   o véu levanta (WAAPI, main.js §5)
```

Ela já era a **segunda** intro do projeto. A primeira encaixava a marca glifo a
glifo e voava com FLIP até um destino no herói; morreu em 25/08 porque
desenhava o **redesenho** da marca, e porque o herói virou vídeo sem logo
dentro — não havia mais onde pousar. Essa história está em `design.md` §3.5 e
no comentário do próprio bloco salvo aqui.

## Os quatro pedaços

| arquivo salvo | de onde saiu |
|---|---|
| `style.css.bloco5.txt` | `fonte/css/style.css`, seção **5. INTRO** (linhas 614–874 na época) |
| `main.js.modulo5.txt` | `fonte/js/main.js`, módulo **5. Intro: o lockup se revela** (linhas 130–250) |
| `build_paginas.intro.txt` | o `intro_html` dentro de `pagina()` |
| `build_paginas.marca_lockup.txt` | `marca_lockup()` inteira |

## Como voltar

1. Em `fonte/css/style.css`, substituir a seção 5 inteira (do comentário
   `5. INTRO` até a linha antes de `6. HERÓI`) pelo conteúdo de
   `style.css.bloco5.txt`.
2. Em `fonte/js/main.js`, substituir o módulo 5 pelo conteúdo de
   `main.js.modulo5.txt`.
3. Em `ferramentas/build_paginas.py`, substituir o bloco `intro_html` de
   `pagina()` pelo de `build_paginas.intro.txt`, e `marca_lockup()` pelo de
   `build_paginas.marca_lockup.txt` se ela tiver mudado.
4. `python ferramentas/build_ativos.py && python ferramentas/build_site.py`

**Os assets de marca não mudam** entre v1 e v2 — as duas usam
`brand/logo-completo-branco-268.png`, que continua sendo gerado por
`build_marca.py`. Voltar é só CSS, JS e o HTML gerado; nenhuma imagem precisa
ser reconstruída.
