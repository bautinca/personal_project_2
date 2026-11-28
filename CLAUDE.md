# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Overview

"Text Entries": a small FastAPI + PostgreSQL app, run with Docker Compose, that stores user-submitted text, lists it and translates it to English through the MyMemory API. The README, code comments, UI strings and Gherkin scenarios are in Spanish.

## Commands

```bash
docker compose up --build        # app on http://localhost:8000, db on 5432, db_test on 5433
docker compose restart app       # needed after code changes: the source is mounted, but uvicorn runs without --reload
docker compose up --build app    # needed after changing requirements.txt
```

Lint and format with ruff (configured in `ruff.toml`; the containers must be running):

```bash
docker compose exec app ruff check .          # add --fix to apply safe fixes
docker compose exec app ruff format .         # add --diff to preview
```

`./ci.sh` (run on the host) is the local CI pipeline: ruff, then pytest, then behave, always against `db_test`, stopping at the first failing stage. GitHub Actions (`.github/workflows/ci.yml`) runs the same three stages on pushes and pull requests to `main`, but independently of the script: it installs dependencies natively on the runner with a PostgreSQL service container. Change both when the stages change.

### Tests

**Both test suites drop all tables in whatever `DATABASE_URL` points to.** The `app` container sets it to the development database, and the test setup only applies its own default when the variable is unset. A plain `docker compose exec app pytest` (as shown in the README) therefore wipes development data. Override it:

```bash
TEST_DB=postgresql+psycopg2://app:app@db_test:5432/appdb_test

# pytest (tests/unit and tests/integration)
docker compose exec -e DATABASE_URL=$TEST_DB app pytest
docker compose exec -e DATABASE_URL=$TEST_DB app pytest tests/unit/test_api.py::test_health

# acceptance (behave)
docker compose exec -e DATABASE_URL=$TEST_DB app behave
docker compose exec -e DATABASE_URL=$TEST_DB app behave -n "Health endpoint"   # single scenario by name
```

From the host (with dependencies installed and `db_test` running via `docker compose up -d db_test`), plain `pytest` and `behave` default to `localhost:5433/appdb_test`, provided `DATABASE_URL` is not set in the shell.

Except for `tests/unit/test_sistema.py` and `tests/unit/test_my_memory_translator.py`, tests need a real PostgreSQL; there is no SQLite fallback.

## Deployment

Pushing any tag runs `.github/workflows/deploy.yml`: it fails unless the tag equals the contents of `VERSION`, then reuses `ci.yml` (`workflow_call`), then triggers a Render deploy hook for the tagged commit and polls the Render API until it is live or fails. A final `smoke` job runs `./smoke.sh <url> [version]` against `PRODUCTION_URL` (set in the workflow); the script sends read-only requests and requires `/version` to equal `VERSION` and `/health`, `/entries` and `/` to respond. Production is the Docker service in `render.yaml` (auto-deploy off) with PostgreSQL on Supabase (session pooler, `DATABASE_URL` set only in Render). The container listens on `$PORT`, default 8000. Setup steps are in the README.

## Architecture

Hexagonal (ports and adapters):

- `app/hexagon/` is the business core: the `Entry` object, domain errors, the outbound ports `EntryRepository` and `Translator` (`ports.py`) and the `Sistema` facade, the only entry point into the core. It must not import FastAPI, SQLAlchemy, Pydantic or anything from `app/adapters`.
- `app/adapters/persistence/` implements the port: `SqlAlchemyEntryRepository` (maps the ORM `EntryModel` to the domain `Entry`) and `InMemoryEntryRepository`.
- `app/adapters/translation/` implements `Translator`: `MyMemoryTranslator` (external API, no key, 500 bytes per query, may report errors inside an HTTP 200 body) and `FakeTranslator`. Tests must never call the real API: the `client` fixture and behave's `environment.py` override `get_sistema` with the fake.
- `app/bootstrap.py` is the composition root, the only place that picks which adapter backs each port.
- `app/main.py` is a pure HTTP controller. Routes get `Sistema` through `Depends(get_sistema)` and translate domain errors into HTTP responses; business logic and database access do not belong there. `app/schemas.py` holds the HTTP DTOs.

The only user interface is the website: HTML forms (`GET`/`POST /` rendering `app/templates/index.html`, plus `POST /entries/{id}/edit` and `POST /entries/{id}/delete`; those form POSTs answer with a 303 redirect to `/`, so reloading never resubmits; the exception is `POST /entries/{id}/translate`, which renders the page directly because translations are never stored). `/health`, `/version` and the read-only `GET /entries` exist for the smoke test and tests. Do not add JSON API routes unless asked: new features only get the routes the website uses.

Tests: `tests/unit/test_sistema.py` exercises the core with the in-memory adapter and needs no database; `tests/unit/test_api.py`, `tests/integration/` and the behave scenarios use real PostgreSQL. Only tests requesting the `client` or `clean_tables` fixtures touch the database.

- `engine` is created at import time from `DATABASE_URL`, so the variable must be set before anything imports `app.main` or the persistence adapter. This is why `tests/conftest.py` and `tests/acceptance/features/environment.py` set it above their imports.
- Schema changes go through Alembic (`alembic.ini`, `app/adapters/persistence/migrations/`). The Dockerfile `CMD` runs `alembic upgrade head` before uvicorn; the app itself never creates tables. After editing `models.py`, generate a revision with `docker compose exec --user "$(id -u):$(id -g)" app alembic revision --autogenerate -m "..."` and review it; `tests/integration/test_migrations.py` fails if models and migrations differ. Revision `0001` skips creation when `entries` already exists (databases that predate Alembic).
- Tests build the schema by running the migrations (`tests/database.py`, shared by pytest and behave).
- The templates directory is a relative path (`app/templates`), so the app and tests must run from the repository root.
- The version is set by hand in the root `VERSION` file (`X.Y.Z`), read once at startup through `app/version.py`. There is no `APP_VERSION` variable, and tests compare against the file.
