from datetime import UTC, date, datetime, timedelta

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy import func
from sqlalchemy.orm import Session

from repertoire.date_utils import current_week_bounds, start_of_utc_day
from repertoire.db import get_db
from repertoire.models.piece import Piece, PieceStatus
from repertoire.models.practice_session import PracticeSession
from repertoire.schemas.practice_session import (
    DayPracticeMinutes,
    NeglectedPiece,
    PiecePracticeStats,
    PracticeSessionCreate,
    PracticeSessionRead,
    PracticeStatsRead,
    RecentlyPracticedPiece,
    SectionPracticeStats,
    SuggestedPlanItem,
)

router = APIRouter(prefix="/practice-sessions", tags=["practice-sessions"])

RECENTLY_PRACTICED_LIMIT = 5
NEGLECTED_LIMIT = 5
UNSPECIFIED_SECTION_LABEL = "(unspecified)"
HEATMAP_DAYS = 98
SUGGESTED_PLAN_LIMIT = 4
SUGGESTED_PLAN_DUE_SOON_DAYS = 14
SUGGESTED_PLAN_LOW_RATING_MAX = 3
SUGGESTED_PLAN_NEGLECTED_MIN_DAYS = 14


def _to_utc_date(moment: datetime) -> date:
    if moment.tzinfo is not None:
        moment = moment.astimezone(UTC)
    return moment.date()


def _current_month_bounds(today: date) -> tuple[datetime, datetime]:
    """[start, end) for the current calendar month, in UTC.

    A session exactly at the 1st 00:00:00 UTC counts as this month; a
    session at the 1st of next month 00:00:00 UTC is excluded.
    """
    start_date = today.replace(day=1)
    end_date = (
        start_date.replace(year=start_date.year + 1, month=1)
        if start_date.month == 12
        else start_date.replace(month=start_date.month + 1)
    )
    return start_of_utc_day(start_date), start_of_utc_day(end_date)


def _compute_streaks(practice_days: set[date], today: date) -> tuple[int, int]:
    """Longest run and current run of consecutive calendar days with a session.

    "Current" counts backward from the most recent practice day only if that
    day is today or yesterday; a gap of 2+ days since the last session resets
    it to 0. A single practiced day is a streak of 1.
    """
    if not practice_days:
        return 0, 0

    sorted_days = sorted(practice_days)

    longest_streak = 1
    run = 1
    for previous_day, day in zip(sorted_days, sorted_days[1:], strict=False):
        run = run + 1 if (day - previous_day).days == 1 else 1
        longest_streak = max(longest_streak, run)

    most_recent_day = sorted_days[-1]
    if (today - most_recent_day).days >= 2:
        return 0, longest_streak

    current_streak = 1
    for i in range(len(sorted_days) - 1, 0, -1):
        if (sorted_days[i] - sorted_days[i - 1]).days == 1:
            current_streak += 1
        else:
            break

    return current_streak, longest_streak


def _section_label(section: str | None) -> str:
    """Sessions with no (or blank) section are grouped under a single label
    rather than excluded, so their time still counts toward the piece total."""
    return section if section else UNSPECIFIED_SECTION_LABEL


def _build_consistency_heatmap(db: Session, today: date) -> list[DayPracticeMinutes]:
    """Daily total-minutes series for the last `HEATMAP_DAYS` UTC calendar days, oldest first."""
    start_day = today - timedelta(days=HEATMAP_DAYS - 1)
    rows = (
        db.query(PracticeSession.practiced_at, PracticeSession.duration_minutes)
        .filter(PracticeSession.practiced_at >= start_of_utc_day(start_day))
        .all()
    )
    minutes_by_day: dict[date, int] = {}
    for practiced_at, duration_minutes in rows:
        day = _to_utc_date(practiced_at)
        minutes_by_day[day] = minutes_by_day.get(day, 0) + duration_minutes

    return [
        DayPracticeMinutes(
            date=start_day + timedelta(days=offset),
            total_minutes=minutes_by_day.get(start_day + timedelta(days=offset), 0),
        )
        for offset in range(HEATMAP_DAYS)
    ]


