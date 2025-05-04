"""FastAPI dependencies for authentication."""

from typing import Annotated

from fastapi import Depends, HTTPException, Security
from fastapi.security import OAuth2PasswordBearer

from api.dependencies import get_app_settings
from api.settings import Settings
from api.users.dependencies import get_user_manager
from api.users.managers import UserManager

from .managers import AuthManager

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="api/auth/token")


async def get_auth_manager(
    settings: Annotated[Settings, Depends(get_app_settings)],
    user_manager: Annotated[UserManager, Depends(get_user_manager)],
):
    """DI Factory to build AuthManager instance."""
    manager = AuthManager(
        user_manager=user_manager,
        verification_token_audience=settings.JWT_AUDIENCE,
        verification_token_secret=settings.JWT_SECRET,
        verification_token_lifetime_seconds=settings.JWT_LIFETIME_SECONDS,
    )
    return manager


async def get_current_user(
    token: Annotated[str, Security(oauth2_scheme)],
    auth_manager: Annotated[AuthManager, Depends(get_auth_manager)],
):
    """Get current user from token."""
    resp = await auth_manager.authenticate_user_by_token(token=token)
    if resp is None:
        raise HTTPException(status_code=401, detail="Invalid token")
    user, _ = resp
    return user
