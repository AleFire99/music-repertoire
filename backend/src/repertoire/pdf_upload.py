import uuid
from dataclasses import dataclass
from pathlib import Path

from fastapi import HTTPException, UploadFile

from repertoire.config import settings

ALLOWED_UPLOAD_CONTENT_TYPE = "application/pdf"


@dataclass
class StoredPdf:
    storage_key: str
    contents: bytes
    original_filename: str | None
    content_type: str | None


def validate_and_store_pdf(file: UploadFile) -> StoredPdf:
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

    return StoredPdf(
        storage_key=storage_key,
        contents=contents,
        original_filename=file.filename,
        content_type=file.content_type,
    )
