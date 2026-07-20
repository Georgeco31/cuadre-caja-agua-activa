from __future__ import annotations

from datetime import date, datetime
from decimal import Decimal

from sqlalchemy import (
    CheckConstraint,
    Date,
    DateTime,
    ForeignKey,
    Numeric,
    String,
    Text,
    func,
)
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.base import Base


class CreditPayment(Base):
    __tablename__ = "credit_payments"
    __table_args__ = (
        CheckConstraint(
            "amount > 0",
            name="ck_credit_payments_amount_positive",
        ),
        CheckConstraint(
            "payment_method IN ('cash', 'transfer', 'card', 'other')",
            name="ck_credit_payments_payment_method",
        ),
        CheckConstraint(
            "status IN ('active', 'voided')",
            name="ck_credit_payments_status",
        ),
        CheckConstraint(
            "(status = 'active' AND void_reason IS NULL AND voided_at IS NULL) OR "
            "(status = 'voided' AND length(trim(void_reason)) > 0 "
            "AND voided_at IS NOT NULL)",
            name="ck_credit_payments_void_state",
        ),
    )

    id: Mapped[int] = mapped_column(primary_key=True)
    sale_id: Mapped[int] = mapped_column(
        ForeignKey("sales.id"),
        nullable=False,
        index=True,
    )
    customer_id: Mapped[int] = mapped_column(
        ForeignKey("customers.id"),
        nullable=False,
        index=True,
    )
    route_load_id: Mapped[int | None] = mapped_column(
        ForeignKey("route_loads.id"),
        index=True,
    )
    payment_date: Mapped[date] = mapped_column(Date, nullable=False, index=True)
    amount: Mapped[Decimal] = mapped_column(Numeric(14, 2), nullable=False)
    payment_method: Mapped[str] = mapped_column(String(20), nullable=False)
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

    sale: Mapped["Sale"] = relationship("Sale", back_populates="payments")
    customer: Mapped["Customer"] = relationship("Customer")
    route_load: Mapped["RouteLoad | None"] = relationship("RouteLoad")
    creator: Mapped["User"] = relationship("User")

    @property
    def sale_number(self) -> str:
        return self.sale.sale_number

    @property
    def customer_name(self) -> str:
        return self.sale.customer_name_snapshot

    @property
    def sale_paid_amount(self) -> Decimal:
        return self.sale.paid_amount

    @property
    def sale_balance_amount(self) -> Decimal:
        return self.sale.balance_amount

    @property
    def sale_credit_status(self) -> str:
        return self.sale.credit_status

    @property
    def route_load_number(self) -> str | None:
        return self.route_load.load_number if self.route_load is not None else None

    @property
    def route_name(self) -> str | None:
        return self.route_load.route_name if self.route_load is not None else None

    @property
    def route_vehicle_name(self) -> str | None:
        return self.route_load.vehicle_name if self.route_load is not None else None

    @property
    def route_load_status(self) -> str | None:
        return self.route_load.status if self.route_load is not None else None
