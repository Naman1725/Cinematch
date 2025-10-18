"""Review schemas"""
from pydantic import BaseModel, Field
from typing import Optional
from datetime import datetime


class ReviewBase(BaseModel):
    """Base review schema"""
    content: str = Field(..., min_length=10, max_length=5000)
    title: Optional[str] = Field(None, max_length=200)
    is_spoiler: bool = False


class ReviewCreate(ReviewBase):
    """Schema for creating a review"""
    movie_id: int


class ReviewUpdate(BaseModel):
    """Schema for updating a review"""
    content: Optional[str] = Field(None, min_length=10, max_length=5000)
    title: Optional[str] = Field(None, max_length=200)
    is_spoiler: Optional[bool] = None


class ReviewResponse(BaseModel):
    """Schema for review response"""
    id: int
    user_id: int
    movie_id: int
    title: Optional[str] = None
    content: str
    helpful_count: int
    is_spoiler: bool
    created_at: datetime
    updated_at: Optional[datetime] = None

    class Config:
        from_attributes = True


class ReviewWithUser(ReviewResponse):
    """Schema for review response with user info"""
    username: str
    user_avatar: Optional[str] = None
