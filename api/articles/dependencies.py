"""Module for dependencies related to articles."""

from typing import Annotated

from fastapi import Depends
from sqlalchemy.ext.asyncio import AsyncSession

from api.articles.managers import ArticleManager
from api.dependencies import get_db_session


async def get_article_manager(
    db: Annotated[AsyncSession, Depends(get_db_session)],
) -> ArticleManager:
    """Dependency to provide an instance of ArticleManager.

    This function is used to inject the ArticleManager into routes that
    require it.
    """
    return ArticleManager(db)
