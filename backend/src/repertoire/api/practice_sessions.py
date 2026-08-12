from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy import func
from sqlalchemy.orm import Session

from repertoire.db import get_db
from repertoire.models.piece import Piece
from repertoire.models.practice_session import PracticeSession
from repertoire.schemas.practice_session import (
    NeglectedPiece,
    PiecePracticeStats,
    PracticeSessionCreate,
    PracticeSessionRead,
    PracticeStatsRead,
    RecentlyPracticedPiece,
)

router = APIRouter(prefix="/practice-sessions", tags=["practice-sessions"])

RECENTLY_PRACTICED_LIMIT = 5
NEGLECTED_LIMIT = 5


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

    pieces = [
        PiecePracticeStats(
            piece_id=piece_id,
            piece_title=title,
            total_minutes=piece_total_minutes,
            session_count=session_count,
            last_practiced_at=last_practiced_at,
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

    return PracticeStatsRead(
        total_minutes=total_minutes,
        pieces=pieces,
        recently_practiced=recently_practiced,
        neglected=neglected,
    )
