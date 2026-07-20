from datetime import date

from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.orm import Session

from app.api.deps import get_current_user, get_db
from app.models.user import User
from app.schemas.route_closure import (
    RouteClosureCreate,
    RouteClosureRead,
    RouteClosureStatus,
    RouteClosureVoid,
)
from app.services import route_closures as route_closures_service

router = APIRouter(
    prefix="/route-closures",
    tags=["route-closures"],
    dependencies=[Depends(get_current_user)],
)


@router.post("", response_model=RouteClosureRead, status_code=status.HTTP_201_CREATED)
def create_route_closure(
    payload: RouteClosureCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    try:
        return route_closures_service.create_route_closure(
            db,
            payload,
            current_user.id,
        )
    except ValueError as error:
        raise _http_error(error) from error


@router.get("", response_model=list[RouteClosureRead])
def list_route_closures(
    date_from: date | None = None,
    date_to: date | None = None,
    closure_status: RouteClosureStatus | None = Query(default=None, alias="status"),
    route_id: int | None = Query(default=None, gt=0),
    vehicle_id: int | None = Query(default=None, gt=0),
    route_load_id: int | None = Query(default=None, gt=0),
    search: str | None = None,
    db: Session = Depends(get_db),
):
    try:
        return route_closures_service.list_route_closures(
            db=db,
            date_from=date_from,
            date_to=date_to,
            status=closure_status,
            route_id=route_id,
            vehicle_id=vehicle_id,
            route_load_id=route_load_id,
            search=search,
        )
    except ValueError as error:
        raise _http_error(error) from error


@router.get("/{closure_id}", response_model=RouteClosureRead)
def get_route_closure(closure_id: int, db: Session = Depends(get_db)):
    try:
        return route_closures_service.get_route_closure(db, closure_id)
    except ValueError as error:
        raise _http_error(error) from error


@router.post("/{closure_id}/void", response_model=RouteClosureRead)
def void_route_closure(
    closure_id: int,
    payload: RouteClosureVoid,
    db: Session = Depends(get_db),
):
    try:
        return route_closures_service.void_route_closure(
            db,
            closure_id,
            payload.reason,
        )
    except ValueError as error:
        raise _http_error(error) from error


def _http_error(error: ValueError) -> HTTPException:
    detail = str(error)
    if "no existe" in detail:
        return HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=detail)
    if "ya esta anulado" in detail or "otro cierre activo" in detail or (
        "ya tiene un cierre financiero activo" in detail
    ):
        return HTTPException(status_code=status.HTTP_409_CONFLICT, detail=detail)
    return HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=detail)
