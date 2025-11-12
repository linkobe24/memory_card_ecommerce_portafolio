"""
Interfaz para repositorio de Order.

Define operaciones para gestión de órdenes.
"""

from abc import ABC, abstractmethod
from app.models.order import Order, OrderStatus


class OrderRepositoryInterface(ABC):

    @abstractmethod
    async def create_from_cart(
        self,
        user_id: int,
        cart_items: list,
        stripe_payment_intent_id: str | None = None,
    ) -> Order:
        """
        Crea orden desde carrito del usuario.

        Args:
            user_id: ID del usuario
            cart_items: Lista de CartItem del carrito
            stripe_payment_intent_id: ID de Stripe (si aplica)

        Returns:
            Orden creada con items
        """
        pass

    @abstractmethod
    async def get_by_id(self, order_id: int) -> Order | None:
        """Obtiene orden por ID (con items eager loaded)."""
        pass

    @abstractmethod
    async def list_by_user(
        self, user_id: int, skip: int = 0, limit: int = 20
    ) -> tuple[list[Order], int]:
        """
        Lista órdenes de un usuario.

        Returns:
            Tupla (órdenes, total_count)
        """
        pass

    @abstractmethod
    async def list_all(
        self, skip: int = 0, limit: int = 20, status: OrderStatus | None = None
    ) -> tuple[list[Order], int]:
        """
        Lista todas las órdenes (admin).

        Args:
            status: Filtrar por estado (opcional)

        Returns:
            Tupla (órdenes, total_count)
        """
        pass

    @abstractmethod
    async def update_status(self, order_id: int, status: OrderStatus) -> Order | None:
        """Actualiza estado de orden."""
        pass
