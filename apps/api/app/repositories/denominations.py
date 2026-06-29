from sqlalchemy.orm import Session

from app.models.denomination import Denomination


def get_denomination(db: Session, denomination_id: int) -> Denomination | None:
    return db.get(Denomination, denomination_id)
