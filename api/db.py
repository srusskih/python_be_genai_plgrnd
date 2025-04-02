"""Functionality to work with the database."""

from sqlalchemy.ext.asyncio import (
    AsyncAttrs,
    AsyncEngine,
    AsyncSession,
    async_sessionmaker,
    create_async_engine,
)
from sqlalchemy.orm import DeclarativeBase
from sqlalchemy.pool import NullPool


class Base(AsyncAttrs, DeclarativeBase):
    """Base class for all models."""


def create_engine(db_url: str) -> AsyncEngine:
    """Create a database pool from a database URL."""
    return create_async_engine(
        db_url,
        poolclass=NullPool,
    )


def async_session_maker(
    db_engine: AsyncEngine,
) -> async_sessionmaker[AsyncSession]:
    """Create an async session class."""
    return async_sessionmaker(
        db_engine, class_=AsyncSession, expire_on_commit=False
    )
