"""
Implementación PostgreSQL del repositorio de GameCatalog.

Usa SQLAlchemy async para operaciones CRUD.
"""

from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func
from app.crud.game_catalog_interface import GameCatalogRepositoryInterface
from app.models.game_catalog import GameCatalog
from app.schemas.game_catalog import GameCatalogCreate, GameCatalogUpdate


class PostgresGameCatalogRepository(GameCatalogRepositoryInterface):
    """Repositorio de productos usando PostgreSQL."""

    def __init__(self, db: AsyncSession):
        self.db = db

    async def create(self, data: GameCatalogCreate, metadata: dict) -> GameCatalog:
        """Crea producto combinando datos admin + metadata RAWG."""
        game = GameCatalog(
            rawg_id=data.rawg_id,
            title=metadata["title"],
            slug=metadata["slug"],
            description=metadata.get("description"),
            image_url=metadata.get("image_url"),
            price=data.price,
            stock=data.stock,
        )

        self.db.add(game)
        await self.db.commit()
        await self.db.refresh(game)
        return game

    async def get_by_id(self, game_id: int) -> GameCatalog | None:
        """Obtiene producto por ID local."""
        result = await self.db.execute(
            select(GameCatalog).where(GameCatalog.id == game_id)
        )
        return result.scalar_one_or_none()

    async def get_by_rawg_id(self, rawg_id: int) -> GameCatalog | None:
        """Obtiene producto por ID de RAWG."""
        result = await self.db.execute(
            select(GameCatalog).where(GameCatalog.rawg_id == rawg_id)
        )
        return result.scalar_one_or_none()

    async def list_all(
        self, skip: int = 0, limit: int = 20, in_stock_only: bool = False
    ) -> tuple[list[GameCatalog], int]:
        """Lista productos con paginación."""
        filters = []
        if in_stock_only:
            filters.append(GameCatalog.stock > 0)

        count_query = select(func.count()).select_from(GameCatalog)
        if filters:
            count_query = count_query.where(*filters)
        total_result = await self.db.execute(count_query)
        total = total_result.scalar()

        data_query = select(GameCatalog)
        if filters:
            data_query = data_query.where(*filters)
        data_query = (
            data_query.order_by(GameCatalog.created_at.desc())
            .offset(skip)
            .limit(limit)
        )

        result = await self.db.execute(data_query)
        games = list(result.scalars().all())

        return games, total

    async def update(self, game_id: int, data: GameCatalogUpdate) -> GameCatalog | None:
        """Actualiza producto (precio, stock, descripción)."""
        game = await self.get_by_id(game_id)
        if not game:
            return None

        # Actualizar solo campos proporcionados
        update_data = data.model_dump(exclude_unset=True)
        for field, value in update_data.items():
            setattr(game, field, value)

        await self.db.commit()
        await self.db.refresh(game)
        return game

    async def delete(self, game_id: int) -> bool:
        """Elimina producto."""
        game = await self.get_by_id(game_id)
        if not game:
            return False

        await self.db.delete(game)
        await self.db.commit()
        return True

    async def reduce_stock(
        self,
        game_id: int,
        quantity: int,
        session: AsyncSession | None = None,
    ) -> GameCatalog | None:
        """
        Reduce stock de producto.

        Raises:
            ValueError si stock insuficiente
        """
        db = session or self.db
        game = await db.get(GameCatalog, game_id)
        if not game:
            return None

        if game.stock < quantity:
            raise ValueError(
                f"Stock insuficiente para {game.title}. "
                f"Disponible: {game.stock}, Solicitado: {quantity}"
            )

        game.stock -= quantity
        if session:
            await db.flush()
        else:
            await db.commit()
        await db.refresh(game)
        return game

    async def increase_stock(
        self,
        game_id: int,
        quantity: int,
        session: AsyncSession | None = None,
    ) -> GameCatalog | None:
        """Aumenta stock de producto."""
        db = session or self.db
        game = await db.get(GameCatalog, game_id)
        if not game:
            return None

        game.stock += quantity
        if session:
            await db.flush()
        else:
            await db.commit()
        await db.refresh(game)
        return game
