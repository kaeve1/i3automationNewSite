# Memória do Projeto — i3Automations

Arquivo de recuperação de contexto. Se você é um agente entrando neste projeto sem histórico, **leia este arquivo primeiro** e depois `specs/design.md`. Registro em ordem cronológica, **mais recente no topo**.

Regra do arquivo: aqui entra o que **não é dedutível do código** — decisões, motivos, medições, becos sem saída e armadilhas. O que o CSS já diz, o CSS diz melhor.

---

## 2026-08-21 (prancha) — O motor troca de leitura sozinho quando a peça muda de altura

Reportado no celular: *"as primeiras imagens da home demoram muito a aparecer e
não chegam no momento certo — só carrega quando está visualizando a segunda."*

O `memoria.md` já registrava queixa quase idêntica em 20/08, e o conserto de lá
resolveu **para desktop**. Este é o mesmo sintoma por causa diferente.

### Não era rede, e provar isso mudou o rumo

Primeiro reflexo seria mexer em carregamento. Medido antes:

```
imagens baixadas antes de qualquer rolagem:
  folha 1  baixada: true    folha 3  baixada: true
  folha 2  baixada: true    folha 4  baixada: true
```

**As quatro já estavam no navegador.** O `fetchpriority="high"` de 20/08 faz o
trabalho dele. O que chegava tarde era a **opacidade**.

### O motor tem DUAS leituras, e a peça mudava de leitura sem mudar de código

`main.js §7` escolhe pela altura do próprio elemento: peça mais BAIXA que a
janela usa a travessia inteira; peça mais ALTA usa `altura − janela`, que só
começa a contar quando o topo dela encosta no topo da tela.

A prancha é uma fileira de quatro. Empilhada, ela cresce — e **cruza a altura
da janela sem que uma linha de CSS dela tenha sido tocada**:

| largura | colunas | altura da peça | janela | leitura |
|---|---|---|---|---|
| 1440 | 4 | 447 px | 900 | baixa ← os tempos são daqui |
| 1024 | 4 | 377 px | 900 | baixa |
| **900** | 2 | **1.063 px** | 900 | **ALTA** |
| **760** | 2 | 947 px | 849 | **ALTA** |
| 620 | 2 | 825 px | 850 | baixa **por 25 px de margem** |
| **560** | 1 | **2.555 px** | 851 | **ALTA** |
| **390** | 1 | 1.893 px | 853 | **ALTA** |

Ou seja: os tempos `.06 / .055 / .16`, afinados para a leitura BAIXA, passaram
a ser aplicados sobre a ALTA **em tudo abaixo de 1024 — tablet incluído, não só
celular**. E em 620 o modo certo voltava por acidente aritmético, o que é pior
que estar errado: funciona até a altura da janela mudar um pouco.

### O que o visitante via, medido a 390 px

| rolagem | folha 1 na tela | opacidade |
|---|---|---|
| topo da peça +0 | y **41** (visível) | **0** |
| +200 | y **−192** (já saiu) | 0,83 |
| +400 | y −399 (sumiu) | 1 |

**A folha 1 nunca era vista.** Ela acendia enquanto subia para fora da tela — e
a primeira que o visitante encontrava acesa era a segunda, exatamente como
relatado.

### O conserto não é reafinar os números

Numa coluna empilhada, "quatro folhas entrando em sequência" **não descreve
nada**: o visitante encontra uma de cada vez, e a sequência é o próprio rolar.
Reafinar as constantes manteria um gesto que perdeu o referente.

Então a entrada por rolagem passou a valer **só onde a fileira é uma fileira**
(`min-width: 1024px`, as quatro em linha). Abaixo disso cada folha se revela
quando ELA chega, pelo `.reveal` que o resto do site inteiro já usa — e o
escalonamento vem do mesmo `--i` que já estava no HTML, sem uma variável nova.

**A especificidade é (0,3,0) de propósito.** `.prancha[data-progresso]
.prancha__item` precisa vencer `.reveal.is-visivel` (0,2,0), que senão forçaria
opacidade 1 e mataria a entrada por rolagem no desktop. Vencer por ORDEM no
arquivo funcionaria hoje e quebraria na primeira reorganização — este arquivo
já registra esse preço três vezes.

E o bloco de desktop desliga `filter` e `transition` do `.reveal`: **transição
de .85 s sobre um valor que a rolagem reescreve a cada quadro é engasgo
garantido**, a mesma lição que a rolagem suave pagou em 20/08.

Abaixo de 1024, `--avanco: 1` é **explícito** e não deixado indefinido: sem ele
as regras que consomem a variável (marca de registro, legenda, assentamento da
foto) cairiam em `var()` inválido. O resultado até seria parecido, mas por
acidente de fallback.

### Provado nos dois lados

| | folha 1 acende em | sequência |
|---|---|---|
| desktop 1440 | `[0,0,0,0] → [0.67,0.32,0,0] → [1,1,1,0.68] → [1,1,1,1]` | **intacta** |
| desktop 1024 | idem | **intacta** |
| celular 390 | y **634** (bem visível) | uma por vez |
| celular 375×667 | y **335** | uma por vez |

No desktop as quatro fecham com a fileira inteira ainda na tela, como antes.

**Movimento reduzido conferido nos dois** — é a armadilha que este arquivo
registra três vezes: todo estado inicial que esconde conteúdo precisa desse
caminho verificado. `main.js §4` marca tudo `is-visivel` de imediato quando há
redução, então opacidade 1 e `--avanco: 1` em celular e desktop.

### REGRA QUE FICA

