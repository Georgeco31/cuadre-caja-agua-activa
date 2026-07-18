from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.api.deps import get_current_user, get_db
from app.schemas.delivery_route import (
    DeliveryRouteCreate,
    DeliveryRouteRead,
    DeliveryRouteUpdate,
)
from app.services import delivery_routes as delivery_route_service

router = APIRouter(
    prefix="/delivery-routes",
    tags=["delivery-routes"],
    dependencies=[Depends(get_current_user)],
)


@router.post("", response_model=DeliveryRouteRead, status_code=status.HTTP_201_CREATED)
def create_delivery_route(
    payload: DeliveryRouteCreate,
    db: Session = Depends(get_db),
):
    try:
        return delivery_route_service.create_delivery_route(db, payload)
    except ValueError as error:
        raise _http_error(error) from error


@router.get("", response_model=list[DeliveryRouteRead])
def list_delivery_routes(
    search: str | None = None,
    is_active: bool | None = None,
    zone: str | None = None,
    sector: str | None = None,
    db: Session = Depends(get_db),
):
    return delivery_route_service.list_delivery_routes(
        db=db,
        search=search,
        is_active=is_active,
        zone=zone,
        sector=sector,
    )


@router.get("/{route_id}", response_model=DeliveryRouteRead)
def get_delivery_route(route_id: int, db: Session = Depends(get_db)):
    try:
        return delivery_route_service.get_delivery_route(db, route_id)
    except ValueError as error:
        raise _http_error(error) from error


@router.patch("/{route_id}", response_model=DeliveryRouteRead)
def update_delivery_route(
    route_id: int,
    payload: DeliveryRouteUpdate,
    db: Session = Depends(get_db),
):
    try:
        return delivery_route_service.update_delivery_route(db, route_id, payload)
    except ValueError as error:
        raise _http_error(error) from error


@router.patch("/{route_id}/deactivate", response_model=DeliveryRouteRead)
def deactivate_delivery_route(route_id: int, db: Session = Depends(get_db)):
    try:
        return delivery_route_service.deactivate_delivery_route(db, route_id)
    except ValueError as error:
        raise _http_error(error) from error


@router.patch("/{route_id}/activate", response_model=DeliveryRouteRead)
def activate_delivery_route(route_id: int, db: Session = Depends(get_db)):
    try:
        return delivery_route_service.activate_delivery_route(db, route_id)
    except ValueError as error:
        raise _http_error(error) from error


def _http_error(error: ValueError) -> HTTPException:
    detail = str(error)
    if "ya esta registrado" in detail:
        return HTTPException(status_code=status.HTTP_409_CONFLICT, detail=detail)
    if "no existe" in detail:
        return HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=detail)
    return HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=detail)
