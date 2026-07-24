from datetime import date, datetime
from decimal import Decimal
from typing import Literal

from pydantic import BaseModel, ConfigDict, Field, field_validator, model_validator

from app.schemas.supplier import SupplierRead

PurchaseStatus = Literal["active", "voided"]
PurchasePaymentStatus = Literal["unpaid", "partial", "paid"]
PurchaseDocumentType = Literal["factura", "nota_venta", "recibo", "otro"]


class PurchaseItemCreate(BaseModel):
    product_id: int | None = Field(default=None, gt=0)
    description: str | None = None
    quantity: Decimal = Field(
        gt=Decimal("0"),
        max_digits=12,
        decimal_places=3,
    )
    unit_cost: Decimal = Field(
        ge=Decimal("0.00"),
        max_digits=12,
        decimal_places=2,
    )
    discount_amount: Decimal = Field(
        default=Decimal("0.00"),
        ge=Decimal("0.00"),
        max_digits=14,
        decimal_places=2,
    )
    tax_amount: Decimal = Field(
        default=Decimal("0.00"),
        ge=Decimal("0.00"),
        max_digits=14,
        decimal_places=2,
    )
    notes: str | None = None

    @field_validator("description", "notes")
    @classmethod
    def normalize_optional_text(cls, value: str | None) -> str | None:
        return _normalize_optional_text(value)

    @model_validator(mode="after")
    def validate_description_and_discount(self):
        if self.product_id is None and self.description is None:
            raise ValueError(
                "La descripcion es obligatoria cuando no se selecciona un producto.",
            )
        gross_amount = self.quantity * self.unit_cost
        if self.discount_amount > gross_amount:
            raise ValueError(
                "El descuento no puede dejar el subtotal del item negativo.",
            )
        return self


class PurchaseCreate(BaseModel):
    supplier_id: int = Field(gt=0)
    purchase_date: date
    document_number: str | None = Field(default=None, max_length=120)
    document_type: PurchaseDocumentType | None = None
    payment_status: PurchasePaymentStatus = "unpaid"
    notes: str | None = None
    items: list[PurchaseItemCreate] = Field(min_length=1)

    @field_validator("document_number", "notes")
    @classmethod
    def normalize_optional_text(cls, value: str | None) -> str | None:
        return _normalize_optional_text(value)


class PurchaseVoid(BaseModel):
    reason: str = Field(min_length=1)

    @field_validator("reason")
    @classmethod
    def validate_reason(cls, value: str) -> str:
        normalized_value = value.strip()
        if not normalized_value:
            raise ValueError("El motivo de anulacion es obligatorio.")
        return normalized_value


class PurchaseItemRead(BaseModel):
    id: int
    purchase_id: int
    product_id: int | None
    description: str | None
    product_sku_snapshot: str | None
    product_name_snapshot: str | None
    product_presentation_snapshot: str | None
    quantity: Decimal
    unit_cost: Decimal
    discount_amount: Decimal
    tax_amount: Decimal
    subtotal_amount: Decimal
    total_amount: Decimal
    notes: str | None
    created_at: datetime

    model_config = ConfigDict(from_attributes=True)


class PurchaseRead(BaseModel):
    id: int
    purchase_number: str
    supplier_id: int
    purchase_date: date
    document_number: str | None
    document_type: PurchaseDocumentType | None
    status: PurchaseStatus
    payment_status: PurchasePaymentStatus
    subtotal_amount: Decimal
    discount_amount: Decimal
    tax_amount: Decimal
    total_amount: Decimal
    notes: str | None
    void_reason: str | None
    voided_at: datetime | None
    created_by: int
    created_at: datetime
    updated_at: datetime
    supplier: SupplierRead
    items: list[PurchaseItemRead]

    model_config = ConfigDict(from_attributes=True)


def _normalize_optional_text(value: str | None) -> str | None:
    if value is None:
        return None
    normalized_value = value.strip()
    return normalized_value or None
