from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.api.deps import get_db, require_admin_auditor
from app.models.user import User
from app.schemas.user import (
    UserCreate,
    UserPasswordUpdate,
    UserRead,
    UserUpdate,
)
from app.services import users as user_service


router = APIRouter(
    prefix="/users",
    tags=["users"],
    dependencies=[Depends(require_admin_auditor)],
)


@router.get("", response_model=list[UserRead])
def list_users(db: Session = Depends(get_db)):
    return user_service.list_users(db)


@router.post("", response_model=UserRead, status_code=status.HTTP_201_CREATED)
def create_user(payload: UserCreate, db: Session = Depends(get_db)):
    try:
        return user_service.create_user(db, payload)
    except ValueError as error:
        raise _http_error(error) from error


@router.patch("/{user_id}", response_model=UserRead)
def update_user(
    user_id: int,
    payload: UserUpdate,
    db: Session = Depends(get_db),
):
    try:
        return user_service.update_user(db, user_id, payload)
    except ValueError as error:
        raise _http_error(error) from error


@router.patch("/{user_id}/activate", response_model=UserRead)
def activate_user(user_id: int, db: Session = Depends(get_db)):
    try:
        return user_service.set_user_active(db, user_id, True)
    except ValueError as error:
        raise _http_error(error) from error


@router.patch("/{user_id}/deactivate", response_model=UserRead)
def deactivate_user(user_id: int, db: Session = Depends(get_db)):
    try:
        return user_service.set_user_active(db, user_id, False)
    except ValueError as error:
        raise _http_error(error) from error


@router.patch("/{user_id}/password", response_model=UserRead)
def update_user_password(
    user_id: int,
    payload: UserPasswordUpdate,
    db: Session = Depends(get_db),
):
    try:
        return user_service.update_password(db, user_id, payload.new_password)
    except ValueError as error:
        raise _http_error(error) from error


def _http_error(error: ValueError) -> HTTPException:
    detail = str(error)
    if "no existe" in detail:
        return HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=detail)
    if "ya esta registrado" in detail:
        return HTTPException(status_code=status.HTTP_409_CONFLICT, detail=detail)
    return HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=detail)
