from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.api.deps import get_current_user, get_db, require_admin_auditor
from app.schemas.supplier import SupplierCreate, SupplierRead, SupplierUpdate
from app.services import suppliers as supplier_service

router = APIRouter(
    prefix="/suppliers",
    tags=["suppliers"],
    dependencies=[Depends(get_current_user)],
)


@router.post(
    "",
    response_model=SupplierRead,
    status_code=status.HTTP_201_CREATED,
    dependencies=[Depends(require_admin_auditor)],
)
def create_supplier(
    payload: SupplierCreate,
    db: Session = Depends(get_db),
):
    try:
        return supplier_service.create_supplier(db, payload)
    except ValueError as error:
        raise _http_error(error) from error


@router.get("", response_model=list[SupplierRead])
def list_suppliers(
    search: str | None = None,
    is_active: bool | None = None,
    supplier_type: str | None = None,
    db: Session = Depends(get_db),
):
    return supplier_service.list_suppliers(
        db=db,
        search=search,
        is_active=is_active,
        supplier_type=supplier_type,
    )


@router.get("/{supplier_id}", response_model=SupplierRead)
def get_supplier(supplier_id: int, db: Session = Depends(get_db)):
    try:
        return supplier_service.get_supplier(db, supplier_id)
    except ValueError as error:
        raise _http_error(error) from error


@router.patch(
    "/{supplier_id}",
    response_model=SupplierRead,
    dependencies=[Depends(require_admin_auditor)],
)
def update_supplier(
    supplier_id: int,
    payload: SupplierUpdate,
    db: Session = Depends(get_db),
):
    try:
        return supplier_service.update_supplier(db, supplier_id, payload)
    except ValueError as error:
        raise _http_error(error) from error


@router.patch(
    "/{supplier_id}/deactivate",
    response_model=SupplierRead,
    dependencies=[Depends(require_admin_auditor)],
)
def deactivate_supplier(supplier_id: int, db: Session = Depends(get_db)):
    try:
        return supplier_service.deactivate_supplier(db, supplier_id)
    except ValueError as error:
        raise _http_error(error) from error


@router.patch(
    "/{supplier_id}/activate",
    response_model=SupplierRead,
    dependencies=[Depends(require_admin_auditor)],
)
def activate_supplier(supplier_id: int, db: Session = Depends(get_db)):
    try:
        return supplier_service.activate_supplier(db, supplier_id)
    except ValueError as error:
        raise _http_error(error) from error


def _http_error(error: ValueError) -> HTTPException:
    detail = str(error)
    if "ya esta registrada" in detail:
        return HTTPException(status_code=status.HTTP_409_CONFLICT, detail=detail)
    if "no existe" in detail:
        return HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=detail)
    return HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=detail)
