# backend/tests/services/conftest.py

import pytest
from unittest.mock import AsyncMock, MagicMock

from app.services.cart_service import CartService
from app.services.order_service import OrderService
from app.services.game_catalog_service import GameCatalogService
from app.services.review_service import ReviewService
from app.clients.rawg.rawg_client import RAWGClient
from app.schemas.rawg import GameDetail

from tests.fakes import (
    InMemoryGameCatalogRepository,
    InMemoryCartRepository,
    InMemoryOrderRepository,
    InMemoryReviewRepository,
)


@pytest.fixture
def game_repo():
    """Repositorio in-memory de GameCatalog."""
    return InMemoryGameCatalogRepository()


@pytest.fixture
def cart_repo(game_repo):
    """Repositorio in-memory de Cart (depende de game_repo)."""
    return InMemoryCartRepository(game_repo)


@pytest.fixture
def order_repo(game_repo):
    """Repositorio in-memory de Order (depende de game_repo)."""
    return InMemoryOrderRepository(game_repo)


@pytest.fixture
def review_repo(game_repo):
    """Repositorio in-memory de Review (depende de game_repo)."""
    return InMemoryReviewRepository(game_repo)


@pytest.fixture
def mock_db_session():
    """
    Mock de AsyncSession para tests de OrderService.

    OrderService usa transacciones pero en tests con fakes
    no necesitamos rollback real.
    """
    session = MagicMock()

    # Mock del context manager (async with session.begin())
    context_manager = AsyncMock()
    context_manager.__aenter__ = AsyncMock(return_value=session)
    context_manager.__aexit__ = AsyncMock(return_value=None)

    session.begin = MagicMock(return_value=context_manager)

    return session


@pytest.fixture
def mock_rawg_client():
    """
    Mock del cliente RAWG para tests de GameCatalogService.

    Devuelve metadata fake sin consultar API real.
    """
    client = AsyncMock(spec=RAWGClient)

    # Configurar comportamiento por defecto con la misma estructura que devuelve RAWGClient.
    mock_game = GameDetail(
        id=3498,
        slug="grand-theft-auto-v",
        name="Grand Theft Auto V",
        description="An action-adventure game...",
        description_raw="An action-adventure game...",
        background_image="https://media.rawg.io/media/games/456/456dea5e1c7e3cd07060c14e96612001.jpg",
        released="2013-09-17",
        rating=4.5,
        platforms=[],
        genres=[],
    )
    client.get_game_details = AsyncMock(return_value=mock_game)

    return client


@pytest.fixture
def cart_service(cart_repo, game_repo):
    """Service de carrito con fakes."""
    return CartService(cart_repo=cart_repo, game_repo=game_repo)


@pytest.fixture
def order_service(order_repo, cart_repo, game_repo, mock_db_session):
    """Service de órdenes con fakes."""
    return OrderService(
        order_repo=order_repo,
        cart_repo=cart_repo,
        game_repo=game_repo,
        db=mock_db_session,
    )


@pytest.fixture
def game_catalog_service(game_repo, mock_rawg_client):
    """Service de catálogo con fake y mock de RAWG."""
    return GameCatalogService(game_repo=game_repo, rawg_client=mock_rawg_client)


@pytest.fixture
def review_service(review_repo, game_repo):
    """Service de reseñas con fakes."""
    return ReviewService(review_repo=review_repo, game_repo=game_repo)
