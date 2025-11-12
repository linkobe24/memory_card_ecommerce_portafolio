"""
Modelos para órdenes de compra.

Una orden registra la compra completa de un usuario, con sus items y estado.
"""

from sqlalchemy import String, Integer, Numeric, DateTime, func, ForeignKey, Enum
from sqlalchemy.orm import Mapped, mapped_column, relationship
from app.core.database import Base
from datetime import datetime
import enum


class OrderStatus(str, enum.Enum):
    """Estados posibles de una orden."""

    PENDING = "pending"  # Creada, esperando pago
    PAID = "paid"  # Pagada (Stripe confirmó)
    COMPLETED = "completed"  # Entregada/completada
    CANCELLED = "cancelled"  # Cancelada (por admin o sistema)


class Order(Base):
    """
    Orden de compra completada por un usuario.

    Se crea después de un checkout exitoso con Stripe.
    """

    __tablename__ = "orders"

    id: Mapped[int] = mapped_column(primary_key=True, index=True)
    user_id: Mapped[int] = mapped_column(
        ForeignKey("users.id", ondelete="CASCADE"), nullable=False, index=True
    )

    # Totales
    subtotal: Mapped[float] = mapped_column(Numeric(10, 2), nullable=False)
    tax: Mapped[float] = mapped_column(Numeric(10, 2), default=0.0, nullable=False)
    total: Mapped[float] = mapped_column(Numeric(10, 2), nullable=False)

    # Estado
    status: Mapped[OrderStatus] = mapped_column(
        Enum(OrderStatus), default=OrderStatus.PENDING, nullable=False, index=True
    )

    # Stripe
    stripe_payment_intent_id: Mapped[str | None] = mapped_column(
        String(255), unique=True, nullable=True, index=True
    )

    # Auditoría
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now()
    )
    completed_at: Mapped[datetime | None] = mapped_column(
        DateTime(timezone=True), nullable=True
    )

    # Relaciones
    user: Mapped["User"] = relationship("User", back_populates="orders")
    items: Mapped[list["OrderItem"]] = relationship(
        "OrderItem", back_populates="order", cascade="all, delete-orphan"
    )

    def __repr__(self):
        return f"<Order(id={self.id}, user_id={self.user_id}, total={self.total}, status={self.status})>"


class OrderItem(Base):
    """
    Item individual dentro de una orden.

    Snapshot del producto en el momento de compra (precio puede cambiar después).
    """

    __tablename__ = "order_items"

    id: Mapped[int] = mapped_column(primary_key=True, index=True)
    order_id: Mapped[int] = mapped_column(
        ForeignKey("orders.id", ondelete="CASCADE"), nullable=False, index=True
    )
    game_id: Mapped[int] = mapped_column(
        ForeignKey(
            "game_catalog.id", ondelete="RESTRICT"
        ),  # No eliminar juego si está en órdenes
        nullable=False,
        index=True,
    )

    # Snapshot del momento de compra
    quantity: Mapped[int] = mapped_column(Integer, nullable=False)
    unit_price: Mapped[float] = mapped_column(Numeric(10, 2), nullable=False)
    subtotal: Mapped[float] = mapped_column(Numeric(10, 2), nullable=False)

    # Relaciones
    order: Mapped["Order"] = relationship("Order", back_populates="items")
    game: Mapped["GameCatalog"] = relationship(
        "GameCatalog", back_populates="order_items"
    )

    def __repr__(self):
        return f"<OrderItem(id={self.id}, game_id={self.game_id}, quantity={self.quantity}, subtotal={self.subtotal})>"
