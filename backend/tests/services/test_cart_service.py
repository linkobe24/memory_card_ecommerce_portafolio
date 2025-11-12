import pytest
from app.schemas.cart import CartItemCreate, CartItemUpdate


@pytest.mark.asyncio
async def test_add_to_cart_creates_cart_if_not_exists(cart_service, game_repo):
    """
    Verifica que agregar un item crea el carrito automáticamente.
    """
    # ARRANGE: Crear producto en catálogo
    from app.schemas.game_catalog import GameCatalogCreate

    game_data = GameCatalogCreate(rawg_id=3498, price=59.99, stock=10)
    metadata = {
        "title": "GTA V",
        "slug": "gta-v",
        "description": "Action game",
        "image_url": "https://example.com/gta.jpg",
    }
    game = await game_repo.create(game_data, metadata)

    # ACT: Agregar item al carrito de usuario nuevo (user_id=1)
    cart_response = await cart_service.add_to_cart(
        user_id=1, data=CartItemCreate(game_id=game.id, quantity=2)
    )

    # ASSERT
    assert cart_response.user_id == 1
    assert len(cart_response.items) == 1
    assert cart_response.items[0].game_id == game.id
    assert cart_response.items[0].quantity == 2
    assert cart_response.total == 119.98  # 59.99 * 2


@pytest.mark.asyncio
async def test_add_to_cart_increments_quantity_if_exists(cart_service, game_repo):
    """
    Verifica que agregar el mismo juego incrementa la cantidad.
    """
    # ARRANGE
    from app.schemas.game_catalog import GameCatalogCreate

    game_data = GameCatalogCreate(rawg_id=3498, price=59.99, stock=10)
    metadata = {"title": "GTA V", "slug": "gta-v"}
    game = await game_repo.create(game_data, metadata)

    # ACT: Agregar dos veces el mismo juego
    await cart_service.add_to_cart(
        user_id=1, data=CartItemCreate(game_id=game.id, quantity=2)
    )
    cart_response = await cart_service.add_to_cart(
        user_id=1, data=CartItemCreate(game_id=game.id, quantity=3)
    )

    # ASSERT: Debe tener 1 item con quantity=5
    assert len(cart_response.items) == 1
    assert cart_response.items[0].quantity == 5
    assert cart_response.total == 299.95  # 59.99 * 5


@pytest.mark.asyncio
async def test_add_to_cart_validates_stock(cart_service, game_repo):
    """
    Verifica que no se puede agregar más items que el stock disponible.

    CRÍTICO: Demuestra validación de reglas de negocio.
    """
    # ARRANGE: Producto con stock limitado
    from app.schemas.game_catalog import GameCatalogCreate

    game_data = GameCatalogCreate(rawg_id=3498, price=59.99, stock=3)
    metadata = {"title": "GTA V", "slug": "gta-v"}
    game = await game_repo.create(game_data, metadata)

    # ACT & ASSERT: Intentar agregar más que el stock
    with pytest.raises(ValueError, match="Stock insuficiente"):
        await cart_service.add_to_cart(
            user_id=1, data=CartItemCreate(game_id=game.id, quantity=5)
        )


@pytest.mark.asyncio
async def test_update_item_validates_stock(cart_service, game_repo):
    """
    Verifica que actualizar cantidad valida stock disponible.
    """
    # ARRANGE
    from app.schemas.game_catalog import GameCatalogCreate

    game_data = GameCatalogCreate(rawg_id=3498, price=59.99, stock=5)
    metadata = {"title": "GTA V", "slug": "gta-v"}
    game = await game_repo.create(game_data, metadata)

    cart_response = await cart_service.add_to_cart(
        user_id=1, data=CartItemCreate(game_id=game.id, quantity=2)
    )
    item_id = cart_response.items[0].id

    # ACT & ASSERT: Intentar actualizar a cantidad mayor que stock
    with pytest.raises(ValueError, match="Stock insuficiente"):
        await cart_service.update_item(
            item_id=item_id, data=CartItemUpdate(quantity=10), user_id=1
        )


@pytest.mark.asyncio
async def test_update_item_success(cart_service, game_repo):
    """
    Verifica que actualizar cantidad funciona correctamente.
    """
    # ARRANGE
    from app.schemas.game_catalog import GameCatalogCreate

    game_data = GameCatalogCreate(rawg_id=3498, price=59.99, stock=10)
    metadata = {"title": "GTA V", "slug": "gta-v"}
    game = await game_repo.create(game_data, metadata)

    cart_response = await cart_service.add_to_cart(
        user_id=1, data=CartItemCreate(game_id=game.id, quantity=2)
    )
    item_id = cart_response.items[0].id

    # ACT: Actualizar a quantity=5
    updated_cart = await cart_service.update_item(
        item_id=item_id, data=CartItemUpdate(quantity=5), user_id=1
    )

    # ASSERT
    assert updated_cart.items[0].quantity == 5
    assert updated_cart.total == 299.95


@pytest.mark.asyncio
async def test_remove_item_validates_ownership(cart_service, game_repo):
    """
    Verifica que solo el dueño puede eliminar items de su carrito.

    CRÍTICO: Demuestra validación de autorización en service layer.
    """
    # ARRANGE: Usuario 1 agrega item
    from app.schemas.game_catalog import GameCatalogCreate

    game_data = GameCatalogCreate(rawg_id=3498, price=59.99, stock=10)
    metadata = {"title": "GTA V", "slug": "gta-v"}
    game = await game_repo.create(game_data, metadata)

    cart_response = await cart_service.add_to_cart(
        user_id=1, data=CartItemCreate(game_id=game.id, quantity=2)
    )
    item_id = cart_response.items[0].id

    # ACT & ASSERT: Usuario 2 intenta eliminar item de usuario 1
    with pytest.raises(ValueError, match="no pertenece al usuario"):
        await cart_service.remove_item(item_id=item_id, user_id=2)


@pytest.mark.asyncio
async def test_clear_cart_success(cart_service, game_repo):
    """
    Verifica que vaciar carrito elimina todos los items.
    """
    # ARRANGE: Agregar 2 productos
    from app.schemas.game_catalog import GameCatalogCreate

    game1 = await game_repo.create(
        GameCatalogCreate(rawg_id=3498, price=59.99, stock=10),
        {"title": "GTA V", "slug": "gta-v"},
    )
    game2 = await game_repo.create(
        GameCatalogCreate(rawg_id=3499, price=39.99, stock=5),
        {"title": "Witcher 3", "slug": "witcher-3"},
    )

    await cart_service.add_to_cart(
        user_id=1, data=CartItemCreate(game_id=game1.id, quantity=1)
    )
    await cart_service.add_to_cart(
        user_id=1, data=CartItemCreate(game_id=game2.id, quantity=1)
    )

    # ACT: Vaciar carrito
    await cart_service.clear_cart(user_id=1)

    # ASSERT: Carrito debe estar vacío
    cart_response = await cart_service.get_cart(user_id=1)
    assert len(cart_response.items) == 0
    assert cart_response.total == 0.0
