"""
Servicio de reseñas.

Lógica de negocio:
- Validar que juego existe
- Evitar reseñas duplicadas (1 reseña por usuario por juego)
- Enriquecer reseñas con metadata del usuario
"""

from app.crud.review_interface import ReviewRepositoryInterface
from app.crud.game_catalog_interface import GameCatalogRepositoryInterface
from app.schemas.review import (
    ReviewCreate,
    ReviewUpdate,
    ReviewResponse,
    ReviewListResponse,
)


class ReviewService:
    """Servicio de reseñas con lógica de negocio."""

    def __init__(
        self,
        review_repo: ReviewRepositoryInterface,
        game_repo: GameCatalogRepositoryInterface,
    ):
        self.review_repo = review_repo
        self.game_repo = game_repo

    async def create_review(self, user_id: int, data: ReviewCreate) -> ReviewResponse:
        """
        Crea reseña.

        Validaciones:
        - Juego existe en catálogo
        - Usuario no tiene reseña previa para este juego

        Raises:
            ValueError si validaciones fallan
        """

        game = await self.game_repo.get_by_id(data.game_id)
        if not game:
            raise ValueError(f"Juego con ID {data.game_id} no encontrado")

        existing_review = await self.review_repo.get_user_review_for_game(
            user_id, data.game_id
        )
        if existing_review:
            raise ValueError(
                f"Ya has reseñado {game.title}. "
                "Puedes editarla o eliminarla, pero no crear otra."
            )

        review = await self.review_repo.create(user_id, data)

        return ReviewResponse(
            id=review.id,
            game_id=review.game_id,
            user_id=review.user_id,
            user_name=review.user.full_name,
            rating=review.rating,
            comment=review.comment,
            created_at=review.created_at,
            updated_at=review.updated_at,
        )

    async def list_game_reviews(
        self, game_id: int, page: int = 1, page_size: int = 20
    ) -> ReviewListResponse:
        """Lista reseñas de un juego con promedio."""
        skip = (page - 1) * page_size
        reviews, total, average_rating = await self.review_repo.list_by_game(
            game_id, skip, page_size
        )

        results = [
            ReviewResponse(
                id=r.id,
                game_id=r.game_id,
                user_id=r.user_id,
                user_name=r.user.full_name,
                rating=r.rating,
                comment=r.comment,
                created_at=r.created_at,
                updated_at=r.updated_at,
            )
            for r in reviews
        ]

        return ReviewListResponse(
            total=total,
            page=page,
            page_size=page_size,
            average_rating=average_rating,
            results=results,
        )

    async def list_reviews_by_game(
        self, game_id: int, page: int = 1, page_size: int = 20
    ) -> dict:
        """
        Alias orientado a tests/unit para mantener compatibilidad con la API anterior
        que retornaba diccionarios en lugar de modelos Pydantic.
        """
        response = await self.list_game_reviews(game_id, page, page_size)
        return response.model_dump()

    async def update_review(
        self, review_id: int, data: ReviewUpdate, user_id: int
    ) -> ReviewResponse | None:
        """
        Actualiza reseña.

        Valida que la reseña pertenezca al usuario.
        """
        review = await self.review_repo.get_by_id(review_id)
        if not review:
            return None
        if review.user_id != user_id:
            raise ValueError("La reseña no pertenece al usuario autenticado")

        updated_review = await self.review_repo.update(review_id, data)
        if not updated_review:
            return None

        return ReviewResponse(
            id=updated_review.id,
            game_id=updated_review.game_id,
            user_id=updated_review.user_id,
            user_name=updated_review.user.full_name,
            rating=updated_review.rating,
            comment=updated_review.comment,
            created_at=updated_review.created_at,
            updated_at=updated_review.updated_at,
        )

    async def delete_review(
        self, review_id: int, user_id: int, *, enforce_owner_error: bool = False
    ) -> bool:
        """Elimina reseña (valida ownership)."""
        review = await self.review_repo.get_by_id(review_id)
        if not review:
            return False
        if review.user_id != user_id:
            if enforce_owner_error:
                raise ValueError("La reseña no pertenece al usuario autenticado")
            return False
        return await self.review_repo.delete(review_id, user_id)
