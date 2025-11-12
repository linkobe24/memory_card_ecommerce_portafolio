import pytest


@pytest.mark.asyncio
async def test_create_review_requires_auth(client, sample_game):
    """
    Verifica que crear reseña requiere autenticación.
    """
    # ACT
    response = await client.post(
        "/api/reviews",
        json={"game_id": sample_game["id"], "rating": 5, "comment": "Great"},
    )

    # ASSERT
    assert response.status_code == 401


@pytest.mark.asyncio
async def test_create_review_success(client, auth_headers, sample_game):
    """
    Test de integración: POST /api/reviews/.
    """
    # ACT
    response = await client.post(
        "/api/reviews",
        headers=auth_headers,
        json={"game_id": sample_game["id"], "rating": 5, "comment": "Excelente"},
    )

    # ASSERT
    assert response.status_code == 201
    data = response.json()
    assert data["rating"] == 5
    assert data["comment"] == "Excelente"


@pytest.mark.asyncio
async def test_list_reviews_is_public(client, auth_headers, sample_game):
    """
    Verifica que listar reseñas NO requiere autenticación.
    """
    # ARRANGE: Crear reseña
    await client.post(
        "/api/reviews",
        headers=auth_headers,
        json={"game_id": sample_game["id"], "rating": 5, "comment": "Test"},
    )

    # ACT: Listar sin auth
    response = await client.get(f"/api/reviews/game/{sample_game['id']}")

    # ASSERT
    assert response.status_code == 200
    data = response.json()
    assert data["total"] == 1
    assert "average_rating" in data


@pytest.mark.asyncio
async def test_update_review_validates_ownership(
    client, auth_headers, admin_headers, sample_game
):
    """
    Verifica que solo el autor puede actualizar su reseña.
    """
    # ARRANGE: Usuario 1 crea reseña
    create_response = await client.post(
        "/api/reviews",
        headers=auth_headers,
        json={"game_id": sample_game["id"], "rating": 5, "comment": "Great"},
    )
    review_id = create_response.json()["id"]

    # ACT: Usuario diferente (admin) intenta actualizar
    response = await client.put(
        f"/api/reviews/{review_id}",
        headers=admin_headers,
        json={"rating": 1, "comment": "Terrible"},
    )

    # ASSERT
    assert response.status_code == 403


@pytest.mark.asyncio
async def test_delete_review_validates_ownership(
    client, auth_headers, admin_headers, sample_game
):
    """
    Verifica que solo el autor puede eliminar su reseña.
    """
    # ARRANGE
    create_response = await client.post(
        "/api/reviews",
        headers=auth_headers,
        json={"game_id": sample_game["id"], "rating": 5, "comment": "Test"},
    )
    review_id = create_response.json()["id"]

    # ACT
    response = await client.delete(f"/api/reviews/{review_id}", headers=admin_headers)

    # ASSERT
    assert response.status_code == 403
