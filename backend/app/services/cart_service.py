"""
Servicio de carrito de compras.

Lógica de negocio:
- Validar stock disponible antes de agregar al carrito
- Calcular subtotales y total
- Enriquecer items con metadata de juegos
"""

from app.crud.cart_interface import CartRepositoryInterface
from app.crud.game_catalog_interface import GameCatalogRepositoryInterface
from app.schemas.cart import (
    CartResponse,
    CartItemResponse,
    CartItemCreate,
    CartItemUpdate,
)


class CartService:
    def __init__(
        self,
        cart_repo: CartRepositoryInterface,
        game_repo: GameCatalogRepositoryInterface,
    ):
        self.cart_repo = cart_repo
        self.game_repo = game_repo

    async def add_to_cart(self, user_id: int, data: CartItemCreate) -> CartResponse:
        """
        Agrega item al carrito.

        Validaciones:
        - Juego existe en catálogo
        - Hay stock suficiente

        Raises:
            ValueError si validaciones fallan
        """

        game = await self.game_repo.get_by_id(data.game_id)
        if not game:
            raise ValueError(f"Juego con ID {data.game_id} no encontrado")

        if game.stock < data.quantity:
            raise ValueError(
                f"Stock insuficiente para {game.title}. "
                f"Disponible: {game.stock}, Solicitado: {data.quantity}"
            )

        await self.cart_repo.add_item(user_id, data.game_id, data.quantity)
        return await self.get_cart(user_id)

    async def get_cart(self, user_id: int) -> CartResponse:
        """
        Obtiene carrito con items enriquecidos.

        Calcula subtotales y total.
        """
        cart = await self.cart_repo.get_cart_with_items(user_id)

        if not cart:
            cart = await self.cart_repo.get_or_create_cart(user_id)

        items_response = []
        total = 0.0

        for item in cart.items:
            subtotal = item.quantity * float(item.game.price)
            total += subtotal

            items_response.append(
                CartItemResponse(
                    id=item.id,
                    game_id=item.game_id,
                    quantity=item.quantity,
                    game_title=item.game.title,
                    game_image=item.game.image_url,
                    game_price=float(item.game.price),
                    subtotal=subtotal,
                    in_stock=item.game.stock >= item.quantity,
                )
            )

        return CartResponse(
            id=cart.id,
            user_id=cart.user_id,
            items=items_response,
            total=total,
            created_at=cart.created_at,
            updated_at=cart.updated_at,
        )

    async def update_item(
        self, item_id: int, data: CartItemUpdate, user_id: int
    ) -> CartResponse:
        """
        Actualiza cantidad de item.

        Validaciones:
        - Item existe y pertenece al usuario
        - Hay stock suficiente para nueva cantidad

        Raises:
            ValueError si validaciones fallan
        """
        cart = await self.cart_repo.get_cart_with_items(user_id)
        if not cart:
            raise ValueError("Carrito no encontrado para el usuario")

        cart_item = next((item for item in cart.items if item.id == item_id), None)
        if not cart_item:
            raise ValueError(f"Item {item_id} no encontrado o no pertenece al usuario")

        game = await self.game_repo.get_by_id(cart_item.game_id)
        if not game:
            raise ValueError(f"Juego asociado al item {item_id} no encontrado")

        if game.stock < data.quantity:
            raise ValueError(
                f"Stock insuficiente para {game.title}. "
                f"Disponible: {game.stock}, Solicitado: {data.quantity}"
            )

        await self.cart_repo.update_item_quantity(item_id, data.quantity, user_id)

        return await self.get_cart(user_id)

    async def remove_item(self, item_id: int, user_id: int) -> None:
        """Elimina item del carrito sin recalcular respuesta."""
        removed = await self.cart_repo.remove_item(item_id, user_id)
        if not removed:
            raise ValueError(f"Item {item_id} no encontrado o no pertenece al usuario")
        return None

    async def clear_cart(self, user_id: int) -> None:
        """Vacía el carrito del usuario."""
        await self.cart_repo.clear_cart(user_id)
