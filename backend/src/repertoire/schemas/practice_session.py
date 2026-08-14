from datetime import date, datetime

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


class SectionPracticeStats(BaseModel):
    section: str
    total_minutes: int


class PiecePracticeStats(BaseModel):
    piece_id: int
    piece_title: str
    total_minutes: int
    session_count: int
    last_practiced_at: datetime
    sections: list[SectionPracticeStats]


class RecentlyPracticedPiece(BaseModel):
    piece_id: int
    piece_title: str
    last_practiced_at: datetime


class NeglectedPiece(BaseModel):
    piece_id: int
    piece_title: str
    last_practiced_at: datetime | None


class DayPracticeMinutes(BaseModel):
    date: date
    total_minutes: int


class SuggestedPlanItem(BaseModel):
    piece_id: int
    piece_title: str
    reason: str


class PracticeStatsRead(BaseModel):
    total_minutes: int
    pieces: list[PiecePracticeStats]
    recently_practiced: list[RecentlyPracticedPiece]
    neglected: list[NeglectedPiece]
    current_streak_days: int
    longest_streak_days: int
    minutes_this_week: int
    minutes_this_month: int
    consistency_heatmap: list[DayPracticeMinutes]
    suggested_plan: list[SuggestedPlanItem]
