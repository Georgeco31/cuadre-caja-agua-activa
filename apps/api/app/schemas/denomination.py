from decimal import Decimal

from pydantic import BaseModel, ConfigDict


class DenominationRead(BaseModel):
    id: int
    type: str
    value: Decimal
    label: str
    is_active: bool

    model_config = ConfigDict(from_attributes=True)
