# Prompt — SEO e desempenho do Universo do CLP

> Cole isto inteiro numa sessão do Claude Code aberta no repositório
> `kaeve1/UnidoCLP`. Ele foi escrito depois de a mesma passada ser feita no
> projeto irmão (i3Automations), e carrega os números medidos do site
> publicado e as armadilhas que já custaram tempo lá.

---

## Contexto

Você está no **Universo do CLP** (`universodoclp.com.br`), site institucional
em PT-BR que vende treinamento em automação industrial pela Hotmart. HTML, CSS
e JS puros, sem framework e sem build step no deploy: publicar a pasta `site/`
é o deploy inteiro.

Hoje ele está em duas versões:

| | onde | o que é |
|---|---|---|
| antigo | `universodoclp.com.br` | WordPress 7.1, Apache, HostGator |
| novo | `universodoclp.pages.dev` | o site estático, com `X-Robots-Tag: noindex` |

O projeto irmão **i3Automations** usa o mesmo sistema de design e acabou de
passar por esta mesma auditoria. O `memoria.md` de lá registra cada armadilha
com a medição que a expôs — vale consultar quando algo aqui não fizer sentido.

**Sua tarefa: melhorar o SEO e o desempenho deste site, na ordem abaixo.**

---

## Regra número um

**Medir, não estimar.** Todo número deste prompt foi medido em **21/08/2026**
contra `universodoclp.pages.dev`. Eles são o ponto de partida, não a verdade
atual: **remedir antes de mexer** e **remedir depois** faz parte da tarefa.

Se um número seu contradisser um número daqui, o seu vence — desde que você
mostre como mediu.

---

## O que JÁ está certo. Não mexa.

Conferido página a página. Isto não é escopo, e "melhorar" aqui só cria risco:

- **Metadados completos nas 5 páginas** — `<title>`, `meta description`,
  `canonical`, `og:image`, `og:type`, `twitter:card`, `theme-color`, `lang="pt-BR"`.
- **29 de 29 imagens com `alt`.**
- **`defer` no `main.js`**, `loading="lazy"` em 24 imagens, fonte com `preload`.
- **Zero script de terceiro.** Nenhum analytics, nenhum pixel, nenhuma CDN.
- **CLS 0,000** nas cinco páginas, nos dois perfis. Não estrague isso: qualquer
  elemento novo que entre no fluxo depois da primeira pintura tem de ter espaço
  reservado antes.
- **`sitemap.xml` e `robots.txt`** já apontam para `universodoclp.com.br`.
- **As URLs do site novo são idênticas às do WordPress** (`/quem-somos/`,
  `/trabalhos-realizados/`, `/treinamentos/`, `/contato/`). **Não há um único
  301 a escrever** — se você se pegar escrevendo redirecionamento, parou de
  resolver o problema certo.

---

## Achados, em ordem de custo

### 1. A home REPROVA o Largest Contentful Paint

Medido no perfil móvel do Lighthouse (4G lento, CPU 4× mais lenta):

| página | FCP | **LCP** | TBT | CLS | transferido |
|---|---|---|---|---|---|
| `/` | 1416 ms | **3728 ms** | 0 ms | 0,000 | **765 KB** |
| `/quem-somos/` | 1504 ms | 1504 ms | 376 ms | 0,000 | 173 KB |
| `/trabalhos-realizados/` | 1492 ms | 1676 ms | 447 ms | 0,000 | 364 KB |
| `/treinamentos/` | 1340 ms | 1520 ms | 425 ms | 0,000 | 171 KB |
| `/contato/` | 1280 ms | 1480 ms | 219 ms | 0,000 | 209 KB |

O limiar de "bom" é **2500 ms**. A home passa dele em **1,2 segundo**.

O elemento LCP é `/img/heroi/cena-1800.avif`, que pinta aos **4236 ms**. Mas
**a culpa não é dele** — ele tem 157 KB e já está em AVIF. A culpa é do que
compete com ele pela banda, que é o achado 2.

### 2. A pasta `/brand/` ficou fora do pipeline de imagem

**Este é o achado principal.** A home baixa 765 KB, e **476 KB (62%) são quatro
PNGs em `/brand/`** — mais peso que a fotografia do herói.

