from __future__ import annotations

from datetime import date, datetime
from decimal import Decimal

from sqlalchemy import (
    CheckConstraint,
    Date,
    DateTime,
    ForeignKey,
    Index,
    Numeric,
    String,
    Text,
    func,
    text,
)
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.base import Base


class RouteClosure(Base):
    __tablename__ = "route_closures"
    __table_args__ = (
        CheckConstraint(
            "length(trim(closure_number)) > 0",
            name="ck_route_closures_number_not_blank",
        ),
        CheckConstraint(
            "length(trim(load_number_snapshot)) > 0",
            name="ck_route_closures_load_snapshot_not_blank",
        ),
        CheckConstraint(
            "length(trim(route_name_snapshot)) > 0",
            name="ck_route_closures_route_snapshot_not_blank",
        ),
        CheckConstraint(
            "length(trim(vehicle_name_snapshot)) > 0",
            name="ck_route_closures_vehicle_snapshot_not_blank",
        ),
        CheckConstraint(
            "cash_sales_total >= 0 AND credit_sales_total >= 0 "
            "AND payments_total >= 0 AND expected_cash_total >= 0 "
            "AND delivered_cash_total >= 0",
            name="ck_route_closures_amounts_nonnegative",
        ),
        CheckConstraint(
            "expected_cash_total = cash_sales_total + payments_total",
            name="ck_route_closures_expected_cash",
        ),
        CheckConstraint(
            "difference_amount = delivered_cash_total - expected_cash_total",
            name="ck_route_closures_difference",
        ),
        CheckConstraint(
            "status IN ('active', 'voided')",
            name="ck_route_closures_status",
        ),
        CheckConstraint(
            "(status = 'active' AND void_reason IS NULL AND voided_at IS NULL) OR "
            "(status = 'voided' AND length(trim(void_reason)) > 0 "
            "AND voided_at IS NOT NULL)",
            name="ck_route_closures_void_state",
        ),
        Index(
            "uq_route_closures_active_route_load",
            "route_load_id",
            unique=True,
            postgresql_where=text("status = 'active'"),
            sqlite_where=text("status = 'active'"),
        ),
    )

    id: Mapped[int] = mapped_column(primary_key=True)
    closure_number: Mapped[str] = mapped_column(
        String(80),
        nullable=False,
        unique=True,
        index=True,
    )
    closure_date: Mapped[date] = mapped_column(Date, nullable=False, index=True)
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
    load_number_snapshot: Mapped[str] = mapped_column(String(80), nullable=False)
    route_name_snapshot: Mapped[str] = mapped_column(String(255), nullable=False)
    vehicle_name_snapshot: Mapped[str] = mapped_column(String(255), nullable=False)
    cash_sales_total: Mapped[Decimal] = mapped_column(
        Numeric(14, 2),
        nullable=False,
    )
    credit_sales_total: Mapped[Decimal] = mapped_column(
        Numeric(14, 2),
        nullable=False,
    )
    payments_total: Mapped[Decimal] = mapped_column(Numeric(14, 2), nullable=False)
    expected_cash_total: Mapped[Decimal] = mapped_column(
        Numeric(14, 2),
        nullable=False,
    )
    delivered_cash_total: Mapped[Decimal] = mapped_column(
        Numeric(14, 2),
        nullable=False,
    )
    difference_amount: Mapped[Decimal] = mapped_column(
        Numeric(14, 2),
        nullable=False,
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
    creator: Mapped["User"] = relationship("User")

    @property
    def route_load_status(self) -> str:
        return self.route_load.status
