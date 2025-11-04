from passlib.context import CryptContext
from jose import JWTError, jwt
from datetime import datetime, timedelta, timezone
from app.core.config import settings

# bcrypt_sha256 evita el límite de 72 bytes de bcrypt puro
pwd_context = CryptContext(schemes=["bcrypt_sha256"], deprecated="auto")


def hash_password(password: str) -> str:
    """
    Hashea una password con bcrypt.

    Bcrypt genera un salt aleatorio automáticamente y lo incluye en el hash.
    El hash resultante tiene formato: $2b$12$<salt><hash>

    Args:
        password: Password en texto plano

    Returns:
        Password hasheado (60 caracteres)
    """
    return pwd_context.hash(password)


def verify_password(plain_password: str, hashed_password: str) -> bool:
    """
    Verifica si una password coincide con el hash guardado.

    Bcrypt extrae el salt del hash guardado y verifica si coincide.

    Args:
        plain_password: Password en texto plano (del request)
        hashed_password: Password hasheado (de la base de datos)

    Returns:
        True si coincide, False si no coincide
    """
    return pwd_context.verify(plain_password, hashed_password)


def create_access_token(data: dict) -> str:
    """
    Genera un access token JWT.

    El token incluye:
    - sub: Email del usuario
    - exp: Timestamp de expiración (15 minutos desde ahora)
    - iat: Timestamp de emisión (issued at)

    Args:
        data: Diccionario con datos a incluir en el payload (ej: {"sub": "user@example.com"})

    Returns:
        JWT firmado como string
    """
    to_encode = data.copy()
    expire = datetime.now(timezone.utc) + timedelta(
        minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES
    )
    to_encode.update({"exp": expire, "iat": datetime.now(timezone.utc)})
    encoded_jwt = jwt.encode(
        to_encode, settings.JWT_SECRET_KEY, algorithm=settings.JWT_ALGORITHM
    )
    return encoded_jwt


def create_refresh_token(data: dict) -> str:
    """
    Genera un refresh token JWT.

    Similar a access token pero con expiración más larga (7 días).

    Args:
        data: Diccionario con datos a incluir en el payload

    Returns:
        JWT firmado como string
    """
    to_encode = data.copy()
    expire = datetime.now(timezone.utc) + timedelta(
        days=settings.REFRESH_TOKEN_EXPIRE_DAYS
    )
    to_encode.update({"exp": expire, "iat": datetime.now(timezone.utc)})
    encoded_jwt = jwt.encode(
        to_encode, settings.JWT_SECRET_KEY, algorithm=settings.JWT_ALGORITHM
    )
    return encoded_jwt


def verify_token(token: str) -> dict | None:
    """
    Verifica y decodifica un JWT.

    Verifica:
    1. Firma (que el token no fue modificado)
    2. Expiración (que no haya expirado)

    Args:
        token: JWT como string

    Returns:
        Payload decodificado si el token es válido, None si es inválido o expirado
    """
    try:
        payload = jwt.decode(
            token, settings.JWT_SECRET_KEY, algorithms=[settings.JWT_ALGORITHM]
        )
        return payload
    except JWTError:
        return None


def decode_token(token: str) -> dict:
    """
    Decodifica un JWT y deja que las excepciones se propaguen.

    Útil cuando el caller necesita saber por qué falló (firma inválida,
    token expirado, etc.) y manejar el error de manera personalizada.

    Args:
        token: JWT como string

    Returns:
        Payload decodificado si el token es válido

    Raises:
        JWTError: Si el token es inválido o expirado
    """
    return jwt.decode(
        token, settings.JWT_SECRET_KEY, algorithms=[settings.JWT_ALGORITHM]
    )
