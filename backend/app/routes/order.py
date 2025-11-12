"""
Endpoints de órdenes.

- Endpoints de usuario: crear orden, ver historial, ver detalle
- Endpoints admin: listar todas, actualizar estado
"""

from fastapi import APIRouter, Depends, HTTPException, status, Query
from app.services.order_service import OrderService
from app.crud.order_repository import PostgresOrderRepository
from app.crud.order_interface import OrderRepositoryInterface
from app.crud.cart_repository import PostgresCartRepository
from app.crud.cart_interface import CartRepositoryInterface
from app.crud.game_catalog_repository import PostgresGameCatalogRepository
from app.crud.game_catalog_interface import GameCatalogRepositoryInterface
from app.core.database import get_db
from app.schemas.order import OrderResponse, OrderCreate, OrderStatusUpdate
from app.models.order import OrderStatus
from app.middleware.auth import CurrentAdmin, CurrentUser
from sqlalchemy.ext.asyncio import AsyncSession

router = APIRouter()


def get_order_service(
    db: AsyncSession = Depends(get_db),
) -> OrderService:
    """Factory para servicio de órdenes."""
    order_repo: OrderRepositoryInterface = PostgresOrderRepository(db)
    cart_repo: CartRepositoryInterface = PostgresCartRepository(db)
    game_repo: GameCatalogRepositoryInterface = PostgresGameCatalogRepository(db)
    return OrderService(order_repo, cart_repo, game_repo, db)


# ========== Endpoints de Usuario ==========


@router.post(
    "",
    response_model=OrderResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Crear orden desde carrito",
)
async def create_order(
    current_user: CurrentUser,
    data: OrderCreate = OrderCreate(),
    service: OrderService = Depends(get_order_service),
):
    """
    Ejecuta el checkout del carrito del usuario autenticado.

    Bloquea el carrito, valida stock, crea la orden y limpia el carrito dentro
    de una sola transacción para evitar compras duplicadas. Devuelve la orden
    enriquecida y lanza HTTP 400 si el carrito está vacío o no hay stock.
    """
    try:
        return await service.create_order_from_cart(
            current_user.id, data.stripe_payment_intent_id
        )
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e),
        )


@router.get(
    "",
    response_model=dict,
    summary="Ver historial de órdenes",
)
async def list_my_orders(
    current_user: CurrentUser,
    page: int = Query(1, ge=1),
    page_size: int = Query(20, ge=1, le=100),
    service: OrderService = Depends(get_order_service),
):
    """
    Recupera el historial paginado de órdenes del usuario autenticado.

    Retorna un diccionario con total de órdenes, metadatos de paginación y la
    lista de órdenes ya enriquecidas para la UI.
    """
    return await service.list_user_orders(current_user.id, page, page_size)


@router.get(
    "/{order_id}",
    response_model=OrderResponse,
    summary="Ver detalle de orden",
)
async def get_order_details(
    order_id: int,
    current_user: CurrentUser,
    service: OrderService = Depends(get_order_service),
):
    """
    Devuelve el detalle completo de una orden perteneciente al usuario.

    Valida ownership antes de exponer la información y traduce la ausencia de la
    orden a HTTP 404.
    """
    order = await service.get_order(order_id, user_id=current_user.id)
    if not order:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Orden con ID {order_id} no encontrada o no pertenece al usuario",
        )
    return order


# ========== Endpoints Admin ==========


@router.get(
    "/admin/all",
    response_model=dict,
    summary="Listar todas las órdenes (Admin)",
)
async def list_all_orders_admin(
    current_user: CurrentAdmin,
    page: int = Query(1, ge=1),
    page_size: int = Query(20, ge=1, le=100),
    status: OrderStatus | None = Query(None, description="Filtrar por estado"),
    service: OrderService = Depends(get_order_service),
):
    """
    Lista todas las órdenes del sistema con paginación y filtro opcional por estado.

    Solo accesible para administradores; ideal para tableros internos.
    """
    return await service.list_all_orders(page, page_size, status)


@router.put(
    "/{order_id}/status",
    response_model=OrderResponse,
    summary="Actualizar estado de orden (Admin)",
)
async def update_order_status_admin(
    order_id: int,
    data: OrderStatusUpdate,
    current_user: CurrentAdmin,
    service: OrderService = Depends(get_order_service),
):
    """
    Permite a un administrador cambiar el estado de una orden existente.

    Retorna la orden actualizada o HTTP 404 si el ID no existe.
    """
    order = await service.update_order_status(order_id, data)
    if not order:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Orden con ID {order_id} no encontrada",
        )
    return order
