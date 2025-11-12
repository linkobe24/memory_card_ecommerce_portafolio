"""
Endpoints de reseñas.

- Crear reseña (autenticado)
- Listar reseñas de juego (público)
- Actualizar/eliminar reseña (solo autor)
"""

from fastapi import APIRouter, Depends, HTTPException, status, Query
from app.services.review_service import ReviewService
from app.crud.review_repository import PostgresReviewRepository
from app.crud.game_catalog_repository import PostgresGameCatalogRepository
from app.core.database import get_db
from app.schemas.review import (
    ReviewCreate,
    ReviewUpdate,
    ReviewResponse,
    ReviewListResponse,
)
from app.middleware.auth import CurrentUser
from sqlalchemy.ext.asyncio import AsyncSession

router = APIRouter()


def get_review_service(
    db: AsyncSession = Depends(get_db),
) -> ReviewService:
    """Factory para servicio de reseñas."""
    review_repo = PostgresReviewRepository(db)
    game_repo = PostgresGameCatalogRepository(db)
    return ReviewService(review_repo, game_repo)


@router.post(
    "",
    response_model=ReviewResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Crear reseña",
)
async def create_review(
    data: ReviewCreate,
    current_user: CurrentUser,
    service: ReviewService = Depends(get_review_service),
):
    """
    Crea la única reseña permitida para un juego por usuario autenticado.

    Valida que el juego exista, evita duplicados y traduce errores de negocio a
    HTTP 400.
    """
    try:
        return await service.create_review(current_user.id, data)
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e),
        )


@router.get(
    "/game/{game_id}",
    response_model=ReviewListResponse,
    summary="Listar reseñas de juego",
)
async def list_game_reviews(
    game_id: int,
    page: int = Query(1, ge=1),
    page_size: int = Query(20, ge=1, le=100),
    service: ReviewService = Depends(get_review_service),
):
    """
    Devuelve reseñas paginadas de un juego junto al promedio de rating agregado.

    Endpoint público ideal para mostrar feedback en la ficha del producto.
    """
    return await service.list_game_reviews(game_id, page, page_size)


@router.put(
    "/{review_id}",
    response_model=ReviewResponse,
    summary="Actualizar reseña",
)
async def update_review(
    review_id: int,
    data: ReviewUpdate,
    current_user: CurrentUser,
    service: ReviewService = Depends(get_review_service),
):
    """
    Permite al autor modificar rating o comentario de su reseña.

    Retorna 404 cuando la reseña no existe o pertenece a otro usuario.
    """
    try:
        review = await service.update_review(review_id, data, current_user.id)
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail=str(e),
        )
    if not review:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Reseña con ID {review_id} no encontrada o no pertenece al usuario",
        )
    return review


@router.delete(
    "/{review_id}",
    status_code=status.HTTP_204_NO_CONTENT,
    summary="Eliminar reseña",
)
async def delete_review(
    review_id: int,
    current_user: CurrentUser,
    service: ReviewService = Depends(get_review_service),
):
    """
    Elimina una reseña propiedad del usuario autenticado y devuelve 204 en éxito.

    Traduce ausencia o falta de ownership a HTTP 404.
    """
    try:
        deleted = await service.delete_review(
            review_id, current_user.id, enforce_owner_error=True
        )
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail=str(e),
        )
    if not deleted:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Reseña con ID {review_id} no encontrada o no pertenece al usuario",
        )
