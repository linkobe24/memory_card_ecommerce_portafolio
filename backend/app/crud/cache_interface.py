"""
Interfaz para repositorio de cache.

Define el contrato que deben cumplir todas las implementaciones
(Redis real, Fake in-memory para tests).
"""

from abc import ABC, abstractmethod


class CacheRepositoryInterface(ABC):
    """Contrato para operaciones de cache."""

    @abstractmethod
    async def get(self, key: str) -> str | None:
        """
        Obtiene un valor del cache.

        Returns:
            Valor en string o None si no existe
        """
        pass

    @abstractmethod
    async def set(self, key: str, value: str, ttl: int | None = None) -> None:
        """
        Guarda un valor en cache.

        Args:
            key: Clave única
            value: Valor a guardar (serializado)
            ttl: Tiempo de vida en segundos (None = sin expiración)
        """
        pass

    @abstractmethod
    async def delete(self, key: str) -> None:
        """Elimina una clave del cache."""
        pass

    @abstractmethod
    async def exists(self, key: str) -> bool:
        """Verifica si una clave existe."""
        pass

    @abstractmethod
    async def clear_pattern(self, pattern: str) -> int:
        """
        Elimina todas las claves que coinciden con el patrón.

        Ej: pattern="rawg:game:*" elimina todos los juegos cacheados

        Returns:
            Número de claves eliminadas
        """
        pass
