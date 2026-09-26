from decimal import Decimal

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from src.models.menu import MenuItem
from src.models.order import Order, OrderItem
from src.schemas.order import OrderCreate


class MenuItemsNotFoundError(Exception):
    def __init__(self, menu_item_ids: list[int]) -> None:
        self.menu_item_ids = menu_item_ids
        super().__init__("Some menu items do not exist")


class MenuItemsUnavailableError(Exception):
    def __init__(self, menu_item_ids: list[int]) -> None:
        self.menu_item_ids = menu_item_ids
        super().__init__("Some menu items are unavailable")


async def create_order(session: AsyncSession, order_in: OrderCreate) -> Order:
    requested_items = {item.menu_item_id: item for item in order_in.items}
    menu_item_ids = list(requested_items)

    async with session.begin():
        result = await session.scalars(
            select(MenuItem)
            .where(MenuItem.id.in_(menu_item_ids))
            .with_for_update()
        )
        menu_items = {item.id: item for item in result.all()}

        missing_ids = sorted(set(menu_item_ids) - set(menu_items))
        if missing_ids:
            raise MenuItemsNotFoundError(missing_ids)

        unavailable_ids = sorted(
            item_id
            for item_id, menu_item in menu_items.items()
            if not menu_item.is_available
        )
        if unavailable_ids:
            raise MenuItemsUnavailableError(unavailable_ids)

        total_price = sum(
            (
                menu_items[item_id].price * requested_items[item_id].quantity
                for item_id in menu_item_ids
            ),
            start=Decimal("0.00"),
        )

        order = Order(
            customer_name=order_in.customer_name,
            customer_phone=order_in.customer_phone,
            delivery_address=order_in.delivery_address,
            total_price=total_price,
        )
        session.add(order)
        await session.flush()

        session.add_all(
            [
                OrderItem(
                    order_id=order.id,
                    menu_item_id=item_id,
                    quantity=requested_items[item_id].quantity,
                    price_at_order=menu_items[item_id].price,
                )
                for item_id in menu_item_ids
            ]
        )

    created_order = await session.scalar(
        select(Order)
        .options(selectinload(Order.items))
        .where(Order.id == order.id)
    )
    assert created_order is not None
    return created_order
