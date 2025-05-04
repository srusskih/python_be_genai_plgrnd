"""FastAPI dependencies for authentication."""

from typing import Annotated

from fastapi import Depends, Security, HTTPException
from fastapi.security import OAuth2PasswordBearer

from api.users.dependencies import get_user_manager
from api.users.managers import UserManager

from .managers import AuthManager

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="api/auth/sign_in")


async def get_auth_manager(
    user_manager: Annotated[UserManager, Depends(get_user_manager)],
):
    """DI Factory to build AuthManager instance."""
    manager = AuthManager(user_manager=user_manager)
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