| arquivo | peso | nativo | desenhado | excesso |
|---|---|---|---|---|
| `logo-completo.png` | **366 KB** | 1833 px | 432 px | **4,2×** |
| `logo-intro-branco.png` | 70 KB | 920 px | 720 px | 1,3× |
| `logo-nav.png` | 24 KB | 300 px | — | — |
| `logo-nav-branco.png` | 15 KB | 300 px | 107–196 px | 1,5–2,8× |

`logo-completo.png` tem **os dois problemas somados**: está em PNG num site que
serve AVIF e WebP em todo o resto, e tem 4,2× mais pixel do que a tela usa.

Conserto medido (redimensionar para 2× do tamanho desenhado, depois converter):

| | hoje | depois |
|---|---|---|
| os quatro logos | 474 KB | **69 KB** |
| **economia** | | **405 KB (−85%)** |

A home cairia de 765 KB para ~360 KB.

**Como fazer, e não é "rodar um conversor":**

- Os quatro têm **canal alfa** e são **arte com gradiente**, não arte chapada —
  `logo-completo.png` tem 13.153 cores únicas. Por isso PNG indexado não serve
  aqui (serviu no i3 porque lá as máscaras tinham RGB constante).
- Emita **AVIF + WebP + PNG de reserva** dentro de `<picture>`, que é o padrão
  que o resto do site já usa para fotografia. O PNG de reserva pode ser o
  redimensionado, não o original.
- **Redimensione para 2× do tamanho DESENHADO**, não para o nativo. Meça o
  tamanho desenhado no navegador; não confie no CSS lido à mão.
- `logo-intro-branco.png` é a exceção: 920 px nativos para 720 px desenhados é
  **menos** que 2×, então ali só o formato muda, não o tamanho.

### 3. TBT acima do limiar em três das cinco páginas

376, 425 e 447 ms medidos, contra um limiar de **200 ms**.

Perfilado, **não há uma função quente**: o `main.js:12` que aparece no topo é a
IIFE inteira (~98 ms sob CPU 4×), e o resto do tempo das tarefas longas é
`(program)` — trabalho interno do navegador, não JS.

Ou seja: é **custo de inicialização espalhado pelos 14 módulos**, mais decode e
layout das imagens do carrossel. Isso muda a abordagem:

- Perfile no repositório com o profiler ligado (ver "Método") e veja **quais
  módulos** custam. Os candidatos são os que leem layout na inicialização.
- Onde houver trabalho pesado, **fatie por orçamento de TEMPO, não por
  contagem**. A lição do i3: um orçamento em contagem calibrado no desktop vira
  uma tarefa de 200 ms no celular, que é justamente quem precisa da proteção.
  Lá, `requestAnimationFrame` com orçamento de 8 ms levou o TBT de 488 → 0 ms
  **sem mudar um único vértice do resultado**.
- Módulo que só importa quando o elemento dele entra na tela deve inicializar
  no `IntersectionObserver`, não na carga.

**Antes de otimizar, prove que o resultado não muda.** No i3 a prova foi rodar
os dois motores no mesmo dado e comparar as saídas byte a byte.

### 4. Qualquer endereço errado devolve HTTP 200 com a home

Conferido: `universodoclp.pages.dev/xyz-nao-existe` → **200**, servindo a home.

Não existe `404.html`. É o comportamento padrão do Cloudflare Pages, e no
domínio real significa que **cada URL errada vira uma cópia da home aos olhos
do buscador**, multiplicada por quantos links quebrados apontarem para lá.

Crie `404.html` com:
- `<meta name="robots" content="noindex, follow">`
- **sem `<link rel="canonical">`** — canônica numa página `noindex` é sinal
  contraditório: uma diz "indexe esta URL", a outra diz "não indexe", e o
  buscador resolve o empate como quiser. Página de erro não tem canônica, tem
  status.
- caminho de saída visível **sem rolar** — o bloco de contato inteiro, não só
  um link "voltar".

### 5. Não existe `.htaccess`, e o site usa AVIF

25 referências a `.avif` só na home. **Se o Apache não conhecer esse tipo, ele
entrega como `application/octet-stream` e o `<picture>` não pinta nada** — o
site fica sem fotografia, e sem um erro no console.

O `.htaccess` completo para este site já está escrito no runbook de publicação
entregue junto. Ele precisa de: `ErrorDocument`, `AddType image/avif`,
`mod_deflate`, `mod_expires`, cabeçalhos de segurança, e 410 para os restos do
WordPress (`/feed/`, `/wp-json/`, `/xmlrpc.php`).

