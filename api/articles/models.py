"""Article DB Model."""

from datetime import datetime
from typing import List

from sqlalchemy import DateTime, ForeignKey, String, Text, func
from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy.schema import UniqueConstraint

from api.db import Base


class Article(Base):
    """Article DB Model."""

    __tablename__ = "articles"

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    title: Mapped[str] = mapped_column(String, nullable=False)
    short_description: Mapped[str] = mapped_column(String, nullable=True)
    description: Mapped[str] = mapped_column(Text, nullable=True)
    created_at: Mapped[datetime] = mapped_column(
        DateTime, nullable=False, server_default=func.now()
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime,
        nullable=False,
        server_default=func.now(),
        onupdate=datetime.now,
    )

    comments: Mapped[List["Comment"]] = relationship(
        "Comment",
        lazy="joined",
        back_populates="article",
        cascade="all, delete-orphan",
    )


class Comment(Base):
    """Comment DB Model."""

    __tablename__ = "comments"

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    article_id: Mapped[int] = mapped_column(
        ForeignKey("articles.id", ondelete="CASCADE"), nullable=False
    )
    content: Mapped[str] = mapped_column(Text, nullable=False)
    created_at: Mapped[datetime] = mapped_column(
        DateTime, nullable=False, server_default=func.now()
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime,
        nullable=False,
        server_default=func.now(),
        onupdate=datetime.now,
    )

    article: Mapped[Article] = relationship(
        "Article", back_populates="comments"
    )


class Like(Base):
    """Like/Dislike DB Model for polymorphic association (e.g., articles)."""

    __tablename__ = "likes"

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    likes: Mapped[int] = mapped_column(default=0)
    dislikes: Mapped[int] = mapped_column(default=0)
    likeable_type: Mapped[str] = mapped_column(
        String, nullable=False, index=True
    )
    likeable_id: Mapped[int] = mapped_column(nullable=False, index=True)
    created_at: Mapped[datetime] = mapped_column(
        DateTime, nullable=False, server_default=func.now()
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime,
        nullable=False,
        server_default=func.now(),
        onupdate=datetime.now,
    )

    __table_args__ = (
        UniqueConstraint("likeable_type", "likeable_id", name="_likeable_uc"),
    )
