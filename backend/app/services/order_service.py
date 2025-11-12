"""
Servicio de órdenes.

Lógica de negocio:
- Crear orden desde carrito
- Reducir stock al crear orden
- Validar stock antes de crear orden
- Enriquecer órdenes con metadata
"""

from app.crud.order_interface import OrderRepositoryInterface
from app.crud.cart_interface import CartRepositoryInterface
from app.crud.game_catalog_interface import GameCatalogRepositoryInterface
from app.models.order import OrderStatus
from app.schemas.order import OrderResponse, OrderItemResponse, OrderStatusUpdate
from sqlalchemy.ext.asyncio import AsyncSession


class OrderService:
    """Servicio de órdenes con lógica de negocio."""

    def __init__(
        self,
        order_repo: OrderRepositoryInterface,
        cart_repo: CartRepositoryInterface,
        game_repo: GameCatalogRepositoryInterface,
        db: AsyncSession,
    ):
        self.order_repo = order_repo
        self.cart_repo = cart_repo
        self.game_repo = game_repo
        self.db = db

    async def create_order_from_cart(
        self, user_id: int, stripe_payment_intent_id: str | None = None
    ) -> OrderResponse:
        """
        Crea orden desde carrito del usuario.

        Flujo:
        1. Obtener carrito con items
        2. Validar stock de todos los items
        3. Crear orden (transacción)
        4. Reducir stock de productos
        5. Vaciar carrito

        Raises:
            ValueError si carrito vacío o stock insuficiente
        """
        # Ejecutar todo dentro de una sola transacción y trabajar con snapshot bloqueado
        session = self.db
        # Transacción atómica: si falla algo, todo se revierte (stock, orden, carrito)
        transaction_ctx = (
            session.begin_nested() if session.in_transaction() else session.begin()
        )
        async with transaction_ctx:
            cart = await self.cart_repo.get_cart_with_items_for_update(
                user_id, session=session
            )
            if not cart or not cart.items:
                raise ValueError("El carrito está vacío")

            for item in cart.items:
                if item.game.stock < item.quantity:
                    raise ValueError(
                        f"Stock insuficiente para {item.game.title}. "
                        f"Disponible: {item.game.stock}, En carrito: {item.quantity}"
                    )

            created_order = await self.order_repo.create_from_cart(
                user_id,
                cart.items,
                stripe_payment_intent_id,
                session=session,
            )

            for item in cart.items:
                await self.game_repo.reduce_stock(
                    item.game_id,
                    item.quantity,
                    session=session,
                )

            await self.cart_repo.clear_cart(user_id, session=session)

        order = await self.order_repo.get_by_id(created_order.id)
        return await self._enrich_order(order)

    async def get_order(
        self, order_id: int, user_id: int | None = None
    ) -> OrderResponse | None:
        """
        Obtiene orden por ID.

        Args:
            order_id: ID de la orden
            user_id: Si se proporciona, valida que la orden pertenezca al usuario

        Returns:
            OrderResponse o None si no existe o no pertenece al usuario
        """
        order = await self.order_repo.get_by_id(order_id)
        if not order:
            return None

        # Validar ownership si se proporciona user_id
        if user_id is not None and order.user_id != user_id:
            return None

        return await self._enrich_order(order)

    async def list_user_orders(
        self, user_id: int, page: int = 1, page_size: int = 20
    ) -> dict:
        """Lista órdenes de un usuario."""
        skip = (page - 1) * page_size
        orders, total = await self.order_repo.list_by_user(user_id, skip, page_size)

        results = [await self._enrich_order(order) for order in orders]

        return {
            "total": total,
            "page": page,
            "page_size": page_size,
            "results": results,
        }

    async def list_all_orders(
        self, page: int = 1, page_size: int = 20, status: OrderStatus | None = None
    ) -> dict:
        """Lista todas las órdenes (admin)."""
        skip = (page - 1) * page_size
        orders, total = await self.order_repo.list_all(skip, page_size, status)

        results = [await self._enrich_order(order) for order in orders]

        return {
            "total": total,
            "page": page,
            "page_size": page_size,
            "results": results,
        }

    async def update_order_status(
        self, order_id: int, data: OrderStatusUpdate
    ) -> OrderResponse | None:
        """Actualiza estado de orden (admin)."""
        order = await self.order_repo.update_status(order_id, data.status)
        if not order:
            return None
        return await self._enrich_order(order)

    async def _enrich_order(self, order) -> OrderResponse:
        """Convierte Order model a OrderResponse con metadata."""
        items_response = [
            OrderItemResponse(
                id=item.id,
                game_id=item.game_id,
                game_title=item.game.title,  # Snapshot
                quantity=item.quantity,
                unit_price=float(item.unit_price),
                subtotal=float(item.subtotal),
            )
            for item in order.items
        ]

        return OrderResponse(
            id=order.id,
            user_id=order.user_id,
            subtotal=float(order.subtotal),
            tax=float(order.tax),
            total=float(order.total),
            status=order.status,
            stripe_payment_intent_id=order.stripe_payment_intent_id,
            items=items_response,
            created_at=order.created_at,
            completed_at=order.completed_at,
        )
