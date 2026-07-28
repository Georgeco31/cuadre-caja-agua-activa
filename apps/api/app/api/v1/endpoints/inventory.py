from datetime import date

from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.orm import Session

from app.api.deps import (
    ensure_admin_auditor,
    get_current_user,
    get_db,
    require_admin_auditor,
)
from app.models.user import User
from app.schemas.inventory import (
    InventoryLocationCreate,
    InventoryLocationRead,
    InventoryLocationType,
    InventoryLocationUpdate,
    InventoryMovementCreate,
    InventoryMovementRead,
    InventoryMovementStatus,
    InventoryMovementType,
    InventoryMovementVoid,
    InventoryStockRead,
)
from app.services import inventory as inventory_service

router = APIRouter(
    prefix="/inventory",
    tags=["inventory"],
    dependencies=[Depends(get_current_user)],
)


@router.post(
    "/locations",
    response_model=InventoryLocationRead,
    status_code=status.HTTP_201_CREATED,
    dependencies=[Depends(require_admin_auditor)],
)
def create_location(
    payload: InventoryLocationCreate,
    db: Session = Depends(get_db),
):
    try:
        return inventory_service.create_location(db, payload)
    except ValueError as error:
        raise _http_error(error) from error


@router.get("/locations", response_model=list[InventoryLocationRead])
def list_locations(
    search: str | None = None,
    is_active: bool | None = None,
    location_type: InventoryLocationType | None = None,
    db: Session = Depends(get_db),
):
    return inventory_service.list_locations(
        db=db,
        search=search,
        is_active=is_active,
        location_type=location_type,
    )


@router.get(
    "/locations/{location_id}",
    response_model=InventoryLocationRead,
)
def get_location(location_id: int, db: Session = Depends(get_db)):
    try:
        return inventory_service.get_location(db, location_id)
    except ValueError as error:
        raise _http_error(error) from error


@router.patch(
    "/locations/{location_id}",
    response_model=InventoryLocationRead,
    dependencies=[Depends(require_admin_auditor)],
)
def update_location(
    location_id: int,
    payload: InventoryLocationUpdate,
    db: Session = Depends(get_db),
):
    try:
        return inventory_service.update_location(db, location_id, payload)
    except ValueError as error:
        raise _http_error(error) from error


@router.patch(
    "/locations/{location_id}/deactivate",
    response_model=InventoryLocationRead,
    dependencies=[Depends(require_admin_auditor)],
)
def deactivate_location(location_id: int, db: Session = Depends(get_db)):
    try:
        return inventory_service.deactivate_location(db, location_id)
    except ValueError as error:
        raise _http_error(error) from error


@router.patch(
    "/locations/{location_id}/activate",
    response_model=InventoryLocationRead,
    dependencies=[Depends(require_admin_auditor)],
)
def activate_location(location_id: int, db: Session = Depends(get_db)):
    try:
        return inventory_service.activate_location(db, location_id)
    except ValueError as error:
        raise _http_error(error) from error


@router.get("/stocks", response_model=list[InventoryStockRead])
def list_stocks(
    product_id: int | None = None,
    location_id: int | None = None,
    only_positive: bool = False,
    db: Session = Depends(get_db),
):
    return inventory_service.list_stocks(
        db=db,
        product_id=product_id,
        location_id=location_id,
        only_positive=only_positive,
    )


@router.post(
    "/movements",
    response_model=InventoryMovementRead,
    status_code=status.HTTP_201_CREATED,
)
def create_movement(
    payload: InventoryMovementCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    try:
        if (
            payload.movement_type in {"adjustment_in", "adjustment_out"}
            or payload.unit_cost is not None
        ):
            ensure_admin_auditor(current_user)
        return inventory_service.create_movement(
            db,
            payload,
            current_user.id,
        )
    except ValueError as error:
        raise _http_error(error) from error


@router.get("/movements", response_model=list[InventoryMovementRead])
def list_movements(
    date_from: date | None = None,
    date_to: date | None = None,
    product_id: int | None = None,
    location_id: int | None = None,
    movement_type: InventoryMovementType | None = None,
    movement_status: InventoryMovementStatus | None = Query(
        default=None,
        alias="status",
    ),
    db: Session = Depends(get_db),
):
    try:
        return inventory_service.list_movements(
            db=db,
            date_from=date_from,
            date_to=date_to,
            product_id=product_id,
            location_id=location_id,
            movement_type=movement_type,
            status=movement_status,
        )
    except ValueError as error:
        raise _http_error(error) from error


@router.get(
    "/movements/{movement_id}",
    response_model=InventoryMovementRead,
)
def get_movement(movement_id: int, db: Session = Depends(get_db)):
    try:
        return inventory_service.get_movement(db, movement_id)
    except ValueError as error:
        raise _http_error(error) from error


@router.post(
    "/movements/{movement_id}/void",
    response_model=InventoryMovementRead,
    dependencies=[Depends(require_admin_auditor)],
)
def void_movement(
    movement_id: int,
    payload: InventoryMovementVoid,
    db: Session = Depends(get_db),
):
    try:
        return inventory_service.void_movement(db, movement_id, payload.reason)
    except ValueError as error:
        raise _http_error(error) from error


def _http_error(error: ValueError) -> HTTPException:
    detail = str(error)
    if "no existe" in detail:
        return HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=detail)
    if "ya esta registrado" in detail or "ya esta anulado" in detail:
        return HTTPException(status_code=status.HTTP_409_CONFLICT, detail=detail)
    return HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=detail)
