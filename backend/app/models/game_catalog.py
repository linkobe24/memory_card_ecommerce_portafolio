"""
Modelo de catálogo de juegos (productos de la tienda).

Almacena los juegos disponibles para venta con precios y stock local.
Relaciona con RAWG API mediante rawg_id.
"""

from sqlalchemy import String, Integer, Numeric, DateTime, func, ForeignKey, Text
from sqlalchemy.orm import Mapped, mapped_column, relationship
from app.core.database import Base
from datetime import datetime


class GameCatalog(Base):
    """
    Productos de la tienda (juegos disponibles para compra).

    Combina metadata de RAWG (rawg_id) con datos locales (precio, stock).
    """

    __tablename__ = "game_catalog"

    id: Mapped[int] = mapped_column(primary_key=True, index=True)
    rawg_id: Mapped[int] = mapped_column(
        Integer, unique=True, index=True, nullable=False
    )

    # Metadata básica (duplicada de RAWG para queries rápidas)
    title: Mapped[str] = mapped_column(String(255), nullable=False, index=True)
    slug: Mapped[str] = mapped_column(String(255), nullable=False)
    description: Mapped[str | None] = mapped_column(Text, nullable=True)
    image_url: Mapped[str | None] = mapped_column(String(500), nullable=True)

    # Datos locales (controlados por admin)
    price: Mapped[float] = mapped_column(Numeric(10, 2), nullable=False)
    stock: Mapped[int] = mapped_column(Integer, default=0, nullable=False)

    # Auditoría
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now()
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), onupdate=func.now()
    )

    # Relaciones
    cart_items: Mapped[list["CartItem"]] = relationship(
        "CartItem", back_populates="game", cascade="all, delete-orphan"
    )
    order_items: Mapped[list["OrderItem"]] = relationship(
        "OrderItem", back_populates="game"
    )
    reviews: Mapped[list["Review"]] = relationship(
        "Review", back_populates="game", cascade="all, delete-orphan"
    )

    def __repr__(self):
        return f"<GameCatalog(id={self.id}, title={self.title}, price={self.price}, stock={self.stock})>"
