from datetime import datetime
from enum import StrEnum

from sqlalchemy import DateTime, ForeignKey, Integer, String, func
from sqlalchemy import Enum as SAEnum
from sqlalchemy.orm import Mapped, mapped_column

from repertoire.db import Base


class SheetResourceKind(StrEnum):
    URL = "url"
    PHYSICAL = "physical"
    LOCAL_DOC = "local-doc"
    UPLOADED = "uploaded"


class SheetResource(Base):
    __tablename__ = "sheet_resources"

    id: Mapped[int] = mapped_column(primary_key=True)
    piece_id: Mapped[int] = mapped_column(
        ForeignKey("pieces.id", ondelete="CASCADE"), index=True
    )
    kind: Mapped[SheetResourceKind] = mapped_column(
        SAEnum(
            SheetResourceKind,
            name="sheet_resource_kind",
            values_callable=lambda obj: [e.value for e in obj],
        )
    )
    reference: Mapped[str] = mapped_column(String(1000))
    label: Mapped[str | None] = mapped_column(String(200), default=None)
    notes: Mapped[str | None] = mapped_column(String(2000), default=None)
    original_filename: Mapped[str | None] = mapped_column(String(255), default=None)
    content_type: Mapped[str | None] = mapped_column(String(100), default=None)
    file_size_bytes: Mapped[int | None] = mapped_column(Integer, default=None)
    storage_key: Mapped[str | None] = mapped_column(String(255), default=None)
    thumbnail_key: Mapped[str | None] = mapped_column(String(255), default=None)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), onupdate=func.now()
    )
