from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy import any_, or_
from sqlalchemy.orm import Session

from repertoire.db import get_db
from repertoire.models.piece import Piece, PieceDifficulty, PieceStatus
from repertoire.schemas.piece import PieceCreate, PieceRead, PieceUpdate

router = APIRouter(prefix="/pieces", tags=["pieces"])


@router.post("", response_model=PieceRead, status_code=201)
def create_piece(payload: PieceCreate, db: Session = Depends(get_db)) -> Piece:
    piece = Piece(**payload.model_dump())
    db.add(piece)
    db.commit()
    db.refresh(piece)
    return piece


IN_FOCUS_STATUSES = (PieceStatus.LEARNING, PieceStatus.MAINTAINING)


@router.get("", response_model=list[PieceRead])
def list_pieces(
    status: PieceStatus | None = None,
    tag: str | None = None,
    favorite: bool | None = None,
    difficulty: PieceDifficulty | None = None,
    instrument: str | None = None,
    has_goal: bool | None = None,
    in_focus: bool | None = None,
    db: Session = Depends(get_db),
) -> list[Piece]:
    query = db.query(Piece)
    if status is not None:
        query = query.filter(Piece.status == status)
    if tag is not None:
        query = query.filter(any_(Piece.tags) == tag)
    if favorite is not None:
        query = query.filter(Piece.is_favorite == favorite)
    if difficulty is not None:
        query = query.filter(Piece.difficulty == difficulty)
    if instrument is not None:
        query = query.filter(Piece.instrument == instrument)
    if has_goal is not None:
        if has_goal:
            query = query.filter(Piece.goal_target_date.isnot(None))
        else:
            query = query.filter(Piece.goal_target_date.is_(None))
    if in_focus:
        query = query.filter(
            Piece.status.in_(IN_FOCUS_STATUSES),
            or_(Piece.goal_text.isnot(None), Piece.goal_target_date.isnot(None)),
        )
    return list(query.order_by(Piece.id).all())


def _get_piece_or_404(piece_id: int, db: Session) -> Piece:
    piece = db.get(Piece, piece_id)
    if piece is None:
        raise HTTPException(status_code=404, detail="Piece not found")
    return piece


@router.get("/{piece_id}", response_model=PieceRead)
def get_piece(piece_id: int, db: Session = Depends(get_db)) -> Piece:
    return _get_piece_or_404(piece_id, db)


@router.patch("/{piece_id}", response_model=PieceRead)
def update_piece(piece_id: int, payload: PieceUpdate, db: Session = Depends(get_db)) -> Piece:
    piece = _get_piece_or_404(piece_id, db)
    for field, value in payload.model_dump(exclude_unset=True).items():
        setattr(piece, field, value)
    db.commit()
    db.refresh(piece)
    return piece


@router.delete("/{piece_id}", status_code=204)
def delete_piece(piece_id: int, db: Session = Depends(get_db)) -> None:
    piece = _get_piece_or_404(piece_id, db)
    db.delete(piece)
    db.commit()
