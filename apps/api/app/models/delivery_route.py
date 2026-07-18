from datetime import datetime
from decimal import Decimal

from sqlalchemy import (
    Boolean,
    CheckConstraint,
    DateTime,
    Numeric,
    String,
    Text,
    func,
    true,
)
from sqlalchemy.orm import Mapped, mapped_column

from app.db.base import Base


class DeliveryRoute(Base):
    __tablename__ = "delivery_routes"
    __table_args__ = (
        CheckConstraint(
            "length(trim(name)) > 0",
            name="ck_delivery_routes_name_not_blank",
        ),
        CheckConstraint(
            "expected_daily_cash >= 0",
            name="ck_delivery_routes_expected_cash_nonnegative",
        ),
    )

    id: Mapped[int] = mapped_column(primary_key=True)
    code: Mapped[str | None] = mapped_column(String(80), unique=True)
    name: Mapped[str] = mapped_column(String(255), nullable=False)
    description: Mapped[str | None] = mapped_column(Text)
    zone: Mapped[str | None] = mapped_column(String(120))
    sector: Mapped[str | None] = mapped_column(String(120))
    service_days: Mapped[str | None] = mapped_column(String(255))
    reference_driver: Mapped[str | None] = mapped_column(String(255))
    reference_vehicle: Mapped[str | None] = mapped_column(String(255))
    expected_daily_cash: Mapped[Decimal] = mapped_column(
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
