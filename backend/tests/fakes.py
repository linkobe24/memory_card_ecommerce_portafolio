from __future__ import annotations

from datetime import datetime, timezone
from uuid import uuid4

from app.crud.user_interface import UserRepositoryInterface
from app.crud.cache_interface import CacheRepositoryInterface
from app.models.user import User, UserRole
from app.schemas.user import UserCreate, UserUpdate
from app.core.security import hash_password
from app.crud.cart_interface import CartRepositoryInterface
from app.crud.order_interface import OrderRepositoryInterface
from app.crud.game_catalog_interface import GameCatalogRepositoryInterface
from app.crud.review_interface import ReviewRepositoryInterface
from app.models.cart import Cart, CartItem
from app.models.order import Order, OrderItem, OrderStatus
from app.models.game_catalog import GameCatalog
from app.models.review import Review
from app.schemas.game_catalog import GameCatalogCreate, GameCatalogUpdate
from app.schemas.review import ReviewCreate, ReviewUpdate
from sqlalchemy.ext.asyncio import AsyncSession


def generate_unique_email(label: str) -> str:
    """Devuelve un email válido distinto en cada llamada."""
    return f"{label}-{uuid4().hex}@example.com"


class InMemoryUserRepository(UserRepositoryInterface):
    """Repositorio en memoria para pruebas de integración."""

    def __init__(self):
        self._users: dict[str, User] = {}
        self._by_id: dict[int, User] = {}
        self._id_sequence = 1

    async def get_by_email(self, email: str) -> User | None:
        return self._users.get(email)

    async def get_by_id(self, id: int) -> User | None:
        return self._by_id.get(id)

    async def create_user(self, user_data: UserCreate) -> User:
        if user_data.email in self._users:
            raise ValueError("duplicate-email")

        user = User(
            id=self._id_sequence,
            email=user_data.email,
            hashed_password=hash_password(user_data.password),
            full_name=user_data.full_name,
            role=UserRole.CUSTOMER,
            created_at=datetime.now(timezone.utc),
        )
        self._users[user.email] = user
        self._by_id[user.id] = user
        self._id_sequence += 1
        return user

    async def create(self, data: UserCreate) -> User:
        return await self.create_user(data)

    async def update(self, id: int, data: UserUpdate) -> User | None:
        user = await self.get_by_id(id)
        if user is None:
            return None

        payload = data.model_dump(exclude_unset=True)
        if "email" in payload:
            self._users.pop(user.email, None)
            user.email = payload["email"]
            self._users[user.email] = user

        if "full_name" in payload:
            user.full_name = payload["full_name"]

        if "password" in payload:
            user.hashed_password = hash_password(payload["password"])

        return user

    async def delete(self, id: int) -> bool:
        user = await self.get_by_id(id)
        if not user:
            return False

        self._by_id.pop(id, None)
        self._users.pop(user.email, None)
        return True

    async def update_last_login(self, user_id: int) -> None:
        """
        Para fines de prueba no necesitamos persistir last_login,
        pero mantenemos la firma para compatibilidad.
        """
        user = await self.get_by_id(user_id)
        if user is not None:
            user.last_login = datetime.now(timezone.utc)


class InMemoryCacheRepository(CacheRepositoryInterface):
    """
    Repositorio de cache en memoria para tests.

    Simula Redis sin necesidad de servidor real.
    """

    def __init__(self):
        self._cache: dict[str, str] = {}
        # En un caso real, TTL se implementaría con timestamps
        # Para tests, lo simplificamos (ignoramos TTL)

    async def get(self, key: str) -> str | None:
        """Obtiene valor del cache."""
        return self._cache.get(key)

    async def set(self, key: str, value: str, ttl: int | None = None) -> None:
        """Guarda valor en cache (ignora TTL en tests)."""
        self._cache[key] = value

    async def delete(self, key: str) -> None:
        """Elimina clave del cache."""
        self._cache.pop(key, None)

    async def exists(self, key: str) -> bool:
        """Verifica si clave existe."""
        return key in self._cache

    async def clear_pattern(self, pattern: str) -> int:
        """
        Elimina claves por patrón (simulación simple).

        Convierte patrón Redis (rawg:*) a Python (rawg:).
        """
        # Convertir patrón Redis a prefijo Python
        prefix = pattern.replace("*", "")
        keys_to_delete = [k for k in self._cache.keys() if k.startswith(prefix)]

        for key in keys_to_delete:
            del self._cache[key]

        return len(keys_to_delete)

    def clear_all(self):
        """Método helper para limpiar todo el cache en tests."""
        self._cache.clear()


