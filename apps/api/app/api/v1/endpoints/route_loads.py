from datetime import date

from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.orm import Session

from app.api.deps import get_current_user, get_db
from app.models.user import User
from app.schemas.route_load import (
    RouteLoadCreate,
    RouteLoadRead,
    RouteLoadStatus,
    RouteLoadVoid,
)
from app.services import route_loads as route_loads_service

router = APIRouter(
    prefix="/route-loads",
    tags=["route-loads"],
    dependencies=[Depends(get_current_user)],
)


@router.post("", response_model=RouteLoadRead, status_code=status.HTTP_201_CREATED)
def create_route_load(
    payload: RouteLoadCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    try:
        return route_loads_service.create_route_load(db, payload, current_user.id)
    except ValueError as error:
        raise _http_error(error) from error


@router.get("", response_model=list[RouteLoadRead])
def list_route_loads(
    date_from: date | None = None,
    date_to: date | None = None,
    route_load_status: RouteLoadStatus | None = Query(default=None, alias="status"),
    route_id: int | None = Query(default=None, gt=0),
    vehicle_id: int | None = Query(default=None, gt=0),
    product_id: int | None = Query(default=None, gt=0),
    search: str | None = None,
    db: Session = Depends(get_db),
):
    try:
        return route_loads_service.list_route_loads(
            db=db,
            date_from=date_from,
            date_to=date_to,
            status=route_load_status,
            route_id=route_id,
            vehicle_id=vehicle_id,
            product_id=product_id,
            search=search,
        )
    except ValueError as error:
        raise _http_error(error) from error


@router.get("/{load_id}", response_model=RouteLoadRead)
def get_route_load(load_id: int, db: Session = Depends(get_db)):
    try:
        return route_loads_service.get_route_load(db, load_id)
    except ValueError as error:
        raise _http_error(error) from error


@router.post("/{load_id}/void", response_model=RouteLoadRead)
def void_route_load(
    load_id: int,
    payload: RouteLoadVoid,
    db: Session = Depends(get_db),
):
    try:
        return route_loads_service.void_route_load(db, load_id, payload.reason)
    except ValueError as error:
        raise _http_error(error) from error


def _http_error(error: ValueError) -> HTTPException:
    detail = str(error)
    if "ya esta anulada" in detail:
        return HTTPException(status_code=status.HTTP_409_CONFLICT, detail=detail)
    if "no existe" in detail:
        return HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=detail)
    return HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=detail)
