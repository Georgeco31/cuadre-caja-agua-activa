from datetime import date

from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.orm import Session

from app.api.deps import (
    get_current_user,
    get_db,
    require_admin_auditor,
    require_operator_or_admin,
)
from app.models.user import User
from app.schemas.simple_route import (
    SimpleRouteAnalyticsRead,
    SimpleRouteAugustDryRunRead,
    SimpleRouteCancel,
    SimpleRouteCashReceiptCreate,
    SimpleRouteCashReceiptRead,
    SimpleRouteCollectionCreate,
    SimpleRouteCollectionRead,
    SimpleRouteExpenseCreate,
    SimpleRouteExpenseRead,
    SimpleRouteListItem,
    SimpleRouteSaleCreate,
    SimpleRouteSaleRead,
    SimpleRouteSettle,
    SimpleRouteSettlementRead,
    SimpleRouteSheetCreate,
    SimpleRouteSheetRead,
    SimpleRouteSheetUpdate,
    SimpleRouteStatus,
    SimpleRouteTripCreate,
    SimpleRouteTripItemCreate,
    SimpleRouteTripItemRead,
    SimpleRouteTripRead,
    SimpleRouteTripUpdate,
)
from app.services import simple_routes as service

router = APIRouter(
    prefix="/simple-routes",
    tags=["simple-routes"],
    dependencies=[Depends(get_current_user)],
)
cash_session_router = APIRouter(
    prefix="/cash-sessions",
    tags=["simple-routes"],
    dependencies=[Depends(get_current_user)],
)


@router.get(
    "/analytics",
    response_model=SimpleRouteAnalyticsRead,
    dependencies=[Depends(require_admin_auditor)],
)
def get_analytics(
    date_from: date,
    date_to: date,
    db: Session = Depends(get_db),
):
    try:
        return service.get_analytics(db, date_from, date_to)
    except ValueError as error:
        raise _http_error(error) from error


@router.get(
    "/cleanup/august-1-route-sales-dry-run",
    response_model=SimpleRouteAugustDryRunRead,
    dependencies=[Depends(require_admin_auditor)],
)
def august_route_sales_dry_run(db: Session = Depends(get_db)):
    return service.august_1_official_route_sales_dry_run(db)


