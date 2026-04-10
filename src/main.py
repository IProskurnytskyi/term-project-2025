from logging import config, getLogger
from contextlib import asynccontextmanager
from pathlib import Path

from fastapi import FastAPI
from fastapi.responses import RedirectResponse
from fastapi.staticfiles import StaticFiles
from fastapi_pagination import add_pagination

from src.api.routers.field import router as field_router
from src.api.routers.satellite import router as satellite_router
from src.api.routers.weather import router as weather_router
from src.database.postgres.handler import PostgreSQLHandler as Database

FRONTEND_DIR = Path(__file__).resolve().parent.parent / "frontend"

# setup logger
config.fileConfig("logging.conf", disable_existing_loggers=False)
logger = getLogger(__name__)


@asynccontextmanager
async def lifespan(app: FastAPI):  # pylint: disable=W0621
    """
    Manages the lifespan of the application.

    This function is used as a context manager to handle the startup and shutdown events
    of the FastAPI application.

    Args:
        app (FastAPI): The FastAPI application instance.
    """
    # startup-event
    db_handler = Database()
    logger.info("Database Health-Check: %s", await db_handler.health_check())

    yield

    # shutdown-event


def create_app() -> FastAPI:
    """
    Initializes and configures a FastAPI application.

    This function sets up the FastAPI application with routers.

    Returns:
        FastAPI: A configured instance of the FastAPI application.
    """
    app = FastAPI(lifespan=lifespan, title="Geo Location Service")

    add_pagination(app)

    app.include_router(field_router, prefix="/api/v1")
    app.include_router(satellite_router, prefix="/api/v1")
    app.include_router(weather_router, prefix="/api/v1")

    @app.get("/", response_class=RedirectResponse, include_in_schema=False)
    async def index():
        return RedirectResponse(url="/app/index.html")

    @app.get("/docs-redirect", response_class=RedirectResponse, include_in_schema=False)
    async def docs():
        return RedirectResponse(url="/docs")

    if FRONTEND_DIR.exists():
        app.mount("/app", StaticFiles(directory=str(FRONTEND_DIR)), name="frontend")

    return app
