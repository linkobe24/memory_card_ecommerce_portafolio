"""
Cliente para RAWG API con retry logic y manejo de errores.

Responsabilidades:
- Realizar requests HTTP a RAWG con httpx async
- Implementar exponential backoff en caso de errores
- Validar respuestas con schemas Pydantic
- Manejar rate limits (1000 req/hora)
"""

import asyncio
import logging
from typing import Any
import httpx

from app.core.config import settings
from app.schemas.rawg import (
    GameListResponse,
    GameDetail,
    GenreListResponse,
    PlatformListResponse,
)

logger = logging.getLogger(__name__)


class RAWGAPIError(Exception):
    """Error base para problemas con RAWG API."""

    pass


class RateLimitError(RAWGAPIError):
    """Rate limit de RAWG excedido (429)."""

    pass


class RAWGClient:
    """
    Cliente asíncrono para RAWG API.

    Implementa:
    - Retry logic con exponential backoff
    - Validación de respuestas con Pydantic
    - Manejo de rate limits
    """

    def __init__(self):
        self.base_url = settings.RAWG_BASE_URL
        self.api_key = settings.RAWG_API_KEY
        self.timeout = settings.RAWG_REQUEST_TIMEOUT
        self.max_retries = settings.RAWG_MAX_RETRIES
        # self.client = httpx.AsyncClient(timeout=self.timeout)

        if not self.api_key:
            logger.warning("⚠️  RAWG_API_KEY no configurada. Requests fallarán.")

    # async def close(self):
    #     await self.client.aclose()

    async def _request(
        self,
        method: str,
        endpoint: str,
        params: dict[str, Any] | None = None,
        retry_count: int = 0,
    ) -> dict:
        """
        Realiza una request HTTP con retry logic.

        Exponential backoff: 1s → 2s → 4s entre reintentos.
        """
        url = f"{self.base_url}/{endpoint}"

        if params is None:
            params = {}
        params["key"] = self.api_key

        try:

            # response = await self.client.request(method, url, params=params)
            async with httpx.AsyncClient(timeout=self.timeout) as client:
                response = await client.request(method, url, params=params)

            if response.status_code == 429:
                raise RateLimitError(
                    "Rate limit de RAWG excedido (1000 req/hora). "
                    "Intenta nuevamente más tarde."
                )

            if 500 <= response.status_code < 600:
                if retry_count < self.max_retries:
                    delay = 2**retry_count
                    logger.warning(
                        f"Error {response.status_code} en RAWG. "
                        f"Reintento {retry_count + 1}/{self.max_retries} "
                        f"en {delay}s..."
                    )
                    await asyncio.sleep(delay)
                    return await self._request(
                        method, endpoint, params, retry_count + 1
                    )
                raise RAWGAPIError(
                    f"RAWG API error {response.status_code} después de "
                    f"{self.max_retries} reintentos"
                )

            if 400 <= response.status_code < 500:
                raise RAWGAPIError(
                    f"Error en request a RAWG: {response.status_code} - "
                    f"{response.text}"
                )

            response.raise_for_status()
            return response.json()

        except httpx.TimeoutException:
            if retry_count < self.max_retries:
                delay = 2**retry_count
                logger.warning(
                    f"Timeout en RAWG. Reintento {retry_count + 1}/{self.max_retries} "
                    f"en {delay}s..."
                )
                await asyncio.sleep(delay)
                return await self._request(method, endpoint, params, retry_count + 1)
            raise RAWGAPIError(
                f"Timeout en RAWG API después de {self.max_retries} reintentos"
            )

        except httpx.RequestError as e:
            raise RAWGAPIError(f"Error de conexión con RAWG: {str(e)}")

    async def search_games(
        self,
        query: str,
        page: int = 1,
        page_size: int = 20,
        genres: str | None = None,
        platforms: str | None = None,
    ) -> GameListResponse:
        """
        Busca juegos por nombre.

        Args:
            query: Término de búsqueda
            page: Número de página (default: 1)
            page_size: Juegos por página (default: 20, max: 40)
            genres: IDs de géneros separados por coma (ej: "4,51")
            platforms: IDs de plataformas separados por coma (ej: "4,187")

        Returns:
            GameListResponse con resultados paginados
        """
        params = {
            "search": query,
            "page": page,
            "page_size": min(page_size, 40),
        }  # rawg max: 40

        if genres:
            params["genres"] = genres
        if platforms:
            params["platforms"] = platforms

        data = await self._request("GET", "games", params)
        return GameListResponse(**data)

    async def get_game_details(self, game_id: int) -> GameDetail:
        """
        Obtiene detalles completos de un juego.

        Args:
            game_id: ID del juego en RAWG

        Returns:
            GameDetail con toda la información
        """
        data = await self._request("GET", f"games/{game_id}")
        return GameDetail(**data)

    async def list_genres(self) -> GenreListResponse:
        """
        Lista todos los géneros disponibles.

        Returns:
            GenreListResponse con lista de géneros
        """
        data = await self._request("GET", "genres")
        return GenreListResponse(**data)

    async def list_platforms(self) -> PlatformListResponse:
        """
        Lista todas las plataformas disponibles.

        Returns:
            PlatformListResponse con lista de plataformas
        """
        data = await self._request("GET", "platforms")
        return PlatformListResponse(**data)


_rawg_client: RAWGClient | None = None


def get_rawg_client() -> RAWGClient:
    global _rawg_client
    if _rawg_client is None:
        _rawg_client = RAWGClient()
    return _rawg_client