class InMemoryGameCatalogRepository(GameCatalogRepositoryInterface):
    """
    Repositorio in-memory para GameCatalog.

    Simula operaciones CRUD de productos sin base de datos.
    """

    def __init__(self):
        self._games: dict[int, GameCatalog] = {}  # Por ID local
        self._by_rawg_id: dict[int, GameCatalog] = {}  # Por RAWG ID
        self._id_sequence = 1

    async def create(self, data: GameCatalogCreate, metadata: dict) -> GameCatalog:
        """Crea producto validando duplicado por rawg_id."""
        if data.rawg_id in self._by_rawg_id:
            raise ValueError(f"Producto con rawg_id {data.rawg_id} ya existe")

        game = GameCatalog(
            id=self._id_sequence,
            rawg_id=data.rawg_id,
            title=metadata["title"],
            slug=metadata["slug"],
            description=metadata.get("description"),
            image_url=metadata.get("image_url"),
            price=data.price,
            stock=data.stock,
            created_at=datetime.now(timezone.utc),
            updated_at=datetime.now(timezone.utc),
        )

        self._games[game.id] = game
        self._by_rawg_id[game.rawg_id] = game
        self._id_sequence += 1
        return game

    async def get_by_id(self, game_id: int) -> GameCatalog | None:
        return self._games.get(game_id)

    async def get_by_rawg_id(self, rawg_id: int) -> GameCatalog | None:
        return self._by_rawg_id.get(rawg_id)

    async def list_all(
        self, skip: int = 0, limit: int = 20, in_stock_only: bool = False
    ) -> tuple[list[GameCatalog], int]:
        """Lista productos con paginación."""
        games = list(self._games.values())

        if in_stock_only:
            games = [g for g in games if g.stock > 0]

        total = len(games)
        return games[skip : skip + limit], total

    async def update(self, game_id: int, data: GameCatalogUpdate) -> GameCatalog | None:
        """Actualiza precio y/o stock."""
        game = self._games.get(game_id)
        if not game:
            return None

        update_data = data.model_dump(exclude_unset=True)
        for key, value in update_data.items():
            setattr(game, key, value)

        game.updated_at = datetime.now(timezone.utc)
        return game

    async def delete(self, game_id: int) -> bool:
        """Elimina producto."""
        game = self._games.pop(game_id, None)
        if game:
            self._by_rawg_id.pop(game.rawg_id, None)
            return True
        return False

    async def reduce_stock(
        self,
        game_id: int,
        quantity: int,
        session: AsyncSession | None = None,
    ) -> GameCatalog | None:
        """
        Reduce stock validando disponibilidad.

        Raises:
            ValueError si stock insuficiente
        """
        game = self._games.get(game_id)
        if not game:
            return None

        if game.stock < quantity:
            raise ValueError(
                f"Stock insuficiente para {game.title}. "
                f"Disponible: {game.stock}, Solicitado: {quantity}"
            )

        game.stock -= quantity
        return game

    async def increase_stock(
        self,
        game_id: int,
        quantity: int,
        session: AsyncSession | None = None,
    ) -> GameCatalog | None:
        """Aumenta stock (usado al cancelar órdenes)."""
        game = self._games.get(game_id)
        if not game:
            return None

        game.stock += quantity
        return game


