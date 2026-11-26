import os
import pytest

os.environ.setdefault("DATABASE_URL", "postgresql+psycopg2://app:app@localhost:5433/appdb_test")
os.environ.setdefault("APP_VERSION", "10.3")

from fastapi.testclient import TestClient

from app.adapters.persistence.database import Base, engine, init_db
from app.main import app


# Solo los tests que piden este fixture necesitan una base de datos.
@pytest.fixture
def clean_tables():
    Base.metadata.drop_all(bind=engine)
    init_db()
    yield
    Base.metadata.drop_all(bind=engine)


@pytest.fixture
def client(clean_tables):
    return TestClient(app)
