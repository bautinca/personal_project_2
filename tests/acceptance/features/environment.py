import os

os.environ.setdefault("DATABASE_URL", "postgresql+psycopg2://app:app@localhost:5433/appdb_test")

from fastapi.testclient import TestClient

from app.adapters.persistence.database import Base, engine, init_db
from app.main import app

init_db()


def before_scenario(context, scenario):
    Base.metadata.drop_all(bind=engine)
    init_db()
    context.client = TestClient(app)


def after_scenario(context, scenario):
    Base.metadata.drop_all(bind=engine)
    init_db()
