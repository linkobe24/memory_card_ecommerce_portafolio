from __future__ import annotations

import pytest

from app.main import app
from app.routes.auth import limiter
from app.core.dependencies import get_user_repository, get_auth_service
from app.services.auth_service import AuthService
from app.crud.user_interface import UserRepositoryInterface

from tests.fakes import InMemoryUserRepository


@pytest.fixture(autouse=True)
def in_memory_repo_override() -> InMemoryUserRepository:
    """
    Reemplaza las dependencias de repositorio/servicio por versiones
    en memoria para todas las pruebas que importan la app FastAPI.
    """
    repo = InMemoryUserRepository()

    def _user_repo_override() -> UserRepositoryInterface:
        return repo

    def _auth_service_override() -> AuthService:
        return AuthService(user_repository=repo)

    app.dependency_overrides[get_user_repository] = _user_repo_override
    app.dependency_overrides[get_auth_service] = _auth_service_override

    previous_state = getattr(limiter, "enabled", True)
    limiter.enabled = False

    yield repo

    app.dependency_overrides.clear()
    limiter.enabled = previous_state
