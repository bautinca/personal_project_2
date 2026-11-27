# Raiz de composicion: el unico lugar donde se decide que adaptador se conecta a cada puerto.
from app.adapters.persistence.database import SessionLocal
from app.adapters.persistence.sql_entry_repository import SqlAlchemyEntryRepository
from app.hexagon.sistema import Sistema


def get_sistema() -> Sistema:
    return Sistema(SqlAlchemyEntryRepository(SessionLocal))
