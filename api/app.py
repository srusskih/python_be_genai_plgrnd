"""API's Fast API Application."""

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from api.routers import root
from api.settings import Settings


def __attach_routers(app: FastAPI) -> FastAPI:
    """Attach routers to the app."""
    app.include_router(root.router)
    return app


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
    )

    # Routers
    app = __attach_routers(app)

    # Middlewares
    app.add_middleware(
        CORSMiddleware,
        **settings.CORS_MIDDLEWARE.model_dump(),
    )
    return app
