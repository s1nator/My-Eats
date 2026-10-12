import asyncio
import logging
import os
import socket
import sys
from datetime import datetime, timezone
from decimal import Decimal

from pythonjsonlogger.json import JsonFormatter
from sqlalchemy import select

from src.core.config import settings
from src.core.database import async_session_factory, engine
from src.models.menu import MenuItem


class StructuredLogFilter(logging.Filter):
    def filter(self, record: logging.LogRecord) -> bool:
        record.timestamp = datetime.now(timezone.utc).isoformat(
            timespec="milliseconds"
        ).replace("+00:00", "Z")
        record.level = record.levelname
        record.service_name = "my-eats-backend-seed"
        record.service_version = "1.0.0"
        record.service_environment = os.getenv("ENVIRONMENT", "production")
        record.service_hostname = socket.gethostname()
        record.service_process_id = os.getpid()
        return True


handler = logging.StreamHandler(sys.stdout)
handler.addFilter(StructuredLogFilter())
handler.setFormatter(
    JsonFormatter(
        "%(timestamp)s %(level)s %(message)s %(service_name)s "
        "%(service_version)s %(service_environment)s "
        "%(service_hostname)s %(service_process_id)s",
        rename_fields={
            "service_name": "service.name",
            "service_version": "service.version",
            "service_environment": "service.environment",
            "service_hostname": "service.hostname",
            "service_process_id": "service.process_id",
        },
    )
)

logging.basicConfig(level=settings.log_level, handlers=[handler], force=True)

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