**Animação atada a `--p` tem de declarar em que LEITURA ela foi afinada.** O
motor troca de modo pela altura do elemento, e a altura muda com a largura da
janela — então uma peça pode trocar de mecanismo sem que nada nela seja
alterado. É irmã da armadilha de 20/08 (*"ao mudar o PAPEL de um elemento numa
quebra, varrer as quebras ACIMA dela"*), com uma diferença que a torna pior:
aqui não há regra sobrando para encontrar na varredura. Não há regra nenhuma —
há a mesma regra medindo outra coisa.

### Estado

Publicado. 306 referências, 0 quebradas, 0 órfãos. 0 conflitos de cascata,
`node --check` limpo. Home a 1472 ms de LCP, TBT 55 ms, CLS 0,000 no perfil
móvel local. No ar: 40 ok / 1 falha (o `.htaccess` em cache de borda, que
expira sozinho).
---

## 2026-08-21 (Cloudflare) — A mesma regra de rota que está certa em Apache é LAÇO no Pages

Pedido: publicar o site no Cloudflare, de graça. Está no ar em
**https://i3automations.pages.dev**, conta `kegit9080@gmail.com`, projeto
`i3automations`. Publicado por `wrangler pages deploy`, sem custo e sem
repositório git no meio.

### O laço: 50 saltos, e o site inteiro inacessível

Primeira publicação foi ao ar quebrada. Todo link interno aponta para `.html`,
e pedir qualquer página entrava num laço infinito:

```
/who-we-are.html  --308-->  /who-we-are      (o Pages canonicaliza sozinho)
/who-we-are       --301-->  /who-we-are.html (a nossa regra do _redirects)
```

Medido: **`curl` desistiu em 50 saltos.**

**O Cloudflare Pages remove a extensão `.html` e devolve 308 para a forma
curta. Não há como desligar isso pelo `_redirects`.** E a regra que colidia com
ele é a variante "sem barra" (`/who-we-are` → `/who-we-are.html`), que em
Apache é **necessária** — o site antigo devolvia 301 nesse caminho, e sem a
regra ele ficaria sem destino.

Ou seja: a mesma linha é obrigatória numa hospedagem e fatal na outra.

O conserto tem duas partes, e as duas são sobre falar a língua da plataforma:
o alvo do `_redirects` passou a ser **sem extensão** (a forma canônica do
Pages), e a variante sem barra **deixou de ser emitida** para lá — o Pages já
serve `/who-we-are` nativamente.

**REGRA QUE FICA: redirecionamento correto numa plataforma pode ser LAÇO em
outra. Regra de rota não se copia entre hospedagens sem testar no ar.** É a
justificativa retroativa para `.htaccess` e `_redirects` serem gerados por
funções separadas em vez de saírem do mesmo texto — decisão tomada hoje cedo
por organização, e que hoje à noite pagou por si.

### O `_redirects` do Pages não aceita 410

Ele aceita 200, 301, 302, 303, 307, 308 e 404. **Uma linha com 410 não vira
"410": ela é descartada na publicação, em silêncio**, e o caminho passa a não
ter regra nenhuma.

410 continua sendo o código certo para os restos do WordPress ("acabou", não
"mudou de lugar") e é o que o `.htaccess` emite, porque em Apache dá. Onde a
plataforma não deixa, 404 é o mais próximo que existe — também tira do índice,
só um pouco mais devagar. Os dois arquivos agora dizem isso em comentário, para
ninguém "corrigir" o 404 de volta para 410.

### O Pages SERVE o `.htaccess`

`_headers` e `_redirects` ele CONSOME — os dois respondem 404. O arquivo do
Apache ele só serve: medido, **`/.htaccess` respondia 200** e entregava a
configuração inteira.

Tentei esconder pelo próprio `_redirects` (`/.htaccess → /404.html 404`) e
**não funciona: arquivo que existe vence a regra**. A saída foi tirar o arquivo
do PACOTE, não do disco — `ferramentas/publicar_cloudflare.sh` copia `site/`
para um diretório temporário, remove o `.htaccess` e publica a cópia.

É o jeito certo pelo motivo geral: **o artefato se prepara para a plataforma de
destino**, em vez de a pasta tentar servir as duas ao mesmo tempo.

**E a borda guardou a versão velha.** `CF-Cache-Status: HIT`, `Age: 363`,
`s-maxage=604800` — a origem devolve 404 (conferido com cache-buster) e a
borda continuará servindo o arquivo por até 7 dias nos nós que o pegaram. Sem
credencial nenhuma dentro, então é sujeira, não risco. Não há como purgar:
`*.pages.dev` não é uma zona da conta.

### O modo `--demo`, e por que ele não pode ser o padrão

`python ferramentas/build_site.py --demo` acrescenta
`X-Robots-Tag: noindex, nofollow` ao `_headers`. **Não é opcional num endereço
de demonstração**: enquanto i3automations.com serve o site velho, uma cópia
indexável em `*.pages.dev` compete com ele — duas URLs, mesmo conteúdo, e quem
escolhe qual sobrevive é o buscador.

Mas ele é PARÂMETRO e não padrão, pelo que este arquivo registra desde 18/08:
se `noindex` fosse o padrão, viajaria junto para o domínio real no dia da troca
e o site oficial sairia do Google — com o sintoma aparecendo semanas depois da
causa. **O padrão falha para o lado seguro; quem publica numa demo pede o modo
demo.**

E o `robots.txt` continua `Allow: /`, o que parece contraditório e não é: o
rastreador precisa BUSCAR a página para ver o `noindex`. Bloqueado no
robots.txt ele não busca, não vê, e ainda pode indexar a URL crua por links
externos. **Deixar rastrear e mandar noindex é a combinação que tira do
índice.**

`publicar_cloudflare.sh` sempre usa `--demo`, então a proteção não pode se
perder numa republicação distraída.

### O validador virou consciente de plataforma

Na primeira passada ele deu **13 falhas**, e **12 eram ele falando Apache com
uma plataforma que não é Apache**: esperava 200 em `/x.html` (o Pages devolve
308), 410 nos restos do WordPress (o Pages devolve 404) e registro MX num
subdomínio `*.pages.dev`, que não tem e-mail e não deveria ter.

Falha falsa é pior que falha nenhuma: um relatório com ruído é um relatório que
ninguém lê até o fim — e a 13ª falha, a única real, estava no meio delas.
`validar_producao.sh` detecta a plataforma pela URL e ajusta o que espera.

Agora: **40 ok, 1 falha** — a falha é o `.htaccess` em cache de borda.

### Medido no ar, servido pelo Cloudflare

| | pior LCP | pior TBT | CLS |
|---|---|---|---|
| local (servidor de teste) | 1836 ms | 152 ms | 0,000 |
| **no ar (Cloudflare)** | **1904 ms** | **310 ms** | **0,000** |

Desktop: pior LCP 468 ms, TBT 0 ms.

**O TBT da home subiu de 84 ms (local) para 271–310 ms no ar**, e não é ruído —
três amostras seguidas deram 271, 298 e 310. A causa provável é de MÉTODO:
medir uma origem remota **e** aplicar Slow 4G empilha a latência real até o
Cloudflare sobre os 150 ms emulados, então a condição testada é mais dura que o
4G lento que ela deveria modelar.

Fica registrado como **não resolvido**: o número verdadeiro para um visitante
real está entre 84 e 310, e daqui não dá para fechar. LCP e CLS passam com
folga nos dois métodos.

### Estado

25/25 rotas ainda passando no Apache de container (o gerador foi mexido, então
foi reconferido). 306 referências, 0 quebradas, 0 órfãos. 0 conflitos.

### PENDENTE

1. **O `_headers` no disco está em modo demo.** Antes de publicar na HostGator,
   rodar `build_site.py` **sem** `--demo`, ou o site oficial sai do Google.
2. **TBT da home no ar**, acima do limiar por método de medição não resolvido.
3. O `.htaccess` em cache de borda expira sozinho em até 7 dias.
---

## 2026-08-21 (contratos) — Quatro causas somadas, e três são armadilhas de tabela

Reportado: *"Contract record em past performances está um pouco quebrado.
ajuste o layout."* Procede, e medindo a peça a 1440 as causas eram quatro
independentes — nenhuma delas visível lendo o CSS.

### 1. Quatro campos curtos não preenchem 1280 px

`width: 100%` sem largura de coluna declarada faz o navegador distribuir o que
sobra igualmente:

| coluna | largura | conteúdo | vazio |
|---|---|---|---|
| Start date | 293 | ~110 | 183 |
| End date | 293 | **~14** | **279** |
| Value | 263 | ~100 | 163 |
| Reference | 431 | ~170 | 261 |

A coluna de data de fim segurava **um travessão no meio de 279 px de vazio**.
Nada lia como linha: cada dado flutuava no centro do próprio vão.

Corrigido com largura declarada — 34/30/36 —, e os números saem da medida do
conteúdo, não de frações redondas: "08 / 16 / 2021" mede ~110 px e
"$150,000.00" ~100 px em `--fs-body`.

### 2. Rótulo à esquerda, número à direita

O `th` de "Value" ficava em x 667 e a cifra terminava em x 907. **240 px entre
o rótulo e o dado que ele nomeia.**

**Regra que fica: alinhamento de cabeçalho e de célula tem de ser o MESMO.**
Num par desalinhado o olho para de associar os dois, e o cabeçalho vira
decoração. Agora `.contratos .contratos__num` casa cabeçalho, células e total
numa regra só.

### 3. O TOTAL NÃO ALINHAVA COM A COLUNA QUE ELE SOMA

A causa era cascata, e não estava escrita em lugar nenhum:

| seletor | especificidade | pedia |
|---|---|---|
| `.contratos tfoot td` | **(0,2,0)** | `text-align: left` |
| `.contratos__valor-cel` | (0,1,0) | `text-align: right` |

As parcelas terminavam em x 907; a soma começava em x 667. **Uma coluna de
cifra em que o total não alinha com as parcelas é o defeito mais visível que
uma tabela pode ter** — e ele era resultado da corrida entre dois seletores
meus, escritos no mesmo bloco.

É a terceira vez que este arquivo registra o mesmo formato de defeito
(`.contato__valor` em 20/08, `.setores` em 20/08). O conserto aqui foi juntar
os três consumidores numa classe só em vez de subir especificidade: separá-los
foi exatamente o que deixou a soma fora do prumo.

### 4. UMA COLUNA CONSTANTE NÃO É COLUNA

"Reference" trazia **"Provided upon request" nas três linhas** — o mesmo texto,
repetido — e a nota logo abaixo da tabela já dizia exatamente isso. Ela sozinha
respondia por um terço da largura.

Coluna cujo valor nunca muda é **nota de rodapé ocupando 431 px**. Saiu, e o
texto virou a nota — que agora mora ao LADO da tabela, no vão que antes era
morto. A informação não se perde: a nota afirma "References for all three are
provided on request", que é o que as três células diziam.

### A nota no topo, e não no pé

Ela ocupa as duas linhas da grade, então a ancoragem decide onde pousa. Medido
a 1440: ancorada no pé, ela começa **282 px abaixo** do rótulo do programa e
deixa esse vão vazio no alto da coluna — o mesmo defeito de novo, num lugar
novo. Em `align-self: start` ela nasce na mesma linha do rótulo mono e as duas
anotações leem como par.

A rolagem horizontal vive em `.contratos__quadro` e não no container da grade:
rolar a grade inteira levaria a nota junto, e a nota não é parte da tabela.

### Medido nas quatro larguras

| largura | colunas | cifras | nota |
|---|---|---|---|
| 1440 | 283 / 250 / 300 | alinhadas em x 912 | ao lado, no topo |
| 1024 | 163 / 144 / 173 | alinhadas em x 528 | ao lado, no topo |
| 760 | 245 / 216 / 259 | alinhadas em x 740 | abaixo |
| 390 | empilhada | alinhadas em x 370 | abaixo |

"Alinhadas" quer dizer as CINCO bordas direitas no mesmo x: as três parcelas,
o total e o cabeçalho. 0 rolagem lateral na página e 0 no container, nas
quatro.

**O empilhamento a 700 precisou desligar as larguras de coluna** — `width: 34%`
num `display: flex` continua valendo e espremeria o par rótulo/valor. Por isso
os seletores `:nth-child` aparecem de novo dentro da media query, com
`width: auto`.

**E o total continua sendo uma LINHA no celular**, não dois blocos empilhados:
é a única linha da peça em que rótulo e valor se leem juntos, e quebrá-la em
duas era o que deixava a soma solta no meio do vazio.

### Contraste, remedido

| | claro | escuro |
|---|---|---|
| valor (20px) | 11,28:1 | 15,80:1 |
| data (17px) | 6,30:1 | 9,34:1 |
| cabeçalho (12px) | 6,00:1 | 9,67:1 |
| nota (14px) | 6,00:1 | 9,67:1 |

Todos passam AA, e o piso do valor é 3:1 por ser texto grande.

### Estado

306 referências, 0 quebradas, 0 órfãos. 0 conflitos de cascata, chaves e
comentários balanceados, `node --check` limpo, e nenhuma classe emitida sem
regra.

---

## 2026-08-21 (migração) — A hospedagem é Apache, e metade do deploy não valia lá

Pedido em três partes, depois da auditoria de conteúdo: resolver as lacunas e
pôr uma camada de contratos em past-performance; ignorar as afirmações sem
fonte; e — a parte que mudou o dia — **"veja em qual plataforma ele está sendo
atribuído e se são compatíveis"**.

### O que a investigação de plataforma achou

`curl -I` em i3automations.com devolve `Server: Apache`, o `Link:` do
`wp-json` e nameservers `ns78/ns79.hostgator.com.br`. É **HostGator
compartilhado, cPanel, Apache, WordPress**, com e-mail no Titan.

**`_headers` e `_redirects` são convenção de Cloudflare Pages e Netlify. Em
Apache os dois são INERTES.** Este arquivo vinha tratando o `_headers` como a
camada de cache do deploy desde 20/08 — e ele nunca teria feito nada no
servidor para onde o site vai. Ficaria lá sem erro nenhum, e o sintoma seria
"o cache não funciona".

E o problema é maior que cache. Cinco coisas dependem de configuração que só
existe no `.htaccess`, e **cada uma some em silêncio**:

| item | sem ele |
|---|---|
| `ErrorDocument` | o Apache serve a página de erro DELE, e a `404.html` do projeto nunca aparece |
| `mod_deflate` | quem liga a compressão hoje é o `.htaccess` do WordPress: trocar o arquivo tira o gzip |
| `AddType image/avif` | **101 arquivos AVIF** viram `octet-stream` e o `<picture>` não pinta nada, sem erro no console |
| `mod_expires` | medido: o servidor atual **não manda `Cache-Control` em nada** — nunca foi configurado |
| https + sem www | as duas regras vivem no `.htaccess` do WordPress; substituí-lo sem repô-las quebra a canônica |

O deploy passou a emitir **os três arquivos**, todos da **mesma tabela**
(`CACHE`, `ROTAS`, `IDOS` em `build_paginas.py`). Escrever a mesma política
duas vezes à mão é como as duas divergem — e a divergência só aparece no dia
em que alguém troca de hospedagem.

### `httpd -t` NÃO valida `.htaccess`, e por isso o teste tinha de ser um pedido

Subi um Apache 2.4 em container com `AllowOverride All`, servindo `site/`.
`httpd -t` disse **Syntax OK**. O primeiro pedido devolveu **500**.

```
ExpiresByType takes two arguments, a MIME type followed by an expiry date code
```

**O parser de configuração do Apache só reconhece `#` no INÍCIO da linha.** Eu
tinha escrito `ExpiresByType image/jpeg "access plus 31536000 seconds"  # imagens`
e o rótulo virou argumento extra.

**Regra que fica: `httpd -t` não lê `.htaccess`** — ele só é interpretado no
momento do PEDIDO, por diretório. Configuração de Apache não testada com uma
requisição de verdade não está testada. E o erro derruba a página inteira com
500, não degrada.

Corrigido, a bateria fecha: **25 verificações, 25 passando** — 9 URLs do
WordPress em 301, `/index.html` → `/`, os restos do WP em 410, as páginas em
200, caminho inexistente em 404 servindo a 404 do projeto, e `/img/` em 403.

**410 e não 301 nos restos do WordPress**, e a distinção é de significado: 301
diz "mudou de lugar" e o buscador vai atrás; 410 diz "acabou" e ele tira do
índice. Mandar um feed RSS para uma página HTML confunde o leitor de feed e
cria conteúdo duplicado.

O laço que eu temia — `DirectoryIndex index.html` mais
`RewriteRule ^index\.html$ /` — **não aconteceu**, e só o teste responde isso.
Estava preparado para guardar com `%{THE_REQUEST}`; não foi preciso.

### DUAS montagens de teste fabricaram O MESMO defeito de 340 KB

A home apareceu duas vezes baixando as cinco máscaras de setor em duplicata. As
duas vezes era a régua, não o site — e as causas eram **diferentes**:

1. **Servidor local sem `Cache-Control`.** As máscaras têm dois consumidores (o
   `mask-image` do CSS e o `new Image()` da lente); sem cabeçalho de cache o
   segundo baixa de novo. Já registrado em 21/08 (fecho).
2. **Certificado autoassinado.** O **Chrome não guarda em cache resposta vinda
   de origem com certificado inválido.** O Apache de teste tinha `Cache-Control:
   immutable` correto e mesmo assim duplicava.

Isolado com o MESMO servidor, MESMO conteúdo, MESMOS cabeçalhos, mudando só o
certificado: **847 KB em http contra 1183 KB em https autoassinado.**

`CDP_TLS_INSEGURO=1` liga `--ignore-certificate-errors` no `cdp.mjs`, atrás de
variável de ambiente — ignorar certificado por padrão é o tipo de atalho que
sobrevive até alguém apontar a ferramenta para a internet. E a medição válida
continua sendo a de http: **847 KB, LCP 1836 ms, TBT 152 ms, CLS 0,000.**

**Regra que fica: ambiente de medição que não reproduz produção — nos
cabeçalhos E na cadeia de confiança — mede outro site.** É a terceira vez nesta
semana que a régua errada quase virou conserto.

### A camada de contratos: três contratos, um cliente

O site antigo publica três projetos com data e valor, e a migração tinha
perdido os três. Conferido na fonte antes de escrever: **o parágrafo de Arcadia
precede os três e não há outro cliente na página.** Apresentá-los como três
clientes seria inventar alcance; como um programa de três contratos é o que a
fonte diz — e prova mais, porque relação renovada três vezes em três anos vale
mais que três trabalhos avulsos.

| início | fim | valor |
|---|---|---|
| 08/16/2021 | — | US$ 150.000,00 |
| 09/21/2022 | — | US$ 35.000,00 |
| 03/18/2024 | 04/30/2024 | US$ 99.450,00 |
| | **combinado** | **US$ 284.450,00** |

**Ordem cronológica, não a da fonte**, onde eles saem 09/2022, 03/2024,
08/2021 — sem ordem nenhuma. Em ordem, a tabela conta que a relação começou em
2021 e ainda era renovada em 2024, que é o que "over three years" afirma em
prosa.

**O campo vazio é um traço, não uma invenção.** Dois contratos não têm data de
fim na fonte. Escrever "ongoing" afirmaria o que ela não diz; a data de hoje
seria pior. O traço diz exatamente o que se sabe.

**`contratos()` é componente novo e NÃO reusa `oferta()`**, e a distinção não é
estilística: em `oferta()` as linhas são CRITÉRIOS e as colunas são as três
ofertas; aqui cada linha é um REGISTRO. Forçar um no outro poria os contratos
nas colunas, e a tabela deixaria de crescer quando o quarto entrasse.

Onde ela entra: **depois** das seis folhas de setor e **antes** do sinóptico.
Qualitativo → específico → agregado. Pô-la no fim jogaria o dado duro depois do
número redondo, e o número redondo é o que menos prova.

### WestRock e Arcadia voltaram, e a prosa mudou por consequência

As duas estavam nomeadas no site antigo. Ao escrever o escopo real da WestRock
— painel de controle, diagnóstico de processo, sistemas de monitoramento e
**câmeras** — a frase anterior da ficha de papel teve de sair: ela descrevia um
escopo diferente. **Escrever o nome do cliente e manter ao lado um escopo que
não é dele é pior que não nomear ninguém.**

Isso removeu uma ocorrência de "alarm rationalisation". As outras duas
(services, who-we-are) **ficam**, por decisão do usuário: perguntado sobre as
quatro afirmações sem fonte, respondeu "não importa".

### Resolvido por medição, não por pergunta

**`i3automationsgov.com` não resolve em DNS.** O domínio está morto. Não era
lacuna do site novo — é sujeira no site antigo, que anuncia um endereço que não
existe. Uma das sete perguntas ao cliente caiu sozinha.

### Estado

306 referências, 0 quebradas, 0 órfãos. 0 conflitos de cascata. `node --check`
limpo em 24 JS mais os 5 `.mjs` de medição; 27 ferramentas Python parseando.
25/25 rotas no Apache real. Cache idêntico nas duas hospedagens, conferido
arquivo a arquivo.

### PENDENTE

1. **Duas perguntas ao cliente**: o Capabilities Statement existe em PDF? E
   "power companies" são clientes distintos das usinas solares?
2. **"Twenty-six years" continua literal** em dois lugares (`past-performance`
   e `who-we-are`). Em janeiro de 2027 o site erra por um ano. Não mexido: caiu
   dentro do "não importa".
3. **`X-Robots-Tag: noindex`** continua ausente do `_headers` e do `.htaccess`,
   de propósito — acrescentar em endereço de demonstração, apagar quando o
   domínio real entrar.
4. **O e-mail está no Titan** (`mx1/mx2.titan.email`). Qualquer mudança de DNS
   na migração precisa preservar os MX, ou o cliente perde e-mail — e o sintoma
   não aparece no site.

---

## 2026-08-21 (fecho) — Duas vezes a medição inventou um defeito, e uma vez ela achou o real

Lista do usuário para a parte final: 404 própria, pagespeed, comprimir imagens,
favicon, og image, sitemap, Google Analytics, cookies, robots, meta
descriptions. **Seis dos dez já existiam** — o valor da sessão está nos quatro
que faltavam e nos dois defeitos que a medição encontrou pelo caminho.

### O Chrome mediu de verdade, e `ferramentas/velocidade/` é o aparato

`servir.mjs` (servidor que imita a hospedagem), `medir.mjs` (LCP/CLS/TBT/bytes
em 7 páginas × 2 perfis), `recursos.mjs` (o que pesa numa página), `tarefas.mjs`
(quem bloqueia a thread) e `psi.mjs` (o PageSpeed real, para o dia em que houver
domínio). O perfil móvel é o do Lighthouse: **Slow 4G + CPU 4x**.

**Não dá para "rodar o PageSpeed" hoje** — ele é serviço do Google e precisa de
URL pública. O que dá, e é o que foi feito, é medir as MESMAS métricas no mesmo
motor com o mesmo estrangulamento.

### A MEDIÇÃO INVENTOU UM DEFEITO DE 720 KB, e quase virou conserto

A primeira varredura acusou as cinco máscaras de setor baixadas **duas vezes**
na home. A causa parecia clara: elas têm dois consumidores — o `mask-image` do
CSS e o `new Image()` da lente.

**Era o meu servidor local, que não mandava `Cache-Control`.** Sem ele o Chrome
não reutiliza, e o segundo consumidor baixa de novo. Com as regras reais do
`_headers`, a home cai de 1952 para 1231 KB e a duplicação some.

O mesmo erro tinha uma segunda cara: `medir.mjs` usava
`Network.setCacheDisabled`, que parece o jeito certo de medir visita fria e não
é — ele também impede a reutilização DENTRO da página. Trocado por
`Network.clearBrowserCache` ENTRE páginas: visita fria de verdade, sem inventar
custo.

**Regra que fica: servidor de medição que não replica os cabeçalhos da
hospedagem mede outro site.** E é a mesma lição de 20/08 — *"antes de reprovar
uma escolha nova, meça a que já está publicada"* — aplicada à própria régua.

### O defeito real: a receita do EPSON nunca chegou às cinco irmãs

O `memoria.md` registra em 19/08 que a máscara do braço saiu em **LA com alfa
posterizado**, com a medição que a justificou. As cinco máscaras de setor
continuaram em **RGBA** — e RGBA numa máscara guarda três canais que ninguém lê:
medido, o RGB é **255 em todo pixel dos cinco arquivos**, e nem o `mask-image`
nem o `texture(uTraco).a` do shader tocam neles.

| empacotamento | peso | |
|---|---|---|
| RGBA (o que estava lá) | 740 KB | 4 bytes/px, três deles constantes |
| LA posterizado | 502 KB | a receita do EPSON (−32%) |
| **P com tRNS** | **331 KB** | 1 byte/px + 32 entradas de alfa (**−54%**) |
| WebP sem perda | 290 KB | −60% |

**WebP ficou de fora, e não por conservadorismo: esta máscara É a via de
reserva** de quem não tem WebGL2. Trocar o formato do fallback por 41 KB põe uma
negociação de formato no único caminho que existe para NÃO falhar.

Conferido reabrindo os arquivos do disco: **erro máximo de 4/255 no alfa, RGB
íntegro em 255**. Com o EPSON junto, **389 KB** a menos.

**A armadilha do PNG indexado:** o Pillow só escreve o chunk `tRNS` se ele vier
por parâmetro no `save()`. Sem isso a máscara sai **opaca** — e o sintoma não é
erro nenhum, é o card inteiro coberto de navy.

### `getPointAtLength` é O(n²), e UM caminho respondia por 95% do pior TBT do site

who-we-are marcava **TBT de 488 ms**, quase o triplo do limiar de "bom". O
perfilador apontou `amostrar` em `marca.js`. Medido caminho a caminho:

| caminho | amostras | custo |
|---|---|---|
| moldura `M21 0h368v226H21z` | 990 | 1,1 ms |
| tela `M41 20h328v186H41z` | 857 | 0,9 ms |
| **o "3" do glifo** | **382** | **66,6 ms** |

As retas são baratas porque o caminho tem 4 comandos. O "3" tem seis cúbicas, e
**cada chamada as re-avalia desde o início** — 60x o custo com 40% das amostras.

O conserto **não reduz amostra nenhuma**: separa o BRUTO do FILTRO e alimenta o
bruto em fatias, com orçamento de **8 ms por fatia**. O orçamento é de TEMPO e
não de contagem, pela mesma razão da rolagem suave de 20/08: contagem calibrada
num desktop vira tarefa de 200 ms no celular que justamente precisa da proteção.

**TBT 488 → 0 ms.** E a prova de que a peça continua a mesma foi rodar os dois
motores no mesmo SVG, no navegador: **215 segmentos, 1720 floats, 0 diferentes,
caixa idêntica** — os mesmos 215 de 19/08. `construir()` continua síncrona
porque `previa_marca.js` a consome assim, e a prévia foi rodada: 215 segmentos,
raio 2,45.

### O favicon existia e mesmo assim faltava em três lugares

Havia `favicon.svg` e mais nada. Os três buracos não dão erro visível — o ícone
simplesmente não aparece:

1. **o navegador pede `/favicon.ico` SOZINHO**, sem link no HTML, e o buscador
   olha para lá. Era 404 em toda visita;
2. **`apple-touch-icon` em SVG é IGNORADO pelo iOS** — quem salva na tela
   inicial recebe um retrato da página;
3. sem manifesto, o Android amplia o ícone de 32 px no atalho.

`build_icones.py` gera tudo **a partir do mesmo SVG**, por captura no Chrome —
não por um desenho paralelo em PIL. Redesenhar o "3" com primitivas seria a
terceira cópia do glifo, a armadilha que `icone_marca()` documenta. 17,2 KB no
total, e as cores conferem com os tokens (`#003566` e `#FDC500` exatos).

O `.ico` vai na RAIZ e não em `brand/`, porque o pedido automático não passa por
link nenhum. `varredura.py` aprendeu a ler o `site.webmanifest` — os dois ícones
do Android apareciam como órfãos, e isentá-los à mão é como um ícone de verdade
sem uso passa despercebido depois.

### Analytics: a política de privacidade JÁ RESPONDIA, e em contradição

A página publicada afirma: *"This site has no contact form, no analytics tags,
no advertising pixels and no third-party scripts."* Instalar GA4 contradiz uma
página legal do próprio site — parei e perguntei. **O usuário escolheu nenhum
analytics**, e a afirmação continua verdadeira.

**E pediu a faixa de consentimento MESMO ASSIM**, sabendo que não há cookie:
comprador corporativo e órgão público costumam exigi-la por política interna.

Isso torna o TEXTO a decisão difícil, não o componente. Escrever *"we use
cookies to improve your experience"* numa página que não põe cookie nenhum é
afirmação falsa, e a política a um clique diz o contrário — **contradição entre
a faixa e a página legal é pior que faixa nenhuma**. Então ela declara o que
existe, e o botão não diz "Accept": não há o que aceitar. Diz **"Got it"**.

Entrou junto a seção *"Cookies and local storage"* na política, porque a faixa
aponta para lá e não havia nada que confirmasse o que ela afirma. Ela lista as
duas chaves de `localStorage`: o tema e — a ironia declarada — **a marca de que
o aviso foi lido**, ou seja o aviso guarda um registro de si mesmo.

### DOIS defeitos meus na faixa, e o segundo é reincidência de um já registrado

**1. Escrevi "zero dourado permanente" no comentário e pus `border-top`
dourada** três parágrafos abaixo, na mesma sessão. A tentação é óbvia — dourado
separa bem — e a faixa flutua sobre o herói, que já está estourando o teto de
dois da regra crítica nº5.

Mas a aresta também não pode ser filete qualquer, e aí a conta manda: **o bloco
de contato que fecha TODAS as páginas é `--sup-3`, exatamente a superfície da
faixa** — navy sobre o mesmo navy dá 1,19:1 no claro e 1,66:1 no escuro. Ficou o
mesmo `rgba(255,255,255,.55)` da aresta da folha do rodapé, pelo mesmo cálculo:
.30 → 1,83:1 reprova, .45 → 2,70:1 reprova, **.55 → 3,75:1 passa, e é o mínimo
que passa**.

**2. `z-index: 900` reintroduziu, na íntegra, a armadilha de 20/08.**
`.nav__painel` é `position: fixed` e desce quase até o pé num aparelho baixo.
Medido no iPhone SE (375×568), com o menu aberto:

| | |
|---|---|
| centro do "Contact Us" | y 566 |
| topo da faixa | y 332 |
| `elementFromPoint` no CTA | **`.aviso__interno`** |

O dedo acertava a faixa. Em **z-index 90** o painel vence e o toque volta ao
botão — conferido pelo mesmo `elementFromPoint`. **Regra que fica: camada nova
`position: fixed` tem de ser testada com o menu ABERTO, no aparelho mais baixo.**

A faixa nasce `hidden` no HTML: sem JavaScript ninguém a dispensa, e faixa que
não se dispensa é pior que faixa nenhuma. Na home ela espera a intro encerrar —
observando a remoção de `intro-ativa`, não um tempo fixo que dessincronizaria
no dia em que a duração mudar. Com rede de segurança de 7 s **e trava de
reexibição**: sem ela, quem dispensasse a faixa nos primeiros segundos a veria
voltar sozinha aos 7 s, e o defeito só apareceria na home.

Ciclo conferido no navegador: aparece → "Got it" → some e persiste → continua
sumida na página seguinte → na home só aparece depois da intro. Movimento
reduzido: visível e sem transição, some no clique.

### As fotos NÃO tinham margem, e vale registrar que foi medido

Testadas outras qualidades e esforços de AVIF/WebP: **2 a 5%**, e regenerar a
partir de arquivo já comprimido só adiciona perda geracional. O pipeline já
estava afinado por papel (74 na faixa, 72 na dupla e no cabeçalho, 80 no setor).
O desperdício estava no EMPACOTAMENTO das máscaras, não na compressão das fotos.

### Estado, medido

| | pior LCP | pior TBT | CLS | home |
|---|---|---|---|---|
| antes | 2216 ms | 488 ms | 0,000 | 1231 KB |
| **depois** | **1836 ms** | **152 ms** | **0,000** | **847 KB** |

Limiares de "bom" do Core Web Vitals: LCP < 2500, TBT < 200, CLS < 0,10 —
**as sete páginas passam nos três, no perfil móvel estrangulado.** No desktop o
pior LCP é 172 ms.

306 referências, 0 quebradas, 0 órfãos. 0 conflitos de cascata, 0 fotos
repetidas entre papéis, tags balanceadas nas 10 páginas, 24 arquivos JS no
`node --check`, JSON-LD parseando, 10/10 metadescrições, 61/61 imagens com
`alt`. **E o Chrome finalmente viu tudo isso rodando.**

### PENDENTE

1. **`X-Robots-Tag: noindex` continua ausente do `_headers`, de propósito.** Se
   publicar num endereço de DEMONSTRAÇÃO, acrescentar a linha na hora — e
   apagá-la quando o domínio real entrar, ou o site oficial sai do Google.
2. **`psi.mjs` só roda depois do deploy.** No dia em que i3automations.com
   apontar para cá: `node ferramentas/velocidade/psi.mjs https://i3automations.com/`.
3. Continuam abertas as três pendências de 20/08 (rótulos mono no celular, o
   `touch-action` da `.malha`, o herói em paisagem) e as seis marcas douradas de
   "Vendor profile".

---

## 2026-08-20 (celular) — O Chrome finalmente entrou, por CDP, e achou o que nenhuma varredura achava

Pedido: otimizar para aparelhos móveis, mantendo o site o mais parecido possível
com o de PC. E, no meio da sessão, a restrição que governou tudo: **"não mude
nada do site para PC, apenas o do celular."**

Por isso **toda regra desta entrega vive dentro de `@media (max-width: N)`, com
N ≤ 900.** Não é organização, é a garantia auditável de que o desktop não mudou.
Conferido no fim, medindo 1440, 1024 e 900 — idênticos ao que eram.

### A extensão continua desconectada, e deixou de importar

Ela está fora do ar há várias sessões, e este arquivo registra "ver no navegador
continua pendente" cinco vezes. **O Chrome está instalado; o que faltava era o
caminho até ele.** Node 24 traz `WebSocket` global, então dá para subir
`chrome.exe --headless=new --remote-debugging-port` e falar CDP direto, sem
puppeteer e sem instalar nada.

`ferramentas/movel/` é isso: `cdp.mjs` (driver), `diagnostico.mjs` (varredura de
10 páginas × 6 aparelhos), `tirar.mjs` / `foto.mjs` (captura), `medir.mjs`
(geometria) e `intro.mjs` (fotografa a intro em instantes EXATOS).

**A lição de método está no `intro.mjs`.** A primeira versão dormia N ms e
fotografava — e eu quase registrei um defeito no cursor que não existia, porque
`pagina()` já espera 900 ms depois do load e todas as marcas saíam deslocadas.
A versão certa **pausa `document.getAnimations()` e escreve `currentTime`**.
Instante pedido = instante fotografado. **Animação não se mede por cronômetro;
mede-se buscando o tempo.**

### O defeito estrutural: `96vw` dentro de um container que não tem 100vw

`.heroi__peca` era `width: min(96vw, 460px)` abaixo de 900. Mas a caixa de
conteúdo do container é `100vw − 2 × --pad-lateral` — **335px num aparelho de
375, 280px num de 320.** `96vw` dá 360 e 307.

E a peça é **item de grade com `min-width: auto`**, então a largura declarada
vira o **piso da trilha `1fr`**: a trilha cresce para 360 e leva junto o
`.heroi__texto`, que é irmão na mesma trilha.

| janela | caixa de conteúdo | 96vw | vazamento |
|---|---|---|---|
| 320 | 280 | 307 | **27px** |
| 375 | 335 | 360 | 5px |
| ≥500 | — | o teto de 460 vence | 0 |

**Nada acusava.** `.heroi` é `overflow-x: clip`, então não havia barra de
rolagem e a varredura de referências não olha layout. O que o visitante via era
a lead cortada no meio da palavra ("...and SCADA", "Lakewood") e a margem
direita menor que a esquerda. Virou `min(100%, 460px)`.

**Regra que fica: `vw` não é a largura do container. Dentro de qualquer coisa
com `padding-inline`, `Nvw` maior que `100vw − 2*pad` transborda — e se o
elemento for item de grade, ele não transborda sozinho: ele arrasta os irmãos.**

### O braço ocupava 54% do próprio slot, e a regra culpada estava a 200 linhas

`@media (max-width: 1200px)` declara
`.heroi__peca .braco { width: min(52vw, 520px) }` — largura pensada para a peça
que fica **ao lado** do texto, onde 52vw é meia tela. Abaixo de 900 a peça deixa
de ficar ao lado e vira bloco empilhado com largura própria, **mas ninguém
desligava aquela regra**: caixa de 360, desenho de 195, encostado na esquerda,
165px de navy morto à direita.

`width: 100%` devolve o desenho à caixa, e a moldura resultante é 5/4 — que a
medição de 19/08 já tinha registrado como o ponto em que a ocupação do braço
trava em 79% (62% em 0,74 · 69% em 1,06 · **79% em 1,25** · 79% em 1,58).

**Regra que fica: ao mudar o PAPEL de um elemento numa quebra (de "ao lado" para
"empilhado"), varrer as quebras ACIMA dela.** A regra que sobra não dá erro —
ela só continua obedecendo a uma composição que não existe mais.

### A frase da intro não cabia em celular nenhum, e o conserto não podia ser tipo menor

Medido: a frase mede **391px** em qualquer aparelho, porque
`clamp(1rem, 1.9vw, 1.625rem)` trava no piso de 16px assim que 1,9vw cai abaixo
dele — ou seja em tudo abaixo de 842px de janela. O teto é `92vw`: 294px a 320,
345px a 375. **391 não cabe em 345.** A frase vazava, cortada no meio de
"instrumentation".

O ponto de quebra sai da conta: 391 / 0,92 = **425px de janela**. O corte ficou
em 440 para dar folga a quem cair na fonte de reserva, que é mais larga.

**Tipo menor estava fora de questão:** caber numa linha a 320px exigiria ~12px
(16 × 294/391), e valor de tipo é intocável sem confirmação (CLAUDE.md nº2).
Duas linhas a 16px leem melhor que uma a 12 e não tocam na escala.

**E o gesto foi preservado, que é o ponto.** A máquina de escrever não virou
varredura: cada linha tem `clip-path` próprio e as duas correm em SEQUÊNCIA; o
apagar inverte a ordem, como backspace de verdade. O salto do fim da linha 1
para o começo da linha 2 é instantâneo porque os dois quadros ficam a **0,001%**
de distância — sem isso o cursor deslizaria na diagonal pelo meio da frase.

**`width: max-content` nas linhas NÃO é acabamento, é o que faz o efeito
existir.** Bloco sem largura própria ocupa a linha inteira (230px, a linha mais
longa), e aí duas coisas quebram juntas: `getBoundingClientRect` devolve 230
para as DUAS linhas, e o cursor da primeira caminharia 72px além da última
letra; e o `clip-path`, que é fatia da CAIXA, abriria 230px de véu sobre 158px
de texto — a linha terminaria de ser escrita a 69% do tempo dela.

**As três animações usam o mesmo `steps(26)`, e isso é obrigatório:** o
`clip-path` revela FATIAS da caixa, não caracteres. Enquanto os três contarem a
mesma quantidade de fatias, o cursor fica colado na borda do texto; conte
diferente e ele descola no meio. A frase inteira já era assim — 46 passos para
53 caracteres.

**A armadilha do movimento reduzido reapareceu, pela terceira vez neste
arquivo.** O bloco de redução desligava `.intro__texto`, mas abaixo de 440 quem
carrega o `clip-path: inset(0 100% 0 0)` é `.intro__linha`. Sem a regra nova as
duas linhas ficariam paradas no estado INICIAL — que é o invisível — e a intro
fecharia em 0,8 s tendo mostrado uma frase em branco. **Todo estado inicial de
animação que esconde conteúdo precisa do caminho de movimento reduzido
conferido, sempre.**

### 22 alvos de toque por página abaixo de 44px, e o padrão era sempre o mesmo

Texto pequeno, vão generoso, **vão não clicável**. O rodapé era o extremo: sete
links de navegação com 21px de altura e 10px de `gap` — passo de 31px em que 21
respondem ao dedo e 10 não fazem nada. Na tela parece lista arejada; no dedo é
uma fileira de fitas finas com buraco no meio.

**Duas técnicas, e a escolha entre elas não é estilística, é distância:**

| vizinho | técnica | por quê |
|---|---|---|
| LONGE | `padding` + `margin` negativa | o texto não se move um pixel; o alvo cresce para dentro do vão que já existia |
| PERTO (lista) | cresce o PASSO, e o alvo preenche ele | margem negativa aqui SOBREPÕE dois alvos, e o toque na faixa comum vai para quem estiver por cima |

Rodapé: `gap` de 10 → 4 e `padding-block: 10px` no `a` (bloco). Passo de 45px em
que 41 respondem e 4 separam. Contato (`tel:` / `mailto:`, o alvo mais
importante do site em celular), trilha e marca do nav foram por padding
compensado.

Entrou junto o `:active` — **sem ponteiro não existe hover, e o `:active` é o
único retorno de que o dedo acertou.** Em rede lenta é exatamente o intervalo em
que a pessoa toca de novo. É `opacity` e não cor: atravessa qualquer superfície
sem precisar de um token por contexto.

Resultado: **de 22 alvos abaixo de 44px por página para 0.** O que a sonda ainda
lista é largura de link inline em frase, que o WCAG 2.5.8 isenta.

### A placa de obra parava a 35px da margem

O teto de `max-width: 300px` é do tablet, onde a coluna é larga e a placa lê como
placa. Numa coluna de 335 ela para a 35px da borda direita — e **quase-alinhado
é o único resultado que parece defeito**, porque o título e o texto logo abaixo
VÃO até a borda. Ou a peça é claramente menor, ou ela alinha.

Liberado abaixo de **640**, e o número é conta: 640 − 2 × 20 = 600, que é
exatamente o lado do acervo autoral (600×600). A fotografia continua sendo
REDUZIDA em todo aparelho abaixo da linha — 0,56x a 375, 0,47x a 320 — e nunca
ampliada, que é o que "a placa é placa" protege.

**640 não consolidou o 620 que está logo abaixo**, e a distinção é a de 20/08:
620 é onde `.obra__linha` deixa de caber em duas colunas, 640 é onde a coluna
cabe nos 600px da fonte. Contas diferentes, pontos diferentes.

### O que a sonda NÃO vê, e vale saber

`overflow-x: clip` num ancestral **esconde o vazamento da varredura**: a sonda
pulava todo elemento com ancestral que corta, e por isso deu "0 transbordando"
enquanto a headline estava cortada na tela. **Quem achou os dois defeitos do
herói foi a CAPTURA, não a medição.** Varredura acha o que você sabe procurar;
a fotografia acha o que você não sabia.

### Estado

60 combinações (10 páginas × 6 aparelhos): **0 com rolagem horizontal, 0
transbordando, 0 alvos de lista abaixo de 44px.** 0 conflitos de cascata,
`node --check` limpo, chaves e comentários balanceados. Desktop conferido em
1440 / 1024 / 900: inalterado.

### PENDENTE — precisa de decisão do usuário

1. **Rótulos mono em 11–12,5px no celular** (`prancha__idx`, `peca__cota`,
   `escada__elo`, `galeria__num`, `prancha__legenda`). Não toquei: a regra
   crítica nº2 proíbe mexer em valor de tipo sem confirmação explícita.
2. **`.malha` (services): o arrasto do setpoint é vertical, mas `touch-action` é
   `pan-y`** — no toque ele não arrasta, e o `pointerdown` altera o setpoint
   quando a pessoa só está rolando a página. O rótulo diz "DRAG the setpoint",
   que é falso no celular.
3. **Herói em paisagem** (667×375): usa a coluna única e deixa metade da tela
   vazia. Restaurar as duas colunas ali seria MAIS parecido com o PC.

---

## 2026-08-20 (deploy) — Dois `loading` no mesmo `<img>`, e o navegador fica com o primeiro

Três pedidos numa frase: otimizar o SEO, tirar todos os comentários do código e
avaliar a estrutura para facilitar o deploy. O terceiro achou o defeito mais
caro dos três, e ele estava escrito no arquivo há semanas — certo, e ignorado.

### A foto do cabeçalho é o LCP de sete páginas, e estava em `lazy`

`cabecalho()` mandava a prioridade pelo parâmetro `extra`:

```
extra='fetchpriority="high" loading="eager"'
```

…sem ligar o `ansioso` de `imagem()` — **que já escreve `loading="lazy"` por
padrão**. O `<img>` saía com o atributo DUAS VEZES:

```
loading="lazy" decoding="async" fetchpriority="high" loading="eager"
```

e o HTML manda o navegador **ficar com a primeira ocorrência**. O `eager` era
descartado em silêncio.

A consequência não é cosmética: essa foto é o maior bloco pintado na primeira
dobra de sete páginas, ou seja o elemento **LCP**. Em `lazy` o download só
dispara quando o navegador julga a imagem perto da janela — e isso só acontece
depois do layout, que só acontece depois do CSS e da fonte. A imagem que devia
abrir a conexão primeiro era a última a ser pedida.

**Nada acusava.** O atributo certo ESTAVA no arquivo. Validador de HTML aceita
atributo duplicado. A varredura de referências só olha caminho. E o sintoma —
"a página demora um pouco para pintar" — é exatamente o que se atribui a imagem
grande, que é a explicação errada aqui.

**Regra que fica: parâmetro que ESCREVE atributo e parâmetro que ACRESCENTA
atributo não podem cobrir o mesmo atributo.** Se um helper já emite `loading`,
mandar `loading` por um canal de texto livre não sobrescreve — duplica, e
duplicata em HTML resolve para a primeira.

### Comentário: a fonte foi separada do publicado, não apagada

O pedido é razoável — **49% do CSS+JS deste site é comentário, 195 KB**. Mas
apagar da fonte contradiz a regra crítica nº3 do CLAUDE.md: *"se um número
entrar no CSS, tem que existir a conta que o produziu"*. São **88 medições só no
style.css** — cada contraste WCAG, cada proporção conferida, cada armadilha que
custou uma sessão. Apagar seria queimar a memória do projeto para ganhar 195 KB
que o gzip já devolveria quase inteiros.

Então: `fonte/css` e `fonte/js` guardam a fonte comentada; `ferramentas/build_ativos.py`
publica a cópia enxuta em `site/`. O deploy não muda — continua sendo publicar a
pasta `site/`. **402,5 KB → 183,6 KB, −54%.**

**A armadilha do stripper de JS é o motivo de ele não ser um regex de três
linhas:** `//` aparece dentro de string — `"https://i3automations.com"` — e
dentro de expressão regular. Um stripper ingênuo come a URL a partir do `//` e
**o arquivo continua com sintaxe válida**, então nem o `node --check` acusa. Por
isso há uma máquina de estados que sabe onde está: string simples, dupla,
template, regex ou código.

E a prova que fecha: o stripper devolve a lista de LITERAIS junto com a saída, e
roda duas vezes. Se um literal mudou, ele comeu conteúdo em vez de comentário.
**941 literais, nenhum alterado**, e os 12 arquivos passam no `node --check`.

**O que ele NÃO faz, de propósito:** não renomeia variável, não reordena regra,
não junta seletor, não remove ponto-e-vírgula. E `enxugar()` não colapsa espaço
DENTRO da linha — `calc(100% - 20px)` precisa dos espaços em volta do `-`, e um
minificador que os remove quebra o calc sem erro nenhum: o valor vira inválido e
a declaração cai.

**Cada arquivo publicado abre com uma linha de proveniência**, e ela paga o
próprio peso: sem ela alguém abre `site/css/style.css`, edita, e o próximo build
apaga o trabalho sem dizer nada. 60 bytes contra uma tarde perdida.

**O HTML precisou de passe próprio.** `build_ativos.py` só alcança `fonte/`, e
sobravam **39 comentários / 8,9 KB** no HTML publicado — a maior parte no script
de tema, que é inline de propósito (tem de rodar antes da primeira pintura;
arquivo externo chegaria tarde). `limpar()` fatia o documento nos limites de
`<script>` **primeiro** e manda cada pedaço ao limpador que serve a ele.
**Invertido, um `<!--` dentro de uma string de JS levaria código junto** — e o
defeito não apareceria no build, apareceria no navegador de alguém.

### SEO: a canônica da home apontava para uma URL que ninguém digita

Era `https://i3automations.com/index.html`. O endereço que existe é
`https://i3automations.com/` — e as duas formas servem a mesma página, que é a
definição de conteúdo duplicado. `url_canonica()` passou a mapear a home para a
barra.

**E `canonica` quase virou duas canônicas.** Ao transformar a chave do template
de URL crua em tag `<link>`, o `og:url` — que consome a MESMA chave — recebeu o
elemento inteiro dentro do próprio `content`, e toda página saiu com duas.
Separado em `canonica` (valor) e `tag_canonica` (marcação). **Valor e marcação
não dividem chave de template.**

Entrou junto: **sete og:image por página**, geradas a 1200x630 (a única de antes
ampliava 1,07x); `sitemap.xml` e `robots.txt` saindo do mesmo lugar que as
páginas, não à mão; e BreadcrumbList em JSON-LD, sem o qual o buscador lê a URL
crua em vez de "i3automations.com > Capabilities".

### A 404 não é enfeite, é o conserto de um defeito de indexação

Este arquivo já registrava, desde 18/08, que **hospedagem estática devolve o
`index.html` com status 200 para qualquer caminho inexistente**. Inofensivo numa
demo; no domínio real, cada URL errada vira uma CÓPIA DA HOME aos olhos do
buscador, multiplicada por quantos links quebrados apontarem para cá.

Com `404.html` presente, a hospedagem serve ele e devolve 404 de verdade.

**Ela leva `noindex` e NÃO leva canônica.** Canônica que aponta para si mesma
numa página `noindex` é sinal contraditório — uma diz "indexe esta URL", a outra
diz "não indexe", e o buscador resolve o empate como quiser. Página de erro não
tem canônica, tem status.

E ela não é um beco: abaixo da mensagem vem o bloco de contato inteiro, em
`min-height: 62vh` — o visitante vê que há para onde ir **sem rolar**.

### `_headers` existe, e o que ele NÃO tem é deliberado

Cache longo em `/img/*` e `/fonts/*` porque **o nome do arquivo carrega a
largura** (`refinaria-2560.jpg`) — aquele nome nunca muda de conteúdo. Cache
curto (1h) em CSS e JS, que têm nome fixo e mudam a cada entrega: cache longo ali
serviria a folha velha para quem já visitou, e o sintoma seria "o site não
atualizou para mim". **O dia em que isso muda é o dia em que os ativos ganharem
hash no nome.**

**Não há `X-Robots-Tag: noindex` no arquivo, e a ausência é a decisão.** Este
arquivo registra que endereço de DEMONSTRAÇÃO precisa dele para não competir com
o domínio oficial — e que ele **tem de ser apagado** quando o domínio real
entrar, ou o site oficial sai do Google. Escrever `noindex` por padrão é criar
exatamente essa armadilha, com a agravante de que o sintoma (sumir do buscador)
aparece semanas depois da causa. **Quem publicar numa demo acrescenta a linha na
hora; o padrão falha para o lado seguro.**

### A estrutura, medida

| | |
|---|---|
| `site/` | 304 arquivos, **25,9 MB** |
| imagem (.jpg/.webp/.avif/.png) | 25,4 MB — **98,3%** |
| HTML + JS + CSS + fonte | 0,44 MB — **1,7%** |
| caminhos absolutos no HTML | **0** |

Os 9,26 MB de `.jpg` **nunca são transferidos na prática**: nenhum deles está em
`srcset`, os 57 são só o `src` de reserva do `<picture>` para quem não tem AVIF
nem WebP. É peso de repositório, não de visitante.

O que o visitante baixa na primeira dobra, medido por página (HTML + JS + CSS +
fonte + as imagens NÃO-lazy, em AVIF):

| página | 1ª dobra | total de imagem |
|---|---|---|
| index | **0,37 MB** | 0,81 MB |
| gallery | 0,17 MB | 1,76 MB |
| who-we-are | 0,17 MB | 1,05 MB |
| as demais | 0,14–0,16 MB | — |

A home é a mais pesada de propósito: são as quatro folhas da prancha em
`fetchpriority="high"`, decisão já registrada aqui — fotografia que é prova logo
abaixo da primeira dobra.

**Nada a cortar.** Os 7 `.jpg` que não aparecem em `src` nem em `srcset` são as
og:image, citadas por URL absoluta em `<meta>`.

### Ferramentas atualizadas

`varredura.py` aprendeu que `_headers` e `404.html` não são órfãos, e por vias
diferentes: o primeiro é lido pela HOSPEDAGEM, nunca pelo navegador; o segundo é
servido quando o caminho NÃO EXISTE, então por definição nenhum link aponta para
ele — **link para a 404 seria justamente o defeito**.

`conflitos.py` e `previa_junta.py` passaram a ler `fonte/`, que é onde a fonte
mora agora.

### PENDENTE

**Ver no navegador continua pendente** — a extensão do Chrome segue desconectada.
Verificado fora dele: 301 referências / 0 quebradas / 0 órfãos, 0 seletores
duplicados, 0 fotos repetidas entre papéis, tags balanceadas nas 10 páginas, 12
arquivos JS e todos os scripts inline passando no `node --check`, e os JSON-LD
parseando.

---

## 2026-08-20 (contenção) — A foto sumia no hover, e a causa não se parece com o sintoma

Reportado: em "What we actually do", a imagem SOME ao passar o mouse. Defeito
meu, introduzido na entrega anterior.

### A causa

**Elemento transformado vira BLOCO DE CONTENÇÃO dos descendentes absolutos.**

O `<img>` da prancha é `position: absolute; inset: 0` — fora do fluxo. Então o
`<picture>` que o envolve tinha **altura zero**, e o img resolvia contra
`.prancha__moldura`, que é `position: relative`. Funcionava.

Aí o hover pôs um `transform` no `<picture>`. Isso o promoveu a bloco de
contenção: o img passou a resolver contra uma caixa de **0×0** e a fotografia
desapareceu.

O conserto é dar tamanho ao `picture` — `position: absolute; inset: 0`. Ele
preenche a moldura, o img resolve contra a mesma geometria de sempre, e o
transform do hover escala a caixa certa.

### Por que eu tinha posto o transform ali, e continua certo

O `img` já tem transform da entrada por rolagem. Pôr o hover no mesmo elemento
sobrescreveria a entrada ou obrigaria a transicionar uma propriedade que o
scroll reescreve por quadro. A separação estava certa — **faltava dar caixa ao
elemento que eu escolhi transformar.**

### REGRA QUE FICA

**Antes de transformar um elemento, conferir se ele tem descendente
`position: absolute`.** O transform muda o referencial deles, e o sintoma —
conteúdo sumindo — não se parece nada com a causa. É irmã da armadilha de
19/08 (`z-index` negativo em filho só pinta se o pai for contexto de
empilhamento): as duas são sobre o pai mudar de papel sem avisar.

### Varredura: era caso único

Escrita uma varredura que cruza "selectors que recebem `transform`" com
"selectors com filho `position: absolute` declarado". **Nenhuma outra
ocorrência no site.** Os outros transforms ou estão no próprio `<img>`
(galeria, faixa, obra) ou em elemento com tamanho próprio (`.lente` é
`width/height: 100%`, `.braco` é `position: relative` com altura).

Confirmada também a ordem de pintura: a marca de registro é `z-index: 2` e o
`picture` agora é posicionado com `z-index: auto`, então as marcas continuam
por cima.

294 referências, 0 quebradas, 0 órfãos. 0 conflitos de cascata.

---

## 2026-08-20 (hover) — Dois transforms no mesmo elemento, e o outro é da rolagem

Pedido: as fotos de "What we actually do" (a prancha) e de "Industries served"
(os setores) precisam de animação de hover.

Levantado o estado: a **prancha não tinha hover nenhum**, e os setores tinham a
LENTE — que abre sob o ponteiro e revela a fotografia por baixo do traço — mas
a folha em volta não reagia. A lente sozinha é um instrumento apontado para o
card, não o card respondendo.

O gesto veio pronto da galeria, que já o estabeleceu: **a foto avança de leve,
a marca de registro acende, o índice vira acento**. Nada inventado.

### O DEFEITO QUE QUASE ENTROU: dois transforms disputando o mesmo elemento

`.prancha__moldura img` **já tem** um `transform`, escrito pela entrada por
rolagem (§21): `scale(1 + (1 - --avanco) * .06)`. Pôr o zoom de hover no mesmo
elemento daria uma de duas coisas ruins:

  ou o hover SOBRESCREVE a entrada, e a folha para de assentar ao rolar;
  ou eu ponho `transition` numa propriedade que o scroll REESCREVE a cada
    quadro -- e transição sobre valor que muda por quadro é engasgo garantido.

A saída foi separar por elemento: o `img` continua sendo da rolagem, o
`picture` que o envolve é do ponteiro. **Aninhados, os dois transforms se
multiplicam**, e cada um tem a sua transição. Nenhum dos dois sabe do outro.

**Regra que fica: antes de animar `transform`, procurar quem já anima
`transform` naquele elemento.** É a propriedade mais disputada do site — a
entrada por rolagem, a lente, o voo da intro e agora o hover, todos escrevem
nela.

### O hover NÃO toca os irmãos, e isso é história

A primeira prancha tinha destaque com `:has()`: o item apontado crescia e os
outros caíam para 38% de opacidade. O usuário mandou tirar em 19/08, com razão
— a fileira inteira reagindo à passada do ponteiro chamava mais atenção para o
mecanismo que para as fotografias. Conferido: nenhum seletor novo alcança irmão.

### Nos setores, o zoom vai na LENTE inteira

E não só no `<img>`: com WebGL ativo, `.lente.is-gl .lente__foto` está em
opacidade 0 e quem desenha é o canvas. Escalar só a imagem não moveria nada na
tela. Escalando `.lente`, fotografia e canvas avançam juntos e continuam
casados.

`lente.js` mede o ponteiro por `getBoundingClientRect`, que já leva o
transform em conta — então o mapeamento da lente continua certo sob o zoom.

### Conflito achado pela própria ferramenta

`ferramentas/conflitos.py` acusou `.prancha__moldura picture` declarando
`display` em dois lugares: a definição do componente (§17) já dizia
`display: block`, e eu repeti. Removido — aqui entra só o que é do ponteiro.
**É a segunda vez que essa ferramenta pega algo meu no mesmo dia em que foi
escrita.**

### Orçamento de dourado

O hover acende marca de registro, tique e régua em dourado. Todos
**transitórios e sob o ponteiro**, então não entram no teto de dois por dobra —
a mesma isenção que o §6.5 concede à lente. Nenhum dourado permanente foi
acrescentado.

294 referências, 0 quebradas, 0 órfãos. 0 conflitos de cascata.

---

## 2026-08-20 (intro) — A marca desliza, e o campo era do rodapé

Pedido: melhorar a animação de entrada — *"não está com as cores certas, e
mude um pouco também, faça a logo da i3 vir deslizando e ir para seu lugar após
o motion."*

### Duas coisas erradas de cor, e a segunda é de orçamento

**O campo era o do RODAPÉ.** `.intro` usava `--sup-3-fundo` (#000814), a cor
mais funda do site — a do fecho. A marca voava sobre quase-preto e pousava
sobre `--sup-3` (#001D3D), então o véu sumia revelando um navy diferente do que
estava atrás dela um quadro antes. Passou a `--sup-3`: a saída da intro deixa
de ter troca de cor, o que desaparece é só o véu e não o chão.

**Havia TRÊS dourados na mesma dobra**, contra o teto de dois:

| janela | douradas |
|---|---|
| 0 → 0,9s | contorno + cursor = 2 |
| 1,6 → 2,5s | contorno + cursor + **tela** = 3 |
| após 3,2s | cursor + tela = 2 |

O contorno virou **aço** (`--navy-luz`, 7,83:1 sobre o campo). E não é só a
conta fechando: **o contorno é o DESENHO, e este site desenha em aço** — o
braço em #9FBEE0, a marca 3D em arame, a planta em aresta. Dourado é o acento
da MARCA, não do traço que a constrói.

### O deslizar vive no mesmo `animate` do voo

A marca entra da esquerda, desembaça na chegada e só então se desenha:

| momento | offset | o que acontece |
|---|---|---|
| 0 → 0,9s | 0 → .161 | **desliza** da esquerda, desfoque saindo junto |
| 0,9 → 1,8s | .161 → .321 | parada, o contorno se traça |
| 1,6 → 2,5s | | as formas cheias entram por trás |
| 2,5 → 3,2s | | o contorno se apaga |
| 4,0 → 5,6s | .714 → 1 | voa até o lugar dela no herói |

**O deslizar e o voo são a MESMA lista de keyframes, e isso não é economia.**
Os dois são `transform`: com um em CSS e o outro em WAAPI, uma das duas
animações seria descartada **em silêncio** — quem perde não avisa. Uma lista
só, uma linha do tempo só, nada disputa.

Entre .161 e .714 a peça fica parada de propósito: é nesse silêncio que o
desenho acontece. Objeto que continua se movendo enquanto se desenha não deixa
ver nenhuma das duas coisas.

A distância é travada em **520 px**: `42vw` num monitor largo mandaria a marca
para 800 px de distância e ela entraria correndo, que é o oposto do gesto.

### A REGRESSÃO QUE EU MESMO INTRODUZI, e que quase foi junto

Atrasar o desenho para depois da chegada quebrou o movimento reduzido. Ali a
intro fecha em **0,8 s** — antes de o contorno começar (0,9) e muito antes das
formas (1,6). Com `backwards`, o estado durante o atraso é o INICIAL: contorno
invisível, formas em opacidade 0.

**Quem pede movimento reduzido veria uma marca vazia por 0,8 s e ela sumiria.**

O bloco de redução passou a zerar as animações da marca também, deixando o
elemento no estado final — formas cheias visíveis, contorno apagado. É a marca,
parada, que é o que a regra dura nº3 pede: o que carrega significado aparece,
só não viaja.

**Regra que fica: ao ATRASAR uma animação, conferir o caminho de movimento
reduzido.** O atraso é invisível ali — o que fica na tela é o estado `from`, e
`backwards` garante justamente isso.

294 referências, 0 quebradas, 0 órfãos. 0 conflitos de cascata.

**Não vista rodando** — a intro é das poucas peças que nenhuma medição
substitui, e o Chrome segue desconectado.

---

## 2026-08-20 (registro) — Três peças irmãs, três tipografias, nenhuma escolhida

Pergunta do usuário: *"past performance, você acha que faz sentido o layout
dessa animação com a tipografia do site?"*

**Não fazia, e o número é feio.**

### O sinóptico saía a 27 px

A composição vive num espaço local de 520x260 e é AMPLIADA para caber na
caixa. A 1440 o fator é **2,46**. Com a fonte declarada em `11px` dentro desse
espaço, o rótulo renderizava na tela com **27,1 px** — mais que o dobro do
maior mono do site, que vai de 11 a 13.

E o tamanho era INSTÁVEL: `m` muda com a janela, então a tipografia da peça não
tinha relação nenhuma com a escala do site. Todo o resto obedece a um `clamp`;
esta flutuava livre.

Dividir por `m` cancela a ampliação — o texto é posicionado no espaço local,
junto do desenho, e renderiza no tamanho de tela declarado.

**E os OFFSETS tiveram de vir junto.** O rótulo do tanque estava a 13 unidades
locais da base (32 px de tela), medida escolhida quando a letra tinha 27 px.
Com a letra em 12, o rótulo descolava. Tudo que fica ao lado de uma letra
passou a se medir EM TIPO: tag a `TIPO * 1,15`, faixa de alarme a `TIPO * 1,7`.

### A pergunta expôs os irmãos

Medidas as quatro peças, cada uma tinha ido para um lado:

| peça | antes | tracking |
|---|---|---|
| malha | 11 px | nenhum |
| mimico | **27,1 px** | nenhum |
| carta | 10 px | nenhum |
| clp | sem texto | — |

Três peças irmãs, escritas no mesmo dia, com três tipografias diferentes — e
**nenhuma delas escolhida**: 11 e 10 saíram do dedo, e 27 era um acidente de
escala. Enquanto isso todo rótulo mono do CSS tem tracking (.02 a .16em).

O registro foi para `tela.js` como função única: **12 px com .14em**, que é o
da linha de cota da prancha (`.prancha__cota`). E é o que um rótulo de peça
é — ANOTAÇÃO sobre um desenho, não corpo de texto.

`T.tipo(ctx, raiz, escala)` recebe `1/m` de quem desenha em espaço
transformado. `letterSpacing` do canvas é recente (Chrome 99, Safari 16.4);
onde não existe a atribuição é ignorada e some o acabamento, não a informação.

### Regra que fica

**Peça que desenha texto dentro de um espaço transformado precisa cancelar a
transformação na fonte.** O erro não aparece no código — `"11px"` parece 11 px
— e só a conta `11 x m` mostra o que chega à tela.

E o corolário: **três consumidores do mesmo registro precisam de UMA
definição.** `tela.js` já centralizava caixa, dpr e pausa; faltava a
tipografia, que era justamente onde as três divergiram.

294 referências, 0 quebradas, 0 órfãos. `node --check` limpo nas cinco peças.

---

## 2026-08-20 (CLP) — O armário virou rack, e o nome do arquivo mudou junto

Retorno: *"a animação não faz sentido ao meu ver (Capabilities), quero que você
mude por um CLP, pode usar a mesma estratégia, e mude o fundo pela grade para
acompanhar os outros."*

### Por que o armário não lia, e por que o rack lê

A peça anterior era um painel COMPLETO — placa de montagem, três trilhos,
sete disjuntores, contator, bornes, cinco trechos de canaleta e a porta. Com
tanta parte e a porta cobrindo a frente, a leitura era "uma caixa"; nem o
repouso parcialmente aberto de 0,34 resolveu, porque o problema não era a pose,
**era a quantidade de coisa**.

O CLP tem seis módulos numa fileira só, e a fileira **se explica contando**:
trilho e barramento, fonte, CPU, cartão de entradas, cartões de saída, bornes.
Dá para ver o barramento por trás e entender que cada bloco pluga nele.

E é o assunto certo desta página: "PLC Programming" é a segunda das oito
disciplinas, e o rack é o objeto que a i3 realmente especifica, monta e programa
— o armário inteiro era mais do que a página estava dizendo.

### A estratégia é a mesma, só a geometria mudou

Segmentos em lista, expansão em quad, instâncias, atenuação por profundidade,
lente dourada com o `RUIDO_GLSL` de `gl.js`, arrasto para orbitar, deriva que
vai e volta, distância de câmera calculada como máximo entre montado e separado.
Nada disso foi reescrito — **287 segmentos contra os 411 do armário**, e o resto
da máquina é o mesmo arquivo.

Medido pelo probe, com as camadas separadas:

| camada | x | z separado |
|---|---|---|
| trilho + barramento | −2,55..2,55 | fixo |
| fonte | −2,50..−1,62 | 1,09..1,62 |
| CPU | −1,58..−0,46 | 1,39..1,94 |
| cartão DI | −0,24..0,44 | 1,69..2,21 |
| cartões DO | 0,52..1,96 | 1,99..2,51 |
| bornes | −0,20..1,92 | 3,75..3,90 |

**0 colisões.** Os bornes vão mais longe porque são a primeira coisa que sai
quando alguém troca um cartão — a ordem da separação é a ordem real de
desmontagem, não escalonamento decorativo.

A proporção passou de 4/3 para **16/9**: o rack tem 5,1 unidades de largura
contra 2,1 de altura, e numa moldura quadrada a câmera recuava para caber a
altura que não existe.

### O NOME DO ARQUIVO MUDOU JUNTO, e isso não é detalhe

`painel.js` virou `clp.js`; `.painel` virou `.clp`; `--painel-*` virou
`--clp-*`; `data-painel` virou `data-clp`. Um arquivo chamado `painel` que
desenha um rack de CLP é a mesma classe de problema que `.secao--foto-claro`
foi em 19/08 — **nome que AFIRMA o que a peça não é**. Renomear custa dez
minutos hoje e uma sessão de confusão daqui a um mês.

### A grade, e por que o fundo continua escuro

A grade é a mesma de `.planta__grade` — mesmo token `--traco-grade`, mesmo
passo de 32 px. É papel milimetrado por baixo do desenho, não textura.

**O fundo escuro não é escolha, é a conta.** Sobre papel, `#FDC500` dá 1,46:1 e
a lente APAGARIA o desenho em vez de acendê-lo (regra crítica nº4). Em
`--sup-3` o dourado dá 10,59:1 no claro e 7,74:1 no escuro. É a mesma conta que
a planta fez em 19/08 e que a versão anterior desta peça já tinha pago.

Detalhe de cascata que precisou de atenção: `.peca` usa o atalho `background:`,
que zera `background-image`. `.clp` vem DEPOIS no arquivo e declara
`background-color` e `background-image` separados, então a grade vence. Se
alguém reordenar, a grade some sem erro nenhum.

### Estado

294 referências, 0 quebradas, 0 órfãos. 0 classes mortas, 0 conflitos, nenhum
`painel.js` órfão no disco. `node --check` limpo nas cinco peças.

---

## 2026-08-20 (retorno) — Quatro correções, e uma delas era uma recusa minha mal resolvida

Retorno do usuário sobre as quatro peças novas. Os quatro pontos procediam.

### 1. contact: "não entendi o que você quis dizer com esse quadro"

**A recusa estava certa; a conclusão estava errada.** Eu tinha me negado a
desenhar litoral de memória — inventar geografia é o tipo de afirmação que
este site já removeu da galeria — e parei aí, entregando retícula com duas
cruzes. Não lê como mapa, e o usuário tem razão.

**A terceira saída era ir BUSCAR O DADO.** Fronteiras estaduais dos EUA,
domínio público (TIGER/US Census), guardadas em
`referencia/us-states.geojson`. `ferramentas/extrair_costa.py` recorta os
estados da janela, descarta os anéis inteiramente fora e simplifica por
Douglas-Peucker:

| eps | pontos | |
|---|---|---|
| 0,06 | 381 | detalhe que esta escala não mostra |
| **0,10** | **246** | escolhido |
| 0,15 | 172 | a península da Flórida começa a ficar reta |

**Regra que fica: quando a alternativa honesta a inventar é NÃO DESENHAR, a
terceira saída costuma ser buscar o dado.** Não parar na recusa.

Os anéis vêm inteiros — o Texas chega a 106°W — então o traço é recortado na
moldura, senão vaza para fora da chapa.

### 2. services: o alternador de sintonia saiu

*"não acho que faça diferença."* Saiu o botão, o rótulo, o CSS de
`.malha__controles` e a segunda entrada de sintonia. **A medição fica no
comentário**, que é onde ela vale: os 8,0/6,0 que ultrapassam 13,5% e nunca
assentam continuam registrados como contraprova, sem pesar no arquivo.

### 3. past-performance: o sinóptico ganhou seção própria

Ele estava dentro do bloco de abertura — seção `--compacta`, 96 px de respiro
contra os 160 normais — espremido logo abaixo do parágrafo de introdução. E
chegava ANTES das seis fichas, ou seja, antes de o visitante saber o que a
página é.

Agora vem DEPOIS do registro de obras, em seção própria com bloco de duas
colunas como todas as outras: *"What stays behind / The screen that runs the
shift"*. É a ordem que a página conta — primeiro o que foi entregue, depois a
tela que ficou rodando.

### 4. capabilities: "é uma porta? não consigo mexer nem brilha em amarelo"

Três queixas, três causas distintas:

**"É uma porta?"** Em repouso a explosão era 0, então a porta cobria tudo pela
frente e a peça lia como uma caixa fechada. O repouso passou a **0,34**: as
camadas aparecem desde o primeiro quadro e o objeto se explica sozinho. O
ponteiro leva a 1.

**"Não consigo mexer."** Não havia arrasto. Ganhou a mesma gramática do braço e
da marca — o mesmo ponteiro acende a lente e, com o botão apertado, orbita.
Deriva de repouso que VAI E VOLTA (de sentido único encostaria no limite e
ficaria parada lá) e inclinação travada entre −0,85 e 0,30, porque de perfil um
armário vira uma tira vertical e para de comunicar.

**"Não brilha em amarelo."** Esta era a mais interessante: **era impossível
onde a peça estava.** Ela ficava sobre papel, e medido, `#FDC500` sobre
`#F2F5F8` dá **1,46:1** — a revelação APAGARIA o desenho em vez de acendê-lo
(regra crítica nº4). A mesma conta que a planta já tinha feito em 19/08.

O conserto não foi mudar a cor, foi **mudar a superfície**: o painel passou a
`--sup-3` como as outras três peças novas. Aí o dourado dá 10,59:1 no tema
claro e 7,74:1 no escuro — e as quatro peças passam a partilhar o mesmo campo,
o que também as faz ler como família.

A lente usa o MESMO `RUIDO_GLSL` de `gl.js`, o mesmo raio (0,30) e a mesma
curva do braço. Se um dia o raio de lá mudar, este muda junto — senão a página
passa a ter dois instrumentos de tamanhos diferentes apontados para ela. E o
espelho do eixo Y do ponteiro já nasceu certo, em vez de custar a sessão que
custou no herói.

### Estado

294 referências, 0 quebradas, 0 órfãos. 0 classes mortas, 0 conflitos.
`node --check` limpo nos cinco arquivos de peça.

**Continua pendente ver rodando.** O Chrome segue desconectado.

---

## 2026-08-20 (quatro peças) — Cada página sem elemento próprio ganhou um, e de TIPO diferente

Pedido: elementos customizáveis como o logo 3D, o braço, os fios e o mapa, nas
páginas que ainda não têm. ("O mapa" é a `planta.js` — não havia mapa
geográfico no site até agora.)

Quatro páginas estavam sem: capabilities, past-performance, services e
**contact, que não tinha nem um**.

### A regra que guiou as escolhas

Não adianta um quinto objeto girando. As quatro peças existentes são de tipos
distintos — braço é CINEMÁTICA, marca é PRISMA, planta é SÍTIO, feixe é
ROTEAMENTO — e cada peça nova teve de trazer um tipo novo:

| página | peça | tipo novo |
|---|---|---|
| services | `malha.js` — PID que responde ao arrasto | **sistema simulado** |
| capabilities | `painel.js` — armário explodido | **separação num eixo** |
| past-performance | `mimico.js` — sinóptico de SCADA | **tela de operação** |
| contact | `carta.js` — as duas operações plotadas | **geografia** |

**Uma ideia foi trocada no meio.** Eu tinha proposto um HISTORIADOR para
past-performance, mas `malha.js` já é uma tendência temporal — duas séries de
tempo a duas páginas de distância enfraqueceriam as duas. Virou sinóptico, que
é o artefato que a empresa entrega e roda no campo.

### Dois núcleos, e o segundo nasceu no dia certo

`tela.js` faz para as peças de canvas 2D o que `gl.js` já fazia para as de
WebGL: medir a caixa, resolver o dpr, parar fora da tela, respeitar movimento
reduzido, reagir ao tema. **Extraído no começo e não depois da segunda cópia**,
porque três consumidores nasceram juntos.

`pagina()` injeta os dois POR DEDUÇÃO: quem consome `I3GL` recebe `gl.js` na
frente, quem consome `I3Tela` recebe `tela.js`. Depender de quem escreve a
tupla lembrar da ordem é como um núcleo some numa madrugada.

### A MEDIÇÃO DERRUBOU A PEÇA MAIS IMPORTANTE, e essa é a lição da entrega

`malha.js` promete provar a tese da empresa: mesma planta, duas sintonias,
resposta diferente. Portei o laço para Python e medi a resposta ao degrau. Os
valores que eu tinha escolhido **ensinavam o CONTRÁRIO**:

| sintonia | overshoot | acomodação ±2% | cruzamentos |
|---|---|---|---|
| "frouxa" (3,10 / 2,60) | 2,2% | 3,4 s | 20 |
| "ajustada" (1,15 / 0,42) | 0,0% | **12,5 s** | 1 |

A errada parecia melhor: ultrapassava quase nada e assentava quatro vezes mais
rápido. Varridas as combinações, ficou **8,00 / 6,00** contra
**2,20 / 0,85 / 0,30**:

| sintonia | overshoot | acomodação | cruzamentos |
|---|---|---|---|
| frouxa | 13,5% | **não assenta** | 36 |
| ajustada | 0,0% | 8,0 s | 0 |

**O que ensina não é o overshoot, é a oscilação sustentada** — a frouxa nunca
para de caçar o setpoint dentro da janela de 22 s, e é isso que o olho lê como
"está errado". A ajustada assenta em 8 s, perto do mínimo teórico desta planta.

**Regra que fica: peça que AFIRMA um comportamento tem de ter o comportamento
medido. Um gráfico bonito com números escolhidos no olho pode demonstrar o
oposto da tese e ninguém percebe.**

### Um falso alarme que eu quase "consertei"

A carta calcula 1.289 km entre Houston e Lakewood Ranch, e eu tinha escrito
"referência ~1.480" no teste. **A referência era palpite meu.** Conferido por
três fórmulas independentes — haversine, lei esférica dos cossenos e Vincenty
esférico — as três dão 1.289,2 km com desvio de 0,00. O cálculo estava certo.
É a segunda vez nesta sessão que calibrar antes de condenar salva uma peça.

### Dois defeitos reais, achados pela varredura

**`%` liga mais forte que `+` em Python.** Ao inserir a carta partindo a string
do contact, só o ÚLTIMO fragmento recebeu o dicionário e `%(zap)s` foi para o
HTML literal. A varredura acusou como referência quebrada. A peça passou a
entrar por PLACEHOLDER, como o resto do arquivo já fazia.

**Classe emitida sem regra.** O helper `peca()` escrevia
`class="peca__tela carta__tela"`, e `carta__tela`/`mimico__tela` não tinham
regra nenhuma — uso sem classe, que é o contrato que ninguém cumpre. Uma classe
só no canvas; quem precisa de regra própria escreve `.malha .peca__tela`.

### O painel: subconjunto que divide plano se separa em sequência

O probe mediu rack de CLP em `1.28..1.62` e disjuntores em `1.29..1.61` — os
dois moram em trilho DIN, então partilham o plano no armário real. Mas na vista
explodida ficavam indistinguíveis em profundidade, e o rótulo prometia seis
camadas mostrando cinco. Afastados em sequência: **0 sobreposições**, 411
segmentos.

E a distância de câmera é o MÁXIMO entre montado e separado, não a do instante
— medindo só a pose atual a peça encolheria enquanto explode, que é o zoom
involuntário que `braco.js` já pagou com as seis fases do ciclo.

### O que NÃO ganhou peça

As duas páginas legais, de propósito: são documentos, e elemento interativo ali
é ruído.

### PENDENTE

**Nenhuma das quatro foi vista rodando.** O Chrome segue desconectado. O que
está verificado: a física da malha (portada e medida), a matemática da carta
(três fórmulas), a geometria do painel (probe em Node, 411 segmentos, 0
sobreposições) e a estrutura (294 referências, 0 quebradas, 0 órfãos, 0 classes
mortas, 0 conflitos). O que só o navegador responde: os shaders do painel
compilando, e se as três telas 2D leem bem em tamanho real.

---

## 2026-08-20 (quatro duplas) — Não existe faixa livre comum, e isso muda o componente

Pedido, com captura anotada: "Federal contracting + Talk to an engineer"
(who-we-are) e "The ledger + Talk to an engineer" (past-performance) viram
duplas como as de home e services. E remover o `_._._` — o tique circulado na
imagem.

### A descoberta que forçou uma mudança no componente

A `.dupla` abria o véu num ponto FIXO (34–42%), tunado para home e services. Ao
medir as duas caixas novas, a fotografia ficava aberta **em cima do texto**:

| página | faixa livre |
|---|---|
| home | 27–52% |
| services | 30–57% |
| past-performance | 37–61% |
| **who-we-are** | **53–68%** |

**A intersecção das quatro é VAZIA.** who-we-are tem o bloco de credenciais
federais, que é longo, e empurra o vão livre para baixo. Com a abertura fixa o
corpo caía para **1,9:1**.

A abertura virou `--d-abre` / `--d-fecha`, por dupla. **Regra que fica: onde um
véu abre é propriedade da PÁGINA, não do componente — depende da altura do
conteúdo, e conteúdo muda de página para página.**

### A caixa de who-we-are eliminou quase todo o acervo

1440x**1560** (proporção 0,92, quase retrato), porque a seção de credenciais é
longa. Nessa caixa **só `baterias` passou AA** — as outras reprovam o corpo
entre 3,5 e 4,1. É a única fonte em RETRATO do acervo (4164x5552), que é
justamente o formato de que uma caixa alta precisa.

Sorte que o assunto fecha: módulos de armazenamento conversam com a copy, que
fala de geração solar. Mas **a resolução decidiu antes do assunto**, e vale
registrar que foi nessa ordem.

`faixa/solar-estrutura`, que eu tinha escolhido para essa seção HÁ UMA HORA,
saiu: 1920x1231 amplia 1,27x numa caixa de 1560. Escolha certa para uma seção,
errada para uma dupla — a caixa dobrou de altura.

### The ledger perdeu o off-white, e isso é consequência declarada

`.dupla` é escura por construção: as seções cedem o fundo para o invólucro que
segura a fotografia. Então "The ledger" deixou de ser `secao--offwhite`.

**A alternância de superfície que ela trazia se perde** — decisão registrada em
20/08 ("o resumo passou a off-white, para a página alternar superfície em vez
de ir navy → navy"). O que entra no lugar é o par lendo como bloco único, que
foi o pedido. Fica registrado como troca consciente, não descuido.

Efeito colateral: `.secao--foto-corpo` ficou **sem consumidor pela segunda
vez** e saiu de novo (2959 bytes). Ela já tinha sido removida em 20/08 e
restaurada duas horas depois para esta mesma seção.

### O dourado: cinco números que teriam virado seis marcas

`.secao--escura .numeros dt` é DOURADO. Com "The ledger" virando escura, os
cinco números da faixa acenderiam — mais o eyebrow, **seis marcas** contra o
teto de duas.

Sobrescrito para `--tinta-titulo` dentro da dupla. E o seletor é
`.dupla .secao--escura .numeros dt` **(0,3,1)** e não `.dupla .numeros dt`
(0,2,1): contra `.secao--escura .numeros dt`, que também é (0,2,1), a segunda
venceria só por ordem no arquivo — **a armadilha exata que `.contato__valor`
custou ontem.**

### O `_._._` saiu inteiro

Era `.junta--interna`, o tique de 120 px na origem do container que marcava
"mesma folha". O usuário circulou na captura, e ele tem razão pelo motivo
estrutural: **numa dupla, em que duas seções dividem uma fotografia e se leem
como um bloco só, um marcador dizendo "aqui começa outra coisa" contradiz o
que a peça inteira afirma.**

Removido da CSS, do gerador e da documentação. Agora superfície igual não ganha
marca nenhuma. A numeração das folhas continua contígua nas nove páginas —
conferido, porque o tique não participava dela.

### Medido

| dupla | escala | pior fundo | branco | dourado | corpo | amplitude |
|---|---|---|---|---|---|---|
| who-we-are claro | 0,563x | #384D63 | 8,71 | 5,46 | 4,74 | 28,4 |
| who-we-are escuro | | #204D76 | 7,48 | 5,52 | 4,58 | 15,6 |
| past-perf claro | 0,562x | #374E67 | 8,58 | 5,38 | 4,67 | 42,3 |
| past-perf escuro | | #1E4D78 | 7,47 | 5,51 | 4,57 | 23,1 |

### Estado

**289 referências**, 0 quebradas, 0 órfãos. 0 classes mortas, 0 conflitos,
0 repetições entre papéis. Quatro duplas no site, cada uma com abertura própria.

**Continua em aberto:** "Vendor profile" tem 6 marcas douradas (1 eyebrow +
5 `.credencial__valor`). Não é regressão desta entrega — é a mesma pendência
de 20/08, e continua esperando decisão do usuário.

---

## 2026-08-20 (oclusão) — O barramento saiu de "Our mission" sem quebrar a cadeia

Pedido: tirar a animação de fios da seção "Our mission" (who-we-are).

**É a única seção do site que tinha barramento E fotografia ao mesmo tempo.**
Duas tramas no mesmo bloco brigam e a mais fina é quem some — o mesmo argumento
que já tinha tirado o barramento do CABEÇALHO desta página em 19/08. E ele
pesava mais agora: a foto nova (`faixa/ferramental`) rende amplitude **30,6**
contra os 15,8 da anterior, ou seja ficou bem mais presente e disputava mais.

### Por que a cadeia não quebrou

O barramento atravessa três seções e cada trecho declara por onde entra e sai:

| trecho | seção | rota |
|---|---|---|
| `feixe_1` | Since 2000 | esq → **dir** |
| ~~`feixe_2`~~ | ~~Our mission~~ | ~~dir → dir~~ |
| `feixe_3` | How we work | **dir** → esq |

O trecho removido era `dir → dir`, um **corrimento reto do mesmo lado**. Como
`feixe_1` sai à direita e `feixe_3` entra pela direita, os dois continuam
casando no mesmo x. O barramento desce, passa ATRÁS da seção fotográfica e
reaparece do outro lado.

**Isso não é um corte, é oclusão** — e é como um roteamento real se comporta ao
passar por trás de alguma coisa. O UnidoCLP já registrava a mesma leitura para
a rede do herói dele: *"onde o enlace passa atrás de um prédio ele não está
desenhado — o pulso some na oclusão e reaparece do outro lado, que é o certo."*

**Se o trecho removido fosse `dir → esq`, a cadeia teria quebrado de verdade** e
seria preciso reapontar os vizinhos. Vale conferir a rota antes de remover
qualquer trecho, não só a marcação.

### Nada mais dependia dele

`.tem-feixe` só declara `position: relative` e o `z-index: 1` do container —
e `.secao--foto`, que esta seção é, já fornece `position: relative` mais
`isolation: isolate`. A chave `feixe_2` saiu do dicionário junto; `feixe()`
continua com dois consumidores.

287 referências, 0 quebradas, 0 órfãos. 0 classes mortas, 0 conflitos.

---

## 2026-08-20 (papéis) — Três fotos serviam a dois papéis, e eu otimizei a métrica errada

Dois pedidos juntos: a foto de "The ledger" está praticamente invisível, e
conferir se alguma foto se repete entre cabeçalhos e seções.

### A auditoria achou três, e uma era minha

| foto | onde |
|---|---|
| `cabecalho/servicos` | cabeçalho de services **E** fundo em who-we-are |
| `faixa/refinaria` | cabeçalho de capabilities **E** fundo em who-we-are |
| `faixa/robotica` | faixa da home **E** fundo de "The ledger" |

A terceira entrou dois dias atrás, por minha mão — e era exatamente a que o
usuário chamou de invisível. **Repetição e invisibilidade tinham a mesma
origem: escolher foto sem medir o que ela vira depois do véu.**

Virou `ferramentas/repetidas.py`. Galeria e placas de setor ficam de fora de
propósito: ali a repetição é esperada, porque a galeria é o acervo.

### Por que "The ledger" sumia, e não era a foto ser ruim

O véu de `.secao--foto-corpo` é **off-white a .78** — só 22% da foto chega à
tela. O que sobrevive a isso não é o assunto, é a **AMPLITUDE**: a variação de
luminância que resta depois da camada. Medido o p95−p5 sobre as 24 fotos do
acervo, depois do véu:

| | amplitude |
|---|---|
| `sala-controle` | 48,7 |
| `prensa-detalhe` | 48,1 |
| **`robotica` (a que estava lá)** | **34,8** |
| `solar-aereo` | 24,8 |

Terço inferior. Por isso lia como lavagem cinza. A substituta (`engrenagem`,
engrenagem e corrente) dá **46,2** — e é um mecanismo NEUTRO, que é o certo
para "six sectors, one discipline": não aponta setor nenhum, ao contrário da
célula robótica, que apontava só o automotivo.

### O ERRO DE MÉTODO, e ele me custou duas voltas

**Otimizei amplitude e ignorei o pior ponto local.** São métricas diferentes:
amplitude é VISIBILIDADE, o pior ponto é LEGIBILIDADE. Escolhi `prensa` para
"Our mission" por ter a maior amplitude sob navy (63,5) — e ela reprovava o
corpo em 3,74:1, porque era clara demais.

**E o modelo do véu estava errado junto.** Eu compunha o alfa dos dois
gradientes de `.secao--foto` (.55 vertical e .35 horizontal → .7075) e aplicava
UNIFORME na largura. Mas o horizontal vai de opaco na esquerda até .35 aos 62%:
o texto vive sob alfa entre .84 e .71, não sob .71 em todo lugar.

**Quem denunciou foi a calibração**: medi as fotos que o site JÁ publica e elas
"reprovavam" também — `refinaria` dava corpo 3,69:1. Quando a régua condena o
que já está no ar e aprovado, **a régua está errada, não a peça**. Modelado o
véu em 2D e amostrado só nas colunas de texto, `cabecalho/servicos` devolve
4,82:1 — que bate com o que este arquivo registrava.

**Regra que fica: antes de reprovar uma escolha nova, meça a que já está
publicada. Se ela reprovar, o defeito é do método.**

### E um terceiro erro, de recorte

Recortei os fundos de seção na proporção de FAIXA (2,62). Mas `.secao--foto`
cobre a seção INTEIRA — a 1440 são 720 a 900 px de altura, proporção ~1,6.
Recortar a 2,62 joga fora justamente a altura de que o fundo precisa, e
`solar-estrutura` acabava **AMPLIADA 1,23x** — o erro que "Since 2000" custou.
A proporção passou a ser por ENTRADA: banda para faixa e cabeçalho, 1,6 para
fundo de seção.

### O resultado: as três substitutas são melhores nos dois eixos

| seção | antes | depois | amplitude | corpo |
|---|---|---|---|---|
| Our mission | `cabecalho/servicos` (repetia) | `faixa/ferramental` | 15,8 → **30,6** | 4,82 → 4,60 |
| Vendor profile | `faixa/refinaria` (repetia) | `faixa/solar-estrutura` | 20,1 → **35,4** | 3,87 → 4,60 |
| The ledger | `faixa/robotica` (repetia) | `faixa/engrenagem` | 34,8 → **46,2** | — → 4,83 |

Todas reduzem (0,56x / 0,75x / 0,56x) e todas passam AA. **Vendor profile
ganhou nos dois eixos**: `refinaria` estava em 3,87:1, ou seja abaixo de AA, e
ninguém tinha medido aquele slot.

E `solar-estrutura` diz o que a copy diz — *"controls work on solar generation
across the United States"* — em vez de uma refinaria genérica.

### PENDENTE que este trabalho descobriu

**A seção "Vendor profile" tem SEIS marcas douradas** contra o teto de duas da
regra crítica nº5: 1 eyebrow + 5 `.credencial__valor` (UEI, CAGE e os NAICS).
Os cinco códigos já eram dourados antes; o eyebrow que virei dourado em
20/08 é o sexto.

Não mexi: é interpretação de regra documentada, não defeito óbvio — cinco
códigos estilizados como conjunto podem ler como UMA marca, do mesmo jeito que
os quatro títulos dourados do rodapé. **Precisa de decisão do usuário.**

### Estado

**287 referências**, 0 quebradas, 0 órfãos. 0 repetições entre papéis.
0 classes mortas, 0 conflitos de cascata.

---

## 2026-08-20 (acervo) — As quatro fotos novas entraram na galeria, espalhadas

Pedido: pôr na galeria as fotos novas. São as quatro que vieram de
`referencia/` — duas já servindo de fundo das seções duplas, duas ainda sem uso.

O acervo passou de **29 para 33** fotografias.

### Elas entraram ESPALHADAS, e isso não é detalhe

Três das quatro são paisagem (1,50 / 1,50 / 1,59). Enfileiradas em bloco no fim
da lista, elas dariam ao mosaico um corredor de altura quase igual — que é
exatamente o defeito que a proporção nativa veio corrigir em 20/08 ("29
quadrados idênticos"). Cada uma entrou onde o ASSUNTO pede E onde a proporção
contrasta com a vizinha:

| # | nova | proporção | por quê ali |
|---|---|---|---|
| 10 | `robo-linha` | 1,59 | bloco automotivo, entre dois 1,00 |
| 12 | `painel-clp` | 1,50 | fecha o grupo de painel: manutenção → programação → interior → fiação |
| 15 | `mesa-comando` | 1,50 | **antes** de `sala-controle` (0,80), não depois |
| 24 | `solda-placa` | 1,33 | no meio da corrida mais longa de 1,50 do acervo |

**A posição 15 tem uma razão aritmética.** Depois de `sala-controle` ela cairia
num corredor de quatro 1,50 seguidos (comando, campo, braço, bornes). Antes
dela, a sequência alterna: 1,00 / 1,50 / 0,80 / 1,50.

Medida a maior corrida de proporção quase igual (tolerância .05): **5, a mesma
de antes**. Ou seja, as quatro entraram sem piorar o ritmo — que era o risco.

### O empilhamento MELHOROU com mais fotos

| colunas | chapas | desvio |
|---|---|---|
| 3 | 11 / 11 / 11 | **4,0%** (era 6,0% com 29) |
| 2 | 16 / 17 | 1,4% |

Mais peças dão ao empilhamento guloso mais chances de equilibrar — o desvio de
6,0% que este arquivo registrava era consequência de 29 ser pouco, não do
algoritmo.

### Duas saem da mesma fonte que as seções duplas, e isso é o padrão

`painel-clp` e `mesa-comando` vêm dos mesmos arquivos que `dupla/clp` e
`dupla/comando`, mas em proporção nativa e nas larguras da galeria (400/800).
Não é duplicação à toa: é o mesmo padrão que `refinaria` já segue, existindo em
`faixa/` e em `galeria/` com recortes diferentes.

### A contagem da página se atualizou sozinha

`.galeria__conta` sai de `len(itens)` — o lead agora diz "33 plates" sem
ninguém ter tocado no texto. É o motivo de ela ter sido escrita como dado e não
como frase fixa.

### RESSALVA REGISTRADA: `solda-placa`

A página afirma mostrar *"panels, control rooms, plant floors and the plants
themselves — the environments this company builds control systems for"*. Um
macro de placa com ferro de solda é **bancada de eletrônica**, não integração
de automação: a i3 monta painel, programa CLP e comissiona, não popula PCB.

Entrou porque foi pedida, com legenda que descreve a cena sem afirmar autoria
("Control board assembly, bench detail"). **É a candidata óbvia a sair** se
alguém quiser a galeria mais apertada ao que a página promete — foi também a
única das quatro que ficou de fora das seções duplas, pelo mesmo motivo.

### Estado

**268 referências** (eram 248; +20 das quatro fotos em três formatos e duas
larguras), 0 quebradas, 0 órfãos. 0 classes mortas, 0 órfãs, 0 conflitos.
`homa-appliances` deixou de ser a única fonte de `referencia/` sem uso: agora
as quatro estão no site.

---

## 2026-08-20 (dupla) — Uma foto para duas seções, e a medição errou antes da peça

Pedido, com captura: as duas seções escuras que fecham a home e services se
leem como um bloco só, mas carregavam **duas fotografias diferentes** — a de
cima terminava e outra começava no meio. Usar uma imagem só, e tirá-la das
fotos ainda não usadas em `referencia/`.

### A foto subiu para um invólucro

`.dupla` é um `<div>` que envolve as duas seções e carrega a fotografia e o
véu; as seções cedem o fundo (`background: transparent`). **É a única forma**,
porque duas fotos em dois elementos nunca casam quando a altura da seção de
cima muda de página para página — e ela muda: 373 px na home, 510 em services.

### A escolha da foto: medi luminância e ela NÃO decidiu

Comparei a cauda clara (p95) das quatro candidatas contra as fotos que o site
já usa em seção escura:

| | p95 |
|---|---|
| as que o site já usa | 160–197 |
| martinelle-desk | 176,7 |
| theaflowers | 217,2 |
| raymond-sime | 219,8 |
| homa-appliances | 232,9 |

Parecia decidir — mas a busca pelo véu mínimo devolveu **praticamente o mesmo
valor para as quatro** (.76–.78 claro, .88 escuro). O que manda não é a cauda
global, é a **pior média local 12×12**, e todas têm alguma mancha clara. A
escolha voltou a ser por assunto:

- **home → `dupla/clp`** (raymond-sime): painel aberto com CLPs, disjuntores e
  bornes. É literalmente o produto da i3, e "Senior control experts know things
  they do not teach in school" fala do conhecimento que mora ali dentro. A home
  não tem foto no cabeçalho — a peça de lá é o braço 3D — então não repete nada.
- **services → `dupla/comando`** (martinelle-desk): mesa de comando, mão no
  joystick. **NÃO um painel**: o cabeçalho daquela página já é close de relés e
  bornes, e duas fotos de painel na mesma página leem como a mesma foto duas
  vezes (armadilha já registrada aqui).

`theaflowers-soldering` ficou de fora: macro de PCB com ferro de solda é
bancada de eletrônica, não automação industrial, e a paleta roxo/verde briga
com navy+dourado.

### DOIS erros meus de medição, e o primeiro reprovou uma peça que estava certa

**1. Amostrei o pior ponto do conjunto INTEIRO.** A faixa livre é, de
propósito, a parte mais aberta do véu — então o pior ponto caía exatamente
onde não existe letra nenhuma, e a medição reprovava tudo com fundos de
`#9EA8AF`. **Medir contraste sobre fotografia exige recortar a região onde o
texto realmente vive.**

**2. O véu fechava tarde demais.** Abria até 50% e só voltava ao cheio em 58% —
mas o eyebrow do CTA nasce em **52%** na home, ou seja DENTRO da rampa de
fechamento, sob véu ainda aberto. Reprovava por 2,72:1. Passou a fechar em 48%.
**A rampa tem de terminar antes da primeira letra, não junto com ela.**

### A armadilha de comparar véus: `.secao--foto` não é .55

Achei que .62 seria mais fechado que o .55 de `.secao--foto` e ficou muito mais
aberto. Lá são **DOIS gradientes sobrepostos** — vertical .55 e horizontal .35 —
que compõem para `1-(1-.55)(1-.35)` = **.71** no ponto mais aberto. Aqui é um
gradiente só, então o valor declarado É o efetivo e precisa valer ~.78.

**Regra que fica: véu de várias camadas não se compara pelo número declarado.**

### Onde o véu abre

A fotografia só respira onde não há letra: a faixa entre o fim do texto de cima
e o começo do de baixo. Ela não é a mesma nas duas páginas, então o véu abre na
INTERSECÇÃO — home 27–52%, services 30–57% → **34–42%**, fechado em 48%.

Medido com o véu composto sobre as fotos de verdade, pior ponto das faixas de
texto:

| página | tema | pior fundo | branco | dourado | corpo | rótulo |
|---|---|---|---|---|---|---|
| home | claro | #384F68 | 8,45 | 5,29 | **4,59** | 5,42 |
| home | escuro | #1F4D78 | 7,46 | 5,51 | **4,57** | 5,63 |
| services | claro | #374B61 | 8,97 | 5,62 | 4,88 | 5,75 |
| services | escuro | #1E4B75 | 7,69 | 5,68 | 4,71 | 5,81 |

**O texto crítico é sempre o `.corpo`**, nunca o branco da citação — ele é
grande e responde a 3:1. E `--sobre-3-2` é `rgba`, então a cor que o olho vê é
ela JÁ composta sobre a superfície; aproximar por cinza chapado (o que fiz na
primeira volta) devolve um contraste que não existe na tela.

### Efeitos colaterais, os dois esperados

`.secao--foto-centro` ficou **sem consumidor** — a citação da home era o único —
e saiu (1673 bytes). A remoção foi provada por comparação do CSS sem
comentários antes e depois.

`cabecalho/contato` deixou de ser fundo do CTA nas duas páginas em que ele
tinha fundo, mas **não virou órfão**: continua sendo o cabeçalho de
contact.html.

### Ferramenta nova

`ferramentas/previa_dupla.py` — acha a faixa livre pela intersecção das
páginas, compõe o véu sobre as fotos de verdade, mede os quatro textos nos dois
temas amostrando SÓ as faixas de texto, e desenha as quatro combinações em PNG
com a emenda marcada em vermelho, para provar que a foto não se interrompe nela.

### Estado

**248 referências** (eram 234; +14 da pasta `dupla/`), 0 quebradas, 0 órfãos.
0 classes mortas, 0 órfãs, 0 conflitos de cascata.

---

## 2026-08-20 (azulado) — O CSS pedia dourado e a cascata entregava azul

Pedido: na seção "Talk to an engineer / Tell us what the process has to do",
que fecha todas as páginas, a tipografia tem de ser amarela — o hover estava
saindo azulado.

### O defeito era de ESPECIFICIDADE, não de intenção

`.contato__valor a:hover` pedia `--accent-txt` (dourado em seção escura) desde
que o bloco de contato nasceu. Nunca funcionou:

| seletor | especificidade | |
|---|---|---|
| `.contato__valor a:hover` | (0,2,1) | o que o componente pedia |
| `.secao--escura p a:hover` | **(0,2,2)** | o que a tela mostrava |

`.contato__valor` **é um `<p>`**, então a regra genérica casa o mesmo elemento
com um seletor mais específico. **Ordem no arquivo não resolvia** — a genérica
ganha por especificidade onde quer que esteja. O telefone e o e-mail acendiam
azul enquanto o código dizia dourado, e nada acusava.

**O conserto é as duas apontarem o MESMO token.** Assim a especificidade deixa
de importar: quem vencer, vence com a cor certa. É mais robusto que subir a
especificidade do componente, porque não depende de ninguém manter a corrida.

### Por que `conflitos.py` não pegou

A ferramenta que escrevi hoje cedo acha **o mesmo seletor declarado duas
vezes**. Este defeito é **dois seletores DIFERENTES casando o mesmo elemento** —
detectar isso exige resolver a cascata contra o DOM de verdade, não comparar
strings. Fica registrado como limite conhecido da ferramenta, não como falha
dela.

**Regra que fica: quando um componente e uma regra genérica disputam o mesmo
elemento, faça os dois apontarem o mesmo token em vez de brigar por
especificidade.** A briga tem vencedor silencioso; o token não.

### O eyebrow também estava azulado, e por descuido antigo

`.eyebrow` usa `--tinta-2`, que `.secao--escura` reaponta para `--navy-luz`.
Então o rótulo de capítulo saía azulado nas seções escuras enquanto
`.cabecalho .eyebrow` era dourado desde sempre — **mesma peça, mesmo papel,
duas cores**, só porque ninguém tinha reapontado. Agora
`.secao--escura .eyebrow` é `--dourado`.

**`.contato__rotulo` NÃO acompanhou, e a conta é o motivo:** são quatro rótulos
no mesmo bloco (Sales, Support, E-mail, Where we are). Levá-los junto poria
CINCO manchas douradas nesta dobra contra o teto de duas da regra crítica nº5.
E o papel deles é outro — etiqueta de campo num bloco de dados, não abertura de
capítulo.

Conferido nas nove páginas: **toda seção escura fica com exatamente 1 dourado
permanente**. Nenhuma delas tem faixa de números (`.secao--escura .numeros dt`
também é dourado, mas hoje não tem consumidor).

### Contraste, medido nas quatro superfícies em que o CTA aparece

O bloco aparece com foto em index e services, e chapado nas outras quatro:

| superfície | dourado |
|---|---|
| `--sup-3` tema claro (#001D3D) | 10,59:1 |
| `--sup-3` tema escuro (#003566) | 7,74:1 |
| foto velada, pior ponto claro (#394E65) | 5,37:1 |
| foto velada, pior ponto escuro (#1F4C75) | 5,60:1 |

Todas passam AA. O hover é transitório e sob o ponteiro, então não entra no
teto de dois por dobra (design.md §6.5) — o eyebrow entra, e é o único.

---

## 2026-08-20 (roda) — A inércia entrou, e ela reverte o que este arquivo dizia

Pedido: rolagem suave de verdade — "o usuário rola e o scroll não para no mesmo
momento". **Isto contradiz decisão registrada duas vezes aqui** ("nada sequestra
a roda", 19/08 e 20/08), então parei e confirmei antes de escrever, como manda
a regra crítica nº1. O usuário escolheu entre três vias, com os custos de cada
uma na mesa.

### O que já existia não era o que ele pediu

`scroll-behavior: smooth` está no `html` desde 19/08 — mas ele só afeta SALTO
DE ÂNCORA, não a roda. A queixa era legítima: não havia inércia nenhuma no
gesto da roda.

### A via escolhida foi a que preserva o que acabamos de entregar

| via | rolagem | `position: sticky` |
|---|---|---|
| **lerp sobre `scrollTo`** (escolhida) | a página rola de verdade | **vive** |
| `transform` num wrapper | a página não rola | **morre** |

**A segunda teria matado o rodapé revelado**, entregue duas horas antes e
inteiramente construído sobre `position: sticky`. Também mataria a barra
nativa, o "localizar na página" e o `scroll-padding` das âncoras. A escolha não
foi de gosto: foi de compatibilidade com o que já está no site.

### Quatro detalhes que decidem entre maciez e mingau

**1. `scroll-behavior` tem de ser DESLIGADO durante o laço.** O `html` o
declara `smooth`; sem desligar, cada `scrollTo` do laço seria ele mesmo animado
pelo navegador — **duas interpolações brigando**. Desligo por atributo de
estilo no início do gesto e restauro no fim, em vez de passar
`behavior: "instant"` na chamada: o atributo funciona em todo navegador que tem
`scroll-behavior`, e "instant" é valor recente.

**2. Trackpad fica de fora, e é o erro mais comum desta funcionalidade.** O SO
já aplica momentum nele; somar o nosso é o "duplo momentum" que faz a página
parecer atrasada. Roda de mouse manda ~100px por dente; trackpad manda muitos e
pequenos. Piso em **50px**: abaixo disso o evento passa sem `preventDefault`.

**3. A suavização é por TEMPO, não por quadro.** `k` fixo roda o dobro de
rápido em 120Hz. Com `dt` na conta, medido:

| refresh | 50% | 90% | 99% |
|---|---|---|---|
| 60 Hz | 100ms | 333ms | 667ms |
| 120 Hz | 100ms | 333ms | 667ms |
| 144 Hz | 104ms | 333ms | 660ms |

**4. Elemento rolável sob o ponteiro tem precedência.** O painel do menu ganhou
`overflow-y: auto` nesta mesma sessão; sem a checagem de ancestral rolável, a
roda sobre o menu aberto rolaria a página atrás dele.

### A sincronia por SINALIZADOR estava errada, e troquei por posição prevista

A primeira versão marcava `nosso = true` antes de cada `scrollTo` e o ouvinte de
`scroll` consumia a marca. **O navegador COALESCE eventos de rolagem** — manda
menos eventos do que chamadas — então a marca ficava presa e a próxima rolagem
externa de verdade era engolida.

Agora o laço guarda a posição que MANDOU o navegador assumir. Se a leitura do
quadro seguinte não bate com ela por mais de 4px, alguém mais mexeu — teclado,
barra, âncora — e o alvo se reancora ali. Funciona inclusive para teclado
pressionado NO MEIO do gesto, que o sinalizador não cobria.

### Beco bobo: um caractere cirílico

Escrevendo o comentário, a palavra "independente" saiu como `независимo` — 9
caracteres cirílicos dentro do `.js`. Passou no `node --check` (é comentário) e
só apareceu numa varredura por faixa de code point. Fica a nota de varrer
caracteres fora do Latin-1 depois de escrever bloco grande de comentário.

### Como ajustar

A força inteira mora em **`LERP = 0.11`** (main.js §11). Mais alto = mais seco,
mais baixo = mais longo. `PISO_RODA = 50` é a fronteira trackpad/roda.

### Estado

234 referências, 0 quebradas. 0 conflitos de cascata. `main.js` com 11 módulos.

---

## 2026-08-20 (retícula) — Tirar a grade consertou um contraste que estava reprovando

Pedido: tirar o efeito de grade da primeira imagem de Capabilities, Past
Performance, Services, Gallery e Contact, deixando só a fotografia.

É a `.reticula` — a grade quadriculada que o cabeçalho desenha **sobre** a
foto (`--reticula-z: 0`, acima do véu e abaixo do conteúdo). Ela estava fixa
na string de `cabecalho()`; virou parâmetro `reticula=True`.

**Fica ligada em who-we-are**, e o motivo é estrutural, não esquecimento:
aquele cabeçalho não tem fotografia (`cabecalho--liso`, decisão de 19/08 para
a marca 3D não disputar com três tramas). Lá a grade É o desenho do bloco —
sem ela sobra navy chapado.

### O achado: a grade estava derrubando o lead abaixo de AA

A retícula é branca a **.07 e .028** de alfa, ou seja **clareia** o fundo. Com
texto branco por cima, clarear o fundo PIORA o contraste. Medido sobre o pior
fundo do cabeçalho de capabilities (#414F62, o de véu mais aberto do site):

| | pior fundo | h1 | lead |
|---|---|---|---|
| com retícula | #4E5B6D | 6,91:1 | **4,43:1 — reprova** |
| sem retícula | #414F62 | 8,33:1 | **5,35:1** |

**A medição de 19/08 que aprovou aquele véu não modelava a retícula** — ela
compunha só véu sobre foto, e por isso deu 5,19:1 para o lead. O valor real,
com a grade por cima, era 4,43:1: abaixo do piso de 4,5 para texto pequeno.

Ou seja: o pedido era estético e **consertou um defeito de acessibilidade que
estava escondido havia um mês**. Nas outras quatro páginas o véu é o padrão
(mais fechado), então lá a grade não chegava a reprovar nada — mas o efeito
da conta é o mesmo, e todas ganharam contraste.

**Regra que fica: sobreposição decorativa entra na conta de contraste.** Véu e
retícula são duas camadas entre a foto e o texto; medir só uma delas dá um
número que não existe na tela. `sobreposicao.py` compõe o véu e ignora a
grade — se a grade voltar a algum bloco com texto, a ferramenta precisa
compor as duas.

### Nada quebrou ao remover a classe

`.reticula` declara `position: relative`, e havia o risco de o cabeçalho
depender disso para a foto absoluta. Não depende: `.cabecalho` tem `position:
relative` E `isolation: isolate` próprios — este último é justamente a
correção de 19/08 que fez a fotografia aparecer nas oito páginas. As cinco
mantêm `.cabecalho__foto`, conferido uma a uma.

Os tokens `--reticula-x/y` (34%/78%) continuam declarados em `.cabecalho` e
agora só servem who-we-are. Não são CSS morto: têm consumidor.

### Em aberto

**privacy-policy e terms-and-conditions continuam com a grade**, porque não
foram pedidas. As duas têm fotografia no cabeçalho (`quem-somos`), então ficam
como as únicas páginas com foto + grade. É inconsistência visível — perguntar
ao usuário se quer as duas junto.

---

## 2026-08-20 (folha) — O rodapé deixou de chegar e passou a ser descoberto

Pedido: a frase de fecho — "Industrial control systems, integrated and
commissioned.", que está nas nove páginas — sobe como página de livro, igual ao
Universo do CLP.

Fui ler o mecanismo de lá em vez de supor, e ele é **layout puro**: `main` com
fundo opaco e `z-index: 1`; `.rodape` com `position: sticky; bottom: 0;
z-index: 0`. O rodapé fica preso ao pé da janela desde a carga, escondido atrás
do conteúdo; quando o `<main>` acaba de subir, ele já está lá. Nenhuma
animação, nenhum JS no caminho da rolagem.

### Três coisas quebrariam se eu tivesse só copiado

**1. `body { overflow-x: hidden }` mata `position: sticky`.** `hidden` num eixo
faz o outro computar para `auto`, e com isso o `<body>` vira contêiner de
rolagem — o assassino clássico do sticky. Virou `overflow-x: clip`, que corta
sem criar contêiner, com `hidden` antes como reserva. **É a mesma lição que o
herói já tinha pago em 19/08**, e o P3 que a auditoria tinha registrado sem
urgência: ele deixou de ser desarrumação no dia em que algo passou a depender
dele.

**2. O rodapé preso já está DENTRO da janela desde a carga.** O
IntersectionObserver não enxerga oclusão, só geometria — então o §4 dispararia
a frase de fecho no primeiro quadro, atrás do `<main>`, e o visitante chegaria
ao fim do site com a animação já gasta. Quem responde "o rodapé está visível?"
não é o rodapé: é o FIM do `<main>`. Entrou um marcador
(`[data-fim-conteudo]`) na última linha do conteúdo, e o §10 observa ele.

**3. Foco de teclado invisível.** Pela mesma razão, focar um link do rodapé não
provoca rolagem — para o navegador ele já está na tela — e o anel de foco
ficaria atrás do conteúdo. O primeiro `focusin` no rodapé leva a página até o
fim. Copiado do módulo 12 do UnidoCLP, que existe exatamente por isso.

### A guarda de tamanho saiu de medição, não de cautela

**Um sticky mais alto que a janela não revela nada.** Ele é puxado para cima
até o pé encostar no pé da tela, e o topo — que é onde a frase mora — fica fora
da tela o tempo todo. Medida a altura real do rodapé:

| largura | colunas | altura |
|---|---|---|
| ≥ 900 | 4 numa linha | **732 px** |
| 600–768 | 2 linhas | 1053 px |
| ≤ 414 | 1 coluna, 4 linhas | 1694 px |

Guarda: `min-width: 900px and min-height: 780px`. Fora dela o rodapé é estático
e a frase entra rolando, como antes — degrada para o que já existia.

**Fica pendente uma decisão de 28 px:** a 1366x768 o rodapé CABE (732 < 768),
mas a guarda desliga. Preferi errar para o lado seguro porque 732 é conta, não
medição de navegador. **Quando o Chrome conectar, medir a altura real e, se
confirmar, baixar a guarda para 760** — 1366x768 é resolução comum demais para
ficar de fora por 12 px de margem.

### O defeito que a paleta escondia: a folha subia e nada mudava

Sete das nove páginas terminam numa seção `--sup-3` (navy) e o rodapé é
`--sup-3-fundo` — um navy só um degrau mais fundo. Medido:

| tema | última seção | rodapé | contraste |
|---|---|---|---|
| claro | #001D3D | #000814 | **1,19:1** |
| escuro | #003566 | #000509 | **1,66:1** |

**A revelação teria sido invisível na maioria do site.** O UnidoCLP não tem esse
problema porque lá o `main` é branco e o rodapé preto.

O remédio é a **aresta da folha**: 1px no fim do `<main>`. E é BORDA e não
sombra porque o design.md decide isso duas vezes — "nunca sombra de caixa" e
"a elevação do sistema vem de fundo e borda". O site inteiro é feito de filete;
a aresta é mais um.

**O alfa saiu da conta, e .3 reprovava.** O vizinho mais claro é a última seção
no tema escuro (#003566):

| alfa | contra #003566 | |
|---|---|---|
| .35 | 1,83:1 | reprova |
| .45 | 2,70:1 | reprova |
| **.55** | **3,75:1** | passa, e é o mínimo que passa |

Ficou `.55` — quase o dobro de `--filete-forte` (.3), e a diferença é a mesma
que este projeto já faz entre filete e borda de componente: **filete é divisória
decorativa e o WCAG 1.4.11 o isenta; esta aresta carrega o efeito**, então
responde ao piso de 3:1. Contra o rodapé ela dá 6,26:1 e 6,23:1.

### Ferramenta nova

`ferramentas/previa_rodape.py` — mede se o rodapé cabe em sete janelas, mede a
aresta nos dois temas contra os dois vizinhos, e desenha três instantes da
subida em PNG (`_rodape.png`), que é o que mostra se o efeito lê.

### Estado

234 referências, 0 quebradas. 0 conflitos de cascata. `main.js` passou a listar
os dez módulos no cabeçalho (listava sete) e o "8" duplicado da lente virou
"6b".

---

## 2026-08-20 (ledger) — A peça que a limpeza tinha acabado de apagar

Pedido: fotografia de fundo em "The ledger", o resumo que fecha
past-performance (eyebrow + "Twenty-six years, counted" + a faixa de números).

**Ironia que vale registrar: `.secao--foto-corpo` era exatamente este
componente, e eu o removi duas entregas atrás** na varredura de CSS morto —
legitimamente, porque a foto de "Since 2000" tinha saído a pedido e ele ficou
sem consumidor. Restaurá-lo custou pouco porque este arquivo guardava a receita
inteira: o véu como token, a faixa de 62%, os contrastes medidos. **É a
primeira vez que o memoria.md paga por si mesmo de forma direta.**

### O que NÃO podia ser copiado de volta como estava

A versão antiga fechava o gradiente em `var(--sup-1)`, porque a seção que ela
cobria era `.secao` (branca). **"The ledger" é `.secao--offwhite`** — colar a
regra velha deixaria uma emenda visível onde o gradiente acaba em branco e o
fundo continua em off-white.

Duas coisas passaram a seguir a superfície, por motivos diferentes:

| token | o que é | por que segue a superfície |
|---|---|---|
| `--veu-corpo` | a cor TRANSLÚCIDA sobre a foto | travada em branco, lavava a foto no tema escuro (bug já registrado em 19/08) |
| `--veu-fim` | a cor SÓLIDA em que o gradiente fecha | tem de ser a superfície da própria seção, senão sobra emenda |

### A escolha da foto foi por repetição, não por assunto

`faixa/refinaria` já serve **três** páginas (who-we-are, capabilities,
services); `faixa/robotica`, só a home. Ficou robotica — e ela ainda calha de
ser o polo "body shop" que a copy desta seção nomeia ("what changes between a
refinery and a body shop"). past-performance não usava nenhuma das duas.

**Proporção conferida ANTES de escolher**, que é a regra que "Since 2000"
custou: 1920x734 numa caixa de 1440x392 é **reduzida 0,750x**. Cobrir a seção
inteira (~632 px a 1440) obrigaria a ampliar — por isso a foto ocupa a FAIXA de
62%, e a banda dos números termina em superfície limpa.

### Dois erros meus na ferramenta de medição, e o segundo é sutil

`previa_ledger.py` reprovou TUDO na primeira volta — pior fundo `#0F151C`,
título a 1,49:1. A peça não estava errada; a medição estava.

**1. O primeiro stop dos dois gradientes é opaco.** No CSS ele é
`var(--sup-N)`, uma cor sólida — **alfa 1,0, não 0**. O gradiente começa
FECHADO (foto invisível) e abre para o véu; eu tinha codificado o inverso,
então a medição olhava a foto praticamente nua.

**2. Em `background: A, B` o A é o de CIMA.** O vertical vem primeiro no CSS,
então ele pinta SOBRE o horizontal. Eu aplicava na ordem contrária.

Corrigidos, com o véu real (.78 no miolo, .56 nas laterais):

| tema | pior fundo | título | corpo | eyebrow | dd |
|---|---|---|---|---|---|
| claro | #DBDEE1 | 9,14:1 | 12,89:1 | **4,86:1** | 5,11:1 |
| escuro | #13273B | 12,92:1 | 12,92:1 | 7,90:1 | 7,64:1 |

Todos passam AA. **O eyebrow é o mais apertado nos dois, como sempre neste
site** — é ele que define o teto de abertura do véu, não o corpo.

**Regra que fica: ferramenta que compõe gradiente do CSS tem de respeitar o
alfa do PRIMEIRO stop e a ordem das camadas. Errar qualquer um dos dois
produz reprovação convincente de uma peça que está certa** — e o risco real é
"consertar" o véu fechando-o até apagar a foto.

### O empilhamento já estava resolvido, e não por acaso

`.secao__foto` é `z-index: -2` e o véu `-1`. Filho de z negativo só pinta acima
do fundo do pai se o pai for contexto de empilhamento — a armadilha que custou
oito cabeçalhos em 19/08. `.secao--foto-corpo` já nasce com `isolation:
isolate`, herdado daquela correção.

E a junta cai bem: no topo da seção o gradiente vertical ainda está SÓLIDO
(alfa 1,0 em 0%), então a linha de eixo de `SHEET 03 OF 04` fica sobre
superfície limpa, sem disputar contraste com a fotografia.

### Ferramenta nova

`ferramentas/previa_ledger.py` — confere a proporção da fonte contra a caixa,
compõe os dois gradientes sobre a foto de verdade, mede os quatro textos nos
dois temas e desenha a seção em PNG (`_ledger.png`) para a composição poder ser
julgada, não só os números.

### Estado

234 referências, 0 quebradas, 0 órfãos. 0 classes mortas, 0 órfãs, 0 conflitos
de cascata.

---

## 2026-08-20 (cascata) — A galeria tinha DUAS definições, e a velha dizia "quadrado"

Pedido: "faça as alterações necessárias". Fui fazer a consolidação de
breakpoints que eu mesmo tinha listado como P3 — e **a medição derrubou o
próprio achado**. O que apareceu no lugar era pior e de verdade.

### Os 11 breakpoints NÃO são desarrumação: são derivados de conteúdo

Catalogados um a um, cada `@media` de largura com o que ele toca. A conclusão
inverte o que eu tinha escrito:

| ponto | quem usa | derivado de |
|---|---|---|
| 860 | `.oferta`, `.capacidade` | a tabela tem `min-width: 720` — cabe até 784, empilha a 860 com 76 px de folga |
| 720 | `.escada` | o degrau para de caber |
| 700 | `.galeria__mosaico` 2→1, `.planta` | largura mínima de coluna |
| 620 | `.diagrama` 2→1, `.obra__trilho` | idem |
| 560 | `.prancha__linha` 2→1 | idem |
| 900/901 | herói | par casado (900+1), que é a forma correta de escrever faixas exclusivas |

**Arredondar 620 para 640, ou 700 para 720, moveria o ponto em que o
componente colapsa** — quebraria no lugar errado para ganhar uma tabela
bonita. Os pares que parecem duplicados (640/620, 720/700) pertencem a
componentes diferentes, com larguras mínimas diferentes. Ficam.

**Regra que fica: breakpoint que sai de uma conta de conteúdo não se
consolida.** E um achado de auditoria que não sobrevive à própria medição deve
ser retirado, não executado por obrigação.

### O defeito real: mesmo seletor, duas vezes, e a velha esperando a vez

Varrendo por "mesmo seletor + mesmo contexto + mesma propriedade" apareceram
**três**: `.galeria__item`, `.galeria__item img` e `.galeria__legenda`, cada uma
declarada duas vezes. A cópia velha era a §16 GALERIA — a grade quadrada, de
antes do mosaico por colunas.

Hoje ela não fazia mal nenhum: a boa vem depois no arquivo, mesma
especificidade, e vence por ordem de cascata. **Mas a velha carrega
`aspect-ratio: 1`.** Qualquer reordenação do arquivo, ou um `@media` novo
envolvendo o bloco, poria as 29 fotos do mosaico de volta em quadrado —
desfazendo em silêncio as 8 proporções nativas que a entrega de 20/08 mediu.

Quando removi `.galeria` (a classe nua) na limpeza anterior, **removi o
telhado e deixei as paredes**: a varredura de classe morta não pegou
`.galeria__item` porque a classe ESTÁ em uso — só não por aquela regra. Duas
varreduras diferentes, dois defeitos diferentes.

### Ferramenta nova: `ferramentas/conflitos.py`

Acusa a regra que vence em silêncio. É a classe de defeito que este arquivo
registra mais vezes — `.setores` colidindo entre duas páginas, `.botao:hover`
vencendo o repouso escrito depois, `.nav__painel a` batendo `.botao`. Todas do
mesmo formato, todas invisíveis, e nenhuma aparece em lista de código morto.
Agora sai de varredura. **Está em 0.**

### Dois cabeçalhos que mentiam

`11. PLATAFORMAS — barra, não carrossel de logos` estava logo acima de
`11. PLATAFORMAS — desenhadas como LÓGICA LADDER`: sobra de quando o ladder
substituiu a barra, com o número repetido. E `22.4 (vago)` era uma subseção
numerada e vazia, tombstone do painel preso. As seções voltaram a ser
contíguas (1–22, subseções 21.1–21.5), com as três referências cruzadas
internas atualizadas junto (`§22.1`→`§21.1`, `§23`→`§22` no CSS, `§22.5`→`§21.4`
em mosaico.js).

**A renumeração foi provada segura por construção:** o script comparou o CSS
com os comentários REMOVIDOS, antes e depois, e confirmou que a única
diferença são as três regras mortas. Tudo o mais mudou só dentro de comentário.

### Estado

style.css 143,5 → **142,9 KB**. 0 classes mortas, 0 órfãs, **0 conflitos de
cascata**, 234 referências, 0 quebradas. Comentários balanceados, `node --check`
limpo nos dois JS tocados.

---

## 2026-08-20 (limpeza) — A lista de "CSS morto" fechou, e ela escondia um cabo solto

Segunda passada de polish, no que a auditoria tecnica nao cobre: codigo morto,
cobertura de estados e consistencia. **A lista de CSS morto que este arquivo
vinha mantendo desde 19/08 foi zerada.**

### O que saiu, e como foi decidido

Varredura de classe declarada contra classe usada nas 9 paginas e nos 7 JS
(`/tmp` — a ferramenta e descartavel, o resultado nao). Oito classes sem
nenhum consumidor, **5,0 KB**:

| classe | por que morreu |
|---|---|
| `.cards` `.card` `.card__num` | a matriz de services foi o ultimo consumidor |
| `.galeria` (nua) | a grade quadrada antes do mosaico por colunas |
| `.secao--foto-corpo` | a foto de "Since 2000" saiu a pedido do usuario |
| `.dados__foto` `.dados__linha--foto` | **nao estavam na lista** — a miniatura por programa entregue |
| `.botao--claro` | ja era morto quando o dourado unificou os botoes |

Os dois de `.dados__` sao o achado: a lista deste arquivo estava
**incompleta**, e ninguem tinha notado porque ela era mantida a mao. Agora sai
de varredura.

**`.botao--claro` tinha uma nota no codigo pedindo para ficar** ("se um dia
alguem o usar, ele acende igual"). Removido mesmo assim, e o motivo e que a
regra que garante isso e a lista de `.botao:hover` — quem reintroduzir a classe
tem de entrar la de qualquer forma. Guardar a declaracao nao garantia nada.

### O cabo solto que so apareceu porque eu procurava o contrario

Varrendo o sentido inverso — classe USADA no HTML que nao tem regra nenhuma —
apareceu **`.rodape__icone`**, presente em 6 paginas e sem uma linha de CSS.

Nao era defeito visivel: o icone era estilizado pelo PAI, por
`.rodape__marca svg`. Mas dos cinco call sites de `icone_marca()` — `nav__icone`,
`intro__marca`, `marca3d__plano`, `heroi__icone`, `rodape__icone` — **era o
unico assim**. A classe emitida no HTML nao valia nada.

Passou a mirar a classe, como os quatro irmaos. Mesma especificidade nos fills
(0,2,0), e agora o estilo acompanha a peca se ela sair de dentro de
`.rodape__marca`. **Regra que fica: varrer nos DOIS sentidos. Classe sem uso
desperdica bytes; uso sem classe e um contrato que ninguem esta cumprindo, e
esse nao aparece em nenhuma lista de codigo morto.**

### Beco: contar `{` e `}` nao valida CSS

Ao cortar `.secao--foto-corpo` ancorei o inicio no MEIO do comentario longo — o
`*/` saiu junto com as regras e o cabecalho `/* --- fotografia sob secao de
CORPO` ficou orfao, engolindo a abertura do comentario da JUNTA logo abaixo.

**A checagem de chaves passou**, porque `{` e `}` dentro de comentario contam
igual. O que pegou foi contar `/*` contra `*/` — e mesmo essa acusou falso
(209 contra 208), porque um comentario legitimamente continha `/*` no corpo. So
a **varredura sequencial** (acha `/*`, acha o `*/` dele, pula) diz a verdade.

Nenhuma regra chegou a ser engolida: o `*/` da JUNTA fechava o comentario orfao
logo antes de `.junta { }`. Mas era churn, e churn e o que o polish remove.

### O que NAO mexi

A medida do corpo (62ch) e a do bloco centrado (48ch) ficam como estao. O piso
de qualidade do skill pede 65–75ch, mas as duas sao decisao registrada aqui e a
tipografia e intocavel por regra critica no2. Brief vence piso generico.

### Estado

**215 classes declaradas, 202 usadas no HTML, 0 orfas nos dois sentidos.**
style.css de 149,6 KB para **143,5 KB**. 234 referencias, 0 quebradas, 0 orfaos.

---

## 2026-08-20 (polish) — Quatro defeitos, e três só existiam no celular

Avaliação geral do site, PC e celular, seguida do polish. Nota **15/20**. O
detector do skill roda DEGRADADO neste ambiente (faltam `htmlparser2`,
`css-select`, `css-tree`, `domutils`) — o que ele não acusa é subcontagem, não
atestado limpo, e a integridade foi lida à mão.

### O CTA do menu mobile era inalcançável, e a conta prova

`.nav__painel` é `position: fixed` sem `max-height` e sem `overflow`. Somando:
7 links de 58 px + botão de 48 com 32 de margem + 96 de padding = **582 px de
conteúdo** abaixo de uma nav de 64.

| aparelho | altura útil | transborda |
|---|---|---|
| iPhone SE (568) | 504 | **78 px** |
| celular em paisagem (~375) | 311 | **271 px** |

E o que transborda é o fim da lista — ou seja, **o botão "Talk to an engineer",
o CTA primário**. Não havia gesto que o alcançasse: sem `max-height` o painel
só crescia para fora da tela.

`max-height: calc(100svh - var(--nav-altura))` + `overflow-y: auto`. **`svh` e
não `vh`**: no celular a barra do navegador entra e sai, e `vh` mede a janela
GRANDE — o painel voltaria a passar da tela exatamente quando a barra está
visível. O herói já usa `100svh`, então é a unidade que o projeto fala.

### A hierarquia de espaçamento sumia abaixo de 768

`--sec-y` descia com a janela e `--gap-bloco` ficava fixo em 64:

| janela | entre seções | dentro da seção | razão |
|---|---|---|---|
| ≥1024 | 160 | 64 | 2,5× |
| 768–1023 | 96 | 64 | 1,5× |
| ≤767 | **64** | **64** | **1,0×** |

No celular o vão entre duas seções INTEIRAS ficava idêntico ao vão entre um
título e o componente dele. É a hierarquia que este arquivo registrou em 19/08
— *"64 dentro da seção contra 160 entre seções mantém o ritmo certo: grupo
junto, assunto separado"* — desfeita justamente onde a tela é menor e a
hierarquia importa mais. `--gap-bloco` passou a descer junto (s-7 / s-6 / s-5)
e a razão fica em 2,5× / 2,0× / 2,0×.

**A prancha não foi afetada:** ela usa `--s-6` literal, não `--gap-bloco` — a
exceção deliberada de 48 px continua de pé.

### Layout thrashing no motor de rolagem, e o `continue` não poupava nada

`medir()` (main.js §7) lia `getBoundingClientRect()` e escrevia `--p` **no mesmo
laço**. A escrita suja o estilo; a leitura do elemento seguinte força o
navegador a recalcular estilo e layout ali mesmo, de forma síncrona. Na galeria
são **30 alvos** — 30 layouts forçados por quadro de rolagem, na página mais
pesada do site e no aparelho mais fraco.

Separado em duas passagens: lê os 30 retângulos, depois escreve os 30 valores.
Um layout por quadro em vez de trinta.

**E o descarte do que está fora da tela era ilusório.** O `continue` vinha
DEPOIS do `getBoundingClientRect()` — o retângulo já tinha sido lido para
decidir. Ele não economizava a leitura, que é a parte cara; só a aritmética.
Agora mora na segunda passagem, onde é honesto.

### Nível de título é da PÁGINA, não do componente

Três saltos de heading, violando WCAG 1.3.1: capabilities ia de `h1` para `h3`,
services e who-we-are de `h2` para `h4`.

O diagrama era `h4` e sempre mora sob o `h2` da seção — virou `h3`, e resolve as
duas páginas.

A lista de capacidades é mais interessante: na home ela vive dentro de uma seção
que já tem `h2`, então `h3` está certo; em capabilities ela é o conteúdo direto
da página, sem `h2` nenhum acima, e o mesmo `h3` faz o documento pular de h1
para h3. **Mesmo componente, nível diferente, porque o que muda é a árvore em
volta** — `lista_capacidades(nivel=...)`. As nove páginas passaram a fechar sem
salto.

### O que NÃO foi mexido, e por quê

**Onze breakpoints ad-hoc** (1439/1200/1100/1023/900/860/720/700/640/620/560),
e o 767 dos tokens sem contrapartida no `style.css`. É desarrumação real, mas
consolidar breakpoints sem navegador é o tipo exato de mudança que quebra em
silêncio — e não há defeito visível atrás dela. Fica registrado.

**58 `<img>` sem `width`/`height`.** O grep acusa CLS; **a leitura desmente**:
os slots são dimensionados por `aspect-ratio` no CSS (prancha 1/1, obra 1/1,
galeria `var(--ar)`, dados 4/3) e as fotos de fundo são `position: absolute`.
Só importaria se o CSS falhasse. Não é o bug que parecia.

### O que já estava certo

Vale registrar, porque foi verificado e não precisa ser reauditado: os três
WebGL pausam fora da tela por `IntersectionObserver`; alvos de toque todos
≥44 px (hambúrguer 44, tema 44, `.cta` 44, `.botao` 48); a tabela de services
empilha com `min-width: 0` abaixo de 860; todas as grades colapsam até uma
coluna; `:focus-visible` global com `--foco` virando por superfície; a `.marca3d`
some abaixo de 1023, então o `touch-action: none` dela nunca prende o dedo de
ninguém; 58/58 imagens com `alt`.

E um falso positivo que quase virou correção: o h1 do herói parecia estourar a
tela a 320 px, porque `h1` nu é `--fs-display` (piso 44 px). Mas
`.heroi__titulo` tem clamp própria de piso **36 px** e `.cabecalho h1` de 40 —
"instrumentation." mede ~250 px numa coluna de 280. Não estoura. **Medir antes
de corrigir também evita conserto de defeito que não existe.**

---

## 2026-08-20 (junta) — A emenda entre seções virou uma REGRA, não uma classe

Pedido: o Universo do CLP tem animações diferentes conforme você navega página
por página; trazer isso para as seções que fazem sentido. Escolhido pelo
usuário, entre três gestos do UnidoCLP: a **linha de corte**.

### O que NÃO veio do UnidoCLP, e por quê

Os três gestos de seção de lá são a rede que se varre e pulsa, o sino de
rolagem do `.filme` (abre entrando, segura, fecha saindo) e a `.esteira` de
foco central. **Portar a esteira teria reintroduzido exatamente o que a
entrega de ontem removeu** — o carrossel saiu porque "não falava a língua do
site", e um trilho de foco central é o mesmo vocabulário de apresentação de
produto. O que atravessou foi a IDEIA (variedade por página), traduzida para a
língua que este site já fala: filete, cota, datum, bloco de título.

### A variedade não é escolhida — é lida da página

O site se lê como conjunto encadernado de desenho técnico, e faltava a marca
que um conjunto usa para dizer que o desenho CONTINUA: quando a planta não cabe
numa folha, ela é cortada por uma **linha de eixo** e cada folha recebe a
referência da seguinte. A regra ficou literal:

| na borda | leitura | o que aparece |
|---|---|---|
| a superfície MUDA | é outra folha | linha de eixo + `SHEET 04 OF 07` |
| a superfície é a MESMA | é a mesma folha | só o tique de 120 px |
| `.faixa` full-bleed | chapa inserida, não folha | nada |

**Duas seções navy seguidas não ganham linha, e isso é o ponto.** O piso de
qualidade proíbe "uma entrada idêntica em toda seção"; aqui a diferença não é
tempero, é informação — a junta diz QUE tipo de troca aconteceu. Contadas nas
nove páginas: **32 bordas, 28 de corte** (3 delas invertidas, acompanhando o
barramento de who-we-are) **e 4 internas**.

### Quem escreve a classe é o gerador, e isso mata uma armadilha registrada

`juntar()` (em `build_paginas.py`) varre os `<section>` do corpo, deduz a
superfície de cada um e escreve a classe. **Escrever à mão em 30 seções seria
pedir para uma ficar para trás — que é a razão de este gerador existir.**

E some de vez a pegadinha que este arquivo registrou em 20/08: `.secao--emenda`
sozinha nunca acendia, porque quem escreve `is-visivel` é o observador do
main.js §4, **que observa `.reveal` e mais nada**. Faltando o par
`reveal reveal--limpo` a emenda ficava travada em `scaleX(0)`, invisível para
sempre, e nada acusava. Agora o marcador entra junto com a junta, sempre.

### O defeito de contagem que a primeira versão tinha

`folhas` começou como `len(seções)`, e os rótulos pulavam número: `02 OF 05` e
logo depois `04 OF 05`, porque a seção sem corte gastava um índice que nunca
aparecia na tela. **Folha é a CORRIDA de superfície, não a seção** — duas
seções navy seguidas são uma folha só. Corrigido, a numeração fecha contígua em
todas as nove páginas.

### LINHA TRACEJADA NÃO SE ANIMA POR ESCALA

É a lição cara desta entrega, e ela é o motivo de a peça ter trocado de
técnica. A emenda velha era uma régua SÓLIDA, então `scaleX(0→1)` servia. Uma
linha de eixo é um PADRÃO periódico, e a escala encolhe o padrão junto:

| instante | traço por `clip-path` | traço por `scaleX` | o que está na tela |
|---|---|---|---|
| p = .08 | 26,0 px | **2,1 px** | linha PONTILHADA |
| p = .18 | 26,0 px | **4,7 px** | linha tracejada fina |
| p = .60 | 26,0 px | 15,6 px | quase lá |
| p = 1,00 | 26,0 px | 26,0 px | traço-ponto |

Três convenções de desenho diferentes dentro de UMA animação. `clip-path`
revela o padrão no tamanho verdadeiro desde o primeiro quadro — que é o que
"ser desenhada" quer dizer.

### A receita da linha foi medida, e a primeira reprovou

Nasceu 22-5-2-5 (período 34). Renderizada a 1x, **o ponto de 2 px entre vãos de
5 não se separava do vão** e a linha lia como tracejado comum — que é outra
convenção. Passou a **26-8-3-8, período 45**: com vão de 8 px o ponto vira
marca e a linha volta a ser traço-ponto.

### O rótulo sai de graça na ordem certa

Ele mora na ponta em que o traço TERMINA, então o mesmo `clip-path` que desenha
a linha o plota depois — linha de construção primeiro, anotação por último, que
é a ordem de um desenho e não dois efeitos disparados juntos. Rima com o fecho
do rodapé, onde a régua entra depois da última palavra. Por isso
`.junta--inversa` troca o lado do rótulo junto com o sentido: no who-we-are,
onde o barramento vira para a direita, a folha é cortada desse lado.

A borda do container é resolvida sem marcação, por
`max(--pad-lateral, 50% - --container/2 + --pad-lateral)`. Conferido em cinco
janelas — 1920, 1440, 1280, 1000 e 600 — bate com a borda real do `.container`
em todas (320, 80, 48, 32, 20 px).

### Contraste e a conta de dourado

O rótulo é `--tinta-2`, que já vira sozinho por superfície. Medidas as seis
combinações (2 temas × 3 níveis), pior par **#8FB4DC sobre #003566 = 5,72:1** —
todas passam AA. A linha é `--filete-forte`, divisória que o WCAG 1.4.11 isenta.

**Nenhum dourado na junta, e não é economia:** ela cai exatamente na dobra entre
duas seções, e a regra crítica nº5 admite duas manchas por dobra. Uma junta
dourada estouraria a conta de toda seção que já usa as duas.

### Por que a `.faixa` ficou de fora

O `::after` dela já é o degradê da fotografia — e é fato técnico, não gosto:
`::before` é o véu de `.secao--foto` e `::after` é o único pseudo livre nas
demais. Mas ela também não precisa: já tem entrada própria, a foto revelada de
baixo para cima por `clip-path`. Uma banda full-bleed não é folha do conjunto,
é a chapa inserida entre duas.

### Ferramenta nova

`ferramentas/previa_junta.py` — desenha a junta fora do navegador em cinco
janelas, confere o alinhamento do rótulo contra a borda do container e põe as
duas técnicas lado a lado no meio do traçado. **Ela LÊ a geometria do próprio
`style.css`** por regex sobre o `repeating-linear-gradient`: guardar cópia dos
números aqui repetiria o erro já pago na prévia do braço, onde a cópia divergiu
em meia hora e a prévia passou a confirmar uma peça que não existia mais.

### Beco de ferramenta: um byte de controle dentro da regex

`juntar()` não casava um único `<section>` e nada acusava — a varredura passava,
as páginas construíam, e as juntas simplesmente não saíam. O padrão tinha sido
escrito por heredoc e o `\b` chegou ao arquivo como **0x08 (backspace)
literal**, dentro de uma string `r'...'`. No `grep` o byte é invisível, então a
linha parecia certa. Só `repr(_SEC.pattern)` mostrou `'<section\x08(...)'`.
**Regra que fica: regex que não casa nada e não ergue erro merece um
`repr(pattern)` antes de qualquer outra hipótese.**

### PENDENTE

**Ver no navegador continua pendente** — a extensão do Chrome segue
desconectada, agora há várias sessões. Tudo aqui foi medido fora dele:
alinhamento e geometria por aritmética e render em PNG (`previa_junta.py`),
contraste pela fórmula WCAG, estrutura pela varredura (**234 referências, 0
quebradas, 0 órfãos**) e a distribuição das juntas conferida seção a seção nas
nove páginas. O que só o navegador responde: a linha de eixo correndo a 60
quadros e se o rótulo em 12 px lê confortável a 1x numa tela de verdade.

**Vídeo de services continua parado.** Os três `.mp4` de `melhorias/services`
somam 180 MB e não há ffmpeg neste ambiente.

---


## 2026-08-20 (colisão) — "Industries served" quebrou por causa de um NOME

Seis itens do usuário: a prancha da home (fotos chegando tarde e a "escada" que
não combinou), o realce dourado na linha errada, a seção de setores quebrada,
past-performance inteira, fotografia nas duas seções escuras de services, e
movimento na galeria. Três deles tinham a mesma causa de fundo — um componente
afirmando uma coisa e entregando outra.

### O defeito mais caro da entrega tinha 1500 linhas de distância da causa

`Industries served` renderizava como um vão navy de quase cinco telas com os
cinco cards empilhados um sobre o outro. O HTML da home estava certo, as
imagens carregavam, a varredura de referências passava com 0 quebradas.

**O painel preso de past-performance usava `.setores` e `.setor` — que já eram
da GRADE DE SETORES DA HOME** (CSS §12). Escrito depois no arquivo, com a mesma
especificidade, ele vencia por ordem de cascata e caía na home junto:

| o que a home herdava | valor |
|---|---|
| `min-height` | `calc(6 * 82vh)` = **492vh** |
| `background` | `--sup-3` (navy) |
| `.setor` | `grid-area: 1 / 1` — os cinco na mesma célula |
| `opacity` | 0, menos o primeiro |

**Regra que fica: componente novo nasce com nome PRÓPRIO.** Reaproveitar o nome
de um componente que já existe em outra página não é economia — é acoplar duas
páginas por cascata, e quem paga é a página que ninguém estava olhando. O
sintoma é só visual e não aparece perto da causa.

O carrossel foi removido inteiro (era para ser refeito de qualquer forma) e o
substituto nasceu como `.obra`. `js/setores.js` foi apagado junto: sem a
marcação, ele não tinha como voltar.

---

### A prancha chegava tarde por DUAS causas, e corrigir uma só não resolveria

Relato: *"as fotos estão demorando para carregar, então só aparecem as 4 quando
você arrasta para quase depois delas."* As duas causas se somavam:

**1. O tempo, e ele era aritmética.** A prancha é mais BAIXA que a janela,
então o módulo 7 do main.js mede a travessia inteira — `--p` NÃO é "quanto dela
está visível", é onde ela está no percurso. Com a janela antiga (duração .25,
passo .72) a quarta folha só fechava em `--p` **.89**:

| `--p` | onde a fileira está (1440x900) |
|---|---|
| .331 | acabou de caber inteira na tela |
| .500 | está no meio da janela |
| **.89** | **o topo já está 275 px ACIMA da dobra** |

A animação estava certa e chegava tarde demais para ser vista. Agora a última
folha fecha em **.385** — logo depois de a fileira caber inteira e antes de ela
chegar ao meio da tela. Conferido em quatro janelas por
`ferramentas/previa_registro.py`:

| janela | fileira inteira a partir de | folha 04 fecha em |
|---|---|---|
| 1440x900 | .331 | .385 |
| 1368x768 | .366 | .385 |
| 1920x1080 | .292 | .385 |
| 1100x800 | .320 | .385 |

As janelas continuam se sobrepondo (passo .055 contra duração .16): sem
sobreposição a fila entra em quatro tempos e lê como quatro animações.

**2. A rede.** `loading="lazy"` só dispara o download quando o navegador julga
a imagem perto da janela, e aí ainda há decodificação pela frente. As quatro
folhas passaram a `fetchpriority="high"` sem lazy. `imagem()` ganhou
`ansioso=True` para isso. **Lazy continua o padrão e continua certo para as 29
fotos da galeria** — o ansioso é para fotografia que é prova logo abaixo da
primeira dobra, e são quatro arquivos de ~600 px.

### A escada saiu, e o que a substitui é a cadeia de cota

*"esse estilo escada que sobe e desce não combinou com o site"* — e ele tem
razão pelo motivo estrutural: o deslocamento alternado nasceu como ritmo de
folha montada à mão, e nada mais no site é colagem. Tudo aqui é desenho
técnico, e **desenho técnico ALINHA**.

O ritmo passou para uma **linha de referência contínua no topo**, com um tique
sobre a borda esquerda de cada folha e o número da vista ao lado. A régua de
cota já fechava o bloco embaixo; agora ela abre e fecha, e a fileira fica presa
entre as duas em vez de flutuar.

**Duas ordens importam e não são enfeite.** A linha se desenha PRIMEIRO
(`--datum` fecha em `--p` .06, exatamente onde a primeira folha começa): é a
ordem de um desenho, linha de construção antes das vistas. E o tique usa
`align-items: flex-start`, não `center` — centrado num trilho de 32 px ele
boiava 11 px abaixo da linha, e **tique que não toca a linha que mede não mede
nada**.

### A conta de dourado da prancha estava estourada desde que ela nasceu

Eram **quatro** marcas de registro douradas na mesma dobra, contra o teto de
duas da regra crítica nº5. Ninguém tinha somado.

As marcas passaram a `--filete-forte` — que é o que uma marca de registro é,
estrutura de folha — e sobrou **um** acento, na ORIGEM da linha de referência.
Não é economia forçada: em desenho técnico a origem de uma cadeia de cota é
mesmo marcada diferente dos tiques intermediários. A dobra fecha em dois: o
realce do rótulo da seção e esta origem.

---

### O realce mudou de linha, e a colocação nova é a certa

Pedido: o bloco dourado estava sobre a tese (*"We build the control system"*) e
era para marcar *"What we actually do"*.

**É a colocação certa, e não só porque foi pedida.** O realce é um MARCADOR —
aponta onde o capítulo começa, como a faixa da headline aponta a tese da
empresa na dobra de cima. Sobre a lead ele competia com o h1 do herói: duas
frases longas em campo dourado na mesma rolagem leem como duas manchetes. Sobre
o rótulo da seção ele vira o que sempre foi, uma aba de capítulo.

O par de cor não muda e não pediu medição nova (navy `#003566` sobre campo
`--dourado`, 7,74:1, opaco), e a contagem de dourado da dobra CAI de dois para
um — a lead volta a ser texto.

---

### Past performance: o carrossel não falava a língua do site

Duas queixas, e as duas procedem:

**"não combina com o site."** O resto das nove páginas se lê como documentação
técnica — filete, cota, rótulo em mono, bloco de dados. Um carrossel preso de
tela cheia é vocabulário de apresentação de produto, e era a única peça do site
falando essa língua.

**"as seções não se conectam suavemente."** Uma seção de **492vh** entre o
cabeçalho e o resumo abre um vão em que nada se encadeia: o visitante rola meia
dezena de telas dentro de UM bloco, e os dois vizinhos ficam longe demais para
lerem como a mesma página.

O substituto é o **registro de obras**: seis fichas em série, cada uma o BLOCO
DE TÍTULO de uma folha de desenho — trilho no topo com índice e setor, e
embaixo a placa fotográfica ao lado da tese e dos dados. Dentro de uma seção de
altura normal, a página volta a ter um fluxo só.

**A alternância do lado da placa não é zigue-zague decorativo:** é a convenção
de um conjunto encadernado, em que o bloco de título fica na margem EXTERNA da
folha. Dá ritmo a uma pilha de seis sem que nenhuma ficha mude de estrutura —
o oposto exato da escada reprovada na home, onde o deslocamento quebrava o
alinhamento sem carregar informação. **Abaixo de 1023 px ela some:** numa
coluna só, alternar não pagina nada, só muda a ordem de leitura de ficha para
ficha.

**A placa continua placa, e a razão continua sendo resolução.** Medido: a 1440
e a 1920 ela fica em 420 px, então a fonte de 600 é REDUZIDA 0,70x e a de 900,
0,47x. Sangrada numa moldura de 1440 seria ampliada 2,4x — o erro que a seção
"Since 2000" custou.

**Três coisas que a página ganhou para se conectar:** um bloco de abertura de
duas colunas (era a única página do site que não abria uma seção assim, e sem
ele as seis fichas começavam do nada); a emenda animada nas duas seções
seguintes, alternando o lado de onde a régua varre; e o resumo passou a
off-white, para a página alternar superfície em vez de ir navy → navy.

**Armadilha: `.secao--emenda` sozinha nunca acende.** A régua da borda de cima
só é desenhada com `is-visivel`, e quem escreve essa classe é o observador do
main.js §4 — **que observa `.reveal` e mais nada**. Sem o marcador
`reveal reveal--limpo` a emenda fica travada em `scaleX(0)`, invisível para
sempre, e nada acusa. who-we-are já usava o par; past-performance nasceu sem.

**Alinhamento óptico do título com a placa, e a conta é da fonte.**
`align-items: start` alinha as CAIXAS, e a caixa de um h2 é maior que a letra:
Outfit tem ascendente 1,00em e descendente 0,26em (área de 1,26em) contra
entrelinha 1,05, então o meio-espaçamento é -0,105em e a base cai 0,895em
abaixo do topo da caixa. Com a maiúscula em 0,70em acima da base, o topo dela
fica **0,195em abaixo da borda da caixa** — a 44 px, quase 9 px de degrau
contra o filete da placa. `margin-top: -.19em` devolve. É a mesma classe de
problema que a faixa do realce resolveu: **a caixa da fonte não é a letra.**

---

### Galeria: faltava VARIAÇÃO, não animação

Pedido: *"uma biblioteca de imagens precisa de mais movimento."* A primeira
medição explicou por que a página parecia parada, e não era o que eu esperava:

**`build_imagens.galeria()` recortava as 29 fotos em `1.0`.** O "mosaico por
proporções" era, na prática, uma grade de **29 quadrados idênticos**. O
comentário do CSS descrevia proporções de 0,56 a 1,50 — descrevia as FONTES,
não o que estava sendo publicado. Nenhuma quantidade de animação conserta isso:
uma grade uniforme continua uniforme se mexer.

Corrigido na origem: a galeria sai na proporção NATIVA, aparada em
**0,66..1,60**. Os limites cortam só o excesso (20 das 29 passam sem tocar em
nada) — `fiacao` é 0,563 e viraria uma tira de 764 px numa coluna de 430, e
`linha-solar`/`prensas` passam de 1,77 e virariam faixas de 241 px em que o
assunto some. Agora são **8 proporções distintas**.

**Efeito colateral que quase passou batido:** quatro fotos mudaram de faixa de
largura (750 → 400/800) e os arquivos de 750, gerados no recorte quadrado
velho, **continuaram no disco**. A varredura passava (o arquivo existia), a
página referenciava o quadrado antigo, e `--ar` vinha medido dele: 1.0. Tudo
consistente, tudo errado. **Arquivo que sobra é mais perigoso que arquivo que
falta, porque nada acusa.** `_proporcao()` passou a medir exatamente as
larguras que a página declara e a quebrar o build quando falta uma.

**Colunas de verdade, não `columns`.** A propriedade do CSS montava isto
sozinha e foi trocada por três elementos por um motivo só: **coluna que é
elemento pode ter deriva própria na rolagem**, e é a deriva que dá profundidade
a um acervo. Com `columns` não há o que animar — é uma caixa só. O preço é
`js/mosaico.js`, que reempilha quando o número de colunas muda; o empilhamento
inicial vem pronto do gerador, então sem JavaScript a página já está certa.

**O empilhamento é guloso pela coluna mais curta, dos dois lados.** Round-robin
(`i % n`) seria uma linha e está errado — com proporções de 0,66 a 1,60 as
colunas terminariam com centenas de pixels de diferença. Medido:

| colunas | chapas | desvio máximo |
|---|---|---|
| 3 | 10 / 9 / 10 | 270 px (**6,0%**) |
| 2 | 15 / 14 | 56 px (0,9%) |

**A deriva não escalona a origem, e essa restrição não é conservadorismo.**
Escalonar o topo das colunas — a solução óbvia, e a que quase toda galeria usa
— seria repetir a escada que o usuário acabou de reprovar na home. As três
nascem no prumo em `--p` 0 e a separação nasce e cresce com a rolagem. `--amp`
é -44 e -88 px ao longo da travessia INTEIRA: na coluna mais alta (~4485 px)
isso é **1,96%** da altura dela. Deriva rápida em galeria vira enjoo, e é ela
que faz o visitante perder a foto que estava olhando.

**A ordem do acervo tinha uma consequência visual que eu não tinha previsto.**
As 9 fotografias autorais do cliente são todas 600x600 e lideram a lista — é a
escolha editorial certa, são o material mais valioso. Mas enfileiradas em bloco
elas dão ao empilhamento nove peças de altura IDÊNTICA, e **as duas primeiras
fileiras do mosaico voltavam a ser uma grade**, exatamente o defeito que a
proporção nativa veio corrigir. `clarificador` (0,80) e `celula` (1,50) foram
trazidas para as posições 3 e 6: a terceira coluna se desloca já na primeira
fileira. As duas são aberturas fortes por conta própria, então a curadoria não
perde nada.

**A goteira vertical vive no `gap` da coluna, não numa margem da figura** — é
o que mantém a conta de empilhamento honesta: a altura de uma chapa é
exatamente foto + legenda + gap, sem margem escondida. A estimativa (.18 de uma
largura de coluna) dá 78 px a 432, contra 76 reais.

---

### Services: fotografia nas duas seções escuras que fecham a página

A pedido, no mesmo par que a home já usa. `faixa/refinaria` (2560, **reduzida
0,56x** na faixa de 1440) em "Your design or ours", e `cabecalho/contato` no
bloco de contato — que carrega a mesma foto em toda página em que ele tem
fundo, de propósito: é o mesmo bloco, e trocar a foto por página o faria
parecer outro componente a cada vez.

`faixa/refinaria` não repete o cabeçalho da própria página, que já usa
`cabecalho/servicos` (relés e bornes) — duas fotos de painel na mesma página
liam como a mesma foto duas vezes. Medido com `sobreposicao.py` nos dois temas:

| tema | pior fundo | branco | eyebrow | corpo |
|---|---|---|---|---|
| claro (.55/.35) | #394E65 | 8,57:1 | 5,49:1 | 5,33:1 |
| escuro (.68/.50) | #1F4C75 | 8,94:1 | 5,73:1 | 5,57:1 |

Todos passam AA com folga — refinaria rende melhor que `contato`, que já era a
referência do véu.

---

### Ferramentas novas

`ferramentas/previa_registro.py` (a conta do tempo da prancha, do encaixe da
ficha de obra e do equilíbrio das colunas), `previa_obra.py` e
`previa_galeria.py` (as duas composições em PNG). `previa_prancha.py` foi
atualizada para a fileira alinhada e o realce no rótulo.

### CSS morto, atualizado

Saiu da lista: `.setores`/`.setor` do painel preso (removidas de verdade).
Entrou: **`.galeria`** — a grade quadrada antiga, sem nenhum usuário desde que
o mosaico virou colunas. Continuam na lista `.cards`/`.card`, `.botao--claro` e
`.secao--foto-corpo`.

### PENDENTE

**Ver no navegador continua pendente** — a extensão do Chrome segue
desconectada. Tudo nesta entrega foi medido fora dele: geometria e tempo por
aritmética (`previa_registro.py`), composição por render em PNG
(`previa_obra.py`, `previa_galeria.py`, `previa_prancha.py`), contraste pela
fórmula WCAG sobre as fotos de verdade (`sobreposicao.py`), e estrutura pela
varredura (**234 referências, 0 quebradas, 0 órfãos**). O que só o navegador
responde: os shaders compilando, e a deriva das colunas da galeria correndo a
60 quadros num acervo de 29 imagens.

**Vídeo de services continua parado.** Os três `.mp4` de `melhorias/services`
somam 180 MB e não há ffmpeg neste ambiente.

---

## 2026-08-20 (rolagem) — Sete itens, e o que a medição mudou em três deles

Lista do usuário: refazer a prancha da home com entrada ligada à rolagem e pôr
o realce dourado em "What we actually do"; dominó no hover das capacidades, nas
duas páginas; refazer past-performance com rolagem interativa; refazer services
como apresentação de produto; galeria com o acervo inteiro; e arrumar o
"Elsewhere" do contato.

### O motor: `--p`, e a rolagem continua sendo do navegador

Três componentes passaram a reagir à POSIÇÃO da rolagem em vez de dispararem
uma vez ao entrar na tela. O módulo 7 do `main.js` publica `--p` (0..1) em
`[data-progresso]` e o CSS faz o resto.

**Nada sequestra a roda.** O ouvinte é `passive: true`, ninguém chama
`preventDefault`, e a leitura é adiada para o quadro seguinte com
`requestAnimationFrame` — ler layout dentro do evento de rolagem é o que causa
engasgo. É a decisão que este arquivo já registrava, e ela pesa mais agora: com
`scroll-behavior: smooth` no site inteiro, um `preventDefault` na roda quebraria
junto todo link para âncora.

Duas leituras, escolhidas pela altura do próprio elemento: **alto** (maior que
a janela, o caso do painel `sticky`) usa `altura - janela` como curso;
**baixo** (a prancha, cada figura da galeria) usa a travessia inteira.

**Por que não `animation-timeline: view()`:** faria isto sem uma linha de JS e é
o caminho certo no dia em que estiver em todo lugar. Hoje não está no Safari, e
o efeito sumiria inteiro para metade dos visitantes de iPhone.

### O dominó não podia esmaecer o texto, e a conta é dura

O sinal óbvio para a onda era esmaecer os itens distantes. Reprova:

| opacidade | claro (#5A5A5A / #F2F5F8) | escuro (#A8BACB / #001427) |
|---|---|---|
| 1,00 | 6,30:1 | 9,34:1 |
| 0,86 | 4,54:1 — **piso** | 7,16:1 |
| 0,62 | **2,74:1 REPROVA** | **4,26:1 REPROVA** |

Resolvendo pelo mínimo AA, o piso legível é **0,86** — uma esmaecida que
ninguém enxerga. **A faixa útil entre "ilegível" e "invisível" não existe
aqui.** A onda passou a ser carregada por MOVIMENTO e pela tinta do NÚMERO, que
vai de `--tinta-2` a `--accent-txt`: medido em todo o percurso da mistura,
mínimo **6,00:1** no claro e 9,67:1 no escuro.

**E o dourado não entra na onda.** A régua da borda é `--dourado`; propagá-la
pelos vizinhos poria até sete manchas douradas na mesma dobra, e a regra crítica
nº5 admite duas. A régua continua só no item apontado.

**A onda move só `transform` e `color`** — nenhuma propriedade de layout. É a
lição já paga: a versão com `:has()` encolhia as irmãs, o alvo fugia de baixo do
ponteiro e a lista piscava em laço.

### Past performance: placa montada, não foto sangrada

A referência do usuário mostra o texto do setor sobre uma fotografia cheia de
detalhe. Fui montar assim e a medição barrou: **a fotografia autoral do cliente
é toda 600x600** (teto do acervo, já registrado aqui). Sangrada numa moldura de
1440 px ela seria AMPLIADA 2,4x — o mesmo erro que quebrou a seção "Since 2000".
E **não existe foto de água em alta resolução no acervo**, então metade dos
setores ficaria em banco de imagem só para poder sangrar.

Montada numa placa de 440 px ela é REDUZIDA, que é a única forma de ficar
nítida. O ganho de composição veio junto: **o texto nunca cai sobre a
fotografia**, e some o problema que o próprio esboço da referência mostra.

Conferido com `ferramentas/previa_setores.py` em quatro janelas — 1440x900,
1368x768, 1920x1080 e 1100x800 — o conteúdo cabe no painel preso em todas, com
folga mínima de **35 px** (o laptop de 768, que já era o caso apertado do herói).

**Dois eixos, um índice.** A rolagem publica uma BASE e as setas movem um
DESLOCAMENTO; o setor visível é a soma em aritmética modular. Se os dois
escrevessem o mesmo número eles brigariam — rolar desfaria a seta. E o "volta
para o início quando acabam as fotos" sai de graça do módulo. Cuidado que
custaria uma sessão: **em JavaScript o resto de negativo é NEGATIVO** (-1 % 6 dá
-1), então é `((x % n) + n) % n`.

**O ponto do carrossel reprovou e foi resolvido pela conta.** A 30% de branco
dava 2,64:1 no claro e 2,24:1 no escuro — abaixo do piso de 3:1 do WCAG 1.4.11
para controle que carrega informação. Ficou **0,44** (4,18:1 e 3,24:1). O pior
caso é o tema ESCURO, e é contraintuitivo pelo mesmo motivo do véu: lá o bloco
de ênfase é mais CLARO, então branco translúcido rende menos.

### Services: matriz, não três cards numerados

Eram três `.card` com 01/02/03 — o contêiner preguiçoso, e com números que não
marcavam nada: as três formas de contratar são PARALELAS, não uma sequência.

Virou **matriz comparativa**, que é o formato para "simples de entender e mesmo
assim com bastante informação": o comprador lê UMA LINHA para comparar as três
ofertas no mesmo critério, ou UMA COLUNA para entender uma oferta inteira. Card
não permite nem uma coisa nem outra — obriga a ler os três textos por inteiro e
guardar a comparação de cabeça.

**É um `<table>` de verdade.** Dados tabulares em `div` perdem a relação
célula/cabeçalho e um leitor de tela lê doze parágrafos soltos. Abaixo de 860 px
ela EMPILHA em vez de rolar de lado: com quatro critérios, a rolagem horizontal
esconderia duas colunas inteiras e o comprador não saberia que existem.

O `diagrama()` de quatro passos entrou nesta página — **ali os números são uma
sequência de verdade**, cada passo é entrada do seguinte.

### Galeria: a página parou de afirmar o que não podia sustentar

O acervo inteiro entrou, por decisão do usuário. Mas a página **afirmava** no
próprio texto: *"Every photograph here is from a job we did… we would rather
show you nothing than show you a stock one."* Só 12 das 29 são autorais. A
afirmação saiu — uma página que afirma autoria e mostra outra coisa é pior que
uma que não afirma nada.

**Ficaram de fora, e o motivo importa:** `image.png` e `3d.png` são captura da
ilustração de marketing de OUTRA empresa ("24/7 Clean Energy as a Service"), e
`bet.png` / `fotologo.png` são identidade do Universo do CLP. Conteúdo de marca
de terceiro não entra num site institucional.

**Mosaico por colunas, não grade de cards.** As proporções vão de 0,56 (retrato)
a 1,50 (paisagem); forçar tudo num card 4:3 recortaria o assunto de metade delas.

### CSS morto que esta entrega criou

`.cards` e `.card` não são mais usados por nenhuma das nove páginas — a matriz
de services era o último consumidor. Entram na lista com `.botao--claro` e
`.secao--foto-corpo`.

### Beco de ferramenta: `data:` URI contado como referência quebrada

O ícone da lista de canais é um SVG embutido em `mask-image`. `varredura.py`
testava o prefixo `data:` DEPOIS de juntar com o diretório do CSS — e
`os.path.join('css', 'data:image/...')` já começa com `css/`, então o teste
passava batido e um ícone inline virava referência quebrada. Filtro movido para
antes do join.

---

## 2026-08-19 (ajuste) — O token de espessura da marca não existia

Pedido: engrossar as linhas da marca 3D e tirar a fotografia do cabeçalho de
who-we-are, mantendo a grade.

### A marca lia um token que não valia nada no escopo dela

`marca.js` pedia `--braco-linha-fina/-grossa`. Esses dois são declarados em
**`.heroi`**, que não é ancestral de `.marca3d` — a leitura vinha vazia e a peça
caía no padrão escrito no código (0,9/1,8) sem que nada indicasse isso. O token
existia no arquivo e não valia nada ali.

Pior que o valor errado é o valor certo por acidente: se um dia a marca fosse
parar dentro do herói, ela passaria a herdar a espessura do braço em silêncio.
Agora tem `--marca-linha-fina/-grossa` próprios.

### O limite da espessura é o GLIFO, não a moldura

Renderizados quatro pares lado a lado (0,9/1,8 · 1,2/2,4 · 1,5/3,0 · 1,8/3,6):

O "3" tem ~48 px de largura na moldura real e a haste dele ~12 px, então o
contorno come o vazio interno pelos dois lados. **A partir de 1,8 os contornos
do "3" se encontram e o glifo vira mancha.** Moldura e base aguentariam muito
mais — quem manda é a menor forma da peça.

Ficou **1,4 / 2,8**. O glifo desenha a 2,59 px (peso .85) e os vazios continuam
abertos.

**E a folga de enquadramento foi remedida com a espessura contada**, porque a
expansão em quad põe `meia + 0,8` px para fora da caixa geométrica: 2,2 px a
2,8 de largura. Varridos os mesmos 170 quadros, **folga real de 5,1 px** —
contra os 6,8 px geométricos que AR .96 garante. Não corta.

Efeito colateral bom: com `fina` em 0,9 e dpr 1, `meia` dava 0,45 — menor que a
meia-rampa de antisserrilhado de 0,5, então **até o centro da linha saía
atenuado** em tela comum. Em 1,4 a linha tem miolo sólido.

### A fotografia saiu do cabeçalho, a retícula ficou

Três tramas no mesmo bloco — fotografia, retícula e peça em arame — e a peça,
que é a mais fina das três, é quem some. `cabecalho()` ganhou `img_base=None`
e a classe `.cabecalho--liso`.

**O véu saiu junto, e removê-lo não muda um pixel:** `rgba(0, 29, 61, a)` sobre
`--navy-fundo`, que É `rgb(0, 29, 61)`, devolve a mesma cor em qualquer alfa.
Ele já era um no-op ali; sair só poupa uma camada de pintura de tela cheia.

A máscara da retícula ficou onde estava (34% / 78%): apoia o texto e deixa o
lado direito em navy limpo, que é onde a marca vive.

`cabecalho/fotovoltaico` foi apagado do disco e saiu de `CABECALHOS` — 5
arquivos, e a varredura caiu de 127 para 122 referências, 0 órfãos. **A receita
do recorte ficou comentada no build_imagens.py** caso a foto volte.

---

## 2026-08-19 (marca 3D) — A geometria não está no arquivo que a desenha

O último item do PENDENTE foi feito: a marca i3 extrudada, à direita do
cabeçalho de who-we-are. `site/js/marca.js`, 215 segmentos, WebGL2 à mão.

### O `d` do caminho NÃO foi copiado para o JS

Era o caminho óbvio e é o errado. O docstring de `icone_marca()` já avisava:
*"três cópias do mesmo caminho e uma fica para trás"*. Copiar os `d` para
`marca.js` seria a terceira cópia, e no dia em que o logo mudasse o site teria
**duas marcas diferentes na mesma página** — a plana no nav e a extrudada no
cabeçalho.

Então `marca.js` **lê a geometria do DOM**: o `<svg>` que o componente já emite
para servir de reserva é a fonte. O achatamento das curvas é do navegador
(`getPointAtLength`), então não há parser de bezier no site. E a reserva sai de
graça — sem WebGL2 o visitante fica com o logo plano, que já estava carregado.

**Consequência de ordem, e ela é silenciosa:** `getPointAtLength` precisa do
elemento RENDERIZADO. `is-gl` (que esconde o SVG) só entra **depois** da
leitura. Invertido, o retorno seria comprimento zero, desenho vazio e nenhum
erro no console.

### O núcleo foi EXTRAÍDO, e a prévia do braço provou que deu certo

A decisão em aberto era duplicar a matemática ou extrair para `site/js/gl.js`.
Extraído: matriz, `enquadrarCaixas`, o parser hexadecimal, `compilar`/`programa`
e o fBm da lente em GLSL. `braco.js` consome por **alias local** no topo, então
nenhum call site de geometria, cinemática ou desenho mudou.

`enquadrar()` continua em `braco.js` como envoltório de 5 argumentos, porque
`ferramentas/previa_braco.js` chama com essa assinatura — e a prévia rodando é
a prova de que a extração não mexeu no braço: **1421 segmentos e distância
24,8**, os mesmos valores de antes.

`pagina()` injeta `gl.js` sozinho na frente de quem consome `I3GL`. Depender de
quem escreve a tupla lembrar da ordem é como o núcleo some numa madrugada, e o
sintoma seria a peça não aparecer, sem erro na página.

### `AR` maior que 1 AUMENTA a peça — eu inverti o sinal e a varredura pegou

Escrevi `AR = 1.06` com o comentário de que dava mais folga que o `0.98` do
braço. É o contrário. A conta de enquadramento usa `tan(FOV/2) * AR` como
meio-campo, mas a **projeção usa `tan(FOV/2)` puro** — então AR > 1 diz à câmera
que ela tem mais campo do que tem, e a peça transborda. Medido: **a base saía
11 px fora da moldura.**

| AR | folga mínima |
|---|---|
| 1,00 | 0,0 px — encosta, e em alguns ângulos corta |
| **0,96** | **6,8 px** |
| 0,92 | 13,6 px |
| 0,88 | 20,4 px |

Ficou 0,96 e não 0,98 como o braço porque **aqui não há folga de graça**: a
caixa envolvente de um prisma reto É a peça, enquanto no braço o canto da caixa
cai fora da silhueta arredondada e devolve margem sozinho.

### A marca não gira solta, e essa é a diferença de comportamento

O braço é uma máquina: girar 360° mostra mais máquina. A marca é uma marca — de
perfil ela vira uma tira vertical e para de comunicar. Medida a ocupação mínima
de largura ao longo do arco: **±0,75 rad → 72% · ±0,95 → 60% · ±1,20 → 42%**.

Ficou **±0,80 no repouso** (nunca abaixo de ~75%) e ±0,95 no arrasto. E a
deriva de repouso **vai e volta**: de sentido único ela encostaria no limite e
ficaria parada lá — exatamente o que a deriva existe para evitar.

Conferido: **170 quadros** (17 ângulos × 5 inclinações × 2 arcos), folga mínima
6,8 px. Nunca corta.

### Pesos por medição, não por gosto

O glifo nasceu em 0,70 e a aresta de fundo dele dava **2,72:1** — abaixo do
piso de 3:1 do WCAG 1.4.11 para elemento gráfico que carrega informação, e o
"i3" carrega, é a marca. Subiu para 0,85 (**3,18:1**). Moldura e base em 1,00
dão 7,60:1 na frente e 3,19:1 no fundo, iguais ao braço. As **nervuras** ficam
em 2,3–2,4:1 de propósito: descrevem profundidade, que é sombreado.

### Contagem de dourado do cabeçalho: exatamente 2

O eyebrow (`.cabecalho .eyebrow` é `--dourado`) e a tela da marca. A lente do
ponteiro não conta — transitória e sob o ponteiro, mesma isenção do §6.5. **Está
no teto da regra crítica nº5, sem folga:** qualquer dourado novo neste bloco
estoura.

### O corte por classe é o contrato

`PAPEL` casa pela CLASSE que `icone_marca()` escreve (`moldura`/`tela`/`glifo`).
Peça sem classe conhecida é ignorada — melhor faltar um detalhe do que extrudar
algo na profundidade errada. E a cópia de contorno da intro
(`.marca__contorno`) é pulada, senão metade da peça sairia duplicada no mesmo
lugar.

### Ferramentas novas

`ferramentas/previa_marca.js` + `.py` e `ferramentas/previa_cabecalho.py`.

A fronteira da prévia da marca é o que importa nela: **o que é estubado é a
PLATAFORMA** (o DOM mínimo e `getPointAtLength`), nunca a lógica do site.
`construir()`, `amostrar()`, `prisma()`, `PAPEL`, `FOV`/`MIRA`/`AR` e o
enquadramento de `gl.js` rodam de verdade, do arquivo de produção. E os
caminhos saem de `site/who-we-are.html` — do que `icone_marca()` realmente
emitiu, não de uma cópia.

`previa_cabecalho.py` refaz a aritmética do CSS e desenha a peça real por cima.
Foi ela que mostrou que a 23vw sobravam **78 px mortos** entre o fim do h1 (que
trava sozinho em `max-width: 18ch`) e a coluna da marca. A 26vw a peça vai a
374 px e a coluna de texto cai de 871 para 858 — 13 px, que não mudam a quebra
do título. **O respiro saiu do vão morto, não do texto.**

**Beco pago pela própria prévia:** guardei a classe do elemento como `cls` e
`marca.js` lê por `getAttribute("class")` — `construir()` devolveu vazio. Um
apelido de atributo no stub é indistinguível de geometria que não existe.

---

## 2026-08-19 (dourado) — Um gesto tinha quatro cores

Pedido do usuário: *"faça todos os botões terem a mesma tipografia, alguns
brilham em azul outros em amarelo, todos precisam brilhar em amarelo."*

### A tipografia já era a mesma — menos num lugar

`.nav__cta`, `.cta` e `.botao` sempre foram `--fs-ui`/500 sem tracking. Mas
`.nav__painel a` é **(0,2,0)** e `.botao` é **(0,1,0)**, e o botão do menu
mobile É um `<a>` — então ele herdava os **18px** dos links do painel enquanto
todo outro botão ficava nos 16px. Um só controle fora da escala, e só abaixo de
1100px, que é onde ninguém olha.

Os três valores viraram **uma declaração só**. Não muda nenhum número: junta os
que já eram iguais para que continuem iguais. `letter-spacing: normal` entrou
explícito — os vizinhos têm tracking (`.eyebrow` .01em, `.mono` .02em) e sem a
declaração bastaria alguém pôr tracking num ancestral.

### O conflito com o design.md era real, e foi confirmado antes

O §6.3 dizia **"Nunca um botão com fundo `--dourado`"**. Regra crítica nº1 do
`CLAUDE.md` manda parar e avisar — perguntei com as três opções medidas, e o
usuário escolheu **preenchimento dourado**.

Havia quatro acenderes para o mesmo gesto: `.nav__cta` branco sobre o herói e
navy depois de rolar; `.cta` navy em seção clara e dourado em escura; `.botao`
navy sempre. O visitante via o mesmo controle acender de três cores descendo a
home.

**Só o preenchimento consegue ser o mesmo amarelo em todo lugar**, e a razão é
estrutural: quando o campo vira dourado, a superfície de baixo deixa de
importar. Borda e tinta dependem dela.

| via | tema claro | escuro | serve? |
|---|---|---|---|
| dourado como **borda** | 1,60:1 sobre branco · 1,46:1 sobre off-white | 12,35:1 | **não** — reprova o piso de 3:1 e some no claro |
| dourado como **tinta** | 1,60:1 | 12,35:1 | **não** — regra crítica nº4 |
| `--accent-txt` como tinta | 7,57:1 sobre branco · **2,23:1 sobre navy** | 12,35:1 | **não** — muda por superfície, que é o defeito a corrigir |
| **preenchimento + tinta navy** | **7,74:1** | **7,74:1** | **sim** |

E 7,74:1 não é um par qualquer: campo dourado com glifo navy **é o logo do
cliente**, o mesmo par do realce da headline do herói.

O §6.3 foi reescrito separando **repouso** (que não mudou: navy ou borda fina) de
**hover** (transitório, um de cada vez, sob o ponteiro — a mesma isenção que o
§6.5 já concede à lente).

### O rótulo do CTA é a única peça não preenchida

Por isso é a única que precisa de token por superfície. `.secao--escura` já
virava `--accent-txt` para dourado; **`.heroi`, `.cabecalho`, `.faixa` e
`.rodape` só declaravam `--foco`** e o rótulo dentro delas teria caído em
2,23:1. As quatro passaram a virar o token junto.

**Armadilha de ordem:** as regras antigas de `.botao:hover` vinham **depois** do
bloco novo, com a mesma especificidade, e venciam em silêncio. Removidas de lá e
o repouso ficou com um comentário dizendo por que o hover não mora ali.

---

## 2026-08-19 (cabeçalho) — Trocar a foto de UMA página, não de duas

O cabeçalho de who-we-are passou a usar
`tylijura-technology-10404349_1920.jpg` — operário de capacete olhando uma
linha de produção de módulos fotovoltaicos. Solar é setor declarado da empresa,
então a foto fala do assunto da página.

**Ela entrou com nome novo (`cabecalho/fotovoltaico`) e não substituiu
`quem-somos`**, porque `quem-somos` também serve `privacy-policy` — trocar a
fonte daquele nome teria mudado a foto de duas páginas de uma vez.

**Proporção conferida ANTES de escolher**, que é a regra que a seção "Since
2000" custou: 1920x1076 recortado para 1920/620 não precisa de ampliação
nenhuma (folga vertical de 456 px), e na caixa real de 1440x620 ainda é
**reduzida 0,75x**. A âncora padrão .42 corta em y 192..812 — mantém o capacete
inteiro e deixa a gola, que é a região mais calma da imagem, exatamente sob o
bloco de texto.

Testei .00/.15/.22/.42 e as quatro preservam o capacete; ficou a padrão, então
`recortar_cobrir()` não precisou de parâmetro novo.

**O véu continua o PADRÃO (.72 → .92), não o aberto de `.cabecalho--foto`.** A
fonte tem resolução para o aberto, mas o véu aberto clareia justamente o lado
DIREITO (`.70 → .26` a 72%), que é onde a marca 3D passou a morar — a peça em
arame ficaria sobre a parte mais agitada da fotografia.

**E a foto de "Since 2000" saiu**, a pedido. `faixa/robotica` continua em uso
pela home, então não virou órfão. A classe `.secao--foto-corpo` ficou sem
nenhum usuário — ver o PENDENTE.

---

## 2026-08-19 (realce) — A tese não é escrita em dourado, é MARCADA em dourado

Da referência em `melhorias/Home.png`: "Good control strategy" deixa de ser
texto branco e vira um **bloco dourado cheio com o texto em navy**.

Amostrado na referência: dourado `[252 196 0]` = `--dourado`; tinta dentro do
bloco `[0 53 102]` = **`#003566`**, que é `--traco`; fundo `[0 29 61]`. Ou seja,
o par do REALCE é exatamente o par do LOGO — glifo navy dentro do campo dourado
da tela. Medido: **7,74:1**. A headline passou a repetir a marca.

**Por que invertido e não dourado como tinta.** Dourado sobre o navy do herói dá
10,59:1 e funcionaria. Mas lê como link, e a frase perderia peso ao competir com
o branco das outras duas linhas. Como bloco cheio ela vira um objeto.

**`box-decoration-break: clone` é o que faz o degrau.** Sem ele o navegador
pinta um fundo contínuo entre a última palavra de uma linha e a primeira da
outra — um retângulo só, que é justamente o que a referência não mostra. Com
`clone`, cada linha ganha o próprio fundo e a borda direita acompanha o texto.

A margem negativa à esquerda (`-.16em`) vale só para o PRIMEIRO fragmento: o
bloco sangra para fora e a primeira letra fica no prumo da marca e do lead.

**O padding vertical (.06em) é maior que o vão entre as linhas** (entrelinha
1,02), de propósito: os fragmentos se tocam e o realce lê como peça só. A
sobreposição cai na faixa de descendente da linha de cima — "Good control" não
tem nenhum, então não come glifo. **Se a frase mudar, conferir isso.**

**A linha realçada saiu da lente do ponteiro** (`data-lente-texto` removido
dela): ela já é dourada permanente, e a lente pintaria dourado sobre dourado.
As outras duas linhas e o lead continuam acendendo.

### Tensão com a regra crítica nº5, e ela é real

O herói passa a ter **três** manchas douradas na mesma dobra: a tela do logo, o
bloco do realce e a régua do lead. O teto é dois. A referência que o usuário
desenhou mostra as três, então ficou como ele pediu — mas **a régua do lead é a
candidata óbvia a sair** se ele quiser fechar a conta: 2 px de dourado ao lado
de uma laje dourada lê como sobra, não como acento.

---

## 2026-08-19 (faixa) — Fundo de caixa inline tem a altura da FONTE, não da linha

O realce saiu "esquisito" e o usuário mandou deixar igual ao exemplo, sem cortar
nada. Medi os dois renders em vez de olhar.

**A causa.** `background-color` numa caixa inline pinta a ÁREA DE CONTEÚDO da
fonte, que é métrica do arquivo e não se negocia. Medido no render real do
usuário: Outfit tem **ascendente 1,00em e descendente 0,26em** — 1,26em de área
contra um passo de linha de **1,02em**. Consequências, as duas visíveis:

1. a faixa nascia **0,30em acima da maiúscula** — ouro morto no topo;
2. os fragmentos se sobrepunham 0,24em e a faixa encostava na linha de baixo.

**A correção: a faixa virou GRADIENTE.** `linear-gradient` sólido com
`background-size` e `background-position` em em dá altura e deslocamento exatos,
independentes da métrica:

| | valor | resultado |
|---|---|---|
| topo da caixa de padding | 1,00em acima da base | — |
| `background-position` | 0,10em | faixa começa 0,90em acima da base |
| maiúscula | 0,70em acima da base | **0,20em de ouro acima dela** |
| `background-size` altura | 1,22em | faixa termina 0,32em abaixo da base |
| descendente de g,y | 0,21em abaixo da base | **0,11em de ouro abaixo dele** |

Confirmado contra a referência, em em: ouro acima da maiúscula 0,20 (ref 0,23),
padding esquerdo 0,03 (ref 0,032), padding direito 0,16 (ref 0,20), vão até
"beats more" 0,22 (ref 0,23), razão de largura entre os dois fragmentos 0,64
(ref 0,61).

**O beiço de ouro à esquerda era o erro real.** Eu tinha `margin-left: -.16em`
com `padding-left: .16em` — o bloco sobrava 0,16em à esquerda da primeira letra
e a headline saía do prumo da marca e do lead. A referência tem 0,03em: o bloco
começa **onde a letra começa**.

### A tinta é literal, e o motivo é grave

`color: var(--traco)` parecia certo — mas dentro de `.heroi` esse token é
sobrescrito para servir à LENTE DO BRAÇO, e a tinta do título mudaria junto com
o desenho da máquina.

Pior: **no tema escuro `--sup-3`, que é o chão do herói, vale `#003566` — a
mesma cor da tinta do realce.** Qualquer glifo que saísse da faixa ficaria a
1:1, invisível. No claro o chão é `#001D3D` e daria 1,37:1, que também some. É
por isso que a faixa precisa ser exata: **fora dela a letra não existe.** As
folgas de 0,20em e 0,11em são a garantia, não acabamento.

A cor literal é aceitável aqui, ao contrário do caso do véu branco: a SUPERFÍCIE
desta tinta é `--dourado`, igual nos dois temas.

**E a reserva falha para o lado seguro.** Sem `box-decoration-break`, só o
primeiro fragmento receberia faixa e a segunda linha ficaria invisível. Todo o
bloco vive dentro de `@supports`, e o padrão é a linha em dourado sólido —
10,59:1 no tema claro, 7,74:1 no escuro.

**Regra que fica: para controlar a altura de um realce de texto, use gradiente
com `background-size`, nunca `background-color`.** A cor pinta a métrica da
fonte; o gradiente pinta o que você mandar.

---

## 2026-08-19 (empilhamento) — A foto do cabeçalho nunca apareceu, em página nenhuma

O usuário pediu "adicione uma imagem de fundo" no cabeçalho de capabilities —
e **já havia uma lá**, em oito das nove páginas. Nunca foi pintada.

`.cabecalho__foto` é `z-index: -2`. Filho de z negativo só pinta ACIMA do fundo
do pai **se o pai for contexto de empilhamento**, e `position: relative` sozinho
não cria um. Sem contexto, o filho negativo vai para trás do `background:
var(--navy-fundo)` do próprio `.cabecalho`. Oito cabeçalhos de navy chapado, com
a fotografia carregada e invisível — inclusive a de who-we-are, que o usuário
tinha marcado como "não aparece".

Uma linha: **`isolation: isolate`**.

**Regra que fica: z-index negativo em filho é uma promessa que só o contexto de
empilhamento do pai cumpre.** E o sintoma é silencioso — nada quebra, a imagem
baixa, o `alt` está certo, a varredura de referências passa. Só não aparece.

### Consequência: oito fotos ficaram visíveis de uma vez, e quatro ampliam

Medido contra a caixa do cabeçalho a 1440x620:

| fonte | tamanho | escala |
|---|---|---|
| refinaria | 2560x979 | 0,63x reduz |
| robotica | 1920x734 | 0,84x reduz |
| contato / servicos | 1920x620 | 1,00x |
| quem-somos | 1127x364 | **1,70x amplia** |
| galeria / projetos | 1125x363 | **1,71x amplia** |
| capacidades | 1024x331 | **1,87x amplia** |

Os quatro que ampliam vêm de originais pequenos (`foto.png`, `image1.png`,
`smpliderautomacao.png`, `engcontrole.png`) — **não existe fonte maior no
acervo**, e é o mesmo teto de resolução já registrado em 18/08. Eles ficam com o
véu PADRÃO (.72 → .92), que deixa a foto em ~8% de presença: nessa proporção a
ampliação não lê. Medido nos seis, o pior texto pequeno dá **4,70:1** — passa AA.

Só capabilities ganhou véu aberto, porque só ela tem fonte com folga.

---

## 2026-08-19 (capabilities) — Véu aberto tem preço, e o preço é medido

O cabeçalho trocou `capacidades-1024` — a mesma 1024x331 que quebrou who-we-are
— por `faixa/refinaria-2560`, e ganhou `.cabecalho--foto`, um véu mais aberto.
Quanto mais aberto, medido sobre a foto real a 1400x620:

| véu | pior fundo | h1 | lead | eyebrow | foto |
|---|---|---|---|---|---|
| .38/.82 + .62/.10 | #676C77 | 5,27:1 | **3,28:1** | **3,30:1** | 56% |
| **.52/.86 + .70/.26** | #414F62 | 8,33:1 | 5,19:1 | 5,22:1 | **36%** |
| .60/.88 + .76/.36 | #2F4157 | 10,42:1 | 6,49:1 | 6,53:1 | 26% |

O primeiro deixa a foto quase o dobro mais presente e era o que eu queria — mas
põe lead e eyebrow abaixo de 4,5:1, e os dois são texto pequeno. Ficou o
segundo: **o mais aberto que ainda passa AA nos três**.

### O hover da lista: `:has()` que encolhia as irmãs era inusável

A primeira versão crescia o item apontado e encolhia TODAS as irmãs com
`:has()`. Isso desloca a linha que está sob o ponteiro — as de cima encolhem,
ela sobe, o ponteiro escapa, o hover desliga, ela volta ao tamanho, o ponteiro
entra de novo. **Pisca em laço.** O usuário reportou: "a animação de hover nos
itens precisa ser usável".

Crescer `padding-block` **não move a borda de cima da própria caixa**: o box
cresce para baixo e o ponteiro continua dentro dele. Descendo de um item para o
outro, o anterior encolhe, o que SOBE a borda de cima do próximo e deixa o
ponteiro ainda mais dentro dele. Subindo, o de cima cresce e empurra o de baixo,
e o ponteiro segue dentro do que cresceu. **Estável nos dois sentidos — e sem
`:has()`.**

Medido sobre `--sup-2`: número `#6B5000` a 6,92:1, nome `#003566` a 11,28:1.

**Regra que fica: hover que mexe no layout dos IRMÃOS pode mover o alvo para
fora do ponteiro. Só crescer para baixo é seguro.**

---

## 2026-08-19 (retícula) — Duplicar oito valores de gradiente é como eles divergem

`.heroi::before` tinha a retícula quadriculada escrita inline. O cabeçalho
passou a querer a mesma coisa. Virou `.reticula`, com o desenho num `::before`
próprio — e não no fundo do elemento, porque herói e cabeçalho já têm
`background` navy, e em `.cabecalho`, que agora é contexto de empilhamento, um
`background-image` no mesmo elemento ficaria atrás dele.

`--reticula-z` decide a camada: **-2 no herói** (sob tudo) e **0 no cabeçalho**
(sobre o véu, sob o conteúdo — desenho técnico sobre a fotografia, não textura
de fundo). `--reticula-x/y` movem o foco da máscara: no cabeçalho ela desce para
34%/78%, onde o título vive neste bloco.

**E o barramento saiu do cabeçalho de who-we-are.** Ele nascia lá com
`extra=feixe('esq','esq',comeca=38)`; agora começa na seção "Since 2000", que já
entra pela esquerda. Duas tramas no mesmo bloco brigam, e o usuário tinha
marcado as pistas com um X.

---


## Estado atual (2026-08-19, tema)

- **Who We Are tem o barramento**: quatro pistas ortogonais que atravessam o cabeçalho e três seções, trocando de lado no caminho, com um pulso percorrendo cada uma.
- **Who We Are:** barramento, fotos de fundo em duas seções, emendas animadas e o método como diagrama de blocos.
- **120 referências, 0 quebradas, 0 órfãos.**

---

## 2026-08-19 (tela branca) — Véu travado em branco não sobrevive ao tema

A seção "Since 2000" virou um borrão branco no **tema escuro**. Causa: eu travei
o véu em `255, 255, 255` em vez de deixá-lo seguir a superfície da seção.

`.secao--foto` cobre o bloco de ÊNFASE, que é navy nos dois temas — por isso o
véu dele pôde ser um valor com override e ficou certo. O véu novo cobria a seção
de CORPO, cuja superfície **muda com o tema**: branca no claro, quase preta no
escuro. Pintando branco por cima da foto num fundo escuro, ele engolia o texto
claro e a seção inteira sumia.

Virou token com override de tema (`--veu-corpo`: branco no claro, `0, 12, 24` no
escuro), no mesmo padrão que `--veu` já usava.

**E o pior caso vira junto com o tema.** Com texto ESCURO sobre véu claro o ponto
perigoso é o mais ESCURO da foto; com texto CLARO sobre véu escuro é o mais
CLARO. Medido nos dois, véu a .78/.56:

| tema | pior fundo | corpo | secundário |
|---|---|---|---|
| claro | #E7E7E8 | 14,08:1 | 5,31:1 |
| escuro | #13202D | 14,02:1 | 8,58:1 |

A classe se chamava `.secao--foto-claro` — nome que **afirmava** o que causou o
bug, já que ela precisa funcionar no escuro também. Renomeada para
`.secao--foto-corpo`: o que a distingue é a SUPERFÍCIE que ela cobre, não a cor.

**Regra que fica: valor de cor literal em componente que atravessa temas é bug
esperando data.** Varri o resto do CSS atrás do mesmo padrão — só sobraram dois
fundos brancos fixos, ambos em hover sobre superfície navy, onde branco é o
certo. (`.botao--claro` é um deles e não é usado por nenhuma página: CSS morto.)

---

## 2026-08-19 (conserto) — Foto de faixa não cobre seção alta

### O que quebrou a seção "Since 2000"

`capacidades-1024.jpg` é **1024 x 331** — uma faixa larga. A seção tem ~900 px de
altura. Com `object-fit: cover` isso **amplia a imagem 2,7 vezes** e recorta uma
tira estreita: vira papa. Escolhi a foto pelo assunto e não conferi a proporção.

**Todas as fotografias do acervo são faixas** (proporção 2,6 a 3,1). Nenhuma serve
como fundo de seção alta. Medido a 1440 px de largura:

| foto | seção inteira (~900) | faixa de 62% (~560) |
|---|---|---|
| capacidades 1024x331 | **2,72x amplia** | 1,69x amplia |
| robotica 1920x734 | 1,23x amplia | **0,76x reduz** |
| servicos 1920x620 | 1,45x amplia | 0,90x reduz |

Conserto: a foto ocupa uma **FAIXA de 62%** da seção, não a seção inteira, e a
fonte passou a ser de 1920. Aí a imagem é REDUZIDA — que é a única forma de ficar
nítida. O véu vertical fecha em `--faixa-foto`, então a banda dos números fica em
branco limpo.

Remedido com as fotos que ficaram: **Since 2000** corpo 14,08:1 e eyebrow 5,31:1;
**Our mission** título 8,76:1, eyebrow 5,62:1, corpo 5,46:1.

**Regra que fica: conferir a PROPORÇÃO da fonte contra a caixa antes de escolher
a foto pelo assunto.** Ampliação acima de 1,0 já é perda visível.

### Espaçamento: cada componente inventava o próprio vão

`numeros` usava 96 px, `escada` 64, `planta` 64, `diagrama` 64 — o vão entre o
bloco de cabeçalho da seção e o componente abaixo mudava sem motivo, e o ritmo
vertical da página saía irregular. Virou um token só, **`--gap-bloco: var(--s-7)`**
(64 px). A `prancha` fica em 48 como exceção deliberada, a pedido do usuário.

64 dentro da seção contra 160 entre seções mantém a hierarquia certa: grupo
junto, assunto separado.

### Hover no diagrama

Os blocos eram estáticos. Sob o ponteiro: uma régua se desenha na borda de cima
(`scaleX`, o mesmo vocabulário do resto do site), a moldura vai a navy e o título
acende. Sem sombra e sem salto de escala. Medido: título navy 12,34:1 e moldura
11,28:1 sobre o off-white.

---

## 2026-08-19 (método) — Quatro cards iguais não eram um método

### Por que NÃO um terceiro modelo 3D

O usuário cogitou outro WebGL para "How we work" e perguntou o que eu achava.
Dois motivos para não: o site já tem dois (braço e planta), e cada um custou uma
sessão — mas o argumento que decide é de conteúdo. **As quatro etapas são uma
SEQUÊNCIA, e objeto 3D expressa objeto, não sequência.** A ordem viraria rótulo
pendurado no modelo.

O que expressa sequência na língua de quem compra esta página é **diagrama de
blocos**: quatro blocos em série, setas entre eles, e o sinal percorrendo. É
quadrado, é 2D, não repete recurso, e o pulso é o MESMO do barramento que desce
a página — a seção deixa de competir com ele e passa a ser a continuação dele.

A ligação fica ancorada no bloco (`::before` e `::after` do próprio passo), não
como célula da grade: assim a grade continua sendo quatro colunas iguais e a
seta some sozinha no último. Nas quebras de 1023 e 620 px as setas somem, porque
seta apontando para o vazio é pior que nenhuma.

### Foto de fundo em seção CLARA inverte o pior caso

Em bloco escuro o perigo é o ponto mais CLARO da foto (texto branco por cima).
Em bloco claro é o contrário: texto escuro, o perigo é o ponto mais ESCURO. A
ferramenta de medição procurava só o mais claro e por isso dava tudo aprovado
sem medir o que importava.

Medido de novo pelo ponto certo, com véu branco a .78 no miolo e .56 nas
laterais: pior fundo **#E7E8EB**, corpo a **14,21:1**, eyebrow a **5,36:1**, com
a fotografia chegando a **43%** de presença. É o véu mais ABERTO que ainda passa
com folga — fechar mais só apagaria a foto sem ganhar legibilidade que já existe.

### A emenda entre seções

Uma régua de 1 px que varre a borda de cima quando a seção entra, **na direção
que o barramento está correndo** naquele trecho. As seções deixam de se encostar
e passam a se entregar uma à outra.

Usa `::after` porque `::before` já é o véu de `.secao--foto`, e as duas coisas
coexistem na mesma seção nesta página.

---

## 2026-08-19 (barramento) — Curva não sobrevive a escala não uniforme

O feixe trançado virou **roteamento de barramento**: quatro pistas ORTOGONAIS,
só vertical e horizontal, que trocam de lado ao longo da página.

### Por que a curva tinha de sair, além do gosto

O pedido foi "mais tecnológico, menos arredondado" — e havia um motivo técnico
junto. `preserveAspectRatio: none` estica só o eixo Y, e **bezier sob escala não
uniforme vira outra bezier**: o ângulo do trançado mudava de seção para seção,
conforme a altura de cada uma. Geometria ortogonal é imune — vertical continua
vertical, horizontal continua horizontal. O que o usuário pediu por estética é
também a única forma de o desenho ser o mesmo em qualquer altura.

### A ordem das viradas não é enfeite

As quatro pistas trocam de lado em alturas diferentes (7%, 10%, 13%, 16%), e
**quem termina mais longe vira PRIMEIRO**. Com a ordem invertida, os trechos
horizontais cruzariam as verticais das vizinhas — que é exatamente o erro que um
roteamento real evita. Conferido pista a pista nos dois sentidos: nenhum
cruzamento.

### O SVG passou a ocupar a largura inteira

Era uma faixa de 64–96 px na margem esquerda. Para o barramento **trocar de
lado** ele precisa da seção inteira. Passa por trás do conteúdo (z-index 0 contra
1 do container), e os trechos horizontais ficam entre 7% e 16% da altura — dentro
do respiro superior da seção, onde não há texto para atravessar.

As pistas ficam em 1,2 / 2,4 / 3,6 / 4,8% à esquerda e 95,2 / 96,4 / 97,6 / 98,8%
à direita. A 1440 px isso é 17–69 px de um lado e 1371–1423 do outro, com o
conteúdo entre 80 e 1360 — as duas margens livres.

### Percurso na página

Cabeçalho: nasce a 38% da altura, à esquerda. Seção dos números: **cruza para a
direita**. Missão: corre à direita. Método: **volta para a esquerda**.

---

## 2026-08-19 (feixe) — A rota virou chicote de cabos

A rota de eletrocalha foi **removida inteira** — CSS, JavaScript e marcação — e
substituída por um feixe: quatro fios que trocam de posição entre si e voltam,
com um pulso de luz percorrendo cada um em tempos diferentes.

**O usuário reportou que o site quebrou com a rota, e eu não consegui
reproduzir.** Sem navegador, a checagem que dá para fazer — tags balanceadas nas
nove páginas, chaves do CSS, sintaxe do JS, referências — passou toda. Removi a
implementação inteira em vez de remendar: é a única forma de garantir que o que
quer que fosse saiu junto. Fica registrado como **não diagnosticado**.

### O que a versão nova elimina por construção

- **Nenhum JavaScript.** A rota tinha ouvinte de rolagem, `requestAnimationFrame`
  e `getBoundingClientRect` por trecho. O pulso do feixe é `stroke-dashoffset`
  animado em CSS — uma propriedade, sem nada lendo layout.
- **Nenhuma medida dependente de conta minha.** A rota tinha nós posicionados por
  aritmética que eu errei duas vezes (container 1280 quando é 1376; padding 32
  quando é 48). O feixe não tem nó nenhum: são quatro curvas e uma faixa.

### O truque que faz as emendas sumirem

**Todo trecho começa e termina nos mesmos quatro x — 20, 40, 60, 80.** Por isso
qualquer trecho encaixa em qualquer outro, e a troca de seção (navy → branco →
navy → off-white) não aparece. `variante` só muda a ALTURA em que os fios se
cruzam, nunca as pontas.

### O pulso, e por que ele não é dourado no claro

`pathLength="100"` normaliza o comprimento de cada fio, então `stroke-dasharray:
4 96` é sempre 4% de luz e 96% de vão, em trecho de qualquer altura. O que anima
é só o deslocamento — um segmento viajando.

A cor vem de `--accent-txt`: **#6B5000 no claro (7,57:1) e #FDC500 no escuro
(10,59:1)**. Dourado puro sobre papel branco dá 1,60:1 e o pulso simplesmente não
existiria. O `drop-shadow` de brilho só entra nas seções escuras — halo dourado
sobre papel branco não é brilho, é borrão.

### Escape de quebra de linha consumido por camada de ferramenta

Escrever `
` dentro de string no gerador virou quebra de linha REAL duas vezes
seguidas, deixando o arquivo com literal não terminado. Resolvido com
`NL = chr(10)` no topo de `build_paginas.py` e montagem por lista de linhas.

---

## Estado anterior (2026-08-19, citação)

- **Seção da citação centrada**, com véu simétrico próprio para texto no meio.
- **Dois `alt` errados corrigidos**, achados ao montar a prévia.
- **120 referências, 0 quebradas, 0 órfãos.**

---

## 2026-08-19 (fecho) — A última frase não podia entrar como um card

`.reveal` — subir e desembaçar — é o movimento de TUDO que entra na tela. Usá-lo
na frase de fecho fazia a última linha do site chegar igual a um card de setor.
Ela é a única linha que o visitante lê **depois** de ter visto o resto, e nas
nove páginas.

Agora as palavras se **plotam** da esquerda para a direita, uma a uma
(`clip-path`, não opacidade: a palavra não aparece, ela é traçada), e a régua
dourada se desenha **depois da última** — `--n` carrega a contagem de palavras e
o atraso da régua sai dela. A ordem importa: frase traçada, depois sublinhada, que
é a ordem de um desenho e não de dois efeitos disparados juntos.

**Rima com a intro**, que abre o site com uma frase sendo escrita. O começo e o
fim passam a ser o mesmo gesto.

Detalhe medido: `clip-path: inset(0 100% 0 -.08em)`. Sem a folga de `-.08em` à
direita, a última letra de cada palavra perde um sub-pixel no fim do traçado e a
frase inteira fica com a borda picotada.

---

## 2026-08-19 (aproximação) — O texto e as fotos são um grupo só

O bloco centrado de "what we actually do" estava a **160 px** do topo da seção e a
**96 px** das fotografias. O vão de baixo foi dividido ao meio (96 → 48), e a
coluna estreitou de 54ch para **48ch**.

O raciocínio: **as fotos são a prova do que o texto afirma** — os dois são um
grupo, e grupo junto se aproxima. O respiro grande fica onde separa assunto, que
é o topo da seção. A coluna mais estreita também lê como mais centrada mesmo
estando no mesmo eixo, porque com as duas margens irregulares a linha curta ajuda
o olho a achar o começo da seguinte.

---

## 2026-08-19 (citação) — Véu assimétrico não aceita texto centrado

A seção da citação foi centrada como a primeira. O que não era óbvio: **o véu da
fotografia estava desenhado para texto à ESQUERDA** — opaco em `--sup-3` na
borda esquerda, abrindo para `--veu-lado` a partir de 62%. Centrar o texto sem
tocar nele o colocaria exatamente sobre a parte mais clara da imagem.

`.secao--foto-centro` inverte a lógica: o véu **fecha no miolo**, onde a citação
vive, e **abre nas duas laterais**, onde a fotografia respira. Paradas em
27% / 45% / 55% / 73%, que são as mesmas que `ferramentas/sobreposicao.py` compõe
sobre a foto de verdade.

Medido no ponto mais claro do terço central, véu lateral .15 e miolo .55:

| tema | branco | secundário |
|---|---|---|
| claro | 8,28:1 | 5,31:1 |
| escuro | 7,88:1 | 5,06:1 |

Os dois passam com folga, então **o mesmo par serve nos dois temas** — e como é o
valor mais aberto que passa, é o que deixa a fotografia mais presente. O véu
padrão continua assimétrico para governo e contato, que seguem com bloco à
esquerda.

### A prévia pegou um defeito que não era de layout

Ao montar a seção para conferir, vi que a foto é um **close de relés e bornes** —
e o `alt` dela dizia "engenheiro sênior numa estação de comando". Texto
alternativo errado não é detalhe: é o que o leitor de tela anuncia no lugar da
imagem.

Auditando os 29 pares imagem/alt do site, achei um segundo: `contato-1920` é uma
**mão apertando um teclado de membrana** e carregava duas descrições, ambas
erradas ("engenheiro andando por um corredor" e "estação de trabalho de sala de
controle"). Corrigidos os dois. As três divergências que sobraram são versão
curta e longa da mesma cena, não contradição.

**Regra que fica:** montar a seção para ver a composição também confere o que a
legenda AFIRMA. Alt escrito longe da imagem envelhece errado.

---

## Estado anterior (2026-08-19, ladder)

- **Plataformas viraram diagrama LADDER.** Credenciais federais só em who-we-are. Past performance saiu da home. Rolagem suave no site inteiro, e a lente dourada chegou à planta.
- **120 referências, 0 quebradas, 0 órfãos.**

---

## 2026-08-19 (ladder) — A grade de plataformas era um card grid com outro nome

### Por que ladder

Oito células iguais com nome e papel não diziam nada sobre o que a empresa faz —
era o "mesmo card repetido" que o piso de qualidade chama de contêiner preguiçoso.
**Lógica ladder é o diagrama que um integrador de CLP escreve todo dia**, e o
comprador desta página lê sem legenda: dois barramentos verticais, um degrau por
plataforma, um contato por degrau.

**A notação carrega a informação em vez de decorar:** plataforma CERTIFICADA é um
contato ENERGIZADO (preenchido); plataforma que apenas operamos é um contato
aberto. O que antes era só cor de texto virou estado de circuito.

**Sem curvas.** A bobina `( )` do ladder real ficaria fora da regra de cantos retos
do projeto, então o estado vive no contato — que é reto por natureza.

### A lente da planta NÃO podia usar o dourado do herói

Medido: `#FDC500` sobre o papel da planta (`#F2F5F8`) dá **1,46:1** — a revelação
teria apagado o desenho em vez de acender. O uniform recebe **`--accent-txt`**,
que já resolve para `#6B5000` no claro (**6,92:1**) e `#FDC500` no escuro
(**11,66:1**). Mesma lente do herói, cor certa para cada papel.

O eixo Y do ponteiro entrou invertido de propósito (`1 - y`): `vTela` sai de NDC,
onde +1 é o topo. Foi o bug que custou uma sessão no herói; aqui já nasceu certo.

O fragment subiu de `mediump` para `highp` — o fBm da borda banda visivelmente em
mediump e o degradê vira degrau.

### Rolagem suave é NATIVA, de propósito

`scroll-behavior: smooth` mais `scroll-padding-top`, que é o que impede todo link
para `#secao` de parar com o título embaixo do nav fixo. **Não** sequestrei a roda
com JavaScript: custaria uma biblioteca no runtime (§9) e quebraria o gesto de quem
usa trackpad, teclado ou leitor de tela. `prefers-reduced-motion` desliga — rolagem
animada é das poucas coisas que provoca enjoo de verdade.

### `.reveal--limpo`: observado, mas parado

A faixa "From strategy to startup" é full-bleed. Dar `.reveal` a ela faria a seção
inteira subir 22 px e **abrir uma fresta da cor da seção vizinha** durante a
transição. O modificador entra na lista do observador sem se mexer, e quem anima
são os filhos: a fotografia se revela de baixo para cima por `clip-path` enquanto
encolhe de 1,06 para 1. Mesma direção do rodapé, no material que a faixa tem.

### Armadilha repetida: `str.replace` que falha em silêncio

De novo. A remoção do bloco de governo da home não entrou porque havia um
comentário no meio do trecho que eu procurava — e o `assert s != o` passou, porque
**outra** substituição do mesmo lote funcionou. Segunda vez nesta sessão. Assert por
lote não prova nada sobre cada item do lote; quando o alvo tem comentário no meio,
usar a ferramenta de edição, que falha alto.

---

## Estado anterior (2026-08-19, prancha)

- **Seção "what we actually do" refeita:** cabeçalho e texto centrados, e o mosaico de três fotos coladas virou uma PRANCHA de quatro fotos separadas, com moldura, marca de registro e linha de cota.
- **Quatro fotografias novas, todas autorais de campo**, entregues em `melhorias/gallery` e já no pipeline.
- **120 referências, 0 quebradas, 0 órfãos.**
- **Pendente de decisão:** os três vídeos de `melhorias/services` somam **180 MB** e não têm como ser publicados assim.

---

## 2026-08-19 (prancha) — Três fotos coladas liam como uma foto recortada

### O defeito não era o tamanho

O `.tiras` colava três fotos com 2 px de goteira. Com tão pouco entre uma e outra,
as três liam como **uma imagem só, recortada por acidente** — nenhuma delas era um
objeto. Aumentar não resolveria; o que faltava era separação e moldura.

A `.prancha` dá a cada foto o vocabulário de uma folha de desenho: moldura de
filete, marca de registro no canto, legenda em mono com referência técnica, e uma
**linha de cota** embaixo nomeando o que a fileira mostra. O deslocamento vertical
alternado é ritmo, não acaso: **duas** alturas repetidas leem como folha montada à
mão; três leriam como erro.

### O foco existiu e saiu

Cheguei a montar o destaque: o item apontado ganhava cor e escala, os irmãos caíam
para 38% de opacidade e quase nenhuma saturação, com `:has()` fazendo o irmão
reagir ao vizinho em CSS puro. **O usuário não gostou e pediu para tirar** — e ele
tem razão: a fileira inteira reagindo à passada do ponteiro chamava mais atenção
para o mecanismo do que para as fotografias.

Ficou só a entrada escalonada ao rolar. As fotos passaram a full color (a
dessaturação de repouso só existia para o hover ter para onde subir), e a **marca
de registro no canto virou estática** — ela nasceu como indicador de foco, mas o
valor dela nunca foi sinalizar estado: é a linguagem de desenho que o resto do
site fala.

### Erro que a prévia pegou: linha de cota sem tique

A cota nasceu com `height: 1px` mais `border-left/right` — com a caixa de 1 px de
altura as bordas laterais também tinham 1 px e **não havia tique nenhum**. A linha
de dimensão de verdade tem a caixa com 9 px (onde os tiques cabem) e a LINHA como
fundo de 1 px centrado nela.

### O bloco centrado tem medida menor de propósito

`.bloco--centro` fica em **54ch**, não nos 62ch do corpo. Texto centralizado tem as
duas margens irregulares, e quanto mais larga a linha mais o olho perde o começo da
seguinte. Centrar sem encurtar a medida teria piorado a leitura em nome do eixo.

### As quatro fotos novas

Todas **autorais de campo** — o §6.5 do design.md prefere isso a qualquer banco de
imagem, e o acervo tinha só cinco até aqui. `scada` (tela de vazão de efluente com
o capacete da i3 no primeiro plano), `painel-campo` (painel externo de estação
elevatória, porta aberta), `bomba` (conjunto submersível descendo de guindaste),
`obra-agua` (armário de controle entrando ao lado das comportas).

### Ferramenta nova

`ferramentas/previa_prancha.py` monta a seção fora do navegador — cabeçalho
centrado, fileira com deslocamento, moldura, legenda e cota — e aceita um índice de
foco, para conferir o estado de destaque sem Chrome.

---

## 2026-08-19 (lente no texto) — Um instrumento, não dois

As letras do herói passam a acender em dourado sob o ponteiro, como a máquina.
Medido sobre o navy: branco em repouso **16,89:1**, dourado aceso **10,59:1**.

**O que fez virar UM gesto, e não dois:** a lente do braço ouvia só `.braco`, então
acendia sobre a máquina e apagava sobre o texto — o dourado SALTAVA de um para o
outro. Agora o listener de posição vive na SEÇÃO (`raiz.closest(".heroi")`) e a
mesma coordenada alimenta os dois. O arrasto continua só na peça, senão arrastar
sobre o texto selecionaria palavra.

`situar()` continua medindo em relação ao canvas: com o ponteiro sobre o texto a
posição sai de 0..1 e a lente do braço cai fora sozinha, sem nenhum caso especial.

**Três decisões que evitaram texto invisível:**

1. O efeito é `background-clip: text` com `text-fill-color: transparent` — sem
   fundo recortado, **não sobra cor nenhuma**. Vive dentro de `@supports`.
2. O alvo são os SPANS de cada linha, **não o `<h1>`**. Os spans é que carregam o
   `transform` da animação de entrada, e um descendente transformado cria contexto
   próprio: o recorte do pai poderia não alcançá-lo e a headline sumiria.
3. O repouso (`--lente-x: -9999px`) deixa o gradiente inteiro na cor base, então o
   estado padrão é branco sólido — falhar aqui falha para o lado seguro.

**O raio e a curva são os MESMOS do shader** (252 px, dourado cheio até 77%). Se um
dia o `uRaio` de `braco.js` mudar, estes dois números mudam junto — senão o herói
passa a ter duas lentes com tamanhos diferentes.

---

## 2026-08-19 (movimento) — Movimento e tamanho disputam o mesmo espaço

O enquadramento é automático e fita o **pior instante do ciclo**, para nunca cortar
a garra. Consequência direta: **mover mais encolhe a peça.** Medido na moldura
real, partindo de 490 x 652 px:

| variação | desenho | custo |
|---|---|---|
| tudo x2,0 | 398 x 593 | −19% largura, −9% altura |
| só juntas no plano, forte | 488 x 579 | largura intacta, −11% altura |
| **só a garra x3,4** | **505 x 628** | **GANHA largura**, −4% altura |

**A garra é o movimento barato.** Os dedos são pequenos, então abrir muito mais
quase não cresce o envelope — e é o gesto mais legível dos dois, porque tem
começo e fim. Por isso ela subiu 2,6x e as juntas só 40%.

**Alargar a moldura não é saída:** a 66vw o desenho encosta na headline. A altura
cresceu (moldura de 1,44 para 1,60 da linha do texto) e o `AR` subiu de 0,96 para
0,98 — a folga existia para o traço fino não sumir na borda, e o traço agora tem
espessura de verdade. Parou em 0,98 e não em 1,00 porque a 1,00 a base
transbordava 2 px no pior de 180 quadros varridos, e a garantia vale mais que 2%.

Resultado: **503 x 671** (maior que os 490 x 652 de antes) com 40% mais movimento
nas juntas e o triplo de curso na garra. 180 quadros conferidos, folga mínima 6 px.

---

## Estado atual (2026-08-19, traço)

- **O braço deixou de ser fantasma.** Espessura de verdade por expansão em quad, e a rampa de profundidade ancorada na câmera. `gl.LINES` saiu do arquivo.
- **9 páginas, 0 referências quebradas, 0 órfãos.**

---

## 2026-08-19 (traço) — Um pixel de dispositivo não é um pixel de desenho

### O diagnóstico que eu errei primeiro

Olhando a captura em que o braço aparecia apagado, atribuí o sumiço à rampa de profundidade ter ficado dessincronizada do enquadramento automático — supondo que a câmera tivesse ido para longe. **Medi e era o contrário:** a distância caiu de 18,6 para 16,6. A frente do desenho estava mesmo em 7,60:1 de alfa.

O que estava errado era mais simples e eu já tinha escrito no próprio arquivo sem tirar a conclusão: **`gl.LINES` desenha 1 pixel de DISPOSITIVO, e `lineWidth > 1` é ignorado no Chrome.** Em DPR 2 isso é meio pixel de CSS. A linha não estava fraca — estava fina demais para o alfa que carregava. Alfa e espessura não são intercambiáveis, e eu tinha tratado como se fossem desde o começo, com o comentário "peso de linha falso" a duas telas de distância do bug.

### As duas correções

**1. Espessura real, por expansão em quad.** Cada segmento virou um retângulo de 6 vértices, expandido na direção NORMAL à linha em pixels de tela. Desenhado com `drawArraysInstanced`: seis vértices e 1421 instâncias.

- O empacotamento mudou de 2 vértices × 5 floats para **1 segmento × 8 floats** (`ax ay az bx by bz peso elo`) — os dois extremos precisam chegar juntos ao mesmo vértice para dar a direção.
- Instanciar em vez de duplicar na CPU: **45 KB em vez de 341 KB**, e a geometria continua escrita uma vez só.
- O `peso` finalmente escolhe **largura** (tokens `--braco-linha-fina: .9px` / `--braco-linha-grossa: 1.8px`) em vez de fingir largura com transparência.
- A borda tem rampa própria de antisserrilhado (0,8 px de cada lado), o que permitiu **desligar o MSAA** — em linha fina ele resolve mal e come justamente a intensidade que faz falta.

**2. Profundidade relativa à câmera.** As constantes 15,0 e 7,5 eram distâncias absolutas, medidas quando a câmera era fixa; depois o enquadramento virou automático e passou a variar de 16,5 a 25,3 conforme a moldura — a mesma aresta caía em pontos diferentes da rampa. Agora é `(c.w − (uDist − uRaioPeca)) / (2·uRaioPeca)`, imune a zoom. **O piso subiu de 0,20 para 0,55:** medido, o contorno estrutural no fundo dava **1,47:1** e sumia; agora dá **3,19:1**, e a frente segue em 7,60:1.

### A armadilha que quase passou: uniforme homônimo

O vertex shader ganhou `uRaio` para o raio da peça — e o fragment **já tinha** `uRaio` para o raio da lente do ponteiro. Num programa ligado, uniformes de mesmo nome compartilham **uma única localização**: os dois `gl.uniform1f` se sobrescreviam, e o último a rodar (0,30 da lente) viraria o raio da peça, achatando a rampa de profundidade. Renomeado para `uRaioPeca`.

**Regra que fica:** ao acrescentar uniforme, conferir os DOIS estágios. O verificador de uniformes do projeto agora separa VS de FS e acusa homônimos.

### Beco: `str.replace` que falha em silêncio

A troca do vertex shader não entrou e eu só percebi porque o verificador acusou os atributos antigos. O `assert s != o` do script passou — **porque as outras duas substituições do mesmo lote funcionaram**. Assert por lote não prova nada sobre cada item do lote. Trocado pela ferramenta de edição, que falha alto quando o alvo não bate.

---

## Estado anterior (2026-08-19, correção)

- **Bug de rolagem corrigido:** a página crescia sem parar e ficava impossível de navegar. Causa: realimentação entre o tamanho do canvas e o layout.
- **9 páginas, 0 referências quebradas, 0 órfãos.**

---

## 2026-08-19 (correção) — O canvas que crescia sozinho

### A cadeia

1. `.heroi__peca { height: 144% }` — porcentagem de altura contra uma **linha de grade de altura automática**.
2. Porcentagem contra altura indefinida resolve para `auto`.
3. → `.braco { height: 100% }` de `auto` → `auto`. → `.braco__tela { height: 100% }` de `auto` → `auto`.
4. → O `<canvas>` cai para o **tamanho intrínseco**, que são os atributos `width`/`height`.
5. → `medir()` lê esse retângulo, multiplica por `dpr` (2) e **escreve de volta nos atributos**.
6. → Quadro seguinte: lê o dobro, escreve o dobro. **A caixa dobrava por quadro.**

A página crescia sem limite, a âncora de rolagem do navegador brigava com isso, e a tela subia e descia sozinha.

### Por que só apareceu agora

Até a entrega anterior a peça tinha `aspect-ratio: 5 / 4` e largura definida — a altura **sempre** era definida, e o intrínseco do canvas nunca vazava. Trocar para `height: 144%` em linha automática armou e disparou a armadilha no mesmo movimento.

### As três correções, e por que são três

1. **`.braco__tela` e `.planta__tela` viraram absolutos.** Canvas tem tamanho intrínseco vindo dos atributos; fora do fluxo, ele não pode vazar para o layout de jeito nenhum. Esta é a correção estrutural — as outras duas são cinto e suspensório.
2. **A caixa da peça só ESTICA na linha** (`align-self: stretch`, altura definida vinda do texto) e o desenho é **absoluto dentro dela**, com `top: -10.5%` e `bottom: -33.5%`. Absoluto não devolve altura para a linha, então o ciclo não tem por onde fechar. Os offsets somam 1,44 e reproduzem a geometria medida antes **exatamente** — a prévia devolve os mesmos `peca 554..1446 x -3..856` a 1440x900.
3. **Teto de 4096 px em `medir()`**, nos dois componentes, mais um `return` quando a caixa ainda não tem tamanho. Não é otimização: é a trava para que a próxima regressão desse tipo seja um desenho feio, e não um site travado.

### A regra que fica

**Componente que LÊ o próprio retângulo e ESCREVE o próprio tamanho não pode participar do fluxo.** Se participar, qualquer altura que deixe de resolver vira realimentação — e o sintoma não aparece perto da causa: some no CSS e reaparece como a página inteira travando.

---

## Estado anterior (2026-08-19, fecho)

- **Herói: a peça saiu de `position: absolute` e virou item da grade**, na mesma linha do texto. É o único jeito de "centralizada com o texto" ser verdade em qualquer altura de janela.
- **9 páginas, 0 referências quebradas, 0 órfãos.**
- **Falta conferir:** a extensão do Chrome nunca conectou nesta sessão. Tudo foi medido fora do navegador — inclusive a composição do herói, com `ferramentas/previa_heroi.py`.

---

## 2026-08-19 (fecho) — O eixo Y do ponteiro estava invertido

### O bug

`vTela` sai de NDC (`p.xy / p.w * 0.5 + 0.5`), onde **+1 é o topo** — então `vTela.y` vale 1 em cima e 0 embaixo. O ponteiro do DOM é o contrário: `clientY` cresce para baixo. Sem inverter, a lente aparecia **espelhada na vertical**: ponteiro no alto, dourado embaixo.

`medirCorte()` já compensava esse eixo (por isso a troca de folha estava certa); só `situar()` tinha ficado para trás. **Regra que fica: num shader que usa NDC direto, todo valor vindo do DOM precisa do mesmo espelho — e é fácil acertar um e esquecer o outro no mesmo arquivo.**

### Centrar com o texto DIMINUIRIA a peça — a conta

O desenho começa a ~6% do topo da moldura. Centrado na linha do texto, ele só cabe até `H <= 2 x centro / 0,94`. A 1368x768 isso trava em **619 px, menos que os 624 de antes** — ou seja, centrar puro e "um pouco maior" eram incompatíveis.

Resolvido com `height: 144%` mais `translateY(8%)`: o deslocamento para baixo compra a altura que faltava sem encostar no topo. Medido:

| janela | linha do texto | moldura | desenho | sobra no topo |
|---|---|---|---|---|
| 1368x768 | 501 px | 721 | **651** (+16%) | 14 px |
| 1920x1080 | 620 px | 893 | **807** (+44%) | 53 px |

O círculo que o usuário desenhou à mão tem o centro **abaixo** do centro do texto — o deslocamento não é licença, é o que o exemplo pede.

### `grid-column: 6 / -1` teria desabado a composição inteira

O texto ocupa as colunas 1..6. Uma peça começando na 6 **colide** com ele na grade, e a auto-colocação empurraria o texto para a linha 2 e o rodapé para a 3. Ficou `7 / -1`, e a largura visual não vem da área de grade: vem do `width`, que transborda para a esquerda por causa do `justify-self: end`.

### Efeito colateral: a peça deixou de atravessar

Centrada no texto, ela não alcança mais a borda de baixo do herói — e o exemplo do usuário mostra exatamente isso, com o círculo parando pouco acima da divisa. **A troca de tinta continua no shader e liga sozinha** (`uCorte` é medido por quadro); é só a geometria que não chega mais lá nesta composição.

### O herói passou a estourar a dobra em laptop de 768

Somando nav 72 + texto ~573 + rodapé 148 + respiro 96, o herói pede ~890 px a 1368 de largura. Ele cresce (é `min-height`, não `height`), então ninguém fica cortado — mas a dobra deixou de caber. **A marca é o bloco novo dessa conta**, e encolhe sozinha abaixo de 820 px de altura. O resto viria de mexer no tamanho do H1, e **tipografia não se altera sem confirmação** (CLAUDE.md #2) — fica como pergunta em aberto.

### Ferramenta nova

`ferramentas/previa_heroi.py` monta o herói inteiro fora do navegador: refaz a aritmética do CSS (grade de 12 colunas, container centrado, peça na 7..12 alinhada ao fim, altura em % da linha do texto e o deslocamento) e desenha o braço por cima com `previa_braco`. Não é motor de layout — é o suficiente para responder "a peça está onde o exemplo pede?" sem Chrome.

---

## Estado anterior (2026-08-19, noite)

- **A home ganhou fotografia e a marca voltou ao centro da narrativa.** Intro = logo que se desenha → herói com logo, texto e o braço 3D → o braço ATRAVESSA a borda de baixo e entra na seção seguinte, trocando de tinta ao cruzar.
- **9 páginas, 0 referências quebradas, 0 órfãos.** Duas ferramentas de medição novas: `varredura.py` (referências) e `sobreposicao.py` (contraste sobre fotografia).
- **Falta conferir:** a extensão do Chrome continua desconectada. Geometria, enquadramento, contraste e estrutura de HTML estão medidos; **ver no navegador continua pendente.**

---

## 2026-08-19 (noite) — Por que o hover não funcionava, e o que mais mudou

### O bug era de EMPILHAMENTO, não de evento

`.heroi__container` é `z-index: 2` e ocupa a largura toda; `.heroi__peca` é `z-index: 1`. O container ficava **por cima** da peça e engolia todo `pointermove` — nenhum `addEventListener` do braço chegava a rodar. Não havia nada errado em `braco.js`.

Resolvido com `pointer-events: none` no container e `auto` de volta só em marca, título, apoio e rodapé. Os **vãos entre os blocos de texto passam direto para o desenho**, e o texto continua selecionável. Regra que fica: **num herói com peça interativa atrás do texto, a camada de texto tem de ser furada, não rebaixada** — mexer em z-index só troca quem cobre quem.

### A peça atravessa duas folhas, e a tinta troca na borda

- O braço agora é `min(56vw, 780px)` e sangra 96 px para dentro da seção seguinte.
- Isso só é possível com **`overflow-x: clip` + `overflow-y: visible`**. Com `hidden` num eixo e `visible` no outro, o `visible` computa para `auto` e nasce barra de rolagem; com `clip` ele sobrevive. O `overflow: hidden` fica declarado antes como reserva — quem não tem `clip` só não vê a peça atravessar.
- **Medido: `#9FBEE0` sobre branco dá 1,92:1.** O desenho simplesmente sumiria ao cruzar. Então o shader ganhou `uCorte` (em espaço de tela) e um segundo par de tintas: abaixo da linha a tinta é navy (12,34:1) e o aceso é `--dourado-txt` (7,57:1) — o dourado puro daria 1,60:1 sobre branco, que é a regra crítica nº4.
- **O GANHO troca junto:** .92 em cima, **1,15 embaixo**. Tinta escura sobre claro precisa de mais alfa para o mesmo contraste — põe a aresta estrutural mais fraca em 4,92:1 em vez de 3,33:1.
- No tema escuro a seção de baixo também é escura (`--sup-1` = `#000C18`), então não há troca de folha: os dois lados usam a mesma tinta.

### A intro virou a MARCA — e agora o pouso é exato

O par foto→traço do braço **nunca ia coincidir**: o desenho da referência e a peça em 3D são a mesma máquina em poses diferentes, e nenhum ajuste de escala conserta isso. O logo não tem esse problema — ele pousa sobre si mesmo, mesmo SVG e mesma proporção, e o `data-encaixe` voltou a 1.

- O logo **se desenha**: uma cópia só de traço por cima das formas cheias, com `stroke-dasharray`. `pathLength="100"` normaliza os três contornos ao mesmo comprimento, então **um único dasharray serve para todos, sem medir caminho em JS**.
- O destino do voo virou `[data-intro-destino]` no HTML, em vez de um seletor fixo no `main.js`.
- Consequência: a fotografia do EPSON saiu do site (4 arquivos, 269 KB). A **máscara de traço ficou** — é a reserva de quem não tem WebGL2.

### Fotografia na home: o véu foi medido, não escolhido

`ferramentas/sobreposicao.py` compõe o véu do CSS **sobre as fotos de verdade** e calcula o contraste por média local de 12×12 (pixel a pixel condena letra grande que lê perfeitamente).

- **`#8FB4DC` reprovou.** Sobre navy chapado dá 7,83:1; sobre a foto velada cai para **3,71:1** — abaixo de 4,5 para texto pequeno. Trocado por `#B9D2EA` em `.secao--foto`: **5,14:1** no pior ponto e 10,84:1 sobre o navy, então serve nos dois.
- **O véu do tema escuro tem de ser mais fechado que o do claro**, e é contraintuitivo: `--sup-3` no escuro é `#003566`, mais CLARO que o `#001D3D` do tema claro. Com .55 o secundário caía para 4,05:1. Ficou **.55/.35 no claro e .68/.50 no escuro** (5,61:1). A foto aparece menos no escuro — é o preço de o fundo já ser claro em relação a ela.
- Legendas das tiras: branco sobre o degradê dá 4,67 a 5,92:1 nas três fotos.

### `height: 100%` num `<img>` dentro de `<picture>` não resolve

O helper `imagem()` envolve o `<img>` num `<picture>`, que é **inline e de altura automática**. Uma altura percentual no `<img>` resolve contra ELE, não contra a moldura, e a foto colapsa para a altura intrínseca. É o motivo pelo qual `.faixa__foto` já era absoluta — `.tiras__item img` e `.dados__foto img` passaram a ser também.

### Contagem de dourado: a dica do rodapé perdeu a cor

O herói passou a ter a tela do logo (1) e a régua do apoio (2). A dica do rodapé era a terceira e estourava a regra crítica nº5 — virou `rgba(255,255,255,.72)`. O dourado do braço não conta: é transitório e sob o ponteiro.

### O que ficou fora, e por quê

O pedido dizia **"mexer apenas na tela principal"** e, na mesma frase, "escolha bem quais imagem usar **em cada página**". **Só a home foi mexida.** As outras oito continuam com as fotos que já tinham. Distribuir imagem pelas demais páginas é o próximo passo, se for o caso.

E **não entrou banco de imagem novo**: o `§6.5` do `design.md` proíbe preferir banco a foto real de campo, e o acervo só tem 5 fotos autorais (todas já em uso). As fotos de fundo que entraram são as que o site já processava — refinaria, contato e serviços.

---

## Estado anterior (2026-08-19, tarde)

- **O herói deixou de ser fotografia.** A peça agora é `site/js/braco.js`: um robô de 6 eixos gerado por código, orbitável por arrasto, que acende em dourado sob o ponteiro. A lente de revelação continua viva nos cinco cards de setor da home e nos cinco de past-performance.
- **9 páginas, 0 referências quebradas, 0 arquivos órfãos** — `python ferramentas/varredura.py` confere isso sozinho agora.
- **Falta conferir:** tudo isto foi medido FORA do navegador, porque a extensão do Chrome não estava conectada nesta sessão. Geometria, enquadramento e contraste estão medidos; **ver os shaders compilando de verdade continua pendente.**

---

## 2026-08-19 (tarde) — O braço do herói: geometria gerada, não fotografada

### O pedido e o que ele virou

O usuário pediu "um elemento igual à planta para o herói", trocando a foto do braço robótico, com o mesmo comportamento de antes e dourado sob o ponteiro. Escolheu, entre três opções, o braço de 6 eixos **gerado em WebGL** com arrasto para orbitar + lente dourada. As imagens de referência que ele passou (uma foto e um desenho do MESMO braço EPSON) viraram duas coisas: o modelo de forma e de estilo do 3D, e o novo par foto↔traço da intro.

### O primitivo que fez a peça existir: envoltória de círculos

- Todo elo deste braço é uma **chapa de cantos arredondados**, e a envoltória convexa de N círculos descreve isso exatamente. Para cada direção `u`, o ponto do contorno é `c_i + r_i·u` do círculo que maximiza `c_i·u + r_i`. Onde o vencedor não muda sai um arco; **no passo em que ele muda sai exatamente a reta tangente** entre os dois círculos.
- São sete linhas de código, e delas saem braço, antebraço, punho, dedos e flange — **sem uma conta de tangente e sem um vértice escrito à mão**. Mesmo espírito da planta (geometria por primitiva), primitivo diferente porque o assunto é outro: lá torre e tanque, aqui chapa usinada.

### Cinemática direta NA GPU

- A geometria é gerada **uma vez**, em espaço local de cada elo, e cada vértice carrega o índice do elo. Por quadro sobem 9 matrizes (`uElo[]`) e o vertex shader faz `uMVP * uElo[elo] * pos`.
- **Nenhum vértice é reescrito para animar.** É a diferença entre animar um robô e redesenhá-lo — e é o que permite um ciclo de trabalho de 13 s (alcança, fecha a garra, recolhe, abre) custando um `drawArrays`.

### Três erros de sinal e de direção que só o desenho revelou

1. **Os dedos cresciam para TRÁS.** Escritos em -Y a partir do nó, entravam no punho em vez de sair dele.
2. **A garra abria ao contrário.** O dedo cresce em +Y e girar +θ em Z leva +Y para `(-sinθ, cosθ)`; para o dedo de +x abrir, o ângulo tem de ser **negativo**. Com os dois sinais iguais, os dois dedos iam para o mesmo lado — a garra "abria" de lado.
3. **O punho dobrava a garra de volta à horizontal.** `a5 = +0,80` punha a ferramenta apontando para o lado; a referência aponta para baixo. O total de rotação em Z é `a2 + a3 + a5`, e resolver para a direção certa deu `a5 ≈ -0,20`.

### O enquadramento não podia ser uma constante — e a conta mostra por quê

- **A silhueta deste braço muda de PROPORÇÃO com o azimute.** Medido: de pé é retrato (218 × 313 px); aberto de lado é paisagem (498 × 371). Distância fixa ou corta a garra quando o visitante gira, ou deixa a peça pequena o tempo inteiro.
- A câmera passou a **resolver a própria distância**, a partir dos 8 cantos da caixa de cada elo já transformados pela cinemática: um ponto a `z` de profundidade e `x` de afastamento só cabe se `d ≥ z + |x| / tan(meio campo)`.
- **A primeira versão media a pose do INSTANTE, e a peça pulsava de tamanho** — perto de 40% de variação a cada 13 s, que lê como zoom involuntário, não como máquina trabalhando. Agora a distância é o máximo sobre **seis fases**, então depende só do ângulo: parada, a peça não muda de tamanho nunca.
- **A folga (`AR`) é medida:** .86 dava 68% de ocupação e 34 px de folga no pior caso; 1.00 dava 78% mas só 2 px, apertado demais para linha antisserrilhada. Ficou **.96**.
- Conferido no fim: **240 quadros** (16 azimutes × 5 fases × 3 inclinações) com folga mínima de **7 px**. Nunca corta.

### A moldura 5/4 é resultado de medição, não de gosto

O braço **alcança de lado**. Numa moldura retrato a extensão lateral é que manda, e a câmera recua até 25,9 unidades para caber — deixando a peça em 62% do quadro. Alargando, a restrição vertical assume e a distância trava em 16,5: **a partir de 1,25, largura extra não compra nada.**

| proporção | 0,74 | 0,90 | 1,06 | **1,25** | 1,58 |
|---|---|---|---|---|---|
| ocupação em repouso | 62% | 63% | 69% | **79%** | 79% |

Consequência: a moldura do herói **não** é mais a mesma da peça da intro (729/991, que é a da fotografia). O `data-encaixe="0.53"` no elemento reconcilia as duas — ver abaixo.

### O par EPSON: a silhueta saiu do DESENHO para servir à FOTO

- A foto é um braço **branco sobre fundo branco em cima de um pedestal branco**. Não existe limiar de cor que separe a peça do fundo — **o discriminante não está na cor, está na forma**. E a forma já existia pronta: o desenho é a mesma peça, na mesma pose.
- Então a silhueta sai do desenho e vira a matte da foto, depois de **registrar os dois por busca de escala + deslocamento**: `s = 0,812`, `dx = -9`, `dy = +23`, **IoU = 0,928**.
- **Isso resolve o pedestal de graça:** o desenho não tem pedestal, então a interseção apaga a caixa branca sem nenhum corte manual em y.
- **Beco sem saída caro:** a primeira busca amostrava ponto a ponto e devolvia **IoU acima de 1**. Com `s < 1`, vários pixels do desenho caem no MESMO pixel da foto e a interseção contava duplicado. Interseção tem de ser contada sobre **máscaras rasterizadas**, não sobre pares de índices.
- **A erosão final de 2 px não é acabamento, é correção:** peça branca sobre fundo branco em JPEG deixa um halo de *ringing* de 2–3 px que passa em qualquer limiar de luminância, e sobre o navy do herói ele lia como purpurina em volta do braço.
- **O discriminante do traço está no AZUL.** A linha é ocre (medido: RGB 0,926 / 0,665 / 0,017) sobre papel 0,996. Em **luminância** ela só alcança 0,46 de tinta, porque R e G continuam altos — ler ali obrigaria a esticar a curva e traria o papel junto. No **azul** a separação é quase binária: 0,017 contra 0,996. Mesma lição do recorte do braço laranja (lá era o verde), em outro canal.
- **A máscara sai em LA (cinza + alfa) com o alfa posterizado em 32 níveis.** Medido a 920 px: RGBA 555 KB · LA 432 KB · **LA posterizado 201 KB**. O alfa é o único canal que alguém lê (`mask-image` e `texImage2D`), e 32 níveis bastam para linha antisserrilhada.

### A intro entrega um DESENHO, não uma fotografia

- Antes, a peça da intro voltava a ser foto no fim do voo, porque a lente esperava fotografia do outro lado. Agora o que espera é o braço em aresta: a troca foto→traço **não volta**.
- **`data-encaixe="0.53"`:** o braço em 3D mede 283 × 377 px numa moldura de 520 × 416; o traço da intro, pousado a escala `e`, mede 520e × 707e. Igualar a ALTURA dá `e = 377/707 = 0,53` — e a largura sai em 276 contra 283, então casam nos dois eixos. Sem isso o desenho pousaria quase o dobro do tamanho da máquina em que ele se transforma.
- O braço nasce com a lente **acesa** (`ativo = 1`) e esfria em ~0,8 s. Não é enfeite de carregamento: é a costura com a intro, que entrega o desenho em dourado exatamente ali.

### `pow(x, 2.0)` com x negativo é INDEFINIDO em GLSL

A banda dourada da lente é uma gaussiana `exp(-pow((dist − 0,95)·26, 2))`. Dentro da lente inteira o argumento é **negativo**, e a especificação diz que `pow(x, y)` é indefinido para `x < 0`; onde o driver devolve NaN, o NaN atravessa a multiplicação e contamina a saída. Trocado pelo **quadrado explícito** (`t*t`) em `braco.js` **e em `lente.js`**, que carregava o mesmo defeito desde a entrega da manhã. É a mesma classe do bug do `uTinta`: valor inválido que sobrevive à máscara que deveria desligá-lo.

### Dois defeitos anteriores achados de raspão, e corrigidos

1. **`past-performance.html` tem 5 lentes e NUNCA carregou `lente.js`.** `scripts_extra` só era passado para a home. As lentes de lá sempre rodaram na via CSS — funcionavam, mas sem o shader.
2. **O herói mobile empilhava errado.** Em ≤900px a peça sai de `position: absolute` e vira irmã **em linha** do container, porque `.heroi` é *flex* — e o `grid-column` daquela regra nunca teve efeito, já que quem manda é o pai. As duas disputavam a largura da tela. Resolvido com `flex-direction: column`.

### Tensões com o `design.md` que o usuário precisa saber

- **§6.5 diz "sem ilustração 3D".** A regra está no parágrafo de **ícones**, e a planta isométrica — aprovada pelo usuário nesta mesma sessão — já abriu o precedente de desenho 3D gerado. Seguimos por isso, mas fica registrado como **leitura**, não como fato.
- **Regra crítica nº5 (máximo 2 dourados por dobra):** no herói há a régua do apoio e a dica do rodapé. O dourado do braço é **transitório e sob o ponteiro**, e substitui a banda dourada que a lente já desenhava ali — a contagem não subiu.

### Cores do braço, medidas

Sobre o navy do herói (`#001D3D`): `#9FBEE0` dá **8,78:1** opaco e **3,57:1** a 55% de alfa; o dourado `#FDC500` dá **10,59:1**. O ganho de linha do shader é **0,92**, que põe a aresta ESTRUTURAL mais fraca (peso .6) exatamente em 55% — o piso de 3:1 do WCAG 1.4.11 para elemento gráfico que carrega informação. As arestas de detalhe caem abaixo disso de propósito: são sombreado, não estrutura. `--traco` (#003566) daria **1,37:1** e sumiria, e por isso o braço não usa o token da lente.

### Ferramenta nova: prévia fora do navegador

`ferramentas/previa_braco.js` + `.py` carregam **o módulo de produção** por `vm`, injetam a exportação antes do fecho da IIFE, e desenham em PNG com o par de cores real. Sem isso, a única pergunta que importa — "isto se parece com um braço de 6 eixos?" — não teria resposta nesta sessão.

**Armadilha que ela mesma criou:** a prévia começou com uma **cópia** de `pose()`, e em meia hora a cópia já tinha divergido — a amplitude da cintura mudou no site e não na prévia. `pose()` e `enquadrar()` foram movidas para o escopo do módulo, e a prévia passou a rodar as originais. **Prévia que diverge do original não é prévia, é ficção.**

---

## Estado anterior (2026-08-19, manha) — superado pela entrega da tarde

- **Fase: o site existe.** 9 páginas em `site/`, 159 KB de HTML, 7,0 MB de imagens, **0 referências quebradas e 0 arquivos órfãos** (conferido por varredura das 109 referências únicas).
- **Falta conferir:** tema claro no navegador, faixa mobile, e as 8 páginas internas — só a home foi inspecionada.

---

## 2026-08-19 — Stack decidida contra o pedido inicial, e por quê

- **O usuário pediu Three.js; a entrega saiu em WebGL2 escrito à mão.** Não foi desvio: o pedido contrariava a §9 do `design.md` ("sem dependência de terceiros no runtime"), a regra crítica nº1 do `CLAUDE.md` mandou avisar antes de mudar, e a escolha voltou para ele com três opções e números. Ele escolheu a via do meio.
- **A conta que decidiu:** Three.js custa ~165 KB gzip. A fonte inteira do site tem 32 KB e CSS+JS somam ~40 KB — a biblioteca pesaria **2,5× o site inteiro**. E para o efeito pedido (duas texturas e uma máscara entre elas) não se usa nada do que ela traz: nem cena, nem câmera, nem luz, nem geometria, nem loader. Sobra um quad de tela cheia.
- **Consequência:** `site/js/lente.js` (~260 linhas) e `site/js/planta.js` (~470 linhas) são shaders e matemática do projeto. A planta tem 60 linhas de matriz (perspectiva, lookAt, multiplicação) e **gera a geometria por código** a partir de primitivas — caixa, cilindro, torre, arranjo solar, bacia de decantação. Nenhum `.glb`, nenhum arquivo de modelo.
- **A planta isométrica navegável é bloco novo, que o UnidoCLP não tem.** Resolve de uma vez o "varie a estrutura" e o "gêmeo digital 3D" que o usuário marcou. Ela desenha em **aresta, não em face** — o que a costura com o resto do site, onde o assunto é sempre o desenho técnico por baixo da fotografia.

## 2026-08-19 (armadilha cara) — `getComputedStyle` de custom property devolve o hexadecimal literal

- **Sintoma:** o braço robótico do herói renderizava **vermelho vivo** em vez de laranja. A suspeita errada custou tempo na composição de alfa e no `premultipliedAlpha` — e não era nada disso.
- **Causa:** `getComputedStyle(el).getPropertyValue('--traco')` **não** resolve para `rgb()`. Devolve a string `"#003566"` crua. O parser lia isso com uma regex de dígitos, que casa o token inteiro como **um** número: `uTinta` virava `[14, NaN, NaN]`.
- **Por que `uAtivo = 0` não salvava:** em IEEE 754, **NaN × 0 = NaN**. A camada de desenho estava multiplicada por zero e mesmo assim contaminava a saída. É um bug de cor que sobrevive à própria máscara que deveria desligá-lo — e por isso não aparecia no código do shader.
- **Como foi achado:** comparando a média de cor da mesma imagem por canvas 2D e por shader. Deram **idênticas** (`[103,48,27]` nas duas), o que eliminou o pipeline de textura e apontou para os uniforms. Medir os dois caminhos resolveu; reler o shader não estava resolvendo.
- **Regra que fica:** todo leitor de token para GL precisa de parser hexadecimal próprio. Está em `lente.js` e `planta.js`, com a nota longa no primeiro.

## 2026-08-19 — Tema escuro: a ênfase muda de direção, não de lugar

- **O `design.md` não previa tema escuro.** É decisão nova, e por isso passou pelo mesmo crivo do resto: `ferramentas/contraste.py` calcula **34 pares** (28 de texto, 6 de borda) nos dois temas. Todos os de texto passam AA.
- **A inversão que faz o sistema fechar:** `--sup-3`, o bloco de ênfase, **continua sendo a marca** nos dois temas. No claro ele é `#001D3D` e lê como "o bloco escuro"; no escuro ele é `#003566` e lê como "o bloco aceso". A ênfase não muda de lugar, muda de direção. Quem inverte um tema achatando tudo perde essa hierarquia.
- **Duas famílias de linha, e a distinção não é cosmética:** `--filete` é divisória decorativa e o **WCAG 1.4.11 a isenta** de 3:1; `--borda-ui` delimita componente (botão, campo) e é **obrigada**. Tratar as duas como uma só foi o que fez as 6 primeiras medições falharem. Resolvido com `#6E8093` no claro (4,06:1) e `rgba(255,255,255,.38)` no escuro (≥3,01:1 nas três superfícies).
- **O anel de foco não podia ser uma cor só:** `#FDC500` dá **1,60:1** sobre branco e `#003566` dá **1,37:1** sobre navy. O token `--foco` vira por superfície — navy no claro, dourado sobre qualquer bloco escuro.
- **`--chip-tinta` existe porque a seta do CTA sumia:** o chip do tema escuro é `rgba(255,255,255,.12)` e a seta navy por cima dele dava 1,3:1.

## 2026-08-19 — O acervo virou asset: recorte e traço gerados, não baixados

- **Não havia `rembg` nem `cv2` no ambiente** — só numpy e Pillow. O recorte do braço (`ferramentas/recorte.py`) foi escrito à mão: semente por saturação laranja, crescimento por componente conexo (BFS em fila), tapa-buracos por inundação a partir da borda, morfologia via `MaxFilter`/`MinFilter` do Pillow.
- **O discriminante que resolveu o recorte está no VERDE, não no vermelho.** A placa "ST" do fundo entrava junto com o braço, mas `(r−g) > .28` sozinho comia **26 mil px** das sombras saturadas do próprio braço. O laranja da ABB tem **G nitidamente acima de B** (medido: G−B ≈ .20); o vermelho puro tem G ≈ B. Com `(r−g)>.30 & |g−b|<.05` a placa sai e o braço fica inteiro.
- **E o vermelho só pode barrar o CRESCIMENTO, nunca a máscara final.** Aplicado no fim, ele reabria buracos dentro do braço. A última linha (`tapa_buracos(corpo & ~vermelho)`) resolve os dois casos opostos de uma vez: o que era placa encostada na borda sai; o que era sombra interna vira buraco e volta preenchido.
- **O traço é XDoG, não Sobel** (`ferramentas/linha.py`). Sobel cru devolve granulado; a XDoG devolve traço contínuo que lê como tinta. **Mas a saída crua vem esmagada na base** (medido: p99 = 0,34), o que renderizava cinza-claro. A curva `(x − .06)/(.34 − .06)` elevada a 0,72 reabre a faixa útil — é o que separa "filtro de Photoshop" de "desenho de engenharia".
- **A máscara sai como RGBA branco + alfa, e só em PNG.** Um arquivo serve os dois temas, porque a cor vem do CSS (`mask-image` sobre bloco sólido) ou de um uniform no shader. Gerar AVIF/WebP dela produziu 10 arquivos que nada referenciava.
- **Teto de resolução herdado, e ele continua valendo:** o braço nativo recortado tem **556×485**. O 2× é LANCZOS, não pixel real. Segura no herói a ~560 CSS px, mas **os originais do cliente continuam sendo pré-requisito, não acabamento.**

## 2026-08-19 — Decisões confirmadas com o usuário

1. **Escopo: 9 páginas** — Home + Who We Are, Capabilities, Past Performance, Services, Gallery, Contact + Privacy Policy e Terms.
2. **Tagline aposentado.** "DEDICATED TO EXCEEDING YOUR NEEDS…" sai do site. O H1 do herói passa a ser a tese real: *"Good control strategy beats more expensive instrumentation."* **Fecha a decisão em aberto nº3** do `design.md`.
3. **Caminhos relativos** — `href="css/style.css"`. Nenhuma opção de hospedagem fica eliminada; a armadilha do UnidoCLP não se repete. **Fecha parte da nº6.**
4. **Sem formulário de contato.** Bloco de contato direto: dois telefones, e-mail, WhatsApp, endereço. **Fecha a nº7.**

## 2026-08-19 — Três medidas que mudaram valor de tipo e de camada

- **`--fs-numero` é o ÚNICO valor de tipo que difere do UnidoCLP**, e difere por conta, não por gosto: a faixa aqui tem 5 itens e o mais largo é "150,000+" (~4,11em em Outfit 300). A coluna útil é 230px, logo o teto de tipo é 230/4,11 = **56px**. Em `3.4vw` dá 65px a 1920 e os dois últimos números encostavam. Ficou `clamp(1.875rem, 2.9vw, 3.25rem)`. Lá a faixa tinha 4 itens curtos, por isso o problema não existia.
- **No herói a lente não segue o tema.** O herói é navy nos dois temas; com o papel do tema escuro (`#001427`) sobre ele (`#001D3D`) a revelação dava **1,1:1** e sumia. Fixado em papel claro + tinta navy: **13,6:1**, e lê como prancha de desenho aberta.
- **O shader precisa saber se é `cover` ou `contain`.** A peça recortada usa contain (a silhueta inteira tem de caber); o card retangular usa cover (a foto sangra a moldura). Com contain nos dois, a foto 1:1 do card de água ganhava tarja transparente dentro do slot 4:3.

## 2026-08-19 — Por que existe um gerador em `ferramentas/` sem haver build step

- `site/` continua sendo **HTML estático puro**: publicar a pasta é o deploy inteiro, sem passo nenhum. O gerador (`build_paginas.py` = chrome, `build_site.py` = conteúdo) roda na autoria, não no deploy.
- **Existe porque nav e rodapé são idênticos em nove páginas.** No UnidoCLP eles eram mantidos à mão sob um comentário "sincronizar ao alterar" — que é exatamente como um deles fica para trás. A separação chrome/conteúdo é proposital: os dois mudam por motivos diferentes.
- **O tom de voz foi refeito; os fatos, não.** O site atual do cliente está em jargão que o §4.1 proíbe literalmente ("revolutionize", "cutting-edge", "game-changing", "unparalleled"). Cada fato sobreviveu; a embalagem virou registro declarativo. Nenhum número, nome de cliente ou credencial foi inventado.

---


---

## 2026-08-18 (estado anterior — superado pela entrega de 19/08)

- **Fase:** esqueleto documental. Existem `specs/design.md`, `specs/tipografia.html`, `CLAUDE.md` e este arquivo. **Nenhuma linha do site em si foi escrita ainda.**
- **Próximo passo:** escrever `specs/plano.md` — inventário de conteúdo página a página, redlines e fases de execução. Idioma e paleta já estão confirmados; falta decidir o tagline (§10 do design.md).
- **Não é repositório git ainda.** Enquanto não for, apagar arquivo é irreversível — no UnidoCLP essa foi a razão de arquivos órfãos terem ficado no disco por dias.

## 2026-08-18 (acervo) — 215 imagens do UnidoCLP importadas, e só 5 servem de verdade

- **Tudo baixado para `referencia/universodoclp-assets/`**, preservando a estrutura de pastas do repositório de origem: 215 arquivos, 77,0 MB, os 215 conferidos byte a byte contra o tamanho declarado pela API do GitHub.
- **A triagem inverte a intuição do volume.** Do total, só **0,40 MB (5 arquivos)** é fotografia autoral de campo. O resto: 28,89 MB de banco de imagem identificável pelo nome (`pexels-*`, `michael_pointner-*`, `mrganso-*`, `tylijura-*`), 15,58 MB de fotos de produto sem origem rastreável (aparência de banco: luz de estúdio, modelo posado), 14,72 MB de referência de estilo (o screenshot de 13 MB da zetta-joule), 11,81 MB em 155 derivados de build do site do UnidoCLP, 3,07 MB do herói de lá e 1,74 MB de marca.
- **Descoberta que muda o plano: as 5 fotos de obra própria são da operação americana, não da brasileira.** Elas mostram, uma a uma, exatamente os setores que o site do cliente declara: linha automotiva com robôs alaranjados em body-in-white (bate com Mercedes-Benz/Daimler e BMW), captação de água com tubulação de grande diâmetro (bate com água/esgoto na Flórida), manutenção em cubículo de manobra, comissionamento em estação de comando e bancada de programação de painel. Foram usadas no site brasileiro, mas **o trabalho retratado é o da i3** — o que as torna o material mais valioso do acervo para este projeto, e não uma herança de outro cliente.
- **E vêm com um teto duro: todas são 600×600.** O `memoria.md` do UnidoCLP já registrava que a origem era 600×600 de celular, e lá isso bastava porque o slot era uma faixa de 340px de altura. **Aqui não basta:** um herói full-bleed pede 1800px ou mais, e 600px ampliado a 3x vira papa. Os nomes (`gal-01-qxsbc8l2owvri…`) têm cara de arquivo servido por CDN de site pronto, o que reforça que são versões já reduzidas — **os originais devem existir com o cliente e precisam ser pedidos**.
- **Consequência direta para a ideia do herói com lente de revelação:** o efeito exige foto de resolução alta, porque a lente amplia a atenção sobre uma área pequena e qualquer moleza de pixel aparece ali primeiro. Com 600×600 a interação não se sustenta. **Pedir os originais virou pré-requisito do herói, não item de acabamento.**
- **O que não pode ser usado, e o motivo:** os 14 arquivos de marca do Universo do CLP (`site/brand/*`, `logo*.png`, `fotologo.png`, o banner promocional `bet.png` do curso CLP10) são identidade de outro produto. Ficam no acervo como referência histórica do projeto irmão, nunca como asset do site da i3.
- **Os 155 derivados de `site/img/**` valem quase nada aqui** — são AVIF/WebP/JPEG já recortados e dimensionados para as páginas do UnidoCLP, com conteúdo brasileiro. O valor deles é servir de exemplo do pipeline do `build_images.py` (três formatos por origem, `sizes` casando com o slot), não de imagem para reaproveitar.

## 2026-08-18 (espécime) — A tipografia virou página renderizada

- **`specs/tipografia.html` existe** — espécime vivo do sistema: cada token renderizado no tamanho real, com Outfit, na paleta do projeto. É a §2 do `design.md` deixando de ser tabela e virando prova. Publicado também como artifact privado.
- **O que só o HTML faz e o markdown não:** a escala é toda `clamp()`, então a pergunta útil é "quanto `--fs-display` vale *agora*". A página mede o `font-size` computado de cada amostra e mostra o valor na largura atual da janela, com barra fixa no rodapé. Conferido: a 1920px dá 199,7px (10,4vw, batendo no teto de 200) e a 1568px dá 163,1px — a faixa fluida responde certo, não está travada no máximo.
- **Três defeitos achados só porque abri no navegador**, nenhum visível no código:
  1. **Sem `<meta charset>`, o arquivo local abre em windows-1252** e todo acento quebra ("famÃlia"). O artifact não mostrava isso porque o wrapper declara o charset — **arquivo HTML solto neste projeto precisa do meta explícito**.
  2. **`overflow-x: auto` faz o eixo Y computar para `auto` também.** Como as amostras usam `line-height` .98/1, o glifo estoura o line box e cada linha ganhava uma barra de rolagem vertical espúria. Corrigido com `overflow-y: hidden` + `padding-block: 12px` e `margin-block: -12px` (a margem negativa devolve o ritmo). **Vale para qualquer faixa com tipo grande e entrelinha apertada no site.**
  3. **A demo de peso 700 estava mentindo.** O texto afirma que 700 é falso-negrito sintetizado, mas eu havia pedido `wght@300..700` ao Google Fonts — então vinha o 700 real. Trocado para `300..500`, que é o que o `.woff2` do projeto cobre. Agora a página demonstra de fato o que afirma.
- **Reset que faltava:** `dd` herda `margin-inline-start: 40px` do navegador. O wrapper do artifact tem reset próprio, o arquivo local não — mais um caso de "o mesmo HTML rende diferente nos dois destinos".
- **Os dois temas foram verificados de verdade**, claro e escuro, não só lidos no CSS. Só existe um literal de cor fora dos tokens em toda a folha (`#003566` sobre o badge dourado), e é deliberado: o dourado é o mesmo nos dois temas.

## 2026-08-18 — Fundação: o projeto nasce como variação do UnidoCLP

### O que é este projeto

Site institucional para a **i3Automations & Controls** (i3automations.com), integradora de automação industrial americana. O mesmo cliente já teve um site feito por nós no Brasil — o **Universo do CLP** (github.com/kaeve1/UnidoCLP, no ar em https://universodoclp.pages.dev/). Este projeto é uma **variação daquele sistema de design**, não um projeto novo do zero.

O valor subentendido do entregável é de **R$ 10.000** — o que quer dizer, na prática: nada de placeholder, nada de "depois a gente ajusta", nada de decisão tomada no olho quando dá para medir.

### O que foi herdado e o que foi trocado — e por quê

**Herdado sem alteração: a tipografia inteira.** Pedido explícito do usuário — "quero pegar a tipografia exata e pegar como referência absoluta". Outfit variável 300–500, escala fluida de 9 degraus, pesos e entrelinhas idênticos aos que estão em produção no UnidoCLP. Os valores vieram dos arquivos reais (`site/css/tokens.css` e `site/css/style.css` do repositório), **não de olhar o site renderizado** — o que garante que sejam exatos e não aproximados.

**Trocado: a paleta.** O UnidoCLP tirou o azul `#628AD1` da referência de estilo zetta-joule.com. O i3Automations **já tem marca própria**, e importar um azul emprestado por cima dela seria erro. Então a cor estrutural passa a ser a marca real do cliente.

**Também trocado: o gradiente creme do herói.** No UnidoCLP o herói descia de azul para creme `#FCEEE1` — transição quente, clima otimista, coerente com quem vende treinamento a estudantes. O i3 vende integração industrial e contrato federal. Herói navy sólido ou foto com overlay navy; sem creme.

### As cores da marca foram medidas, não estimadas

Baixei o logo real do site do cliente (`variacao-contorno@2x-8-1-1024x387.png` → salvo em `referencia/i3automations/logo-i3.png`) e contei os pixels por cor:

- **`#003566`** — navy, 44.534 px (contorno do monitor + wordmark)
- **`#FDC500`** — dourado, 23.370 px (tela do monitor / campo do "i3")

As outras cores presentes (`#F7CA3C`, `#EAB306`, `#E0AC0B`, `#FFDC6E`) são **facetas do gradiente em raios da tela**, não cores de sistema. Não entram no site — e ao achatar o ícone elas somem, o que também deixa o PNG muito mais leve (aprendizado direto do UnidoCLP: arte flat com poucas cores únicas cabe numa paleta de 256 e cai ~84% de tamanho).

Nota lateral: `#003566` + `#FDC500` são praticamente dois degraus de uma paleta navy/gold conhecida (`#000814`, `#001D3D`, `#003566`, `#FFC300`, `#FFD60A`) — o que explica por que os tons escuros derivados (`#001D3D`, `#000814`) caem tão bem com o navy medido. Não é coincidência de gosto; a marca do cliente já saiu de lá.

### Todo contraste da paleta foi calculado, nenhum foi escolhido no olho

Rodei a fórmula WCAG em cada par que o site vai usar. Os que importam:

- `#003566` sobre branco = **12,34:1** — o navy pode ser texto de corpo, não só de título.
- `#FDC500` sobre branco = **1,6:1** — **o dourado é ilegível como texto sobre claro.** É o achado mais importante da paleta: ele nunca pode ser cor de letra em fundo claro. Para escrever em dourado sobre claro existe `--dourado-txt: #6B5000` (**7,57:1**).
- `#FDC500` sobre `#003566` = **7,74:1**; sobre `#001D3D` = **10,59:1** — **é sobre navy que o dourado deve viver.** Números de credibilidade, barras de dado, ícones do rodapé.
- `#8FB4DC` sobre `#001D3D` = **7,83:1** — link em bloco escuro. O navy puro não serve de link sobre escuro (some), daí a existência deste token.
- `#40607F` sobre off-white `#F2F5F8` = **6,0:1** — o steel-blue do eyebrow ainda passa AA no fundo alternado, que é o pior caso dele.

### A regra de escassez do accent viajou junto — e ficou mais rígida

No UnidoCLP a regra era "laranja, máximo 2 por dobra". Aqui vale a mesma, e **importa mais**: `#FDC500` é bem mais saturado que o laranja `#F2891F` de lá. Três manchas douradas na mesma tela e o site vira outra coisa. A régua dourada do nav é a exceção deliberada — o nav não conta como dobra, e é o lugar mais barato de assinar a marca.

### O que descobri sobre o cliente que muda o design

- **O site atual é WordPress/Elementor** e as cores no HTML são as do tema padrão (`#ff6900`, `#0693e3`, `#cf2e2e`…). **Não existe paleta real declarada no site** — o único lugar onde a marca vive de verdade é o logo. Por isso a extração de cor foi feita a partir do arquivo de imagem, não do CSS.
- **O comprador público é metade do negócio.** UEI `XUZ4WKEZLS67`, CAGE `9ZJM6`, NAICS primário `541511` (+ 238210, 334513, 335313, 518210, 541330, 541512). Isso não é rodapé burocrático: para quem compra pelo governo, é o conteúdo mais importante da página. Ganhou bloco próprio na estrutura.
- **Os números existem e são bons:** 279+ projetos no mundo, 158+ nos EUA, 78+ na Flórida, **150.000+ tags historiados em PI System**, empresa **desde 2000**. Sede em Lakewood Ranch, Flórida; operação de Oil & Gas em Houston, Texas.
- **A empresa tem uma tese, e ela é melhor que o tagline atual.** No site: *"Good control strategy beats more expensive instrumentation"* e *"Senior control experts know things they do not teach in school."* Contra isso, o tagline oficial — "DEDICATED TO EXCEEDING YOUR NEEDS WITH UNWAVERING COMMITMENT" — é vazio e está em caixa alta. A recomendação é aposentar o tagline e promover a frase de controle a headline de bloco navy. **Falta confirmar com o usuário.**
- **Certificações declaradas:** Ignition Certified, VTScada Certified, Canary Certified. Plataformas: Rockwell, Siemens, Schneider.
- **Clientes nomeados** no site atual: Mercedes-Benz/Daimler, BMW. Setores: Oil & Gas, água/esgoto, papel e celulose, solar/renováveis.
- **Dois telefones, não um:** Sales & Services +1 (407) 820-0299 (também WhatsApp) e Support +1 (941) 666-1880. E-mail `acastro@i3automations.com`. Redes: LinkedIn, Facebook, YouTube, Instagram `@i3automations.plc`.
- **Menu atual a preservar:** Home, Who We Are, Capabilities, Past Performance, Services, Gallery, Contact Us + Privacy Policy e Terms and Conditions.

### Decisões confirmadas com o usuário (2026-08-18)

1. **Idioma: EN-US.** Cliente americano, público americano, conteúdo do site atual em inglês. A documentação interna (este arquivo, design.md, CLAUDE.md) fica em **PT-BR** — quem lê é o usuário e os agentes, não o cliente final.
2. **Paleta navy/dourado da marca real** (`#003566` + `#FDC500`) no lugar do azul `#628AD1` da referência zetta-joule. O usuário escolheu a marca do cliente sobre a cor herdada.

### Ainda em aberto

3. **Aposentar o tagline atual** ("DEDICATED TO EXCEEDING YOUR NEEDS WITH UNWAVERING COMMITMENT") em favor de "Good control strategy beats more expensive instrumentation" — não confirmado.
4. Fotografia real de campo, hospedagem/domínio, formulário de contato e o destino da página "Gallery" — ver `specs/design.md` §10.

### Armadilhas herdadas do UnidoCLP que já valem aqui

Estas custaram tempo lá e estão registradas para não custarem de novo:

- **`animation-fill-mode: backwards` em toda animação com `animation-delay` longo.** Sem ele, durante o atraso o elemento renderiza no estado base — no UnidoCLP isso deixou tocos de linha laranja **parados** na tela por até 6,5 segundos após a página abrir.
- **Caminho absoluto no HTML amarra a hospedagem.** Os 204 `href="/css/..."` do UnidoCLP fizeram o site só funcionar na **raiz de um domínio**, o que eliminou GitHub Pages de projeto de uma vez. Decidir isso **antes** do primeiro arquivo.
- **Cloudflare Pages não devolve 404 por padrão** — qualquer caminho inexistente devolve o `index.html` com **status 200**. Inofensivo em endereço de demonstração; **problema de indexação** no dia em que o domínio real apontar para lá, porque cada URL errada vira uma cópia da home aos olhos do buscador.
- **Endereço de demonstração precisa de `_headers` com `X-Robots-Tag: noindex`** para não competir com o domínio oficial — e esse arquivo **tem que ser apagado** quando o domínio real entrar, ou o site oficial sai do Google.
- **Julgar contraste em JPEG reduzido dá falso negativo.** Compressão esmaga diferenças de poucos níveis. Para qualquer coisa de baixo contraste, medir no PNG original ou recompor a cena offline.
- **Contraste de texto sobre foto/ilustração se mede por média local (12×12), não pixel a pixel.** Pixel a pixel condena letra grande que na verdade lê perfeitamente.
- **Foto de banco ao lado de foto real denuncia a si mesma.** Se só existir banco de imagem para um tema, é melhor não ter a foto.
- **Componente que amarra duração de animação a largura medida em JS** absorve conteúdo novo sem retoque — vale como padrão sempre que houver faixa/esteira.

### Como o material de referência foi obtido

Para quem precisar refazer: `specs/design.md`, `CLAUDE.md`, `memoria.md`, `site/css/tokens.css` e `site/css/style.css` do UnidoCLP vieram de `raw.githubusercontent.com/kaeve1/UnidoCLP/main/`. O logo e o HTML da home do cliente foram baixados de i3automations.com e estão em `referencia/i3automations/`. As cores foram contadas com Pillow; os contrastes, calculados com a fórmula WCAG em Python. **Pillow está disponível no ambiente.**
