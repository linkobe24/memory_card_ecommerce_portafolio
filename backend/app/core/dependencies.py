from typing import Annotated
from fastapi import Depends
from sqlalchemy.ext.asyncio import AsyncSession
from app.core.database import get_db
from app.crud.user_interface import UserRepositoryInterface
from app.crud.user_repository import PostgresUserRepository
from app.services.auth_service import AuthService


def get_user_repository(db: AsyncSession = Depends(get_db)) -> UserRepositoryInterface:
    """
    Factory que crea instancias de UserRepository.

    Esta función es un Dependency de FastAPI que:
    1. Recibe la session de DB (inyectada por FastAPI)
    2. Crea una instancia de PostgresUserRepository
    3. La devuelve como UserRepositoryInterface (abstracción)

    Uso en routes:
        @app.post("/register")
        async def register(
            user_repo: Annotated[UserRepositoryInterface, Depends(get_user_repository)]
        ):
            user = await user_repo.get_by_email(email)

    Para cambiar de PostgreSQL a MongoDB:
        return MongoUserRepository(db)  # ← Solo cambiar esta línea

    Args:
        db: Session de base de datos (inyectada automáticamente por FastAPI)

    Returns:
        Instancia de UserRepositoryInterface (implementación concreta)
    """
    return PostgresUserRepository(db)


# Type alias para simplificar uso en routes
# En lugar de escribir: Annotated[UserRepositoryInterface, Depends(get_user_repository)]
# Puedes escribir: UserRepoDep
UserRepoDep = Annotated[UserRepositoryInterface, Depends(get_user_repository)]


def get_auth_service(user_repo: UserRepoDep) -> AuthService:
    """
    Factory para inyectar AuthService.

    El service depende del repository, FastAPI los inyecta automáticamente.
    """
    return AuthService(user_repository=user_repo)


AuthServiceDep = Annotated[AuthService, Depends(get_auth_service)]
