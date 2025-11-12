from fastapi import APIRouter, Request, status, Depends
from fastapi.security import OAuth2PasswordRequestForm
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
    Registra un usuario y devuelve el par de tokens inicial; limitado a 5 req/min IP.

    Valida datos con Pydantic, delega las verificaciones de negocio al servicio y
    retorna inmediatamente los tokens para que el cliente quede autenticado.
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
    Autentica credenciales y emite un nuevo par access/refresh token (5 req/min IP).

    Levanta HTTP 401 cuando el servicio detecta credenciales inválidas.
    """
    token_response = await auth_service.login_user(
        email=login_data.email, password=login_data.password
    )
    return token_response


@router.post("/token", response_model=TokenResponse)
@limiter.limit("5/minute")
async def token(
    request: Request,
    form_data: OAuth2PasswordRequestForm = Depends(),
    auth_service: AuthServiceDep = None,
):
    """
    Variante OAuth2 password grant pensada para Swagger UI (5 req/min IP).

    Acepta form-data `username/password`, reutiliza la lógica de `/login` y debe
    evitarse desde el frontend en producción.
    """
    token_response = await auth_service.login_user(
        email=form_data.username, password=form_data.password
    )
    return token_response


@router.post("/refresh", response_model=TokenResponse)
async def refresh(refresh_data: RefreshRequest, auth_service: AuthServiceDep):
    """
    Intercambia un refresh_token válido por un nuevo access_token.

    Preserva el refresh original y retorna HTTP 401 si el token fue revocado o expiró.
    """
    token_response = await auth_service.refresh_access_token(refresh_data.refresh_token)
    return token_response


@router.get("/me", response_model=UserResponse)
async def get_me(current_user: CurrentUser, auth_service: AuthServiceDep):
    """
    Devuelve el perfil público del usuario asociado al JWT enviado en Authorization.

    El middleware ya validó el token y cargó el modelo como `current_user`.
    """
    return current_user
