import os
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, declarative_base

DATABASE_URL = os.getenv("DATABASE_URL", "postgresql+psycopg2://app:app@localhost:5432/appdb") # Obtenemos la URL de la base de datos de desarrollo local desde la variable de entorno DATABASE_URL, si no está definida, usamos la URL por defecto para PostgreSQL.

engine = create_engine(DATABASE_URL, pool_pre_ping=True)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base() # Clase base de la que heredan los modelos ORM


# Crea las tablas definidas en los modelos ORM si no existen.
def init_db():
    from . import models  # noqa: F401  (registra los modelos en Base antes de crear las tablas)

    Base.metadata.create_all(bind=engine)
