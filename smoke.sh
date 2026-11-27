#!/usr/bin/env bash
# Smoke test: comprueba que una instancia desplegada responda y tenga la version esperada.
# Solo hace peticiones GET: no crea ni borra datos.
#
# Uso: ./smoke.sh <url> [version]
#   Si no se indica la version, se usa la del archivo VERSION.
#   Reintentos de la version: SMOKE_ATTEMPTS (20) y SMOKE_DELAY en segundos (10).
set -euo pipefail

if [ "$#" -lt 1 ] || [ "$#" -gt 2 ]; then
    echo "Uso: $0 <url> [version]" >&2
    exit 2
fi

base_url="${1%/}"
expected="${2:-$(tr -d '[:space:]' < "$(dirname "${BASH_SOURCE[0]}")/VERSION")}"
attempts="${SMOKE_ATTEMPTS:-20}"
delay="${SMOKE_DELAY:-10}"

fail() {
    echo "SMOKE TEST FALLIDO: $1" >&2
    exit 1
}

request() {
    curl -sS --fail --max-time 60 "$@"
}

# $1: ruta a consultar; $2: filtro jq que la respuesta tiene que cumplir.
check_json() {
    request --retry 3 "$base_url$1" | jq -e "$2" > /dev/null || fail "$1 no respondio lo esperado"
    echo "OK    $1"
}

echo "Smoke test de $base_url (version esperada: $expected)"

# Se reintenta porque puede haber una demora hasta que el trafico pase a la version nueva.
actual="sin respuesta"
for attempt in $(seq 1 "$attempts"); do
    actual=$(request "$base_url/version" | jq -r '.version') || actual="sin respuesta"
    echo "Intento $attempt: version desplegada $actual"
    if [ "$actual" = "$expected" ]; then
        break
    fi
    if [ "$attempt" -lt "$attempts" ]; then
        sleep "$delay"
    fi
done
[ "$actual" = "$expected" ] || fail "se esperaba la version $expected y la ultima respuesta fue: $actual"
echo "OK    /version"

check_json /health '.status == "ok"'
# Listar las entradas confirma que la aplicacion llega a la base de datos.
check_json /entries 'type == "array"'
request --retry 3 -o /dev/null "$base_url/" || fail "/ no respondio"
echo "OK    /"

echo "SMOKE TEST OK"
