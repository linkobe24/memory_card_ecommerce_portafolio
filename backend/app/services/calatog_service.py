"""
Servicio de catálogo que orquesta RAWG API y cache.

Responsabilidades:
- Coordinar RAWG client y cache service
- Aplicar lógica de negocio (ej: filtros, enriquecimiento de datos)
- Manejar errores y retornar respuestas consistentes
"""

from app.clients.rawg.rawg_client import RAWGClient
from app.services.cache_service import CacheService
from app.schemas.rawg import (
    GameListResponse,
    GameDetail,
    GenreListResponse,
    PlatformListResponse,
)


class CatalogService:
    """
    Servicio que provee acceso al catálogo de juegos.

    Usa cache-aside pattern para todas las consultas a RAWG.
    """

    def __init__(self, rawg_client: RAWGClient, cache_service: CacheService):
        self.rawg = rawg_client
        self.cache = cache_service

    async def search_games(
        self,
        query: str,
        page: int = 1,
        page_size: int = 20,
        genres: str | None = None,
        platforms: str | None = None,
    ) -> GameListResponse:
        """
        Busca juegos con cache.

        Cache key incluye todos los parámetros para evitar conflictos.
        """
        cache_key = self.cache.build_key(
            "rawg",
            "search",
            query,
            f"p{page}",
            f"ps{page_size}",
            f"g{genres or 'none'}",
            f"pl{platforms or 'none'}",
        )

        async def fetch_from_rawg():
            response = await self.rawg.search_games(
                query=query,
                page=page,
                page_size=page_size,
                genres=genres,
                platforms=platforms,
            )
            return response.model_dump(mode="json")

        data = await self.cache.get_or_set(
            key=cache_key, fetch_func=fetch_from_rawg
        )
        return GameListResponse(**data)

    async def get_game_details(self, game_id: int) -> GameDetail:
        """
        Obtiene detalles de un juego con cache.
        """
        cache_key = self.cache.build_key("rawg", "game", game_id)

        async def fetch_from_rawg():
            game = await self.rawg.get_game_details(game_id)
            return game.model_dump(mode="json")

        data = await self.cache.get_or_set(
            key=cache_key, fetch_func=fetch_from_rawg
        )
        return GameDetail(**data)

    async def list_genres(self) -> GenreListResponse:
        """
        Lista géneros con cache.

        TTL largo (7 días) porque géneros cambian raramente.
        """
        cache_key = self.cache.build_key("rawg", "genres")

        async def fetch_from_rawg():
            response = await self.rawg.list_genres()
            return response.model_dump(mode="json")

        data = await self.cache.get_or_set(
            key=cache_key, fetch_func=fetch_from_rawg, ttl=604800
        )
        return GenreListResponse(**data)

    async def list_platforms(self) -> PlatformListResponse:
        """
        Lista plataformas con cache.

        TTL largo (7 días) porque plataformas cambian raramente.
        """
        cache_key = self.cache.build_key("rawg", "platforms")

        async def fetch_from_rawg():
            response = await self.rawg.list_platforms()
            return response.model_dump(mode="json")

        data = await self.cache.get_or_set(
            key=cache_key, fetch_func=fetch_from_rawg, ttl=604800
        )
        return PlatformListResponse(**data)
