class EntryNotFound(Exception):
    def __init__(self, entry_id: int):
        super().__init__(f"No existe la entrada con id {entry_id}")
        self.entry_id = entry_id
