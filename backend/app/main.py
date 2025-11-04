from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from contextlib import asynccontextmanager

from app.routes import auth
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
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.CORS_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(auth.router, prefix="/api/auth", tags=["Auth"])


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
