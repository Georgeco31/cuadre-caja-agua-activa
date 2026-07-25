from __future__ import annotations

from datetime import date, datetime, time
from decimal import Decimal

from sqlalchemy import (
    CheckConstraint,
    Date,
    DateTime,
    ForeignKey,
    Numeric,
    String,
    Text,
    Time,
    UniqueConstraint,
    func,
)
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.base import Base


class EmployeeAttendance(Base):
    __tablename__ = "employee_attendance"
    __table_args__ = (
        CheckConstraint(
            "status IN "
            "('present', 'absent', 'late', 'permission', 'vacation', 'sick')",
            name="ck_employee_attendance_status",
        ),
        CheckConstraint(
            "hours_worked IS NULL OR hours_worked >= 0",
            name="ck_employee_attendance_hours_nonnegative",
        ),
        UniqueConstraint(
            "employee_id",
            "attendance_date",
            name="uq_employee_attendance_employee_date",
        ),
    )

    id: Mapped[int] = mapped_column(primary_key=True)
    employee_id: Mapped[int] = mapped_column(
        ForeignKey("employees.id"),
        nullable=False,
        index=True,
    )
    attendance_date: Mapped[date] = mapped_column(
        Date,
        nullable=False,
        index=True,
    )
    status: Mapped[str] = mapped_column(String(20), nullable=False, index=True)
    check_in_time: Mapped[time | None] = mapped_column(Time)
    check_out_time: Mapped[time | None] = mapped_column(Time)
    hours_worked: Mapped[Decimal | None] = mapped_column(Numeric(8, 2))
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

    employee: Mapped["Employee"] = relationship("Employee")
    creator: Mapped["User"] = relationship("User")

    @property
    def employee_name(self) -> str:
        return f"{self.employee.first_name} {self.employee.last_name}"
