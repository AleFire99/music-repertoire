from datetime import datetime

from pydantic import BaseModel, ConfigDict

from repertoire.models.piece import PieceStatus


class PieceCreate(BaseModel):
    title: str
    composer: str | None = None
    status: PieceStatus = PieceStatus.BACKLOG
    tags: list[str] = []


class PieceUpdate(BaseModel):
    title: str | None = None
    composer: str | None = None
    status: PieceStatus | None = None
    tags: list[str] | None = None


class PieceRead(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    title: str
    composer: str | None
    status: PieceStatus
    tags: list[str]
    created_at: datetime
    updated_at: datetime
