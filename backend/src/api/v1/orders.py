from fastapi import APIRouter, HTTPException, Query, status

from src.api.deps import DbSession
from src.models.order import Order, OrderStatus
from src.metrics import (
    order_creation_duration_seconds,
    order_creation_errors_total,
    order_status_changes_total,
    orders_created_total,
    orders_revenue_total,
)
from src.schemas.order import OrderCreate, OrderRead, OrderStatusUpdate
from src.services.order_service import (
    MenuItemsNotFoundError,
    MenuItemsUnavailableError,
    create_order,
    get_order,
    get_orders,
    update_order_status,
)


router = APIRouter(prefix="/orders", tags=["Orders"])


async def get_order_or_404(session: DbSession, order_id: int) -> Order:
    order = await get_order(session, order_id)
    if order is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Order not found")
    return order


@router.post("", response_model=OrderRead, status_code=status.HTTP_201_CREATED)
async def create_new_order(order_in: OrderCreate, session: DbSession) -> OrderRead:
    try:
        with order_creation_duration_seconds.time():
            order = await create_order(session, order_in)

        orders_created_total.inc()
        orders_revenue_total.inc(float(order.total_price))
        return OrderRead.model_validate(order)
    except MenuItemsNotFoundError as error:
        order_creation_errors_total.labels(reason="items_not_found").inc()
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail={"message": "Menu items not found", "menu_item_ids": error.menu_item_ids},
        ) from error
    except MenuItemsUnavailableError as error:
        order_creation_errors_total.labels(reason="items_unavailable").inc()
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail={"message": "Menu items unavailable", "menu_item_ids": error.menu_item_ids},
        ) from error


@router.get("", response_model=list[OrderRead])
async def list_orders(
    session: DbSession,
    order_status: OrderStatus | None = Query(default=None, alias="status"),
) -> list[OrderRead]:
    orders = await get_orders(session, order_status)
    return [OrderRead.model_validate(order) for order in orders]


@router.get("/{order_id}", response_model=OrderRead)
async def get_order_by_id(order_id: int, session: DbSession) -> OrderRead:
    order = await get_order_or_404(session, order_id)
    return OrderRead.model_validate(order)


@router.patch("/{order_id}/status", response_model=OrderRead)
async def change_order_status(
    order_id: int,
    status_in: OrderStatusUpdate,
    session: DbSession,
) -> OrderRead:
    order = await get_order_or_404(session, order_id)
    previous_status = order.status
    updated_order = await update_order_status(session, order, status_in.status)

    if previous_status != status_in.status:
        order_status_changes_total.labels(
            from_status=previous_status.value,
            to_status=status_in.status.value,
        ).inc()

    return OrderRead.model_validate(updated_order)