def _build_suggested_plan(
    db: Session, today: date, neglected: list[NeglectedPiece]
) -> list[SuggestedPlanItem]:
    """A few pieces worth practicing next, ranked by due/overdue goals, longest-neglected,
    and low-rated recent sessions — a deterministic heuristic over existing fields, no
    music-theory logic and no LLM."""
    due_soon_cutoff = today + timedelta(days=SUGGESTED_PLAN_DUE_SOON_DAYS)
    due_soon_rows = (
        db.query(Piece.id, Piece.title, Piece.goal_target_date)
        .filter(
            Piece.goal_target_date.isnot(None),
            Piece.goal_target_date <= due_soon_cutoff,
            Piece.status != PieceStatus.ARCHIVED,
        )
        .order_by(Piece.goal_target_date.asc())
        .limit(SUGGESTED_PLAN_LIMIT)
        .all()
    )
    candidates: list[SuggestedPlanItem] = []
    for piece_id, title, target_date in due_soon_rows:
        days = (target_date - today).days
        if days < 0:
            reason = f"Goal was due {-days} day{'s' if -days != 1 else ''} ago"
        elif days == 0:
            reason = "Goal due today"
        else:
            reason = f"Goal due in {days} day{'s' if days != 1 else ''}"
        candidates.append(SuggestedPlanItem(piece_id=piece_id, piece_title=title, reason=reason))

    for piece in neglected:
        if piece.last_practiced_at is None:
            reason = "Never practiced"
        else:
            days = (today - _to_utc_date(piece.last_practiced_at)).days
            if days < SUGGESTED_PLAN_NEGLECTED_MIN_DAYS:
                continue
            reason = f"Not practiced in {days} day{'s' if days != 1 else ''}"
        candidates.append(
            SuggestedPlanItem(piece_id=piece.piece_id, piece_title=piece.piece_title, reason=reason)
        )

    latest_session = (
        db.query(
            PracticeSession.piece_id,
            PracticeSession.rating,
            func.row_number()
            .over(
                partition_by=PracticeSession.piece_id,
                order_by=PracticeSession.practiced_at.desc(),
            )
            .label("rn"),
        )
        .subquery()
    )
    low_rated_rows = (
        db.query(Piece.id, Piece.title, latest_session.c.rating)
        .join(latest_session, latest_session.c.piece_id == Piece.id)
        .filter(
            latest_session.c.rn == 1,
            latest_session.c.rating.isnot(None),
            latest_session.c.rating <= SUGGESTED_PLAN_LOW_RATING_MAX,
        )
        .order_by(latest_session.c.rating.asc())
        .limit(SUGGESTED_PLAN_LIMIT)
        .all()
    )
    for piece_id, title, rating in low_rated_rows:
        candidates.append(
            SuggestedPlanItem(
                piece_id=piece_id, piece_title=title, reason=f"Last session rated {rating}/5"
            )
        )

    seen: set[int] = set()
    plan: list[SuggestedPlanItem] = []
    for item in candidates:
        if item.piece_id in seen:
            continue
        seen.add(item.piece_id)
        plan.append(item)
        if len(plan) == SUGGESTED_PLAN_LIMIT:
            break
    return plan


@router.post("", response_model=PracticeSessionRead, status_code=201)
def create_practice_session(
    payload: PracticeSessionCreate, db: Session = Depends(get_db)
) -> PracticeSession:
    if db.get(Piece, payload.piece_id) is None:
        raise HTTPException(status_code=404, detail="Piece not found")
    session = PracticeSession(**payload.model_dump())
    db.add(session)
    db.commit()
    db.refresh(session)
    return session


@router.get("", response_model=list[PracticeSessionRead])
def list_practice_sessions(
    piece_id: int | None = None, db: Session = Depends(get_db)
) -> list[PracticeSession]:
    query = db.query(PracticeSession)
    if piece_id is not None:
        query = query.filter(PracticeSession.piece_id == piece_id)
    return list(query.order_by(PracticeSession.practiced_at.desc()).all())


