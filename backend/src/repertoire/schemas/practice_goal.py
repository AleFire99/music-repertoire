from datetime import datetime

from pydantic import BaseModel, Field


class PracticeGoalSet(BaseModel):
    target_minutes: int = Field(gt=0)


class PracticeGoalRead(BaseModel):
    id: int
    target_minutes: int
    minutes_this_week: int
    created_at: datetime
    updated_at: datetime
