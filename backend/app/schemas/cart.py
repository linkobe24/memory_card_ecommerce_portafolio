"""
Schemas para carrito de compras.

Validación de requests y responses para endpoints de carrito.
"""

from pydantic import BaseModel, Field, ConfigDict
from datetime import datetime


class CartItemBase(BaseModel):
    """Campos comunes de item de carrito."""

    game_id: int
    quantity: int = Field(..., ge=1, description="Cantidad debe ser mayor a 0")


class CartItemCreate(CartItemBase):
    """Schema para agregar item al carrito."""

    pass


class CartItemUpdate(BaseModel):
    """Schema para actualizar cantidad de item."""

    quantity: int = Field(..., ge=1, description="Cantidad debe ser mayor a 0")


class CartItemResponse(CartItemBase):
    """Respuesta de item de carrito con metadata del juego."""

    id: int
    # Metadata del juego (join)
    game_title: str
    game_image: str | None
    game_price: float
    subtotal: float  # quantity * price
    in_stock: bool

    model_config = ConfigDict(from_attributes=True)


class CartResponse(BaseModel):
    """Respuesta completa de carrito."""

    id: int
    user_id: int
    items: list[CartItemResponse]
    total: float
    created_at: datetime
    updated_at: datetime

    model_config = ConfigDict(from_attributes=True)
