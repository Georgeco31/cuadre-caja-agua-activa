from app.core.config import get_settings
from app.db.session import SessionLocal
from app.seeds.admin_user import seed_admin_user_from_settings
from app.seeds.denominations import seed_denominations


def run_seeds() -> None:
    settings = get_settings()
    with SessionLocal() as db:
        denominations = seed_denominations(db)
        admin_user = seed_admin_user_from_settings(db, settings)

    print(f"Denominaciones iniciales listas: {len(denominations)}")
    print(f"Usuario admin inicial listo: {admin_user.username}")


if __name__ == "__main__":
    run_seeds()
