"""Authentication data access schemas schemas."""

from pydantic import BaseModel, EmailStr


class SignInUser(BaseModel):
    """Sign-in user schema."""

    email: EmailStr
    password: str


class UserSignInRequest(BaseModel):
    """User sign-in request schema."""

    user: SignInUser


class UserSignInResponse(BaseModel):
    """User sign-in response schema."""

    id: int
    email: EmailStr
    authentication_token: str


class SignOutUser(BaseModel):
    """Sign-out user schema."""

    email: EmailStr


class UserSignOutRequest(BaseModel):
    """User sign-out request schema."""

    user: SignOutUser


class UserSignOutResponse(BaseModel):
    """User sign-out response schema."""

    message: str
