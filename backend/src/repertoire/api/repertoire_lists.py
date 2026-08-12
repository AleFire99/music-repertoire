from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy import func
from sqlalchemy.orm import Session

from repertoire.db import get_db
from repertoire.models.piece import Piece
from repertoire.models.repertoire_list import RepertoireList
from repertoire.models.repertoire_list_piece import RepertoireListPiece
from repertoire.schemas.piece import PieceRead
from repertoire.schemas.repertoire_list import (
    RepertoireListCreate,
    RepertoireListDetail,
    RepertoireListPieceCreate,
    RepertoireListRead,
    RepertoireListUpdate,
)

router = APIRouter(prefix="/repertoire-lists", tags=["repertoire-lists"])


def _get_list_or_404(list_id: int, db: Session) -> RepertoireList:
    repertoire_list = db.get(RepertoireList, list_id)
    if repertoire_list is None:
        raise HTTPException(status_code=404, detail="Repertoire list not found")
    return repertoire_list


def _piece_count(list_id: int, db: Session) -> int:
    return (
        db.query(RepertoireListPiece)
        .filter(RepertoireListPiece.repertoire_list_id == list_id)
        .count()
    )


def _to_read(repertoire_list: RepertoireList, piece_count: int) -> RepertoireListRead:
    return RepertoireListRead(
        id=repertoire_list.id,
        name=repertoire_list.name,
        created_at=repertoire_list.created_at,
        updated_at=repertoire_list.updated_at,
        piece_count=piece_count,
    )


def _to_detail(repertoire_list: RepertoireList, db: Session) -> RepertoireListDetail:
    pieces = (
        db.query(Piece)
        .join(RepertoireListPiece, RepertoireListPiece.piece_id == Piece.id)
        .filter(RepertoireListPiece.repertoire_list_id == repertoire_list.id)
        .order_by(Piece.title)
        .all()
    )
    return RepertoireListDetail(
        id=repertoire_list.id,
        name=repertoire_list.name,
        created_at=repertoire_list.created_at,
        updated_at=repertoire_list.updated_at,
        pieces=[PieceRead.model_validate(piece) for piece in pieces],
    )


@router.post("", response_model=RepertoireListRead, status_code=201)
def create_repertoire_list(
    payload: RepertoireListCreate, db: Session = Depends(get_db)
) -> RepertoireListRead:
    repertoire_list = RepertoireList(name=payload.name)
    db.add(repertoire_list)
    db.commit()
    db.refresh(repertoire_list)
    return _to_read(repertoire_list, piece_count=0)


@router.get("", response_model=list[RepertoireListRead])
def list_repertoire_lists(db: Session = Depends(get_db)) -> list[RepertoireListRead]:
    counts: dict[int, int] = {
        row[0]: row[1]
        for row in db.query(
            RepertoireListPiece.repertoire_list_id, func.count(RepertoireListPiece.piece_id)
        ).group_by(RepertoireListPiece.repertoire_list_id)
    }
    lists = db.query(RepertoireList).order_by(RepertoireList.created_at.desc()).all()
    return [_to_read(lst, piece_count=counts.get(lst.id, 0)) for lst in lists]


@router.get("/{list_id}", response_model=RepertoireListDetail)
def get_repertoire_list(list_id: int, db: Session = Depends(get_db)) -> RepertoireListDetail:
    repertoire_list = _get_list_or_404(list_id, db)
    return _to_detail(repertoire_list, db)


@router.patch("/{list_id}", response_model=RepertoireListRead)
def update_repertoire_list(
    list_id: int, payload: RepertoireListUpdate, db: Session = Depends(get_db)
) -> RepertoireListRead:
    repertoire_list = _get_list_or_404(list_id, db)
    for field, value in payload.model_dump(exclude_unset=True).items():
        setattr(repertoire_list, field, value)
    db.commit()
    db.refresh(repertoire_list)
    return _to_read(repertoire_list, piece_count=_piece_count(list_id, db))


@router.delete("/{list_id}", status_code=204)
def delete_repertoire_list(list_id: int, db: Session = Depends(get_db)) -> None:
    repertoire_list = _get_list_or_404(list_id, db)
    db.delete(repertoire_list)
    db.commit()


@router.post("/{list_id}/pieces", response_model=RepertoireListDetail, status_code=201)
def add_piece_to_list(
    list_id: int, payload: RepertoireListPieceCreate, db: Session = Depends(get_db)
) -> RepertoireListDetail:
    repertoire_list = _get_list_or_404(list_id, db)
    if db.get(Piece, payload.piece_id) is None:
        raise HTTPException(status_code=404, detail="Piece not found")
    if db.get(RepertoireListPiece, (list_id, payload.piece_id)) is None:
        db.add(RepertoireListPiece(repertoire_list_id=list_id, piece_id=payload.piece_id))
        db.commit()
    return _to_detail(repertoire_list, db)


@router.delete("/{list_id}/pieces/{piece_id}", status_code=204)
def remove_piece_from_list(list_id: int, piece_id: int, db: Session = Depends(get_db)) -> None:
    _get_list_or_404(list_id, db)
    association = db.get(RepertoireListPiece, (list_id, piece_id))
    if association is None:
        raise HTTPException(status_code=404, detail="Piece is not on this list")
    db.delete(association)
    db.commit()
