"""Security helpers: password hashing + JWT utilities.

This module keeps auth-related primitives in one place.
- Password hashing: Passlib (bcrypt)
- JWT: python-jose

Used by CRUD / auth routes.
"""

from __future__ import annotations

from datetime import datetime, timedelta, timezone
from fastapi import HTTPException
from typing import Any

from jose import JWTError, jwt
from passlib.context import CryptContext


# Password hashing (bcrypt)
_pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")



class PasswordHasher:
    """Tiny wrapper so the rest of the app can call `.hash()` / `.verify()`."""

    def hash(self, plain_password: str) -> str:
        return _pwd_context.hash(plain_password)

    def verify(self, plain_password: str, hashed_password: str) -> bool:
        return _pwd_context.verify(plain_password, hashed_password)


password_hash = PasswordHasher()


# JWT helpers
# NOTE: Keep these values in environment variables in production.
# Example:
#   SECRET_KEY="change-me"
#   ALGORITHM="HS256"
#   ACCESS_TOKEN_EXPIRE_MINUTES=60
try:
    # If you have a settings module, prefer importing from there.
    from app.core.config import settings  # type: ignore

    SECRET_KEY: str = settings.SECRET_KEY
    ALGORITHM: str = settings.ALGORITHM
    ACCESS_TOKEN_EXPIRE_MINUTES: int = int(settings.ACCESS_TOKEN_EXPIRE_MINUTES)
except Exception:
    # Fallback defaults (use env/settings in real deployments)
    SECRET_KEY = "rahasia"  # pragma: no cover
    ALGORITHM = "HS256"  # pragma: no cover
    ACCESS_TOKEN_EXPIRE_MINUTES = 60  # pragma: no cover


def create_access_token(
    data: dict[str, Any],
    expires_delta: timedelta | None = None,
) -> str:
    """Create a signed JWT.

    `data` should contain identity info like {"user_id": "..."}.
    Adds an `exp` claim automatically.
    """

    to_encode = data.copy()

    expire = datetime.now(timezone.utc) + (
        expires_delta
        if expires_delta is not None
        else timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    )

    to_encode.update({"exp": expire})
    return jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)

def decode_token(token: str) -> dict[str, Any]:
    try:
        return jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
    except JWTError:
        return None


def safe_decode_token(token: str) -> dict[str, Any] | None:
    """Decode a token but return None instead of raising."""

    try:
        return decode_token(token)
    except JWTError:
        return None
