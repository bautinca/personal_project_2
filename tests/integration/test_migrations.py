import pytest
from alembic import command
from sqlalchemy import inspect, text

from app.adapters.persistence.database import engine
from tests.database import alembic_config, drop_database


@pytest.fixture
def empty_database():
    drop_database()
    yield
    drop_database()


def table_names():
    return set(inspect(engine).get_table_names())


def test_models_match_migrations(clean_tables):
    # Falla si se cambio un modelo y no se creo la migracion correspondiente.
    command.check(alembic_config())


def test_upgrade_and_downgrade(empty_database):
    command.upgrade(alembic_config(), "head")
    assert "entries" in table_names()

    command.downgrade(alembic_config(), "base")
    assert "entries" not in table_names()

    command.upgrade(alembic_config(), "head")
    assert "entries" in table_names()


def test_upgrade_keeps_data_of_a_database_previous_to_alembic(empty_database):
    # Reproduce el estado de produccion: la tabla ya existe y tiene datos, pero no hay historial de Alembic.
    with engine.begin() as connection:
        connection.execute(text("CREATE TABLE entries (id SERIAL PRIMARY KEY, text TEXT NOT NULL)"))
        connection.execute(text("CREATE INDEX ix_entries_id ON entries (id)"))
        connection.execute(text("INSERT INTO entries (text) VALUES ('dato existente')"))

    command.upgrade(alembic_config(), "head")

    with engine.connect() as connection:
        assert connection.execute(text("SELECT text FROM entries")).scalars().all() == ["dato existente"]
    command.check(alembic_config())
