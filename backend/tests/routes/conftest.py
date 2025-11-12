import pytest
from httpx import AsyncClient, ASGITransport
from unittest.mock import AsyncMock, MagicMock

from app.main import app
from app.schemas.user import UserCreate
from app.schemas.rawg import GameDetail
from app.routes.game_catalog import get_game_catalog_service
from app.routes.cart import get_cart_service
from app.routes.order import get_order_service
from app.routes.review import get_review_service
from app.services.game_catalog_service import GameCatalogService
from app.services.cart_service import CartService
from app.services.order_service import OrderService
from app.services.review_service import ReviewService
from tests.fakes import (
    InMemoryGameCatalogRepository,
    InMemoryCartRepository,
    InMemoryOrderRepository,
    InMemoryReviewRepository,
)


@pytest.fixture
async def client():
    """
    Cliente async de httpx para tests de integración.

    Simula requests HTTP reales a la app FastAPI.
    """
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as ac:
        yield ac


@pytest.fixture
async def auth_headers(client, in_memory_repo_override):
    """
    Headers con JWT token de usuario autenticado (role=customer).

    Útil para tests de endpoints protegidos.
    """
    user_repo, _ = in_memory_repo_override

    # Crear usuario
    user_data = UserCreate(
        email="customer@example.com",
        password="password123",
        full_name="Test Customer",
    )
    await user_repo.create_user(user_data)

    # Login
    login_response = await client.post(
        "/api/auth/login",
        json={"email": "customer@example.com", "password": "password123"},
    )
    token = login_response.json()["access_token"]

    return {"Authorization": f"Bearer {token}"}


@pytest.fixture
async def admin_headers(client, in_memory_repo_override):
    """
    Headers con JWT token de admin (role=admin).

    Útil para tests de endpoints de administración.
    """
    user_repo, _ = in_memory_repo_override

    # Crear admin
    from app.models.user import UserRole

    user_data = UserCreate(
        email="admin@example.com",
        password="admin123",
        full_name="Test Admin",
    )
    user = await user_repo.create_user(user_data)
    user.role = UserRole.ADMIN  # Promocionar a admin

    # Login
    login_response = await client.post(
        "/api/auth/login",
        json={"email": "admin@example.com", "password": "admin123"},
    )
    token = login_response.json()["access_token"]

    return {"Authorization": f"Bearer {token}"}


def _mock_db_session():
    session = MagicMock()
    context_manager = AsyncMock()
    context_manager.__aenter__ = AsyncMock(return_value=session)
    context_manager.__aexit__ = AsyncMock(return_value=None)
    session.begin = MagicMock(return_value=context_manager)
    return session


@pytest.fixture(autouse=True)
def override_domain_services(mock_rawg_client):
    """
    Usa repositorios in-memory para catálogo, carrito y órdenes durante tests.
    Evita conexiones reales a base de datos y facilita assertions determinísticas.
    """
    game_repo = InMemoryGameCatalogRepository()
    cart_repo = InMemoryCartRepository(game_repo)
    order_repo = InMemoryOrderRepository(game_repo)
    review_repo = InMemoryReviewRepository(game_repo)
    mock_session = _mock_db_session()

    catalog_service = GameCatalogService(game_repo=game_repo, rawg_client=mock_rawg_client)
    cart_service = CartService(cart_repo=cart_repo, game_repo=game_repo)
    order_service = OrderService(
        order_repo=order_repo,
        cart_repo=cart_repo,
        game_repo=game_repo,
        db=mock_session,
    )
    review_service = ReviewService(review_repo=review_repo, game_repo=game_repo)

    app.dependency_overrides[get_game_catalog_service] = lambda: catalog_service
    app.dependency_overrides[get_cart_service] = lambda: cart_service
    app.dependency_overrides[get_order_service] = lambda: order_service
    app.dependency_overrides[get_review_service] = lambda: review_service

    yield {
        "game_repo": game_repo,
        "cart_repo": cart_repo,
        "order_repo": order_repo,
        "db_session": mock_session,
        "review_repo": review_repo,
    }

    app.dependency_overrides.pop(get_game_catalog_service, None)
    app.dependency_overrides.pop(get_cart_service, None)
    app.dependency_overrides.pop(get_order_service, None)
    app.dependency_overrides.pop(get_review_service, None)


@pytest.fixture
async def sample_game(client, admin_headers, mock_rawg_client):
    """
    Helper fixture: crea un producto de ejemplo para tests.

    Devuelve el JSON response del endpoint POST /api/game-catalog/.
    """
    mock_rawg_client.get_game_details.return_value = GameDetail(
        id=3498,
        slug="gta-v",
        name="Grand Theft Auto V",
        description="An action game",
        description_raw="An action game",
        background_image="https://example.com/gta.jpg",
        released="2013-09-17",
        rating=4.9,
        platforms=[],
        genres=[],
    )

    response = await client.post(
        "/api/products",
        headers=admin_headers,
        json={"rawg_id": 3498, "price": 59.99, "stock": 10},
    )

    response.raise_for_status()
    return response.json()
