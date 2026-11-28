class EntryNotFound(Exception):
    def __init__(self, entry_id: int):
        super().__init__(f"No existe la entrada con id {entry_id}")
        self.entry_id = entry_id


class TextTooLongToTranslate(Exception):
    def __init__(self):
        super().__init__("El texto es demasiado largo para traducirlo")


class TranslationUnavailable(Exception):
    def __init__(self):
        super().__init__("El servicio de traduccion no esta disponible")
