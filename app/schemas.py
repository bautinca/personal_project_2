from pydantic import BaseModel, ConfigDict


class EntryCreate(BaseModel):
    text: str


class EntryUpdate(BaseModel):
    text: str


class EntryRead(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    text: str
