"""
Servicio de productos (GameCatalog).

Lógica de negocio:
- Validar que rawg_id no esté duplicado
- Obtener metadata de RAWG antes de crear producto
- Enriquecer productos con datos de RAWG al listar
"""

from app.crud.game_catalog_interface import GameCatalogRepositoryInterface
from app.clients.rawg.rawg_client import RAWGClient, RAWGAPIError
from app.schemas.game_catalog import (
    GameCatalogCreate,
    GameCatalogUpdate,
    GameCatalogResponse,
    GameCatalogEnriched,
)
from app.models.game_catalog import GameCatalog


class GameCatalogService:
    """Servicio de productos con lógica de negocio."""

    def __init__(
        self,
        game_repo: GameCatalogRepositoryInterface,
        rawg_client: RAWGClient,
    ):
        self.game_repo = game_repo
        self.rawg = rawg_client

    async def create_product(self, data: GameCatalogCreate) -> GameCatalogResponse:
        """
        Crea producto en la tienda.

        Flujo:
        1. Verificar que rawg_id no esté duplicado
        2. Obtener metadata de RAWG
        3. Crear producto en DB

        Raises:
            ValueError si rawg_id ya existe
            RAWGAPIError si juego no existe en RAWG
        """
        existing = await self.game_repo.get_by_rawg_id(data.rawg_id)
        if existing:
            raise ValueError(
                f"Producto con rawg_id {data.rawg_id} ya existe (ID local: {existing.id})"
            )

        try:
            rawg_game = await self.rawg.get_game_details(data.rawg_id)
        except RAWGAPIError as e:
            raise RAWGAPIError(
                f"No se pudo obtener información del juego desde RAWG: {str(e)}"
            )

        metadata = {
            "title": rawg_game.name,
            "slug": rawg_game.slug,
            "description": rawg_game.description_raw,
            "image_url": rawg_game.background_image,
        }

        game = await self.game_repo.create(data, metadata)
        return GameCatalogResponse.model_validate(game)

    async def get_product_enriched(self, game_id: int) -> GameCatalogEnriched | None:
        """
        Obtiene producto enriquecido con datos de RAWG.

        Combina datos locales (precio, stock) con metadata actualizada de RAWG.
        """
        # Obtener datos locales
        game = await self.game_repo.get_by_id(game_id)
        if not game:
            return None

        # Obtener metadata de RAWG (desde cache si existe)
        try:
            rawg_game = await self.rawg.get_game_details(game.rawg_id)
        except RAWGAPIError:
            # Si RAWG falla, devolver solo datos locales
            return GameCatalogEnriched(
                id=game.id,
                rawg_id=game.rawg_id,
                price=game.price,
                stock=game.stock,
                in_stock=game.stock > 0,
                name=game.title,
                slug=game.slug,
                description=game.description,
                background_image=game.image_url,
                rating=None,
                released=None,
                platforms=[],
                genres=[],
            )

        # Combinar datos
        return GameCatalogEnriched(
            # Datos locales
            id=game.id,
            rawg_id=game.rawg_id,
            price=game.price,
            stock=game.stock,
            in_stock=game.stock > 0,
            # Metadata de RAWG
            name=rawg_game.name,
            slug=rawg_game.slug,
            description=rawg_game.description_raw,
            background_image=rawg_game.background_image,
            rating=rawg_game.rating,
            released=str(rawg_game.released) if rawg_game.released else None,
            platforms=[p.platform.model_dump() for p in (rawg_game.platforms or [])],
            genres=[g.model_dump() for g in (rawg_game.genres or [])],
        )

    async def list_products(
        self, page: int = 1, page_size: int = 20, in_stock_only: bool = False
    ) -> dict:
        """
        Lista productos con paginación.

        Returns:
            Dict con total, page, page_size, results
        """
        skip = (page - 1) * page_size
        games, total = await self.game_repo.list_all(
            skip=skip, limit=page_size, in_stock_only=in_stock_only
        )

        return {
            "total": total,
            "page": page,
            "page_size": page_size,
            "results": [GameCatalogResponse.model_validate(g) for g in games],
        }

    async def update_product(
        self, game_id: int, data: GameCatalogUpdate
    ) -> GameCatalogResponse | None:
        """Actualiza producto (precio, stock)."""
        game = await self.game_repo.update(game_id, data)
        if not game:
            return None
        return GameCatalogResponse.model_validate(game)

    async def delete_product(self, game_id: int) -> bool:
        """Elimina producto."""
        return await self.game_repo.delete(game_id)
