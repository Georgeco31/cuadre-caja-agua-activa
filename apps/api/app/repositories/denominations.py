from sqlalchemy.orm import Session

from app.models.denomination import Denomination


def get_denomination(db: Session, denomination_id: int) -> Denomination | None:
    return db.get(Denomination, denomination_id)


def list_denominations(db: Session, active_only: bool = True) -> list[Denomination]:
    query = db.query(Denomination).order_by(Denomination.type, Denomination.value)
    if active_only:
        query = query.filter(Denomination.is_active.is_(True))
    return list(query)
