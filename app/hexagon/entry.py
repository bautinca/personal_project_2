from dataclasses import dataclass


# Objeto de negocio: un texto guardado por el usuario. No sabe nada de bases de datos ni de HTTP.
@dataclass(frozen=True)
class Entry:
    id: int
    text: str
