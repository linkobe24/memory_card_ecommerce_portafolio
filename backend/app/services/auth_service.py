from datetime import datetime, timedelta
from fastapi import HTTPException, status
from app.crud.user_interface import UserRepositoryInterface
from app.schemas.user import UserCreate
from app.schemas.auth import TokenResponse
from app.models.user import User
from app.core.security import (
    hash_password,
    verify_password,
    create_access_token,
    create_refresh_token,
    decode_token,
)


class AuthService:
    """
    Servicio de autenticación que maneja toda la lógica de negocio.

    Responsabilidades:
    - Registro de usuarios (validaciones + creación)
    - Login (verificación + generación de tokens)
    - Refresh de access tokens
    - Validaciones de negocio (email único, password válido, etc.)
    """

    def __init__(self, user_repository: UserRepositoryInterface):
        """
        Args:
            user_repository: Repositorio para operaciones de datos de usuarios
        """
        self.user_repo = user_repository

    async def register_user(self, user_data: UserCreate) -> User:
        """
        Registra un nuevo usuario.

        Validaciones:
        - Email no debe existir
        - Password debe ser válido (mínimo 8 caracteres)

        Args:
            user_data: Datos del nuevo usuario

        Returns:
            Usuario creado

        Raises:
            HTTPException 400: Si email ya existe
            HTTPException 422: Si password no es válido
        """
        existing_user = await self.user_repo.get_by_email(user_data.email)
        if existing_user:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"El email '{user_data.email}' ya está registrado",
            )

        if len(user_data.password) < 8:
            raise HTTPException(
                status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
                detail="La contraseña debe tener al menos 8 caracteres",
            )

        hashed_password = hash_password(user_data.password)

        new_user = await self.user_repo.create_user(user_data=user_data)

        return new_user

    async def login_user(self, email: str, password: str) -> TokenResponse:
        """
        Autentica un usuario y genera tokens.

        Flujo:
        1. Buscar usuario por email
        2. Verificar password
        3. Generar access token (15 min)
        4. Generar refresh token (7 días)
        5. Actualizar last_login timestamp

        Args:
            email: Email del usuario
            password: Password en texto plano

        Returns:
            TokenResponse con access_token y refresh_token

        Raises:
            HTTPException 401: Si credenciales son inválidas
        """
        user = await self.user_repo.get_by_email(email)
        if not user:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Email o contraseña incorrectos",
            )

        if not verify_password(password, user.hashed_password):
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Email o contraseña incorrectos",
            )

        access_token = create_access_token(data={"sub": user.email, "user_id": user.id})
        refresh_token = create_refresh_token(
            data={"sub": user.email, "user_id": user.id}
        )

        await self.user_repo.update_last_login(user.id)

        return TokenResponse(
            access_token=access_token, refresh_token=refresh_token, token_type="bearer"
        )

    async def refresh_access_token(self, refresh_token: str) -> TokenResponse:
        """
        Genera un nuevo access token usando un refresh token válido.

        Validaciones:
        - Refresh token debe ser válido (firma correcta, no expirado)
        - Usuario debe existir

        Args:
            refresh_token: Refresh token JWT

        Returns:
            TokenResponse con nuevo access_token y mismo refresh_token

        Raises:
            HTTPException 401: Si refresh token es inválido o usuario no existe
        """
        try:
            payload = decode_token(refresh_token)
            email = payload.get("sub")
            if not email:
                raise HTTPException(
                    status_code=status.HTTP_401_UNAUTHORIZED,
                    detail="Token de actualización inválido",
                )
        except Exception:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Token de actualización inválido o expirado",
            )

        user = await self.user_repo.get_by_email(email)
        if not user:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="El usuario ya no existe",
            )

        new_access_token = create_access_token(
            data={"sub": user.email, "user_id": user.id}
        )

        return TokenResponse(
            access_token=new_access_token,
            refresh_token=refresh_token,
            token_type="bearer",
        )

    async def get_current_user_profile(self, email: str) -> User:
        """
        Obtiene el perfil del usuario actual.

        Usado por el endpoint /me para devolver información del usuario autenticado.

        Args:
            email: Email del usuario (extraído del JWT)

        Returns:
            Usuario encontrado

        Raises:
            HTTPException 404: Si usuario no existe
        """
        user = await self.user_repo.get_by_email(email)
        if not user:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND, detail="Usuario no encontrado"
            )
        return user
