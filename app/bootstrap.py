# Raiz de composicion: el unico lugar donde se decide que adaptador se conecta a cada puerto.
import httpx

from app.adapters.persistence.database import SessionLocal
from app.adapters.persistence.sql_entry_repository import SqlAlchemyEntryRepository
from app.adapters.translation.my_memory_translator import MyMemoryTranslator
from app.hexagon.sistema import Sistema

# Se reutiliza un unico cliente HTTP. El timeout evita que una API lenta deje peticiones colgadas.
translator = MyMemoryTranslator(httpx.Client(timeout=5))


def get_sistema() -> Sistema:
    return Sistema(SqlAlchemyEntryRepository(SessionLocal), translator)
