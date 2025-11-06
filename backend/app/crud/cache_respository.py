"""
Implementación Redis del repositorio de cache.

Usa redis-py con soporte async.
"""

import redis.asyncio as redis
from app.crud.cache_interface import CacheRepositoryInterface
from app.core.config import settings


class RedisCacheRepository(CacheRepositoryInterface):
    """Repositorio de cache usando Redis."""

    def __init__(self):
        self.redis_client: redis.Redis | None = None

    async def _get_client(self) -> redis.Redis:
        """Lazy initialization del cliente Redis."""
        if self.redis_client is None:
            self.redis_client = redis.from_url(
                settings.REDIS_URL,
                encoding="utf-8",
                decode_responses=True,
            )
        return self.redis_client
    
    async def get(self, key: str) -> str | None:
        """Obtiene valor del cache."""
        client = await self._get_client()
        return await client.get(key)
    
    async def set(self, key: str, value: str, ttl: int | None = None):
        """
        Guarda valor en cache con TTL opcional.

        Si ttl es None, la clave no expira.
        """
        client = await self._get_client()
        if ttl:
            await client.setex(key, ttl, value)
        else:
            await client.set(key, value)

    async def delete(self, key: str) -> None:
        """Elimina clave del cache."""
        client = await self._get_client()
        await client.delete(key)
    
    async def exists(self, key: str) -> bool:
        """Verifica si clave existe."""
        client = await self._get_client()
        return await client.exists(key) > 0
    
    async def clear_pattern(self, pattern: str) -> int:
        """
        Elimina claves por patrón usando SCAN.

        SCAN es más seguro que KEYS en producción (no bloquea).
        """
        client = await self._get_client()
        count = 0
        async for key in client.scan_iter(match=pattern):
            await client.delete(key)
            count += 1
        return count
    
    async def close(self):
        """Cierra conexión Redis."""
        if self.redis_client:
            await self.redis_client.close()

    
