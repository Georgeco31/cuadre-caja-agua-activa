from collections.abc import Callable, Generator

from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from sqlalchemy.orm import Session

from app.db.session import SessionLocal
from app.models.user import User
from app.repositories.users import get_user
from app.security.tokens import decode_access_token


bearer_scheme = HTTPBearer(auto_error=False)
ROLE_OPERATOR = "operator"
ROLE_ADMIN_AUDITOR = "admin_auditor"
VALID_ROLES = frozenset({ROLE_OPERATOR, ROLE_ADMIN_AUDITOR})
PERMISSION_DENIED_DETAIL = "No tienes permisos para realizar esta acción."


def get_db() -> Generator[Session]:
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


def get_current_user(
    credentials: HTTPAuthorizationCredentials | None = Depends(bearer_scheme),
    db: Session = Depends(get_db),
) -> User:
    if credentials is None or credentials.scheme.lower() != "bearer":
        raise _credentials_exception()

    try:
        payload = decode_access_token(credentials.credentials)
        subject = payload.get("sub")
        if subject is None:
            raise ValueError("Token sin sujeto.")
        user_id = int(subject)
    except (TypeError, ValueError):
        raise _credentials_exception() from None

    user = get_user(db, user_id)
    if user is None:
        raise _credentials_exception()
    if not user.is_active:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="El usuario esta inactivo.",
        )

    return user


get_current_active_user = get_current_user


def require_roles(*roles: str) -> Callable[..., User]:
    invalid_roles = set(roles) - VALID_ROLES
    if not roles or invalid_roles:
        raise ValueError("La dependencia de roles contiene roles invalidos.")

    def role_dependency(
        current_user: User = Depends(get_current_active_user),
    ) -> User:
        if current_user.role not in roles:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail=PERMISSION_DENIED_DETAIL,
            )
        return current_user

    return role_dependency


def ensure_admin_auditor(current_user: User) -> None:
    if current_user.role != ROLE_ADMIN_AUDITOR:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail=PERMISSION_DENIED_DETAIL,
        )


require_admin_auditor = require_roles(ROLE_ADMIN_AUDITOR)
require_operator_or_admin = require_roles(
    ROLE_OPERATOR,
    ROLE_ADMIN_AUDITOR,
)


def _credentials_exception() -> HTTPException:
    return HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="No se pudo validar el token.",
        headers={"WWW-Authenticate": "Bearer"},
    )
