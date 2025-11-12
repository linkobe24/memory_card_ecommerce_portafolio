"""
Interfaz para repositorio de GameCatalog.

Define operaciones CRUD para productos de la tienda.
"""

from abc import ABC, abstractmethod
from sqlalchemy.ext.asyncio import AsyncSession
from app.models.game_catalog import GameCatalog
from app.schemas.game_catalog import GameCatalogCreate, GameCatalogUpdate


class GameCatalogRepositoryInterface(ABC):

    @abstractmethod
    async def create(self, data: GameCatalogCreate, metadata: dict) -> GameCatalog:
        """
        Crea un producto en la tienda.

        Args:
            data: Datos del admin (rawg_id, precio, stock)
            metadata: Metadata de RAWG (title, slug, description, image_url)

        Returns:
            GameCatalog creado
        """
        pass

    @abstractmethod
    async def get_by_id(self, game_id: int) -> GameCatalog | None:
        """Obtiene producto por ID local."""
        pass

    @abstractmethod
    async def get_by_rawg_id(self, rawg_id: int) -> GameCatalog | None:
        """Obtiene producto por ID de RAWG."""
        pass

    @abstractmethod
    async def list_all(
        self, skip: int = 0, limit: int = 20, in_stock_only: bool = False
    ) -> tuple[list[GameCatalog], int]:
        """
        Lista productos con paginación.

        Returns:
            Tupla (productos, total_count)
        """
        pass

    @abstractmethod
    async def update(self, game_id: int, data: GameCatalogUpdate) -> GameCatalog | None:
        """Actualiza producto (precio, stock)."""
        pass

    @abstractmethod
    async def delete(self, game_id: int) -> bool:
        """
        Elimina producto.

        Returns:
            True si se eliminó, False si no existía
        """
        pass

    @abstractmethod
    async def reduce_stock(
        self,
        game_id: int,
        quantity: int,
        session: AsyncSession | None = None,
    ) -> GameCatalog | None:
        """
        Reduce stock de un producto (al crear orden).

        Raises:
            ValueError si stock insuficiente
        """
        pass

    @abstractmethod
    async def increase_stock(
        self,
        game_id: int,
        quantity: int,
        session: AsyncSession | None = None,
    ) -> GameCatalog | None:
        """Aumenta stock de un producto (al cancelar orden)."""
        pass
