import pytest
from app.schemas.review import ReviewCreate, ReviewUpdate


@pytest.mark.asyncio
async def test_create_review_validates_duplicate(review_service, game_repo):
    """
    Verifica que un usuario no puede crear múltiples reseñas del mismo juego.
    """
    # ARRANGE: Crear juego
    from app.schemas.game_catalog import GameCatalogCreate

    game = await game_repo.create(
        GameCatalogCreate(rawg_id=3498, price=59.99, stock=10),
        {"title": "GTA V", "slug": "gta-v"},
    )

    # ACT: Crear primera reseña
    data = ReviewCreate(game_id=game.id, rating=5, comment="Excelente juego")
    await review_service.create_review(user_id=1, data=data)

    # ASSERT: Intentar crear segunda reseña debe fallar
    with pytest.raises(ValueError, match="Ya has reseñado"):
        await review_service.create_review(user_id=1, data=data)


@pytest.mark.asyncio
async def test_create_review_validates_game_exists(review_service):
    """
    Verifica que no se puede reseñar un juego inexistente.
    """
    # ACT & ASSERT
    data = ReviewCreate(game_id=999, rating=5, comment="Test")

    with pytest.raises(ValueError, match="no encontrado"):
        await review_service.create_review(user_id=1, data=data)


@pytest.mark.asyncio
async def test_list_reviews_calculates_average(review_service, game_repo, review_repo):
    """
    Verifica cálculo de rating promedio.
    """
    # ARRANGE: Crear juego
    from app.schemas.game_catalog import GameCatalogCreate

    game = await game_repo.create(
        GameCatalogCreate(rawg_id=3498, price=59.99, stock=10),
        {"title": "GTA V", "slug": "gta-v"},
    )

    # Crear 3 reseñas con ratings diferentes
    await review_repo.create(
        user_id=1, data=ReviewCreate(game_id=game.id, rating=5, comment="Great")
    )
    await review_repo.create(
        user_id=2, data=ReviewCreate(game_id=game.id, rating=4, comment="Good")
    )
    await review_repo.create(
        user_id=3, data=ReviewCreate(game_id=game.id, rating=3, comment="OK")
    )

    # ACT
    result = await review_service.list_reviews_by_game(game.id)

    # ASSERT: Average = (5+4+3)/3 = 4.0
    assert result["total"] == 3
    assert result["average_rating"] == 4.0


@pytest.mark.asyncio
async def test_update_review_validates_ownership(
    review_service, game_repo, review_repo
):
    """
    Verifica que solo el autor puede actualizar su reseña.
    """
    # ARRANGE: Usuario 1 crea reseña
    from app.schemas.game_catalog import GameCatalogCreate

    game = await game_repo.create(
        GameCatalogCreate(rawg_id=3498, price=59.99, stock=10),
        {"title": "GTA V", "slug": "gta-v"},
    )

    review = await review_repo.create(
        user_id=1,
        data=ReviewCreate(game_id=game.id, rating=5, comment="Great"),
    )

    # ACT & ASSERT: Usuario 2 intenta actualizar
    update_data = ReviewUpdate(rating=1, comment="Terrible")

    with pytest.raises(ValueError, match="no pertenece"):
        await review_service.update_review(
            review_id=review.id, data=update_data, user_id=2
        )


@pytest.mark.asyncio
async def test_delete_review_validates_ownership(
    review_service, game_repo, review_repo
):
    """
    Verifica que solo el autor puede eliminar su reseña.
    """
    # ARRANGE
    from app.schemas.game_catalog import GameCatalogCreate

    game = await game_repo.create(
        GameCatalogCreate(rawg_id=3498, price=59.99, stock=10),
        {"title": "GTA V", "slug": "gta-v"},
    )

    review = await review_repo.create(
        user_id=1,
        data=ReviewCreate(game_id=game.id, rating=5, comment="Great"),
    )

    # ACT & ASSERT
    result = await review_service.delete_review(review_id=review.id, user_id=2)
    assert result is False

    # Usuario correcto puede eliminar
    result = await review_service.delete_review(review_id=review.id, user_id=1)
    assert result is True
