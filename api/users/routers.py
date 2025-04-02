"""User's functionality API Router."""

from typing import Annotated

from fastapi import APIRouter, Depends
from fastapi.exceptions import HTTPException

from . import schemas
from .dependencies import get_user_manager
from .managers import UserAlreadyExists, UserManager

router = APIRouter(prefix="/users", tags=["users"])


@router.post("/registrations", response_model=schemas.UserRegistrationResponse)
async def create_user(
    payload: schemas.UserRegistrationRequest,
    user_manager: Annotated[UserManager, Depends(get_user_manager)],
):
    """Create a new user."""
    try:
        user = await user_manager.create_user(
            payload.user.email, payload.user.password, commit=True
        )
    except UserAlreadyExists as e:
        raise HTTPException(status_code=409, detail=[{"msg": str(e)}]) from e

    r = schemas.UserRegistrationResponse.model_validate(
        user, from_attributes=True
    )

    return r
