from datetime import datetime

from pydantic import BaseModel, ConfigDict

from repertoire.models.piece import PieceDifficulty, PieceStatus


class PieceCreate(BaseModel):
    title: str
    composer: str | None = None
    key: str | None = None
    tempo_bpm: int | None = None
    difficulty: PieceDifficulty | None = None
    instrument: str | None = None
    status: PieceStatus = PieceStatus.BACKLOG
    tags: list[str] = []
    is_favorite: bool = False


class PieceUpdate(BaseModel):
    title: str | None = None
    composer: str | None = None
    key: str | None = None
    tempo_bpm: int | None = None
    difficulty: PieceDifficulty | None = None
    instrument: str | None = None
    status: PieceStatus | None = None
    tags: list[str] | None = None
    is_favorite: bool | None = None


class PieceRead(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    title: str
    composer: str | None
    key: str | None
    tempo_bpm: int | None
    difficulty: PieceDifficulty | None
    instrument: str | None
    status: PieceStatus
    tags: list[str]
    is_favorite: bool
    created_at: datetime
    updated_at: datetime
