from .entry import Entry
from .errors import EntryNotFound
from .ports import EntryRepository


# Fachada del hexagono: es la unica puerta de entrada a la logica de negocio.
class Sistema:
    def __init__(self, entry_repository: EntryRepository):
        self._entries = entry_repository

    def add_entry(self, text: str) -> Entry:
        return self._entries.add(text)

    def list_entries(self) -> list[Entry]:
        return self._entries.list_all()

    def delete_entry(self, entry_id: int) -> None:
        if not self._entries.delete(entry_id):
            raise EntryNotFound(entry_id)
