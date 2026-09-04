#!/bin/sh
# Confere cada rota contra um Apache real servindo o .htaccess gerado.
# Ver testar_htaccess.sh para subir o container.
B=${1:-https://127.0.0.1:8443}
pass=0; fail=0
c() { # caminho, codigo esperado, destino esperado (ou "-")
  r=$(curl -sk -o /dev/null -w "%{http_code}|%{redirect_url}" "$B$1")
  cod=${r%%|*}; dest=${r#*|}; dest=${dest#*://*/}; dest="/$dest"
  [ "$3" = "-" ] && dest="-"
  if [ "$cod" = "$2" ] && { [ "$3" = "-" ] || [ "$dest" = "$3" ]; }; then
    pass=$((pass+1)); printf "  ok   %-30s %s %s\n" "$1" "$cod" "$3"
  else
    fail=$((fail+1)); printf "  FALHA %-29s esperado %s %s / veio %s %s\n" "$1" "$2" "$3" "$cod" "$dest"
  fi
}
echo "== URLs do WordPress -> 301 =="
c /who-we-are/ 301 /who-we-are.html
c /who-we-are 301 /who-we-are.html
c /capabilities/ 301 /capabilities.html
c /past-performance/ 301 /past-performance.html
c /services/ 301 /services.html
c /gallery/ 301 /gallery.html
c /contact-us/ 301 /contact.html
c /privacy-policy/ 301 /privacy-policy.html
c /terms-and-conditions/ 301 /terms-and-conditions.html
c /home/ 301 /
c /index.html 301 /
echo "== restos do WordPress -> 410 =="
c /feed/ 410 -
c /wp-json/ 410 -
c /xmlrpc.php 410 -
c /wp-admin/ 410 -
echo "== paginas servidas -> 200 =="
c / 200 -
c /who-we-are.html 200 -
c /past-performance.html 200 -
c /contact.html 200 -
c /css/style.css 200 -
c /favicon.ico 200 -
c /site.webmanifest 200 -
echo "== caminho inexistente -> 404 =="
c /nao-existe 404 -
c /nao-existe.html 404 -
echo "== listagem de diretorio bloqueada =="
c /img/ 403 -
echo
echo "$pass ok, $fail falhas"
[ "$fail" = 0 ] || exit 1
