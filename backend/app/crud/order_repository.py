"""
Implementación PostgreSQL del repositorio de Order.

Usa transacciones para crear órdenes atómicamente.
"""

from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func
from sqlalchemy.orm import selectinload
from datetime import datetime, timezone
from app.crud.order_interface import OrderRepositoryInterface
from app.models.order import Order, OrderItem, OrderStatus
from app.models.cart import CartItem

TAX_RATE = 0.10


class PostgresOrderRepository(OrderRepositoryInterface):
    def __init__(self, db: AsyncSession):
        self.db = db

    async def create_from_cart(
        self,
        user_id: int,
        cart_items: list[CartItem],
        stripe_payment_intent_id: str | None = None,
        session: AsyncSession | None = None,
    ) -> Order:
        """
        Crea orden desde carrito.

        Calcula subtotal, tax y total.
        """
        db = session or self.db

        subtotal = 0.0
        tax = 0.0
        for item in cart_items:
            line_subtotal = item.quantity * float(item.game.price)
            subtotal += line_subtotal
            tax += line_subtotal * TAX_RATE

        subtotal = round(subtotal, 2)
        tax = round(tax, 2)
        total = subtotal + tax

        # Crear orden
        order = Order(
            user_id=user_id,
            subtotal=subtotal,
            tax=tax,
            total=total,
            status=OrderStatus.PENDING,
            stripe_payment_intent_id=stripe_payment_intent_id,
        )
        db.add(order)
        await db.flush()  # Obtener order.id

        # Crear order items (snapshot del momento de compra)
        for item in cart_items:
            unit_price = float(item.game.price)
            order_item = OrderItem(
                order_id=order.id,
                game_id=item.game_id,
                quantity=item.quantity,
                unit_price=unit_price,
                subtotal=item.quantity * unit_price,
            )
            db.add(order_item)

        # El commit ocurre en la transacción externa (OrderService)
        await db.flush()
        await db.refresh(order)
        return order

    async def get_by_id(self, order_id: int) -> Order | None:
        """Obtiene orden con items (eager loading)."""
        result = await self.db.execute(
            select(Order)
            .where(Order.id == order_id)
            .options(selectinload(Order.items).selectinload(OrderItem.game))
        )
        return result.scalar_one_or_none()

    async def list_by_user(
        self, user_id: int, skip: int = 0, limit: int = 20
    ) -> tuple[list[Order], int]:
        """Lista órdenes de un usuario."""
        # Count total
        count_result = await self.db.execute(
            select(func.count()).select_from(Order).where(Order.user_id == user_id)
        )
        total = count_result.scalar()

        result = await self.db.execute(
            select(Order)
            .where(Order.user_id == user_id)
            .options(selectinload(Order.items).selectinload(OrderItem.game))
            .order_by(Order.created_at.desc())
            .offset(skip)
            .limit(limit)
        )
        orders = list(result.scalars().all())

        return orders, total

    async def list_all(
        self, skip: int = 0, limit: int = 20, status: OrderStatus | None = None
    ) -> tuple[list[Order], int]:
        """Lista todas las órdenes (admin)."""
        filters = []
        if status:
            filters.append(Order.status == status)

        count_query = select(func.count()).select_from(Order)
        if filters:
            count_query = count_query.where(*filters)
        count_result = await self.db.execute(count_query)
        total = count_result.scalar()

        data_query = (
            select(Order)
            .where(*filters)
            .options(selectinload(Order.items).selectinload(OrderItem.game))
            .order_by(Order.created_at.desc())
            .offset(skip)
            .limit(limit)
        )

        result = await self.db.execute(data_query)
        orders = list(result.scalars().all())

        return orders, total

    async def update_status(self, order_id: int, status: OrderStatus) -> Order | None:
        """Actualiza estado de orden."""
        order = await self.get_by_id(order_id)
        if not order:
            return None

        order.status = status

        if status == OrderStatus.COMPLETED:
            order.completed_at = datetime.now(timezone.utc)

        await self.db.commit()
        await self.db.refresh(order)
        return order
