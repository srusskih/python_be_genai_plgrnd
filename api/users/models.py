"""User's DB Models."""

from datetime import datetime
from typing import Optional

from sqlalchemy import DateTime, String, func
from sqlalchemy.orm import Mapped, mapped_column

from ..db import Base


class User(Base):
    """User's DB Model."""

    __tablename__ = "users"

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    email: Mapped[str] = mapped_column(String, nullable=False, unique=True)
    encrypted_password: Mapped[str] = mapped_column(String, nullable=False)

    # Reset Password functionality
    reset_password_token: Mapped[Optional[str]] = mapped_column(
        String, unique=True
    )
    reset_password_sent_at: Mapped[Optional[datetime]] = mapped_column(DateTime)
    remember_created_at: Mapped[Optional[datetime]] = mapped_column(DateTime)

    # Created & Updated At
    created_at: Mapped[datetime] = mapped_column(
        DateTime, nullable=False, server_default=func.now()
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime, nullable=False, server_default=func.now(), onupdate=func.now
    )


class JwtDenylist(Base):
    """JWT Denylist DB Model for tracking revoked tokens."""

    __tablename__ = "jwt_denylists"

    jti: Mapped[str] = mapped_column(String, primary_key=True)
    exp: Mapped[datetime] = mapped_column(DateTime, nullable=True)

    # Created & Updated At
    created_at: Mapped[datetime] = mapped_column(
        DateTime, nullable=False, default=func.now
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime, nullable=False, default=func.now, onupdate=func.now
    )
