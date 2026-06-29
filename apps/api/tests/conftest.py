from collections.abc import Generator
from datetime import date
from decimal import Decimal

import pytest
from sqlalchemy import create_engine
from sqlalchemy.orm import Session, sessionmaker

from app.db.base import Base
from app.models.denomination import Denomination
import app.models  # noqa: F401


@pytest.fixture
def db() -> Generator[Session]:
    engine = create_engine("sqlite+pysqlite:///:memory:")
    TestingSessionLocal = sessionmaker(
        autocommit=False,
        autoflush=False,
        bind=engine,
    )
    Base.metadata.create_all(bind=engine)

    with TestingSessionLocal() as session:
        yield session

    Base.metadata.drop_all(bind=engine)


@pytest.fixture
def sample_denominations(db: Session) -> dict[str, Denomination]:
    denominations = {
        "coin_025": Denomination(
            type="coin",
            value=Decimal("0.25"),
            label="0.25",
        ),
        "coin_100": Denomination(
            type="coin",
            value=Decimal("1.00"),
            label="1.00",
        ),
        "bill_1000": Denomination(
            type="bill",
            value=Decimal("10.00"),
            label="10.00",
        ),
        "bill_2000": Denomination(
            type="bill",
            value=Decimal("20.00"),
            label="20.00",
        ),
    }
    db.add_all(denominations.values())
    db.commit()

    for denomination in denominations.values():
        db.refresh(denomination)

    return denominations


@pytest.fixture
def cash_session(db: Session):
    from app.services.cash_session_service import create_cash_session

    return create_cash_session(db, date(2026, 6, 29), notes="Cuadre diario")
