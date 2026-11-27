import pytest

from app.adapters.persistence.in_memory_entry_repository import InMemoryEntryRepository
from app.hexagon.errors import EntryNotFound
from app.hexagon.sistema import Sistema


@pytest.fixture
def sistema():
    return Sistema(InMemoryEntryRepository())


def test_starts_without_entries(sistema):
    assert sistema.list_entries() == []


def test_add_entry_returns_it_and_lists_it(sistema):
    entry = sistema.add_entry("hola")

    assert entry.text == "hola"
    assert sistema.list_entries() == [entry]


def test_entries_are_listed_in_creation_order(sistema):
    first = sistema.add_entry("primero")
    second = sistema.add_entry("segundo")

    assert sistema.list_entries() == [first, second]


def test_delete_only_removes_selected_entry(sistema):
    deleted = sistema.add_entry("a borrar")
    kept = sistema.add_entry("se queda")

    sistema.delete_entry(deleted.id)

    assert sistema.list_entries() == [kept]


def test_delete_missing_entry_raises(sistema):
    with pytest.raises(EntryNotFound):
        sistema.delete_entry(999)


def test_update_entry_changes_text_and_keeps_id(sistema):
    entry = sistema.add_entry("original")

    updated = sistema.update_entry(entry.id, "modificado")

    assert updated.id == entry.id
    assert updated.text == "modificado"
    assert sistema.list_entries() == [updated]


def test_update_only_changes_selected_entry_and_keeps_order(sistema):
    first = sistema.add_entry("primero")
    second = sistema.add_entry("segundo")

    updated = sistema.update_entry(first.id, "primero modificado")

    assert sistema.list_entries() == [updated, second]


def test_update_missing_entry_raises_and_creates_nothing(sistema):
    with pytest.raises(EntryNotFound):
        sistema.update_entry(999, "nada")

    assert sistema.list_entries() == []
