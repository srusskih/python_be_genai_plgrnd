"""User repository managers to operate on the DB."""

from argon2 import PasswordHasher
from sqlalchemy.exc import IntegrityError
from sqlalchemy.ext.asyncio import AsyncSession

from .models import User


class PasswordManager:
    """Password manager to encrypt and decrypt the password string."""

    hasher: PasswordHasher

    def __init__(self, salt: str) -> None:
        self.hasher = PasswordHasher()
        self.__salt = bytes(salt, "utf-8")

    def hash_password(self, password: str) -> str:
        """Hash the password."""
        return self.hasher.hash(password, salt=self.__salt)

    def verify_password(self, password: str, hashed_password: str) -> bool:
        """Verify the password."""
        return self.hasher.hash(password, salt=self.__salt) == hashed_password


class UserAlreadyExists(Exception):
    """User already exists exception."""

    def __init__(self, email: str) -> None:
        super().__init__("User already exists.")
        self.email = email


class UserManager:
    """User repository manager to run main actions on users records."""

    session: AsyncSession
    password_manager: PasswordManager

    def __init__(
        self,
        session: AsyncSession,
        password_manager: PasswordManager,
    ):
        self.session = session
        self.password_manager = password_manager

    def set_password(self, user: User, password: str) -> None:
        """Set the user's password."""
        user.encrypted_password = self.password_manager.hash_password(password)

    async def create_user(
        self, user_email: str, password: str | None = None, commit: bool = False
    ) -> User:
        """Create a new user."""
        user = User(email=user_email, encrypted_password="")
        if password:
            self.set_password(user, password)
        self.session.add(user)

        if commit:
            try:
                await self.session.commit()
            except IntegrityError as e:
                raise UserAlreadyExists(user_email) from e

            await self.session.refresh(user)
        return user
