from datetime import datetime

from pydantic import BaseModel, ConfigDict

from repertoire.schemas.piece import PieceRead


class RepertoireListCreate(BaseModel):
    name: str


class RepertoireListUpdate(BaseModel):
    name: str | None = None


class RepertoireListRead(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    name: str
    created_at: datetime
    updated_at: datetime
    piece_count: int


class RepertoireListDetail(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    name: str
    created_at: datetime
    updated_at: datetime
    pieces: list[PieceRead]


class RepertoireListPieceCreate(BaseModel):
    piece_id: int
