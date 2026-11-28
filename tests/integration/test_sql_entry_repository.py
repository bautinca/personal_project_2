import pytest

from app.adapters.persistence.database import SessionLocal
from app.adapters.persistence.sql_entry_repository import SqlAlchemyEntryRepository


@pytest.fixture
def repository(clean_tables):
    return SqlAlchemyEntryRepository(SessionLocal)


def test_add_persists_entry(repository):
    entry = repository.add("persistido")

    assert SqlAlchemyEntryRepository(SessionLocal).list_all() == [entry]


def test_list_all_is_ordered_by_id(repository):
    first = repository.add("primero")
    second = repository.add("segundo")

    assert repository.list_all() == [first, second]


def test_delete_existing_entry(repository):
    entry = repository.add("a borrar")

    assert repository.delete(entry.id) is True
    assert repository.list_all() == []


def test_delete_missing_entry(repository):
    assert repository.delete(999) is False


def test_update_persists_new_text(repository):
    entry = repository.add("original")

    updated = repository.update(entry.id, "modificado")

    assert (updated.id, updated.text) == (entry.id, "modificado")
    assert SqlAlchemyEntryRepository(SessionLocal).list_all() == [updated]


def test_update_only_changes_selected_entry_and_keeps_order(repository):
    first = repository.add("primero")
    second = repository.add("segundo")

    updated = repository.update(first.id, "primero modificado")

    assert repository.list_all() == [updated, second]


def test_update_missing_entry(repository):
    assert repository.update(999, "nada") is None
    assert repository.list_all() == []


def test_get_returns_selected_entry(repository):
    repository.add("otra")
    entry = repository.add("buscada")

    assert repository.get(entry.id) == entry


def test_get_missing_entry(repository):
    assert repository.get(999) is None
