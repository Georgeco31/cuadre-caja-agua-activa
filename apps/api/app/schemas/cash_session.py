from datetime import date, datetime

from pydantic import BaseModel, ConfigDict


class CashSessionCreate(BaseModel):
    session_date: date
    created_by: int | None = None
    notes: str | None = None


class CashSessionRead(BaseModel):
    id: int
    session_date: date
    status: str
    notes: str | None
    created_by: int | None
    created_at: datetime
    updated_at: datetime
    closed_at: datetime | None

    model_config = ConfigDict(from_attributes=True)
