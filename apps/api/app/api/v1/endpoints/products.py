from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.api.deps import get_current_user, get_db
from app.schemas.product import (
    ProductCategory,
    ProductCreate,
    ProductRead,
    ProductUnit,
    ProductUpdate,
)
from app.services import products as product_service

router = APIRouter(
    prefix="/products",
    tags=["products"],
    dependencies=[Depends(get_current_user)],
)


@router.post("", response_model=ProductRead, status_code=status.HTTP_201_CREATED)
def create_product(
    payload: ProductCreate,
    db: Session = Depends(get_db),
):
    try:
        return product_service.create_product(db, payload)
    except ValueError as error:
        raise _http_error(error) from error


@router.get("", response_model=list[ProductRead])
def list_products(
    search: str | None = None,
    is_active: bool | None = None,
    category: ProductCategory | None = None,
    unit: ProductUnit | None = None,
    db: Session = Depends(get_db),
):
    return product_service.list_products(
        db=db,
        search=search,
        is_active=is_active,
        category=category,
        unit=unit,
    )


@router.get("/{product_id}", response_model=ProductRead)
def get_product(product_id: int, db: Session = Depends(get_db)):
    try:
        return product_service.get_product(db, product_id)
    except ValueError as error:
        raise _http_error(error) from error


@router.patch("/{product_id}", response_model=ProductRead)
def update_product(
    product_id: int,
    payload: ProductUpdate,
    db: Session = Depends(get_db),
):
    try:
        return product_service.update_product(db, product_id, payload)
    except ValueError as error:
        raise _http_error(error) from error


@router.patch("/{product_id}/deactivate", response_model=ProductRead)
def deactivate_product(product_id: int, db: Session = Depends(get_db)):
    try:
        return product_service.deactivate_product(db, product_id)
    except ValueError as error:
        raise _http_error(error) from error


@router.patch("/{product_id}/activate", response_model=ProductRead)
def activate_product(product_id: int, db: Session = Depends(get_db)):
    try:
        return product_service.activate_product(db, product_id)
    except ValueError as error:
        raise _http_error(error) from error


def _http_error(error: ValueError) -> HTTPException:
    detail = str(error)
    if "ya esta registrado" in detail:
        return HTTPException(status_code=status.HTTP_409_CONFLICT, detail=detail)
    if "no existe" in detail:
        return HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=detail)
    return HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=detail)
