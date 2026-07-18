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


class Sale(Base):
    __tablename__ = "sales"
    __table_args__ = (
        CheckConstraint(
            "length(trim(sale_number)) > 0",
            name="ck_sales_sale_number_not_blank",
        ),
        CheckConstraint(
            "length(trim(customer_name_snapshot)) > 0",
            name="ck_sales_customer_snapshot_not_blank",
        ),
        CheckConstraint(
            "sale_type = 'cash'",
            name="ck_sales_sale_type",
        ),
        CheckConstraint(
            "payment_method IN ('cash', 'transfer', 'card', 'other')",
            name="ck_sales_payment_method",
        ),
        CheckConstraint(
            "status IN ('active', 'voided')",
            name="ck_sales_status",
        ),
        CheckConstraint(
            "total_amount >= 0",
            name="ck_sales_total_amount_nonnegative",
        ),
    )

    id: Mapped[int] = mapped_column(primary_key=True)
    sale_number: Mapped[str] = mapped_column(
        String(50),
        unique=True,
        nullable=False,
    )
    sale_date: Mapped[date] = mapped_column(Date, nullable=False)
    customer_id: Mapped[int | None] = mapped_column(ForeignKey("customers.id"))
    customer_name_snapshot: Mapped[str] = mapped_column(String(255), nullable=False)
    sale_type: Mapped[str] = mapped_column(
        String(20),
        nullable=False,
        server_default="cash",
    )
    payment_method: Mapped[str] = mapped_column(
        String(20),
        nullable=False,
        server_default="cash",
    )
    status: Mapped[str] = mapped_column(
        String(20),
        nullable=False,
        server_default="active",
    )
    total_amount: Mapped[Decimal] = mapped_column(Numeric(14, 2), nullable=False)
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

    customer: Mapped["Customer | None"] = relationship("Customer")
    creator: Mapped["User"] = relationship("User")
    items: Mapped[list["SaleItem"]] = relationship(
        "SaleItem",
        back_populates="sale",
        cascade="all, delete-orphan",
        order_by="SaleItem.id",
    )
