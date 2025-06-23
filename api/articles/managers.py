"""Article repository manager to operate on the DB."""

from typing import Optional

from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from sqlalchemy.orm import joinedload
from api.articles.models import Article, Like


class ArticleManager:
    """Manager to run main actions on articles records."""

    def __init__(self, session: AsyncSession):
        """Initialize ArticleManager with a database session."""
        self.session = session

    async def create_article(
        self,
        title: str,
        short_description: Optional[str] = None,
        description: Optional[str] = None,
        commit: bool = True,
    ) -> Article:
        """Create a new article and persist it to the database.

        Args:
            title (str): The title of the article.
            short_description (Optional[str]): Short description of the article.
            description (Optional[str]): Full article text.
            commit (bool): Whether to commit the transaction immediately.

        Returns:
            Article: The created Article instance.
        """
        article = Article(
            title=title,
            short_description=short_description,
            description=description,
        )
        self.session.add(article)
        if commit:
            await self.session.commit()
            await self.session.refresh(article)
        return article

    async def get_article_likes(self, article_id: int) -> tuple[int, int]:
        """Get like/dislike counts for an article.
        Args:
            article_id (int): The ID of the article.

        Returns:
            tuple[int, int]: A tuple containing the number of likes and dislikes.
        """
        query = select(Like).where(
            Like.likeable_type == "Article", Like.likeable_id == article_id
        )
        res = await self.session.execute(query)
        like = res.scalars().first()
        if like:
            return like.likes, like.dislikes
        return 0, 0

    async def get_article_by_id(self, article_id: int) -> Optional[Article]:
        """Retrieve an article by its ID, including comments.

        Args:
            article_id (int): The ID of the article to retrieve.

        Returns:
            Optional[Article]: The Article instance if found, else None.
        """
        query = (
            select(Article)
            .options(joinedload(Article.comments))
            .where(Article.id == article_id)
        )
        res = await self.session.execute(query)
        return res.scalars().first()

    async def list_articles(self) -> list[Article]:
        """List all articles in the database, including comments.

        Returns:
            list[Article]: List of all Article instances.
        """
        query = select(Article).options(joinedload(Article.comments))
        res = await self.session.execute(query)
        return res.unique().scalars().all()

    async def get_likes_for_articles(
        self, article_ids: list[int]
    ) -> dict[int, tuple[int, int]]:
        """Fetch likes/dislikes for all given article IDs in a single query.
        Args:
            article_ids (list[int]): List of article IDs to fetch likes/dislikes for.

        Returns:
            dict[int, tuple[int, int]]: A mapping of article ID to (likes, dislikes).
        """
        if not article_ids:
            return {}
        query = select(Like.likeable_id, Like.likes, Like.dislikes).where(
            Like.likeable_type == "Article", Like.likeable_id.in_(article_ids)
        )
        res = await self.session.execute(query)
        # Map: article_id -> (likes, dislikes)
        return {row.likeable_id: (row.likes, row.dislikes) for row in res.all()}
