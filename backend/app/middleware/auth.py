from typing import Annotated
from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from app.core.dependencies import UserRepoDep
from app.core.security import verify_token
from app.models.user import User


security = OAuth2PasswordBearer(tokenUrl="/api/auth/token")


async def get_current_user(
    token: str = Depends(security),
    user_repo: UserRepoDep = None,
) -> User:
    """
    Dependency de FastAPI que verifica JWT y devuelve usuario actual.

    Flujo:
    1. OAuth2PasswordBearer extrae token del header Authorization automáticamente
    2. Verifica firma y expiración del JWT
    3. Extrae email del payload
    4. Busca usuario en base de datos
    5. Devuelve usuario o error 401

    Args:
        token: Extraído automáticamente del header Authorization (sin prefijo "Bearer ")
        user_repo: Repositorio de usuarios (inyectado por FastAPI)

    Returns:
        Usuario autenticado

    Raises:
        HTTPException 401: Si token es inválido, expirado, o usuario no existe
    """
    payload = verify_token(token)
    if payload is None:
        # Firma o expiracion invalida -> respuesta 401
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Token inválido o expirado",
            headers={"WWW-Authenticate": "Bearer"},
        )

    email = payload.get("sub")
    if email is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Token inválido: no contiene email",
            headers={"WWW-Authenticate": "Bearer"},
        )

    user = await user_repo.get_by_email(email)

    if user is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Usuario no encontrado",
            headers={"WWW-Authenticate": "Bearer"},
        )

    return user


CurrentUser = Annotated[User, Depends(get_current_user)]


async def get_current_admin(current_user: CurrentUser) -> User:
    """
    Dependency que verifica que el usuario actual sea administrador.

    Usa get_current_user para obtener el usuario autenticado,
    luego verifica que tenga rol de admin.

    Args:
        current_user: Usuario autenticado (inyectado por CurrentUser)

    Returns:
        Usuario autenticado con rol admin

    Raises:
        HTTPException 403: Si el usuario no es administrador
    """
    if not current_user.is_admin:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="No tienes permisos de administrador"
        )
    return current_user


CurrentAdmin = Annotated[User, Depends(get_current_admin)]
