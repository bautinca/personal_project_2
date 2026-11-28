from .entry import Entry
from .errors import EntryNotFound
from .ports import EntryRepository, Translator


# Fachada del hexagono: es la unica puerta de entrada a la logica de negocio.
class Sistema:
    def __init__(self, entry_repository: EntryRepository, translator: Translator):
        self._entries = entry_repository
        self._translator = translator

    def add_entry(self, text: str) -> Entry:
        return self._entries.add(text)

    def list_entries(self) -> list[Entry]:
        return self._entries.list_all()

    def update_entry(self, entry_id: int, text: str) -> Entry:
        entry = self._entries.update(entry_id, text)
        if entry is None:
            raise EntryNotFound(entry_id)
        return entry

    def delete_entry(self, entry_id: int) -> None:
        if not self._entries.delete(entry_id):
            raise EntryNotFound(entry_id)

    # La traduccion solo se devuelve: no se guarda ni modifica la entrada.
    def translate_entry(self, entry_id: int) -> str:
        entry = self._entries.get(entry_id)
        if entry is None:
            raise EntryNotFound(entry_id)
        return self._translator.translate(entry.text)
