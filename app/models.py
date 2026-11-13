from sqlalchemy import Column, Integer, Text

from .database import Base

# Entry hereda de Base, que es la clase base de SQLAlchemy para los modelos ORM. Esto permite que Entry se mapee a una tabla en la base de datos.
# En resumidas cuentas la clase Entry representa una tabla en la base de datos, precisamente la tabla 'entries', y cada instancia de Entry representa una fila en esa tabla. Los atributos de la clase corresponden a las columnas de la tabla, y SQLAlchemy se encarga de manejar la interacción con la base de datos.
class Entry(Base):
    __tablename__ = "entries"

    id = Column(Integer, primary_key=True, index=True)
    text = Column(Text, nullable=False)
