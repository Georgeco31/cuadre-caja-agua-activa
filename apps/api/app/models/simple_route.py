from __future__ import annotations

from datetime import date, datetime
from decimal import Decimal

from sqlalchemy import (
    Boolean,
    CheckConstraint,
    Date,
    DateTime,
    ForeignKey,
    Index,
    Integer,
    Numeric,
    String,
    Text,
    UniqueConstraint,
    false,
    func,
)
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.base import Base


class SimpleRouteSheet(Base):
    __tablename__ = "simple_route_sheets"
    __table_args__ = (
        CheckConstraint(
            "length(trim(seller_name)) > 0",
            name="ck_simple_route_sheets_seller_not_blank",
        ),
        CheckConstraint(
            "status IN ('draft', 'in_progress', 'settled', 'cancelled')",
            name="ck_simple_route_sheets_status",
        ),
        CheckConstraint(
            "cash_delivered IS NULL OR cash_delivered >= 0",
            name="ck_simple_route_sheets_cash_nonnegative",
        ),
        CheckConstraint(
            "(cash_received_in_cash_session = false AND cash_session_id IS NULL) "
            "OR (cash_received_in_cash_session = true AND cash_session_id IS NOT NULL)",
            name="ck_simple_route_sheets_cash_receipt_state",
        ),
        CheckConstraint(
            "status != 'settled' OR "
            "(cash_delivered IS NOT NULL AND settled_by IS NOT NULL "
            "AND settled_at IS NOT NULL)",
            name="ck_simple_route_sheets_settled_state",
        ),
        CheckConstraint(
            "status != 'cancelled' OR "
            "(cancelled_by IS NOT NULL AND cancelled_at IS NOT NULL "
            "AND length(trim(cancellation_reason)) > 0)",
            name="ck_simple_route_sheets_cancelled_state",
        ),
    )

    id: Mapped[int] = mapped_column(primary_key=True)
    route_date: Mapped[date] = mapped_column(Date, nullable=False, index=True)
    seller_name: Mapped[str] = mapped_column(String(255), nullable=False, index=True)
    employee_id: Mapped[int | None] = mapped_column(
        ForeignKey("employees.id"),
        index=True,
    )
    vehicle_id: Mapped[int | None] = mapped_column(
        ForeignKey("vehicles.id"),
        index=True,
    )
    route_label: Mapped[str | None] = mapped_column(String(255), index=True)
    status: Mapped[str] = mapped_column(
        String(20),
        nullable=False,
        server_default="draft",
        index=True,
    )
    cash_delivered: Mapped[Decimal | None] = mapped_column(Numeric(14, 2))
    cash_received_in_cash_session: Mapped[bool] = mapped_column(
        Boolean,
        nullable=False,
        server_default=false(),
    )
    cash_session_id: Mapped[int | None] = mapped_column(
        ForeignKey("cash_sessions.id"),
        index=True,
    )
    notes: Mapped[str | None] = mapped_column(Text)
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
    settled_by: Mapped[int | None] = mapped_column(ForeignKey("users.id"))
    settled_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True))
    cancelled_by: Mapped[int | None] = mapped_column(ForeignKey("users.id"))
    cancelled_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True))
    cancellation_reason: Mapped[str | None] = mapped_column(Text)

    employee: Mapped["Employee | None"] = relationship("Employee")
    vehicle: Mapped["Vehicle | None"] = relationship("Vehicle")
    cash_session: Mapped["CashSession | None"] = relationship("CashSession")
    creator: Mapped["User"] = relationship("User", foreign_keys=[created_by])
    settler: Mapped["User | None"] = relationship("User", foreign_keys=[settled_by])
    canceller: Mapped["User | None"] = relationship(
        "User",
        foreign_keys=[cancelled_by],
    )
    trips: Mapped[list["SimpleRouteTrip"]] = relationship(
        "SimpleRouteTrip",
        back_populates="route_sheet",
        cascade="all, delete-orphan",
        order_by="SimpleRouteTrip.trip_number",
    )
    sales: Mapped[list["SimpleRouteSale"]] = relationship(
        "SimpleRouteSale",
        back_populates="route_sheet",
        cascade="all, delete-orphan",
        order_by="SimpleRouteSale.id",
    )
    collections: Mapped[list["SimpleRouteCollection"]] = relationship(
        "SimpleRouteCollection",
        back_populates="route_sheet",
        cascade="all, delete-orphan",
        foreign_keys="SimpleRouteCollection.route_sheet_id",
        order_by="SimpleRouteCollection.id",
    )
    expenses: Mapped[list["SimpleRouteExpense"]] = relationship(
        "SimpleRouteExpense",
        back_populates="route_sheet",
        cascade="all, delete-orphan",
        order_by="SimpleRouteExpense.id",
    )
    audit_logs: Mapped[list["SimpleRouteAuditLog"]] = relationship(
        "SimpleRouteAuditLog",
        back_populates="route_sheet",
        cascade="all, delete-orphan",
        order_by="SimpleRouteAuditLog.id",
    )
    cash_receipt: Mapped["SimpleRouteCashReceipt | None"] = relationship(
        "SimpleRouteCashReceipt",
        back_populates="route_sheet",
        uselist=False,
    )

    @property
    def vehicle_name(self) -> str | None:
        return self.vehicle.name if self.vehicle is not None else None

    @property
    def employee_name(self) -> str | None:
        if self.employee is None:
            return None
        return f"{self.employee.first_name} {self.employee.last_name}".strip()


