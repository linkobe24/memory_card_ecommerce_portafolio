import pytest
from app.schemas.rawg import GameDetail


@pytest.mark.asyncio
async def test_create_product_requires_admin(client, auth_headers, mock_rawg_client):
    """
    Verifica que crear producto requiere rol admin.

    CRÍTICO: Validación de permisos en endpoints de gestión.
    """
    mock_rawg_client.get_game_details.return_value = GameDetail(
        id=3498,
        slug="gta-v",
        name="GTA V",
        description="Test",
        description_raw="Test",
        background_image="https://example.com/img.jpg",
        released="2013-09-17",
        rating=4.8,
        platforms=[],
        genres=[],
    )

    # ACT: Usuario normal intenta crear producto
    response = await client.post(
        "/api/products",
        headers=auth_headers,
        json={"rawg_id": 3498, "price": 59.99, "stock": 10},
    )

    # ASSERT
    assert response.status_code == 403


@pytest.mark.asyncio
async def test_list_products_is_public(client, sample_game):
    """
    Verifica que listar productos NO requiere autenticación.

    CRÍTICO: Endpoint público para frontend.
    """
    # ACT: Request sin headers de auth
    response = await client.get("/api/products")

    # ASSERT
    assert response.status_code == 200
    data = response.json()
    assert data["total"] >= 1


@pytest.mark.asyncio
async def test_get_product_details_is_public(client, sample_game):
    """
    Verifica que detalles de producto son públicos.
    """
    # ACT
    response = await client.get(f"/api/products/{sample_game['id']}")

    # ASSERT
    assert response.status_code == 200
    data = response.json()
    assert data["id"] == sample_game["id"]


@pytest.mark.asyncio
async def test_update_product_requires_admin(client, auth_headers, sample_game):
    """
    Verifica que actualizar producto requiere rol admin.
    """
    # ACT
    response = await client.put(
        f"/api/products/{sample_game['id']}",
        headers=auth_headers,
        json={"price": 49.99, "stock": 20},
    )

    # ASSERT
    assert response.status_code == 403


@pytest.mark.asyncio
async def test_delete_product_requires_admin(client, auth_headers, sample_game):
    """
    Verifica que eliminar producto requiere rol admin.
    """
    # ACT
    response = await client.delete(
        f"/api/products/{sample_game['id']}", headers=auth_headers
    )

    # ASSERT
    assert response.status_code == 403


@pytest.mark.asyncio
async def test_create_product_validates_duplicate_rawg_id(
    client, admin_headers, mock_rawg_client
):
    """
    Verifica que no se puede crear producto duplicado.
    """
    # ARRANGE: Configurar mock
    mock_rawg_client.get_game_details.return_value = GameDetail(
        id=3498,
        slug="gta-v",
        name="GTA V",
        description="Test",
        description_raw="Test",
        background_image="https://example.com/img.jpg",
        released="2013-09-17",
        rating=4.8,
        platforms=[],
        genres=[],
    )

    # ACT: Crear dos veces el mismo producto
    await client.post(
        "/api/products",
        headers=admin_headers,
        json={"rawg_id": 3498, "price": 59.99, "stock": 10},
    )

    response = await client.post(
        "/api/products",
        headers=admin_headers,
        json={"rawg_id": 3498, "price": 39.99, "stock": 5},
    )

    # ASSERT
    assert response.status_code == 400
    assert "ya existe" in response.json()["detail"]
