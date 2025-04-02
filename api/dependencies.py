"""Fast API Application for API Application.

Usage example:

```python
# some_router.py
from api.settings import Settings
from api.dependencies import get_settings


@router.get("/some-endpoint")
async def some_endpoint(
    settings: Annotate[Settings, Depends(get_settings)],
): ...
```
"""

from typing import Annotated, AsyncGenerator

from fastapi import Depends, FastAPI, Request
from sqlalchemy.ext.asyncio import AsyncSession

from .db import async_session_maker
from .settings import Settings


async def get_app_instance(request: Request) -> FastAPI:
    """DI function to populate app instance"""
    return request.app


async def get_app_settings(
    app: Annotated[FastAPI, Depends(get_app_instance)],
) -> Settings:
    """DI function to populate settings singleton over the app."""
    return app.state.settings


async def get_db_session(
    app: Annotated[FastAPI, Depends(get_app_instance)],
) -> AsyncGenerator[AsyncSession, None]:
    """DI function to populate SQLAlchemy Session over the app."""
    session_class = async_session_maker(app.state.db_engine)
    async with session_class() as session:
        yield session
