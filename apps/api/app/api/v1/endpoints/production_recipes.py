from decimal import Decimal

from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.orm import Session

from app.api.deps import get_current_user, get_db, require_admin_auditor
from app.models.user import User
from app.schemas.product import ProductKind
from app.schemas.production_recipe import (
    ProductionRecipeCostEstimate,
    ProductionRecipeCreate,
    ProductionRecipeItemCreate,
    ProductionRecipeItemRead,
    ProductionRecipeItemUpdate,
    ProductionRecipeRead,
    ProductionRecipeStatus,
    ProductionRecipeUpdate,
    ProductionRecipeVoid,
)
from app.services import production_recipes as recipe_service

router = APIRouter(
    prefix="/production",
    tags=["production-recipes"],
    dependencies=[Depends(get_current_user)],
)


@router.post(
    "/recipes",
    response_model=ProductionRecipeRead,
    status_code=status.HTTP_201_CREATED,
    dependencies=[Depends(require_admin_auditor)],
)
def create_recipe(
    payload: ProductionRecipeCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    try:
        return recipe_service.create_recipe(db, payload, current_user.id)
    except ValueError as error:
        raise _http_error(error) from error


@router.get("/recipes", response_model=list[ProductionRecipeRead])
def list_recipes(
    search: str | None = None,
    recipe_status: ProductionRecipeStatus | None = Query(
        default=None,
        alias="status",
    ),
    output_product_id: int | None = Query(default=None, gt=0),
    product_kind: ProductKind | None = None,
    is_valid_today: bool | None = None,
    db: Session = Depends(get_db),
):
    return recipe_service.list_recipes(
        db=db,
        search=search,
        status=recipe_status,
        output_product_id=output_product_id,
        product_kind=product_kind,
        is_valid_today=is_valid_today,
    )


@router.get("/recipes/{recipe_id}", response_model=ProductionRecipeRead)
def get_recipe(recipe_id: int, db: Session = Depends(get_db)):
    try:
        return recipe_service.get_recipe(db, recipe_id)
    except ValueError as error:
        raise _http_error(error) from error


@router.patch(
    "/recipes/{recipe_id}",
    response_model=ProductionRecipeRead,
    dependencies=[Depends(require_admin_auditor)],
)
def update_recipe(
    recipe_id: int,
    payload: ProductionRecipeUpdate,
    db: Session = Depends(get_db),
):
    try:
        return recipe_service.update_recipe(db, recipe_id, payload)
    except ValueError as error:
        raise _http_error(error) from error


@router.patch(
    "/recipes/{recipe_id}/activate",
    response_model=ProductionRecipeRead,
    dependencies=[Depends(require_admin_auditor)],
)
def activate_recipe(recipe_id: int, db: Session = Depends(get_db)):
    try:
        return recipe_service.activate_recipe(db, recipe_id)
    except ValueError as error:
        raise _http_error(error) from error


@router.patch(
    "/recipes/{recipe_id}/deactivate",
    response_model=ProductionRecipeRead,
    dependencies=[Depends(require_admin_auditor)],
)
def deactivate_recipe(recipe_id: int, db: Session = Depends(get_db)):
    try:
        return recipe_service.deactivate_recipe(db, recipe_id)
    except ValueError as error:
        raise _http_error(error) from error


@router.post(
    "/recipes/{recipe_id}/void",
    response_model=ProductionRecipeRead,
    dependencies=[Depends(require_admin_auditor)],
)
def void_recipe(
    recipe_id: int,
    payload: ProductionRecipeVoid,
    db: Session = Depends(get_db),
):
    try:
        return recipe_service.void_recipe(db, recipe_id, payload.reason)
    except ValueError as error:
        raise _http_error(error) from error


@router.post(
    "/recipes/{recipe_id}/items",
    response_model=ProductionRecipeItemRead,
    status_code=status.HTTP_201_CREATED,
    dependencies=[Depends(require_admin_auditor)],
)
def create_recipe_item(
    recipe_id: int,
    payload: ProductionRecipeItemCreate,
    db: Session = Depends(get_db),
):
    try:
        return recipe_service.create_recipe_item(db, recipe_id, payload)
    except ValueError as error:
        raise _http_error(error) from error


@router.patch(
    "/recipe-items/{item_id}",
    response_model=ProductionRecipeItemRead,
    dependencies=[Depends(require_admin_auditor)],
)
def update_recipe_item(
    item_id: int,
    payload: ProductionRecipeItemUpdate,
    db: Session = Depends(get_db),
):
    try:
        return recipe_service.update_recipe_item(db, item_id, payload)
    except ValueError as error:
        raise _http_error(error) from error


@router.patch(
    "/recipe-items/{item_id}/deactivate",
    response_model=ProductionRecipeItemRead,
    dependencies=[Depends(require_admin_auditor)],
)
def deactivate_recipe_item(item_id: int, db: Session = Depends(get_db)):
    try:
        return recipe_service.set_recipe_item_active(db, item_id, False)
    except ValueError as error:
        raise _http_error(error) from error


@router.patch(
    "/recipe-items/{item_id}/activate",
    response_model=ProductionRecipeItemRead,
    dependencies=[Depends(require_admin_auditor)],
)
def activate_recipe_item(item_id: int, db: Session = Depends(get_db)):
    try:
        return recipe_service.set_recipe_item_active(db, item_id, True)
    except ValueError as error:
        raise _http_error(error) from error


@router.get(
    "/recipes/{recipe_id}/cost-estimate",
    response_model=ProductionRecipeCostEstimate,
)
def get_cost_estimate(
    recipe_id: int,
    output_quantity: Decimal | None = Query(
        default=None,
        gt=Decimal("0"),
        max_digits=14,
        decimal_places=3,
    ),
    db: Session = Depends(get_db),
):
    try:
        return recipe_service.get_cost_estimate(
            db,
            recipe_id,
            output_quantity,
        )
    except ValueError as error:
        raise _http_error(error) from error


def _http_error(error: ValueError) -> HTTPException:
    detail = str(error)
    if "no existe" in detail:
        return HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=detail)
    if "anulada" in detail:
        return HTTPException(status_code=status.HTTP_409_CONFLICT, detail=detail)
    return HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=detail)
