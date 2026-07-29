from __future__ import annotations

from datetime import datetime

from sqlalchemy import CheckConstraint, DateTime, ForeignKey, String, Text, func
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.base import Base


class PayrollAuditLog(Base):
    __tablename__ = "payroll_audit_logs"
    __table_args__ = (
        CheckConstraint(
            "action IN ('run_created', 'item_added', 'item_updated', "
            "'approved', 'paid', 'cancelled')",
            name="ck_payroll_audit_logs_action",
        ),
    )

    id: Mapped[int] = mapped_column(primary_key=True)
    payroll_run_id: Mapped[int] = mapped_column(
        ForeignKey("payroll_runs.id"),
        nullable=False,
        index=True,
    )
    action: Mapped[str] = mapped_column(String(30), nullable=False)
    actor_id: Mapped[int] = mapped_column(
        ForeignKey("users.id"),
        nullable=False,
        index=True,
    )
    reason: Mapped[str | None] = mapped_column(Text)
    details: Mapped[str | None] = mapped_column(Text)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        nullable=False,
        server_default=func.now(),
        index=True,
    )

    payroll_run: Mapped["PayrollRun"] = relationship(
        "PayrollRun",
        back_populates="audit_logs",
    )
    actor: Mapped["User"] = relationship("User")
