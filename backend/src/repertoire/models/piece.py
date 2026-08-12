from datetime import datetime
from enum import StrEnum

from sqlalchemy import Boolean, DateTime, String, func
from sqlalchemy import Enum as SAEnum
from sqlalchemy.dialects.postgresql import ARRAY
from sqlalchemy.orm import Mapped, mapped_column

from repertoire.db import Base


class PieceStatus(StrEnum):
    BACKLOG = "backlog"
    LEARNING = "learning"
    MEMORIZED = "memorized"
    MAINTAINING = "maintaining"
    PERFORMANCE_READY = "performance-ready"
    ARCHIVED = "archived"


class Piece(Base):
    __tablename__ = "pieces"

    id: Mapped[int] = mapped_column(primary_key=True)
    title: Mapped[str] = mapped_column(String(200))
    composer: Mapped[str | None] = mapped_column(String(200), default=None)
    status: Mapped[PieceStatus] = mapped_column(
        SAEnum(
            PieceStatus,
            name="piece_status",
            values_callable=lambda obj: [e.value for e in obj],
        ),
        default=PieceStatus.BACKLOG,
        server_default=PieceStatus.BACKLOG.value,
    )
    tags: Mapped[list[str]] = mapped_column(ARRAY(String(50)), default=list, server_default="{}")
    is_favorite: Mapped[bool] = mapped_column(Boolean, default=False, server_default="false")
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), onupdate=func.now()
    )
