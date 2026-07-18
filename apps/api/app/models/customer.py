from datetime import datetime
from decimal import Decimal

from sqlalchemy import (
    Boolean,
    CheckConstraint,
    DateTime,
    Numeric,
    String,
    Text,
    false,
    func,
    true,
)
from sqlalchemy.orm import Mapped, mapped_column

from app.db.base import Base


class Customer(Base):
    __tablename__ = "customers"
    __table_args__ = (
        CheckConstraint(
            "length(trim(name)) > 0",
            name="ck_customers_name_not_blank",
        ),
        CheckConstraint(
            "customer_type IN ('household', 'store', 'business', 'distributor', 'other')",
            name="ck_customers_customer_type",
        ),
        CheckConstraint(
            "credit_limit >= 0",
            name="ck_customers_credit_limit_nonnegative",
        ),
    )

    id: Mapped[int] = mapped_column(primary_key=True)
    name: Mapped[str] = mapped_column(String(255), nullable=False)
    primary_phone: Mapped[str | None] = mapped_column(String(50), unique=True)
    secondary_phone: Mapped[str | None] = mapped_column(String(50))
    address: Mapped[str | None] = mapped_column(String(255))
    sector: Mapped[str | None] = mapped_column(String(120))
    customer_type: Mapped[str] = mapped_column(
        String(20),
        nullable=False,
        server_default="household",
    )
    route_reference: Mapped[str | None] = mapped_column(String(150))
    credit_allowed: Mapped[bool] = mapped_column(
        Boolean,
        nullable=False,
        server_default=false(),
    )
    credit_limit: Mapped[Decimal] = mapped_column(
        Numeric(12, 2),
        nullable=False,
        server_default="0.00",
    )
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
