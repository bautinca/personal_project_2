from abc import ABC, abstractmethod

from .entry import Entry


# Puerto de salida: lo que el hexagono necesita para persistir entradas, sin importar con que tecnologia se haga.
class EntryRepository(ABC):
    @abstractmethod
    def add(self, text: str) -> Entry:
        """Guarda un texto y devuelve la entrada creada, con su id asignado."""

    @abstractmethod
    def list_all(self) -> list[Entry]:
        """Devuelve todas las entradas ordenadas por id."""

    @abstractmethod
    def delete(self, entry_id: int) -> bool:
        """Elimina la entrada indicada. Devuelve False si no existe."""
