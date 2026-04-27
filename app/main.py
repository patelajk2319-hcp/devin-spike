from contextlib import asynccontextmanager

from fastapi import FastAPI

from app.db.database import init_db
from app.routes import metrics, webhook
from app.utils.logger import get_logger

logger = get_logger(__name__)


@asynccontextmanager
async def lifespan(app: FastAPI):
    init_db()
    logger.info("Database initialised")
    logger.info("ready")
    yield
    logger.info("Shutting down")


app = FastAPI(
    title="Devin Remediation System",
    description="Event-driven vulnerability remediation via Devin API",
    version="1.0.0",
    lifespan=lifespan,
)

app.include_router(webhook.router)
app.include_router(metrics.router)
