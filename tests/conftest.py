import os
import pytest

os.environ.setdefault("DATABASE_URL", "postgresql+psycopg2://app:app@localhost:5433/appdb_test")
os.environ.setdefault("APP_VERSION", "10.3")

from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from app.database import Base, engine
from app.main import app

# ensure tables
Base.metadata.create_all(bind=engine)


@pytest.fixture(autouse=True)
def clean_tables():
    Base.metadata.drop_all(bind=engine)
    Base.metadata.create_all(bind=engine)
    yield
    Base.metadata.drop_all(bind=engine)


@pytest.fixture
def client():
    return TestClient(app)
