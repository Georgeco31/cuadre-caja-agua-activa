from datetime import date

from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.orm import Session

from app.api.deps import get_current_user, get_db
from app.models.user import User
from app.schemas.production import (
    ProductionBatchCreate,
    ProductionBatchRead,
    ProductionBatchVoid,
    ProductionStatus,
)
from app.schemas.production_inventory import (
    ProductionInventoryApplicationRead,
    ProductionInventoryApplicationVoid,
    ProductionInventoryApply,
)
from app.services import production as production_service
from app.services import production_inventory as production_inventory_service

router = APIRouter(
    prefix="/production",
    tags=["production"],
    dependencies=[Depends(get_current_user)],
)


@router.post(
    "/batches",
    response_model=ProductionBatchRead,
    status_code=status.HTTP_201_CREATED,
)
def create_production_batch(
    payload: ProductionBatchCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    try:
        return production_service.create_production_batch(
            db,
            payload,
            current_user.id,
        )
    except ValueError as error:
        raise _http_error(error) from error


@router.get("/batches", response_model=list[ProductionBatchRead])
def list_production_batches(
    date_from: date | None = None,
    date_to: date | None = None,
    production_status: ProductionStatus | None = Query(default=None, alias="status"),
    product_id: int | None = Query(default=None, gt=0),
    search: str | None = None,
    db: Session = Depends(get_db),
):
    try:
        return production_service.list_production_batches(
            db=db,
            date_from=date_from,
            date_to=date_to,
            status=production_status,
            product_id=product_id,
            search=search,
        )
    except ValueError as error:
        raise _http_error(error) from error


@router.get("/batches/{batch_id}", response_model=ProductionBatchRead)
def get_production_batch(batch_id: int, db: Session = Depends(get_db)):
    try:
        return production_service.get_production_batch(db, batch_id)
    except ValueError as error:
        raise _http_error(error) from error


@router.post("/batches/{batch_id}/void", response_model=ProductionBatchRead)
def void_production_batch(
    batch_id: int,
    payload: ProductionBatchVoid,
    db: Session = Depends(get_db),
):
    try:
        return production_service.void_production_batch(
            db,
            batch_id,
            payload.reason,
        )
    except ValueError as error:
        raise _http_error(error) from error


@router.post(
    "/batches/{batch_id}/apply-inventory",
    response_model=ProductionInventoryApplicationRead,
    status_code=status.HTTP_201_CREATED,
)
def apply_production_to_inventory(
    batch_id: int,
    payload: ProductionInventoryApply,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    try:
        return production_inventory_service.apply_production_to_inventory(
            db,
            batch_id,
            payload,
            current_user.id,
        )
    except ValueError as error:
        raise _http_error(error) from error


@router.get(
    "/batches/{batch_id}/inventory-application",
    response_model=ProductionInventoryApplicationRead,
)
def get_production_inventory_application(
    batch_id: int,
    db: Session = Depends(get_db),
):
    try:
        return production_inventory_service.get_inventory_application(db, batch_id)
    except ValueError as error:
        raise _http_error(error) from error


@router.post(
    "/inventory-applications/{application_id}/void",
    response_model=ProductionInventoryApplicationRead,
)
def void_production_inventory_application(
    application_id: int,
    payload: ProductionInventoryApplicationVoid,
    db: Session = Depends(get_db),
):
    try:
        return production_inventory_service.void_inventory_application(
            db,
            application_id,
            payload.reason,
        )
    except ValueError as error:
        raise _http_error(error) from error


def _http_error(error: ValueError) -> HTTPException:
    detail = str(error)
    if (
        "ya esta anulada" in detail
        or "ya tiene una aplicacion activa" in detail
        or "Primero anule" in detail
        or "Anule la aplicacion" in detail
    ):
        return HTTPException(status_code=status.HTTP_409_CONFLICT, detail=detail)
    if "no existe" in detail:
        return HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=detail)
    return HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=detail)
