from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session

from app.models.vehicle import Vehicle
from app.repositories import vehicles
from app.schemas.vehicle import VehicleCreate, VehicleUpdate


def create_vehicle(db: Session, payload: VehicleCreate) -> Vehicle:
    if payload.code is not None:
        _ensure_code_is_available(db, payload.code)
    if payload.plate is not None:
        _ensure_plate_is_available(db, payload.plate)

    vehicle = vehicles.create_vehicle(db, payload.model_dump())
    _commit_vehicle(db, vehicle)
    return vehicle


def list_vehicles(
    db: Session,
    search: str | None = None,
    is_active: bool | None = None,
    vehicle_type: str | None = None,
    fuel_type: str | None = None,
) -> list[Vehicle]:
    return vehicles.list_vehicles(
        db=db,
        search=_normalize_filter(search),
        is_active=is_active,
        vehicle_type=vehicle_type,
        fuel_type=fuel_type,
    )


def get_vehicle(db: Session, vehicle_id: int) -> Vehicle:
    vehicle = vehicles.get_vehicle(db, vehicle_id)
    if vehicle is None:
        raise ValueError("El vehiculo no existe.")
    return vehicle


def update_vehicle(
    db: Session,
    vehicle_id: int,
    payload: VehicleUpdate,
) -> Vehicle:
    vehicle = get_vehicle(db, vehicle_id)
    values = payload.model_dump(exclude_unset=True)

    if "code" in values and values["code"] is not None:
        _ensure_code_is_available(
            db,
            str(values["code"]),
            exclude_vehicle_id=vehicle.id,
        )
    if "plate" in values and values["plate"] is not None:
        _ensure_plate_is_available(
            db,
            str(values["plate"]),
            exclude_vehicle_id=vehicle.id,
        )

    vehicles.update_vehicle(db, vehicle, values)
    _commit_vehicle(db, vehicle)
    return vehicle


def deactivate_vehicle(db: Session, vehicle_id: int) -> Vehicle:
    vehicle = get_vehicle(db, vehicle_id)
    vehicles.set_vehicle_active(db, vehicle, False)
    _commit_vehicle(db, vehicle)
    return vehicle


def activate_vehicle(db: Session, vehicle_id: int) -> Vehicle:
    vehicle = get_vehicle(db, vehicle_id)
    vehicles.set_vehicle_active(db, vehicle, True)
    _commit_vehicle(db, vehicle)
    return vehicle


def _ensure_code_is_available(
    db: Session,
    code: str,
    exclude_vehicle_id: int | None = None,
) -> None:
    existing_vehicle = vehicles.get_vehicle_by_code(
        db,
        code,
        exclude_vehicle_id=exclude_vehicle_id,
    )
    if existing_vehicle is not None:
        raise ValueError("El codigo del vehiculo ya esta registrado.")


def _ensure_plate_is_available(
    db: Session,
    plate: str,
    exclude_vehicle_id: int | None = None,
) -> None:
    existing_vehicle = vehicles.get_vehicle_by_plate(
        db,
        plate,
        exclude_vehicle_id=exclude_vehicle_id,
    )
    if existing_vehicle is not None:
        raise ValueError("La placa del vehiculo ya esta registrada.")


def _commit_vehicle(db: Session, vehicle: Vehicle) -> None:
    try:
        db.commit()
    except IntegrityError as error:
        db.rollback()
        raise ValueError("El codigo o la placa del vehiculo ya esta registrado.") from error
    db.refresh(vehicle)


def _normalize_filter(value: str | None) -> str | None:
    if value is None:
        return None
    normalized_value = value.strip()
    return normalized_value or None
