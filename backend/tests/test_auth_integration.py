import sys
from pathlib import Path

sys.path.append(str(Path(__file__).resolve().parents[1]))

import pytest
from uuid import uuid4
from datetime import datetime, timezone

from httpx import AsyncClient, ASGITransport

from app.main import app
from app.core.dependencies import get_user_repository, get_auth_service
from app.services.auth_service import AuthService
from app.crud.user_interface import UserRepositoryInterface
from app.schemas.user import UserCreate, UserUpdate
from app.models.user import User, UserRole
from app.core.security import hash_password
from app.routes.auth import limiter


def unique_email(label: str) -> str:
    return f"{label}-{uuid4().hex}@example.com"


class InMemoryUserRepository(UserRepositoryInterface):
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
            user.hashed_password = payload["password"]
        return user

    async def delete(self, id: int) -> bool:
        user = await self.get_by_id(id)
        if not user:
            return False
        self._by_id.pop(id, None)
        self._users.pop(user.email, None)
        return True

    async def update_last_login(self, user_id: int) -> None:
        # No-op for in-memory repo
        return None


@pytest.fixture(autouse=True)
def override_dependencies():
    repo = InMemoryUserRepository()

    def _user_repo_override() -> UserRepositoryInterface:
        return repo

    def _auth_service_override() -> AuthService:
        return AuthService(user_repository=repo)

    app.dependency_overrides[get_user_repository] = _user_repo_override
    app.dependency_overrides[get_auth_service] = _auth_service_override
    previous_enabled = getattr(limiter, "enabled", True)
    limiter.enabled = False
    yield
    app.dependency_overrides.clear()
    limiter.enabled = previous_enabled


@pytest.mark.asyncio
async def test_register_success():
    """
    Integration test: Registro exitoso de usuario nuevo (con DB real).
    """
    transport = ASGITransport(app=app)
    email = unique_email("register")

    async with AsyncClient(transport=transport, base_url="http://test") as client:
        response = await client.post(
            "/api/auth/register",
            json={
                "email": email,
                "password": "password123",
                "full_name": "Test User",
            },
        )

    assert response.status_code == 201
    data = response.json()
    assert "access_token" in data
    assert "refresh_token" in data
    assert data["token_type"] == "bearer"


@pytest.mark.asyncio
async def test_register_duplicate_email():
    """
    Integration test: Registro con email duplicado devuelve error 400.
    """
    transport = ASGITransport(app=app)
    email = unique_email("duplicate")

    async with AsyncClient(transport=transport, base_url="http://test") as client:
        # Primer registro
        first_response = await client.post(
            "/api/auth/register",
            json={
                "email": email,
                "password": "password123",
                "full_name": "Test User",
            },
        )

        assert first_response.status_code == 201

        # Segundo registro con mismo email
        response = await client.post(
            "/api/auth/register",
            json={
                "email": email,
                "password": "password456",
                "full_name": "Another User",
            },
        )

        assert response.status_code == 400, f"Unexpected response: {response.status_code} -> {response.json()}"
        assert response.json()["detail"] == f"El email '{email}' ya está registrado"


@pytest.mark.asyncio
async def test_login_success():
    """
    Integration test: Login exitoso con credenciales correctas.
    """
    transport = ASGITransport(app=app)
    email = unique_email("login")

    async with AsyncClient(transport=transport, base_url="http://test") as client:
        # Registrar usuario
        await client.post(
            "/api/auth/register",
            json={
                "email": email,
                "password": "password123",
                "full_name": "Login Test",
            },
        )

        # Login
        response = await client.post(
            "/api/auth/login",
            json={"email": email, "password": "password123"},
        )

    assert response.status_code == 200
    data = response.json()
    assert "access_token" in data
    assert "refresh_token" in data


@pytest.mark.asyncio
async def test_login_wrong_password():
    """
    Integration test: Login con password incorrecta devuelve error 401.
    """
    transport = ASGITransport(app=app)
    email = unique_email("wrong")

    async with AsyncClient(transport=transport, base_url="http://test") as client:
        # Registrar usuario
        await client.post(
            "/api/auth/register",
            json={
                "email": email,
                "password": "correctpassword",
                "full_name": "Wrong Test",
            },
        )

        # Login con password incorrecta
        response = await client.post(
            "/api/auth/login",
            json={"email": email, "password": "wrongpassword"},
        )

    assert response.status_code == 401
    assert response.json()["detail"] == "Email o contraseña incorrectos"


@pytest.mark.asyncio
async def test_refresh_token():
    """
    Integration test: Refresh token genera nuevo access token.
    """
    transport = ASGITransport(app=app)
    email = unique_email("refresh")

    async with AsyncClient(transport=transport, base_url="http://test") as client:
        # Registrar usuario
        register_response = await client.post(
            "/api/auth/register",
            json={
                "email": email,
                "password": "password123",
                "full_name": "Refresh Test",
            },
        )
        refresh_token = register_response.json()["refresh_token"]

        # Refresh
        response = await client.post(
            "/api/auth/refresh", json={"refresh_token": refresh_token}
        )

    assert response.status_code == 200
    data = response.json()
    assert "access_token" in data
    assert data["token_type"] == "bearer"


@pytest.mark.asyncio
async def test_get_me():
    """
    Integration test: Endpoint protegido /me devuelve usuario autenticado.
    """
    transport = ASGITransport(app=app)
    email = unique_email("me")

    async with AsyncClient(transport=transport, base_url="http://test") as client:
        # Registrar usuario
        register_response = await client.post(
            "/api/auth/register",
            json={
                "email": email,
                "password": "password123",
                "full_name": "Me Test",
            },
        )
        access_token = register_response.json()["access_token"]

        # Request a /me con Authorization header
        response = await client.get(
            "/api/auth/me", headers={"Authorization": f"Bearer {access_token}"}
        )

    assert response.status_code == 200
    data = response.json()
    assert data["email"] == email
    assert data["full_name"] == "Me Test"
    assert "hashed_password" not in data  # Seguridad: password no se devuelve


@pytest.mark.asyncio
async def test_get_me_no_token():
    """
    Integration test: Endpoint protegido sin token devuelve error 401.
    """
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as client:
        response = await client.get("/api/auth/me")

    assert response.status_code == 403


@pytest.mark.asyncio
async def test_get_me_invalid_token():
    """
    Integration test: Endpoint protegido con token inválido devuelve error 401.
    """
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as client:
        response = await client.get(
            "/api/auth/me", headers={"Authorization": "Bearer invalid_token_12345"}
        )

    assert response.status_code == 401