@router.post(
    "",
    response_model=SimpleRouteSheetRead,
    status_code=status.HTTP_201_CREATED,
    dependencies=[Depends(require_operator_or_admin)],
)
def create_sheet(
    payload: SimpleRouteSheetCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    try:
        return service.create_sheet(db, payload, current_user.id)
    except ValueError as error:
        raise _http_error(error) from error


@router.get("", response_model=list[SimpleRouteListItem])
def list_sheets(
    date_from: date | None = None,
    date_to: date | None = None,
    route_status: SimpleRouteStatus | None = Query(default=None, alias="status"),
    employee_id: int | None = Query(default=None, gt=0),
    vehicle_id: int | None = Query(default=None, gt=0),
    search: str | None = None,
    db: Session = Depends(get_db),
):
    try:
        return service.list_sheets(
            db,
            date_from=date_from,
            date_to=date_to,
            status=route_status,
            employee_id=employee_id,
            vehicle_id=vehicle_id,
            search=search,
        )
    except ValueError as error:
        raise _http_error(error) from error


@router.get("/{sheet_id}", response_model=SimpleRouteSheetRead)
def get_sheet(sheet_id: int, db: Session = Depends(get_db)):
    try:
        return service.get_sheet(db, sheet_id)
    except ValueError as error:
        raise _http_error(error) from error


@router.patch(
    "/{sheet_id}",
    response_model=SimpleRouteSheetRead,
    dependencies=[Depends(require_operator_or_admin)],
)
def update_sheet(
    sheet_id: int,
    payload: SimpleRouteSheetUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    try:
        return service.update_sheet(db, sheet_id, payload, current_user.id)
    except ValueError as error:
        raise _http_error(error) from error


@router.post(
    "/{sheet_id}/trips",
    response_model=SimpleRouteTripRead,
    status_code=status.HTTP_201_CREATED,
    dependencies=[Depends(require_operator_or_admin)],
)
def add_trip(
    sheet_id: int,
    payload: SimpleRouteTripCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    try:
        return service.add_trip(db, sheet_id, payload, current_user.id)
    except ValueError as error:
        raise _http_error(error) from error


@router.patch(
    "/{sheet_id}/trips/{trip_id}",
    response_model=SimpleRouteTripRead,
    dependencies=[Depends(require_operator_or_admin)],
)
def update_trip(
    sheet_id: int,
    trip_id: int,
    payload: SimpleRouteTripUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    try:
        return service.update_trip(db, sheet_id, trip_id, payload, current_user.id)
    except ValueError as error:
        raise _http_error(error) from error


@router.post(
    "/{sheet_id}/trips/{trip_id}/items",
    response_model=SimpleRouteTripItemRead,
    status_code=status.HTTP_201_CREATED,
    dependencies=[Depends(require_operator_or_admin)],
)
def add_trip_item(
    sheet_id: int,
    trip_id: int,
    payload: SimpleRouteTripItemCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    try:
        return service.add_trip_item(
            db,
            sheet_id,
            trip_id,
            payload,
            current_user.id,
        )
    except ValueError as error:
        raise _http_error(error) from error


@router.post(
    "/{sheet_id}/sales",
    response_model=SimpleRouteSaleRead,
    status_code=status.HTTP_201_CREATED,
    dependencies=[Depends(require_operator_or_admin)],
)
def add_sale(
    sheet_id: int,
    payload: SimpleRouteSaleCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    try:
        return service.add_sale(db, sheet_id, payload, current_user.id)
    except ValueError as error:
        raise _http_error(error) from error


@router.post(
    "/{sheet_id}/collections",
    response_model=SimpleRouteCollectionRead,
    status_code=status.HTTP_201_CREATED,
    dependencies=[Depends(require_operator_or_admin)],
)
def add_collection(
    sheet_id: int,
    payload: SimpleRouteCollectionCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    try:
        return service.add_collection(db, sheet_id, payload, current_user.id)
    except ValueError as error:
        raise _http_error(error) from error


@router.post(
    "/{sheet_id}/expenses",
    response_model=SimpleRouteExpenseRead,
    status_code=status.HTTP_201_CREATED,
    dependencies=[Depends(require_operator_or_admin)],
)
def add_expense(
    sheet_id: int,
    payload: SimpleRouteExpenseCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    try:
        return service.add_expense(db, sheet_id, payload, current_user.id)
    except ValueError as error:
        raise _http_error(error) from error


@router.get("/{sheet_id}/settlement", response_model=SimpleRouteSettlementRead)
def get_settlement(sheet_id: int, db: Session = Depends(get_db)):
    try:
        return service.get_settlement(db, sheet_id)
    except ValueError as error:
        raise _http_error(error) from error


@router.post(
    "/{sheet_id}/settle",
    response_model=SimpleRouteSheetRead,
    dependencies=[Depends(require_admin_auditor)],
)
def settle_sheet(
    sheet_id: int,
    payload: SimpleRouteSettle,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    try:
        return service.settle_sheet(db, sheet_id, payload, current_user.id)
    except ValueError as error:
        raise _http_error(error) from error


@router.post(
    "/{sheet_id}/cancel",
    response_model=SimpleRouteSheetRead,
    dependencies=[Depends(require_admin_auditor)],
)
def cancel_sheet(
    sheet_id: int,
    payload: SimpleRouteCancel,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    try:
        return service.cancel_sheet(db, sheet_id, payload, current_user.id)
    except ValueError as error:
        raise _http_error(error) from error


@router.post(
    "/{sheet_id}/cash-receipt",
    response_model=SimpleRouteCashReceiptRead,
    status_code=status.HTTP_201_CREATED,
    dependencies=[Depends(require_admin_auditor)],
)
def receive_cash(
    sheet_id: int,
    payload: SimpleRouteCashReceiptCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    try:
        return service.receive_cash(db, sheet_id, payload, current_user.id)
    except ValueError as error:
        raise _http_error(error) from error


@cash_session_router.get(
    "/{cash_session_id}/simple-route-cash-receipts",
    response_model=list[SimpleRouteCashReceiptRead],
)
def list_cash_session_receipts(
    cash_session_id: int,
    db: Session = Depends(get_db),
):
    try:
        return service.list_cash_session_receipts(db, cash_session_id)
    except ValueError as error:
        raise _http_error(error) from error


def _http_error(error: ValueError) -> HTTPException:
    detail = str(error)
    if "no existe" in detail:
        return HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=detail)
    if (
        "ya " in detail
        or "no puede editarse" in detail
        or "no puede cancelarse" in detail
    ):
        return HTTPException(status_code=status.HTTP_409_CONFLICT, detail=detail)
    return HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=detail)