Não há bloco de redirecionamento nele, pelo motivo do topo: as URLs não mudam.

### 6. `apple-touch-icon` aponta para um SVG

```html
<link rel="apple-touch-icon" href="/brand/favicon.svg">
```

**O iOS ignora `apple-touch-icon` em SVG.** Quem salvar o site na tela inicial
do iPhone recebe um retrato da página, não a marca. Faltam também:

- `favicon.ico` **na raiz** — o navegador pede `/favicon.ico` sozinho, sem
  consultar link nenhum, e o buscador olha para lá. Hoje é 404 em toda visita.
- `site.webmanifest` com ícones 192 e 512 — sem ele o Android amplia o favicon
  de 32 px no atalho.

Gere tudo **a partir do mesmo SVG**, por captura em navegador headless. Não
redesenhe a marca em código: seria uma segunda cópia da geometria, e no dia em
que o logo mudar o site teria duas marcas diferentes.

O `apple-touch-icon` deve ser PNG **opaco** — o iOS compõe sobre preto, e alfa
ali engrossa a silhueta.

### 7. Uma `og:image` para as cinco páginas, e sem dimensões

```html
<meta property="og:image" content="https://universodoclp.com.br/img/og/og-1200.jpg">
```

Faltam `og:image:width`, `og:image:height` e `og:image:type` — sem eles a rede
social precisa baixar a imagem antes de saber o formato do card, e às vezes
desiste.

E uma imagem só para cinco páginas faz todo compartilhamento parecer o mesmo
link. Gere **uma por página**, a 1200×630, do mesmo recorte que o cabeçalho
daquela página usa. **Confira que a fonte é maior que 1200×630** — ampliar
aparece justamente no card, que é onde a primeira impressão acontece.

### 8. Dois textos passam do que o Google mostra

| página | problema |
|---|---|
| `/` | título com **67 caracteres** (o corte fica em ~60) |
| `/trabalhos-realizados/` | descrição com **172** (o corte fica em ~155) |
| `/treinamentos/` | descrição com **183** |

Cortar não é só encurtar: o que sobra tem de continuar sendo a frase que faz
alguém clicar. Reescreva, não trunque.

### 9. Dados estruturados faltam em duas páginas

`/quem-somos/` e `/trabalhos-realizados/` não têm `application/ld+json`. As
outras três têm.

Acrescente pelo menos `BreadcrumbList` nas duas — sem ele o buscador exibe a
URL crua no lugar da trilha. E confira se há uma `Organization` na home com
nome, logo, URL e os canais de contato.

---

## Método

### Monte o aparato de medição antes de mexer em qualquer coisa

O i3 tem isso pronto e **os arquivos são portáveis** — copie e ajuste:

| arquivo | o que faz |
|---|---|
| `ferramentas/movel/cdp.mjs` | driver de Chrome headless por CDP, sem puppeteer e sem dependência |
| `ferramentas/velocidade/servir.mjs` | servidor local que **imita a hospedagem**: gzip e `Cache-Control` iguais aos de produção |
| `ferramentas/velocidade/medir.mjs` | LCP, CLS, TBT e bytes, por página, nos dois perfis |
| `ferramentas/velocidade/recursos.mjs` | o que pesa numa página, por arquivo |
| `ferramentas/velocidade/tarefas.mjs` | quem bloqueia a thread principal, e por quanto tempo |
| `ferramentas/velocidade/testar_htaccess.sh` | sobe um Apache 2.4 em container com o site e o `.htaccess` |
| `ferramentas/velocidade/rotas.sh` | bateria de rotas contra esse Apache |
| `ferramentas/velocidade/validar_producao.sh` | confere um site já no ar (perfil `clp` já existe lá) |

O perfil móvel é o do Lighthouse: **4G lento (1,6 Mbps / 150 ms) e CPU 4×**.

### Não dá para "rodar o PageSpeed" enquanto o domínio não apontar para cá

O PageSpeed Insights é serviço do Google e precisa de URL pública. O que dá, e
é o que estes números são, é medir **as mesmas métricas no mesmo motor com o
mesmo estrangulamento**. Depois da troca de domínio, use `psi.mjs`.

---

## Armadilhas já pagas. Não pague de novo.

