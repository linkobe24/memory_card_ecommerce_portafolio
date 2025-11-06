"""
Tests de integración para endpoints de catálogo.

Usa Fake Cache Repository y Mock RAWG Client.
"""

import pytest
from httpx import AsyncClient, ASGITransport

from app.main import app
from app.schemas.rawg import GameListResponse, GameShort, GameDetail


@pytest.mark.asyncio
async def test_search_games_returns_results(mock_rawg_client):
    """Buscar juegos devuelve resultados de RAWG."""

    # Mock de respuesta RAWG
    mock_response = GameListResponse(
        count=1,
        next=None,
        previous=None,
        results=[
            GameShort(
                id=3498,
                slug="grand-theft-auto-v",
                name="Grand Theft Auto V",
                released="2013-09-17",
                background_image="https://example.com/gta5.jpg",
                rating=4.5,
                rating_top=5,
                ratings_count=5000,
                metacritic=96,
                playtime=50,
                platforms=[],
                genres=[],
            )
        ],
    )

    mock_rawg_client.search_games.return_value = mock_response

    async with AsyncClient(
        transport=ASGITransport(app=app), base_url="http://test"
    ) as client:
        response = await client.get("/api/catalog/search?query=gta")

    assert response.status_code == 200
    data = response.json()

    assert data["count"] == 1
    assert len(data["results"]) == 1
    assert data["results"][0]["name"] == "Grand Theft Auto V"

    # Verificar que llamó al cliente RAWG
    mock_rawg_client.search_games.assert_called_once()


@pytest.mark.asyncio
async def test_search_games_uses_cache(mock_rawg_client, in_memory_repo_override):
    """Segunda búsqueda usa cache (cache hit)."""

    _, cache_repo = in_memory_repo_override

    mock_response = GameListResponse(
        count=1,
        next=None,
        previous=None,
        results=[
            GameShort(
                id=3498,
                slug="gta-v",
                name="GTA V",
                released="2013-09-17",
                background_image="https://example.com/gta5.jpg",
                rating=4.5,
                platforms=[],
                genres=[],
            )
        ],
    )
    mock_rawg_client.search_games.return_value = mock_response

    async with AsyncClient(
        transport=ASGITransport(app=app), base_url="http://test"
    ) as client:
        # Primera request: cache miss
        response1 = await client.get(
            "/api/catalog/search?query=gta&page=1&page_size=20"
        )
        assert response1.status_code == 200

        # Segunda request: cache hit
        response2 = await client.get(
            "/api/catalog/search?query=gta&page=1&page_size=20"
        )
        assert response2.status_code == 200

    # RAWG client debe llamarse solo 1 vez (segunda usa cache)
    assert mock_rawg_client.search_games.call_count == 1

    # Verificar que existe en cache
    cache_key = "rawg:search:gta:p1:ps20:gnone:plnone"
    assert await cache_repo.exists(cache_key)


@pytest.mark.asyncio
async def test_get_game_details_returns_full_info(mock_rawg_client):
    """Obtener detalles de juego devuelve información completa."""

    mock_game = GameDetail(
        id=3498,
        slug="gta-v",
        name="Grand Theft Auto V",
        released="2013-09-17",
        background_image="https://example.com/gta5.jpg",
        rating=4.5,
        description="<p>Open world game...</p>",
        description_raw="Open world game...",
        website="https://www.rockstargames.com/gta-v",
        platforms=[],
        genres=[],
        stores=[],
    )
    mock_rawg_client.get_game_details.return_value = mock_game

    async with AsyncClient(
        transport=ASGITransport(app=app), base_url="http://test"
    ) as client:
        response = await client.get("/api/catalog/game/3498")

    assert response.status_code == 200
    data = response.json()

    assert data["name"] == "Grand Theft Auto V"
    assert data["description_raw"] == "Open world game..."
    assert data["website"] == "https://www.rockstargames.com/gta-v"


@pytest.mark.asyncio
async def test_get_game_details_not_found(mock_rawg_client):
    """Juego inexistente devuelve 404."""

    from app.clients.rawg.rawg_client import RAWGAPIError

    mock_rawg_client.get_game_details.side_effect = RAWGAPIError(
        "Error en request a RAWG: 404 - Not Found"
    )

    async with AsyncClient(
        transport=ASGITransport(app=app), base_url="http://test"
    ) as client:
        response = await client.get("/api/catalog/game/999999")

    assert response.status_code == 404
    assert "no encontrado" in response.json()["detail"]


@pytest.mark.asyncio
async def test_list_genres_returns_genres(mock_rawg_client):
    """Listar géneros devuelve lista completa."""

    from app.schemas.rawg import GenreListResponse, Genre

    mock_response = GenreListResponse(
        count=2,
        results=[
            Genre(id=4, name="Action", slug="action", games_count=50000),
            Genre(id=51, name="Indie", slug="indie", games_count=30000),
        ],
    )
    mock_rawg_client.list_genres.return_value = mock_response

    async with AsyncClient(
        transport=ASGITransport(app=app), base_url="http://test"
    ) as client:
        response = await client.get("/api/catalog/genres")

    assert response.status_code == 200
    data = response.json()

    assert data["count"] == 2
    assert len(data["results"]) == 2
    assert data["results"][0]["name"] == "Action"
    assert data["results"][1]["name"] == "Indie"


@pytest.mark.asyncio
async def test_list_platforms_returns_platforms(mock_rawg_client):
    """Listar plataformas devuelve lista completa."""

    from app.schemas.rawg import PlatformListResponse, Platform

    mock_response = PlatformListResponse(
        count=2,
        results=[
            Platform(id=4, name="PC", slug="pc", games_count=100000),
            Platform(id=7, name="Nintendo Switch", slug="switch", games_count=20000),
        ],
    )
    mock_rawg_client.list_platforms.return_value = mock_response

    async with AsyncClient(
        transport=ASGITransport(app=app), base_url="http://test"
    ) as client:
        response = await client.get("/api/catalog/platforms")

    assert response.status_code == 200
    data = response.json()

    assert data["count"] == 2
    assert data["results"][0]["name"] == "PC"
    assert data["results"][1]["name"] == "Nintendo Switch"


@pytest.mark.asyncio
async def test_cache_invalidation_pattern(in_memory_repo_override):
    """Invalidar patrón elimina múltiples claves."""

    _, cache_repo = in_memory_repo_override

    # Guardar múltiples claves
    await cache_repo.set("rawg:game:1", "data1")
    await cache_repo.set("rawg:game:2", "data2")
    await cache_repo.set("rawg:search:mario", "data3")

    # Invalidar solo juegos
    count = await cache_repo.clear_pattern("rawg:game:*")

    assert count == 2
    assert not await cache_repo.exists("rawg:game:1")
    assert not await cache_repo.exists("rawg:game:2")
    assert await cache_repo.exists("rawg:search:mario")  # No debe eliminarse
