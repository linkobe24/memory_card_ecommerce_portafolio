import pytest


@pytest.mark.asyncio
async def test_create_order_endpoint(client, auth_headers, sample_game):
    """
    Test de integración: POST /api/orders/.

    CRÍTICO: Valida flujo completo de checkout.
    """
    # ARRANGE: Agregar item al carrito
    await client.post(
        "/api/cart/items",
        headers=auth_headers,
        json={"game_id": sample_game["id"], "quantity": 2},
    )

    # ACT: Crear orden
    response = await client.post("/api/orders", headers=auth_headers)

    # ASSERT
    assert response.status_code == 201
    data = response.json()
    assert data["status"] == "pending"
    assert len(data["items"]) == 1
    assert data["subtotal"] == 119.98


@pytest.mark.asyncio
async def test_list_my_orders_endpoint(client, auth_headers, sample_game):
    """
    Test de integración: GET /api/orders/.
    """
    # ARRANGE: Crear orden
    await client.post(
        "/api/cart/items",
        headers=auth_headers,
        json={"game_id": sample_game["id"], "quantity": 1},
    )
    await client.post("/api/orders", headers=auth_headers)

    # ACT: Listar mis órdenes
    response = await client.get("/api/orders", headers=auth_headers)

    # ASSERT
    assert response.status_code == 200
    data = response.json()
    assert data["total"] == 1
    assert len(data["results"]) == 1


@pytest.mark.asyncio
async def test_get_order_details_validates_ownership(
    client, auth_headers, admin_headers, sample_game
):
    """
    Verifica que un usuario solo puede ver sus propias órdenes.

    CRÍTICO: Validación de autorización en route layer.
    """
    # ARRANGE: Usuario 1 crea orden
    await client.post(
        "/api/cart/items",
        headers=auth_headers,
        json={"game_id": sample_game["id"], "quantity": 1},
    )
    order_response = await client.post("/api/orders", headers=auth_headers)
    order_id = order_response.json()["id"]

    # ACT: Usuario diferente (admin) intenta ver la orden
    response = await client.get(f"/api/orders/{order_id}", headers=admin_headers)

    # ASSERT
    assert response.status_code == 404  # Not found (oculta existencia)


@pytest.mark.asyncio
async def test_list_all_orders_requires_admin(client, auth_headers):
    """
    Verifica que listar todas las órdenes requiere rol admin.

    CRÍTICO: Validación de RBAC (Role-Based Access Control).
    """
    # ACT: Usuario normal intenta acceder a endpoint admin
    response = await client.get("/api/orders/admin/all", headers=auth_headers)

    # ASSERT
    assert response.status_code == 403


@pytest.mark.asyncio
async def test_update_order_status_requires_admin(client, auth_headers, sample_game):
    """
    Verifica que actualizar estado de orden requiere rol admin.
    """
    # ARRANGE: Crear orden
    await client.post(
        "/api/cart/items",
        headers=auth_headers,
        json={"game_id": sample_game["id"], "quantity": 1},
    )
    order_response = await client.post("/api/orders", headers=auth_headers)
    order_id = order_response.json()["id"]

    # ACT: Usuario normal intenta actualizar estado
    response = await client.put(
        f"/api/orders/{order_id}/status",
        headers=auth_headers,
        json={"status": "completed"},
    )

    # ASSERT
    assert response.status_code == 403


@pytest.mark.asyncio
async def test_create_order_validates_empty_cart(client, auth_headers):
    """
    Verifica que no se puede crear orden con carrito vacío.
    """
    # ACT: Intentar crear orden sin items
    response = await client.post("/api/orders", headers=auth_headers)

    # ASSERT
    assert response.status_code == 400
    assert "vacío" in response.json()["detail"]
