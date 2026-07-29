from datetime import date, datetime

from sqlalchemy.orm import Session

from app.models.sale_date_correction import SaleDateCorrection


def create_sale_date_correction(
    db: Session,
    *,
    sale_id: int,
    previous_sale_date: date,
    new_sale_date: date,
    reason: str,
    created_by: int,
    created_at: datetime,
) -> SaleDateCorrection:
    correction = SaleDateCorrection(
        sale_id=sale_id,
        correction_type="date_change",
        previous_sale_date=previous_sale_date,
        new_sale_date=new_sale_date,
        reason=reason,
        created_by=created_by,
        created_at=created_at,
    )
    db.add(correction)
    return correction
