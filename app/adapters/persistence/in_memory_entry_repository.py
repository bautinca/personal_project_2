from itertools import count

from app.hexagon.entry import Entry
from app.hexagon.ports import EntryRepository


# Adaptador en memoria del puerto EntryRepository. Permite probar el hexagono sin base de datos.
class InMemoryEntryRepository(EntryRepository):
    def __init__(self):
        self._entries: dict[int, Entry] = {}
        self._ids = count(1)

    def add(self, text: str) -> Entry:
        entry = Entry(id=next(self._ids), text=text)
        self._entries[entry.id] = entry
        return entry

    def list_all(self) -> list[Entry]:
        return list(self._entries.values())

    def delete(self, entry_id: int) -> bool:
        return self._entries.pop(entry_id, None) is not None
