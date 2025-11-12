import pytest


@pytest.mark.asyncio
async def test_add_to_cart_endpoint(client, auth_headers, sample_game):
    """
    Test de integración: POST /api/cart/items.
    """
    # ACT
    response = await client.post(
        "/api/cart/items",
        headers=auth_headers,
        json={"game_id": sample_game["id"], "quantity": 2},
    )

    # ASSERT
    assert response.status_code == 201
    data = response.json()
    assert len(data["items"]) == 1
    assert data["items"][0]["quantity"] == 2
    assert data["total"] == 119.98


@pytest.mark.asyncio
async def test_get_cart_endpoint(client, auth_headers, sample_game):
    """
    Test de integración: GET /api/cart/.
    """
    # ARRANGE: Agregar item primero
    await client.post(
        "/api/cart/items",
        headers=auth_headers,
        json={"game_id": sample_game["id"], "quantity": 1},
    )

    # ACT: Obtener carrito
    response = await client.get("/api/cart", headers=auth_headers)

    # ASSERT
    assert response.status_code == 200
    data = response.json()
    assert len(data["items"]) == 1


@pytest.mark.asyncio
async def test_update_cart_item_endpoint(client, auth_headers, sample_game):
    """
    Test de integración: PUT /api/cart/items/{item_id}.
    """
    # ARRANGE: Agregar item
    add_response = await client.post(
        "/api/cart/items",
        headers=auth_headers,
        json={"game_id": sample_game["id"], "quantity": 1},
    )
    item_id = add_response.json()["items"][0]["id"]

    # ACT: Actualizar cantidad
    response = await client.put(
        f"/api/cart/items/{item_id}",
        headers=auth_headers,
        json={"quantity": 5},
    )

    # ASSERT
    assert response.status_code == 200
    data = response.json()
    assert data["items"][0]["quantity"] == 5


@pytest.mark.asyncio
async def test_remove_cart_item_endpoint(client, auth_headers, sample_game):
    """
    Test de integración: DELETE /api/cart/items/{item_id}.
    """
    # ARRANGE
    add_response = await client.post(
        "/api/cart/items",
        headers=auth_headers,
        json={"game_id": sample_game["id"], "quantity": 1},
    )
    item_id = add_response.json()["items"][0]["id"]

    # ACT
    response = await client.delete(f"/api/cart/items/{item_id}", headers=auth_headers)

    # ASSERT
    assert response.status_code == 204


@pytest.mark.asyncio
async def test_cart_endpoints_require_auth(client, sample_game):
    """
    Verifica que endpoints de carrito requieren autenticación.

    CRÍTICO: Valida middleware de auth.
    """
    # ACT: Intentar agregar sin token
    response = await client.post(
        "/api/cart/items",
        json={"game_id": sample_game["id"], "quantity": 1},
    )

    # ASSERT
    assert response.status_code == 401


@pytest.mark.asyncio
async def test_add_to_cart_validates_stock(client, auth_headers, sample_game):
    """
    Verifica que endpoint valida stock disponible.

    CRÍTICO: Integración entre route → service → repository.
    """
    # ACT: Intentar agregar más que el stock (sample_game tiene stock=10)
    response = await client.post(
        "/api/cart/items",
        headers=auth_headers,
        json={"game_id": sample_game["id"], "quantity": 15},
    )

    # ASSERT
    assert response.status_code == 400
    assert "Stock insuficiente" in response.json()["detail"]
