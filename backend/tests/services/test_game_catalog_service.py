import pytest
from app.schemas.game_catalog import GameCatalogCreate, GameCatalogUpdate
from app.schemas.rawg import GameDetail


@pytest.mark.asyncio
async def test_create_product_validates_duplicate_rawg_id(game_catalog_service):
    """
    Verifica que no se puede crear producto con rawg_id duplicado.
    """
    # ARRANGE
    data = GameCatalogCreate(rawg_id=3498, price=59.99, stock=10)

    # ACT: Crear producto
    await game_catalog_service.create_product(data)

    # ASSERT: Intentar crear duplicado debe fallar
    with pytest.raises(ValueError, match="ya existe"):
        await game_catalog_service.create_product(data)


@pytest.mark.asyncio
async def test_create_product_fetches_metadata_from_rawg(
    game_catalog_service, mock_rawg_client
):
    """
    Verifica que crear producto consulta metadata de RAWG API.

    CRÍTICO: Demuestra integración con API externa (mockeada).
    """
    # ARRANGE
    mock_rawg_client.get_game_details.return_value = GameDetail(
        id=3498,
        slug="gta-v",
        name="Grand Theft Auto V",
        description="An action game...",
        description_raw="An action game...",
        background_image="https://example.com/gta.jpg",
        released="2013-09-17",
        rating=4.9,
        platforms=[],
        genres=[],
    )

    data = GameCatalogCreate(rawg_id=3498, price=59.99, stock=10)

    # ACT
    product = await game_catalog_service.create_product(data)

    # ASSERT: Metadata viene de RAWG
    assert product.title == "Grand Theft Auto V"
    assert product.slug == "gta-v"
    assert product.image_url == "https://example.com/gta.jpg"

    # ASSERT: Mock fue llamado correctamente
    mock_rawg_client.get_game_details.assert_called_once_with(3498)


@pytest.mark.asyncio
async def test_update_product_price_and_stock(game_catalog_service, game_repo):
    """
    Verifica actualización de precio y stock.
    """
    # ARRANGE: Crear producto
    product = await game_repo.create(
        GameCatalogCreate(rawg_id=3498, price=59.99, stock=10),
        {"title": "GTA V", "slug": "gta-v"},
    )

    # ACT: Actualizar precio y stock
    update_data = GameCatalogUpdate(price=49.99, stock=20)
    updated = await game_catalog_service.update_product(product.id, update_data)

    # ASSERT
    assert updated.price == 49.99
    assert updated.stock == 20


@pytest.mark.asyncio
async def test_delete_product(game_catalog_service, game_repo):
    """
    Verifica eliminación de producto.
    """
    # ARRANGE
    product = await game_repo.create(
        GameCatalogCreate(rawg_id=3498, price=59.99, stock=10),
        {"title": "GTA V", "slug": "gta-v"},
    )

    # ACT
    result = await game_catalog_service.delete_product(product.id)

    # ASSERT
    assert result is True
    assert await game_repo.get_by_id(product.id) is None


@pytest.mark.asyncio
async def test_list_products_with_stock_filter(game_catalog_service, game_repo):
    """
    Verifica filtro de productos en stock.
    """
    # ARRANGE: Crear productos con y sin stock
    await game_repo.create(
        GameCatalogCreate(rawg_id=3498, price=59.99, stock=10),
        {"title": "GTA V", "slug": "gta-v"},
    )
    await game_repo.create(
        GameCatalogCreate(rawg_id=3499, price=39.99, stock=0),
        {"title": "Out of Stock", "slug": "oos"},
    )

    # ACT: Listar solo con stock
    result = await game_catalog_service.list_products(in_stock_only=True)

    # ASSERT: Solo debe devolver 1 producto
    assert result["total"] == 1
    assert result["results"][0].title == "GTA V"
