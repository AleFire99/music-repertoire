from datetime import datetime

from pydantic import BaseModel, ConfigDict, Field


class PracticeSessionCreate(BaseModel):
    piece_id: int
    practiced_at: datetime
    duration_minutes: int = Field(gt=0)
    notes: str | None = None
    rating: int | None = Field(default=None, ge=1, le=5)
    section: str | None = None


class PracticeSessionRead(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    piece_id: int
    practiced_at: datetime
    duration_minutes: int
    notes: str | None
    rating: int | None
    section: str | None
    created_at: datetime
    updated_at: datetime
