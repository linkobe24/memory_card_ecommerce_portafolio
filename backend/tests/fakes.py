from __future__ import annotations

from datetime import datetime, timezone
from uuid import uuid4

from app.crud.user_interface import UserRepositoryInterface
from app.crud.cache_interface import CacheRepositoryInterface
from app.models.user import User, UserRole
from app.schemas.user import UserCreate, UserUpdate
from app.core.security import hash_password


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
