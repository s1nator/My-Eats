import asyncio
import logging
import sys
from decimal import Decimal

from sqlalchemy import select

from src.core.config import settings
from src.core.database import async_session_factory, engine
from src.models.menu import MenuItem


logging.basicConfig(
    level=settings.log_level,
    format="%(asctime)s | %(levelname)s | %(message)s",
    stream=sys.stdout,
    force=True,
)

logger = logging.getLogger(__name__)


MENU_ITEMS = [
    {
        "title": "Пепперони",
        "description": "Томатный соус, моцарелла и пикантная пепперони.",
        "price": Decimal("649.00"),
        "category": "Пицца",
        "is_available": True,
        "image_url": "https://images.unsplash.com/photo-1628840042765-356cda07504e",
    },
    {
        "title": "Маргарита",
        "description": "Томатный соус, моцарелла и свежий базилик.",
        "price": Decimal("549.00"),
        "category": "Пицца",
        "is_available": True,
        "image_url": "https://images.unsplash.com/photo-1574071318508-1cdbab80d002",
    },
    {
        "title": "Чизбургер",
        "description": "Говяжья котлета, сыр чеддер, овощи и фирменный соус.",
        "price": Decimal("429.00"),
        "category": "Бургеры",
        "is_available": True,
        "image_url": "https://images.unsplash.com/photo-1568901346375-23c9450c58cd",
    },
    {
        "title": "Картофель фри",
        "description": "Хрустящий картофель с солью.",
        "price": Decimal("199.00"),
        "category": "Закуски",
        "is_available": True,
        "image_url": "https://images.unsplash.com/photo-1573080496219-bb080dd4f877",
    },
    {
        "title": "Цезарь с курицей",
        "description": "Куриное филе, салат романо, томаты, сыр и соус Цезарь.",
        "price": Decimal("389.00"),
        "category": "Салаты",
        "is_available": True,
        "image_url": "https://images.unsplash.com/photo-1546793665-c74683f339c1",
    },
    {
        "title": "Кола 0.5 л",
        "description": "Газированный напиток.",
        "price": Decimal("129.00"),
        "category": "Напитки",
        "is_available": True,
        "image_url": "https://images.unsplash.com/photo-1554866585-cd94860890b7",
    },
]


async def seed_menu() -> None:
    async with async_session_factory() as session:
        existing_titles = set(await session.scalars(select(MenuItem.title)))
        items_to_create = [
            MenuItem(**item)
            for item in MENU_ITEMS
            if item["title"] not in existing_titles
        ]

        if not items_to_create:
            logger.info("Seed data already exists")
            return

        session.add_all(items_to_create)
        await session.commit()
        logger.info("Created %s menu items", len(items_to_create))


async def main() -> None:
    try:
        await seed_menu()
    finally:
        await engine.dispose()


if __name__ == "__main__":
    asyncio.run(main())
