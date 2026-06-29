from sqlalchemy import select
from sqlalchemy.orm import Session

from app.models.user import User


def get_user_by_username(db: Session, username: str) -> User | None:
    statement = select(User).where(User.username == username)
    return db.scalar(statement)


def create_user(
    db: Session,
    username: str,
    password_hash: str,
    is_active: bool = True,
) -> User:
    user = User(
        username=username,
        password_hash=password_hash,
        is_active=is_active,
    )
    db.add(user)
    return user
