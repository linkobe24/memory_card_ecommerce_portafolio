from sqlalchemy import String, DateTime, Enum, func
from sqlalchemy.orm import Mapped, mapped_column
from app.core.database import Base
from datetime import datetime
import enum


class UserRole(str, enum.Enum):
    CUSTOMER = "customer"
    ADMIN = "admin"


class User(Base):
    """
    Modelo de usuario para autenticación y autorización.

    Campos:
    - id: Primary key auto-incremental
    - email: Único, usado para login
    - hashed_password: Password hasheado con bcrypt (NUNCA guardamos passwords en texto plano)
    - full_name: Nombre completo del usuario
    - role: customer o admin (usado para autorización)
    - created_at: Timestamp de creación (auto-generado)
    - last_login: Timestamp del último login exitoso (nullable, usado para auditoría y seguridad)
    """

    __tablename__ = "users"

    id: Mapped[int] = mapped_column(primary_key=True, index=True)
    email: Mapped[str] = mapped_column(String, unique=True, index=True, nullable=False)
    hashed_password: Mapped[str] = mapped_column(String, nullable=False)
    full_name: Mapped[str] = mapped_column(String, nullable=False)
    role: Mapped[UserRole] = mapped_column(
        Enum(UserRole), default=UserRole.CUSTOMER, nullable=False
    )
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now()
    )
    last_login: Mapped[datetime | None] = mapped_column(
        DateTime(timezone=True), nullable=True
    )

    def __repr__(self):
        return f"<User(id={self.id}, email={self.email}, role={self.role})>"
