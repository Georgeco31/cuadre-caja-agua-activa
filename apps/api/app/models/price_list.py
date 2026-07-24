from __future__ import annotations

from datetime import date, datetime

from sqlalchemy import (
    Boolean,
    CheckConstraint,
    Date,
    DateTime,
    ForeignKey,
    Integer,
    String,
    Text,
    func,
    true,
)
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.base import Base


class PriceList(Base):
    __tablename__ = "price_lists"
    __table_args__ = (
        CheckConstraint(
            "length(trim(name)) > 0",
            name="ck_price_lists_name_not_blank",
        ),
        CheckConstraint(
            "list_type IN "
            "('general', 'customer', 'route', 'customer_route', 'special')",
            name="ck_price_lists_type",
        ),
        CheckConstraint(
            "list_type <> 'customer' OR customer_id IS NOT NULL",
            name="ck_price_lists_customer_target",
        ),
        CheckConstraint(
            "list_type <> 'route' OR route_id IS NOT NULL",
            name="ck_price_lists_route_target",
        ),
        CheckConstraint(
            "list_type <> 'customer_route' OR "
            "(customer_id IS NOT NULL AND route_id IS NOT NULL)",
            name="ck_price_lists_customer_route_target",
        ),
        CheckConstraint(
            "valid_from IS NULL OR valid_to IS NULL OR valid_from <= valid_to",
            name="ck_price_lists_valid_dates",
        ),
    )

    id: Mapped[int] = mapped_column(primary_key=True)
    name: Mapped[str] = mapped_column(String(255), nullable=False)
    list_type: Mapped[str] = mapped_column(String(30), nullable=False, index=True)
    customer_id: Mapped[int | None] = mapped_column(
        ForeignKey("customers.id"),
        index=True,
    )
    route_id: Mapped[int | None] = mapped_column(
        ForeignKey("delivery_routes.id"),
        index=True,
    )
    priority: Mapped[int] = mapped_column(
        Integer,
        nullable=False,
        server_default="0",
    )
    valid_from: Mapped[date | None] = mapped_column(Date)
    valid_to: Mapped[date | None] = mapped_column(Date)
    is_active: Mapped[bool] = mapped_column(
        Boolean,
        nullable=False,
        server_default=true(),
        index=True,
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

    customer: Mapped["Customer | None"] = relationship("Customer")
    route: Mapped["DeliveryRoute | None"] = relationship("DeliveryRoute")
    items: Mapped[list["PriceListItem"]] = relationship(
        "PriceListItem",
        back_populates="price_list",
        cascade="all, delete-orphan",
        order_by="PriceListItem.id",
    )

    @property
    def customer_name(self) -> str | None:
        return self.customer.name if self.customer is not None else None

    @property
    def route_name(self) -> str | None:
        return self.route.name if self.route is not None else None
