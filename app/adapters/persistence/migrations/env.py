# Entorno de Alembic: conecta las migraciones con la base y los modelos de la aplicacion.
from logging.config import fileConfig

from alembic import context

from app.adapters.persistence import models  # noqa: F401  (registra los modelos en Base)
from app.adapters.persistence.database import Base, engine

if context.config.config_file_name is not None:
    fileConfig(context.config.config_file_name, disable_existing_loggers=False)

if context.is_offline_mode():
    raise RuntimeError("Las migraciones requieren una conexion a la base; el modo --sql no esta soportado.")

with engine.connect() as connection:
    context.configure(connection=connection, target_metadata=Base.metadata)
    with context.begin_transaction():
        context.run_migrations()
