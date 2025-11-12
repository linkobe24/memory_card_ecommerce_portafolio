import pytest
from app.models.order import OrderStatus


@pytest.mark.asyncio
async def test_create_order_validates_empty_cart(order_service):
    """
    Verifica que no se puede crear orden con carrito vacío.

    CRÍTICO: Validación de precondiciones.
    """
    # ACT & ASSERT: Intentar crear orden sin items en carrito
    with pytest.raises(ValueError, match="carrito está vacío"):
        await order_service.create_order_from_cart(user_id=1)


@pytest.mark.asyncio
async def test_create_order_validates_stock(order_service, cart_service, game_repo):
    """
    Verifica que no se puede crear orden si algún item no tiene stock.

    CRÍTICO: Previene overselling.
    """
    # ARRANGE: Producto con stock limitado
    from app.schemas.game_catalog import GameCatalogCreate
    from app.schemas.cart import CartItemCreate

    game_data = GameCatalogCreate(rawg_id=3498, price=59.99, stock=2)
    metadata = {"title": "GTA V", "slug": "gta-v"}
    game = await game_repo.create(game_data, metadata)

    # Agregar al carrito (quantity dentro del stock)
    await cart_service.add_to_cart(
        user_id=1, data=CartItemCreate(game_id=game.id, quantity=2)
    )

    # Reducir stock manualmente (simula compra concurrente)
    await game_repo.reduce_stock(game.id, 1)

    # ACT & ASSERT: Intentar crear orden con stock insuficiente
    with pytest.raises(ValueError, match="Stock insuficiente"):
        await order_service.create_order_from_cart(user_id=1)


@pytest.mark.asyncio
async def test_create_order_reduces_stock(order_service, cart_service, game_repo):
    """
    Verifica que crear orden reduce el stock de productos.

    CRÍTICO: Test más importante - valida flujo completo.
    """
    # ARRANGE: Crear producto con stock
    from app.schemas.game_catalog import GameCatalogCreate
    from app.schemas.cart import CartItemCreate

    game_data = GameCatalogCreate(rawg_id=3498, price=59.99, stock=10)
    metadata = {"title": "GTA V", "slug": "gta-v"}
    game = await game_repo.create(game_data, metadata)

    # Agregar al carrito
    await cart_service.add_to_cart(
        user_id=1, data=CartItemCreate(game_id=game.id, quantity=3)
    )

    # ACT: Crear orden
    order_response = await order_service.create_order_from_cart(user_id=1)

    # ASSERT: Stock debe haber disminuido
    updated_game = await game_repo.get_by_id(game.id)
    assert updated_game.stock == 7  # 10 - 3

    # ASSERT: Orden creada correctamente
    assert order_response.status == OrderStatus.PENDING
    assert len(order_response.items) == 1
    assert order_response.subtotal == 179.97  # 59.99 * 3


@pytest.mark.asyncio
async def test_create_order_clears_cart(order_service, cart_service, game_repo):
    """
    Verifica que crear orden vacía el carrito del usuario.

    CRÍTICO: Previene doble compra del mismo carrito.
    """
    # ARRANGE
    from app.schemas.game_catalog import GameCatalogCreate
    from app.schemas.cart import CartItemCreate

    game_data = GameCatalogCreate(rawg_id=3498, price=59.99, stock=10)
    metadata = {"title": "GTA V", "slug": "gta-v"}
    game = await game_repo.create(game_data, metadata)

    await cart_service.add_to_cart(
        user_id=1, data=CartItemCreate(game_id=game.id, quantity=2)
    )

    # ACT: Crear orden
    await order_service.create_order_from_cart(user_id=1)

    # ASSERT: Carrito debe estar vacío
    cart_response = await cart_service.get_cart(user_id=1)
    assert len(cart_response.items) == 0


