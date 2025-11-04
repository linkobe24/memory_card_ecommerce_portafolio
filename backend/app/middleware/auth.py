from typing import Annotated
from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from app.core.dependencies import UserRepoDep
from app.core.security import verify_token
from app.models.user import User


security = HTTPBearer()


async def get_current_user(
    credentials: HTTPAuthorizationCredentials = Depends(security),
    user_repo: UserRepoDep = None,
) -> User:
    """
    Dependency de FastAPI que verifica JWT y devuelve usuario actual.

    Flujo:
    1. Extrae token del header Authorization
    2. Verifica firma y expiración del JWT
    3. Extrae email del payload
    4. Busca usuario en base de datos
    5. Devuelve usuario o error 401

    Args:
        credentials: Extraído automáticamente del header Authorization
        db: Session de base de datos

    Returns:
        Usuario autenticado

    Raises:
        HTTPException 401: Si token es inválido, expirado, o usuario no existe
    """
    token = credentials.credentials

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
