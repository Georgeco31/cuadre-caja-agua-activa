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


class RouteCashReceipt(Base):
    __tablename__ = "route_cash_receipts"
    __table_args__ = (
        CheckConstraint(
            "length(trim(receipt_number)) > 0",
            name="ck_route_cash_receipts_number_not_blank",
        ),
        CheckConstraint(
            "length(trim(closure_number_snapshot)) > 0",
            name="ck_route_cash_receipts_closure_snapshot_not_blank",
        ),
        CheckConstraint(
            "length(trim(route_name_snapshot)) > 0",
            name="ck_route_cash_receipts_route_snapshot_not_blank",
        ),
        CheckConstraint(
            "length(trim(vehicle_name_snapshot)) > 0",
            name="ck_route_cash_receipts_vehicle_snapshot_not_blank",
        ),
        CheckConstraint(
            "delivered_cash_total >= 0 AND received_amount >= 0",
            name="ck_route_cash_receipts_amounts_nonnegative",
        ),
        CheckConstraint(
            "difference_amount = received_amount - delivered_cash_total",
            name="ck_route_cash_receipts_difference",
        ),
        CheckConstraint(
            "status IN ('active', 'voided')",
            name="ck_route_cash_receipts_status",
        ),
        CheckConstraint(
            "(status = 'active' AND void_reason IS NULL AND voided_at IS NULL) OR "
            "(status = 'voided' AND length(trim(void_reason)) > 0 "
            "AND voided_at IS NOT NULL)",
            name="ck_route_cash_receipts_void_state",
        ),
        Index(
            "uq_route_cash_receipts_active_closure",
            "route_closure_id",
            unique=True,
            postgresql_where=text("status = 'active'"),
            sqlite_where=text("status = 'active'"),
        ),
    )

    id: Mapped[int] = mapped_column(primary_key=True)
    receipt_number: Mapped[str] = mapped_column(
        String(80),
        nullable=False,
        unique=True,
        index=True,
    )
    receipt_date: Mapped[date] = mapped_column(Date, nullable=False, index=True)
    route_closure_id: Mapped[int] = mapped_column(
        ForeignKey("route_closures.id"),
        nullable=False,
        index=True,
    )
    cash_session_id: Mapped[int] = mapped_column(
        ForeignKey("cash_sessions.id"),
        nullable=False,
        index=True,
    )
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
    closure_number_snapshot: Mapped[str] = mapped_column(
        String(80),
        nullable=False,
    )
    route_name_snapshot: Mapped[str] = mapped_column(String(255), nullable=False)
    vehicle_name_snapshot: Mapped[str] = mapped_column(
        String(255),
        nullable=False,
    )
    delivered_cash_total: Mapped[Decimal] = mapped_column(
        Numeric(14, 2),
        nullable=False,
    )
    received_amount: Mapped[Decimal] = mapped_column(
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

    route_closure: Mapped["RouteClosure"] = relationship("RouteClosure")
    cash_session: Mapped["CashSession"] = relationship("CashSession")
    route_load: Mapped["RouteLoad"] = relationship("RouteLoad")
    delivery_route: Mapped["DeliveryRoute"] = relationship("DeliveryRoute")
    vehicle: Mapped["Vehicle"] = relationship("Vehicle")
    creator: Mapped["User"] = relationship("User")
