#!/bin/sh
# Publica no Cloudflare Pages, GRATUITO, como endereco de DEMONSTRACAO.
#
# Duas coisas acontecem aqui que nao acontecem no deploy da HostGator, e as
# duas sao obrigatorias:
#
#   1. O build roda com `--demo`, que poe `X-Robots-Tag: noindex` no _headers.
#      Sem isso a copia em *.pages.dev COMPETE com i3automations.com no
#      buscador -- duas URLs, mesmo conteudo, e quem escolhe e o Google.
#
#   2. O `.htaccess` NAO sobe. Ele e do Apache e inerte aqui, mas o Pages o
#      SERVE: medido, `/.htaccess` respondia 200 e entregava a configuracao de
#      servidor inteira. O `_redirects` nao consegue esconde-lo (arquivo que
#      existe vence a regra), entao ele sai do pacote -- que e o jeito certo:
#      o artefato e preparado para a plataforma de destino.
set -e
PROJETO=${1:-i3automations}
RAIZ=$(cd "$(dirname "$0")/.." && pwd)
PACOTE="${TEMP:-/tmp}/publicar-$PROJETO"

echo "== build em modo demonstracao =="
python "$RAIZ/ferramentas/build_site.py" --demo | tail -3

echo "== preparando o pacote (sem o .htaccess) =="
rm -rf "$PACOTE"
cp -r "$RAIZ/site" "$PACOTE"
rm -f "$PACOTE/.htaccess"
echo "   $(find "$PACOTE" -type f | wc -l) arquivos"

echo "== publicando =="
npx --yes wrangler@4 pages deploy "$PACOTE" \
  --project-name "$PROJETO" --branch main --commit-dirty=true 2>&1 | tail -4

rm -rf "$PACOTE"
echo
echo "== conferindo o que so o ar responde =="
sleep 6
B="https://$PROJETO.pages.dev"
printf "   noindex .......... "; curl -sSI --max-time 30 "$B/" | tr -d '\r' | grep -i x-robots-tag || echo "AUSENTE -- PARE"
printf "   /.htaccess ....... "; curl -sS -o /dev/null -w "%{http_code} (esperado 404)\n" --max-time 30 "$B/.htaccess"
printf "   sem laco ......... "; curl -sSL --max-time 40 -o /dev/null -w "%{num_redirects} saltos, final %{http_code}\n" "$B/who-we-are.html"
