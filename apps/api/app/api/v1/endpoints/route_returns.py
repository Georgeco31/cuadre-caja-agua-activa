from datetime import date

from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.orm import Session

from app.api.deps import get_current_user, get_db, require_admin_auditor
from app.models.user import User
from app.schemas.route_return import (
    RouteReturnCreate,
    RouteReturnRead,
    RouteReturnStatus,
    RouteReturnVoid,
)
from app.services import route_returns as route_returns_service

router = APIRouter(
    prefix="/route-returns",
    tags=["route-returns"],
    dependencies=[Depends(get_current_user)],
)


@router.post("", response_model=RouteReturnRead, status_code=status.HTTP_201_CREATED)
def create_route_return(
    payload: RouteReturnCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    try:
        return route_returns_service.create_route_return(db, payload, current_user.id)
    except ValueError as error:
        raise _http_error(error) from error


@router.get("", response_model=list[RouteReturnRead])
def list_route_returns(
    date_from: date | None = None,
    date_to: date | None = None,
    route_return_status: RouteReturnStatus | None = Query(default=None, alias="status"),
    route_id: int | None = Query(default=None, gt=0),
    vehicle_id: int | None = Query(default=None, gt=0),
    route_load_id: int | None = Query(default=None, gt=0),
    product_id: int | None = Query(default=None, gt=0),
    search: str | None = None,
    db: Session = Depends(get_db),
):
    try:
        return route_returns_service.list_route_returns(
            db=db,
            date_from=date_from,
            date_to=date_to,
            status=route_return_status,
            route_id=route_id,
            vehicle_id=vehicle_id,
            route_load_id=route_load_id,
            product_id=product_id,
            search=search,
        )
    except ValueError as error:
        raise _http_error(error) from error


@router.get("/{return_id}", response_model=RouteReturnRead)
def get_route_return(return_id: int, db: Session = Depends(get_db)):
    try:
        return route_returns_service.get_route_return(db, return_id)
    except ValueError as error:
        raise _http_error(error) from error


@router.post(
    "/{return_id}/void",
    response_model=RouteReturnRead,
    dependencies=[Depends(require_admin_auditor)],
)
def void_route_return(
    return_id: int,
    payload: RouteReturnVoid,
    db: Session = Depends(get_db),
):
    try:
        return route_returns_service.void_route_return(db, return_id, payload.reason)
    except ValueError as error:
        raise _http_error(error) from error


def _http_error(error: ValueError) -> HTTPException:
    detail = str(error)
    if (
        "ya esta anulado" in detail
        or "retorno activo" in detail
        or "cierre financiero activo" in detail
    ):
        return HTTPException(status_code=status.HTTP_409_CONFLICT, detail=detail)
    if "no existe" in detail:
        return HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=detail)
    return HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=detail)
