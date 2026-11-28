import os

os.environ.setdefault("DATABASE_URL", "postgresql+psycopg2://app:app@localhost:5433/appdb_test")

from fastapi.testclient import TestClient

from app.adapters.persistence.database import SessionLocal
from app.adapters.persistence.sql_entry_repository import SqlAlchemyEntryRepository
from app.adapters.translation.fake_translator import FakeTranslator
from app.bootstrap import get_sistema
from app.hexagon.sistema import Sistema
from app.main import app
from tests.database import reset_database


def before_scenario(context, scenario):
    reset_database()
    # Traductor falso: los escenarios no llaman a MyMemory.
    context.translator = FakeTranslator()
    app.dependency_overrides[get_sistema] = lambda: Sistema(SqlAlchemyEntryRepository(SessionLocal), context.translator)
    context.client = TestClient(app)


def after_scenario(context, scenario):
    app.dependency_overrides.clear()
    reset_database()
