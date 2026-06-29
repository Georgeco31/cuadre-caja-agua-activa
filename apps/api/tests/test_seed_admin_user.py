from sqlalchemy import select

from app.models.user import User
from app.security.password import verify_password
from app.seeds.admin_user import seed_admin_user


def test_seed_admin_user_creates_admin_with_password_hash(db) -> None:
    admin = seed_admin_user(
        db=db,
        username="admin",
        password="admin123",
        is_active=True,
    )

    assert admin.id is not None
    assert admin.username == "admin"
    assert admin.password_hash
    assert admin.password_hash != "admin123"
    assert verify_password("admin123", admin.password_hash)
    assert admin.is_active is True


def test_seed_admin_user_is_idempotent(db) -> None:
    first_admin = seed_admin_user(
        db=db,
        username="admin",
        password="admin123",
        is_active=True,
    )
    second_admin = seed_admin_user(
        db=db,
        username="admin",
        password="changed-password",
        is_active=True,
    )

    assert first_admin.id == second_admin.id
    assert _count_users(db) == 1
    assert verify_password("admin123", second_admin.password_hash)


def test_seed_admin_user_requires_password(db) -> None:
    try:
        seed_admin_user(
            db=db,
            username="admin",
            password=None,
            is_active=True,
        )
    except ValueError as error:
        assert "ADMIN_PASSWORD" in str(error)
    else:
        raise AssertionError("seed_admin_user debe exigir ADMIN_PASSWORD")


def _count_users(db) -> int:
    return len(db.scalars(select(User)).all())
