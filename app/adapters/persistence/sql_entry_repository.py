from sqlalchemy.orm import sessionmaker

from app.hexagon.entry import Entry
from app.hexagon.ports import EntryRepository

from .models import EntryModel


def _to_entry(model: EntryModel) -> Entry:
    return Entry(id=model.id, text=model.text)


# Adaptador del puerto EntryRepository que persiste con SQLAlchemy.
class SqlAlchemyEntryRepository(EntryRepository):
    def __init__(self, session_factory: sessionmaker):
        self._session_factory = session_factory

    def add(self, text: str) -> Entry:
        with self._session_factory() as db:
            model = EntryModel(text=text)
            db.add(model)
            db.commit()
            db.refresh(model)
            return _to_entry(model)

    def list_all(self) -> list[Entry]:
        with self._session_factory() as db:
            models = db.query(EntryModel).order_by(EntryModel.id).all()
            return [_to_entry(m) for m in models]

    def delete(self, entry_id: int) -> bool:
        with self._session_factory() as db:
            model = db.get(EntryModel, entry_id)
            if model is None:
                return False
            db.delete(model)
            db.commit()
            return True
