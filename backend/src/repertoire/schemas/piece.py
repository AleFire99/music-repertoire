from datetime import date, datetime

from pydantic import BaseModel, ConfigDict, Field

from repertoire.models.piece import PieceDifficulty, PieceStatus
from repertoire.models.sheet_resource import SheetResourceKind


class PieceCreate(BaseModel):
    title: str
    composer: str | None = None
    key: str | None = None
    tempo_bpm: int | None = None
    difficulty: PieceDifficulty | None = None
    instrument: str | None = None
    goal_text: str | None = None
    goal_target_date: date | None = None
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
    goal_text: str | None = None
    goal_target_date: date | None = None
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
    goal_text: str | None
    goal_target_date: date | None
    status: PieceStatus
    tags: list[str]
    is_favorite: bool
    sheet_resource_kinds: list[SheetResourceKind] = Field(default_factory=list)
    preview_sheet_resource_id: int | None = None
    created_at: datetime
    updated_at: datetime