class SimpleRouteTrip(Base):
    __tablename__ = "simple_route_trips"
    __table_args__ = (
        UniqueConstraint(
            "route_sheet_id",
            "trip_number",
            name="uq_simple_route_trips_sheet_number",
        ),
        CheckConstraint(
            "trip_number > 0",
            name="ck_simple_route_trips_number_positive",
        ),
    )

    id: Mapped[int] = mapped_column(primary_key=True)
    route_sheet_id: Mapped[int] = mapped_column(
        ForeignKey("simple_route_sheets.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )
    trip_number: Mapped[int] = mapped_column(Integer, nullable=False)
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

    route_sheet: Mapped["SimpleRouteSheet"] = relationship(
        "SimpleRouteSheet",
        back_populates="trips",
    )
    items: Mapped[list["SimpleRouteTripItem"]] = relationship(
        "SimpleRouteTripItem",
        back_populates="trip",
        cascade="all, delete-orphan",
        order_by="SimpleRouteTripItem.id",
    )


class SimpleRouteTripItem(Base):
    __tablename__ = "simple_route_trip_items"
    __table_args__ = (
        CheckConstraint(
            "movement_type IN ('out', 'return')",
            name="ck_simple_route_trip_items_movement",
        ),
        CheckConstraint(
            "length(trim(item_label)) > 0",
            name="ck_simple_route_trip_items_label_not_blank",
        ),
        CheckConstraint(
            "quantity > 0",
            name="ck_simple_route_trip_items_quantity_positive",
        ),
    )

    id: Mapped[int] = mapped_column(primary_key=True)
    trip_id: Mapped[int] = mapped_column(
        ForeignKey("simple_route_trips.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )
    movement_type: Mapped[str] = mapped_column(String(10), nullable=False)
    product_id: Mapped[int | None] = mapped_column(ForeignKey("products.id"))
    item_label: Mapped[str] = mapped_column(String(255), nullable=False)
    item_category: Mapped[str] = mapped_column(String(40), nullable=False)
    quantity: Mapped[Decimal] = mapped_column(Numeric(14, 3), nullable=False)
    notes: Mapped[str | None] = mapped_column(Text)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        nullable=False,
        server_default=func.now(),
    )

    trip: Mapped["SimpleRouteTrip"] = relationship(
        "SimpleRouteTrip",
        back_populates="items",
    )
    product: Mapped["Product | None"] = relationship("Product")


class SimpleRouteSale(Base):
    __tablename__ = "simple_route_sales"
    __table_args__ = (
        CheckConstraint(
            "sale_type IN ('cash', 'credit', 'partial')",
            name="ck_simple_route_sales_type",
        ),
        CheckConstraint(
            "status IN ('active', 'voided')",
            name="ck_simple_route_sales_status",
        ),
        CheckConstraint(
            "total_amount >= 0 AND paid_amount >= 0 AND pending_amount >= 0",
            name="ck_simple_route_sales_amounts_nonnegative",
        ),
        CheckConstraint(
            "paid_amount + pending_amount = total_amount",
            name="ck_simple_route_sales_amounts_balance",
        ),
    )

    id: Mapped[int] = mapped_column(primary_key=True)
    route_sheet_id: Mapped[int] = mapped_column(
        ForeignKey("simple_route_sheets.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )
    customer_id: Mapped[int | None] = mapped_column(ForeignKey("customers.id"))
    customer_name_snapshot: Mapped[str | None] = mapped_column(String(255))
    sale_type: Mapped[str] = mapped_column(String(20), nullable=False)
    sale_date: Mapped[date] = mapped_column(Date, nullable=False, index=True)
    total_amount: Mapped[Decimal] = mapped_column(Numeric(14, 2), nullable=False)
    paid_amount: Mapped[Decimal] = mapped_column(Numeric(14, 2), nullable=False)
    pending_amount: Mapped[Decimal] = mapped_column(Numeric(14, 2), nullable=False)
    status: Mapped[str] = mapped_column(
        String(20),
        nullable=False,
        server_default="active",
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

    route_sheet: Mapped["SimpleRouteSheet"] = relationship(
        "SimpleRouteSheet",
        back_populates="sales",
    )
    customer: Mapped["Customer | None"] = relationship("Customer")
    items: Mapped[list["SimpleRouteSaleItem"]] = relationship(
        "SimpleRouteSaleItem",
        back_populates="sale",
        cascade="all, delete-orphan",
        order_by="SimpleRouteSaleItem.id",
    )
    linked_collections: Mapped[list["SimpleRouteCollection"]] = relationship(
        "SimpleRouteCollection",
        back_populates="linked_sale",
        foreign_keys="SimpleRouteCollection.simple_route_sale_id",
        order_by="SimpleRouteCollection.id",
    )

    @property
    def remaining_amount(self) -> Decimal:
        collected = sum(
            (collection.amount for collection in self.linked_collections),
            start=Decimal("0.00"),
        )
        return max(Decimal("0.00"), self.pending_amount - collected)


class SimpleRouteSaleItem(Base):
    __tablename__ = "simple_route_sale_items"
    __table_args__ = (
        CheckConstraint(
            "length(trim(product_name_snapshot)) > 0",
            name="ck_simple_route_sale_items_name_not_blank",
        ),
        CheckConstraint(
            "quantity > 0 AND unit_price >= 0 AND subtotal >= 0",
            name="ck_simple_route_sale_items_amounts",
        ),
    )

    id: Mapped[int] = mapped_column(primary_key=True)
    simple_route_sale_id: Mapped[int] = mapped_column(
        ForeignKey("simple_route_sales.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )
    product_id: Mapped[int | None] = mapped_column(ForeignKey("products.id"))
    product_name_snapshot: Mapped[str] = mapped_column(String(255), nullable=False)
    item_category: Mapped[str] = mapped_column(String(40), nullable=False)
    quantity: Mapped[Decimal] = mapped_column(Numeric(14, 3), nullable=False)
    unit_price: Mapped[Decimal] = mapped_column(Numeric(14, 2), nullable=False)
    subtotal: Mapped[Decimal] = mapped_column(Numeric(14, 2), nullable=False)

    sale: Mapped["SimpleRouteSale"] = relationship(
        "SimpleRouteSale",
        back_populates="items",
    )
    product: Mapped["Product | None"] = relationship("Product")


class SimpleRouteCollection(Base):
    __tablename__ = "simple_route_collections"
    __table_args__ = (
        CheckConstraint(
            "amount > 0",
            name="ck_simple_route_collections_amount_positive",
        ),
    )

    id: Mapped[int] = mapped_column(primary_key=True)
    route_sheet_id: Mapped[int] = mapped_column(
        ForeignKey("simple_route_sheets.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )
    simple_route_sale_id: Mapped[int | None] = mapped_column(
        ForeignKey("simple_route_sales.id"),
        index=True,
    )
    customer_id: Mapped[int | None] = mapped_column(ForeignKey("customers.id"))
    customer_name_snapshot: Mapped[str | None] = mapped_column(String(255))
    amount: Mapped[Decimal] = mapped_column(Numeric(14, 2), nullable=False)
    collection_date: Mapped[date] = mapped_column(Date, nullable=False, index=True)
    notes: Mapped[str | None] = mapped_column(Text)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        nullable=False,
        server_default=func.now(),
    )

    route_sheet: Mapped["SimpleRouteSheet"] = relationship(
        "SimpleRouteSheet",
        back_populates="collections",
        foreign_keys=[route_sheet_id],
    )
    linked_sale: Mapped["SimpleRouteSale | None"] = relationship(
        "SimpleRouteSale",
        back_populates="linked_collections",
        foreign_keys=[simple_route_sale_id],
    )
    customer: Mapped["Customer | None"] = relationship("Customer")


class SimpleRouteExpense(Base):
    __tablename__ = "simple_route_expenses"
    __table_args__ = (
        CheckConstraint(
            "length(trim(description)) > 0",
            name="ck_simple_route_expenses_description_not_blank",
        ),
        CheckConstraint(
            "amount > 0",
            name="ck_simple_route_expenses_amount_positive",
        ),
    )

    id: Mapped[int] = mapped_column(primary_key=True)
    route_sheet_id: Mapped[int] = mapped_column(
        ForeignKey("simple_route_sheets.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )
    description: Mapped[str] = mapped_column(String(255), nullable=False)
    amount: Mapped[Decimal] = mapped_column(Numeric(14, 2), nullable=False)
    category: Mapped[str] = mapped_column(String(40), nullable=False)
    expense_date: Mapped[date] = mapped_column(Date, nullable=False, index=True)
    notes: Mapped[str | None] = mapped_column(Text)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        nullable=False,
        server_default=func.now(),
    )

    route_sheet: Mapped["SimpleRouteSheet"] = relationship(
        "SimpleRouteSheet",
        back_populates="expenses",
    )


class SimpleRouteAuditLog(Base):
    __tablename__ = "simple_route_audit_logs"

    id: Mapped[int] = mapped_column(primary_key=True)
    route_sheet_id: Mapped[int] = mapped_column(
        ForeignKey("simple_route_sheets.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )
    action: Mapped[str] = mapped_column(String(40), nullable=False)
    reason: Mapped[str | None] = mapped_column(Text)
    created_by: Mapped[int] = mapped_column(ForeignKey("users.id"), nullable=False)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        nullable=False,
        server_default=func.now(),
        index=True,
    )
    metadata_json: Mapped[str | None] = mapped_column(Text)

    route_sheet: Mapped["SimpleRouteSheet"] = relationship(
        "SimpleRouteSheet",
        back_populates="audit_logs",
    )
    creator: Mapped["User"] = relationship("User")


class SimpleRouteCashReceipt(Base):
    __tablename__ = "simple_route_cash_receipts"
    __table_args__ = (
        UniqueConstraint(
            "route_sheet_id",
            name="uq_simple_route_cash_receipts_sheet",
        ),
        CheckConstraint(
            "amount >= 0",
            name="ck_simple_route_cash_receipts_amount_nonnegative",
        ),
        Index(
            "ix_simple_route_cash_receipts_session_received",
            "cash_session_id",
            "received_at",
        ),
    )

    id: Mapped[int] = mapped_column(primary_key=True)
    route_sheet_id: Mapped[int] = mapped_column(
        ForeignKey("simple_route_sheets.id"),
        nullable=False,
        index=True,
    )
    cash_session_id: Mapped[int] = mapped_column(
        ForeignKey("cash_sessions.id"),
        nullable=False,
        index=True,
    )
    amount: Mapped[Decimal] = mapped_column(Numeric(14, 2), nullable=False)
    received_by: Mapped[int] = mapped_column(ForeignKey("users.id"), nullable=False)
    received_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        nullable=False,
        server_default=func.now(),
    )
    notes: Mapped[str | None] = mapped_column(Text)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        nullable=False,
        server_default=func.now(),
    )

    route_sheet: Mapped["SimpleRouteSheet"] = relationship(
        "SimpleRouteSheet",
        back_populates="cash_receipt",
    )
    cash_session: Mapped["CashSession"] = relationship("CashSession")
    receiver: Mapped["User"] = relationship("User")