Cada uma destas custou tempo no i3 e está documentada lá com a medição que a
expôs.

1. **Servidor de medição sem `Cache-Control` inventa download duplicado.** Um
   arquivo com dois consumidores (`mask-image` no CSS e `new Image()` no JS)
   aparece baixado duas vezes. Foram 720 KB de defeito que só existia na régua.

2. **Certificado autoassinado também inventa o mesmo defeito.** O Chrome **não
   guarda em cache resposta vinda de origem com certificado inválido**. Isolado
   com o mesmo servidor e o mesmo conteúdo: 847 KB em http contra 1183 KB em
   https autoassinado.

3. **`httpd -t` NÃO valida `.htaccess`.** Ele diz "Syntax OK" e o primeiro
   pedido devolve 500. O arquivo só é interpretado no momento do pedido, por
   diretório. **Teste com uma requisição de verdade.**

4. **O Apache só reconhece `#` no INÍCIO da linha.** Escrever
   `ExpiresByType image/jpeg "..." # imagens` faz o rótulo virar argumento
   extra, e a diretiva aceita exatamente dois. Resultado: **HTTP 500 em todas
   as páginas**.

5. **Antes de reprovar uma escolha nova, meça a que já está publicada.** Se a
   sua régua condena o que já está no ar e aprovado, a régua está errada, não a
   peça.

6. **Camada nova `position: fixed` tem de ser testada com o menu ABERTO, no
   aparelho mais baixo.** No i3, uma faixa em `z-index: 900` cobriu o CTA
   primário do menu mobile no iPhone SE — `elementFromPoint` no centro do botão
   devolvia a faixa, não o botão.

7. **No Git Bash, `/` dentro de variável de ambiente vira caminho do Windows.**
   `PAGINAS="/"` chegou ao Node como `C:/Program Files/Git/` e a home
   simplesmente não foi medida. Use `MSYS_NO_PATHCONV=1`.

8. **Valor de cor literal em componente que atravessa temas é bug esperando
   data.** Este site tem tema claro e escuro; toda cor nova sai de token.

---

## Ordem sugerida

1. Remedir tudo e guardar o antes.
2. `/brand/` no pipeline de imagem — é o maior ganho e o mais barato.
3. Remedir a home. O LCP deve entrar na faixa boa aqui.
4. `404.html` e `.htaccess`, testados em Apache real.
5. Família de ícones completa.
6. `og:image` por página, com dimensões.
7. Títulos e descrições dentro do limite; JSON-LD nas duas páginas que faltam.
8. TBT: perfilar, e só então mexer — com prova de que a saída não muda.
9. Remedir tudo e comparar com o antes, número a número.
10. Registrar no `memoria.md` do projeto: o que mudou, o que foi medido, e todo
    beco sem saída. **Especialmente os becos** — é o que impede a próxima
    sessão de repetir o caminho.

---

## Critérios de aceitação

Nada disto é opinião. Tudo é medível, e a entrega só fecha com os números na
mesa:

| critério | alvo |
|---|---|
| LCP, perfil móvel, nas 5 páginas | **< 2500 ms** |
| TBT, perfil móvel, nas 5 páginas | **< 200 ms** |
| CLS, nas 5 páginas | **≤ 0,010** (hoje é 0,000 — não piore) |
| peso da home | **< 400 KB** |
| endereço inexistente | **HTTP 404**, servindo a `404.html` do projeto |
| `.htaccess` em Apache real | bateria de rotas **N/N** |
| `/favicon.ico` | **200** |
| `apple-touch-icon` | **PNG**, 180×180, opaco |
| `og:image` | **uma por página**, 1200×630, com `width`/`height`/`type` |
| títulos | **≤ 60 caracteres** |
| descrições | **≤ 155 caracteres** |
| JSON-LD | **5 de 5 páginas** |
| referências quebradas e arquivos órfãos | **0** |

---

## Uma nota sobre o que NÃO fazer

Não instale analytics. Este site não tem script de terceiro nenhum hoje, e isso
é um ativo — de privacidade, de desempenho e de simplicidade. Se alguém pedir
medição de audiência, traga a decisão para o dono antes de escrever a tag, e
apresente as opções sem cookie primeiro.

E não troque a tipografia, a escala ou os pesos. Eles são herdados e
intocáveis por regra do projeto: **título grande é peso leve, e nada passa de
500 em lugar nenhum.**
