from datetime import date

from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.orm import Session

from app.api.deps import get_current_user, get_db, require_admin_auditor
from app.models.user import User
from app.schemas.production_material_consumption import (
    ProductionBatchMaterialConsumptionRead,
    ProductionMaterialConsumptionCreate,
    ProductionMaterialConsumptionPreview,
    ProductionMaterialConsumptionPreviewRequest,
    ProductionMaterialConsumptionRead,
    ProductionMaterialConsumptionStatus,
    ProductionMaterialConsumptionVoid,
)
from app.services import production_material_consumptions as consumption_service

router = APIRouter(
    prefix="/production",
    tags=["production-material-consumptions"],
    dependencies=[Depends(get_current_user)],
)


@router.post(
    "/batches/{batch_id}/material-consumption/preview",
    response_model=ProductionMaterialConsumptionPreview,
)
def preview_material_consumption(
    batch_id: int,
    payload: ProductionMaterialConsumptionPreviewRequest,
    db: Session = Depends(get_db),
):
    try:
        return consumption_service.preview_material_consumption(
            db,
            batch_id,
            payload,
        )
    except ValueError as error:
        raise _http_error(error) from error


@router.post(
    "/batches/{batch_id}/material-consumption",
    response_model=ProductionMaterialConsumptionRead,
    status_code=status.HTTP_201_CREATED,
    dependencies=[Depends(require_admin_auditor)],
)
def create_material_consumption(
    batch_id: int,
    payload: ProductionMaterialConsumptionCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    try:
        return consumption_service.create_material_consumption(
            db,
            batch_id,
            payload,
            current_user.id,
        )
    except ValueError as error:
        raise _http_error(error) from error


@router.get(
    "/batches/{batch_id}/material-consumption",
    response_model=ProductionBatchMaterialConsumptionRead,
)
def get_batch_material_consumption(
    batch_id: int,
    db: Session = Depends(get_db),
):
    try:
        return consumption_service.get_batch_material_consumption(db, batch_id)
    except ValueError as error:
        raise _http_error(error) from error


@router.get(
    "/material-consumptions",
    response_model=list[ProductionMaterialConsumptionRead],
)
def list_material_consumptions(
    date_from: date | None = None,
    date_to: date | None = None,
    consumption_status: ProductionMaterialConsumptionStatus | None = Query(
        default=None,
        alias="status",
    ),
    production_batch_id: int | None = Query(default=None, gt=0),
    source_location_id: int | None = Query(default=None, gt=0),
    input_product_id: int | None = Query(default=None, gt=0),
    search: str | None = None,
    db: Session = Depends(get_db),
):
    try:
        return consumption_service.list_material_consumptions(
            db=db,
            date_from=date_from,
            date_to=date_to,
            status=consumption_status,
            production_batch_id=production_batch_id,
            source_location_id=source_location_id,
            input_product_id=input_product_id,
            search=search,
        )
    except ValueError as error:
        raise _http_error(error) from error


@router.get(
    "/material-consumptions/{consumption_id}",
    response_model=ProductionMaterialConsumptionRead,
)
def get_material_consumption(
    consumption_id: int,
    db: Session = Depends(get_db),
):
    try:
        return consumption_service.get_material_consumption(db, consumption_id)
    except ValueError as error:
        raise _http_error(error) from error


@router.post(
    "/material-consumptions/{consumption_id}/void",
    response_model=ProductionMaterialConsumptionRead,
    dependencies=[Depends(require_admin_auditor)],
)
def void_material_consumption(
    consumption_id: int,
    payload: ProductionMaterialConsumptionVoid,
    db: Session = Depends(get_db),
):
    try:
        return consumption_service.void_material_consumption(
            db,
            consumption_id,
            payload.reason,
        )
    except ValueError as error:
        raise _http_error(error) from error


def _http_error(error: ValueError) -> HTTPException:
    detail = str(error)
    if "ya tiene un consumo" in detail or "ya esta anulado" in detail:
        return HTTPException(status_code=status.HTTP_409_CONFLICT, detail=detail)
    if "no existe" in detail:
        return HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=detail)
    return HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=detail)
