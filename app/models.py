from sqlalchemy import Column, Integer, Text

from .database import Base


class Entry(Base):
    __tablename__ = "entries"

    id = Column(Integer, primary_key=True, index=True)
    text = Column(Text, nullable=False)
