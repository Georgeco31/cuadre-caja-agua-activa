from datetime import date, datetime, timezone
from decimal import Decimal, ROUND_HALF_UP
from uuid import uuid4

from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session

from app.models.purchase import Purchase
from app.repositories import products
from app.repositories import purchases as purchase_repository
from app.repositories import suppliers
from app.schemas.purchase import PurchaseCreate, PurchaseItemCreate

MONEY_QUANTUM = Decimal("0.01")
ZERO = Decimal("0.00")


def create_purchase(
    db: Session,
    payload: PurchaseCreate,
    created_by: int,
) -> Purchase:
    supplier = suppliers.get_supplier(db, payload.supplier_id)
    if supplier is None:
        raise ValueError("El proveedor no existe.")
    if not supplier.is_active:
        raise ValueError("El proveedor esta inactivo.")

    item_values = [_build_purchase_item(db, item) for item in payload.items]
    subtotal_amount = _sum_amount(
        values["subtotal_amount"] for values in item_values
    )
    discount_amount = _sum_amount(
        values["discount_amount"] for values in item_values
    )
    tax_amount = _sum_amount(values["tax_amount"] for values in item_values)
    total_amount = (subtotal_amount + tax_amount).quantize(MONEY_QUANTUM)

    purchase = purchase_repository.create_purchase(
        db,
        {
            "purchase_number": f"PENDING-{uuid4().hex}",
            "supplier_id": supplier.id,
            "purchase_date": payload.purchase_date,
            "document_number": payload.document_number,
            "document_type": payload.document_type,
            "status": "active",
            "payment_status": payload.payment_status,
            "subtotal_amount": subtotal_amount,
            "discount_amount": discount_amount,
            "tax_amount": tax_amount,
            "total_amount": total_amount,
            "notes": payload.notes,
            "created_by": created_by,
        },
    )
    try:
        db.flush()
        purchase.purchase_number = (
            f"PUR-{purchase.purchase_date:%Y%m%d}-{purchase.id:04d}"
        )
        for values in item_values:
            purchase_repository.create_purchase_item(
                db,
                {"purchase_id": purchase.id, **values},
            )
        db.commit()
    except IntegrityError as error:
        db.rollback()
        raise ValueError("No se pudo registrar la compra.") from error

    created_purchase = purchase_repository.get_purchase(db, purchase.id)
    if created_purchase is None:
        raise RuntimeError("La compra registrada no pudo recuperarse.")
    return created_purchase


def list_purchases(
    db: Session,
    date_from: date | None = None,
    date_to: date | None = None,
    status: str | None = None,
    payment_status: str | None = None,
    supplier_id: int | None = None,
    product_id: int | None = None,
    search: str | None = None,
) -> list[Purchase]:
    if date_from is not None and date_to is not None and date_from > date_to:
        raise ValueError("La fecha desde no puede ser posterior a la fecha hasta.")
    return purchase_repository.list_purchases(
        db=db,
        date_from=date_from,
        date_to=date_to,
        status=status,
        payment_status=payment_status,
        supplier_id=supplier_id,
        product_id=product_id,
        search=_normalize_filter(search),
    )


def get_purchase(db: Session, purchase_id: int) -> Purchase:
    purchase = purchase_repository.get_purchase(db, purchase_id)
    if purchase is None:
        raise ValueError("La compra no existe.")
    return purchase


def void_purchase(
    db: Session,
    purchase_id: int,
    reason: str,
) -> Purchase:
    purchase = purchase_repository.get_purchase(
        db,
        purchase_id,
        for_update=True,
    )
    if purchase is None:
        raise ValueError("La compra no existe.")
    if purchase.status == "voided":
        raise ValueError("La compra ya esta anulada.")

    purchase_repository.mark_purchase_voided(
        db,
        purchase,
        reason,
        datetime.now(timezone.utc),
    )
    try:
        db.commit()
    except IntegrityError as error:
        db.rollback()
        raise ValueError("No se pudo anular la compra.") from error

    voided_purchase = purchase_repository.get_purchase(db, purchase.id)
    if voided_purchase is None:
        raise RuntimeError("La compra anulada no pudo recuperarse.")
    return voided_purchase


def _build_purchase_item(
    db: Session,
    item: PurchaseItemCreate,
) -> dict[str, object]:
    product_sku_snapshot = None
    product_name_snapshot = None
    product_presentation_snapshot = None
    description = item.description

    if item.product_id is not None:
        product = products.get_product(db, item.product_id)
        if product is None:
            raise ValueError(f"El producto {item.product_id} no existe.")
        if not product.is_active:
            raise ValueError(f"El producto {product.name} esta inactivo.")
        product_sku_snapshot = product.sku
        product_name_snapshot = product.name
        product_presentation_snapshot = product.presentation
        if description is None:
            description = product.name
    elif description is None:
        raise ValueError(
            "La descripcion es obligatoria cuando no se selecciona un producto.",
        )

    gross_amount = item.quantity * item.unit_cost
    if item.discount_amount > gross_amount:
        raise ValueError(
            "El descuento no puede dejar el subtotal del item negativo.",
        )
    subtotal_amount = (gross_amount - item.discount_amount).quantize(
        MONEY_QUANTUM,
        rounding=ROUND_HALF_UP,
    )
    total_amount = (subtotal_amount + item.tax_amount).quantize(
        MONEY_QUANTUM,
        rounding=ROUND_HALF_UP,
    )
    return {
        "product_id": item.product_id,
        "description": description,
        "product_sku_snapshot": product_sku_snapshot,
        "product_name_snapshot": product_name_snapshot,
        "product_presentation_snapshot": product_presentation_snapshot,
        "quantity": item.quantity,
        "unit_cost": item.unit_cost,
        "discount_amount": item.discount_amount.quantize(MONEY_QUANTUM),
        "tax_amount": item.tax_amount.quantize(MONEY_QUANTUM),
        "subtotal_amount": subtotal_amount,
        "total_amount": total_amount,
        "notes": item.notes,
    }


def _sum_amount(values) -> Decimal:
    return sum(values, start=ZERO).quantize(MONEY_QUANTUM)


def _normalize_filter(value: str | None) -> str | None:
    if value is None:
        return None
    normalized_value = value.strip()
    return normalized_value or None
