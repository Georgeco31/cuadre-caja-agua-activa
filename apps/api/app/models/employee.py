from datetime import date, datetime
from decimal import Decimal

from sqlalchemy import (
    Boolean,
    CheckConstraint,
    Date,
    DateTime,
    Numeric,
    String,
    Text,
    func,
    true,
)
from sqlalchemy.orm import Mapped, mapped_column

from app.db.base import Base


class Employee(Base):
    __tablename__ = "employees"
    __table_args__ = (
        CheckConstraint(
            "length(trim(first_name)) > 0",
            name="ck_employees_first_name_not_blank",
        ),
        CheckConstraint(
            "length(trim(last_name)) > 0",
            name="ck_employees_last_name_not_blank",
        ),
        CheckConstraint(
            "employee_type IN ('driver', 'assistant', 'office', 'production', 'sales', 'other')",
            name="ck_employees_employee_type",
        ),
        CheckConstraint(
            "payment_frequency IN ('daily', 'weekly', 'biweekly', 'monthly', 'other')",
            name="ck_employees_payment_frequency",
        ),
        CheckConstraint(
            "base_salary >= 0",
            name="ck_employees_base_salary_nonnegative",
        ),
    )

    id: Mapped[int] = mapped_column(primary_key=True)
    first_name: Mapped[str] = mapped_column(String(120), nullable=False)
    last_name: Mapped[str] = mapped_column(String(120), nullable=False)
    identification: Mapped[str | None] = mapped_column(String(50), unique=True)
    primary_phone: Mapped[str | None] = mapped_column(String(50))
    secondary_phone: Mapped[str | None] = mapped_column(String(50))
    address: Mapped[str | None] = mapped_column(String(255))
    job_position: Mapped[str | None] = mapped_column(String(120))
    employee_type: Mapped[str] = mapped_column(
        String(20),
        nullable=False,
        server_default="other",
    )
    base_salary: Mapped[Decimal] = mapped_column(
        Numeric(12, 2),
        nullable=False,
        server_default="0.00",
    )
    payment_frequency: Mapped[str] = mapped_column(
        String(20),
        nullable=False,
        server_default="monthly",
    )
    hire_date: Mapped[date | None] = mapped_column(Date)
    termination_date: Mapped[date | None] = mapped_column(Date)
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
