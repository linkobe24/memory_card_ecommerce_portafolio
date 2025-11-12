from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from app.crud.user_interface import UserRepositoryInterface
from app.models.user import User
from app.schemas.user import UserCreate, UserUpdate
from app.core.security import hash_password


class PostgresUserRepository(UserRepositoryInterface):
    """
    Implementación concreta del repository de usuarios usando PostgreSQL + SQLAlchemy.

    Esta clase implementa TODOS los métodos abstractos definidos en:
    - UserRepositoryInterface (get_by_email, create_user)
    - BaseRepository[User] (get_by_id, create, update, delete)

    Args:
        db: AsyncSession de SQLAlchemy (inyectada por FastAPI)
    """

    def __init__(self, db: AsyncSession):
        self.db = db

    async def get_by_email(self, email: str) -> User | None:
        """
        Buscar usuario por email (implementación PostgreSQL).
        """
        result = await self.db.execute(select(User).where(User.email == email))
        return result.scalar_one_or_none()

    async def get_by_id(self, id: int) -> User | None:
        """
        Buscar usuario por ID (implementación PostgreSQL).
        """
        result = await self.db.execute(select(User).where(User.id == id))
        return result.scalar_one_or_none()

    async def create_user(self, user_data: UserCreate) -> User:
        """
        Crear nuevo usuario (implementación PostgreSQL).

        Flujo:
        1. Hashea la password con bcrypt
        2. Crea instancia de User (SQLAlchemy model)
        3. Añade a session (no commitea todavía)
        4. Commitea transacción
        5. Refresca para obtener ID asignado
        6. Devuelve usuario completo
        """
        new_user = User(
            email=user_data.email,
            hashed_password=hash_password(user_data.password),
            full_name=user_data.full_name,
        )

        self.db.add(new_user)
        await self.db.commit()
        await self.db.refresh(new_user)
        return new_user

    async def create(self, data: UserCreate) -> User:
        """
        Implementación de BaseRepository.create() (delega a create_user).
        """
        return await self.create_user(data)

    async def update(self, id: int, data: UserUpdate) -> User | None:
        """
        Actualizar usuario (implementación PostgreSQL).
        """
        user = await self.get_by_id(id)
        if user is None:
            return None

        update_data = data.model_dump(exclude_unset=True)
        for field, value in update_data.items():
            if field == "password":
                value = hash_password(value)
                field = "hashed_password"
            setattr(user, field, value)

        await self.db.commit()
        await self.db.refresh(user)
        return user

    async def delete(self, id: int) -> bool:
        """
        Eliminar usuario (implementación PostgreSQL).

        Devuelve True si fue eliminado, False si no existía.
        """
        user = await self.get_by_id(id)
        if user is None:
            return False

        await self.db.delete(user)
        await self.db.commit()
        return True

    async def update_last_login(self, user_id: int) -> None:
        """
        Actualizar timestamp del último login exitoso.

        Actualiza el campo last_login con el timestamp actual (UTC).
        Este método se llama después de una autenticación exitosa.

        Args:
            user_id: ID del usuario

        Nota:
            Este método no lanza excepción si el usuario no existe.
            Es un side effect (efecto secundario) del login exitoso.
        """
        from datetime import datetime, timezone

        user = await self.get_by_id(user_id)
        if user:
            user.last_login = datetime.now(timezone.utc)
            await self.db.commit()
