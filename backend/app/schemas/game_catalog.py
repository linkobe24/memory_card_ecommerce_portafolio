"""
Schemas para GameCatalog (productos de la tienda).

Validación de requests y responses para endpoints de productos.
"""

from pydantic import BaseModel, Field, ConfigDict
from datetime import datetime


class GameCatalogBase(BaseModel):
    """Campos comunes para crear/actualizar productos."""

    title: str = Field(..., min_length=1, max_length=255)
    slug: str = Field(..., min_length=1, max_length=255)
    description: str | None = None
    image_url: str | None = Field(None, max_length=500)
    price: float = Field(..., gt=0, description="Precio debe ser mayor a 0")
    stock: int = Field(..., ge=0, description="Stock no puede ser negativo")


class GameCatalogCreate(BaseModel):
    """
    Schema para crear producto.

    Admin proporciona rawg_id y datos locales.
    """

    rawg_id: int = Field(..., description="ID del juego en RAWG API")
    price: float = Field(..., gt=0, description="Precio en USD")
    stock: int = Field(default=0, ge=0, description="Stock inicial")


class GameCatalogUpdate(BaseModel):
    """
    Schema para actualizar producto.

    Todos los campos son opcionales (partial update).
    """

    price: float | None = Field(None, gt=0)
    stock: int | None = Field(None, ge=0)
    description: str | None = None


class GameCatalogResponse(GameCatalogBase):
    """
    Respuesta completa de producto (datos locales + metadata RAWG).
    """

    id: int
    rawg_id: int
    created_at: datetime
    updated_at: datetime

    model_config = ConfigDict(from_attributes=True)


class GameCatalogEnriched(BaseModel):
    """
    Producto enriquecido con datos de RAWG API.

    Combina datos locales (precio, stock) con metadata de RAWG.
    """

    # Datos locales
    id: int
    rawg_id: int
    price: float
    stock: int
    in_stock: bool

    # Metadata de RAWG (obtenida en runtime)
    name: str
    slug: str
    description: str | None
    background_image: str | None
    rating: float | None
    released: str | None
    platforms: list[dict] | None
    genres: list[dict] | None

    model_config = ConfigDict(from_attributes=True)


class GameCatalogListResponse(BaseModel):
    """Respuesta paginada de productos."""

    total: int
    page: int
    page_size: int
    results: list[GameCatalogResponse]
