from datetime import date
from decimal import Decimal

from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.orm import Session

from app.api.deps import get_current_user, get_db, require_admin_auditor
from app.schemas.pricing import (
    PriceListCreate,
    PriceListItemCreate,
    PriceListItemRead,
    PriceListItemUpdate,
    PriceListRead,
    PriceListType,
    PriceListUpdate,
    PriceResolution,
)
from app.services import pricing as pricing_service

router = APIRouter(
    prefix="/pricing",
    tags=["pricing"],
    dependencies=[Depends(get_current_user)],
)


@router.post(
    "/price-lists",
    response_model=PriceListRead,
    status_code=status.HTTP_201_CREATED,
    dependencies=[Depends(require_admin_auditor)],
)
def create_price_list(
    payload: PriceListCreate,
    db: Session = Depends(get_db),
):
    try:
        return pricing_service.create_price_list(db, payload)
    except ValueError as error:
        raise _http_error(error) from error


@router.get("/price-lists", response_model=list[PriceListRead])
def list_price_lists(
    search: str | None = None,
    list_type: PriceListType | None = None,
    customer_id: int | None = Query(default=None, gt=0),
    route_id: int | None = Query(default=None, gt=0),
    is_active: bool | None = None,
    db: Session = Depends(get_db),
):
    return pricing_service.list_price_lists(
        db=db,
        search=search,
        list_type=list_type,
        customer_id=customer_id,
        route_id=route_id,
        is_active=is_active,
    )


@router.get("/price-lists/{price_list_id}", response_model=PriceListRead)
def get_price_list(
    price_list_id: int,
    db: Session = Depends(get_db),
):
    try:
        return pricing_service.get_price_list(db, price_list_id)
    except ValueError as error:
        raise _http_error(error) from error


@router.patch(
    "/price-lists/{price_list_id}",
    response_model=PriceListRead,
    dependencies=[Depends(require_admin_auditor)],
)
def update_price_list(
    price_list_id: int,
    payload: PriceListUpdate,
    db: Session = Depends(get_db),
):
    try:
        return pricing_service.update_price_list(db, price_list_id, payload)
    except ValueError as error:
        raise _http_error(error) from error


@router.patch(
    "/price-lists/{price_list_id}/deactivate",
    response_model=PriceListRead,
    dependencies=[Depends(require_admin_auditor)],
)
def deactivate_price_list(
    price_list_id: int,
    db: Session = Depends(get_db),
):
    try:
        return pricing_service.set_price_list_active(db, price_list_id, False)
    except ValueError as error:
        raise _http_error(error) from error


@router.patch(
    "/price-lists/{price_list_id}/activate",
    response_model=PriceListRead,
    dependencies=[Depends(require_admin_auditor)],
)
def activate_price_list(
    price_list_id: int,
    db: Session = Depends(get_db),
):
    try:
        return pricing_service.set_price_list_active(db, price_list_id, True)
    except ValueError as error:
        raise _http_error(error) from error


@router.post(
    "/price-lists/{price_list_id}/items",
    response_model=PriceListItemRead,
    status_code=status.HTTP_201_CREATED,
    dependencies=[Depends(require_admin_auditor)],
)
def create_price_list_item(
    price_list_id: int,
    payload: PriceListItemCreate,
    db: Session = Depends(get_db),
):
    try:
        return pricing_service.create_price_list_item(
            db,
            price_list_id,
            payload,
        )
    except ValueError as error:
        raise _http_error(error) from error


@router.patch(
    "/price-list-items/{item_id}",
    response_model=PriceListItemRead,
    dependencies=[Depends(require_admin_auditor)],
)
def update_price_list_item(
    item_id: int,
    payload: PriceListItemUpdate,
    db: Session = Depends(get_db),
):
    try:
        return pricing_service.update_price_list_item(db, item_id, payload)
    except ValueError as error:
        raise _http_error(error) from error


@router.patch(
    "/price-list-items/{item_id}/deactivate",
    response_model=PriceListItemRead,
    dependencies=[Depends(require_admin_auditor)],
)
def deactivate_price_list_item(
    item_id: int,
    db: Session = Depends(get_db),
):
    try:
        return pricing_service.set_price_list_item_active(db, item_id, False)
    except ValueError as error:
        raise _http_error(error) from error


@router.patch(
    "/price-list-items/{item_id}/activate",
    response_model=PriceListItemRead,
    dependencies=[Depends(require_admin_auditor)],
)
def activate_price_list_item(
    item_id: int,
    db: Session = Depends(get_db),
):
    try:
        return pricing_service.set_price_list_item_active(db, item_id, True)
    except ValueError as error:
        raise _http_error(error) from error


@router.get("/resolve", response_model=PriceResolution)
def resolve_price(
    product_id: int = Query(gt=0),
    customer_id: int | None = Query(default=None, gt=0),
    route_id: int | None = Query(default=None, gt=0),
    route_load_id: int | None = Query(default=None, gt=0),
    quantity: Decimal = Query(
        default=Decimal("1"),
        gt=Decimal("0"),
        max_digits=12,
        decimal_places=3,
    ),
    price_date: date | None = None,
    db: Session = Depends(get_db),
):
    try:
        return pricing_service.resolve_price(
            db=db,
            product_id=product_id,
            customer_id=customer_id,
            route_id=route_id,
            route_load_id=route_load_id,
            quantity=quantity,
            price_date=price_date,
        )
    except ValueError as error:
        raise _http_error(error) from error


def _http_error(error: ValueError) -> HTTPException:
    detail = str(error)
    if "no existe" in detail:
        return HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=detail)
    return HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=detail)
