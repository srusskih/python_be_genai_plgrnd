"""Authentication API Router."""

from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException
from fastapi.security import OAuth2PasswordRequestForm

from ..users.models import User
from .dependencies import get_auth_manager, get_current_user, oauth2_scheme
from .managers import AuthManager
from .schemas import (
    UserSignInRequest,
    UserSignInResponse,
    UserSignOutRequest,
    UserSignOutResponse,
    TokenResponse,
)

router = APIRouter(tags=["auth", "users"])


@router.post("/sign_in", response_model=UserSignInResponse)
async def sign_in(
    payload: UserSignInRequest,
    auth_manager: Annotated[AuthManager, Depends(get_auth_manager)],
) -> UserSignInResponse:
    """Sign in endpoint for frontend app."""
    res = await auth_manager.authenticate_user(**payload.user.model_dump())
    if res is None:
        raise HTTPException(status_code=401)

    user, auth_token = res
    return UserSignInResponse(
        id=user.id,
        email=user.email,
        authentication_token=auth_token,
    )


@router.post("/token", response_model=TokenResponse)
async def get_token(
    form_data: Annotated[OAuth2PasswordRequestForm, Depends()],
    auth_manager: Annotated[AuthManager, Depends(get_auth_manager)],
) -> TokenResponse:
    """Get token endpoint for OAuth2 Password Flow."""
    # We are going to reuse sign_in logic
    # to authenticate user and get token
    # to reduce number of location to edit authentication logic
    resp = await sign_in(
        UserSignInRequest.model_validate(
            {
                "user": {
                    "email": form_data.username,
                    "password": form_data.password,
                }
            }
        ),
        auth_manager=auth_manager,
    )
    return TokenResponse(
        access_token=resp.authentication_token,
        token_type="bearer",
    )


@router.delete("/sign_out", response_model=UserSignOutResponse)
async def sign_out(
    _payload: UserSignOutRequest,
    # Note:
    # API COntract requires payload,
    # but we would not use it because email or id would be in JWT
    # to identify the user
    token: Annotated[str, Depends(oauth2_scheme)],
    # Token is required to sign out
    _current_user: Annotated[User, Depends(get_current_user)],
    # We need identify user to sign out
    auth_manager: Annotated[AuthManager, Depends(get_auth_manager)],
):
    """Sign out endpoint for frontend."""
    await auth_manager.sign_out(token)
    return {
        "message": "Signed out successfully.",
    }
