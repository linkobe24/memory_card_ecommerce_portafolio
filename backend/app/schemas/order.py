"""
Schemas para órdenes de compra.

Validación de requests y responses para endpoints de órdenes.
"""

from pydantic import BaseModel, Field, ConfigDict
from datetime import datetime
from app.models.order import OrderStatus


class OrderItemResponse(BaseModel):
    """Item de orden con snapshot del momento de compra."""

    id: int
    game_id: int
    game_title: str  # Snapshot
    quantity: int
    unit_price: float
    subtotal: float

    model_config = ConfigDict(from_attributes=True)


class OrderCreate(BaseModel):
    """
    Schema para crear orden (después de pago exitoso).

    En Etapa 6 (Stripe), este schema será usado por el webhook.
    """

    stripe_payment_intent_id: str | None = None


class OrderResponse(BaseModel):
    """Respuesta completa de orden."""

    id: int
    user_id: int
    subtotal: float
    tax: float
    total: float
    status: OrderStatus
    stripe_payment_intent_id: str | None
    items: list[OrderItemResponse]
    created_at: datetime
    completed_at: datetime | None

    model_config = ConfigDict(from_attributes=True)


class OrderStatusUpdate(BaseModel):
    """Schema para actualizar estado de orden (admin)."""

    status: OrderStatus = Field(..., description="Nuevo estado de la orden")


class OrderListResponse(BaseModel):
    """Respuesta paginada de órdenes."""

    total: int
    page: int
    page_size: int
    results: list[OrderResponse]
