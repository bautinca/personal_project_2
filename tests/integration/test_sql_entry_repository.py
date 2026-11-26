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
