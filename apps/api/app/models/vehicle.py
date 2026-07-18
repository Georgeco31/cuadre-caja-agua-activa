from datetime import datetime

from sqlalchemy import (
    Boolean,
    CheckConstraint,
    DateTime,
    Integer,
    String,
    Text,
    func,
    true,
)
from sqlalchemy.orm import Mapped, mapped_column

from app.db.base import Base


class Vehicle(Base):
    __tablename__ = "vehicles"
    __table_args__ = (
        CheckConstraint(
            "length(trim(name)) > 0",
            name="ck_vehicles_name_not_blank",
        ),
        CheckConstraint(
            "vehicle_type IN ('truck', 'van', 'motorcycle', 'car', 'other')",
            name="ck_vehicles_vehicle_type",
        ),
        CheckConstraint(
            "fuel_type IN ('gasoline', 'diesel', 'electric', 'hybrid', 'other')",
            name="ck_vehicles_fuel_type",
        ),
        CheckConstraint(
            "year IS NULL OR (year >= 1900 AND year <= 2100)",
            name="ck_vehicles_year_reasonable",
        ),
    )

    id: Mapped[int] = mapped_column(primary_key=True)
    code: Mapped[str | None] = mapped_column(String(80), unique=True)
    name: Mapped[str] = mapped_column(String(255), nullable=False)
    plate: Mapped[str | None] = mapped_column(String(50), unique=True)
    vehicle_type: Mapped[str] = mapped_column(
        String(20),
        nullable=False,
        server_default="other",
    )
    brand: Mapped[str | None] = mapped_column(String(120))
    model: Mapped[str | None] = mapped_column(String(120))
    year: Mapped[int | None] = mapped_column(Integer)
    color: Mapped[str | None] = mapped_column(String(80))
    fuel_type: Mapped[str] = mapped_column(
        String(20),
        nullable=False,
        server_default="other",
    )
    capacity_reference: Mapped[str | None] = mapped_column(String(255))
    reference_driver: Mapped[str | None] = mapped_column(String(255))
    is_active: Mapped[bool] = mapped_column(
        Boolean,
        nullable=False,
        server_default=true(),
    )
    notes: Mapped[str | None] = mapped_column(Text)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        nullable=False,
        server_default=func.now(),
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        nullable=False,
        server_default=func.now(),
        onupdate=func.now(),
    )
