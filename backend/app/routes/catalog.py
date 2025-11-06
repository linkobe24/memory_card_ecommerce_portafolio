"""
Endpoints de catálogo de juegos.

Proxy de RAWG API con cache en Redis.
"""

from typing import Annotated
from fastapi import APIRouter, Depends, HTTPException, status

from app.clients.rawg.rawg_client import RAWGClient, RAWGAPIError, RateLimitError
from app.core.dependencies import CatalogServiceDep
from app.schemas.rawg import (
    GameListResponse,
    GameDetail,
    GameSearchParams,
    GenreListResponse,
    PlatformListResponse,
)

router = APIRouter()


@router.get("/search", response_model=GameListResponse)
async def search_games(
    params: Annotated[GameSearchParams, Depends()], catalog_service: CatalogServiceDep
):
    """
    Busca juegos en RAWG API.

    Ejemplos:
    - `/api/catalog/search?query=mario`
    - `/api/catalog/search?query=zelda&genres=4&platforms=7`
    - `/api/catalog/search?query=shooter&page=2&page_size=10`
    """
    try:
        return await catalog_service.search_games(**params.model_dump())
    except RateLimitError as e:
        raise HTTPException(
            status_code=status.HTTP_429_TOO_MANY_REQUESTS,
            detail=str(e),
        )
    except RAWGAPIError as e:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail=f"Error al consultar RAWG API: {str(e)}",
        )


@router.get("/game/{game_id}", response_model=GameDetail)
async def get_game_details(game_id: int, catalog_service: CatalogServiceDep):
    """
    Obtiene detalles completos de un juego.

    Ejemplo: `/api/catalog/game/3498` (GTA V)
    """
    try:
        return await catalog_service.get_game_details(game_id)
    except RateLimitError as e:
        raise HTTPException(
            status_code=status.HTTP_429_TOO_MANY_REQUESTS,
            detail=str(e),
        )
    except RAWGAPIError as e:
        if "404" in str(e):
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Juego con ID {game_id} no encontrado en RAWG",
            )
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail=f"Error al consultar RAWG API: {str(e)}",
        )


@router.get("/genres", response_model=GenreListResponse)
async def list_genres(catalog_service: CatalogServiceDep):
    """
    Lista todos los géneros disponibles.

    Ejemplo: `/api/catalog/genres`
    """
    try:
        return await catalog_service.list_genres()
    except RAWGAPIError as e:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail=f"Error al consultar RAWG API: {str(e)}",
        )


@router.get("/platforms", response_model=PlatformListResponse)
async def list_platforms(catalog_service: CatalogServiceDep):
    """
    Lista todas las plataformas disponibles.

    Ejemplo: `/api/catalog/platforms`
    """
    try:
        return await catalog_service.list_platforms()
    except RAWGAPIError as e:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail=f"Error al consultar RAWG API: {str(e)}",
        )
