import subprocess
import uuid
from dataclasses import dataclass
from pathlib import Path

from fastapi import HTTPException, UploadFile

from repertoire.config import settings

ALLOWED_UPLOAD_CONTENT_TYPE = "application/pdf"
THUMBNAIL_TIMEOUT_SECONDS = 15


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


def generate_pdf_thumbnail(pdf_path: Path) -> str | None:
    """Best-effort first-page PNG thumbnail via Poppler's pdftoppm.

    Never raises: a missing binary, a corrupt PDF, or a timeout all just
    mean no preview image, not a failed upload.
    """
    thumbnail_stem = uuid.uuid4().hex
    output_prefix = pdf_path.parent / thumbnail_stem
    try:
        subprocess.run(
            [
                "pdftoppm",
                "-png",
                "-f",
                "1",
                "-l",
                "1",
                "-scale-to",
                "400",
                "-singlefile",
                str(pdf_path),
                str(output_prefix),
            ],
            check=True,
            capture_output=True,
            timeout=THUMBNAIL_TIMEOUT_SECONDS,
        )
    except (subprocess.SubprocessError, OSError):
        return None

    thumbnail_key = f"{thumbnail_stem}.png"
    if not (pdf_path.parent / thumbnail_key).is_file():
        return None
    return thumbnail_key
