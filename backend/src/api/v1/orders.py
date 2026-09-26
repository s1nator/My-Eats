from fastapi import APIRouter, HTTPException, status

from src.api.deps import DbSession
from src.schemas.order import OrderCreate, OrderRead
from src.services.order_service import (
    MenuItemsNotFoundError,
    MenuItemsUnavailableError,
    create_order,
)


router = APIRouter(prefix="/orders", tags=["Orders"])


@router.post("", response_model=OrderRead, status_code=status.HTTP_201_CREATED)
async def create_new_order(order_in: OrderCreate, session: DbSession) -> OrderRead:
    try:
        order = await create_order(session, order_in)
        return OrderRead.model_validate(order)
    except MenuItemsNotFoundError as error:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail={"message": "Menu items not found", "menu_item_ids": error.menu_item_ids},
        ) from error
    except MenuItemsUnavailableError as error:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail={"message": "Menu items unavailable", "menu_item_ids": error.menu_item_ids},
        ) from error
