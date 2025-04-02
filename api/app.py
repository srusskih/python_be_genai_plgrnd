"""API's Fast API Application."""

import contextlib

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from api.db import create_engine
from api.routers import v1
from api.settings import Settings


@contextlib.asynccontextmanager
async def lifespan(app: FastAPI):
    """Application ASGI's lifespan handler."""
    settings = app.state.settings

    engine = create_engine(db_url=settings.get_db_url())
    app.state.db_engine = engine

    try:
        yield
    finally:
        app.state.db_engine = None
        await engine.dispose()


def create_app(settings: Settings) -> FastAPI:
    """Create the FastAPI app instance."""
    app = FastAPI(
        debug=settings.DEBUG,
        title="Sports-Hub Application Back-End",
        description="API Documentation",
        version=settings.VERSION,
        docs_url="/docs",
        redoc_url="/redoc",
        openapi_url="/swagger.json",
        lifespan=lifespan,
    )
    app.state.settings = settings

    # Routers
    app.include_router(v1.router)

    # Middlewares
    app.add_middleware(
        CORSMiddleware,
        **settings.CORS_MIDDLEWARE.model_dump(),
    )
    return app
