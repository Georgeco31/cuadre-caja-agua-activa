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


class Purchase(Base):
    __tablename__ = "purchases"
    __table_args__ = (
        CheckConstraint(
            "length(trim(purchase_number)) > 0",
            name="ck_purchases_number_not_blank",
        ),
        CheckConstraint(
            "status IN ('active', 'voided')",
            name="ck_purchases_status",
        ),
        CheckConstraint(
            "payment_status IN ('unpaid', 'partial', 'paid')",
            name="ck_purchases_payment_status",
        ),
        CheckConstraint(
            "subtotal_amount >= 0 AND discount_amount >= 0 "
            "AND tax_amount >= 0 AND total_amount >= 0",
            name="ck_purchases_amounts_nonnegative",
        ),
        CheckConstraint(
            "total_amount = subtotal_amount + tax_amount",
            name="ck_purchases_total",
        ),
        CheckConstraint(
            "(status = 'active' AND void_reason IS NULL AND voided_at IS NULL) OR "
            "(status = 'voided' AND length(trim(void_reason)) > 0 "
            "AND voided_at IS NOT NULL)",
            name="ck_purchases_void_state",
        ),
    )

    id: Mapped[int] = mapped_column(primary_key=True)
    purchase_number: Mapped[str] = mapped_column(
        String(80),
        nullable=False,
        unique=True,
        index=True,
    )
    supplier_id: Mapped[int] = mapped_column(
        ForeignKey("suppliers.id"),
        nullable=False,
        index=True,
    )
    purchase_date: Mapped[date] = mapped_column(Date, nullable=False, index=True)
    document_number: Mapped[str | None] = mapped_column(String(120), index=True)
    document_type: Mapped[str | None] = mapped_column(String(50))
    status: Mapped[str] = mapped_column(
        String(20),
        nullable=False,
        server_default="active",
        index=True,
    )
    payment_status: Mapped[str] = mapped_column(
        String(20),
        nullable=False,
        server_default="unpaid",
        index=True,
    )
    subtotal_amount: Mapped[Decimal] = mapped_column(
        Numeric(14, 2),
        nullable=False,
    )
    discount_amount: Mapped[Decimal] = mapped_column(
        Numeric(14, 2),
        nullable=False,
    )
    tax_amount: Mapped[Decimal] = mapped_column(Numeric(14, 2), nullable=False)
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

    supplier: Mapped["Supplier"] = relationship(
        "Supplier",
        back_populates="purchases",
    )
    creator: Mapped["User"] = relationship("User")
    items: Mapped[list["PurchaseItem"]] = relationship(
        "PurchaseItem",
        back_populates="purchase",
        cascade="all, delete-orphan",
        order_by="PurchaseItem.id",
    )
