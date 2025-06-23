"""Article API Router."""

from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException

from api.articles import schemas
from api.articles.dependencies import get_article_manager
from api.articles.managers import ArticleManager
from api.articles.models import Article

router = APIRouter(tags=["articles"])


@router.post("", response_model=schemas.ArticleResponse)
async def create_article(
    payload: schemas.ArticleCreateRequest,
    article_manager: Annotated[ArticleManager, Depends(get_article_manager)],
):
    """Create a new article. Requires authentication."""
    article: Article = await article_manager.create_article(
        title=payload.article.title,
        short_description=payload.article.short_description,
        description=payload.article.description,
    )
    # Manually build response to avoid async attribute errors
    return schemas.ArticleResponse(
        id=article.id,
        title=article.title,
        short_description=article.short_description,
        description=article.description,
        created_at=article.created_at,
        updated_at=article.updated_at,
        comments=[
            schemas.CommentResponse(
                id=c.id,
                content=c.content,
                created_at=c.created_at,
                updated_at=c.updated_at,
            )
            for c in getattr(article, "comments", [])
        ],
    )


@router.get("/{article_id}", response_model=schemas.ArticleResponse)
async def get_article_by_id(
    article_id: int,
    article_manager: Annotated[ArticleManager, Depends(get_article_manager)],
):
    """Get an article by its ID."""
    article = await article_manager.get_article_by_id(article_id)
    if not article:
        raise HTTPException(status_code=404, detail="Article not found")
    likes, dislikes = await article_manager.get_article_likes(article.id)
    return schemas.ArticleResponse(
        id=article.id,
        title=article.title,
        short_description=article.short_description,
        description=article.description,
        created_at=article.created_at,
        updated_at=article.updated_at,
        comments=[
            schemas.CommentResponse(
                id=c.id,
                content=c.content,
                created_at=c.created_at,
                updated_at=c.updated_at,
            )
            for c in getattr(article, "comments", [])
        ],
        article_likes=likes,
        article_dislikes=dislikes,
    )


@router.get("", response_model=list[schemas.ArticleResponse])
async def list_articles(
    article_manager: Annotated[ArticleManager, Depends(get_article_manager)],
):
    """List all articles."""
    articles = await article_manager.list_articles()
    # Efficiently load all likes/dislikes for all articles in a single query
    article_ids = [article.id for article in articles]
    likes_map = await article_manager.get_likes_for_articles(article_ids)
    result = []
    for article in articles:
        likes, dislikes = likes_map.get(article.id, (0, 0))
        result.append(
            schemas.ArticleResponse(
                id=article.id,
                title=article.title,
                short_description=article.short_description,
                description=article.description,
                created_at=article.created_at,
                updated_at=article.updated_at,
                comments=[
                    schemas.CommentResponse(
                        id=c.id,
                        content=c.content,
                        created_at=c.created_at,
                        updated_at=c.updated_at,
                    )
                    for c in getattr(article, "comments", [])
                ],
                article_likes=likes,
                article_dislikes=dislikes,
            )
        )
    return result


@router.put("/{article_id}", response_model=schemas.ArticleResponse)
async def update_article(
    article_id: int,
    payload: schemas.ArticleCreateRequest,
    article_manager: Annotated[ArticleManager, Depends(get_article_manager)],
):
    """Update an article by its ID."""
    article = await article_manager.get_article_by_id(article_id)
    if not article:
        raise HTTPException(status_code=404, detail="Article not found")
    # Update fields
    article.title = payload.article.title
    article.short_description = payload.article.short_description
    article.description = payload.article.description
    await article_manager.session.commit()
    await article_manager.session.refresh(article)
    return schemas.ArticleResponse.model_validate(article, from_attributes=True)


@router.delete("/{article_id}", status_code=204)
async def delete_article(
    article_id: int,
    article_manager: Annotated[ArticleManager, Depends(get_article_manager)],
):
    """Delete an article by its ID."""
    article = await article_manager.get_article_by_id(article_id)
    if not article:
        raise HTTPException(status_code=404, detail="Article not found")
    await article_manager.session.delete(article)
    await article_manager.session.commit()
    return None
