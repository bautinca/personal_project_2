from sqlalchemy import Column, Integer, Text

from .database import Base

# EntryModel hereda de Base, que es la clase base de SQLAlchemy para los modelos ORM. Esto permite que se mapee a una tabla en la base de datos, precisamente la tabla 'entries': cada instancia representa una fila y cada atributo una columna.
# No es el objeto de negocio (ese es app.hexagon.entry.Entry), sino su representacion en la base de datos.
class EntryModel(Base):
    __tablename__ = "entries"

    id = Column(Integer, primary_key=True, index=True)
    text = Column(Text, nullable=False)
