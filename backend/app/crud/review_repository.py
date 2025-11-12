"""
Implementación PostgreSQL del repositorio de Review.

Usa joins para obtener metadata del usuario.
"""

from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func
from sqlalchemy.orm import selectinload
from app.crud.review_interface import ReviewRepositoryInterface
from app.models.review import Review
from app.schemas.review import ReviewCreate, ReviewUpdate


class PostgresReviewRepository(ReviewRepositoryInterface):
    """Repositorio de reseñas usando PostgreSQL."""

    def __init__(self, db: AsyncSession):
        self.db = db

    async def create(self, user_id: int, data: ReviewCreate) -> Review:
        """Crea reseña."""
        review = Review(
            user_id=user_id,
            game_id=data.game_id,
            rating=data.rating,
            comment=data.comment,
        )

        self.db.add(review)
        await self.db.commit()
        await self.db.refresh(review, ["user"])  # Eager load user
        return review

    async def get_by_id(self, review_id: int) -> Review | None:
        """Obtiene reseña con user eager loaded."""
        result = await self.db.execute(
            select(Review)
            .where(Review.id == review_id)
            .options(selectinload(Review.user))
        )
        return result.scalar_one_or_none()

    async def get_user_review_for_game(
        self, user_id: int, game_id: int
    ) -> Review | None:
        """Obtiene reseña de usuario para juego específico."""
        result = await self.db.execute(
            select(Review).where(Review.user_id == user_id, Review.game_id == game_id)
        )
        return result.scalar_one_or_none()

    async def list_by_game(
        self, game_id: int, skip: int = 0, limit: int = 20
    ) -> tuple[list[Review], int, float]:
        """Lista reseñas de un juego con promedio de rating."""
        # Count total
        count_result = await self.db.execute(
            select(func.count()).select_from(Review).where(Review.game_id == game_id)
        )
        total = count_result.scalar()

        # Calcular promedio de rating
        avg_result = await self.db.execute(
            select(func.avg(Review.rating)).where(Review.game_id == game_id)
        )
        average_rating = avg_result.scalar() or 0.0

        # Query con paginación
        result = await self.db.execute(
            select(Review)
            .where(Review.game_id == game_id)
            .options(selectinload(Review.user))
            .order_by(Review.created_at.desc())
            .offset(skip)
            .limit(limit)
        )
        reviews = list(result.scalars().all())

        return reviews, total, float(average_rating)

    async def update(self, review_id: int, data: ReviewUpdate) -> Review | None:
        """Actualiza reseña."""
        review = await self.get_by_id(review_id)
        if not review:
            return None

        # Actualizar solo campos proporcionados
        update_data = data.model_dump(exclude_unset=True)
        for field, value in update_data.items():
            setattr(review, field, value)

        await self.db.commit()
        await self.db.refresh(review)
        return review

    async def delete(self, review_id: int, user_id: int) -> bool:
        """Elimina reseña (valida ownership)."""
        result = await self.db.execute(
            select(Review).where(Review.id == review_id, Review.user_id == user_id)
        )
        review = result.scalar_one_or_none()

        if not review:
            return False

        await self.db.delete(review)
        await self.db.commit()
        return True
