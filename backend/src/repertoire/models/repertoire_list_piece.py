from sqlalchemy import ForeignKey
from sqlalchemy.orm import Mapped, mapped_column

from repertoire.db import Base


class RepertoireListPiece(Base):
    __tablename__ = "repertoire_list_pieces"

    repertoire_list_id: Mapped[int] = mapped_column(
        ForeignKey("repertoire_lists.id", ondelete="CASCADE"), primary_key=True
    )
    piece_id: Mapped[int] = mapped_column(
        ForeignKey("pieces.id", ondelete="CASCADE"), primary_key=True, index=True
    )
