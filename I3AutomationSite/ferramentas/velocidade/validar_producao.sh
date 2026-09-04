#!/bin/sh
# Confere um site JA NO AR, do lado de fora. Roda depois da troca -- e tambem
# antes, contra o subdominio de ensaio.
#
# Por que existir, se rotas.sh ja testa o .htaccess: aquele roda contra um
# Apache de container, com o arquivo que ESTA no disco aqui. Este roda contra
# o servidor de verdade, com o arquivo que foi realmente enviado, atras do
# certificado de verdade e do CDN de verdade. Sao perguntas diferentes: um
# valida a configuracao, o outro valida a PUBLICACAO.
#
#   sh validar_producao.sh https://i3automations.com i3
#   sh validar_producao.sh https://i3automations.pages.dev i3
#   sh validar_producao.sh https://universodoclp.com.br clp
#
# A PLATAFORMA E DETECTADA, e ela muda o que e certo -- nao so o que e bonito:
#
#   .html ..... o Cloudflare Pages canonicaliza `/x.html` para `/x` com 308,
#               e nao ha como desligar. Em Apache `/x.html` responde 200 direto.
#   410 ....... o `_redirects` do Pages aceita ate 404; o Apache emite 410.
#   MX ........ um subdominio `*.pages.dev` nao tem e-mail, e nao deveria ter.
#
# Sem isso o validador reprova diferenca de plataforma como se fosse defeito --
# e um relatorio com falha falsa e um relatorio que ninguem le ate o fim.
set -u
B=${1:-}
PERFIL=${2:-i3}
[ -z "$B" ] && { echo "uso: sh validar_producao.sh <https://dominio> [i3|clp]"; exit 1; }
B=${B%/}
case "$B" in *.pages.dev*) PLAT=pages ;; *) PLAT=apache ;; esac
echo "plataforma detectada: $PLAT"

ok=0; falha=0
c() { # caminho, codigo esperado, destino esperado ("-" = nao confere)
  r=$(curl -sS -o /dev/null -w "%{http_code}|%{redirect_url}" --max-time 25 "$B$1" 2>/dev/null)
  cod=${r%%|*}; dest=${r#*|}
  # so o caminho do destino interessa, nao o dominio
  dcam=$(printf '%s' "$dest" | sed -e 's|^https\{0,1\}://[^/]*||')
  [ -z "$dcam" ] && dcam="-"
  if [ "$cod" = "$2" ] && { [ "$3" = "-" ] || [ "$dcam" = "$3" ]; }; then
    ok=$((ok+1)); printf "  ok    %-34s %s\n" "$1" "$cod"
  else
    falha=$((falha+1))
    printf "  FALHA %-34s esperado %s %s / veio %s %s\n" "$1" "$2" "$3" "$cod" "$dcam"
  fi
}
cab() { # caminho, cabecalho, trecho esperado
  v=$(curl -sSI --max-time 25 "$B$1" 2>/dev/null | tr -d '\r' | grep -i "^$2:" | head -1)
  case "$v" in
    *"$3"*) ok=$((ok+1)); printf "  ok    %-34s %s\n" "$1" "$(printf '%s' "$v" | cut -c1-52)" ;;
    *) falha=$((falha+1)); printf "  FALHA %-34s %s deveria conter '%s' / veio '%s'\n" "$1" "$2" "$3" "$v" ;;
  esac
}

echo "== $B =="
echo "-- paginas respondem --"
c / 200 -
if [ "$PERFIL" = "i3" ]; then
  for p in who-we-are capabilities past-performance services gallery contact \
           privacy-policy terms-and-conditions; do
    if [ "$PLAT" = pages ]; then
      # o Pages tira o .html sozinho: o certo aqui e 308 para a forma curta,
      # e a forma curta responder 200
      c "/$p.html" 308 "/$p"
      c "/$p" 200 -
    else
      c "/$p.html" 200 -
    fi
  done
  echo "-- URLs antigas do WordPress redirecionam (301) --"
  if [ "$PLAT" = pages ]; then EXT=""; else EXT=".html"; fi
  c /who-we-are/ 301 "/who-we-are$EXT"
  c /capabilities/ 301 "/capabilities$EXT"
  c /past-performance/ 301 "/past-performance$EXT"
  c /services/ 301 "/services$EXT"
  c /gallery/ 301 "/gallery$EXT"
  c /contact-us/ 301 "/contact$EXT"
  c /privacy-policy/ 301 "/privacy-policy$EXT"
  c /terms-and-conditions/ 301 "/terms-and-conditions$EXT"
  c /home/ 301 /
  # a forma SEM barra so tem regra em Apache: no Pages ela e a URL canonica e
  # uma regra ali criaria laco com o 308 dele -- ver build_paginas.py
  if [ "$PLAT" = apache ]; then
    c /who-we-are 301 /who-we-are.html
    c /index.html 301 /
  else
    c /who-we-are 200 -
    c /index.html 308 /
  fi
  AVIF=/img/setores/agua-600.avif
