from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session

from app.models.user import User
from app.repositories import users as user_repository
from app.schemas.user import UserCreate, UserUpdate
from app.security.password import get_password_hash


LAST_ADMIN_ERROR = "No se puede dejar al sistema sin un admin_auditor activo."
USERNAME_EXISTS_ERROR = "El nombre de usuario ya esta registrado."


def list_users(db: Session) -> list[User]:
    return user_repository.list_users(db)


def create_user(db: Session, payload: UserCreate) -> User:
    if user_repository.get_user_by_username(db, payload.username) is not None:
        raise ValueError(USERNAME_EXISTS_ERROR)

    user = user_repository.create_user(
        db,
        username=payload.username,
        password_hash=get_password_hash(payload.password),
        role=payload.role,
        is_active=payload.is_active,
    )
    return _commit_user(db, user)


def update_user(db: Session, user_id: int, payload: UserUpdate) -> User:
    user = _get_user_or_raise(db, user_id)
    fields = payload.model_fields_set

    target_role = payload.role if "role" in fields else user.role
    target_is_active = (
        payload.is_active if "is_active" in fields else user.is_active
    )
    if (
        user.role == "admin_auditor"
        and user.is_active
        and (target_role != "admin_auditor" or not target_is_active)
    ):
        _ensure_another_active_admin(db)

    if "username" in fields and payload.username is not None:
        existing = user_repository.get_user_by_username(db, payload.username)
        if existing is not None and existing.id != user.id:
            raise ValueError(USERNAME_EXISTS_ERROR)
        user.username = payload.username
    if "password" in fields and payload.password is not None:
        user.password_hash = get_password_hash(payload.password)
    if "role" in fields and payload.role is not None:
        user.role = payload.role
    if "is_active" in fields and payload.is_active is not None:
        user.is_active = payload.is_active

    return _commit_user(db, user)


def set_user_active(db: Session, user_id: int, is_active: bool) -> User:
    return update_user(db, user_id, UserUpdate(is_active=is_active))


def update_password(db: Session, user_id: int, new_password: str) -> User:
    user = _get_user_or_raise(db, user_id)
    user.password_hash = get_password_hash(new_password)
    return _commit_user(db, user)


def _get_user_or_raise(db: Session, user_id: int) -> User:
    user = user_repository.get_user(db, user_id)
    if user is None:
        raise ValueError("El usuario no existe.")
    return user


def _ensure_another_active_admin(db: Session) -> None:
    if len(user_repository.list_active_admin_auditors_for_update(db)) <= 1:
        raise ValueError(LAST_ADMIN_ERROR)


def _commit_user(db: Session, user: User) -> User:
    try:
        db.commit()
    except IntegrityError as error:
        db.rollback()
        raise ValueError(USERNAME_EXISTS_ERROR) from error
    db.refresh(user)
    return user
