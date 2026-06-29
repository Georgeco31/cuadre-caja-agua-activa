from collections.abc import Generator
from datetime import date
from decimal import Decimal

import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import Session, sessionmaker
from sqlalchemy.pool import StaticPool

from app.api.deps import get_db
from app.db.base import Base
from app.main import app
from app.models.denomination import Denomination
import app.models as _models  # noqa: F401


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


@pytest.fixture
def api_client() -> Generator[tuple[TestClient, sessionmaker[Session]]]:
    engine = create_engine(
        "sqlite+pysqlite:///:memory:",
        connect_args={"check_same_thread": False},
        poolclass=StaticPool,
    )
    TestingSessionLocal = sessionmaker(
        autocommit=False,
        autoflush=False,
        bind=engine,
    )
    Base.metadata.create_all(bind=engine)

    def override_get_db() -> Generator[Session]:
        with TestingSessionLocal() as session:
            yield session

    app.dependency_overrides[get_db] = override_get_db

    with TestClient(app) as client:
        yield client, TestingSessionLocal

    app.dependency_overrides.clear()
    Base.metadata.drop_all(bind=engine)


@pytest.fixture
def api_denominations(
    api_client,
) -> dict[str, Denomination]:
    _, testing_session_local = api_client
    denominations = {
        "coin_025": Denomination(
            type="coin",
            value=Decimal("0.25"),
            label="Moneda de 25 centavos",
            is_active=True,
        ),
        "coin_100": Denomination(
            type="coin",
            value=Decimal("1.00"),
            label="Moneda de 1 dolar",
            is_active=True,
        ),
        "bill_1000": Denomination(
            type="bill",
            value=Decimal("10.00"),
            label="Billete de 10 dolares",
            is_active=True,
        ),
        "bill_2000": Denomination(
            type="bill",
            value=Decimal("20.00"),
            label="Billete de 20 dolares",
            is_active=True,
        ),
    }

    with testing_session_local() as session:
        session.add_all(denominations.values())
        session.commit()
        for denomination in denominations.values():
            session.refresh(denomination)

    return denominations
