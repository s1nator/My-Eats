from typing import Any

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from src.models.menu import MenuItem
from src.schemas.menu import MenuItemCreate, MenuItemUpdate


def _payload(schema: MenuItemCreate | MenuItemUpdate) -> dict[str, Any]:
    data = schema.model_dump(exclude_unset=True)

    if data.get("image_url") is not None:
        data["image_url"] = str(data["image_url"])

    return data


async def get_menu_items(
    session: AsyncSession,
    category: str | None = None,
    is_available: bool | None = None,
) -> list[MenuItem]:
    statement = select(MenuItem).order_by(MenuItem.id)

    if category is not None:
        statement = statement.where(MenuItem.category == category)
    if is_available is not None:
        statement = statement.where(MenuItem.is_available == is_available)

    result = await session.scalars(statement)
    return list(result.all())


async def get_menu_item(session: AsyncSession, item_id: int) -> MenuItem | None:
    return await session.get(MenuItem, item_id)


async def create_menu_item(
    session: AsyncSession,
    item_in: MenuItemCreate,
) -> MenuItem:
    item = MenuItem(**_payload(item_in))
    session.add(item)
    await session.commit()
    await session.refresh(item)
    return item


async def update_menu_item(
    session: AsyncSession,
    item: MenuItem,
    item_in: MenuItemUpdate,
) -> MenuItem:
    for field_name, value in _payload(item_in).items():
        setattr(item, field_name, value)

    await session.commit()
    await session.refresh(item)
    return item


async def delete_menu_item(session: AsyncSession, item: MenuItem) -> None:
    await session.delete(item)
    await session.commit()
