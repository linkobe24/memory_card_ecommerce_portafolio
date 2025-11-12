"""
Modelos de base de datos.

Importa todos los modelos para que Alembic los detecte automáticamente.
"""

from app.models.user import User, UserRole
from app.models.game_catalog import GameCatalog
from app.models.cart import Cart, CartItem
from app.models.order import Order, OrderItem, OrderStatus
from app.models.review import Review

__all__ = [
    "User",
    "UserRole",
    "GameCatalog",
    "Cart",
    "CartItem",
    "Order",
    "OrderItem",
    "OrderStatus",
    "Review",
]
