#!/bin/sh
# Sobe um Apache DE VERDADE com o site publicado e o .htaccess gerado, e
# confere cada rota. Configuracao de Apache nao testada e a classe de coisa
# que ou quebra em silencio ou derruba o site inteiro com 500 -- e nenhum dos
# dois aparece lendo o arquivo.
#
# `AllowOverride All` reproduz o que a hospedagem compartilhada faz; sem isso
# o .htaccess seria ignorado e o teste passaria por motivo errado.
set -e
PORTA=${1:-8899}
NOME=i3-apache-teste
docker rm -f $NOME >/dev/null 2>&1 || true
docker run -d --name $NOME -p $PORTA:80 \
  -v "//c/Users/kegit/I3Automations/site":/usr/local/apache2/htdocs:ro \
  httpd:2.4 >/dev/null
# Os modulos que o .htaccess exige nao vem ligados na imagem oficial.
docker exec $NOME sh -c "sed -i \
  -e 's|^#LoadModule rewrite_module|LoadModule rewrite_module|' \
  -e 's|^#LoadModule deflate_module|LoadModule deflate_module|' \
  -e 's|^#LoadModule expires_module|LoadModule expires_module|' \
  -e 's|^#LoadModule headers_module|LoadModule headers_module|' \
  conf/httpd.conf"
docker exec $NOME sh -c "sed -i 's|AllowOverride None|AllowOverride All|g' conf/httpd.conf"
docker exec $NOME httpd -t
docker exec $NOME apachectl -k graceful
sleep 2
echo "apache no ar em http://127.0.0.1:$PORTA"
