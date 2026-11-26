# Raiz de composicion: el unico lugar donde se decide que adaptador se conecta a cada puerto.
from app.adapters.persistence.database import SessionLocal, init_db
from app.adapters.persistence.sql_entry_repository import SqlAlchemyEntryRepository
from app.hexagon.sistema import Sistema


# Prepara los servicios externos al arrancar la aplicacion.
def init_infrastructure() -> None:
    init_db()


def get_sistema() -> Sistema:
    return Sistema(SqlAlchemyEntryRepository(SessionLocal))
