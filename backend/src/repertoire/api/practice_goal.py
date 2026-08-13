from datetime import UTC, datetime

from fastapi import APIRouter, Depends
from sqlalchemy import func
from sqlalchemy.orm import Session

from repertoire.date_utils import current_week_bounds
from repertoire.db import get_db
from repertoire.models.practice_goal import PracticeGoal
from repertoire.models.practice_session import PracticeSession
from repertoire.schemas.practice_goal import PracticeGoalRead, PracticeGoalSet

router = APIRouter(prefix="/practice-goal", tags=["practice-goal"])


def _minutes_this_week(db: Session) -> int:
    today = datetime.now(UTC).date()
    week_start, week_end = current_week_bounds(today)
    return (
        db.query(func.sum(PracticeSession.duration_minutes))
        .filter(
            PracticeSession.practiced_at >= week_start,
            PracticeSession.practiced_at < week_end,
        )
        .scalar()
        or 0
    )


def _to_read(goal: PracticeGoal, db: Session) -> PracticeGoalRead:
    return PracticeGoalRead(
        id=goal.id,
        target_minutes=goal.target_minutes,
        minutes_this_week=_minutes_this_week(db),
        created_at=goal.created_at,
        updated_at=goal.updated_at,
    )


@router.get("", response_model=PracticeGoalRead | None)
def get_practice_goal(db: Session = Depends(get_db)) -> PracticeGoalRead | None:
    goal = db.query(PracticeGoal).first()
    return _to_read(goal, db) if goal is not None else None


@router.put("", response_model=PracticeGoalRead)
def set_practice_goal(payload: PracticeGoalSet, db: Session = Depends(get_db)) -> PracticeGoalRead:
    goal = db.query(PracticeGoal).first()
    if goal is None:
        goal = PracticeGoal(target_minutes=payload.target_minutes)
        db.add(goal)
    else:
        goal.target_minutes = payload.target_minutes
    db.commit()
    db.refresh(goal)
    return _to_read(goal, db)