@pytest.mark.asyncio
async def test_create_order_atomic_transaction(order_service, cart_service, game_repo):
    """
    Verifica que si falla reducir stock, la orden no se crea.

    CRÍTICO: Demuestra atomicidad de transacciones.

    En producción, esto funcionaría con rollback de DB.
    En tests con fakes, simulamos el comportamiento.
    """
    # ARRANGE: Dos productos, uno sin stock suficiente
    from app.schemas.game_catalog import GameCatalogCreate
    from app.schemas.cart import CartItemCreate

    game1 = await game_repo.create(
        GameCatalogCreate(rawg_id=3498, price=59.99, stock=10),
        {"title": "GTA V", "slug": "gta-v"},
    )
    game2 = await game_repo.create(
        GameCatalogCreate(rawg_id=3499, price=39.99, stock=5),
        {"title": "Witcher 3", "slug": "witcher-3"},
    )

    await cart_service.add_to_cart(
        user_id=1, data=CartItemCreate(game_id=game1.id, quantity=2)
    )
    await cart_service.add_to_cart(
        user_id=1, data=CartItemCreate(game_id=game2.id, quantity=5)
    )

    # Simula compra concurrente que deja stock insuficiente antes del checkout.
    await game_repo.reduce_stock(game2.id, 4)

    # ACT & ASSERT: Debe fallar por stock insuficiente
    with pytest.raises(ValueError, match="Stock insuficiente"):
        await order_service.create_order_from_cart(user_id=1)

    # ASSERT: Stock no debe haber cambiado (rollback simulado)
    game1_updated = await game_repo.get_by_id(game1.id)
    game2_updated = await game_repo.get_by_id(game2.id)
    assert game1_updated.stock == 10  # No se redujo
    assert game2_updated.stock == 1  # Se mantiene el stock previo al fallo


@pytest.mark.asyncio
async def test_get_order_validates_ownership(order_service, cart_service, game_repo):
    """
    Verifica que un usuario solo puede ver sus propias órdenes.

    CRÍTICO: Validación de autorización.
    """
    # ARRANGE: Usuario 1 crea orden
    from app.schemas.game_catalog import GameCatalogCreate
    from app.schemas.cart import CartItemCreate

    game = await game_repo.create(
        GameCatalogCreate(rawg_id=3498, price=59.99, stock=10),
        {"title": "GTA V", "slug": "gta-v"},
    )

    await cart_service.add_to_cart(
        user_id=1, data=CartItemCreate(game_id=game.id, quantity=1)
    )
    order_response = await order_service.create_order_from_cart(user_id=1)

    # ACT: Usuario 2 intenta ver orden de usuario 1
    result = await order_service.get_order(order_id=order_response.id, user_id=2)

    # ASSERT: Debe devolver None (acceso denegado)
    assert result is None


@pytest.mark.asyncio
async def test_list_user_orders_pagination(order_service, cart_service, game_repo):
    """
    Verifica paginación de órdenes de un usuario.
    """
    # ARRANGE: Crear 3 órdenes para usuario 1
    from app.schemas.game_catalog import GameCatalogCreate
    from app.schemas.cart import CartItemCreate

    game = await game_repo.create(
        GameCatalogCreate(rawg_id=3498, price=59.99, stock=50),
        {"title": "GTA V", "slug": "gta-v"},
    )

    for _ in range(3):
        await cart_service.add_to_cart(
            user_id=1, data=CartItemCreate(game_id=game.id, quantity=1)
        )
        await order_service.create_order_from_cart(user_id=1)

    # ACT: Paginar con page_size=2
    result = await order_service.list_user_orders(user_id=1, page=1, page_size=2)

    # ASSERT
    assert result["total"] == 3
    assert len(result["results"]) == 2
    assert result["page"] == 1


@pytest.mark.asyncio
async def test_update_order_status_admin(order_service, cart_service, game_repo):
    """
    Verifica actualización de estado de orden (admin).
    """
    # ARRANGE: Crear orden
    from app.schemas.game_catalog import GameCatalogCreate
    from app.schemas.cart import CartItemCreate
    from app.schemas.order import OrderStatusUpdate

    game = await game_repo.create(
        GameCatalogCreate(rawg_id=3498, price=59.99, stock=10),
        {"title": "GTA V", "slug": "gta-v"},
    )

    await cart_service.add_to_cart(
        user_id=1, data=CartItemCreate(game_id=game.id, quantity=1)
    )
    order_response = await order_service.create_order_from_cart(user_id=1)

    # ACT: Admin actualiza a COMPLETED
    updated_order = await order_service.update_order_status(
        order_id=order_response.id,
        data=OrderStatusUpdate(status=OrderStatus.COMPLETED),
    )

    # ASSERT
    assert updated_order.status == OrderStatus.COMPLETED
    assert updated_order.completed_at is not None
