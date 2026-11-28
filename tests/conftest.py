import os

import pytest

os.environ.setdefault("DATABASE_URL", "postgresql+psycopg2://app:app@localhost:5433/appdb_test")

from fastapi.testclient import TestClient

from app.adapters.persistence.database import SessionLocal
from app.adapters.persistence.sql_entry_repository import SqlAlchemyEntryRepository
from app.adapters.translation.fake_translator import FakeTranslator
from app.bootstrap import get_sistema
from app.hexagon.sistema import Sistema
from app.main import app
from tests.database import drop_database, reset_database


# Solo los tests que piden este fixture necesitan una base de datos.
@pytest.fixture
def clean_tables():
    reset_database()
    yield
    drop_database()


@pytest.fixture
def translator():
    return FakeTranslator()


# La app usa la base de testing pero un traductor falso: los tests no llaman a MyMemory.
@pytest.fixture
def client(clean_tables, translator):
    app.dependency_overrides[get_sistema] = lambda: Sistema(SqlAlchemyEntryRepository(SessionLocal), translator)
    yield TestClient(app)
    app.dependency_overrides.clear()
