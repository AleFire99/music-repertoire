from collections import defaultdict
from pathlib import Path

from fastapi import APIRouter, Depends, File, HTTPException, UploadFile
from sqlalchemy import any_, or_
from sqlalchemy.orm import Session

from repertoire.config import settings
from repertoire.db import get_db
from repertoire.models.piece import Piece, PieceDifficulty, PieceStatus
from repertoire.models.sheet_resource import SheetResource, SheetResourceKind
from repertoire.musicbrainz import find_composer_for_title
from repertoire.pdf_metadata import extract_title_and_composer
from repertoire.pdf_upload import generate_pdf_thumbnail, validate_and_store_pdf
from repertoire.schemas.piece import PieceCreate, PieceRead, PieceUpdate

router = APIRouter(prefix="/pieces", tags=["pieces"])

KIND_ORDER = {kind: index for index, kind in enumerate(SheetResourceKind)}
DEFAULT_QUICK_UPLOAD_TITLE = "Untitled piece"


def _attach_sheet_resource_kinds(pieces: list[Piece], db: Session) -> None:
    piece_ids = [piece.id for piece in pieces]
    kinds_by_piece: dict[int, list[SheetResourceKind]] = defaultdict(list)
    preview_by_piece: dict[int, int] = {}
    if piece_ids:
        rows = (
            db.query(SheetResource.piece_id, SheetResource.kind)
            .filter(SheetResource.piece_id.in_(piece_ids))
            .distinct()
            .all()
        )
        for piece_id, kind in rows:
            kinds_by_piece[piece_id].append(kind)

        preview_rows = (
            db.query(SheetResource.piece_id, SheetResource.id)
            .filter(
                SheetResource.piece_id.in_(piece_ids),
                SheetResource.kind == SheetResourceKind.UPLOADED,
                SheetResource.thumbnail_key.isnot(None),
            )
            .order_by(
                SheetResource.piece_id,
                SheetResource.created_at.desc(),
                SheetResource.id.desc(),
            )
            .all()
        )
        for piece_id, resource_id in preview_rows:
            preview_by_piece.setdefault(piece_id, resource_id)

    for piece in pieces:
        piece.sheet_resource_kinds = sorted(  # type: ignore[attr-defined]
            kinds_by_piece.get(piece.id, []), key=lambda kind: KIND_ORDER[kind]
        )
        piece.preview_sheet_resource_id = preview_by_piece.get(piece.id)  # type: ignore[attr-defined]


@router.post("", response_model=PieceRead, status_code=201)
def create_piece(payload: PieceCreate, db: Session = Depends(get_db)) -> Piece:
    piece = Piece(**payload.model_dump())
    db.add(piece)
    db.commit()
    db.refresh(piece)
    _attach_sheet_resource_kinds([piece], db)
    return piece


def _title_from_filename(filename: str | None) -> str | None:
    if not filename:
        return None
    stem = Path(filename).stem.strip()
    return stem or None


@router.post("/quick-upload", response_model=PieceRead, status_code=201)
def quick_upload_piece(file: UploadFile = File(...), db: Session = Depends(get_db)) -> Piece:
    stored = validate_and_store_pdf(file)
    thumbnail_key = generate_pdf_thumbnail(
        Path(settings.sheet_resource_storage_dir) / stored.storage_key
    )

    extracted_title, extracted_composer = extract_title_and_composer(stored.contents)
    title = (
        extracted_title
        or _title_from_filename(stored.original_filename)
        or DEFAULT_QUICK_UPLOAD_TITLE
    )
    composer = extracted_composer or find_composer_for_title(title)

    piece = Piece(title=title, composer=composer)
    db.add(piece)
    db.flush()

    resource = SheetResource(
        piece_id=piece.id,
        kind=SheetResourceKind.UPLOADED,
        reference=stored.original_filename or stored.storage_key,
        original_filename=stored.original_filename,
        content_type=stored.content_type,
        file_size_bytes=len(stored.contents),
        storage_key=stored.storage_key,
        thumbnail_key=thumbnail_key,
    )
    db.add(resource)
    db.commit()
    db.refresh(piece)
    _attach_sheet_resource_kinds([piece], db)
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
    pieces = list(query.order_by(Piece.id).all())
    _attach_sheet_resource_kinds(pieces, db)
    return pieces


def _get_piece_or_404(piece_id: int, db: Session) -> Piece:
    piece = db.get(Piece, piece_id)
    if piece is None:
        raise HTTPException(status_code=404, detail="Piece not found")
    return piece


@router.get("/{piece_id}", response_model=PieceRead)
def get_piece(piece_id: int, db: Session = Depends(get_db)) -> Piece:
    piece = _get_piece_or_404(piece_id, db)
    _attach_sheet_resource_kinds([piece], db)
    return piece


@router.patch("/{piece_id}", response_model=PieceRead)
def update_piece(piece_id: int, payload: PieceUpdate, db: Session = Depends(get_db)) -> Piece:
    piece = _get_piece_or_404(piece_id, db)
    for field, value in payload.model_dump(exclude_unset=True).items():
        setattr(piece, field, value)
    db.commit()
    db.refresh(piece)
    _attach_sheet_resource_kinds([piece], db)
    return piece


@router.delete("/{piece_id}", status_code=204)
def delete_piece(piece_id: int, db: Session = Depends(get_db)) -> None:
    piece = _get_piece_or_404(piece_id, db)
    db.delete(piece)
    db.commit()
