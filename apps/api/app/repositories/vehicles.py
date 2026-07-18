from sqlalchemy import func, or_, select
from sqlalchemy.orm import Session

from app.models.vehicle import Vehicle


def get_vehicle(db: Session, vehicle_id: int) -> Vehicle | None:
    return db.get(Vehicle, vehicle_id)


def get_vehicle_by_code(
    db: Session,
    code: str,
    exclude_vehicle_id: int | None = None,
) -> Vehicle | None:
    statement = select(Vehicle).where(Vehicle.code == code)
    if exclude_vehicle_id is not None:
        statement = statement.where(Vehicle.id != exclude_vehicle_id)
    return db.scalar(statement)


def get_vehicle_by_plate(
    db: Session,
    plate: str,
    exclude_vehicle_id: int | None = None,
) -> Vehicle | None:
    statement = select(Vehicle).where(Vehicle.plate == plate)
    if exclude_vehicle_id is not None:
        statement = statement.where(Vehicle.id != exclude_vehicle_id)
    return db.scalar(statement)


def list_vehicles(
    db: Session,
    search: str | None = None,
    is_active: bool | None = None,
    vehicle_type: str | None = None,
    fuel_type: str | None = None,
) -> list[Vehicle]:
    statement = select(Vehicle)

    if search is not None:
        search_pattern = f"%{search}%"
        statement = statement.where(
            or_(
                Vehicle.name.ilike(search_pattern),
                Vehicle.plate.ilike(search_pattern),
                Vehicle.code.ilike(search_pattern),
                Vehicle.vehicle_type.ilike(search_pattern),
                Vehicle.brand.ilike(search_pattern),
                Vehicle.model.ilike(search_pattern),
            )
        )
    if is_active is not None:
        statement = statement.where(Vehicle.is_active == is_active)
    if vehicle_type is not None:
        statement = statement.where(Vehicle.vehicle_type == vehicle_type)
    if fuel_type is not None:
        statement = statement.where(Vehicle.fuel_type == fuel_type)

    statement = statement.order_by(func.lower(Vehicle.name), Vehicle.id)
    return list(db.scalars(statement))


def create_vehicle(db: Session, values: dict[str, object]) -> Vehicle:
    vehicle = Vehicle(**values)
    db.add(vehicle)
    return vehicle


def update_vehicle(
    db: Session,
    vehicle: Vehicle,
    values: dict[str, object],
) -> Vehicle:
    for field_name, value in values.items():
        setattr(vehicle, field_name, value)
    db.add(vehicle)
    return vehicle


def set_vehicle_active(
    db: Session,
    vehicle: Vehicle,
    is_active: bool,
) -> Vehicle:
    vehicle.is_active = is_active
    db.add(vehicle)
    return vehicle
