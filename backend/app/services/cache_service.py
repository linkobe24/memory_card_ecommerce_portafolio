"""
Servicio de cache que implementa el patrón cache-aside.

Flujo:
1. Intentar obtener de cache
2. Si no existe, ejecutar función de carga (ej: RAWG API)
3. Guardar resultado en cache
4. Devolver resultado
"""

import json
import logging
from typing import Any, Callable, TypeVar
from app.crud.cache_interface import CacheRepositoryInterface
from app.core.config import settings

logger = logging.getLogger(__name__)

T = TypeVar("T")


class CacheService:
    """
    Servicio que orquesta operaciones de cache.

    Responsabilidades:
    - Implementar cache-aside pattern
    - Serializar/deserializar JSON
    - Manejar TTL
    """

    def __init__(self, cache_repo: CacheRepositoryInterface):
        self.cache_repo = cache_repo
        self.default_ttl = settings.CACHE_DEFAULT_TTL

    async def get_or_set(
        self, key: str, fetch_func: Callable[[], Any], ttl: int | None = None
    ) -> Any:
        """
        Cache-aside pattern: busca en cache o ejecuta función de carga.

        Args:
            key: Clave única de cache
            fetch_func: Función async que obtiene datos si no están en cache
            ttl: TTL en segundos (None usa default de config)

        Returns:
            Datos deserializados (dict, list, etc.)
        """
        cached_value = await self.cache_repo.get(key)

        if cached_value is not None:
            logger.info(f"✅ Cache HIT: {key}")
            return json.loads(cached_value)

        logger.info(f"❌ Cache MISS: {key}. Consultando origen...")
        fresh_data = await fetch_func()

        ttl_to_use = ttl if ttl is not None else self.default_ttl
        await self.cache_repo.set(key, json.dumps(fresh_data), ttl=ttl_to_use)
        logger.info(f"💾 Guardado en cache: {key} (TTL: {ttl_to_use}s)")

        return fresh_data

    async def invalidate(self, key: str) -> None:
        """Invalida (elimina) una clave de cache."""
        await self.cache_repo.delete(key)
        logger.info(f"🗑️  Invalidado cache: {key}")

    async def invalidate_pattern(self, pattern: str) -> int:
        """Invalida todas las claves que coinciden con patrón."""
        count = await self.cache_repo.clear_pattern(pattern)
        logger.info(f"🗑️  Invalidadas {count} claves con patrón: {pattern}")
        return count

    def build_key(self, namespace: str, *parts: str | int) -> str:
        """
        Construye clave de cache consistente.

        Ej: build_key("rawg", "game", 123) → "rawg:game:123"
        """
        key_parts = [namespace, *[str(p) for p in parts]]
        return ":".join(key_parts)
