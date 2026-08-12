from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from repertoire.db import get_db
from repertoire.models.piece import Piece
from repertoire.models.practice_session import PracticeSession
from repertoire.schemas.practice_session import PracticeSessionCreate, PracticeSessionRead

router = APIRouter(prefix="/practice-sessions", tags=["practice-sessions"])


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
