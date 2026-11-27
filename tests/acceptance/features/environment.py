import os

os.environ.setdefault("DATABASE_URL", "postgresql+psycopg2://app:app@localhost:5433/appdb_test")

from fastapi.testclient import TestClient

from app.main import app
from tests.database import reset_database


def before_scenario(context, scenario):
    reset_database()
    context.client = TestClient(app)


def after_scenario(context, scenario):
    reset_database()
