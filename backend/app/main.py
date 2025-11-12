from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from contextlib import asynccontextmanager

from app.routes import auth, catalog, game_catalog, cart, order, review
from app.core.init_db import init_db
from app.core.config import settings


@asynccontextmanager
async def lifespan(app: FastAPI):
    await init_db()

    print("✅ Base de datos inicializada")
    yield
    print("Apagando")


app = FastAPI(
    title=settings.APP_NAME,
    description="Backend para tienda de videojuegos con RAWG API y Stripe",
    version="1.0.0",
    docs_url="/docs",
    redoc_url="/redoc",
    debug=settings.DEBUG,
    lifespan=lifespan,
    swagger_ui_init_oauth={
        "usePkceWithAuthorizationCodeGrant": False,  # No usamos PKCE (solo password grant)
        "useBasicAuthenticationWithAccessCodeGrant": False,  # No usamos Basic Auth
    },
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.CORS_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(auth.router, prefix="/api/auth", tags=["Auth"])
app.include_router(catalog.router, prefix="/api/catalog", tags=["Catalog"])
app.include_router(game_catalog.router, prefix="/api/products", tags=["Products"])
app.include_router(cart.router, prefix="/api/cart", tags=["Cart"])
app.include_router(order.router, prefix="/api/orders", tags=["Orders"])
app.include_router(review.router, prefix="/api/reviews", tags=["Reviews"])


@app.get("/")
async def root():
    """
    Endpoint raíz que confirma que la API está funcionando.
    """
    return {
        "message": "MemoryCard E-Commerce API",
        "status": "running",
        "docs": "/docs",
    }
