import logging
import os
import socket
import sys
from collections.abc import AsyncGenerator
from contextlib import asynccontextmanager
from datetime import datetime, timezone

from pythonjsonlogger.json import JsonFormatter

from fastapi import FastAPI

from src.api.v1.menu import router as menu_router
from src.api.v1.orders import router as orders_router
from src.core.config import settings
from src.core.database import engine


class StructuredLogFilter(logging.Filter):
    def filter(self, record: logging.LogRecord) -> bool:
        record.timestamp = datetime.now(timezone.utc).isoformat(
            timespec="milliseconds"
        ).replace("+00:00", "Z")
        record.level = record.levelname
        record.service_name = "my-eats-backend"
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


logging.basicConfig(
    level=settings.log_level,
    handlers=[handler],
    force=True,
)

for logger_name in ("uvicorn", "uvicorn.error", "uvicorn.access"):
    uvicorn_logger = logging.getLogger(logger_name)
    uvicorn_logger.handlers = [handler]
    uvicorn_logger.propagate = False

logger = logging.getLogger(__name__)


@asynccontextmanager
async def lifespan(_: FastAPI) -> AsyncGenerator[None, None]:
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
