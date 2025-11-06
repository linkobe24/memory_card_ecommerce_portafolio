from __future__ import annotations

import pytest
from unittest.mock import AsyncMock

from app.main import app
from app.routes.auth import limiter
from app.core.dependencies import (
    get_user_repository,
    get_auth_service,
    get_cache_repository,
    get_cache_service,
    get_rawg_client_dep,
)
from app.services.auth_service import AuthService
from app.services.cache_service import CacheService
from app.clients.rawg.rawg_client import RAWGClient
from app.crud.user_interface import UserRepositoryInterface
from app.crud.cache_interface import CacheRepositoryInterface

from tests.fakes import InMemoryUserRepository, InMemoryCacheRepository


@pytest.fixture(autouse=True)
def in_memory_repo_override() -> tuple[InMemoryUserRepository, InMemoryCacheRepository]:
    """
    Reemplaza las dependencias de repositorio/servicio por versiones
    en memoria para todas las pruebas que importan la app FastAPI.
    """
    user_repo = InMemoryUserRepository()
    cache_repo = InMemoryCacheRepository()

    def _user_repo_override() -> UserRepositoryInterface:
        return user_repo

    def _auth_service_override() -> AuthService:
        return AuthService(user_repository=user_repo)

    def _cache_repo_override() -> CacheRepositoryInterface:
        return cache_repo

    def _cache_service_override() -> CacheService:
        return CacheService(cache_repo=cache_repo)

    app.dependency_overrides[get_user_repository] = _user_repo_override
    app.dependency_overrides[get_auth_service] = _auth_service_override
    app.dependency_overrides[get_cache_repository] = _cache_repo_override
    app.dependency_overrides[get_cache_service] = _cache_service_override

    previous_state = getattr(limiter, "enabled", True)
    limiter.enabled = False

    yield user_repo, cache_repo

    app.dependency_overrides.clear()
    limiter.enabled = previous_state


@pytest.fixture
def mock_rawg_client():
    """
    Mock del cliente RAWG para tests.

    Devuelve datos fake sin consultar API real.
    """
    client = AsyncMock(spec=RAWGClient)

    app.dependency_overrides[get_rawg_client_dep] = lambda: client

    yield client

    app.dependency_overrides.pop(get_rawg_client_dep, None)
