"""
Schemas para respuestas de RAWG API.

Modelos Pydantic que validan y serializan datos de la API externa.
"""

from pydantic import BaseModel, ConfigDict, Field
from datetime import date


class PlatformShort(BaseModel):
    """Plataforma básica dentro de un juego."""

    id: int
    name: str
    slug: str


class PlatformInfo(BaseModel):
    """Información de plataforma con detalles de release."""

    platform: PlatformShort
    released_at: date | None = None
    requirements: dict | None = None


class GenreShort(BaseModel):
    """Género de videojuego."""

    id: int
    name: str
    slug: str


class StoreShort(BaseModel):
    """Información básica de una tienda."""

    id: int
    name: str
    slug: str


class StoreInfo(BaseModel):
    """Detalle de tienda dentro de la respuesta de un juego."""

    id: int
    url: str | None = None
    store: StoreShort


class RatingInfo(BaseModel):
    """Rating con título y porcentaje."""

    id: int
    title: str
    count: int
    percent: float


class GameShort(BaseModel):
    """
    Modelo resumido de juego para listados.

    Usado en búsquedas y catálogos.
    """

    id: int
    slug: str
    name: str
    released: date | None = None
    background_image: str | None = Field(None, alias="background_image")
    rating: float | None = 0.0
    rating_top: int | None = 5
    ratings_count: int | None = 0
    metacritic: int | None = None
    playtime: int | None = 0
    platforms: list[PlatformInfo] | None = []
    genres: list[GenreShort] | None = []

    model_config = ConfigDict(populate_by_name=True)


class GameDetail(GameShort):
    """
    Modelo detallado de juego con toda la información.

    Usado en páginas de detalle de producto.
    """

    description: str | None = ""
    description_raw: str | None = ""
    website: str | None = ""
    reddit_url: str | None = ""
    stores: list[StoreInfo] | None = []
    developers: list[dict] | None = []
    publishers: list[dict] | None = []
    ratings: list[RatingInfo] | None = []
    esrb_rating: dict | None = None


class GameListResponse(BaseModel):
    """Respuesta de listado de juegos de RAWG."""

    count: int
    next: str | None = None
    previous: str | None = None
    results: list[GameShort]


class Genre(BaseModel):
    """Género completo con metadata."""

    id: int
    name: str
    slug: str
    games_count: int
    image_background: str | None = None


class GenreListResponse(BaseModel):
    """Respuesta de listado de géneros."""

    count: int
    results: list[Genre]


class Platform(BaseModel):
    """Plataforma completa con metadata."""

    id: int
    name: str
    slug: str
    games_count: int
    image_background: str | None = None


class PlatformListResponse(BaseModel):
    """Respuesta de listado de plataformas."""

    count: int
    results: list[Platform]


class GameSearchParams(BaseModel):
    """
    Parámetros de búsqueda para catálogo de juegos.

    FastAPI parsea esto automáticamente como query parameters
    cuando se usa con Depends().
    """

    query: str = Field(..., min_length=1, description="Término de búsqueda")
    page: int = Field(1, ge=1, description="Número de página")
    page_size: int = Field(20, ge=1, le=40, description="Juegos por página (máximo 40)")
    genres: str | None = Field(
        None, description="IDs de géneros separados por coma (ej: '4,51')"
    )
    platforms: str | None = Field(
        None, description="IDs de plataformas separados por coma (ej: '4,187')"
    )

    model_config = ConfigDict(extra="forbid")  # Rechaza parámetros no declarados
