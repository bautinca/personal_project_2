from app.hexagon.ports import Translator


# Adaptador falso del puerto Translator. Permite probar la app sin conexion a internet.
class FakeTranslator(Translator):
    def __init__(self):
        self.error: Exception | None = None  # Si se define, translate lo lanza.
        self.requested: list[str] = []

    def translate(self, text: str) -> str:
        self.requested.append(text)
        if self.error is not None:
            raise self.error
        return f"[en] {text}"