else
  for p in quem-somos trabalhos-realizados treinamentos contato; do c "/$p/" 200 -; done
  echo "-- as URLs do UnidoCLP NAO mudam: nada aqui deve redirecionar --"
  AVIF=$(curl -sS --max-time 25 "$B/" 2>/dev/null | grep -o '/img/[^" ]*\.avif' | head -1)
  [ -z "$AVIF" ] && AVIF=/img/nao-achei.avif
fi

if [ "$PLAT" = apache ]; then
  echo "-- restos do WordPress saem do indice (410) --"
  c /feed/ 410 -
  c /wp-json/ 410 -
  c /xmlrpc.php 410 -
else
  echo "-- restos do WordPress saem do indice (404: o Pages nao emite 410) --"
  c /feed/ 404 -
  c /wp-json/ 404 -
  c /xmlrpc.php 404 -
fi
if [ "$PLAT" = pages ]; then
  echo "-- protecao de demonstracao --"
  # sem isto a copia em pages.dev compete com o dominio oficial no buscador
  cab / x-robots-tag noindex
  # o .htaccess e do Apache e nao deve subir para ca -- ele seria SERVIDO
  c /.htaccess 404 -
fi

echo "-- caminho inexistente da 404 DE VERDADE --"
# 200 aqui e o defeito de indexacao: cada URL errada vira uma copia da home
c /caminho-que-nao-existe-xyz 404 -

echo "-- portas do buscador --"
c /sitemap.xml 200 -
c /robots.txt 200 -
c /favicon.ico 200 -

echo "-- tipo MIME do AVIF (sem isto o site fica sem fotografia) --"
cab "$AVIF" content-type image/avif

echo "-- compressao de texto --"
g=$(curl -sS -H "Accept-Encoding: gzip" -o /dev/null -w '%{size_download}' --max-time 25 "$B/css/style.css" 2>/dev/null)
n=$(curl -sS -o /dev/null -w '%{size_download}' --max-time 25 "$B/css/style.css" 2>/dev/null)
if [ "${g:-0}" -gt 0 ] && [ "${n:-0}" -gt "${g:-0}" ]; then
  ok=$((ok+1)); printf "  ok    %-34s %s -> %s bytes\n" "/css/style.css" "$n" "$g"
else
  falha=$((falha+1)); printf "  FALHA %-34s sem compressao (gzip %s, cru %s)\n" "/css/style.css" "${g:-?}" "${n:-?}"
fi

echo "-- cache de imagem --"
cab "$AVIF" cache-control max-age=31536000

echo "-- canonica: https e sem www --"
c_http=$(curl -sS -o /dev/null -w '%{http_code}' --max-time 25 "$(printf '%s' "$B" | sed 's|^https|http|')/" 2>/dev/null)
case "$c_http" in 301|308) ok=$((ok+1)); echo "  ok    http -> https                      $c_http" ;;
  *) falha=$((falha+1)); echo "  FALHA http nao redireciona para https (veio $c_http)" ;; esac

if [ "$PLAT" = pages ]; then
  echo "-- MX: nao se aplica a um subdominio *.pages.dev --"
else
echo "-- o e-mail continua de pe (MX intactos) --"
dom=$(printf '%s' "$B" | sed -e 's|^https\{0,1\}://||' -e 's|/.*||' -e 's|^www\.||' -e 's|^novo\.||')
mx=$(nslookup -type=MX "$dom" 8.8.8.8 2>/dev/null | grep -ci 'mail exchanger')
if [ "${mx:-0}" -gt 0 ]; then
  ok=$((ok+1)); echo "  ok    MX de $dom respondendo ($mx registros)"
else
  falha=$((falha+1)); echo "  FALHA nenhum MX para $dom -- O E-MAIL PODE ESTAR FORA"
fi
fi

echo
echo "$ok ok, $falha falhas"
[ "$falha" = 0 ] || exit 1