class InMemoryCartRepository(CartRepositoryInterface):
    """
    Repositorio in-memory para Cart.

    Simula operaciones de carrito con relaciones a GameCatalog.
    """

    def __init__(self, game_repo: InMemoryGameCatalogRepository):
        self._carts: dict[int, Cart] = {}  # Por user_id (unique)
        self._items: dict[int, CartItem] = {}  # Por item ID
        self._item_id_sequence = 1
        self._cart_id_sequence = 1
        self.game_repo = game_repo

    async def get_or_create_cart(self, user_id: int) -> Cart:
        """Obtiene o crea carrito del usuario."""
        if user_id in self._carts:
            return self._carts[user_id]

        cart = Cart(
            id=self._cart_id_sequence,
            user_id=user_id,
            items=[],
            created_at=datetime.now(timezone.utc),
            updated_at=datetime.now(timezone.utc),
        )

        self._carts[user_id] = cart
        self._cart_id_sequence += 1
        return cart

    async def add_item(self, user_id: int, game_id: int, quantity: int) -> CartItem:
        """
        Agrega item al carrito (o incrementa cantidad si existe).
        """
        cart = await self.get_or_create_cart(user_id)

        # Buscar item existente
        existing_item = next(
            (item for item in cart.items if item.game_id == game_id), None
        )

        if existing_item:
            existing_item.quantity += quantity
            return existing_item

        # Crear nuevo item
        item = CartItem(
            id=self._item_id_sequence,
            cart_id=cart.id,
            game_id=game_id,
            quantity=quantity,
            created_at=datetime.now(timezone.utc),
        )

        # Cargar relación con game
        item.game = await self.game_repo.get_by_id(game_id)

        cart.items.append(item)
        self._items[item.id] = item
        self._item_id_sequence += 1

        return item

    async def update_item_quantity(
        self, item_id: int, quantity: int, user_id: int
    ) -> CartItem | None:
        """Actualiza cantidad validando ownership."""
        item = self._items.get(item_id)
        if not item:
            return None

        cart = self._carts.get(user_id)
        if not cart or item not in cart.items:
            return None

        item.quantity = quantity
        return item

    async def remove_item(self, item_id: int, user_id: int) -> bool:
        """Elimina item validando ownership."""
        item = self._items.pop(item_id, None)
        if not item:
            return False

        cart = self._carts.get(user_id)
        if not cart:
            return False

        try:
            cart.items.remove(item)
            return True
        except ValueError:
            return False

    async def clear_cart(
        self,
        user_id: int,
        session: AsyncSession | None = None,
    ) -> None:
        """Vacía carrito eliminando todos los items."""
        cart = self._carts.get(user_id)
        if not cart:
            return

        # Eliminar items del índice
        for item in cart.items:
            self._items.pop(item.id, None)

        cart.items.clear()

    async def get_cart_with_items(self, user_id: int) -> Cart | None:
        """Obtiene carrito con items (con relaciones cargadas)."""
        cart = self._carts.get(user_id)
        if not cart:
            return None

        # Eager load games
        for item in cart.items:
            if not hasattr(item, "game") or item.game is None:
                item.game = await self.game_repo.get_by_id(item.game_id)

        return cart

    async def get_cart_with_items_for_update(
        self, user_id: int, session: AsyncSession | None = None
    ) -> Cart | None:
        """
        Obtiene carrito bloqueado para updates concurrentes.

        En tests, simplemente devuelve el carrito (no hay locks en memoria).
        """
        return await self.get_cart_with_items(user_id)


class InMemoryOrderRepository(OrderRepositoryInterface):
    """
    Repositorio in-memory para Order.

    Simula creación y gestión de órdenes con snapshots.
    """

    def __init__(self, game_repo: InMemoryGameCatalogRepository):
        self._orders: dict[int, Order] = {}
        self._order_id_sequence = 1
        self._order_item_id_sequence = 1
        self.game_repo = game_repo

    async def create_from_cart(
        self,
        user_id: int,
        cart_items: list[CartItem],
        stripe_payment_intent_id: str | None = None,
        session: AsyncSession | None = None,
    ) -> Order:
        """
        Crea orden desde items del carrito.

        Genera snapshot de precios en el momento de compra.
        """
        order_items = []
        subtotal = 0.0

        for cart_item in cart_items:
            game = await self.game_repo.get_by_id(cart_item.game_id)
            unit_price = float(game.price)
            item_subtotal = unit_price * cart_item.quantity
            subtotal += item_subtotal

            order_item = OrderItem(
                id=self._order_item_id_sequence,
                order_id=None,  # Se asigna después
                game_id=cart_item.game_id,
                quantity=cart_item.quantity,
                unit_price=unit_price,
                subtotal=item_subtotal,
            )

            # Cargar relación con game (snapshot)
            order_item.game = game

            order_items.append(order_item)
            self._order_item_id_sequence += 1

        tax = 0.0  # Simplificado para MVP
        total = subtotal + tax

        order = Order(
            id=self._order_id_sequence,
            user_id=user_id,
            subtotal=subtotal,
            tax=tax,
            total=total,
            status=OrderStatus.PENDING,
            stripe_payment_intent_id=stripe_payment_intent_id,
            items=order_items,
            created_at=datetime.now(timezone.utc),
            completed_at=None,
        )

        # Asignar order_id a items
        for item in order_items:
            item.order_id = order.id

        self._orders[order.id] = order
        self._order_id_sequence += 1

        return order

    async def get_by_id(self, order_id: int) -> Order | None:
        """Obtiene orden por ID (con items eager loaded)."""
        return self._orders.get(order_id)

    async def list_by_user(
        self, user_id: int, skip: int = 0, limit: int = 20
    ) -> tuple[list[Order], int]:
        """Lista órdenes de un usuario."""
        user_orders = [o for o in self._orders.values() if o.user_id == user_id]
        total = len(user_orders)

        # Ordenar por fecha descendente
        user_orders.sort(key=lambda o: o.created_at, reverse=True)

        return user_orders[skip : skip + limit], total

    async def list_all(
        self, skip: int = 0, limit: int = 20, status: OrderStatus | None = None
    ) -> tuple[list[Order], int]:
        """Lista todas las órdenes (admin)."""
        orders = list(self._orders.values())

        if status:
            orders = [o for o in orders if o.status == status]

        total = len(orders)
        orders.sort(key=lambda o: o.created_at, reverse=True)

        return orders[skip : skip + limit], total

    async def update_status(self, order_id: int, status: OrderStatus) -> Order | None:
        """Actualiza estado de orden."""
        order = self._orders.get(order_id)
        if not order:
            return None

        order.status = status

        if status == OrderStatus.COMPLETED and order.completed_at is None:
            order.completed_at = datetime.now(timezone.utc)

        return order


