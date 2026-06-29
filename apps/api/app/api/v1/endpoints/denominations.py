from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.api.deps import get_db
from app.repositories.denominations import list_denominations
from app.schemas.denomination import DenominationRead

router = APIRouter(prefix="/denominations", tags=["denominations"])


@router.get("", response_model=list[DenominationRead])
def get_denominations(db: Session = Depends(get_db)):
    return list_denominations(db)