@router.get("/stats", response_model=PracticeStatsRead)
def get_practice_stats(db: Session = Depends(get_db)) -> PracticeStatsRead:
    total_minutes = db.query(func.sum(PracticeSession.duration_minutes)).scalar() or 0

    rows = (
        db.query(
            PracticeSession.piece_id,
            Piece.title,
            func.sum(PracticeSession.duration_minutes),
            func.count(PracticeSession.id),
            func.max(PracticeSession.practiced_at),
        )
        .join(Piece, Piece.id == PracticeSession.piece_id)
        .group_by(PracticeSession.piece_id, Piece.title)
        .order_by(func.max(PracticeSession.practiced_at).desc())
        .all()
    )

    section_rows = (
        db.query(
            PracticeSession.piece_id,
            PracticeSession.section,
            func.sum(PracticeSession.duration_minutes),
        )
        .group_by(PracticeSession.piece_id, PracticeSession.section)
        .all()
    )

    sections_by_piece: dict[int, dict[str, int]] = {}
    for piece_id, section, section_minutes in section_rows:
        label = _section_label(section)
        bucket = sections_by_piece.setdefault(piece_id, {})
        bucket[label] = bucket.get(label, 0) + section_minutes

    pieces = [
        PiecePracticeStats(
            piece_id=piece_id,
            piece_title=title,
            total_minutes=piece_total_minutes,
            session_count=session_count,
            last_practiced_at=last_practiced_at,
            sections=[
                SectionPracticeStats(section=label, total_minutes=minutes)
                for label, minutes in sorted(
                    sections_by_piece.get(piece_id, {}).items(),
                    key=lambda item: (-item[1], item[0]),
                )
            ],
        )
        for piece_id, title, piece_total_minutes, session_count, last_practiced_at in rows
    ]

    # `pieces` is already ordered by last_practiced_at desc (max practiced_at
    # per piece), so the most recently practiced pieces are simply its head.
    recently_practiced = [
        RecentlyPracticedPiece(
            piece_id=p.piece_id,
            piece_title=p.piece_title,
            last_practiced_at=p.last_practiced_at,
        )
        for p in pieces[:RECENTLY_PRACTICED_LIMIT]
    ]

    last_practiced_subquery = (
        db.query(
            PracticeSession.piece_id.label("piece_id"),
            func.max(PracticeSession.practiced_at).label("last_practiced_at"),
        )
        .group_by(PracticeSession.piece_id)
        .subquery()
    )

    neglected_rows = (
        db.query(
            Piece.id,
            Piece.title,
            last_practiced_subquery.c.last_practiced_at,
        )
        .outerjoin(last_practiced_subquery, last_practiced_subquery.c.piece_id == Piece.id)
        .order_by(last_practiced_subquery.c.last_practiced_at.asc().nulls_first())
        .limit(NEGLECTED_LIMIT)
        .all()
    )

    neglected = [
        NeglectedPiece(piece_id=piece_id, piece_title=title, last_practiced_at=last_practiced_at)
        for piece_id, title, last_practiced_at in neglected_rows
    ]

    practiced_at_values = db.query(PracticeSession.practiced_at).distinct().all()
    practice_days = {_to_utc_date(row[0]) for row in practiced_at_values}
    today = datetime.now(UTC).date()
    current_streak_days, longest_streak_days = _compute_streaks(practice_days, today=today)

    week_start, week_end = current_week_bounds(today)
    minutes_this_week = (
        db.query(func.sum(PracticeSession.duration_minutes))
        .filter(
            PracticeSession.practiced_at >= week_start,
            PracticeSession.practiced_at < week_end,
        )
        .scalar()
        or 0
    )

    month_start, month_end = _current_month_bounds(today)
    minutes_this_month = (
        db.query(func.sum(PracticeSession.duration_minutes))
        .filter(
            PracticeSession.practiced_at >= month_start,
            PracticeSession.practiced_at < month_end,
        )
        .scalar()
        or 0
    )

    return PracticeStatsRead(
        total_minutes=total_minutes,
        pieces=pieces,
        recently_practiced=recently_practiced,
        neglected=neglected,
        current_streak_days=current_streak_days,
        longest_streak_days=longest_streak_days,
        minutes_this_week=minutes_this_week,
        minutes_this_month=minutes_this_month,
        consistency_heatmap=_build_consistency_heatmap(db, today),
        suggested_plan=_build_suggested_plan(db, today, neglected),
    )
