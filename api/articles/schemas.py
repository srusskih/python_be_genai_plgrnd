"""Article API Schemas."""

from datetime import datetime
from typing import List, Optional

from pydantic import BaseModel, ConfigDict


class CommentResponse(BaseModel):
    id: int
    content: str
    created_at: datetime
    updated_at: datetime


class ArticleBase(BaseModel):
    title: str
    short_description: Optional[str] = None
    description: Optional[str] = None


class ArticleCreateRequest(BaseModel):
    article: ArticleBase


class ArticleResponse(ArticleBase):
    model_config = ConfigDict(from_attributes=True)
    id: int
    created_at: datetime
    updated_at: datetime
    comments: List[CommentResponse] = []
    article_likes: int = 0
    article_dislikes: int = 0
