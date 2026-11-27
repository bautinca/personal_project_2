import os

import pytest

os.environ.setdefault("DATABASE_URL", "postgresql+psycopg2://app:app@localhost:5433/appdb_test")

from fastapi.testclient import TestClient

from app.main import app
from tests.database import drop_database, reset_database


# Solo los tests que piden este fixture necesitan una base de datos.
@pytest.fixture
def clean_tables():
    reset_database()
    yield
    drop_database()


@pytest.fixture
def client(clean_tables):
    return TestClient(app)
