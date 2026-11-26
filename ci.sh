#!/usr/bin/env bash
# Simula un pipeline de CI: linter -> tests unitarios y de integracion -> tests de aceptacion.
# Se detiene en la primera etapa que falla y termina con un codigo de salida distinto de 0.
set -euo pipefail

cd "$(dirname "${BASH_SOURCE[0]}")"

# Los tests borran todas las tablas: SIEMPRE deben correr contra la base de testing.
TEST_DATABASE_URL="postgresql+psycopg2://app:app@db_test:5432/appdb_test"

STAGE="preparacion"
STARTED_DB_TEST=false

run_in_app() {
    docker compose run --rm --no-deps -T -e DATABASE_URL="$TEST_DATABASE_URL" app "$@"
}

stage() {
    STAGE="$1"
    printf '\n==> %s\n' "$STAGE"
}

finish() {
    local exit_code=$?
    # Solo se detiene la base de testing si la levanto este script.
    if [ "$STARTED_DB_TEST" = true ]; then
        docker compose stop db_test >/dev/null 2>&1 || true
    fi
    if [ "$exit_code" -eq 0 ]; then
        printf '\nPIPELINE OK\n'
    else
        printf '\nPIPELINE FALLIDO en la etapa: %s (codigo %s)\n' "$STAGE" "$exit_code"
    fi
}
trap finish EXIT

stage "preparacion"
docker compose build app
if [ -z "$(docker compose ps --status running -q db_test)" ]; then
    STARTED_DB_TEST=true
fi
docker compose up -d db_test
# Se consulta por TCP porque, mientras Postgres se inicializa, todavia no acepta conexiones de red.
for attempt in $(seq 1 30); do
    if docker compose exec -T db_test pg_isready -h 127.0.0.1 -U app -d appdb_test >/dev/null 2>&1; then
        break
    fi
    if [ "$attempt" -eq 30 ]; then
        echo "La base de testing no respondio a tiempo."
        exit 1
    fi
    sleep 1
done

stage "1/3 linter (ruff)"
run_in_app ruff check --no-cache .

stage "2/3 tests unitarios y de integracion (pytest)"
run_in_app pytest

stage "3/3 tests de aceptacion (behave)"
run_in_app behave
