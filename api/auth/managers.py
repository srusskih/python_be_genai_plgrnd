"""Authentication Managers"""

from abc import ABC, abstractmethod
from typing import Any, Optional

from api.users.managers import UserManager
from api.users.models import User

from .jwt import InvalidTokenError, decode_jwt, generate_jwt


class AuthManagerABC(ABC):
    """Abstract AuthManager."""

    @abstractmethod
    async def authenticate_user(
        self, email: str, password: str
    ) -> tuple[User, str] | None:
        """Authenticate user with email and password."""


class AuthManager(AuthManagerABC):
    """Manager to authenticate users."""

    user_manager: UserManager

    def __init__(self, user_manager: UserManager):
        self.user_manager = user_manager

        # TODO
        # Replace with actual audience value
        self.verification_token_audience = "your_audience_value"

        # TODO
        # Replace with actual secret value
        self.verification_token_secret = "your_secret_value"

        # TODO
        # Ensure it's an integer
        self.verification_token_lifetime_seconds = int(3600)

    async def authenticate_user(
        self, email: str, password: str
    ) -> tuple[User, str] | None:
        """Authenticate user with email and password."""
        user = await self.user_manager.get_user_by_email(email=email)
        if not user:
            return None

        if not self.user_manager.verify_password(
            plain_password=password, hashed_password=user.encrypted_password
        ):
            return None

        auth_token = self.create_auth_token(user)

        return user, auth_token

    async def authenticate_user_by_token(
        self, token: str
    ) -> tuple[User, str] | None:
        """Authenticate user with token."""
        user_object = self.parse_token(token)
        if not user_object or user_object.get("email") is None:
            return None

        if await self.user_manager.is_token_revoked(token):
            return None

        user = await self.user_manager.get_user_by_email(
            email=user_object["email"]
        )
        if not user:
            return None

        return user, token

    def create_auth_token(self, user: User) -> str:
        """Create authentication token for user."""
        token_data = {
            "sub": str(user.id),
            "email": user.email,
            "aud": self.verification_token_audience,
        }
        token = generate_jwt(
            token_data,
            self.verification_token_secret,
            self.verification_token_lifetime_seconds,
        )
        return token

    def parse_token(self, token: str) -> Optional[dict[str, Any]]:
        """Parse and decode the token."""
        try:
            data = decode_jwt(
                token,
                self.verification_token_secret,
                [self.verification_token_audience],
            )
            return data
        except InvalidTokenError:
            return None

    async def sign_out(self, token: str) -> str:
        """Sign out user by adding token to denylist."""
        await self.user_manager.add_to_jwt_denylist(token, commit=True)
        return token
