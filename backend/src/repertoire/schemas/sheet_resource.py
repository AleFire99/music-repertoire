from datetime import datetime

from pydantic import BaseModel, ConfigDict

from repertoire.models.sheet_resource import SheetResourceKind


class SheetResourceCreate(BaseModel):
    piece_id: int
    kind: SheetResourceKind
    reference: str
    label: str | None = None
    notes: str | None = None


class SheetResourceRead(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    piece_id: int
    kind: SheetResourceKind
    reference: str
    label: str | None
    notes: str | None
    original_filename: str | None
    content_type: str | None
    file_size_bytes: int | None
    thumbnail_key: str | None
    created_at: datetime
    updated_at: datetime
