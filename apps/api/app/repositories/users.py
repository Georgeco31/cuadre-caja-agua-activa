from sqlalchemy import select
from sqlalchemy.orm import Session

from app.models.user import User


def get_user(db: Session, user_id: int) -> User | None:
    return db.get(User, user_id)


def get_user_by_username(db: Session, username: str) -> User | None:
    statement = select(User).where(User.username == username)
    return db.scalar(statement)


def list_users(db: Session) -> list[User]:
    statement = select(User).order_by(User.username, User.id)
    return list(db.scalars(statement))


def list_active_admin_auditors_for_update(db: Session) -> list[User]:
    statement = (
        select(User)
        .where(
            User.role == "admin_auditor",
            User.is_active.is_(True),
        )
        .order_by(User.id)
        .with_for_update()
    )
    return list(db.scalars(statement))


def create_user(
    db: Session,
    username: str,
    password_hash: str,
    role: str = "operator",
    is_active: bool = True,
) -> User:
    user = User(
        username=username,
        password_hash=password_hash,
        role=role,
        is_active=is_active,
    )
    db.add(user)
    return user
