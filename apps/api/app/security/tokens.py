from datetime import UTC, datetime, timedelta

import jwt
from jwt import InvalidTokenError

from app.core.config import get_settings


def create_access_token(
    subject: str | int,
    role: str | None = None,
    expires_delta: timedelta | None = None,
) -> str:
    settings = get_settings()
    expire = datetime.now(UTC) + (
        expires_delta or timedelta(minutes=settings.access_token_expire_minutes)
    )
    payload = {
        "sub": str(subject),
        "exp": expire,
    }
    if role is not None:
        payload["role"] = role
    return jwt.encode(
        payload,
        settings.auth_secret_key,
        algorithm=settings.auth_algorithm,
    )


def decode_access_token(token: str) -> dict[str, object]:
    settings = get_settings()
    try:
        return jwt.decode(
            token,
            settings.auth_secret_key,
            algorithms=[settings.auth_algorithm],
        )
    except InvalidTokenError as error:
        raise ValueError("Token invalido.") from error
