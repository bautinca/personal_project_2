from pydantic import BaseModel, ConfigDict


class EntryRead(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    text: str
