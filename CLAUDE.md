# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Overview

"Text Entries": a small FastAPI + PostgreSQL app, run with Docker Compose, that stores user-submitted text and lists it. The README, code comments, UI strings and Gherkin scenarios are in Spanish.

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

Except for `tests/unit/test_sistema.py`, tests need a real PostgreSQL; there is no SQLite fallback.

## Architecture

Hexagonal (ports and adapters):

- `app/hexagon/` is the business core: the `Entry` object, domain errors, the outbound port `EntryRepository` (`ports.py`) and the `Sistema` facade, the only entry point into the core. It must not import FastAPI, SQLAlchemy, Pydantic or anything from `app/adapters`.
- `app/adapters/persistence/` implements the port: `SqlAlchemyEntryRepository` (maps the ORM `EntryModel` to the domain `Entry`) and `InMemoryEntryRepository`.
- `app/bootstrap.py` is the composition root, the only place that picks which adapter backs each port.
- `app/main.py` is a pure HTTP controller. Routes get `Sistema` through `Depends(get_sistema)` and translate domain errors into HTTP responses; business logic and database access do not belong there. `app/schemas.py` holds the HTTP DTOs.

Two interfaces go through the same facade: HTML forms (`GET`/`POST /` rendering `app/templates/index.html`, plus `POST /entries/{id}/delete`, which redirects to `/`) and a JSON API (`GET`/`POST /entries`, `DELETE /entries/{id}`). `/health` and `/version` are also there.

Tests: `tests/unit/test_sistema.py` exercises the core with the in-memory adapter and needs no database; `tests/unit/test_api.py`, `tests/integration/` and the behave scenarios use real PostgreSQL. Only tests requesting the `client` or `clean_tables` fixtures touch the database.

- `engine` is created at import time from `DATABASE_URL`, so the variable must be set before anything imports `app.main` or the persistence adapter. This is why `tests/conftest.py` and `tests/acceptance/features/environment.py` set it above their imports.
- There are no migrations. The schema comes from `init_db()` (`create_all`, run in the app lifespan through `bootstrap.init_infrastructure()`), which does not alter existing tables; a model change needs the table or the `db_data` volume recreated.
- The tests use `TestClient` without a context manager, so the lifespan does not run; the test setup creates the tables itself.
- The templates directory is a relative path (`app/templates`), so the app and tests must run from the repository root.
- The version string is repeated in `docker-compose.yml` (`APP_VERSION`), the default in `app/main.py`, `tests/conftest.py`, `environment.py`, and the assertions in `test_api.py` and `text_entry.feature`. Change them together.
