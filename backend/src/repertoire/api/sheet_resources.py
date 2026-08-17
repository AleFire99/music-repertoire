import uuid
from pathlib import Path

from fastapi import APIRouter, Depends, File, Form, HTTPException, UploadFile
from fastapi.responses import FileResponse
from sqlalchemy.orm import Session

from repertoire.config import settings
from repertoire.db import get_db
from repertoire.models.piece import Piece
from repertoire.models.sheet_resource import SheetResource, SheetResourceKind
from repertoire.schemas.sheet_resource import SheetResourceCreate, SheetResourceRead

router = APIRouter(prefix="/sheet-resources", tags=["sheet-resources"])

ALLOWED_UPLOAD_CONTENT_TYPE = "application/pdf"


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


@router.post("/upload", response_model=SheetResourceRead, status_code=201)
def upload_sheet_resource(
    piece_id: int = Form(...),
    file: UploadFile = File(...),
    label: str | None = Form(None),
    notes: str | None = Form(None),
    db: Session = Depends(get_db),
) -> SheetResource:
    if db.get(Piece, piece_id) is None:
        raise HTTPException(status_code=404, detail="Piece not found")

    if file.content_type != ALLOWED_UPLOAD_CONTENT_TYPE:
        raise HTTPException(status_code=415, detail="Only PDF uploads are supported")

    max_bytes = settings.sheet_resource_max_upload_bytes
    contents = file.file.read(max_bytes + 1)
    if len(contents) > max_bytes:
        raise HTTPException(
            status_code=413,
            detail=f"File exceeds the {max_bytes // (1024 * 1024)}MB upload limit",
        )

    storage_dir = Path(settings.sheet_resource_storage_dir)
    storage_dir.mkdir(parents=True, exist_ok=True)
    storage_key = f"{uuid.uuid4().hex}.pdf"
    (storage_dir / storage_key).write_bytes(contents)

    resource = SheetResource(
        piece_id=piece_id,
        kind=SheetResourceKind.UPLOADED,
        reference=file.filename or storage_key,
        label=label,
        notes=notes,
        original_filename=file.filename,
        content_type=file.content_type,
        file_size_bytes=len(contents),
        storage_key=storage_key,
    )
    db.add(resource)
    db.commit()
    db.refresh(resource)
    return resource


@router.get("/{sheet_resource_id}/file")
def download_sheet_resource_file(
    sheet_resource_id: int, db: Session = Depends(get_db)
) -> FileResponse:
    resource = db.get(SheetResource, sheet_resource_id)
    if (
        resource is None
        or resource.kind != SheetResourceKind.UPLOADED
        or resource.storage_key is None
    ):
        raise HTTPException(status_code=404, detail="Sheet resource not found")

    file_path = Path(settings.sheet_resource_storage_dir) / resource.storage_key
    if not file_path.is_file():
        raise HTTPException(status_code=404, detail="Stored file not found")

    return FileResponse(
        path=file_path,
        media_type=resource.content_type or ALLOWED_UPLOAD_CONTENT_TYPE,
        filename=resource.original_filename or resource.storage_key,
    )


@router.delete("/{sheet_resource_id}", status_code=204)
def delete_sheet_resource(sheet_resource_id: int, db: Session = Depends(get_db)) -> None:
    resource = db.get(SheetResource, sheet_resource_id)
    if resource is None:
        raise HTTPException(status_code=404, detail="Sheet resource not found")
    if resource.kind == SheetResourceKind.UPLOADED and resource.storage_key is not None:
        file_path = Path(settings.sheet_resource_storage_dir) / resource.storage_key
        file_path.unlink(missing_ok=True)
    db.delete(resource)
    db.commit()
