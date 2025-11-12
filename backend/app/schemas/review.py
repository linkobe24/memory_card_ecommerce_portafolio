"""
Schemas para reseñas de productos.

Validación de requests y responses para endpoints de reseñas.
"""

from pydantic import BaseModel, Field, ConfigDict
from datetime import datetime


class ReviewCreate(BaseModel):
    """Schema para crear reseña."""

    game_id: int = Field(..., description="ID del juego a reseñar")
    rating: int = Field(..., ge=1, le=5, description="Calificación de 1 a 5 estrellas")
    comment: str | None = Field(
        None, max_length=1000, description="Comentario opcional"
    )


class ReviewUpdate(BaseModel):
    """Schema para actualizar reseña."""

    rating: int | None = Field(None, ge=1, le=5)
    comment: str | None = Field(None, max_length=1000)


class ReviewResponse(BaseModel):
    """Respuesta de reseña con metadata del usuario."""

    id: int
    game_id: int
    user_id: int
    user_name: str  # Nombre del usuario que escribió la reseña
    rating: int
    comment: str | None
    created_at: datetime
    updated_at: datetime

    model_config = ConfigDict(from_attributes=True)


class ReviewListResponse(BaseModel):
    """Respuesta paginada de reseñas."""

    total: int
    page: int
    page_size: int
    average_rating: float  # Promedio de todas las reseñas del juego
    results: list[ReviewResponse]
