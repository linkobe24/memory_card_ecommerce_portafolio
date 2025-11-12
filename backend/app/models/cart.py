"""
Modelos para carrito de compras.

Un usuario tiene un carrito activo que contiene múltiples items (cart_items).
"""

from sqlalchemy import Integer, DateTime, func, ForeignKey
from sqlalchemy.orm import Mapped, mapped_column, relationship
from app.core.database import Base
from datetime import datetime


class Cart(Base):
    """
    Carrito de compras de un usuario.

    Relación: Un usuario → un carrito activo → muchos cart_items
    """

    __tablename__ = "carts"

    id: Mapped[int] = mapped_column(primary_key=True, index=True)
    user_id: Mapped[int] = mapped_column(
        ForeignKey("users.id", ondelete="CASCADE"),
        unique=True,  # Un usuario solo tiene un carrito activo
        index=True,
        nullable=False,
    )

    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now()
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), onupdate=func.now()
    )

    # Relaciones
    user: Mapped["User"] = relationship("User", back_populates="cart")
    items: Mapped[list["CartItem"]] = relationship(
        "CartItem", back_populates="cart", cascade="all, delete-orphan"
    )

    def __repr__(self):
        return f"<Cart(id={self.id}, user_id={self.user_id}, items={len(self.items)})>"


class CartItem(Base):
    """
    Item individual dentro de un carrito.

    Representa: "Cantidad X del juego Y en el carrito Z"
    """

    __tablename__ = "cart_items"

    id: Mapped[int] = mapped_column(primary_key=True, index=True)
    cart_id: Mapped[int] = mapped_column(
        ForeignKey("carts.id", ondelete="CASCADE"), nullable=False, index=True
    )
    game_id: Mapped[int] = mapped_column(
        ForeignKey("game_catalog.id", ondelete="CASCADE"), nullable=False, index=True
    )
    quantity: Mapped[int] = mapped_column(Integer, default=1, nullable=False)

    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now()
    )

    # Relaciones
    cart: Mapped["Cart"] = relationship("Cart", back_populates="items")
    game: Mapped["GameCatalog"] = relationship(
        "GameCatalog", back_populates="cart_items"
    )

    def __repr__(self):
        return f"<CartItem(id={self.id}, game_id={self.game_id}, quantity={self.quantity})>"
