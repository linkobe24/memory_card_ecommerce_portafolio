from abc import ABC, abstractmethod
from typing import TypeVar, Generic

T = TypeVar("T")


class BaseRepository(ABC, Generic[T]):
    """
    Interfaz base genérica para repositorios.

    Esta clase define el contrato mínimo que todos los repositories deben cumplir.
    Usando Generics, podemos reutilizar esta interfaz para diferentes modelos.

    Type Parameters:
        T: El tipo de modelo que este repository maneja (ej: User, Product, Order)

    Ejemplo de uso:
        class UserRepositoryInterface(BaseRepository[User]):
            pass
    """

    @abstractmethod
    async def get_by_id(self, id: int) -> T | None:
        """
        Interfaz base genérica para repositorios.

        Esta clase define el contrato mínimo que todos los repositories deben cumplir.
        Usando Generics, podemos reutilizar esta interfaz para diferentes modelos.

        Type Parameters:
            T: El tipo de modelo que este repository maneja (ej: User, Product, Order)

        Ejemplo de uso:
            class UserRepositoryInterface(BaseRepository[User])
        """
        pass

    @abstractmethod
    async def create(self, data) -> T:
        """
        Crear nueva entidad.

        Args:
            data: Schema de Pydantic con datos de creación

        Returns:
            Entidad creada con ID asignado
        """
        pass

    @abstractmethod
    async def update(self, id: int, data) -> T | None:
        """
        Actualizar entidad existente.

        Args:
            id: ID de la entidad
            data: Schema de Pydantic con datos de actualización

        Returns:
            Entidad actualizada si existe, None si no existe
        """
        pass

    @abstractmethod
    async def delete(self, id: int) -> bool:
        """
        Eliminar entidad.

        Args:
            id: ID de la entidad

        Returns:
            True si fue eliminada, False si no existía
        """
        pass
