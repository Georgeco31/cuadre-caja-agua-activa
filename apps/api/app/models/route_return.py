from __future__ import annotations

from datetime import date, datetime

from sqlalchemy import CheckConstraint, Date, DateTime, ForeignKey, String, Text, func
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.base import Base


class RouteReturn(Base):
    __tablename__ = "route_returns"
    __table_args__ = (
        CheckConstraint(
            "length(trim(return_number)) > 0",
            name="ck_route_returns_number_not_blank",
        ),
        CheckConstraint(
            "source_location_id <> destination_location_id",
            name="ck_route_returns_locations_different",
        ),
        CheckConstraint(
            "status IN ('active', 'voided')",
            name="ck_route_returns_status",
        ),
        CheckConstraint(
            "(status = 'active' AND void_reason IS NULL AND voided_at IS NULL) OR "
            "(status = 'voided' AND length(trim(void_reason)) > 0 "
            "AND voided_at IS NOT NULL)",
            name="ck_route_returns_void_state",
        ),
    )

    id: Mapped[int] = mapped_column(primary_key=True)
    return_number: Mapped[str] = mapped_column(
        String(80),
        nullable=False,
        unique=True,
        index=True,
    )
    return_date: Mapped[date] = mapped_column(Date, nullable=False, index=True)
    route_load_id: Mapped[int] = mapped_column(
        ForeignKey("route_loads.id"),
        nullable=False,
        index=True,
    )
    route_id: Mapped[int] = mapped_column(
        ForeignKey("delivery_routes.id"),
        nullable=False,
        index=True,
    )
    vehicle_id: Mapped[int] = mapped_column(
        ForeignKey("vehicles.id"),
        nullable=False,
        index=True,
    )
    source_location_id: Mapped[int] = mapped_column(
        ForeignKey("inventory_locations.id"),
        nullable=False,
        index=True,
    )
    destination_location_id: Mapped[int] = mapped_column(
        ForeignKey("inventory_locations.id"),
        nullable=False,
        index=True,
    )
    status: Mapped[str] = mapped_column(
        String(20),
        nullable=False,
        server_default="active",
        index=True,
    )
    notes: Mapped[str | None] = mapped_column(Text)
    void_reason: Mapped[str | None] = mapped_column(Text)
    voided_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True))
    created_by: Mapped[int] = mapped_column(ForeignKey("users.id"), nullable=False)
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

    route_load: Mapped["RouteLoad"] = relationship("RouteLoad")
    delivery_route: Mapped["DeliveryRoute"] = relationship("DeliveryRoute")
    vehicle: Mapped["Vehicle"] = relationship("Vehicle")
    source_location: Mapped["InventoryLocation"] = relationship(
        "InventoryLocation",
        foreign_keys=[source_location_id],
    )
    destination_location: Mapped["InventoryLocation"] = relationship(
        "InventoryLocation",
        foreign_keys=[destination_location_id],
    )
    creator: Mapped["User"] = relationship("User")
    items: Mapped[list["RouteReturnItem"]] = relationship(
        "RouteReturnItem",
        back_populates="route_return",
        cascade="all, delete-orphan",
        order_by="RouteReturnItem.id",
    )

    @property
    def route_load_number(self) -> str:
        return self.route_load.load_number

    @property
    def route_load_status(self) -> str:
        return self.route_load.status

    @property
    def route_name(self) -> str:
        return self.delivery_route.name

    @property
    def vehicle_name(self) -> str:
        return self.vehicle.name

    @property
    def source_location_name(self) -> str:
        return self.source_location.name

    @property
    def destination_location_name(self) -> str:
        return self.destination_location.name
