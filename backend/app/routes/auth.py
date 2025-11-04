from fastapi import APIRouter, Request, status
from slowapi import Limiter
from slowapi.util import get_remote_address

from app.core.dependencies import AuthServiceDep
from app.schemas.user import UserCreate, UserResponse
from app.schemas.auth import LoginRequest, RefreshRequest, TokenResponse
from app.middleware.auth import CurrentUser

router = APIRouter()

limiter = Limiter(key_func=get_remote_address)


@router.post(
    "/register", response_model=TokenResponse, status_code=status.HTTP_201_CREATED
)
@limiter.limit("5/minute")
async def register(
    user_data: UserCreate, request: Request, auth_service: AuthServiceDep
):
    """
    Registra un nuevo usuario.

    Flujo:
    1. FastAPI valida user_data con Pydantic (automático)
    2. Route delega al service
    3. Service maneja validaciones de negocio + creación
    4. Route devuelve tokens

    Rate limit: 5 requests/minuto por IP

    Args:
        user_data: Schema con email, password, full_name
        request: Request de FastAPI (usado por rate limiter)
        auth_service: Servicio de autenticación (inyectado por FastAPI)

    Returns:
        TokenResponse con access_token y refresh_token

    Raises:
        HTTPException 400: Si email ya está registrado (levantado por service)
        HTTPException 422: Si password no es válido (levantado por service)
    """
    user = await auth_service.register_user(user_data)

    token_response = await auth_service.login_user(user.email, user_data.password)

    return token_response


@router.post("/login", response_model=TokenResponse)
@limiter.limit("5/minute")
async def login(
    login_data: LoginRequest, request: Request, auth_service: AuthServiceDep
):
    """
    Autentica un usuario y devuelve tokens.

    Flujo:
    1. FastAPI valida login_data con Pydantic (automático)
    2. Route delega al service
    3. Service maneja validaciones + generación de tokens
    4. Route devuelve tokens

    Rate limit: 5 requests/minuto por IP

    Args:
        login_data: Schema con email y password
        request: Request de FastAPI (usado por rate limiter)
        auth_service: Servicio de autenticación (inyectado por FastAPI)

    Returns:
        TokenResponse con access_token y refresh_token

    Raises:
        HTTPException 401: Si credenciales son incorrectas (levantado por service)
    """
    token_response = await auth_service.login_user(
        email=login_data.email, password=login_data.password
    )
    return token_response


@router.post("/refresh", response_model=TokenResponse)
async def refresh(refresh_data: RefreshRequest, auth_service: AuthServiceDep):
    """
    Renueva access token usando refresh token.

    Flujo:
    1. FastAPI valida refresh_data con Pydantic (automático)
    2. Route delega al service
    3. Service verifica refresh token + genera nuevo access token
    4. Route devuelve tokens

    Args:
        refresh_data: Schema con refresh_token
        auth_service: Servicio de autenticación (inyectado por FastAPI)

    Returns:
        TokenResponse con nuevo access_token y mismo refresh_token

    Raises:
        HTTPException 401: Si refresh token es inválido (levantado por service)
    """
    token_response = await auth_service.refresh_access_token(refresh_data.refresh_token)
    return token_response


@router.get("/me", response_model=UserResponse)
async def get_me(current_user: CurrentUser, auth_service: AuthServiceDep):
    """
    Devuelve información del usuario autenticado.

    Endpoint protegido: Requiere JWT válido en header Authorization.

    El middleware get_current_user extrae y verifica el JWT automáticamente.

    Flujo:
    1. Middleware verifica JWT y extrae email
    2. Middleware busca usuario y lo inyecta en `current_user`
    3. Route devuelve información del usuario

    Args:
        current_user: Usuario autenticado (inyectado por middleware)
        auth_service: Servicio de autenticación (inyectado, no usado aquí)

    Returns:
        UserResponse con información del usuario (sin password)
    """
    return current_user
