"""
Configuración centralizada de la aplicación usando Pydantic Settings.

Pydantic Settings permite:
- Validación automática de tipos
- Valores por defecto claros
- Carga desde variables de entorno
- Documentación centralizada
"""

from pydantic_settings import BaseSettings
from pydantic import Field


class Settings(BaseSettings):
    """
    Configuración de la aplicación.

    Pydantic lee automáticamente desde:
    1. Variables de entorno (.env)
    2. Valores por defecto definidos aquí
    """

    # Database
    DATABASE_URL: str = Field(
        default="postgresql+asyncpg://postgres:postgres123@postgres:5432/memorycard",
        description="URL de conexión a PostgreSQL",
    )

    # Redis
    REDIS_URL: str = Field(
        default="redis://redis:6379/0",
        description="URL de conexión a Redis para caches y rate limiting",
    )

    # JWT Settings
    JWT_SECRET_KEY: str = Field(
        default="dev-secret-key-change-in-production",
        description="Clave secreta para firmar JWT (CAMBIAR EN PRODUCCIÓN)",
    )
    JWT_ALGORITHM: str = Field(default="HS256", description="Algoritmo de firma JWT")
    ACCESS_TOKEN_EXPIRE_MINUTES: int = Field(
        default=15, description="Tiempo de expiración del access token en minutos"
    )
    REFRESH_TOKEN_EXPIRE_DAYS: int = Field(
        default=7, description="Tiempo de expiración del refresh token en días"
    )

    # CORS
    CORS_ORIGINS: list[str] = Field(
        default=["http://localhost:3000"], description="Orígenes permitidos para CORS"
    )

    # App Settings
    APP_NAME: str = Field(
        default="Memory Card E-commerce API", description="Nombre de la aplicación"
    )
    DEBUG: bool = Field(
        default=True, description="Modo debug (desactivar en producción)"
    )

    # RAWG API Settings
    RAWG_API_KEY: str = Field(
        default="",
        description="API key de RAWG (obtener en https://rawg.io/apidocs)",
    )
    RAWG_BASE_URL: str = Field(
        default="https://api.rawg.io/api",
        description="URL base de RAWG API",
    )
    RAWG_REQUEST_TIMEOUT: int = Field(
        default=10,
        description="Timeout en segundos para requests a RAWG",
    )
    RAWG_MAX_RETRIES: int = Field(
        default=3,
        description="Máximo número de reintentos en caso de error",
    )

    # Cache Settings
    CACHE_DEFAULT_TTL: int = Field(
        default=86400,  # 24 horas
        description="TTL por defecto para cache en segundos",
    )

    class Config:
        """
        Configuración de Pydantic Settings.

        env_file: Archivo .env a leer
        case_sensitive: Si las variables de entorno distinguen mayúsculas/minúsculas
        """

        env_file = ".env"
        case_sensitive = False


settings = Settings()
