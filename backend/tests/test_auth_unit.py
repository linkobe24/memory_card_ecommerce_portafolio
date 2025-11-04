import pytest
from httpx import AsyncClient
from app.main import app
from app.core.dependencies import get_user_repository
from tests.mocks.mock_user_repository import MockUserRepository


def override_get_user_repository():
    return MockUserRepository()


app.dependency_overrides[get_user_repository] = override_get_user_repository


@pytest.mark.asyncio
async def test_register_with_mock():
    """
    Unit test: Registro usando mock repository (sin DB).
    """
    async with AsyncClient(app=app, base_url="http://test") as client:
        response = await client.post(
            "/api/auth/register",
            json={
                "email": "mock@example.com",
                "password": "password123",
                "full_name": "Mock User",
            },
        )

    assert response.status_code == 201
    data = response.json()
    assert "access_token" in data
    assert "refresh_token" in data


@pytest.mark.asyncio
async def test_login_with_mock():
    """
    Unit test: Login usando mock repository (sin DB).
    """
    async with AsyncClient(app=app, base_url="http://test") as client:
        # Registrar
        await client.post(
            "/api/auth/register",
            json={
                "email": "mocklogin@example.com",
                "password": "password123",
                "full_name": "Mock Login",
            },
        )

        # Login
        response = await client.post(
            "/api/auth/login",
            json={"email": "mocklogin@example.com", "password": "password123"},
        )

    assert response.status_code == 200
    assert "access_token" in response.json()
