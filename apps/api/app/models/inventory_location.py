from __future__ import annotations

from datetime import datetime

from sqlalchemy import (
    Boolean,
    CheckConstraint,
    DateTime,
    ForeignKey,
    String,
    Text,
    func,
    true,
)
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.base import Base


class InventoryLocation(Base):
    __tablename__ = "inventory_locations"
    __table_args__ = (
        CheckConstraint(
            "length(trim(name)) > 0",
            name="ck_inventory_locations_name_not_blank",
        ),
        CheckConstraint(
            "location_type IN ('warehouse', 'vehicle', 'production_area', 'other')",
            name="ck_inventory_locations_type",
        ),
    )

    id: Mapped[int] = mapped_column(primary_key=True)
    code: Mapped[str | None] = mapped_column(String(80), unique=True)
    name: Mapped[str] = mapped_column(String(255), nullable=False)
    location_type: Mapped[str] = mapped_column(
        String(30),
        nullable=False,
        server_default="warehouse",
    )
    vehicle_id: Mapped[int | None] = mapped_column(ForeignKey("vehicles.id"))
    description: Mapped[str | None] = mapped_column(Text)
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

    vehicle: Mapped["Vehicle | None"] = relationship("Vehicle")

