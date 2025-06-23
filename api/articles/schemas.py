"""Article API Schemas."""

from datetime import datetime
from pydantic import BaseModel, ConfigDict
from typing import Optional


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
