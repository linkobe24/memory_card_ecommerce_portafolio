"""
Endpoints de productos (GameCatalog).

- Endpoints públicos: listar, ver detalle (cualquier usuario)
- Endpoints admin: crear, actualizar, eliminar (solo admin)
"""

from fastapi import APIRouter, Depends, HTTPException, status, Query
from app.services.game_catalog_service import GameCatalogService
from app.crud.game_catalog_interface import GameCatalogRepositoryInterface
from app.crud.game_catalog_repository import PostgresGameCatalogRepository
from app.clients.rawg.rawg_client import RAWGClient, RAWGAPIError
from app.core.dependencies import get_rawg_client_dep
from app.core.database import get_db
from app.schemas.game_catalog import (
    GameCatalogCreate,
    GameCatalogUpdate,
    GameCatalogResponse,
    GameCatalogEnriched,
)
from app.middleware.auth import CurrentAdmin
from sqlalchemy.ext.asyncio import AsyncSession

router = APIRouter()


def get_game_catalog_repository(
    db: AsyncSession = Depends(get_db),
) -> GameCatalogRepositoryInterface:
    return PostgresGameCatalogRepository(db)


def get_game_catalog_service(
    game_repo: GameCatalogRepositoryInterface = Depends(get_game_catalog_repository),
    rawg_client: RAWGClient = Depends(get_rawg_client_dep),
) -> GameCatalogService:
    return GameCatalogService(game_repo, rawg_client)


# ========== Endpoints Admin ==========


@router.post(
    "",
    response_model=GameCatalogResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Crear producto (Admin)",
)
async def create_product(
    data: GameCatalogCreate,
    current_user: CurrentAdmin,
    service: GameCatalogService = Depends(get_game_catalog_service),
):
    """
    Crea un producto combinando datos locales y metadata de RAWG (solo admin).

    Verifica duplicados por `rawg_id` y propaga errores de negocio como HTTP 400.
    """
    try:
        return await service.create_product(data)
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e),
        )
    except RAWGAPIError as e:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail=f"Error al consultar RAWG API: {str(e)}",
        )


@router.put(
    "/{game_id}",
    response_model=GameCatalogResponse,
    summary="Actualizar producto (Admin)",
)
async def update_product(
    game_id: int,
    data: GameCatalogUpdate,
    current_user: CurrentAdmin,
    service: GameCatalogService = Depends(get_game_catalog_service),
):
    """Actualiza precio, stock o descripción de un producto existente (admin)."""
    game = await service.update_product(game_id, data)
    if not game:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Producto con ID {game_id} no encontrado",
        )
    return game


@router.delete(
    "/{game_id}",
    status_code=status.HTTP_204_NO_CONTENT,
    summary="Eliminar producto (Admin)",
)
async def delete_product(
    game_id: int,
    current_user: CurrentAdmin,
    service: GameCatalogService = Depends(get_game_catalog_service),
):
    """
    Elimina un producto del catálogo siempre que no esté referenciado en órdenes.
    """
    deleted = await service.delete_product(game_id)
    if not deleted:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Producto con ID {game_id} no encontrado",
        )


# ========== Endpoints Públicos ==========


@router.get(
    "",
    response_model=dict,
    summary="Listar productos",
)
async def list_products(
    page: int = Query(1, ge=1, description="Número de página"),
    page_size: int = Query(20, ge=1, le=100, description="Items por página"),
    in_stock_only: bool = Query(False, description="Solo productos en stock"),
    service: GameCatalogService = Depends(get_game_catalog_service),
):
    """
    Lista productos paginados con opción de filtrar por stock disponible.

    Endpoint público pensado para el storefront.
    """
    return await service.list_products(page, page_size, in_stock_only)


@router.get(
    "/{game_id}",
    response_model=GameCatalogEnriched,
    summary="Obtener detalle de producto",
)
async def get_product_details(
    game_id: int,
    service: GameCatalogService = Depends(get_game_catalog_service),
):
    """
    Retorna la ficha enriquecida de un producto mezclando datos locales y RAWG.
    """
    game = await service.get_product_enriched(game_id)
    if not game:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Producto con ID {game_id} no encontrado",
        )
    return game
