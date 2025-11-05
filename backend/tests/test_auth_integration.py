import sys
from pathlib import Path

sys.path.append(str(Path(__file__).resolve().parents[1]))

import pytest

from httpx import AsyncClient, ASGITransport

from app.main import app

from tests.fakes import generate_unique_email as unique_email


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
