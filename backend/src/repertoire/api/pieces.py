from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from repertoire.db import get_db
from repertoire.models.piece import Piece
from repertoire.schemas.piece import PieceCreate, PieceRead, PieceUpdate

router = APIRouter(prefix="/pieces", tags=["pieces"])


@router.post("", response_model=PieceRead, status_code=201)
def create_piece(payload: PieceCreate, db: Session = Depends(get_db)) -> Piece:
    piece = Piece(**payload.model_dump())
    db.add(piece)
    db.commit()
    db.refresh(piece)
    return piece


@router.get("", response_model=list[PieceRead])
def list_pieces(db: Session = Depends(get_db)) -> list[Piece]:
    return list(db.query(Piece).order_by(Piece.id).all())


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
