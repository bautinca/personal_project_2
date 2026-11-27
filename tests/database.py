# Utilidades de base de datos compartidas por pytest y behave. BORRAN TODOS LOS DATOS.
from pathlib import Path

from alembic import command
from alembic.config import Config
from sqlalchemy import text

from app.adapters.persistence.database import Base, engine

ALEMBIC_INI = Path(__file__).resolve().parent.parent / "alembic.ini"


def alembic_config() -> Config:
    return Config(str(ALEMBIC_INI))


def drop_database() -> None:
    Base.metadata.drop_all(bind=engine)
    with engine.begin() as connection:
        connection.execute(text("DROP TABLE IF EXISTS alembic_version"))


# El esquema de los tests se crea con las mismas migraciones que usa produccion.
def reset_database() -> None:
    drop_database()
    command.upgrade(alembic_config(), "head")
