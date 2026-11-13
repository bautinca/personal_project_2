import os

os.environ.setdefault("DATABASE_URL", "postgresql+psycopg2://app:app@localhost:5433/appdb_test")
os.environ.setdefault("APP_VERSION", "10.3")

from fastapi.testclient import TestClient
from app.database import Base, engine
from app.main import app

Base.metadata.create_all(bind=engine)


def before_scenario(context, scenario):
    Base.metadata.drop_all(bind=engine)
    Base.metadata.create_all(bind=engine)
    context.client = TestClient(app)


def after_scenario(context, scenario):
    Base.metadata.drop_all(bind=engine)
    Base.metadata.create_all(bind=engine)
