"""
Interfaz para repositorio de Cart.

Define operaciones para gestión de carrito de compras.
"""

from abc import ABC, abstractmethod
from app.models.cart import Cart, CartItem
from sqlalchemy.ext.asyncio import AsyncSession


class CartRepositoryInterface(ABC):

    @abstractmethod
    async def get_or_create_cart(self, user_id: int) -> Cart:
        """
        Obtener el carrito activo del usuario o crear uno nuevo si no existe.

        Args:
            user_id: Identificador del usuario al que pertenece el carrito.

        Returns:
            Cart: Instancia del carrito existente o recién creado.
        """
        pass

    @abstractmethod
    async def add_item(self, user_id: int, game_id: int, quantity: int) -> CartItem:
        """
        Agregar un juego al carrito del usuario.

        Si el artículo ya está presente se incrementa la cantidad.

        Args:
            user_id: Dueño del carrito.
            game_id: Juego que se agrega.
            quantity: Cantidad que se desea sumar.

        Returns:
            CartItem: Artículo actualizado o recién creado.
        """
        pass

    @abstractmethod
    async def update_item_quantity(
        self, item_id: int, quantity: int, user_id: int
    ) -> CartItem | None:
        """
        Actualizar la cantidad de un item validando pertenencia al usuario.

        Args:
            item_id: Identificador del artículo en el carrito.
            quantity: Nueva cantidad solicitada.
            user_id: Dueño del carrito; usado para validar acceso.

        Returns:
            CartItem | None: Item actualizado o None si no pertenece al usuario.
        """
        pass

    @abstractmethod
    async def remove_item(self, item_id: int, user_id: int) -> bool:
        """
        Eliminar un item del carrito del usuario.

        Args:
            item_id: Identificador del artículo en el carrito.
            user_id: Dueño del carrito que realiza la operación.

        Returns:
            bool: True si se eliminó, False si no existía o no pertenecía al usuario.
        """
        pass

    @abstractmethod
    async def clear_cart(
        self,
        user_id: int,
        session: AsyncSession | None = None,
    ) -> None:
        """
        Vaciar el carrito del usuario eliminando todos los items.

        Args:
            user_id: Dueño del carrito.
            session: Sesión transaccional existente si se desea reutilizar.

        Returns:
            None
        """
        pass

    @abstractmethod
    async def get_cart_with_items(self, user_id: int) -> Cart | None:
        """
        Obtener el carrito con todos sus items y relaciones relevantes.

        Incluye eager loading de game_catalog para tener metadata del juego.

        Args:
            user_id: Dueño del carrito solicitado.

        Returns:
            Cart | None: Carrito con items o None si no existe.
        """
        pass

    @abstractmethod
    async def get_cart_with_items_for_update(
        self, user_id: int, session: AsyncSession | None = None
    ) -> Cart | None:
        """
        Obtener el carrito con items bloqueado para actualizaciones concurrentes.

        Args:
            user_id: Dueño del carrito solicitado.
            session: Sesión transaccional a reutilizar si existe.

        Returns:
            Cart | None: Carrito bloqueado con items o None si no existe.
        """
        pass
