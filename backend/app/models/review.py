"""
Modelo de reseñas de productos.

Los usuarios pueden calificar y comentar juegos que han comprado (o no, según reglas).
"""

from sqlalchemy import (
    Integer,
    DateTime,
    func,
    ForeignKey,
    Text,
    CheckConstraint,
)
from sqlalchemy.orm import Mapped, mapped_column, relationship
from app.core.database import Base
from datetime import datetime


class Review(Base):
    """
    Reseña de un juego por un usuario.

    Incluye rating (1-5 estrellas) y comentario opcional.
    """

    __tablename__ = "reviews"

    # Constraint para rating entre 1 y 5
    __table_args__ = (
        CheckConstraint("rating >= 1 AND rating <= 5", name="check_rating_range"),
    )

    id: Mapped[int] = mapped_column(primary_key=True, index=True)
    game_id: Mapped[int] = mapped_column(
        ForeignKey("game_catalog.id", ondelete="CASCADE"), nullable=False, index=True
    )
    user_id: Mapped[int] = mapped_column(
        ForeignKey("users.id", ondelete="CASCADE"), nullable=False, index=True
    )

    rating: Mapped[int] = mapped_column(Integer, nullable=False)  # 1-5
    comment: Mapped[str | None] = mapped_column(Text, nullable=True)

    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now()
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), onupdate=func.now()
    )

    # Relaciones
    game: Mapped["GameCatalog"] = relationship("GameCatalog", back_populates="reviews")
    user: Mapped["User"] = relationship("User", back_populates="reviews")

    def __repr__(self):
        return f"<Review(id={self.id}, game_id={self.game_id}, user_id={self.user_id}, rating={self.rating})>"
