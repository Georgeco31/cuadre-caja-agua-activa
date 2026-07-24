from datetime import date, datetime, timezone
from decimal import Decimal
from uuid import uuid4

from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session

from app.models.route_cash_receipt import RouteCashReceipt
from app.repositories import cash_sessions as cash_sessions_repository
from app.repositories import route_cash_receipts as receipts_repository
from app.repositories import route_closures as closures_repository
from app.schemas.route_cash_receipt import (
    CashSessionRouteCashReceiptsRead,
    RouteCashReceiptCreate,
    RouteCashReceiptTotals,
    RouteClosureCashReceiptRead,
)

MONEY_QUANTUM = Decimal("0.01")
ZERO = Decimal("0.00")


def create_route_cash_receipt(
    db: Session,
    payload: RouteCashReceiptCreate,
    created_by: int,
) -> RouteCashReceipt:
    closure = closures_repository.get_route_closure(
        db,
        payload.route_closure_id,
        for_update=True,
    )
    if closure is None:
        raise ValueError("El cierre financiero de ruta no existe.")
    if closure.status != "active":
        raise ValueError("No se puede registrar un cierre de ruta anulado.")

    cash_session = cash_sessions_repository.get_cash_session(
        db,
        payload.cash_session_id,
        for_update=True,
    )
    if cash_session is None:
        raise ValueError("El cuadre de caja no existe.")
    if cash_session.status != "open":
        raise ValueError(
            "El cuadre de caja esta cerrado y no permite registrar dinero de ruta.",
        )
    if receipts_repository.has_active_receipt_for_closure(db, closure.id):
        raise ValueError(
            "El cierre de ruta ya tiene un registro de dinero en caja activo.",
        )

    delivered_cash_total = closure.delivered_cash_total.quantize(MONEY_QUANTUM)
    received_amount = (
        delivered_cash_total
        if payload.received_amount is None
        else payload.received_amount.quantize(MONEY_QUANTUM)
    )
    difference_amount = (received_amount - delivered_cash_total).quantize(
        MONEY_QUANTUM,
    )
    receipt = receipts_repository.create_route_cash_receipt(
        db,
        {
            "receipt_number": f"PENDING-{uuid4().hex}",
            "receipt_date": payload.receipt_date,
            "route_closure_id": closure.id,
            "cash_session_id": cash_session.id,
            "route_load_id": closure.route_load_id,
            "route_id": closure.route_id,
            "vehicle_id": closure.vehicle_id,
            "closure_number_snapshot": closure.closure_number,
            "route_name_snapshot": closure.route_name_snapshot,
            "vehicle_name_snapshot": closure.vehicle_name_snapshot,
            "delivered_cash_total": delivered_cash_total,
            "received_amount": received_amount,
            "difference_amount": difference_amount,
            "status": "active",
            "notes": payload.notes,
            "created_by": created_by,
        },
    )
    try:
        db.flush()
        receipt.receipt_number = (
            f"RCR-{receipt.receipt_date:%Y%m%d}-{receipt.id:04d}"
        )
        db.commit()
    except IntegrityError as error:
        db.rollback()
        raise ValueError(
            "No se pudo registrar el dinero de ruta. "
            "Verifique que el cierre no tenga otro recibo activo.",
        ) from error

    created_receipt = receipts_repository.get_route_cash_receipt(db, receipt.id)
    if created_receipt is None:
        raise RuntimeError("El registro de dinero de ruta no pudo recuperarse.")
    return created_receipt


def list_route_cash_receipts(
    db: Session,
    date_from: date | None = None,
    date_to: date | None = None,
    status: str | None = None,
    route_id: int | None = None,
    vehicle_id: int | None = None,
    route_closure_id: int | None = None,
    cash_session_id: int | None = None,
    search: str | None = None,
) -> list[RouteCashReceipt]:
    if date_from is not None and date_to is not None and date_from > date_to:
        raise ValueError("La fecha desde no puede ser posterior a la fecha hasta.")
    return receipts_repository.list_route_cash_receipts(
        db=db,
        date_from=date_from,
        date_to=date_to,
        status=status,
        route_id=route_id,
        vehicle_id=vehicle_id,
        route_closure_id=route_closure_id,
        cash_session_id=cash_session_id,
        search=_normalize_filter(search),
    )


def get_route_cash_receipt(db: Session, receipt_id: int) -> RouteCashReceipt:
    receipt = receipts_repository.get_route_cash_receipt(db, receipt_id)
    if receipt is None:
        raise ValueError("El registro de dinero de ruta no existe.")
    return receipt


def get_cash_receipt_for_closure(
    db: Session,
    closure_id: int,
) -> RouteClosureCashReceiptRead:
    closure = closures_repository.get_route_closure(db, closure_id)
    if closure is None:
        raise ValueError("El cierre financiero de ruta no existe.")
    receipt = receipts_repository.get_active_receipt_for_closure(db, closure_id)
    return RouteClosureCashReceiptRead(
        status="received" if receipt is not None else "not_received",
        active_receipt=receipt,
    )


def get_receipts_for_cash_session(
    db: Session,
    cash_session_id: int,
) -> CashSessionRouteCashReceiptsRead:
    cash_session = cash_sessions_repository.get_cash_session(db, cash_session_id)
    if cash_session is None:
        raise ValueError("El cuadre de caja no existe.")
    receipts = receipts_repository.list_route_cash_receipts(
        db,
        cash_session_id=cash_session_id,
    )
    active_receipts = [receipt for receipt in receipts if receipt.status == "active"]
    return CashSessionRouteCashReceiptsRead(
        cash_session_id=cash_session.id,
        session_date=cash_session.session_date,
        status=cash_session.status,
        receipts=receipts,
        totals=RouteCashReceiptTotals(
            receipts_count=len(active_receipts),
            delivered_cash_total=_sum_amount(
                receipt.delivered_cash_total for receipt in active_receipts
            ),
            received_amount_total=_sum_amount(
                receipt.received_amount for receipt in active_receipts
            ),
            difference_total=_sum_amount(
                receipt.difference_amount for receipt in active_receipts
            ),
        ),
    )


def void_route_cash_receipt(
    db: Session,
    receipt_id: int,
    reason: str,
) -> RouteCashReceipt:
    receipt = receipts_repository.get_route_cash_receipt(
        db,
        receipt_id,
        for_update=True,
    )
    if receipt is None:
        raise ValueError("El registro de dinero de ruta no existe.")
    if receipt.status == "voided":
        raise ValueError("El registro de dinero de ruta ya esta anulado.")

    receipts_repository.mark_route_cash_receipt_voided(
        db,
        receipt,
        reason,
        datetime.now(timezone.utc),
    )
    try:
        db.commit()
    except IntegrityError as error:
        db.rollback()
        raise ValueError("No se pudo anular el registro de dinero de ruta.") from error

    voided_receipt = receipts_repository.get_route_cash_receipt(db, receipt.id)
    if voided_receipt is None:
        raise RuntimeError("El registro de dinero anulado no pudo recuperarse.")
    return voided_receipt


def _sum_amount(values) -> Decimal:
    return sum(values, start=ZERO).quantize(MONEY_QUANTUM)


def _normalize_filter(value: str | None) -> str | None:
    if value is None:
        return None
    normalized_value = value.strip()
    return normalized_value or None
