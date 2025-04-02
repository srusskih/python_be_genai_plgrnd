"""Users' FastAPI DI definitions."""

from typing import Annotated

from fastapi import Depends
from sqlalchemy.ext.asyncio import AsyncSession

from api.dependencies import get_app_settings, get_db_session
from api.settings import Settings

from .managers import PasswordManager, UserManager


async def get_password_manager(
    settings: Annotated[Settings, Depends(get_app_settings)],
):
    """DI Factory to build PasswordManager instance."""
    manager = PasswordManager(settings.SALT)
    return manager


async def get_user_manager(
    session: Annotated[AsyncSession, Depends(get_db_session)],
    password_manager: Annotated[PasswordManager, Depends(get_password_manager)],
):
    """DI Factory to build UserManager instance."""
    manager = UserManager(
        session=session,
        password_manager=password_manager,
    )
    return manager
