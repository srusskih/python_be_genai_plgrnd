"""Article API Router."""

from typing import Annotated
from fastapi import APIRouter, Depends, HTTPException

from api.articles import schemas
from api.articles.managers import ArticleManager
from api.articles.models import Article
from api.articles.dependencies import get_article_manager

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
    return schemas.ArticleResponse.model_validate(article, from_attributes=True)


@router.get("/{article_id}", response_model=schemas.ArticleResponse)
async def get_article_by_id(
    article_id: int,
    article_manager: Annotated[ArticleManager, Depends(get_article_manager)],
):
    """Get an article by its ID."""
    article = await article_manager.get_article_by_id(article_id)
    if not article:
        raise HTTPException(status_code=404, detail="Article not found")
    return schemas.ArticleResponse.model_validate(article, from_attributes=True)


@router.get("", response_model=list[schemas.ArticleResponse])
async def list_articles(
    article_manager: Annotated[ArticleManager, Depends(get_article_manager)],
):
    """List all articles."""
    articles = await article_manager.list_articles()
    return [
        schemas.ArticleResponse.model_validate(article, from_attributes=True)
        for article in articles
    ]


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