class InMemoryReviewRepository(ReviewRepositoryInterface):
    """
    Repositorio in-memory para Review.

    Simula operaciones CRUD de reseñas con validación de duplicados.
    """

    def __init__(self, game_repo: InMemoryGameCatalogRepository):
        self._reviews: dict[int, Review] = {}
        self._id_sequence = 1
        self.game_repo = game_repo

    async def create(self, user_id: int, data: ReviewCreate) -> Review:
        """Crea reseña (debe validar duplicados en service layer)."""
        review = Review(
            id=self._id_sequence,
            game_id=data.game_id,
            user_id=user_id,
            rating=data.rating,
            comment=data.comment,
            created_at=datetime.now(timezone.utc),
            updated_at=datetime.now(timezone.utc),
        )

        # Cargar relación con game
        review.game = await self.game_repo.get_by_id(data.game_id)
        # Simular relación con usuario para que los servicios puedan acceder a user.full_name.
        review.user = User(
            id=user_id,
            email=f"user{user_id}@example.com",
            hashed_password="not-used",
            full_name=f"Usuario {user_id}",
            role=UserRole.CUSTOMER,
            created_at=datetime.now(timezone.utc),
        )

        self._reviews[review.id] = review
        self._id_sequence += 1

        return review

    async def get_by_id(self, review_id: int) -> Review | None:
        return self._reviews.get(review_id)

    async def get_user_review_for_game(
        self, user_id: int, game_id: int
    ) -> Review | None:
        """Busca reseña existente de un usuario para un juego."""
        return next(
            (
                r
                for r in self._reviews.values()
                if r.user_id == user_id and r.game_id == game_id
            ),
            None,
        )

    async def list_by_game(
        self, game_id: int, skip: int = 0, limit: int = 20
    ) -> tuple[list[Review], int, float]:
        """
        Lista reseñas de un juego.

        Returns:
            Tupla (reseñas, total_count, average_rating)
        """
        game_reviews = [r for r in self._reviews.values() if r.game_id == game_id]
        total = len(game_reviews)

        # Calcular promedio
        if total > 0:
            avg_rating = sum(r.rating for r in game_reviews) / total
        else:
            avg_rating = 0.0

        game_reviews.sort(key=lambda r: r.created_at, reverse=True)

        return game_reviews[skip : skip + limit], total, avg_rating

    async def update(self, review_id: int, data: ReviewUpdate) -> Review | None:
        """Actualiza reseña."""
        review = self._reviews.get(review_id)
        if not review:
            return None

        update_data = data.model_dump(exclude_unset=True)
        for key, value in update_data.items():
            setattr(review, key, value)

        review.updated_at = datetime.now(timezone.utc)
        return review

    async def delete(self, review_id: int, user_id: int) -> bool:
        """Elimina reseña validando ownership."""
        review = self._reviews.get(review_id)
        if not review or review.user_id != user_id:
            return False

        self._reviews.pop(review_id)
        return True
