"""General fixtures for tests."""

from pathlib import Path
from typing import AsyncGenerator

import fastapi
import pytest
from alembic import command, config
from httpx import ASGITransport, AsyncClient
from sqlalchemy.ext.asyncio import AsyncEngine, AsyncSession

from api.app import create_app, lifespan
from api.db import async_session_maker
from api.dependencies import get_db_session
from api.settings import Settings

from .db_helpers import create_db, db_exists, drop_db


@pytest.fixture(scope="session", autouse=True)
def event_loop():
    """
    Creates an instance of the default event loop for the test session.
    This is necessary to avoid "RuntimeError: Event loop is closed" on Windows
    """
    import asyncio
    import sys

    if sys.platform.startswith("win") and sys.version_info[:2] >= (3, 8):
        # Avoid "RuntimeError: Event loop is closed"
        # on Windows when tearing down tests
        # https://github.com/encode/httpx/issues/914
        asyncio.set_event_loop_policy(asyncio.WindowsSelectorEventLoopPolicy())

    loop = asyncio.new_event_loop()
    asyncio.set_event_loop(loop)
    yield loop
    loop.close()


async def _db_manager(url: str):
    """Create a test database and run migrations."""

    # asyncpg doesn't support asyncpg+asyncio,
    # so we need to remove it from the URL.
    url = url.replace("+asyncpg", "")

    if await db_exists(url):
        await drop_db(url)
    await create_db(url)


async def _run_migrations(engine: AsyncEngine):
    """Run migrations for the test database."""
    path = Path(__file__).parent.parent / "alembic.ini"
    cfg = config.Config(str(path.absolute()))

    def run_upgrade(connection, cfg):
        cfg.attributes["connection"] = connection
        command.upgrade(cfg, "head")

    async with engine.begin() as connection:
        await connection.run_sync(run_upgrade, cfg)


@pytest.fixture(scope="session")
async def app_instance() -> AsyncGenerator[fastapi.FastAPI, None]:
    """Create a FastApi App instance for tests."""
    settings = Settings()
    settings.DB_NAME = "test__" + settings.DB_NAME

    # we need to make sure the database exists
    await _db_manager(settings.get_db_url())

    app = create_app(settings)
    # run the lifespan (initialize db connection, etc.)
    async with lifespan(app):
        await _run_migrations(app.state.db_engine)

        yield app


@pytest.fixture
async def api_client(
    app_instance: fastapi.FastAPI,
    db_session: AsyncSession,
) -> AsyncGenerator[AsyncClient, None]:
    """Create a test api client."""

    # use one sessions for all connections
    app_instance.dependency_overrides[get_db_session] = lambda: db_session

    client = AsyncClient(
        transport=ASGITransport(app_instance),
        base_url="http://test",
    )

    yield client


@pytest.fixture()
async def db_session(
    app_instance: fastapi.FastAPI,
) -> AsyncGenerator[AsyncSession, None]:
    """Create a database session for per test function."""
    engine = app_instance.state.db_engine

    connection = await engine.connect()
    transaction = await connection.begin()

    session_class = async_session_maker(connection)
    session = session_class()
    try:
        yield session
    finally:
        print("Closing session")
        await session.close()
        await transaction.rollback()
        await connection.close()
