import logging
import sys
from collections.abc import AsyncIterator
from contextlib import asynccontextmanager

from fastapi import FastAPI

from src.api.v1.menu import router as menu_router
from src.api.v1.orders import router as orders_router
from src.core.config import settings
from src.core.database import engine


logging.basicConfig(
    level=settings.log_level,
    format="%(asctime)s | %(levelname)s | %(message)s",
    stream=sys.stdout,
    force=True,
)

logger = logging.getLogger(__name__)


@asynccontextmanager
async def lifespan(_: FastAPI) -> AsyncIterator[None]:
    logger.info("Application started")

    yield

    await engine.dispose()
    logger.info("Database connection pool closed")
    logger.info("Application stopped")


app = FastAPI(
    title="My Eats API",
    version="1.0.0",
    lifespan=lifespan,
)

app.include_router(menu_router, prefix="/api/v1")
app.include_router(orders_router, prefix="/api/v1")


@app.get("/health", tags=["Health"])
async def health_check() -> dict[str, str]:
    return {"status": "ok"}
