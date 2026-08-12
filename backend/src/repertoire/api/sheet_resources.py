from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from repertoire.db import get_db
from repertoire.models.piece import Piece
from repertoire.models.sheet_resource import SheetResource
from repertoire.schemas.sheet_resource import SheetResourceCreate, SheetResourceRead

router = APIRouter(prefix="/sheet-resources", tags=["sheet-resources"])


@router.post("", response_model=SheetResourceRead, status_code=201)
def create_sheet_resource(
    payload: SheetResourceCreate, db: Session = Depends(get_db)
) -> SheetResource:
    if db.get(Piece, payload.piece_id) is None:
        raise HTTPException(status_code=404, detail="Piece not found")
    resource = SheetResource(**payload.model_dump())
    db.add(resource)
    db.commit()
    db.refresh(resource)
    return resource


@router.get("", response_model=list[SheetResourceRead])
def list_sheet_resources(
    piece_id: int | None = None, db: Session = Depends(get_db)
) -> list[SheetResource]:
    query = db.query(SheetResource)
    if piece_id is not None:
        query = query.filter(SheetResource.piece_id == piece_id)
    return list(query.order_by(SheetResource.created_at.desc()).all())


@router.delete("/{sheet_resource_id}", status_code=204)
def delete_sheet_resource(sheet_resource_id: int, db: Session = Depends(get_db)) -> None:
    resource = db.get(SheetResource, sheet_resource_id)
    if resource is None:
        raise HTTPException(status_code=404, detail="Sheet resource not found")
    db.delete(resource)
    db.commit()
