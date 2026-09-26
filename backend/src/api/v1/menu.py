from fastapi import APIRouter, HTTPException, Query, Response, status

from src.api.deps import DbSession
from src.schemas.menu import MenuItemCreate, MenuItemRead, MenuItemUpdate
from src.services import menu_service


router = APIRouter(prefix="/menu", tags=["Menu"])


@router.get("", response_model=list[MenuItemRead])
async def list_menu_items(
    session: DbSession,
    category: str | None = Query(default=None, min_length=1, max_length=100),
    is_available: bool | None = Query(default=None),
) -> list[MenuItemRead]:
    items = await menu_service.get_menu_items(
        session,
        category=category,
        is_available=is_available,
    )
    return [MenuItemRead.model_validate(item) for item in items]


@router.post(
    "",
    response_model=MenuItemRead,
    status_code=status.HTTP_201_CREATED,
)
async def create_menu_item(
    item_in: MenuItemCreate,
    session: DbSession,
) -> MenuItemRead:
    item = await menu_service.create_menu_item(session, item_in)
    return MenuItemRead.model_validate(item)


@router.put("/{item_id}", response_model=MenuItemRead)
async def update_menu_item(
    item_id: int,
    item_in: MenuItemUpdate,
    session: DbSession,
) -> MenuItemRead:
    item = await menu_service.get_menu_item(session, item_id)
    if item is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Menu item not found")

    updated_item = await menu_service.update_menu_item(session, item, item_in)
    return MenuItemRead.model_validate(updated_item)


@router.delete("/{item_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_menu_item(item_id: int, session: DbSession) -> Response:
    item = await menu_service.get_menu_item(session, item_id)
    if item is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Menu item not found")

    await menu_service.delete_menu_item(session, item)
    return Response(status_code=status.HTTP_204_NO_CONTENT)
