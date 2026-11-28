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

    def get(self, entry_id: int) -> Entry | None:
        return self._entries.get(entry_id)

    def list_all(self) -> list[Entry]:
        return list(self._entries.values())

    def update(self, entry_id: int, text: str) -> Entry | None:
        if entry_id not in self._entries:
            return None
        self._entries[entry_id] = Entry(id=entry_id, text=text)
        return self._entries[entry_id]

    def delete(self, entry_id: int) -> bool:
        return self._entries.pop(entry_id, None) is not None
