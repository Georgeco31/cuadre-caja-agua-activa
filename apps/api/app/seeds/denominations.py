from decimal import Decimal

from sqlalchemy import select
from sqlalchemy.orm import Session

from app.models.denomination import Denomination


INITIAL_DENOMINATIONS = (
    {"type": "coin", "value": Decimal("0.01"), "label": "Moneda de 1 centavo"},
    {"type": "coin", "value": Decimal("0.05"), "label": "Moneda de 5 centavos"},
    {"type": "coin", "value": Decimal("0.10"), "label": "Moneda de 10 centavos"},
    {"type": "coin", "value": Decimal("0.25"), "label": "Moneda de 25 centavos"},
    {"type": "coin", "value": Decimal("0.50"), "label": "Moneda de 50 centavos"},
    {"type": "coin", "value": Decimal("1.00"), "label": "Moneda de 1 dolar"},
    {"type": "bill", "value": Decimal("1.00"), "label": "Billete de 1 dolar"},
    {"type": "bill", "value": Decimal("5.00"), "label": "Billete de 5 dolares"},
    {"type": "bill", "value": Decimal("10.00"), "label": "Billete de 10 dolares"},
    {"type": "bill", "value": Decimal("20.00"), "label": "Billete de 20 dolares"},
    {"type": "bill", "value": Decimal("50.00"), "label": "Billete de 50 dolares"},
    {"type": "bill", "value": Decimal("100.00"), "label": "Billete de 100 dolares"},
)


def seed_denominations(db: Session) -> list[Denomination]:
    denominations: list[Denomination] = []

    for item in INITIAL_DENOMINATIONS:
        denomination = _get_denomination_by_type_and_value(
            db=db,
            denomination_type=str(item["type"]),
            value=item["value"],
        )
        if denomination is None:
            denomination = Denomination(
                type=str(item["type"]),
                value=item["value"],
                label=str(item["label"]),
                is_active=True,
            )
            db.add(denomination)
        else:
            denomination.label = str(item["label"])
            denomination.is_active = True

        denominations.append(denomination)

    db.commit()
    for denomination in denominations:
        db.refresh(denomination)

    return denominations


def _get_denomination_by_type_and_value(
    db: Session,
    denomination_type: str,
    value: Decimal,
) -> Denomination | None:
    statement = select(Denomination).where(
        Denomination.type == denomination_type,
        Denomination.value == value,
    )
    return db.scalar(statement)
