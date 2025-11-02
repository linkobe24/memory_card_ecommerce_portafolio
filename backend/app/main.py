from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

app = FastAPI(
    title="MemoryCard E-Commerce API",
    description="Backend para tienda de videojuegos con RAWG API y Stripe",
    version="1.0.0",
    docs_url="/docs",
    redoc_url="/redoc",
)

# configuracion de CORS
origins = [
    "http://localhost:3000",
    "http://frontend:3000",
]  # front en desarrollo y front en red de docker

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.get("/")
async def root():
    return {
        "message": "MemoryCard E-Commerce API",
        "status": "running",
        "docs": "/docs",
    }
