from pydantic import BaseModel, EmailStr, Field, ConfigDict
from datetime import datetime
from app.models.user import UserRole


class UserCreate(BaseModel):
    """
    Schema de validación para registro de usuario.
    """

    email: EmailStr
    password: str = Field(..., min_length=8, max_length=20)
    full_name: str = Field(..., min_length=2, max_length=100)


class UserUpdate(BaseModel):
    """
    Schema de validación para actualización parcial de usuario.

    - Todos los campos son opcionales (PATCH semantics).
    - No permite cambiar `id`, `created_at` ni `role` por seguridad.
    - Si se incluye `password`, se hashea en el servicio antes de guardar.
    """

    email: EmailStr | None = Field(None, description="Nuevo email del usuario")
    full_name: str | None = Field(
        None, min_length=2, max_length=100, description="Nombre completo actualizado"
    )
    password: str | None = Field(
        None, min_length=8, max_length=20, description="Nueva contraseña (sin hashear)"
    )

    model_config = {
        "extra": "forbid",  # evita campos no declarados
    }


class UserResponse(BaseModel):
    """
    Schema de respuesta para endpoints que devuelven info de usuario.
    IMPORTANTE: NO incluye hashed_password (seguridad).
    """

    id: int
    email: str
    full_name: str
    role: UserRole
    created_at: datetime
    last_login: datetime | None = None

    model_config = ConfigDict(from_attributes=True)


class Token(BaseModel):
    """
    Schema de respuesta para /login y /register.
    """

    access_token: str
    refres_token: str
    token_type: str = "bearer"


class TokenData(BaseModel):
    """
    Schema para datos deserializados del payload del JWT.
    """

    email: str | None = None
