"""
Interfaz para repositorio de Review.

Define operaciones para gestión de reseñas.
"""

from abc import ABC, abstractmethod
from app.models.review import Review
from app.schemas.review import ReviewCreate, ReviewUpdate


class ReviewRepositoryInterface(ABC):
    """Contrato para operaciones de reseñas."""

    @abstractmethod
    async def create(self, user_id: int, data: ReviewCreate) -> Review:
        """Crea reseña."""
        pass

    @abstractmethod
    async def get_by_id(self, review_id: int) -> Review | None:
        """Obtiene reseña por ID (con user eager loaded)."""
        pass

    @abstractmethod
    async def get_user_review_for_game(
        self, user_id: int, game_id: int
    ) -> Review | None:
        """
        Obtiene reseña de un usuario para un juego específico.

        Usado para validar duplicados.
        """
        pass

    @abstractmethod
    async def list_by_game(
        self, game_id: int, skip: int = 0, limit: int = 20
    ) -> tuple[list[Review], int, float]:
        """
        Lista reseñas de un juego.

        Returns:
            Tupla (reseñas, total_count, average_rating)
        """
        pass

    @abstractmethod
    async def update(self, review_id: int, data: ReviewUpdate) -> Review | None:
        """Actualiza reseña."""
        pass

    @abstractmethod
    async def delete(self, review_id: int, user_id: int) -> bool:
        """
        Elimina reseña (valida ownership).

        Returns:
            True si se eliminó, False si no existía o no pertenece al usuario
        """
        pass
