"""User repository managers to operate on the DB."""

from argon2 import PasswordHasher
from sqlalchemy.exc import IntegrityError
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select

from .models import User, JwtDenylist


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

    def verify_password(
        self, plain_password: str, hashed_password: str
    ) -> bool:
        """Verify the user's password."""
        # We do not want to expose instance dependencies to other classes,
        # so we have use a "chain of methods" to call the password manager
        return self.password_manager.verify_password(
            plain_password, hashed_password
        )

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

    async def get_user_by_email(self, email: str) -> User | None:
        """Get user by email."""
        query = select(User).where(User.email == email)
        res = await self.session.execute(query)
        user = res.scalars().first()
        return user

    async def add_to_jwt_denylist(
        self, token: str, commit: bool = False
    ) -> None:
        """Add token to JWT denylist."""
        jwt_denylist = JwtDenylist(jti=token)
        self.session.add(jwt_denylist)
        if commit:
            await self.session.commit()

    async def is_token_revoked(self, token: str) -> bool:
        """Check if token is revoked."""
        query = select(JwtDenylist).where(JwtDenylist.jti == token)
        res = await self.session.execute(query)
        return res.scalars().first() is not None
