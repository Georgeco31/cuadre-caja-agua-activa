from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.api.deps import get_current_user, get_db
from app.schemas.vehicle import (
    FuelType,
    VehicleCreate,
    VehicleRead,
    VehicleType,
    VehicleUpdate,
)
from app.services import vehicles as vehicle_service

router = APIRouter(
    prefix="/vehicles",
    tags=["vehicles"],
    dependencies=[Depends(get_current_user)],
)


@router.post("", response_model=VehicleRead, status_code=status.HTTP_201_CREATED)
def create_vehicle(
    payload: VehicleCreate,
    db: Session = Depends(get_db),
):
    try:
        return vehicle_service.create_vehicle(db, payload)
    except ValueError as error:
        raise _http_error(error) from error


@router.get("", response_model=list[VehicleRead])
def list_vehicles(
    search: str | None = None,
    is_active: bool | None = None,
    vehicle_type: VehicleType | None = None,
    fuel_type: FuelType | None = None,
    db: Session = Depends(get_db),
):
    return vehicle_service.list_vehicles(
        db=db,
        search=search,
        is_active=is_active,
        vehicle_type=vehicle_type,
        fuel_type=fuel_type,
    )


@router.get("/{vehicle_id}", response_model=VehicleRead)
def get_vehicle(vehicle_id: int, db: Session = Depends(get_db)):
    try:
        return vehicle_service.get_vehicle(db, vehicle_id)
    except ValueError as error:
        raise _http_error(error) from error


@router.patch("/{vehicle_id}", response_model=VehicleRead)
def update_vehicle(
    vehicle_id: int,
    payload: VehicleUpdate,
    db: Session = Depends(get_db),
):
    try:
        return vehicle_service.update_vehicle(db, vehicle_id, payload)
    except ValueError as error:
        raise _http_error(error) from error


@router.patch("/{vehicle_id}/deactivate", response_model=VehicleRead)
def deactivate_vehicle(vehicle_id: int, db: Session = Depends(get_db)):
    try:
        return vehicle_service.deactivate_vehicle(db, vehicle_id)
    except ValueError as error:
        raise _http_error(error) from error


@router.patch("/{vehicle_id}/activate", response_model=VehicleRead)
def activate_vehicle(vehicle_id: int, db: Session = Depends(get_db)):
    try:
        return vehicle_service.activate_vehicle(db, vehicle_id)
    except ValueError as error:
        raise _http_error(error) from error


def _http_error(error: ValueError) -> HTTPException:
    detail = str(error)
    if "ya esta registrad" in detail:
        return HTTPException(status_code=status.HTTP_409_CONFLICT, detail=detail)
    if "no existe" in detail:
        return HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=detail)
    return HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=detail)
