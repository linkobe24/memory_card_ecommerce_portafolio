"""
Implementación PostgreSQL del repositorio de Cart.

Usa SQLAlchemy async con eager loading para joins.
"""

from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from sqlalchemy.orm import selectinload
from app.crud.cart_interface import CartRepositoryInterface
from app.models.cart import Cart, CartItem


class PostgresCartRepository(CartRepositoryInterface):
    """Repositorio de carrito usando PostgreSQL."""

    def __init__(self, db: AsyncSession):
        self.db = db

    async def get_or_create_cart(self, user_id: int) -> Cart:
        """Obtiene o crea carrito del usuario."""
        result = await self.db.execute(select(Cart).where(Cart.user_id == user_id))
        cart = result.scalar_one_or_none()

        if not cart:
            cart = Cart(user_id=user_id)
            self.db.add(cart)
            await self.db.commit()
            await self.db.refresh(cart)

        return cart

    async def add_item(self, user_id: int, game_id: int, quantity: int) -> CartItem:
        """Agrega item al carrito o suma cantidad si ya existe."""
        # Obtener o crear carrito
        cart = await self.get_or_create_cart(user_id)

        # Verificar si item ya existe
        result = await self.db.execute(
            select(CartItem).where(
                CartItem.cart_id == cart.id, CartItem.game_id == game_id
            )
        )
        existing_item = result.scalar_one_or_none()

        if existing_item:
            # Sumar cantidad
            existing_item.quantity += quantity
            await self.db.commit()
            await self.db.refresh(existing_item)
            return existing_item

        # Crear nuevo item
        new_item = CartItem(cart_id=cart.id, game_id=game_id, quantity=quantity)
        self.db.add(new_item)
        await self.db.commit()
        await self.db.refresh(new_item)
        return new_item

    async def update_item_quantity(
        self, item_id: int, quantity: int, user_id: int
    ) -> CartItem | None:
        """Actualiza cantidad de item (verifica ownership)."""
        result = await self.db.execute(
            select(CartItem)
            .join(Cart)
            .where(CartItem.id == item_id, Cart.user_id == user_id)
        )
        item = result.scalar_one_or_none()

        if not item:
            return None

        item.quantity = quantity
        await self.db.commit()
        await self.db.refresh(item)
        return item

    async def remove_item(self, item_id: int, user_id: int) -> bool:
        """Elimina item del carrito (verifica ownership)."""
        result = await self.db.execute(
            select(CartItem)
            .join(Cart)
            .where(CartItem.id == item_id, Cart.user_id == user_id)
        )
        item = result.scalar_one_or_none()

        if not item:
            return False

        await self.db.delete(item)
        await self.db.commit()
        return True

    async def clear_cart(
        self,
        user_id: int,
        session: AsyncSession | None = None,
    ) -> None:
        """Vacía carrito del usuario."""
        db = session or self.db
        result = await db.execute(select(Cart).where(Cart.user_id == user_id))
        cart = result.scalar_one_or_none()

        if cart:
            # Eliminar todos los items (cascade lo hace automáticamente)
            for item in list(cart.items):
                await db.delete(item)
            if session:
                await db.flush()
            else:
                await db.commit()

    async def get_cart_with_items(self, user_id: int) -> Cart | None:
        """Obtiene carrito con items y metadata de juegos."""
        result = await self.db.execute(
            select(Cart)
            .where(Cart.user_id == user_id)
            .options(selectinload(Cart.items).selectinload(CartItem.game))
        )
        return result.scalar_one_or_none()

    async def get_cart_with_items_for_update(
        self, user_id: int, session: AsyncSession | None = None
    ) -> Cart | None:
        """Obtiene carrito con items aplicando bloqueo FOR UPDATE."""
        db = session or self.db
        stmt = (
            select(Cart)
            .where(Cart.user_id == user_id)
            .options(selectinload(Cart.items).selectinload(CartItem.game))
            .execution_options(with_for_update=True)
        )
        result = await db.execute(stmt)
        return result.scalar_one_or_none()
