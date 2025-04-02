"""User's API DTOs."""

from typing import Self

from pydantic import (
    BaseModel,
    ConfigDict,
    EmailStr,
    model_validator,
)


class UserRegistration(BaseModel):
    """User registration DTO."""

    email: EmailStr
    password: str
    password_confirmation: str

    @model_validator(mode="after")
    def validate_password_confirmation(self) -> Self:
        """Validate password confirmation."""
        if self.password != self.password_confirmation:
            raise ValueError("Passwords do not match")
        return self


class UserRegistrationRequest(BaseModel):
    """User registration response DTO."""

    user: UserRegistration


class UserRegistrationResponse(BaseModel):
    """User registration response DTO."""

    model_config = ConfigDict(from_attributes=True)

    id: int
    email: EmailStr
