"""
Endpoints de carrito de compras.

Todos los endpoints requieren autenticación (usuario debe estar logueado).
"""

from fastapi import APIRouter, Depends, HTTPException, status
from app.services.cart_service import CartService
from app.crud.cart_repository import PostgresCartRepository
from app.crud.game_catalog_repository import PostgresGameCatalogRepository
from app.core.database import get_db
from app.schemas.cart import CartResponse, CartItemCreate, CartItemUpdate
from sqlalchemy.ext.asyncio import AsyncSession
from app.middleware.auth import CurrentUser

router = APIRouter()


def get_cart_service(
    db: AsyncSession = Depends(get_db),
) -> CartService:
    """
    Factory para servicio de carrito.

    Comparte la misma sesión de base de datos entre los repositorios para asegurar
    consistencia cuando se combinan operaciones (ej. validar stock y actualizar items).
    """
    cart_repo = PostgresCartRepository(db)
    game_repo = PostgresGameCatalogRepository(db)
    return CartService(cart_repo, game_repo)


@router.post(
    "/items",
    response_model=CartResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Agregar item al carrito",
)
async def add_to_cart(
    data: CartItemCreate,
    current_user: CurrentUser,
    service: CartService = Depends(get_cart_service),
):
    """
    Agrega o incrementa un juego en el carrito del usuario autenticado.

    Valida que el producto exista y tenga stock suficiente antes de delegar la
    operación al servicio. Devuelve el carrito completo con subtotales
    actualizados; levanta HTTP 400 si la validación de negocio falla.
    """
    try:
        return await service.add_to_cart(current_user.id, data)
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e),
        )


@router.get(
    "",
    response_model=CartResponse,
    summary="Ver carrito",
)
async def get_cart(
    current_user: CurrentUser,
    service: CartService = Depends(get_cart_service),
):
    """
    Devuelve un snapshot del carrito del usuario, incluyendo items y totales.

    Crea el carrito si todavía no existe para el usuario y retorna siempre la
    misma estructura para facilitar al frontend el refresco de la UI.
    """
    return await service.get_cart(current_user.id)


@router.put(
    "/items/{item_id}",
    response_model=CartResponse,
    summary="Actualizar cantidad de item",
)
async def update_cart_item(
    item_id: int,
    data: CartItemUpdate,
    current_user: CurrentUser,
    service: CartService = Depends(get_cart_service),
):
    """
    Actualiza la cantidad de un item del carrito asegurando ownership y stock.

    El servicio valida que el item pertenezca al usuario y que exista stock
    suficiente para la nueva cantidad; en caso contrario lanza HTTP 400.
    """
    try:
        return await service.update_item(item_id, data, current_user.id)
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e),
        )


@router.delete(
    "/items/{item_id}",
    status_code=status.HTTP_204_NO_CONTENT,
    summary="Eliminar item del carrito",
)
async def remove_cart_item(
    item_id: int,
    current_user: CurrentUser,
    service: CartService = Depends(get_cart_service),
):
    """
    Elimina un item específico del carrito del usuario autenticado.

    Retorna 204 en caso de éxito y traduce a HTTP 404 cuando el item no existe
    o no pertenece al usuario.
    """
    try:
        await service.remove_item(item_id, current_user.id)
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=str(e),
        )


@router.delete(
    "",
    status_code=status.HTTP_204_NO_CONTENT,
    summary="Vaciar carrito",
)
async def clear_cart(
    current_user: CurrentUser,
    service: CartService = Depends(get_cart_service),
):
    """
    Vacía por completo el carrito del usuario eliminando todos los items.

    La operación es idempotente: devuelve 204 tanto si había items como si el
    carrito ya estaba vacío.
    """
    await service.clear_cart(current_user.id)
