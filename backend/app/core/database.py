from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession, async_sessionmaker
from sqlalchemy.orm import DeclarativeBase
from app.core.config import settings

engine = create_async_engine(settings.DATABASE_URL, echo=True)

AsyncSessionLocal = async_sessionmaker(
    engine, class_=AsyncSession, expire_on_commit=False
)


class Base(DeclarativeBase):
    pass


async def get_db():
    """
    Dependency que crea una session async de base de datos.
    Se usa con FastAPI Depends: db: AsyncSession = Depends(get_db)

    El yield garantiza que la session se cierre después del request,
    incluso si hay una excepción.
    """
    async with AsyncSessionLocal() as session:
        try:
            yield session
        finally:
            await session.close()
