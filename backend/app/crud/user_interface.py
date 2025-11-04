from abc import abstractmethod
from app.crud.base import BaseRepository
from app.models.user import User
from app.schemas.user import UserCreate


class UserRepositoryInterface(BaseRepository[User]):
    """
    Interfaz (contrato) para repositorios de usuarios.

    Cualquier clase que implemente esta interfaz debe proporcionar implementaciones
    concretas de todos los métodos abstractos.

    Ejemplo de uso:
        class PostgresUserRepository(UserRepositoryInterface):
            async def get_by_email(self, email: str) -> User | None:
                # Implementación específica de PostgreSQL
                ...
    """

    @abstractmethod
    async def get_by_email(self, email: str) -> User | None:
        """
        Buscar usuario por email.

        Args:
            email: Email del usuario (único)

        Returns:
            User si existe, None si no existe
        """
        pass

    @abstractmethod
    async def create_user(self, user_data: UserCreate) -> User:
        """
        Crear nuevo usuario.

        Especializcacion de create() para el caso de usuarios.

        Args:
            user_data: Schema de Pydantic con email, password, full_name

        Returns:
            Usuario creado con ID asignado y password hasheado
        """
        pass

    @abstractmethod
    async def update_last_login(self, user_id: int) -> None:
        """
        Actualizar timestamp del último login exitoso.

        Este método se llama después de una autenticación exitosa para mantener
        un registro de auditoría de la actividad del usuario.

        Args:
            user_id: ID del usuario

        Returns:
            None
        """
        pass
