from datetime import datetime

from pydantic import BaseModel, ConfigDict


class PieceCreate(BaseModel):
    title: str
    composer: str | None = None


class PieceUpdate(BaseModel):
    title: str | None = None
    composer: str | None = None


class PieceRead(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    title: str
    composer: str | None
    created_at: datetime
    updated_at: datetime
