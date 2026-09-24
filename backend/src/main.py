import logging
import sys

from contextlib import asynccontextmanager
from fastapi import FastAPI
from fastapi import Response


#logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(message)s",
    stream=sys.stdout
)

logger = logging.getLogger(__name__)


@asynccontextmanager
async def lifespan(app: FastAPI):
    logger.info("App starting...")
    yield
    logger.info("App shutting down...")


# Initialize app
app = FastAPI(
    title="My Eats API",
    version="1.0.0",
    lifespan=lifespan
)


#Health check
@app.get("/health")
async def health_check() -> dict[str,str]:
    return {"status": "ok"}