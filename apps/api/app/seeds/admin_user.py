from sqlalchemy.orm import Session

from app.core.config import Settings
from app.models.user import User
from app.repositories.users import create_user, get_user_by_username
from app.security.password import get_password_hash


def seed_admin_user(
    db: Session,
    username: str,
    password: str | None,
    is_active: bool = True,
) -> User:
    if not password:
        raise ValueError("ADMIN_PASSWORD es obligatorio para crear el admin inicial.")

    existing_user = get_user_by_username(db, username)
    if existing_user is not None:
        if existing_user.role != "admin_auditor":
            existing_user.role = "admin_auditor"
            db.commit()
            db.refresh(existing_user)
        return existing_user

    user = create_user(
        db=db,
        username=username,
        password_hash=get_password_hash(password),
        role="admin_auditor",
        is_active=is_active,
    )
    db.commit()
    db.refresh(user)
    return user


def seed_admin_user_from_settings(db: Session, settings: Settings) -> User:
    return seed_admin_user(
        db=db,
        username=settings.admin_username,
        password=settings.admin_password,
        is_active=settings.admin_is_active,
    )
