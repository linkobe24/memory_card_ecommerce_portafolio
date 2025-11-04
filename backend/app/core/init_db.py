from app.core.database import engine, Base
from app.models.user import User


async def init_db():
    """
    Crea todas las tablas definidas en los models.

    Ejecuta CREATE TABLE para cada modelo que hereda de Base.
    Si la tabla ya existe, no hace nada (no es destructivo).
    """
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)


async def drop_db():
    """
    Elimina todas las tablas (útil para tests o reset completo).

    ⚠️ CUIDADO: Esto borra TODOS los datos.
    """
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.drop_all)
