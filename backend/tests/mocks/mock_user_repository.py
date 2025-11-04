from app.crud.user_interface import UserRepositoryInterface
from app.models.user import User
from app.schemas.user import UserCreate
from app.core.security import hash_password
from datetime import datetime, timezone


class MockUserRepository(UserRepositoryInterface):
    """
    Mock repository para tests unitarios.

    Simula el comportamiento del repository sin usar DB real.
    Los datos se guardan en un diccionario en memoria.
    """

    def __init__(self):
        # Almacenamiento en memoria (simulando DB)
        self.users: dict[str, User] = {}
        self.next_id = 1

    async def get_by_email(self, email: str) -> User | None:
        """Buscar usuario por email en diccionario"""
        return self.users.get(email)

    async def get_by_id(self, id: int) -> User | None:
        """Buscar usuario por ID en diccionario"""
        for user in self.users.values():
            if user.id == id:
                return user
        return None

    async def create_user(self, user_data: UserCreate) -> User:
        """Crear usuario en memoria"""
        if user_data.email in self.users:
            raise ValueError("Email ya existe")

        new_user = User(
            id=self.next_id,
            email=user_data.email,
            hashed_password=hash_password(user_data.password),
            full_name=user_data.full_name,
            role="customer",
            created_at=datetime.now(timezone.utc),
        )

        self.users[user_data.email] = new_user
        self.next_id += 1
        return new_user

    async def create(self, data: UserCreate) -> User:
        """Delega a create_user"""
        return await self.create_user(data)

    async def update(self, id: int, data) -> User | None:
        """Actualizar usuario en memoria"""
        user = await self.get_by_id(id)
        if user is None:
            return None

        if hasattr(data, "full_name") and data.full_name:
            user.full_name = data.full_name
        if hasattr(data, "email") and data.email:
            # Actualizar key en diccionario
            del self.users[user.email]
            user.email = data.email
            self.users[data.email] = user

        return user

    async def delete(self, id: int) -> bool:
        """Eliminar usuario en memoria"""
        user = await self.get_by_id(id)
        if user is None:
            return False

        del self.users[user.email]
        return True

    async def update_last_login(self, user_id: int) -> None:
        """Actualizar last_login en memoria"""
        user = await self.get_by_id(user_id)
        if user:
            user.last_login = datetime.now(timezone.utc)
